from __future__ import annotations

from pathlib import Path
import shutil


FIXTURE = Path(__file__).resolve().parent / "fixtures" / "backlog_status" / "valid"


def copy_fixture(root: Path) -> None:
    shutil.copytree(FIXTURE, root, dirs_exist_ok=True)


def replace_text(root: Path, path: str, old: str, new: str) -> None:
    target = root / Path(path)
    content = target.read_text(encoding="utf-8")
    if content.count(old) != 1:
        raise ValueError(f"expected one occurrence of {old!r} in {path}")
    target.write_text(content.replace(old, new, 1), encoding="utf-8", newline="\n")
