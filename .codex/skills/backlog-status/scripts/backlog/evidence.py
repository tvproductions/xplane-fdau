from __future__ import annotations

from pathlib import Path
import re
import stat
import subprocess

from backlog.findings import finding_key
from backlog.model import Finding
from backlog.parse import MarkdownParseError, parse_evidence


class ObservationError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


def _regular_path(root: Path, path: str) -> Path:
    parts = path.split("/")
    if not path.endswith(".md") or path.startswith("/") or "\\" in path or ":" in path or any(part in {"", ".", ".."} for part in parts):
        raise ObservationError("evidence.path", "evidence must be a repository-relative Markdown path")
    target = root / path
    try:
        target.resolve().relative_to(root.resolve())
        if not stat.S_ISREG(target.lstat().st_mode):
            raise ObservationError("evidence.path", "evidence must be a regular file")
    except (OSError, ValueError) as error:
        if isinstance(error, ObservationError):
            raise
        raise ObservationError("evidence.path", "evidence must be an existing contained regular file") from error
    return target


def _git(root: Path, *arguments: str) -> bytes:
    try:
        result = subprocess.run(["git", "--literal-pathspecs", "-C", str(root), *arguments], capture_output=True, check=False, shell=False)
    except OSError as error:
        raise ObservationError("evidence.git", f"cannot inspect Git evidence: {error}") from error
    if result.returncode:
        raise ObservationError("evidence.git", "Git could not establish evidence eligibility")
    return result.stdout


def observed_bytes(root: Path, path: str, *, require_head: bool) -> bytes:
    """Require a regular stage-zero entry and exact worktree/index/optional HEAD bytes."""
    target = _regular_path(root, path)
    try:
        content = target.read_bytes()
    except OSError as error:
        raise ObservationError("evidence.path", f"cannot read evidence: {error}") from error
    entries = _git(root, "ls-files", "--stage", "-z", "--", path).split(b"\0")
    entries = [entry for entry in entries if entry]
    if not entries:
        raise ObservationError("evidence.untracked", "evidence must be present in the Git index")
    if len(entries) != 1:
        raise ObservationError("evidence.dirty", "evidence has an unresolved index conflict")
    header, separator, name = entries[0].partition(b"\t")
    match = re.fullmatch(rb"(100644|100755) ([0-9a-f]+) 0", header)
    if not separator or name != path.encode("utf-8"):
        raise ObservationError("evidence.git", "Git returned an unexpected evidence entry")
    if match is None:
        code = "evidence.path" if header.startswith(b"120000 ") or header.startswith(b"160000 ") else "evidence.dirty"
        raise ObservationError(code, "evidence requires a regular stage-zero Git entry")
    indexed = _git(root, "cat-file", "blob", match.group(2).decode("ascii"))
    if content != indexed:
        raise ObservationError("evidence.dirty", "evidence file bytes differ from the Git index")
    if require_head:
        _head_bytes(root, path, indexed)
    return content


def _head_bytes(root: Path, path: str, indexed: bytes) -> None:
    try:
        entries = _git(root, "ls-tree", "-z", "HEAD", "--", path).split(b"\0")
    except ObservationError as error:
        # An unborn repository has no HEAD; other failures remain Git failures.
        if not _git(root, "rev-parse", "--is-inside-work-tree").strip() == b"true":
            raise error
        if _git(root, "for-each-ref", "--format=%(refname)", "refs/heads/").strip():
            raise error
        raise ObservationError("evidence.not-in-head", "evidence must exist in HEAD") from error
    entries = [entry for entry in entries if entry]
    if len(entries) != 1:
        raise ObservationError("evidence.not-in-head", "evidence must exist in HEAD")
    header, _, name = entries[0].partition(b"\t")
    match = re.fullmatch(rb"(100644|100755) blob ([0-9a-f]+)", header)
    if match is None or name != path.encode("utf-8") or _git(root, "cat-file", "blob", match.group(2).decode("ascii")) != indexed:
        raise ObservationError("evidence.not-in-head", "evidence index bytes must match regular HEAD content")


def evidence_findings(root: Path, path: str, child: str, gate: int | None, *, kinds: frozenset[str], require_head: bool) -> tuple[Finding, ...]:
    """Observe explicit evidence without Git writes or inferred completion."""
    findings: list[Finding] = []

    def add(code: str, message: str, line: int = 1) -> None:
        findings.append(Finding(code, "error", path, line, child, gate, message))

    try:
        observed_bytes(root, path, require_head=require_head)
    except ObservationError as error:
        add(error.code, str(error))
        if error.code == "evidence.path":
            return tuple(findings)
    try:
        artifact = parse_evidence(root, root / path)
    except MarkdownParseError as error:
        add(error.code, error.message, error.line)
        return tuple(sorted(findings, key=finding_key))
    if artifact.child != child:
        add("evidence.child-mismatch", f"evidence Child must equal {child}", 3)
    if artifact.gate != gate:
        add("evidence.gate-mismatch", f"evidence Gate must equal {gate if gate is not None else '—'}", 4)
    if artifact.kind not in kinds:
        add("evidence.kind", "evidence Kind is not eligible for the referring slot", 5)
    expected = {"verification": "passed", "artifact": "passed", "review": "accepted", "approval": "accepted"}.get(artifact.kind)
    if expected is not None and artifact.result != expected:
        add("evidence.result", f"{artifact.kind} evidence requires Result {expected}", 6)
    return tuple(sorted(findings, key=finding_key))
