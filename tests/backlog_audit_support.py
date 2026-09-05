from __future__ import annotations

from pathlib import Path
import shutil


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
