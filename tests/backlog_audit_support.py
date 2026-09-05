from __future__ import annotations

from pathlib import Path
import shutil
import subprocess


FIXTURE = Path(__file__).resolve().parent / "fixtures" / "backlog_status" / "valid"

AUDIT_VALID_DESIGN_ACCEPTANCE = """\
## Acceptance criteria

### T1.1 — Markdown authority contract and explicit inventory normalization

- Frozen contract is verified and
  remains explicit.

### T1.2 — Typed parser, status report, and versioned JSON

- Frozen parser remains open.
"""


def copy_fixture(root: Path) -> None:
    shutil.copytree(FIXTURE, root, dirs_exist_ok=True)
    with (root / "ROADMAP.md").open("a", encoding="utf-8", newline="\n") as stream:
        stream.write("\n## Version 0.1.0 release gates\n\n- [ ] A separate release review authorizes publication.\n")
    design = root / "docs/superpowers/specs/t1-design.md"
    design.write_text(
        design.read_text(encoding="utf-8").rstrip() + "\n\n" + AUDIT_VALID_DESIGN_ACCEPTANCE,
        encoding="utf-8",
        newline="\n",
    )
    replace_text(
        root,
        "docs/superpowers/specs/historical-design.md",
        "Superseded fixture design.",
        "Superseded by `docs/superpowers/specs/t1-design.md`.",
    )
    replace_text(
        root,
        "docs/superpowers/plans/historical-plan.md",
        "Completed fixture plan.",
        "Completed under `M0`.",
    )


def replace_text(root: Path, path: str, old: str, new: str) -> None:
    target = root / Path(path)
    content = target.read_text(encoding="utf-8")
    if content.count(old) != 1:
        raise ValueError(f"expected one occurrence of {old!r} in {path}")
    target.write_text(content.replace(old, new, 1), encoding="utf-8", newline="\n")


def run_git(root: Path, *arguments: str, data: bytes | None = None) -> bytes:
    return subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "-c",
            "core.hooksPath=",
            "-c",
            "commit.gpgsign=false",
            "-c",
            "core.autocrlf=false",
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            *arguments,
        ],
        input=data,
        capture_output=True,
        check=True,
        shell=False,
    ).stdout


def initialize_git(root: Path) -> None:
    run_git(root, "init", "-q")
    run_git(root, "config", "core.autocrlf", "false")
    run_git(root, "add", "-f", "--", ".")
    run_git(root, "commit", "-qm", "Fixture baseline")


def write_evidence(
    root: Path, path: str, *, child: str = "T1.1", gate: int | None = 1, kind: str = "verification", result: str = "passed", newline: str = "\n"
) -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    ordinal = "—" if gate is None else f"`{gate}`"
    target.write_text(
        f"# Evidence\n\n- **Child:** `{child}`\n- **Gate:** {ordinal}\n"
        f"- **Kind:** {kind}\n- **Result:** {result}\n- **Date:** 2026-09-05\n"
        "- **Subject:** Verified fixture contract\n\nInspected fixture.\n",
        encoding="utf-8",
        newline=newline,
    )


def evidence_fixture(root: Path) -> None:
    copy_fixture(root)
    write_evidence(root, ".superpowers/sdd/t1-1/gate-1.md")
    write_evidence(root, ".superpowers/sdd/t1-1/completion.md", gate=None)
    write_evidence(root, ".superpowers/sdd/t1-1/review.md", gate=None, kind="review", result="accepted")
    replace_text(
        root,
        "BACKLOG.md",
        "- Active child: —.",
        "- Active child: —.\n- Release, tag, and package publication: prohibited pending their separate gates and authorization.",
    )
    initialize_git(root)
