"""Smoke-test an installed xplane-fdau wheel without importing its checkout."""

from __future__ import annotations

import importlib
import importlib.resources
import importlib.util
from pathlib import Path
import pkgutil
import subprocess
import sys
import tempfile
from types import ModuleType


MINIMAL_V3 = (
    b"A\n3\nTIME, 18:30:00\nDATE, 08/09/2026\n"
    b"DATA,0,-87.9048,41.9742,640,270,2,-1,29.92,640,0,100,95,98,0,0,0,20,180,10,20,20,28,0,45,180,75,2500,24,10,350,351,352,353,354,355,1300,1301,1302,1303,1304,1305\n"
)
MINIMAL_V4 = b"A\n4\nDATE, 08/09/2026\n18:30:00, -87.9048, 41.9742, 640, 270, 2, -1\n"


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
    raise SmokeError(f"xplane_fdau imported from checkout: {imported}")


def ensure_legacy_package_absent() -> None:
    """Reject an environment that still exposes the unreleased legacy package."""
    if importlib.util.find_spec("xplane_fdr") is not None:
        raise SmokeError("legacy xplane_fdr package is installed")


def import_all_modules(package: ModuleType) -> tuple[str, ...]:
    """Discover and import every module shipped below one installed package."""
    package_path = getattr(package, "__path__", None)
    if package_path is None:
        raise SmokeError(f"{package.__name__} is not an importable package")
    names = (package.__name__, *(module.name for module in pkgutil.walk_packages(package_path, f"{package.__name__}.")))
    for name in names:
        importlib.import_module(name)
    return names


def validate_command_path(command: Path, interpreter: Path) -> Path:
    """Require a console script beside the interpreter without resolving venv symlinks."""
    command_path = command.absolute()
    if command_path.parent != interpreter.absolute().parent:
        raise SmokeError(f"xplane-fdau command is not in this interpreter's scripts directory: {command_path}")
    return command_path


def _command_path() -> Path:
    interpreter = Path(sys.executable)
    scripts = interpreter.absolute().parent
    for name in ("xplane-fdau", "xplane-fdau.exe", "xplane-fdau.cmd"):
        command = scripts / name
        if command.is_file():
            return validate_command_path(command, interpreter)
    raise SmokeError("interpreter-local xplane-fdau command was not found beside the interpreter")


def _run(command: list[str]) -> None:
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise SmokeError(f"command failed ({' '.join(command)}): {result.stderr.strip()}")


def smoke(version: str, *, checkout: Path) -> None:
    """Exercise the installed public API, schema, FDR files, and CLI commands."""
    import xplane_fdau
    import xplane_fdau.formats.xplane_fdr as native_fdr

    location = Path(xplane_fdau.__file__ or "")
    if not location:
        raise SmokeError("xplane_fdau has no import location")
    ensure_outside_checkout(location, checkout)
    if xplane_fdau.__version__ != version:
        raise SmokeError(f"installed version is {xplane_fdau.__version__}, expected {version}")
    ensure_legacy_package_absent()
    import_all_modules(xplane_fdau)
    for name in xplane_fdau.__all__:
        getattr(xplane_fdau, name)
    schema = importlib.resources.files("xplane_fdau.formats.xplane_fdr").joinpath("schemas/fdr-record-config-v1.schema.json")
    if not schema.is_file() or '"$schema"' not in schema.read_text(encoding="utf-8"):
        raise SmokeError("installed schema resource is unavailable or invalid")
    command = _command_path()
    with tempfile.TemporaryDirectory() as raw:
        work = Path(raw)
        v3 = work / "version3-minimal.fdr"
        v4 = work / "version4-minimal.fdr"
        v3.write_bytes(MINIMAL_V3)
        v4.write_bytes(MINIMAL_V4)
        for fixture in (v3, v4):
            native_fdr.FDRReader().read(fixture)
            _run([str(command), "fdr", "validate", str(fixture)])
        round_trip = work / "round-trip.fdr"
        native_fdr.FDRWriter().write(native_fdr.FDRReader().read(v4), round_trip)
        if not round_trip.read_bytes().startswith(b"A\n4\n"):
            raise SmokeError("canonical v4 output does not begin with A\\n4\\n")
        native_fdr.FDRReader().read(round_trip)
        _run([str(command), "fdr", "to-geojson", str(v4), str(work / "recording.geojson")])


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
