"""Validate local xplane-fdr release artifacts without publishing them."""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from email.parser import BytesParser
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import tarfile
import tomllib
from typing import Callable
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
    if dependencies or project.get("requires-python") != ">=3.12":
        raise ReleaseError("project runtime dependencies and Requires-Python do not match the release contract")
    return version


def _version_from_source(source: bytes, *, label: str) -> str:
    tree = ast.parse(source.decode("utf-8"), filename=label)
    for statement in tree.body:
        if isinstance(statement, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "__version__" for target in statement.targets):
            value = ast.literal_eval(statement.value)
            if isinstance(value, str):
                return value
    raise ReleaseError(f"{label} does not define a string __version__")


def _version() -> str:
    project_version = _project_version()
    runtime_version = _version_from_source((ROOT / PACKAGE / "__init__.py").read_bytes(), label="source __init__.py")
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


def _forbidden(parts: tuple[str, ...]) -> bool:
    forbidden = {".codex", ".git", ".superpowers", "__pycache__", ".ruff_cache", ".pytest_cache"}
    return bool(forbidden.intersection(parts)) or ("docs" in parts and "superpowers" in parts) or "official" in "/".join(parts).lower()


def _safe_member_path(name: str, *, label: str) -> PurePosixPath:
    if not name or "\\" in name or name.startswith("/"):
        raise ReleaseError(f"{label} has an unsafe archive path: {name!r}")
    path = PurePosixPath(name)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts) or path.as_posix() != name:
        raise ReleaseError(f"{label} has an unsafe archive path: {name!r}")
    if _forbidden(path.parts):
        raise ReleaseError(f"{label} contains forbidden member: {name}")
    return path


def _validated_zip_names(archive: zipfile.ZipFile) -> tuple[str, ...]:
    names: list[str] = []
    seen: set[str] = set()
    for info in archive.infolist():
        if stat.S_ISLNK(info.external_attr >> 16):
            raise ReleaseError(f"wheel contains an unsafe link member: {info.filename}")
        if info.is_dir() and (not info.filename.endswith("/") or info.filename.endswith("//")):
            raise ReleaseError(f"wheel has an unsafe archive path: {info.filename!r}")
        name = _safe_member_path(info.filename[:-1] if info.is_dir() else info.filename, label="wheel")
        canonical = name.as_posix()
        if canonical in seen:
            raise ReleaseError(f"wheel contains duplicate member: {canonical}")
        seen.add(canonical)
        if not info.is_dir():
            names.append(canonical)
    return tuple(names)


def _validated_tar_members(archive: tarfile.TarFile, root: str) -> tuple[tarfile.TarInfo, ...]:
    members: list[tarfile.TarInfo] = []
    seen: set[str] = set()
    root_count = 0
    for member in archive.getmembers():
        if member.name == root:
            if not member.isdir():
                raise ReleaseError("sdist root member must be a directory")
            root_count += 1
            continue
        path = _safe_member_path(member.name, label="sdist")
        if not (member.isfile() or member.isdir()):
            raise ReleaseError(f"sdist contains an unsafe link or member type: {member.name}")
        parts = path.parts
        if not parts or parts[0] != root:
            raise ReleaseError(f"sdist member escapes the source root: {member.name}")
        canonical = path.as_posix()
        if canonical in seen:
            raise ReleaseError(f"sdist contains duplicate member: {canonical}")
        seen.add(canonical)
        if member.isfile():
            members.append(member)
    if root_count != 1:
        raise ReleaseError(f"sdist must contain exactly one root directory, found {root_count}")
    return tuple(members)


def _expected_package_files() -> dict[str, bytes]:
    expected: dict[str, bytes] = {}
    for source in (ROOT / PACKAGE).rglob("*"):
        if source.is_file() and (source.suffix == ".py" or source.suffix == ".json" or source.name == "py.typed"):
            expected[source.relative_to(ROOT).as_posix()] = source.read_bytes()
    return expected


def _check_metadata(payload: bytes, version: str, *, label: str) -> None:
    message = BytesParser().parsebytes(payload)
    for field, expected in (("Name", PROJECT), ("Version", version), ("Requires-Python", ">=3.12")):
        if message.get_all(field, []) != [expected]:
            raise ReleaseError(f"{label} metadata must contain exactly {field}: {expected}")
    if message.get_all("Requires-Dist", []):
        raise ReleaseError(f"{label} metadata declares a Requires-Dist runtime dependency")


def _check_package_payloads(read: Callable[[str], bytes], names: set[str], version: str, *, label: str) -> None:
    expected = _expected_package_files()
    package_names = {name for name in names if name.startswith(f"{PACKAGE}/")}
    if package_names != set(expected):
        raise ReleaseError(f"{label} package members differ from the expected runtime module/resource set")
    for name, payload in expected.items():
        if read(name) != payload:
            raise ReleaseError(f"{label} member bytes differ from tracked source: {name}")
    if _version_from_source(read(f"{PACKAGE}/__init__.py"), label=f"{label} __init__.py") != version:
        raise ReleaseError(f"{label} runtime __version__ differs from the release version")


def _check_wheel(wheel: Path, version: str) -> None:
    expected_name = f"{PACKAGE}-{version}-py3-none-any.whl"
    if wheel.name != expected_name:
        raise ReleaseError(f"wheel must be named {expected_name}")
    dist_info = f"{PACKAGE}-{version}.dist-info"
    with zipfile.ZipFile(wheel) as archive:
        names = _validated_zip_names(archive)
        if any(not (name.startswith(f"{PACKAGE}/") or name.startswith(f"{dist_info}/")) for name in names):
            raise ReleaseError("wheel member is outside the package or dist-info roots")
        required = {f"{dist_info}/METADATA", f"{dist_info}/WHEEL", f"{dist_info}/RECORD", f"{dist_info}/licenses/LICENSE"}
        if not required.issubset(names):
            raise ReleaseError("wheel is missing required dist-info members")
        _check_metadata(archive.read(f"{dist_info}/METADATA"), version, label="wheel")
        wheel_metadata = BytesParser().parsebytes(archive.read(f"{dist_info}/WHEEL"))
        if wheel_metadata.get_all("Tag", []) != ["py3-none-any"]:
            raise ReleaseError("wheel WHEEL metadata must contain exactly Tag: py3-none-any")
        if archive.read(f"{dist_info}/licenses/LICENSE") != (ROOT / "LICENSE").read_bytes():
            raise ReleaseError("wheel LICENSE must match the tracked license at its expected location")
        _check_package_payloads(archive.read, set(names), version, label="wheel")


def _check_sdist(sdist: Path, version: str) -> None:
    expected_name = f"{PACKAGE}-{version}.tar.gz"
    if sdist.name != expected_name:
        raise ReleaseError(f"sdist must be named {expected_name}")
    root = f"{PACKAGE}-{version}"
    with tarfile.open(sdist, "r:gz") as archive:
        members = _validated_tar_members(archive, root)
        names = {member.name for member in members}
        relative = {name.removeprefix(f"{root}/") for name in names}
        required = {"PKG-INFO", "pyproject.toml", "LICENSE"}
        if not required.issubset(relative):
            raise ReleaseError("sdist is missing required root members")

        def read(relative_name: str) -> bytes:
            stream = archive.extractfile(f"{root}/{relative_name}")
            if stream is None:
                raise ReleaseError(f"sdist cannot read required member: {relative_name}")
            return stream.read()

        _check_metadata(read("PKG-INFO"), version, label="sdist")
        if read("LICENSE") != (ROOT / "LICENSE").read_bytes() or [name for name in relative if PurePosixPath(name).name == "LICENSE"] != ["LICENSE"]:
            raise ReleaseError("sdist must contain one tracked LICENSE at its expected location")
        _check_package_payloads(read, relative, version, label="sdist")


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
            print(json.dumps(artifacts.__dict__, default=str, sort_keys=True))
    except ReleaseError as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
