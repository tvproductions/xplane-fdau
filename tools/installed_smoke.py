"""Smoke-test an installed xplane-fdr wheel without importing its checkout."""

from __future__ import annotations

import importlib.resources
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


class SmokeError(RuntimeError):
    """Report a failure in the installed-wheel contract."""


def parse_version(arguments: list[str]) -> str:
    """Require the one expected distribution version argument."""
    if len(arguments) != 1 or not arguments[0]:
        raise SmokeError("usage: installed_smoke.py VERSION")
    return arguments[0]


def ensure_outside_checkout(imported: Path, checkout: Path) -> None:
    """Reject an import resolved within the source checkout."""
    try:
        imported.resolve().relative_to(checkout.resolve())
    except ValueError:
        return
    raise SmokeError(f"xplane_fdr imported from checkout: {imported}")


def _command_path() -> Path:
    command = shutil.which("xplane-fdr")
    if command is None:
        raise SmokeError("interpreter-local xplane-fdr command was not found on PATH")
    resolved = Path(command).resolve()
    if resolved.parent != Path(sys.executable).resolve().parent:
        raise SmokeError(f"xplane-fdr command is not in this interpreter's scripts directory: {resolved}")
    return resolved


def _run(command: list[str]) -> None:
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise SmokeError(f"command failed ({' '.join(command)}): {result.stderr.strip()}")


def smoke(version: str, *, checkout: Path) -> None:
    """Exercise the installed public API, schema, FDR files, and CLI commands."""
    import xplane_fdr

    location = Path(xplane_fdr.__file__ or "")
    if not location:
        raise SmokeError("xplane_fdr has no import location")
    ensure_outside_checkout(location, checkout)
    if xplane_fdr.__version__ != version:
        raise SmokeError(f"installed version is {xplane_fdr.__version__}, expected {version}")
    for name in xplane_fdr.__all__:
        getattr(xplane_fdr, name)
    schema = importlib.resources.files("xplane_fdr").joinpath("schemas/fdr-record-config-v1.schema.json")
    if not schema.is_file() or '"$schema"' not in schema.read_text(encoding="utf-8"):
        raise SmokeError("installed schema resource is unavailable or invalid")
    command = _command_path()
    fixture_root = checkout / "tests" / "fixtures" / "fdr"
    with tempfile.TemporaryDirectory() as raw:
        work = Path(raw)
        v3 = work / "version3-minimal.fdr"
        v4 = work / "version4-minimal.fdr"
        shutil.copy2(fixture_root / v3.name, v3)
        shutil.copy2(fixture_root / v4.name, v4)
        for fixture in (v3, v4):
            xplane_fdr.FDRReader().read(fixture)
            _run([str(command), "validate", str(fixture)])
        round_trip = work / "round-trip.fdr"
        xplane_fdr.FDRWriter().write(xplane_fdr.FDRReader().read(v4), round_trip)
        if not round_trip.read_bytes().startswith(b"A\n4\n"):
            raise SmokeError("canonical v4 output does not begin with A\\n4\\n")
        xplane_fdr.FDRReader().read(round_trip)
        _run([str(command), "to-geojson", str(v4), str(work / "recording.geojson")])


def main(argv: list[str] | None = None) -> int:
    """Run the installed-wheel smoke test for one exact version."""
    try:
        version = parse_version(sys.argv[1:] if argv is None else argv)
        smoke(version, checkout=Path(__file__).resolve().parents[1])
    except SmokeError as error:
        print(f"installed smoke failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
