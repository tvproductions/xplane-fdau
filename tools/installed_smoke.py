"""Smoke-test an installed xplane-fdau wheel without importing its checkout."""

from __future__ import annotations

import importlib
import importlib.resources
import importlib.util
import pkgutil
import subprocess
import sys
import tempfile
from pathlib import Path
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
    launch = ["uv", "run", "--offline", "--no-project", "--python", sys.executable, *command]
    result = subprocess.run(launch, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise SmokeError(f"command failed ({' '.join(command)}): {result.stderr.strip()}")


def _canonical_identity_smoke() -> None:
    """Pin the installed C1.2 reference, provenance, and self-hash behavior."""
    from xplane_fdau.contracts import DefinitionRef, ProvenanceSource
    from xplane_fdau.contracts._content_hash import (
        _definition_content_hash,
        _definition_preimage,
        _record_content_hash,
        _record_preimage,
    )
    from xplane_fdau.contracts.identity import _definition_ref_wire
    from xplane_fdau.contracts.provenance import _provenance_source_wire

    reference = DefinitionRef(definition_id="test.altitude", definition_revision=2, definition_hash="a" * 64)
    if _definition_ref_wire(reference) != {
        "definition_id": "test.altitude",
        "definition_revision": 2,
        "definition_hash": "a" * 64,
    }:
        raise SmokeError("installed definition reference differs from the C1.2 contract")
    source = ProvenanceSource(source_id="test.manual", scope="manual", source_revision=1)
    if _provenance_source_wire(source) != {"scope": "manual", "source_id": "test.manual", "source_revision": 1}:
        raise SmokeError("installed provenance differs from the C1.2 contract")
    record: dict[str, object] = {
        "content_hash": "a" * 64,
        "nested": {"content_hash": "b" * 64},
        "record_id": "12345678-1234-1234-8234-123456789abc",
        "value": 1.0,
    }
    record_bytes = (
        b'{"nested":{"content_hash":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"},'
        b'"record_id":"12345678-1234-1234-8234-123456789abc","value":1.0}\n'
    )
    record_digest = "d1bcf9869ac210446527b4ce344db5256a0420a70a4bcc432d73023ac0c9fa3e"  # pragma: allowlist secret
    if _record_preimage(record) != record_bytes or _record_content_hash(record) != record_digest:
        raise SmokeError("installed record hashing differs from the C1.2 contract")
    family = "https://tvproductions.github.io/xplane-fdau/contracts/measurement-catalog"
    definition: dict[str, object] = {
        "content_hash": "a" * 64,
        "authority": {"authority_id": "test.owner", "authority_revision": 1},
        "definition_id": "test.altitude",
        "definition_revision": 2,
        "provenance": [_provenance_source_wire(source)],
        "quantity_id": "test.pressure_altitude",
    }
    definition_bytes = (
        b'{"contract_family":"https://tvproductions.github.io/xplane-fdau/contracts/measurement-catalog",'
        b'"definition":{"authority":{"authority_id":"test.owner","authority_revision":1},'
        b'"definition_id":"test.altitude","definition_revision":2,"provenance":'
        b'[{"scope":"manual","source_id":"test.manual","source_revision":1}],'
        b'"quantity_id":"test.pressure_altitude"},"schema_version":1}\n'
    )
    if (
        _definition_preimage(family, definition) != definition_bytes
        or _definition_content_hash(family, definition) != "4645ff5b3d74719279bd5492047f14355361214f13d8f4ec794ed5145d5f97dd"  # pragma: allowlist secret
    ):
        raise SmokeError("installed definition hashing differs from the C1.2 contract")


def _canonical_values_smoke() -> None:
    """Pin installed typed values, payload declarations, and storage isolation."""
    from xplane_fdau.contracts import ContractShapeError, InlineValue, PayloadReference, PayloadSpec, RepresentationSpec, canonical_bytes

    original = [2.0, 1.0]
    inline = InlineValue(representation="fixed_array", element_representation="real", value=original)
    original.reverse()
    if inline.value != (2.0, 1.0) or canonical_bytes(inline) != b'{"element_representation":"real","representation":"fixed_array","value":[2.0,1.0]}\n':
        raise SmokeError("installed inline value type or order differs from the C1.3 contract")
    declaration = RepresentationSpec(kind="referenced_bytes", payload=PayloadSpec(allowed_media_types=["a/b"], allowed_storage_roles=["test.raw"]))
    if canonical_bytes(declaration) != b'{"kind":"referenced_bytes","payload":{"allowed_media_types":["a/b"],"allowed_storage_roles":["test.raw"]}}\n':
        raise SmokeError("installed payload declaration differs from the C1.3 contract")
    claim = PayloadReference(media_type="a/b", byte_length=2, sha256="a" * 64, storage_role="test.raw", retention_status="missing")
    expected = (
        b'{"byte_length":2,"media_type":"a/b","retention_status":"missing",'
        b'"sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","storage_role":"test.raw"}\n'
    )
    if canonical_bytes(claim) != expected:
        raise SmokeError("installed original payload claim differs from the C1.3 contract")
    try:
        InlineValue(representation="referenced_bytes", value=b"bytes")
    except ContractShapeError:
        return
    raise SmokeError("installed byte-only value was accepted inline")


def _canonical_timing_smoke() -> None:
    """Verify installed timing precision and domain boundaries."""
    import json

    import xplane_fdau.contracts as contracts
    from xplane_fdau.contracts._json_parse import _parse_json_document
    from xplane_fdau.contracts._timing_io import _observation_timing_from_wire

    clock = contracts.ClockDomain(
        clock_domain_id="11111111-1111-4111-8111-111111111111",
        kind="host_monotonic",
        unit="tick",
        resolution=1,
        origin="installed process",
        scope="smoke",
        producer_instance_id="22222222-2222-4222-8222-222222222222",
        tick_period={"numerator_ns": 1, "denominator": 3},
    )
    zero = contracts.ClockReading(clock_domain_id=clock.clock_domain_id, value=0)
    three = contracts.ClockReading(clock_domain_id=clock.clock_domain_id, value=3)
    if contracts.difference_clock_readings_ns(three, zero, clock) != 1 or contracts.compare_clock_readings(zero, three) != -1:
        raise SmokeError("installed clock arithmetic differs from the C1.4 contract")
    utc = contracts.UtcInstant(value="2026-10-26T12:34:56.123456789Z")
    if contracts.canonical_bytes(utc) != b'"2026-10-26T12:34:56.123456789Z"\n':
        raise SmokeError("installed UTC lost nanosecond text")
    try:
        utc.to_datetime()
    except contracts.ContractValidationError:
        pass
    else:
        raise SmokeError("installed UTC conversion silently lost precision")
    anchor = contracts.ClockAnchor(monotonic_reading=three, utc=utc, uncertainty_ns=5)
    minimum = contracts.ObservationTiming(receipt_clock=clock, receipt_reading=three, receipt_utc=utc)
    minimum_wire = contracts.canonical_bytes(minimum)
    if set(json.loads(minimum_wire)) != {"receipt_clock", "receipt_reading", "receipt_utc"}:
        raise SmokeError("installed timing invented optional evidence")
    full = contracts.ObservationTiming(
        receipt_clock=clock,
        receipt_reading=three,
        receipt_utc=utc,
        receipt_anchor=anchor,
        xplane_cycle=0,
        simulator_flight_time_ns=-1,
        acquisition_phase="unknown",
        paused=False,
        replay_state="replay",
        time_speed=-1.0,
    )
    wire = contracts.canonical_bytes(full)
    if _observation_timing_from_wire(_parse_json_document(wire)) != full:
        raise SmokeError("installed receipt anchor or optional timing did not round-trip")
    try:
        contracts.compare_clock_readings(zero, contracts.ClockReading(clock_domain_id="33333333-3333-4333-8333-333333333333", value=0))
    except contracts.ContractValidationError:
        return
    raise SmokeError("installed arithmetic accepted unrelated clocks")


def _measurement_quality_smoke() -> None:
    """Verify installed validity ownership and strict acquisition-quality inputs."""
    import xplane_fdau.measurements as measurements
    from xplane_fdau.contracts.errors import ContractValidationError
    from xplane_fdau.measurements import QualityFlag, ValidityState, _quality, models

    for name in ("ValidityState", "QualityFlag"):
        if getattr(measurements, name) is not getattr(models, name):
            raise SmokeError("installed measurement vocabulary ownership differs")
    if tuple(state.value for state in ValidityState) != ("valid", "invalid", "unknown", "not_applicable"):
        raise SmokeError("installed validity vocabulary differs")
    if tuple(flag.value for flag in QualityFlag) != (
        "conversion_failed",
        "discontinuous",
        "dropped",
        "duplicate",
        "orphaned",
        "out_of_declared_range",
        "precision_lost",
        "provider_degraded",
        "read_error",
        "reordered",
        "rounded",
        "saturated",
        "stale",
        "type_mismatch",
        "unavailable",
    ):
        raise SmokeError("installed acquisition-quality vocabulary differs")
    if _quality._validity_state("unknown") is not ValidityState.UNKNOWN or _quality._quality_flags(()) != ():
        raise SmokeError("installed quality validation changed explicit unknown or empty quality")
    if _quality._quality_flags(("rounded", "stale")) != (QualityFlag.ROUNDED, QualityFlag.STALE):
        raise SmokeError("installed quality validation changed ordered flags")
    for noncanonical in (("stale", "rounded"), ("stale", "stale")):
        try:
            _quality._quality_flags(noncanonical)
        except ContractValidationError as error:
            if error.path != "/quality/1":
                raise SmokeError("installed quality rejection lost its item path") from error
        else:
            raise SmokeError("installed quality validation accepted noncanonical flags")


def smoke(version: str, *, checkout: Path) -> None:
    """Exercise the installed public API, schema, FDR files, and CLI commands."""
    import xplane_fdau
    import xplane_fdau.contracts as contracts
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
    if contracts.canonical_bytes({"test.x": 1.0}) != b'{"test.x":1.0}\n':
        raise SmokeError("installed canonical JSON bytes differ from the C1.1 contract")
    _canonical_identity_smoke()
    _canonical_values_smoke()
    _canonical_timing_smoke()
    _measurement_quality_smoke()
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
