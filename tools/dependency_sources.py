"""Read official PyPI Index JSON evidence for dependency refresh."""

from __future__ import annotations

import json
from html.parser import HTMLParser
from pathlib import Path
import re
from collections.abc import Callable
from typing import Any, cast, override
from urllib.parse import parse_qs, quote, unquote, urlparse
from urllib.request import Request, urlopen

from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.utils import InvalidSdistFilename, InvalidWheelFilename, canonicalize_name, parse_sdist_filename, parse_wheel_filename
from packaging.version import InvalidVersion, Version

INDEX_MEDIA_TYPE = "application/vnd.pypi.simple.v1+json"
INDEX_CEILING = 5 * 1024 * 1024
Opener = Callable[[Request, int, int], tuple[bytes, str, str]]
Runner = Callable[[tuple[str, ...], Path], tuple[int, str, str]]


class SourceError(ValueError):
    """Official source evidence is absent, malformed, or untrusted."""


def open_index(request: Request, timeout: int, ceiling: int) -> tuple[bytes, str, str]:
    """Retrieve one bounded Index JSON response."""
    with urlopen(request, timeout=timeout) as response:  # noqa: S310 - the caller fixes the official HTTPS origin
        body = response.read(ceiling + 1)
        final_url = response.geturl()
        content_type = response.headers.get("Content-Type", "")
        if not isinstance(body, bytes) or not isinstance(final_url, str) or not isinstance(content_type, str):
            raise SourceError("invalid Index transport response")
        return body, final_url, content_type


class _HtmlIndexParser(HTMLParser):
    """Read only official distribution links from a bounded Simple HTML page."""

    def __init__(self, package_name: str) -> None:
        super().__init__()
        self.package_name = package_name
        self.files: list[dict[str, object]] = []
        self.versions: set[str] = set()

    @override
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        values = dict(attrs)
        href = values.get("href")
        if not isinstance(href, str):
            raise SourceError(f"{self.package_name}: missing HTML Index link")
        parsed = urlparse(href)
        if parsed.scheme != "https" or parsed.hostname != "files.pythonhosted.org":
            raise SourceError(f"{self.package_name}: untrusted HTML Index artifact URL")
        filename = unquote(Path(parsed.path).name)
        sha256 = parse_qs(parsed.fragment).get("sha256", [None])[0]
        item: dict[str, object] = {
            "filename": filename,
            "hashes": {"sha256": sha256} if sha256 is not None else {},
            "yanked": "data-yanked" in values,
            "requires-python": values.get("data-requires-python"),
        }
        self.files.append(item)
        try:
            artifact_name, version = _artifact_identity(filename)
        except SourceError:
            return  # Legacy, unrelated formats cannot establish a selectable release.
        if artifact_name == self.package_name:
            self.versions.add(str(version))


def _trusted_index_response(name: str, body: bytes, final_url: str, ceiling: int) -> None:
    parsed_url = urlparse(final_url)
    if parsed_url.scheme != "https" or parsed_url.hostname != "pypi.org" or len(body) > ceiling:
        raise SourceError(f"{name}: untrusted or oversized Index response")


def fetch_index(name: str, opener: Opener) -> dict[str, object]:
    """Fetch and validate one package's official bounded Index document."""
    if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?", name):
        raise SourceError(f"{name}: invalid package name")
    normalized_name = canonicalize_name(name)
    index_url = f"https://pypi.org/simple/{normalized_name}/"
    request = Request(index_url, headers={"Accept": INDEX_MEDIA_TYPE})
    try:
        body, final_url, content_type = opener(request, 15, INDEX_CEILING)
    except (OSError, ValueError) as error:
        raise SourceError(f"{normalized_name}: Index request failed: {error}") from error
    parsed_url = urlparse(final_url)
    if parsed_url.scheme != "https" or parsed_url.hostname != "pypi.org":
        raise SourceError(f"{normalized_name}: untrusted or oversized Index response")
    if len(body) > INDEX_CEILING and content_type.split(";", 1)[0].strip() == INDEX_MEDIA_TYPE:
        html_request = Request(index_url, headers={"Accept": "text/html"})
        try:
            html_body, html_url, html_type = opener(html_request, 15, INDEX_CEILING)
        except (OSError, ValueError) as error:
            raise SourceError(f"{normalized_name}: HTML Index request failed: {error}") from error
        _trusted_index_response(normalized_name, html_body, html_url, INDEX_CEILING)
        if html_type.split(";", 1)[0].strip() != "text/html":
            raise SourceError(f"{normalized_name}: unexpected HTML Index content type")
        try:
            parser = _HtmlIndexParser(normalized_name)
            parser.feed(html_body.decode("utf-8"))
            parser.close()
        except UnicodeDecodeError as error:
            raise SourceError(f"{normalized_name}: invalid HTML Index encoding") from error
        if not parser.files or not parser.versions:
            raise SourceError(f"{normalized_name}: HTML Index has no usable artifacts")
        return {"name": normalized_name, "versions": sorted(parser.versions), "files": parser.files}
    _trusted_index_response(normalized_name, body, final_url, INDEX_CEILING)
    if content_type.split(";", 1)[0].strip() != INDEX_MEDIA_TYPE:
        raise SourceError(f"{normalized_name}: unexpected Index content type")
    try:
        index = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise SourceError(f"{normalized_name}: invalid Index JSON") from error
    if not isinstance(index, dict):
        raise SourceError(f"{normalized_name}: Index root must be an object")
    if canonicalize_name(str(index.get("name", ""))) != normalized_name:
        raise SourceError(f"{normalized_name}: Index package identity mismatch")
    if not isinstance(index.get("versions"), list) or not isinstance(index.get("files"), list):
        raise SourceError(f"{normalized_name}: Index versions and files are required")
    return cast(dict[str, object], index)


def fetch_release_requirements(name: str, version: str, opener: Opener) -> list[str]:
    """Read bounded official metadata for one exact PyPI release."""
    normalized_name = canonicalize_name(name)
    try:
        parsed_version = Version(version)
    except InvalidVersion as error:
        raise SourceError(f"{normalized_name}: invalid release version: {version}") from error
    path = f"/pypi/{normalized_name}/{quote(version, safe='')}/json"
    url = f"https://pypi.org{path}"
    try:
        body, final_url, content_type = opener(Request(url, headers={"Accept": "application/json"}), 15, INDEX_CEILING)
    except (OSError, ValueError) as error:
        raise SourceError(f"{normalized_name}: release metadata request failed: {error}") from error
    parsed_url = urlparse(final_url)
    if parsed_url.scheme != "https" or parsed_url.hostname != "pypi.org" or parsed_url.path != path or len(body) > INDEX_CEILING:
        raise SourceError(f"{normalized_name}: untrusted or oversized release metadata")
    if content_type.split(";", 1)[0].strip() != "application/json":
        raise SourceError(f"{normalized_name}: unexpected release metadata content type")
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise SourceError(f"{normalized_name}: invalid release JSON") from error
    info = payload.get("info") if isinstance(payload, dict) else None
    if not isinstance(info, dict) or canonicalize_name(str(info.get("name", ""))) != normalized_name or str(info.get("version")) != str(parsed_version):
        raise SourceError(f"{normalized_name}: release metadata identity mismatch")
    requirements = info.get("requires_dist")
    if not isinstance(requirements, list) or any(not isinstance(item, str) for item in requirements):
        raise SourceError(f"{normalized_name}: missing or invalid requires_dist")
    return cast(list[str], requirements)


def _artifact_identity(filename: str) -> tuple[str, Version]:
    try:
        name, version, _, _ = parse_wheel_filename(filename)
    except InvalidWheelFilename:
        try:
            name, version = parse_sdist_filename(filename)
        except InvalidSdistFilename as error:
            raise SourceError(f"invalid artifact filename: {filename}") from error
    return canonicalize_name(name), version


def release_python_exclusions(index: dict[str, object], version: str, supported: tuple[Version, ...]) -> tuple[list[str], list[str]]:
    """Return supported Python minors excluded by every non-yanked official file."""
    name = canonicalize_name(str(index.get("name", "")))
    files = index.get("files")
    if not isinstance(files, list):
        raise SourceError(f"{name}: missing release files")
    try:
        expected = (name, Version(version))
    except InvalidVersion as error:
        raise SourceError(f"{name}: invalid release version") from error
    specifiers: list[SpecifierSet] = []
    requirements: set[str] = set()
    for item in files:
        if not isinstance(item, dict) or not isinstance(item.get("filename"), str):
            raise SourceError(f"{name}: malformed Index file")
        try:
            identity = _artifact_identity(item["filename"])
        except SourceError:
            continue
        if identity != expected or item.get("yanked", False):
            continue
        requirement = item.get("requires-python")
        if requirement is None:
            requirement = ""
        if not isinstance(requirement, str):
            raise SourceError(f"{name}: invalid Requires-Python metadata")
        try:
            specifiers.append(SpecifierSet(requirement))
        except InvalidSpecifier as error:
            raise SourceError(f"{name}: invalid Requires-Python metadata") from error
        requirements.add(requirement or "(unconstrained)")
    if not specifiers:
        raise SourceError(f"{name}: no non-yanked files for {version}")
    excluded = [str(python) for python in supported if not any(python in specifier for specifier in specifiers)]
    return excluded, sorted(requirements)


def newest_stable_release(index: dict[str, object]) -> str:
    """Select the newest stable version with a non-yanked official file."""
    package_name = str(index.get("name", ""))
    versions = index.get("versions")
    files = index.get("files")
    if not isinstance(versions, list) or not isinstance(files, list):
        raise SourceError(f"{package_name}: Index versions and files are required")
    available: set[Version] = set()
    invalid_files: list[str] = []
    for item in files:
        if not isinstance(item, dict) or not isinstance(item.get("filename"), str):
            raise SourceError(f"{package_name}: malformed Index file")
        filename = item["filename"]
        try:
            artifact_name, version = _artifact_identity(filename)
        except SourceError:
            invalid_files.append(filename)
            continue
        if artifact_name == canonicalize_name(package_name) and not item.get("yanked", False):
            available.add(version)
    stable: list[Version] = []
    for value in versions:
        try:
            version = Version(str(value))
        except InvalidVersion as error:
            raise SourceError(f"{package_name}: invalid Index version: {value}") from error
        if version in available and not version.is_prerelease and not version.is_devrelease:
            stable.append(version)
    if not stable:
        if invalid_files and not available:
            raise SourceError(f"{package_name}: invalid artifact filename: {invalid_files[0]}")
        raise SourceError(f"{package_name}: no stable non-yanked release")
    return str(max(stable))


def release_is_yanked(index: dict[str, object], version: str, sha256: str) -> bool:
    """Return the yank state of the one official artifact matching a locked hash."""
    package_name = str(index.get("name", ""))
    files = index.get("files")
    if not isinstance(files, list) or not re.fullmatch(r"[0-9a-f]{64}", sha256):
        raise SourceError(f"{package_name}: invalid locked artifact evidence")
    try:
        expected_version = Version(version)
    except InvalidVersion as error:
        raise SourceError(f"{package_name}: invalid locked version") from error
    expected = (canonicalize_name(package_name), expected_version)
    matches: list[dict[str, Any]] = []
    for item in files:
        if not isinstance(item, dict) or not isinstance(item.get("filename"), str):
            raise SourceError(f"{package_name}: malformed Index file")
        hashes = item.get("hashes")
        if not isinstance(hashes, dict) or hashes.get("sha256") != sha256:
            continue
        try:
            identity = _artifact_identity(item["filename"])
        except SourceError as error:
            raise SourceError(f"{package_name}: {error}") from error
        if identity == expected:
            matches.append(item)
    if len(matches) != 1:
        raise SourceError(f"{package_name}: locked artifact has no unique official hash match")
    return bool(matches[0].get("yanked", False))
