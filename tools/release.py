"""Validate local xplane-fdr release artifacts without publishing them."""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path, PurePosixPath
import tarfile
import tomllib
import zipfile


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "xplane_fdr"
PROJECT = "xplane-fdr"


class ReleaseError(ValueError):
    """Report a local release-contract violation."""


@dataclass(frozen=True)
class ReleaseArtifacts:
    """Name and digest evidence for a validated artifact pair."""

    wheel: Path
    sdist: Path
    wheel_sha256: str
    sdist_sha256: str


def _project_version() -> str:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    version = project["version"]
    dependencies = project["dependencies"]
    if not isinstance(version, str) or not isinstance(dependencies, list):
        raise ReleaseError("pyproject project version and dependencies must be declared")
    if dependencies:
        raise ReleaseError("runtime dependencies must be empty")
    if project.get("requires-python") != ">=3.12":
        raise ReleaseError("Requires-Python must be >=3.12")
    return version


def _runtime_version() -> str:
    source = ROOT / PACKAGE / "__init__.py"
    tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
    version: object | None = None
    for statement in tree.body:
        if isinstance(statement, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "__version__" for target in statement.targets):
            version = ast.literal_eval(statement.value)
            break
    if not isinstance(version, str):
        raise ReleaseError("xplane_fdr.__version__ must be a string")
    return version


def _version() -> str:
    project_version = _project_version()
    runtime_version = _runtime_version()
    if project_version != runtime_version:
        raise ReleaseError(f"project version {project_version!r} differs from runtime version {runtime_version!r}")
    return project_version


def validate_tag(tag: str) -> str:
    """Return the release version when *tag* exactly matches its v-prefixed form."""
    version = _version()
    expected = f"v{version}"
    if tag != expected:
        raise ReleaseError(f"release tag must be {expected!r}, got {tag!r}")
    return version


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _forbidden(name: str) -> bool:
    parts = PurePosixPath(name).parts
    forbidden_parts = {".codex", ".git", ".superpowers", "__pycache__", ".ruff_cache", ".pytest_cache"}
    return bool(forbidden_parts.intersection(parts)) or ("docs" in parts and "superpowers" in parts) or "official" in name.lower()


def _require_archive_names(names: list[str], *, prefix: str, label: str) -> None:
    for name in names:
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or not name.startswith(prefix):
            raise ReleaseError(f"{label} member escapes the source root: {name}")
        if _forbidden(name):
            raise ReleaseError(f"{label} contains forbidden member: {name}")


def _required_package_members(version: str) -> set[str]:
    members = {path.relative_to(ROOT).as_posix() for path in (ROOT / PACKAGE).rglob("*.py")}
    members.add(f"{PACKAGE}/schemas/fdr-record-config-v1.schema.json")
    return members


def _check_metadata(metadata: str, version: str, *, label: str) -> None:
    for field in (f"Name: {PROJECT}", f"Version: {version}", "Requires-Python: >=3.12"):
        if field not in metadata:
            raise ReleaseError(f"{label} metadata is missing {field}")
    if "Requires-Dist:" in metadata:
        raise ReleaseError(f"{label} metadata declares a Requires-Dist runtime dependency")


def _check_wheel(wheel: Path, version: str) -> None:
    expected_name = f"{PACKAGE}-{version}-py3-none-any.whl"
    if wheel.name != expected_name:
        raise ReleaseError(f"wheel must be named {expected_name}")
    dist_info = f"{PACKAGE}-{version}.dist-info"
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        _require_archive_names(names, prefix="", label="wheel")
        for name in names:
            if not (name.startswith(f"{PACKAGE}/") or name.startswith(f"{dist_info}/")):
                raise ReleaseError(f"wheel member is outside the package or dist-info roots: {name}")
        metadata = archive.read(f"{dist_info}/METADATA").decode("utf-8")
        _check_metadata(metadata, version, label="wheel")
        missing = _required_package_members(version).difference(names)
        if missing:
            raise ReleaseError(f"wheel is missing required members: {', '.join(sorted(missing))}")
        licenses = [name for name in names if name.endswith("/LICENSE")]
        if len(licenses) != 1:
            raise ReleaseError(f"wheel must contain exactly one LICENSE, found {len(licenses)}")


def _check_sdist(sdist: Path, version: str) -> None:
    expected_name = f"{PACKAGE}-{version}.tar.gz"
    if sdist.name != expected_name:
        raise ReleaseError(f"sdist must be named {expected_name}")
    root = f"{PACKAGE}-{version}/"
    with tarfile.open(sdist, "r:gz") as archive:
        names = archive.getnames()
        _require_archive_names([name for name in names if name != root.rstrip("/")], prefix=root, label="sdist")
        relative = {name.removeprefix(root) for name in names}
        metadata_stream = archive.extractfile(f"{root}PKG-INFO")
        if metadata_stream is None:
            raise ReleaseError("sdist is missing PKG-INFO")
        _check_metadata(metadata_stream.read().decode("utf-8"), version, label="sdist")
        missing = _required_package_members(version).difference(relative)
        if missing:
            raise ReleaseError(f"sdist is missing required members: {', '.join(sorted(missing))}")
        licenses = [name for name in relative if PurePosixPath(name).name == "LICENSE"]
        if len(licenses) != 1:
            raise ReleaseError(f"sdist must contain exactly one LICENSE, found {len(licenses)}")


def check_dist(directory: Path) -> ReleaseArtifacts:
    """Validate the exact wheel/sdist pair in *directory* and return hashes."""
    version = _version()
    if not directory.is_dir():
        raise ReleaseError(f"distribution directory does not exist: {directory}")
    expected = {f"{PACKAGE}-{version}-py3-none-any.whl", f"{PACKAGE}-{version}.tar.gz"}
    entries = tuple(directory.iterdir())
    if any(path.name == ".gitignore" and not path.is_file() for path in entries):
        raise ReleaseError("dist .gitignore marker must be a file")
    actual = {path.name for path in entries if path.name != ".gitignore"}
    if actual != expected:
        raise ReleaseError(f"dist must contain exactly {sorted(expected)}, found {sorted(actual)}")
    wheel = directory / f"{PACKAGE}-{version}-py3-none-any.whl"
    sdist = directory / f"{PACKAGE}-{version}.tar.gz"
    _check_wheel(wheel, version)
    _check_sdist(sdist, version)
    return ReleaseArtifacts(wheel, sdist, _sha256(wheel), _sha256(sdist))


def main(argv: list[str] | None = None) -> int:
    """Run a non-publishing release validation command."""
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    tag = commands.add_parser("check-tag", help="validate a v-prefixed release tag")
    tag.add_argument("tag")
    dist = commands.add_parser("check-dist", help="validate the local wheel and sdist")
    dist.add_argument("directory", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "check-tag":
            print(validate_tag(args.tag))
        else:
            artifacts = check_dist(args.directory)
            print(
                json.dumps(
                    {
                        "sdist": artifacts.sdist.name,
                        "sdist_sha256": artifacts.sdist_sha256,
                        "wheel": artifacts.wheel.name,
                        "wheel_sha256": artifacts.wheel_sha256,
                    },
                    sort_keys=True,
                )
            )
    except ReleaseError as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
