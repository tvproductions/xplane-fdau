"""Read-only official dependency status and a guarded refresh entry point."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import re
import subprocess
import sys
import tomllib
from collections.abc import Callable, Sequence
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request

from packaging.requirements import InvalidRequirement, Requirement
from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.utils import canonicalize_name
from packaging.version import InvalidVersion, Version

try:
    from .dependency_sources import Opener, Runner, SourceError, fetch_index, fetch_release_requirements, newest_stable_release, open_index, release_is_yanked
    from .dependency_matrix import MatrixResult, run_matrix
except ImportError:  # Direct script execution puts tools/ on sys.path.
    from dependency_sources import Opener, Runner, SourceError, fetch_index, fetch_release_requirements, newest_stable_release, open_index, release_is_yanked
    from dependency_matrix import MatrixResult, run_matrix

SCHEMA_VERSION = 1


class ScopeError(ValueError):
    """The reviewed plan is stale or a pre-mutation guard failed."""


class UpdateError(RuntimeError):
    """A refresh command failed after the mutation boundary."""

    def __init__(self, message: str, report: dict[str, Any]) -> None:
        super().__init__(message)
        self.report = report


SUPPORTED_PYTHON = (Version("3.12"), Version("3.13"), Version("3.14"))
MANAGED_FILES = (
    ".python-version",
    ".github/workflows/ci.yml",
    ".github/workflows/release-readiness.yml",
    "pyproject.toml",
    "uv.lock",
)
TREE_COMMAND = ("uv", "--no-config", "tree", "--outdated", "--all-groups", "--universal", "--locked", "--format", "json")
METADATA_COMMAND = ("uv", "--no-config", "workspace", "metadata", "--locked")
AUDIT_COMMAND = ("uv", "--no-config", "audit", "--locked", "--output-format", "json")


def canonical_json(report: dict[str, Any]) -> str:
    """Serialize a report as stable UTF-8 JSON with one terminal line feed."""
    return json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n"


def _run(args: tuple[str, ...], cwd: Path) -> tuple[int, str, str]:
    timeout = 1800 if args == ("uv", "run", "--offline", "--frozen", "python", ".codex/skills/hygiene/scripts/hygiene.py") else 120
    try:
        result = subprocess.run(args, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as error:
        return 1, "", str(error)
    return result.returncode, result.stdout, result.stderr


def _json_result(runner: Runner, args: tuple[str, ...], root: Path, blockers: list[dict[str, object]], *, findings_exit: bool = False) -> dict[str, Any] | None:
    code, output, error = runner(args, root)
    try:
        value = json.loads(output)
    except (ValueError, TypeError):
        blockers.append({"kind": "source", "command": list(args), "reason": f"invalid JSON or failed command: {error.strip()}"})
        return None
    if not isinstance(value, dict) or (code != 0 and not (findings_exit and code == 1)):
        blockers.append({"kind": "source", "command": list(args), "reason": f"unexpected command result: exit {code}: {error.strip()}"})
        return None
    if findings_exit and code == 1 and not value.get("vulnerabilities") and not value.get("adverse_statuses"):
        blockers.append({"kind": "source", "command": list(args), "reason": "findings exit without findings payload"})
        return None
    return value


def _preview_resolution(value: dict[str, Any], command: tuple[str, ...], blockers: list[dict[str, object]]) -> dict[str, dict[str, Any]]:
    expected = (
        {"schema", "workspace_root", "workspace", "roots", "inverted", "members", "resolution"}
        if command == TREE_COMMAND
        else {"schema", "workspace_root", "environment", "workspace", "requires_python", "conflicts", "module_owners", "members", "resolution"}
    )
    if (
        set(value) != expected
        or value.get("schema") != {"version": "preview"}
        or not isinstance(value.get("workspace_root"), str)
        or not isinstance(value.get("workspace"), dict)
        or not isinstance(value.get("members"), list)
        or not isinstance(value.get("resolution"), dict)
    ):
        blockers.append({"kind": "source", "command": list(command), "reason": "unknown uv preview schema"})
        return {}
    if command == TREE_COMMAND and (not isinstance(value.get("roots"), list) or not isinstance(value.get("inverted"), bool)):
        blockers.append({"kind": "source", "command": list(command), "reason": "unknown uv preview schema"})
        return {}
    if command == METADATA_COMMAND and (
        not isinstance(value.get("environment"), dict)
        or not isinstance(value.get("requires_python"), str)
        or not isinstance(value.get("conflicts"), dict)
        or not isinstance(value.get("module_owners"), dict)
    ):
        blockers.append({"kind": "source", "command": list(command), "reason": "unknown uv preview schema"})
        return {}
    resolution = value["resolution"]
    for key, node in resolution.items():
        if not isinstance(key, str) or not isinstance(node, dict) or "kind" not in node:
            blockers.append({"kind": "source", "command": list(command), "reason": "malformed uv resolution node"})
            return {}
    return resolution


def _required_declarations(project: dict[str, Any], blockers: list[dict[str, object]]) -> tuple[dict[str, list[str]], list[str]]:
    groups = project.get("dependency-groups", {})
    production = project.get("project", {}).get("dependencies", [])
    build = project.get("build-system", {}).get("requires", [])
    if not isinstance(groups, dict) or not isinstance(production, list) or not isinstance(build, list):
        blockers.append({"kind": "source", "reason": "malformed project requirement declarations"})
        return {}, []
    declarations: dict[str, list[str]] = {"project": production, "build": build}
    for group, requirements in sorted(groups.items()):
        if not isinstance(group, str) or not isinstance(requirements, list):
            blockers.append({"kind": "source", "reason": "malformed dependency group"})
            continue
        declarations[group] = requirements
    names: list[str] = []
    for group, requirements in declarations.items():
        for requirement in requirements:
            try:
                names.append(canonicalize_name(Requirement(requirement).name))
            except (InvalidRequirement, TypeError):
                blockers.append({"kind": "source", "group": group, "reason": f"invalid requirement: {requirement}"})
    return declarations, sorted(set(names))


def _locked_artifacts(package: dict[str, Any]) -> list[tuple[str, str]]:
    artifacts = []
    sdist = package.get("sdist")
    if sdist is not None:
        artifacts.append(sdist)
    wheels = package.get("wheels", [])
    if not isinstance(wheels, list):
        raise SourceError("invalid locked wheel list")
    artifacts.extend(wheels)
    if not artifacts:
        raise SourceError("missing locked artifacts")
    result: list[tuple[str, str]] = []
    for artifact in artifacts:
        if not isinstance(artifact, dict) or not isinstance(artifact.get("url"), str):
            raise SourceError("invalid locked artifact")
        hash_value = artifact.get("hash")
        if not isinstance(hash_value, str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", hash_value):
            raise SourceError("missing locked SHA-256")
        parsed = urlparse(artifact["url"])
        if parsed.scheme != "https" or parsed.hostname != "files.pythonhosted.org":
            raise SourceError("untrusted locked artifact URL")
        result.append((Path(parsed.path).name, hash_value.removeprefix("sha256:")))
    return result


def _audit_findings(value: dict[str, Any], locked_versions: dict[str, set[str]], blockers: list[dict[str, object]]) -> list[dict[str, object]]:
    if (
        value.get("schema") != {"version": "preview"}
        or not isinstance(value.get("summary"), dict)
        or not isinstance(value.get("vulnerabilities"), list)
        or not isinstance(value.get("adverse_statuses"), list)
    ):
        blockers.append({"kind": "source", "command": list(AUDIT_COMMAND), "reason": "unknown uv audit schema"})
        return []
    findings: list[dict[str, object]] = []
    for item in value["vulnerabilities"]:
        if not isinstance(item, dict):
            blockers.append({"kind": "source", "reason": "malformed uv advisory"})
            continue
        package = item.get("package") if isinstance(item.get("package"), dict) else item
        name, version = package.get("name"), package.get("version")
        advisory = item.get("vulnerability") if isinstance(item.get("vulnerability"), dict) else item
        advisory_id = advisory.get("id")
        if (
            not isinstance(name, str)
            or not isinstance(version, str)
            or not isinstance(advisory_id, str)
            or version not in locked_versions.get(canonicalize_name(name), set())
        ):
            blockers.append({"kind": "source", "reason": "advisory does not identify a locked package/version"})
            continue
        fixed = advisory.get("fixed_version", advisory.get("fix_version"))
        if fixed is None and isinstance(advisory.get("fixed_versions"), list):
            fixed = advisory["fixed_versions"][0] if advisory["fixed_versions"] else None
        findings.append(
            {"kind": "advisory", "name": canonicalize_name(name), "version": version, "id": advisory_id, "fixed_version": fixed, "source": "uv audit / OSV"}
        )
    for item in value["adverse_statuses"]:
        if not isinstance(item, dict):
            blockers.append({"kind": "source", "reason": "malformed uv adverse status"})
            continue
        findings.append({"kind": "adverse-status", "source": "uv audit / OSV", "detail": item})
    return findings


def _scope(root: Path, runner: Runner, blockers: list[dict[str, object]]) -> tuple[str, list[dict[str, object]]]:
    code, branch, error = runner(("git", "branch", "--show-current"), root)
    if code or not branch.strip():
        blockers.append({"kind": "source", "reason": f"Git branch unavailable: {error.strip()}"})
    code, raw_status, error = runner(("git", "status", "--porcelain=v1", "-z", "--untracked-files=all"), root)
    if code:
        blockers.append({"kind": "source", "reason": f"Git status unavailable: {error.strip()}"})
    code, raw_index, error = runner(("git", "ls-files", "-s", "-z"), root)
    if code:
        blockers.append({"kind": "source", "reason": f"Git index unavailable: {error.strip()}"})
    index_blobs: dict[str, str] = {}
    for entry in raw_index.split("\0"):
        if entry:
            try:
                metadata, path = entry.split("\t", 1)
                index_blobs[path.replace("\\", "/")] = metadata.split()[1]
            except (ValueError, IndexError):
                blockers.append({"kind": "source", "reason": "malformed Git index listing"})
    paths: list[dict[str, object]] = []
    entries = raw_status.split("\0")
    position = 0
    while position < len(entries) and entries[position]:
        entry = entries[position]
        if len(entry) < 4 or entry[2] != " ":
            blockers.append({"kind": "source", "reason": "malformed Git status listing"})
            break
        status = entry[:2]
        path = entry[3:].replace("\\", "/")
        if status[0] in "RC" and position + 1 < len(entries):
            position += 1  # The extra NUL entry is the prior path.
        file_path = root / path
        digest = hashlib.sha256(file_path.read_bytes()).hexdigest() if file_path.is_file() else None
        paths.append({"path": path, "status": status, "sha256": digest, "index_blob": index_blobs.get(path)})
        position += 1
    return branch.strip(), sorted(paths, key=lambda item: str(item["path"]))


def collect_status(root: Path, runner: Runner, opener: Opener) -> dict[str, Any]:
    """Collect official uv, lock, PyPI, and advisory evidence without mutation."""
    root = root.resolve()
    blockers: list[dict[str, object]] = []
    official_evidence: list[tuple[str, str, str, str]] = []

    def evidence_opener(request: Request, timeout: int, ceiling: int) -> tuple[bytes, str, str]:
        body, final_url, content_type = opener(request, timeout, ceiling)
        official_evidence.append((request.full_url, hashlib.sha256(body).hexdigest(), final_url, content_type))
        return body, final_url, content_type

    findings: list[dict[str, object]] = []
    dependencies: list[dict[str, object]] = []
    try:
        project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
        lock = tomllib.loads((root / "uv.lock").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as error:
        blockers.append({"kind": "source", "reason": f"invalid managed TOML: {error}"})
        project, lock = {}, {}
    declarations, declared_names = _required_declarations(project, blockers)
    code, output, error = runner(("uv", "--version"), root)
    match = re.match(r"uv (\d+\.\d+\.\d+)", output) if code == 0 else None
    installed = match.group(1) if match else None
    if installed is None:
        blockers.append({"kind": "source", "reason": f"unverified installed uv: {error.strip()}"})
    required = project.get("tool", {}).get("uv", {}).get("required-version")
    if required is not None and (not isinstance(required, str) or not re.fullmatch(r"==\d+\.\d+\.\d+", required)):
        blockers.append({"kind": "source", "reason": "invalid exact uv requirement"})
    tree_value = _json_result(runner, TREE_COMMAND, root, blockers)
    metadata_value = _json_result(runner, METADATA_COMMAND, root, blockers)
    tree = _preview_resolution(tree_value, TREE_COMMAND, blockers) if tree_value is not None else {}
    metadata = _preview_resolution(metadata_value, METADATA_COMMAND, blockers) if metadata_value is not None else {}
    if tree and metadata and set(tree) != set(metadata):
        blockers.append({"kind": "source", "reason": "universal tree and workspace metadata disagree"})
    lock_packages = lock.get("package", [])
    if not isinstance(lock_packages, list):
        blockers.append({"kind": "source", "reason": "invalid universal lock package list"})
        lock_packages = []
    locked_versions: dict[str, set[str]] = {}
    for package in lock_packages:
        if not isinstance(package, dict) or not isinstance(package.get("name"), str) or not isinstance(package.get("version"), str):
            blockers.append({"kind": "source", "reason": "invalid locked package"})
            continue
        name, version = canonicalize_name(package["name"]), package["version"]
        if "registry" not in package.get("source", {}):
            continue
        locked_versions.setdefault(name, set()).add(version)
        node = next(
            (
                node
                for node in tree.values()
                if node.get("name") == name and node.get("version") == version and isinstance(node.get("source", {}).get("registry"), dict)
            ),
            None,
        )
        if node is None:
            blockers.append({"kind": "source", "name": name, "version": version, "reason": "universal lock package absent from uv tree"})
        try:
            index = fetch_index(name, evidence_opener)
            newest = newest_stable_release(index)
            artifacts = _locked_artifacts(package)
            yanked = any(release_is_yanked(index, version, digest) for _, digest in artifacts)
            if yanked:
                findings.append({"kind": "yanked", "name": name, "version": version, "source": f"https://pypi.org/simple/{name}/"})
            latest = node.get("latest_version") if node else None
            if latest is not None and not isinstance(latest, str):
                raise SourceError("invalid uv latest_version")
            outdated = latest is not None and Version(latest) > Version(version)
            if latest is None and Version(newest) > Version(version):
                findings.append(
                    {"kind": "no-candidate", "name": name, "version": version, "newest_stable": newest, "source": "uv universal resolution and PyPI Index JSON"}
                )
            dependencies.append(
                {
                    "name": name,
                    "version": version,
                    "newest_stable": newest,
                    "resolver_candidate": latest,
                    "outdated": outdated,
                    "declared": name in declared_names,
                    "source": f"https://pypi.org/simple/{name}/",
                }
            )
        except (SourceError, InvalidVersion, ValueError) as source_error:
            blockers.append({"kind": "source", "name": name, "version": version, "reason": str(source_error)})
    audit_value = _json_result(runner, AUDIT_COMMAND, root, blockers, findings_exit=True)
    if audit_value is not None:
        findings.extend(_audit_findings(audit_value, locked_versions, blockers))
    candidate = installed
    uv_latest: str | None = None
    try:
        uv_index = fetch_index("uv", evidence_opener)
        uv_latest = newest_stable_release(uv_index)
        uv_files = uv_index["files"]
        if not isinstance(uv_files, list):
            raise SourceError("uv: missing official release files")
        matching_files = [
            item
            for item in uv_files
            if isinstance(item, dict)
            and isinstance(item.get("filename"), str)
            and re.search(rf"-{re.escape(uv_latest)}(?:-|\.)", item["filename"])
            and not item.get("yanked", False)
        ]
        requires_python = {item.get("requires-python") for item in matching_files}
        if not matching_files or len(requires_python) != 1 or not isinstance(next(iter(requires_python)), str):
            raise SourceError("uv candidate lacks unambiguous official Python metadata")
        allowed = SpecifierSet(next(iter(requires_python)))
        if any(version not in allowed for version in SUPPORTED_PYTHON):
            blockers.append({"kind": "incompatible-uv", "version": uv_latest, "requires_python": str(allowed)})
        else:
            candidate = uv_latest
    except (SourceError, InvalidSpecifier, ValueError) as source_error:
        blockers.append({"kind": "source", "name": "uv", "reason": str(source_error)})
    branch, reviewed_paths = _scope(root, runner, blockers)
    proposed_files = list(MANAGED_FILES)
    proposed_commands = [["uv", "lock", "--upgrade"], ["uv", "sync", "--all-groups", "--locked"], ["uv", "lock", "--check"]]
    managed_hashes = {path: hashlib.sha256((root / path).read_bytes()).hexdigest() if (root / path).is_file() else None for path in MANAGED_FILES}
    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "uv": {"installed": installed, "required": required, "newest_stable": uv_latest, "candidate": candidate, "source": "https://pypi.org/simple/uv/"},
        "python": {
            "declared": project.get("project", {}).get("requires-python"),
            "lock": lock.get("requires-python"),
            "selector": (root / ".python-version").read_text(encoding="utf-8").strip() if (root / ".python-version").is_file() else None,
            "supported": [str(v) for v in SUPPORTED_PYTHON],
            "groups": declarations,
        },
        "dependencies": sorted(dependencies, key=lambda item: (str(item["name"]), str(item["version"]))),
        "current_findings": sorted(findings, key=lambda item: (str(item.get("kind")), str(item.get("name")), str(item.get("id")))),
        "pre_apply_blockers": sorted(blockers, key=lambda item: (str(item.get("kind")), str(item.get("name")), str(item.get("reason")))),
        "proposed_files": proposed_files,
        "proposed_commands": proposed_commands,
        "reviewed_paths": reviewed_paths,
        "plan_sha256": "",
    }
    digest_payload = {
        "report": {key: value for key, value in report.items() if key != "plan_sha256"},
        "managed_hashes": managed_hashes,
        "branch": branch,
        "official_evidence": official_evidence,
    }
    report["plan_sha256"] = hashlib.sha256(canonical_json(digest_payload).encode("utf-8")).hexdigest()
    return report


def _reviewed_scope(root: Path, report: dict[str, Any], paths: Sequence[str]) -> None:
    """Require exact repository-relative paths from the digest-protected status."""
    expected = {str(item["path"]) for item in report["reviewed_paths"]}
    supplied: set[str] = set()
    for value in paths:
        parsed = PurePosixPath(value)
        if value != parsed.as_posix() or parsed.is_absolute() or any(part in {"", ".", ".."} for part in parsed.parts) or "\\" in value:
            raise ScopeError(f"invalid review scope path: {value}")
        if value in supplied or root not in (root / value).resolve().parents:
            raise ScopeError(f"invalid review scope path: {value}")
        supplied.add(value)
    if supplied != expected:
        raise ScopeError(f"review scope differs from status: expected {sorted(expected)}, got {sorted(supplied)}")


def replace_exact(source: str, old: str, new: str) -> str:
    """Replace a single reviewed anchor without touching surrounding bytes."""
    if source.count(old) != 1:
        raise ScopeError(f"expected one anchor: {old!r}")
    return source.replace(old, new)


def _workflow_edit(source: str, allowed_current: set[str], candidate: str) -> str:
    lines = source.splitlines(keepends=True)
    starts = [i for i, line in enumerate(lines) if "- uses: astral-sh/setup-uv@" in line]
    if not starts:
        raise ScopeError("setup-uv workflow anchor missing")
    for start in reversed(starts):
        indent = len(lines[start]) - len(lines[start].lstrip())
        end = next(
            (i for i in range(start + 1, len(lines)) if len(lines[i]) - len(lines[i].lstrip()) == indent and lines[i].lstrip().startswith("- ")),
            len(lines),
        )
        matches = [i for i in range(start + 1, end) if re.fullmatch(r'\s*version: ["\']\d+\.\d+\.\d+["\']\s*', lines[i])]
        if len(matches) != 1:
            raise ScopeError("setup-uv requires one exact version anchor")
        index = matches[0]
        version = re.search(r"version: [\"'](\d+\.\d+\.\d+)[\"']", lines[index])
        if version is None or version.group(1) not in allowed_current:
            raise ScopeError("setup-uv version differs from reviewed uv pins")
        lines[index] = lines[index].replace(version.group(1), candidate)
    return "".join(lines)


def _prepare_edits(root: Path, report: dict[str, Any]) -> dict[Path, bytes]:
    """Validate all managed anchors and build replacement bytes before writes."""
    installed = report["uv"]["installed"]
    candidate = report["uv"]["candidate"]
    if not isinstance(installed, str) or not isinstance(candidate, str):
        raise ScopeError("unverified uv version")
    project_path = root / "pyproject.toml"
    source = project_path.read_bytes().decode("utf-8")
    try:
        project = tomllib.loads(source)
    except tomllib.TOMLDecodeError as error:
        raise ScopeError(f"invalid project TOML: {error}") from error
    python_policy = project.get("project", {}).get("requires-python")
    if python_policy not in {">=3.12", ">=3.12,<3.15"}:
        raise ScopeError("unexpected Python policy")
    if source.count(f'requires-python = "{python_policy}"') != 1:
        raise ScopeError("duplicate or missing Python policy anchor")
    if python_policy != ">=3.12,<3.15":
        source = replace_exact(source, 'requires-python = ">=3.12"', 'requires-python = ">=3.12,<3.15"')
    uv_section = project.get("tool", {}).get("uv", {})
    required = uv_section.get("required-version")
    if required is None:
        source = replace_exact(source, "[tool.uv.build-backend]", f'[tool.uv]\nrequired-version = "=={candidate}"\n\n[tool.uv.build-backend]')
    elif isinstance(required, str) and required == report["uv"]["required"] and re.fullmatch(r"==\d+\.\d+\.\d+", required):
        if required != f"=={candidate}":
            source = replace_exact(source, f'required-version = "{required}"', f'required-version = "=={candidate}"')
    else:
        raise ScopeError("unexpected uv required-version anchor")
    build_reqs = project.get("build-system", {}).get("requires", [])
    if not isinstance(build_reqs, list) or not any(
        isinstance(item, str) and Requirement(item).name == "uv_build" and candidate in Requirement(item).specifier for item in build_reqs
    ):
        raise ScopeError("candidate incompatible with uv_build requirement")
    prepared = {project_path: source.encode("utf-8")}
    current_pins = {installed}
    if isinstance(required, str) and re.fullmatch(r"==\d+\.\d+\.\d+", required):
        current_pins.add(required.removeprefix("=="))
    for relative in (".github/workflows/ci.yml", ".github/workflows/release-readiness.yml"):
        path = root / relative
        prepared[path] = _workflow_edit(path.read_bytes().decode("utf-8"), current_pins, candidate).encode("utf-8")
    return prepared


def _uv_owner(root: Path, runner: Runner, candidate: str) -> str:
    executable = shutil.which("uv")
    if executable is None:
        return "unknown"
    path = Path(executable).resolve()
    if os.name == "nt" and "microsoft\\winget\\packages\\astral-sh.uv_" in str(path).lower():
        code, output, _ = runner(("winget", "list", "--id", "astral-sh.uv", "--exact"), root)
        return "winget:astral-sh.uv" if code == 0 and "astral-sh.uv" in output else "unknown"
    code, _, _ = runner(("uv", "self", "update", "--dry-run", candidate), root)
    return "standalone" if code == 0 else "unknown"


def apply_status(
    root: Path,
    expected_sha256: str,
    review_scopes: Sequence[str],
    runner: Runner,
    opener: Opener,
    *,
    uv_owner: str | None = None,
    matrix_runner: Callable[[Path], MatrixResult] = run_matrix,
) -> dict[str, Any]:
    """Apply only the current, scope-reviewed official status plan."""
    root = root.resolve()
    report = collect_status(root, runner, opener)
    if not re.fullmatch(r"[0-9a-f]{64}", expected_sha256) or report["plan_sha256"] != expected_sha256:
        raise ScopeError("status digest changed")
    if report["pre_apply_blockers"]:
        raise ScopeError(f"pre-apply blocker: {report['pre_apply_blockers']}")
    _reviewed_scope(root, report, review_scopes)
    prepared = _prepare_edits(root, report)
    installed, candidate = report["uv"]["installed"], report["uv"]["candidate"]
    owner = uv_owner if uv_owner is not None else _uv_owner(root, runner, candidate)
    if owner not in {"standalone", "winget:astral-sh.uv"}:
        raise ScopeError(f"uv owner could not be verified: {owner}")
    if installed != candidate and owner != "standalone":
        raise ScopeError(f"uv owner action required: {owner}; update to {candidate} and rerun status")
    result: dict[str, Any] = {
        "status": "running",
        "before": report,
        "after": None,
        "uv_owner": owner,
        "commands": [],
        "prepared_files": [str(path.relative_to(root)).replace("\\", "/") for path in prepared],
        "remaining_constraints": [],
        "matrix": None,
    }

    def run(command: tuple[str, ...]) -> None:
        code, output, error = runner(command, root)
        result["commands"].append({"command": list(command), "exit_code": code, "stdout": output[-4000:], "stderr": error[-4000:]})
        if code:
            result["status"] = "failed"
            raise UpdateError(f"command failed ({code}): {' '.join(command)}: {error.strip()}", result)

    if installed != candidate:
        code, _, error = runner(("uv", "self", "update", "--dry-run", candidate), root)
        if code:
            raise ScopeError(f"uv installer ownership could not be proved: {error}")
        run(("uv", "self", "update", candidate))
        code, output, error = runner(("uv", "--version"), root)
        result["commands"].append({"command": ["uv", "--version"], "exit_code": code, "stdout": output, "stderr": error})
        if code or not re.match(rf"uv {re.escape(candidate)}(?:\s|$)", output):
            result["status"] = "failed"
            raise UpdateError(f"uv version verification failed: {error}", result)
    for path, contents in prepared.items():
        if path.read_bytes() != contents:
            path.write_bytes(contents)
            if path.read_bytes() != contents:
                result["status"] = "failed"
                raise UpdateError(f"managed file write verification failed: {path}", result)
    for command in (("uv", "lock", "--upgrade"), ("uv", "sync", "--all-groups", "--locked"), ("uv", "lock", "--check")):
        run(command)
    after = collect_status(root, runner, opener)
    result["after"] = after
    remaining = _remaining_constraints(root, after, opener)
    result["remaining_constraints"] = remaining
    unresolved = [item for item in remaining if not item["explained"]]
    adverse = [item for item in after["current_findings"] if item.get("kind") != "no-candidate"]
    if after["pre_apply_blockers"] or adverse or unresolved:
        result["status"] = "failed"
        raise UpdateError(
            f"refreshed graph has unresolved evidence: {after['pre_apply_blockers']} {adverse} {unresolved}",
            result,
        )
    if after["python"]["declared"] != ">=3.12,<3.15" or after["uv"]["required"] != f"=={candidate}":
        result["status"] = "failed"
        raise UpdateError("refreshed project policy differs from reviewed target", result)
    run(
        (
            "uv",
            "run",
            "--frozen",
            "python",
            "-m",
            "unittest",
            "tests.test_dependency_sources",
            "tests.test_dependency_refresh",
            "tests.test_dependency_matrix",
            "tests.test_project_metadata",
            "tests.test_release_tool",
            "tests.test_release_workflows",
            "tests.test_project_skills",
            "-v",
        )
    )
    run(("uv", "run", "--offline", "--frozen", "python", ".codex/skills/hygiene/scripts/hygiene.py"))
    matrix = matrix_runner(root)
    result["matrix"] = {
        "success": matrix.success,
        "commands": [{"command": list(entry.command), "cwd": str(entry.cwd), "exit_code": entry.exit_code} for entry in matrix.commands],
        "artifact_hashes": matrix.artifact_hashes,
        "preserved_failure_paths": [str(path) for path in matrix.preserved_failure_paths],
        "error": matrix.error,
    }
    if not matrix.success:
        result["status"] = "failed"
        raise UpdateError(f"Python source/installed-wheel matrix failed: {matrix.error}", result)
    result["status"] = "passed"
    return result


def _remaining_constraints(root: Path, after: dict[str, Any], opener: Opener) -> list[dict[str, object]]:
    """Attribute stale transitive versions to exact official parent requirements."""
    declarations = after["python"]["groups"]
    direct: dict[str, list[tuple[str, str, Requirement]]] = {}
    for group_name, group in declarations.items():
        for requirement_text in group:
            parsed = Requirement(requirement_text)
            direct.setdefault(canonicalize_name(parsed.name), []).append((group_name, requirement_text, parsed))
    try:
        lock = tomllib.loads((root / "uv.lock").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as error:
        raise UpdateError(f"cannot inspect refreshed lock constraints: {error}", {"after": after, "status": "failed"}) from error
    packages = lock.get("package")
    if not isinstance(packages, list):
        raise UpdateError("refreshed lock has no package list", {"after": after, "status": "failed"})
    release_cache: dict[tuple[str, str], list[str]] = {}
    remaining: list[dict[str, object]] = []
    for dependency in after["dependencies"]:
        name, latest = dependency["name"], dependency["newest_stable"]
        if not dependency["outdated"] and not any(
            finding.get("kind") == "no-candidate" and finding.get("name") == name for finding in after["current_findings"]
        ):
            continue
        covered: set[str] = set()
        constraints: list[dict[str, object]] = []
        errors: list[str] = []
        for group_name, requirement_text, parsed in direct.get(name, []):
            if latest not in parsed.specifier:
                versions = [str(version) for version in SUPPORTED_PYTHON if parsed.marker is None or parsed.marker.evaluate({"python_version": str(version)})]
                covered.update(versions)
                constraints.append(
                    {"parent": "xplane-fdau", "requirement": requirement_text, "source": "pyproject.toml", "group": group_name, "applies_python": versions}
                )
        parents: list[tuple[str, str]] = []
        for package in packages:
            if not isinstance(package, dict):
                continue
            children = package.get("dependencies", [])
            if not isinstance(children, list) or not any(
                isinstance(child, dict) and canonicalize_name(str(child.get("name", ""))) == name for child in children
            ):
                continue
            parent_name, parent_version = package.get("name"), package.get("version")
            if not isinstance(parent_name, str) or not isinstance(parent_version, str) or "registry" not in package.get("source", {}):
                errors.append(f"unverified parent for {name}")
                continue
            parents.append((canonicalize_name(parent_name), parent_version))
        for parent_name, parent_version in sorted(set(parents)):
            key = (parent_name, parent_version)
            try:
                if key not in release_cache:
                    release_cache[key] = fetch_release_requirements(parent_name, parent_version, opener)
                requirements = [(text, Requirement(text)) for text in release_cache[key]]
            except (SourceError, InvalidRequirement) as error:
                errors.append(f"{parent_name} {parent_version}: {error}")
                continue
            for requirement_text, parsed in requirements:
                if canonicalize_name(parsed.name) != name or latest in parsed.specifier:
                    continue
                versions = [str(version) for version in SUPPORTED_PYTHON if parsed.marker is None or parsed.marker.evaluate({"python_version": str(version)})]
                if not versions:
                    continue
                covered.update(versions)
                constraints.append(
                    {
                        "parent": parent_name,
                        "parent_version": parent_version,
                        "requirement": requirement_text,
                        "source": f"https://pypi.org/pypi/{parent_name}/{parent_version}/json",
                        "applies_python": versions,
                    }
                )
        explained = not errors and covered == {str(version) for version in SUPPORTED_PYTHON}
        remaining.append(
            {
                "name": name,
                "version": dependency["version"],
                "newest_stable": latest,
                "constraints": constraints,
                "errors": errors,
                "explained": explained,
            }
        )
    return remaining


def main(argv: Sequence[str] | None = None) -> int:
    """Print a read-only human or canonical JSON status report."""
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    status = subcommands.add_parser("status", help="inspect official dependency evidence without mutation")
    status.add_argument("--json", action="store_true", help="emit canonical JSON")
    apply = subcommands.add_parser("apply", help="run a reviewed dependency refresh")
    apply.add_argument("--plan-sha256", required=True)
    apply.add_argument("--review-scope", action="append", default=[])
    apply.add_argument("--json", action="store_true", help="emit canonical JSON")
    args = parser.parse_args(argv)
    if args.command == "apply":
        try:
            outcome = apply_status(Path.cwd(), args.plan_sha256, args.review_scope, _run, open_index)
        except ScopeError as error:
            print(f"apply blocked: {error}", file=sys.stderr)
            return 1
        except UpdateError as error:
            print(canonical_json(error.report), end="")
            print(f"apply failed: {error}", file=sys.stderr)
            return 1
        print(canonical_json(outcome), end="")
        return 0
    report = collect_status(Path.cwd(), _run, open_index)
    if args.json:
        sys.stdout.write(canonical_json(report))
    else:
        print(f"Dependency refresh status (schema {report['schema_version']})")
        print(f"uv: {report['uv']}")
        print(f"Locked packages: {len(report['dependencies'])}")
        print(f"Current findings: {len(report['current_findings'])}")
        print(f"Pre-apply blockers: {len(report['pre_apply_blockers'])}")
        for blocker in report["pre_apply_blockers"]:
            print(f"  {blocker}")
        print(f"Plan SHA-256: {report['plan_sha256']}")
    return 0 if not report["pre_apply_blockers"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
