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

_FIXTURE_ACCEPTANCE = {
    "T1.1": ("Markdown authority contract and explicit inventory normalization", "Frozen contract is verified and\n  remains explicit."),
    "T1.2": ("Typed parser, status report, and versioned JSON", "Frozen parser remains open."),
}


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


def replace_bytes(root: Path, path: str, old: bytes, new: bytes) -> None:
    """Replace one exact byte sequence without normalizing the fixture file."""
    target = root / Path(path)
    content = target.read_bytes()
    if content.count(old) != 1:
        raise ValueError(f"expected one occurrence of {old!r} in {path}")
    target.write_bytes(content.replace(old, new, 1))


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


def audit_fixture(root: Path) -> None:
    """Create complete, committed audit authorities, separate from syntax fixtures."""
    evidence_fixture(root)
    policy = root / "docs/superpowers/specs/2026-09-05-t1-3-audit-policy-supplement-design.md"
    policy.write_text(
        "# Fixture policy\n\n- **Governance:** active\n- **Status:** approved\n"
        "- **Date:** 2026-09-05\n- **Decision owner:** Fixture\n"
        "- **Roadmap epic:** `T1`\n- **Roadmap children:** `T1.2`\n"
        "- **Approval:** 2026-09-05 — Fixture\n\n"
        "| Child | Historical plan | SHA-256 |\n| --- | --- | --- |\n"
        f"| `T1.1` | `docs/superpowers/plans/historical-plan.md` | `{'0' * 64}` |\n",
        encoding="utf-8",
        newline="\n",
    )
    run_git(root, "add", "--", policy.relative_to(root).as_posix())
    run_git(root, "commit", "-qm", "Fixture policy")


def write_active_design(root: Path, path: str, *, children: tuple[str, ...], status: str = "approved") -> None:
    """Write a minimal active design accepted by the lifecycle audit."""
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    targets = ", ".join(f"`{child}`" for child in children)
    approval = "2026-09-05 — Fixture" if status == "approved" else "—"
    acceptance = "".join(f"\n### {child} — {_FIXTURE_ACCEPTANCE[child][0]}\n\n- {_FIXTURE_ACCEPTANCE[child][1]}\n" for child in children)
    target.write_text(
        "# Fixture design\n\n"
        "- **Governance:** active\n"
        f"- **Status:** {status}\n"
        "- **Date:** 2026-09-05\n"
        "- **Decision owner:** Fixture\n"
        "- **Roadmap epic:** `T1`\n"
        f"- **Roadmap children:** {targets}\n"
        f"- **Approval:** {approval}\n\n## Acceptance criteria\n" + acceptance,
        encoding="utf-8",
        newline="\n",
    )


def write_active_plan(
    root: Path,
    path: str,
    *,
    child: str = "T1.2",
    specification: str = "docs/superpowers/specs/t1-design.md",
    status: str = "approved",
    completion_evidence: str | None = None,
) -> None:
    """Write a minimal active single-child plan accepted by the lifecycle audit."""
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    approval = "2026-09-05 — Fixture" if status in {"approved", "in_progress", "completed"} else "—"
    completion = f"`{completion_evidence}`" if completion_evidence is not None else "—"
    target.write_text(
        "# Fixture plan\n\n"
        "- **Governance:** active\n"
        f"- **Status:** {status}\n"
        "- **Date:** 2026-09-05\n"
        f"- **Roadmap child:** `{child}`\n"
        f"- **Source specification:** `{specification}`\n"
        f"- **Approval:** {approval}\n"
        f"- **Completion evidence:** {completion}\n",
        encoding="utf-8",
        newline="\n",
    )


def reviewed_gate_fixture(root: Path) -> None:
    """Prepare T1.2 for a gate edit with eligible staged child evidence."""
    write_active_plan(
        root,
        "docs/superpowers/plans/t1-2.md",
        status="completed",
        completion_evidence=".superpowers/sdd/t1-2/completion.md",
    )
    write_evidence(root, ".superpowers/sdd/t1-2/completion.md", child="T1.2", gate=None)
    write_evidence(root, ".superpowers/sdd/t1-2/review.md", child="T1.2", gate=None, kind="review", result="accepted")
    replace_text(
        root,
        "BACKLOG.md",
        (
            "| `T1.2` | Typed parser, status report, and versioned JSON | `specified` | `T1.1` | "
            "[design](docs/superpowers/specs/t1-design.md) | — | 0/1 | — | — | — |"
        ),
        (
            "| `T1.2` | Typed parser, status report, and versioned JSON | `reviewed` | `T1.1` | "
            "[design](docs/superpowers/specs/t1-design.md) | [plan](docs/superpowers/plans/t1-2.md) | "
            "0/1 | [review](.superpowers/sdd/t1-2/review.md) | — | — |"
        ),
    )
    run_git(root, "add", "--", ".superpowers")
