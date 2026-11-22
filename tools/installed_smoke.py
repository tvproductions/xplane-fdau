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
    result = subprocess.run(launch, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
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


def _measurement_definition_smoke() -> None:
    """Verify installed definition ownership, identity, immutability and rejection."""
    import hashlib
    import json
    from dataclasses import FrozenInstanceError, replace

    import xplane_fdau.measurements as measurements
    from xplane_fdau.contracts import Authority, ContractHashError, ContractValidationError, ProvenanceSource, RepresentationSpec, UnitSpec
    from xplane_fdau.measurements import _definition_io, models

    for name in (
        "EnumerationMemberKind",
        "InterpolationPolicy",
        "DiscontinuityPolicy",
        "Sensitivity",
        "AxisSpec",
        "CoordinateSpec",
        "NumericSpec",
        "EnumerationMember",
        "EnumerationSpec",
        "FreshnessSpec",
        "ApplicabilitySelector",
        "MeasurementDefinition",
    ):
        if getattr(measurements, name) is not getattr(models, name):
            raise SmokeError("installed measurement definition ownership differs")
    limitations = ["Synthetic example only"]
    value = measurements.MeasurementDefinition(
        definition_id="test.boolean",
        definition_revision=1,
        authority=Authority(authority_id="test.authority", authority_revision=1),
        provenance=[ProvenanceSource(source_id="test.source", source_revision=1, scope="Synthetic")],
        title="Boolean",
        description="Synthetic Boolean meaning",
        limitations=limitations,
        quantity_id="test.state",
        representation=RepresentationSpec(kind="boolean"),
        unit=UnitSpec(kind="unitless"),
        coordinates=measurements.CoordinateSpec(kind="not_applicable"),
        freshness=measurements.FreshnessSpec(fresh_for_ns=0),
        interpolation_policy="prohibited",
        discontinuity_policy="preserve",
        allowed_validity=["unknown"],
        allowed_quality=[],
        sensitivity="unknown",
        applicability=[],
    )
    wire = _definition_io._measurement_definition_wire(value)
    canonical = json.dumps(wire, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8") + b"\n"
    if _definition_io._measurement_definition_bytes(value) != canonical:
        raise SmokeError("installed measurement definition canonical entry bytes differ")
    body = {key: child for key, child in wire.items() if key != "content_hash"}

    def digest(fields: dict[str, object]) -> str:
        preimage = dict(
            contract_family="https://tvproductions.github.io/xplane-fdau/contracts/measurement-catalog",
            schema_version=1,
            definition=fields,
        )
        return hashlib.sha256(json.dumps(preimage, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8") + b"\n").hexdigest()

    if value.content_hash != digest(body) or wire.get("content_hash") != value.content_hash:
        raise SmokeError("installed measurement definition hash differs")
    restored = _definition_io._measurement_definition_from_wire(json.loads(canonical))
    if restored != value or restored.content_hash != value.content_hash or _definition_io._measurement_definition_bytes(restored) != canonical:
        raise SmokeError("installed measurement definition did not round-trip")
    limitations.append("Caller mutation")
    if value.limitations != ("Synthetic example only",) or _definition_io._measurement_definition_bytes(value) != canonical:
        raise SmokeError("installed measurement definition retained mutable input")
    for name, changed in (("title", "Tampered"), ("content_hash", "0" * 64)):
        try:
            setattr(value, name, changed)
        except (FrozenInstanceError, AttributeError, TypeError):
            pass
        else:
            raise SmokeError("installed measurement definition is mutable")
    try:
        replace(value, numeric=measurements.NumericSpec(storage_precision_bits=1, resolution=1))
    except ContractValidationError as error:
        if error.path != "/numeric":
            raise SmokeError("installed irrelevant numeric rejection lost its path") from error
    else:
        raise SmokeError("installed constructor accepted irrelevant numeric metadata")
    numeric = body | {"numeric": {"storage_precision_bits": 1, "resolution": 1}}
    for tampered, expected, message in (
        (numeric | {"content_hash": digest(numeric)}, ContractValidationError, "irrelevant numeric"),
        (wire | {"title": "Tampered"}, ContractHashError, "stale hash"),
    ):
        try:
            _definition_io._measurement_definition_from_wire(tampered)
        except expected as error:
            expected_path = "/numeric" if expected is ContractValidationError else "/content_hash"
            if error.path != expected_path:
                raise SmokeError(f"installed {message} rejection lost its path") from error
        else:
            raise SmokeError(f"installed reader accepted {message}")


def smoke_measurement_catalog() -> None:
    """Prove installed catalog identity, strict rejection and schema access."""
    import hashlib
    import io
    import json
    from dataclasses import replace

    from xplane_fdau import measurements
    from xplane_fdau.contracts import (
        Authority,
        ContractHashError,
        ContractValidationError,
        DefinitionRef,
        ProvenanceSource,
        RepresentationSpec,
        UnitSpec,
        UnsupportedContractVersionError,
    )

    authority = Authority(authority_id="test.authority", authority_revision=1)
    sources = [ProvenanceSource(source_id="test.source", scope="Synthetic", source_revision=1)]
    definition = measurements.MeasurementDefinition(
        definition_id="test.boolean",
        definition_revision=1,
        authority=authority,
        provenance=sources,
        title="Boolean",
        description="Boolean meaning",
        limitations=[],
        quantity_id="test.state",
        representation=RepresentationSpec(kind="boolean"),
        unit=UnitSpec(kind="unitless"),
        coordinates=measurements.CoordinateSpec(kind="not_applicable"),
        freshness=measurements.FreshnessSpec(fresh_for_ns=0),
        interpolation_policy="prohibited",
        discontinuity_policy="preserve",
        allowed_validity=["unknown"],
        allowed_quality=[],
        sensitivity="unknown",
        applicability=[],
    )
    value = measurements.MeasurementCatalog(
        contract_family="https://tvproductions.github.io/xplane-fdau/contracts/measurement-catalog",
        schema_version=1,
        catalog_id="test.catalog",
        catalog_revision=1,
        authority=authority,
        provenance=sources,
        definitions=[definition],
    )
    if (
        definition.content_hash != "f54509db50da50bd1c72c59ed3b4ce736d97ff31c16cdc07e5790ccd55a745b9"
        or value.content_hash != "b1778b9c7eb974c8b52cf3a4d0ea18f11338f55e4e2b5c3eea9a5ff819639366"
    ):
        raise SmokeError("installed catalog or definition hash differs from the independent vector")
    encoded = measurements.dumps_measurement_catalog_v1(value)
    loaded = measurements.loads_measurement_catalog_v1(encoded)
    stream = io.BytesIO()
    measurements.dump_measurement_catalog_v1(value, stream)
    if stream.getvalue() != encoded or stream.closed:
        raise SmokeError("installed catalog binary dump differs or closed its stream")
    stream.seek(0)
    if measurements.load_measurement_catalog_v1(stream) != loaded or stream.closed:
        raise SmokeError("installed catalog binary load differs or closed its stream")
    if loaded != value or loaded.content_hash != value.content_hash or measurements.dumps_measurement_catalog_v1(loaded) != encoded:
        raise SmokeError("installed catalog round trip differs")
    before = DefinitionRef(definition_id=definition.definition_id, definition_revision=definition.definition_revision, definition_hash=definition.content_hash)
    entry = loaded.definitions[0]
    after = DefinitionRef(definition_id=entry.definition_id, definition_revision=entry.definition_revision, definition_hash=entry.content_hash)
    if before != after:
        raise SmokeError("installed catalog lost an exact definition reference")
    pair = replace(value, definitions=[definition, replace(definition, definition_revision=2)])
    raw = json.loads(measurements.dumps_measurement_catalog_v1(pair))
    raw["definitions"].reverse()
    del raw["content_hash"]
    # This synthetic vector contains only ASCII strings and integer tokens.
    raw["content_hash"] = hashlib.sha256(json.dumps(raw, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n").hexdigest()
    try:
        measurements.loads_measurement_catalog_v1(json.dumps(raw))
    except ContractValidationError as error:
        if error.path != "/definitions/1/definition_revision":
            raise SmokeError("installed catalog ordering rejection lost its path") from error
    else:
        raise SmokeError("installed catalog accepted noncanonical definition order")
    for field, changed, error_type in (("content_hash", "0" * 64, ContractHashError), ("schema_version", 2, UnsupportedContractVersionError)):
        raw = json.loads(encoded)
        raw[field] = changed
        try:
            measurements.loads_measurement_catalog_v1(json.dumps(raw))
        except error_type:
            pass
        else:
            raise SmokeError(f"installed catalog accepted invalid {field}")
    schema_bytes = importlib.resources.files("xplane_fdau.schemas").joinpath("measurement-catalog-v1.schema.json").read_bytes()
    try:
        schema = json.loads(schema_bytes)
    except (ValueError, UnicodeError) as error:
        raise SmokeError("installed measurement catalog schema is invalid JSON") from error
    if (
        schema.get("$id") != "https://tvproductions.github.io/xplane-fdau/schemas/measurement-catalog-v1.schema.json"
        or schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
        or schema.get("unevaluatedProperties") is not False
        or not schema_bytes.endswith(b"\n")
    ):
        raise SmokeError("installed measurement catalog schema identity or closure differs")


def smoke_source_binding_definition() -> None:
    """Exercise installed binding constructors without a catalog or executor."""
    from dataclasses import FrozenInstanceError, replace

    import xplane_fdau.bindings as bindings
    from xplane_fdau.contracts import (
        AdapterIdentity,
        AlgorithmRef,
        Authority,
        ContractValidationError,
        DefinitionRef,
        ProvenanceSource,
        ProviderIdentity,
        ShapeSpec,
        UnitSpec,
        ValueRepresentation,
    )

    selection = {"kind": "index", "index": 0}
    parameters = {"test.factor": [1, 1.0]}
    unit = UnitSpec(kind="unit", quantity_id="test.length", unit_id="test.feet")
    source = bindings.SourceSpec(
        provider=ProviderIdentity(provider_family_id="test.provider", provider_version="1"),
        adapter=AdapterIdentity(adapter_family_id="test.adapter", adapter_version="1"),
        resource_kind="test.resource",
        resource_id="test.primary",
        resource_selection=selection,
        declared_representation=ValueRepresentation.REAL,
        declared_shape=ShapeSpec(kind="scalar"),
        native_unit=unit,
    )
    reference = DefinitionRef(definition_id="test.measurement", definition_revision=1, definition_hash="b" * 64)
    policy = bindings.FailurePolicy(
        unavailable=bindings.FailureDisposition.REJECT,
        orphaned=bindings.FailureDisposition.REJECT,
        stale=bindings.FailureDisposition.REJECT,
        read_error=bindings.FailureDisposition.REJECT,
        type_mismatch=bindings.FailureDisposition.REJECT,
        provider_degraded=bindings.FailureDisposition.REJECT,
    )
    step = bindings.TransformStep(
        step_id="test.convert",
        algorithm=AlgorithmRef(definition_id="test.convert", definition_revision=1, definition_hash="a" * 64, parameters=parameters),
        inputs=[bindings.TransformInput(input_id="binding.primary", representation=ValueRepresentation.REAL, shape=ShapeSpec(kind="scalar"), unit=unit)],
        output_representation=ValueRepresentation.REAL,
        output_shape=ShapeSpec(kind="scalar"),
        output_unit=unit,
    )

    def make(steps: list[bindings.TransformStep]) -> bindings.SourceBindingDefinition:
        return bindings.SourceBindingDefinition(
            definition_id="test.binding",
            definition_revision=1,
            authority=Authority(authority_id="test.authority", authority_revision=1),
            provenance=[ProvenanceSource(source_id="test.source", scope="synthetic", source_revision=1)],
            measurement_ref=reference,
            source=source,
            applicability=[],
            dependencies=[],
            companions=[],
            transforms=steps,
            failure_policy=policy,
            acquisition_phase=bindings.AcquisitionPhase.UNKNOWN,
            replay_policy=bindings.BindingReplayPolicy.PRESERVE,
            limitations=[],
        )

    direct, transformed = make([]), make([step])
    for value, digest in (
        (direct, "d6478ba9fa8a62118c6f452cd96d74b08737be739177297e26f08ad901aebd40"),
        (transformed, "4d4ac78007260dc377d69cc4e198f66169e8b2220cf464093fe2ad88c0be1122"),
    ):
        if value.content_hash != digest or value.measurement_ref != reference:
            raise SmokeError("installed binding hash or exact measurement reference differs")
        try:
            field_name = "definition_revision"
            setattr(value, field_name, 2)
        except FrozenInstanceError:
            pass
        else:
            raise SmokeError("installed binding is mutable")
    if transformed.transforms[0].algorithm != step.algorithm or step.algorithm.definition_hash != "a" * 64:
        raise SmokeError("installed binding lost its algorithm reference")
    selection["index"] = 99
    parameters["test.factor"].append(2)
    if source.resource_selection != {"kind": "index", "index": 0} or step.algorithm.parameters != {"test.factor": (1, 1.0)}:
        raise SmokeError("installed binding retained mutable selection or parameters")
    if transformed.content_hash != "4d4ac78007260dc377d69cc4e198f66169e8b2220cf464093fe2ad88c0be1122":
        raise SmokeError("installed binding identity changed after caller mutation")
    try:
        make([replace(step, inputs=[replace(step.inputs[0], input_id="test.future")])])
    except ContractValidationError as error:
        if error.path != "/transforms/0/inputs/0/input_id":
            raise SmokeError("installed forward-edge rejection lost its path") from error
    else:
        raise SmokeError("installed binding accepted a forward edge")
    try:
        replace(policy, unavailable="accept_flagged")
    except ContractValidationError as error:
        if error.path != "/unavailable":
            raise SmokeError("installed failure policy rejection lost its path") from error
    else:
        raise SmokeError("installed binding accepted an unusable flagged policy")


def smoke_source_binding_catalog() -> None:
    """Prove installed public catalog interchange, compatibility and schema access."""
    import hashlib
    import io
    import json
    from dataclasses import replace

    from xplane_fdau import bindings, measurements
    from xplane_fdau.contracts import (
        AdapterIdentity,
        AlgorithmRef,
        Authority,
        ContractValidationError,
        DefinitionRef,
        FDAUContractError,
        ProvenanceSource,
        ProviderIdentity,
        RepresentationSpec,
        ShapeSpec,
        UnitSpec,
        ValueRepresentation,
    )

    authority = Authority(authority_id="test.authority", authority_revision=1)
    provenance = [ProvenanceSource(source_id="test.source", scope="Synthetic", source_revision=1)]
    unit = UnitSpec(kind="unitless")
    measurement = measurements.MeasurementDefinition(
        definition_id="test.boolean",
        definition_revision=1,
        authority=authority,
        provenance=provenance,
        title="Boolean",
        description="Boolean meaning",
        limitations=[],
        quantity_id="test.state",
        representation=RepresentationSpec(kind="boolean"),
        unit=unit,
        coordinates=measurements.CoordinateSpec(kind="not_applicable"),
        freshness=measurements.FreshnessSpec(fresh_for_ns=0),
        interpolation_policy="prohibited",
        discontinuity_policy="preserve",
        allowed_validity=["unknown"],
        allowed_quality=[],
        sensitivity="unknown",
        applicability=[],
    )
    measurement_catalog = measurements.MeasurementCatalog(
        contract_family="https://tvproductions.github.io/xplane-fdau/contracts/measurement-catalog",
        schema_version=1,
        catalog_id="test.measurements",
        catalog_revision=1,
        authority=authority,
        provenance=provenance,
        definitions=[measurement],
    )
    reference = DefinitionRef(
        definition_id=measurement.definition_id, definition_revision=measurement.definition_revision, definition_hash=measurement.content_hash
    )
    source = bindings.SourceSpec(
        provider=ProviderIdentity(provider_family_id="test.provider", provider_version="1"),
        adapter=AdapterIdentity(adapter_family_id="test.adapter", adapter_version="1"),
        resource_kind="test.resource",
        resource_id="test.primary",
        declared_representation=ValueRepresentation.BOOLEAN,
        declared_shape=ShapeSpec(kind="scalar"),
        native_unit=unit,
    )
    reject = bindings.FailureDisposition.REJECT
    policy = bindings.FailurePolicy(unavailable=reject, orphaned=reject, stale=reject, read_error=reject, type_mismatch=reject, provider_degraded=reject)
    direct = bindings.SourceBindingDefinition(
        definition_id="test.direct",
        definition_revision=1,
        authority=authority,
        provenance=provenance,
        measurement_ref=reference,
        source=source,
        applicability=[],
        dependencies=[],
        companions=[],
        transforms=[],
        failure_policy=policy,
        acquisition_phase=bindings.AcquisitionPhase.UNKNOWN,
        replay_policy=bindings.BindingReplayPolicy.PRESERVE,
        limitations=[],
    )
    step = bindings.TransformStep(
        step_id="test.identity",
        algorithm=AlgorithmRef(definition_id="test.opaque", definition_revision=1, definition_hash="a" * 64, parameters={"test.marker": 1}),
        inputs=[bindings.TransformInput(input_id="binding.primary", representation=ValueRepresentation.BOOLEAN, shape=ShapeSpec(kind="scalar"), unit=unit)],
        output_representation=ValueRepresentation.BOOLEAN,
        output_shape=ShapeSpec(kind="scalar"),
        output_unit=unit,
    )
    transformed = replace(direct, definition_id="test.transformed", transforms=[step])
    family = "https://tvproductions.github.io/xplane-fdau/contracts/source-binding-catalog"
    value = bindings.SourceBindingCatalog(
        contract_family=family,
        schema_version=1,
        catalog_id="test.bindings",
        catalog_revision=1,
        authority=authority,
        provenance=provenance,
        definitions=[direct, transformed],
    )
    try:
        encoded = bindings.dumps_source_binding_catalog_v1(value)
        loaded = bindings.loads_source_binding_catalog_v1(encoded)
        if loaded != value or loaded.content_hash != value.content_hash or bindings.dumps_source_binding_catalog_v1(loaded) != encoded:
            raise SmokeError("installed binding catalog round trip differs")
        if loaded.definitions[0].measurement_ref != reference or loaded.definitions[1].transforms[0].algorithm.definition_hash != "a" * 64:
            raise SmokeError("installed binding catalog lost pinned references")
        # Independent preimages: this synthetic vector uses only ASCII, integers and Booleans.
        raw = json.loads(encoded)
        for entry in raw["definitions"]:
            body = {key: child for key, child in entry.items() if key != "content_hash"}
            preimage = dict(contract_family=family, schema_version=1, definition=body)
            expected = hashlib.sha256(json.dumps(preimage, sort_keys=True, separators=(",", ":")).encode() + b"\n").hexdigest()
            if expected != entry["content_hash"]:
                raise SmokeError("installed binding entry hash differs from independent preimage")
        body = {key: child for key, child in raw.items() if key != "content_hash"}
        expected = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode() + b"\n").hexdigest()
        if expected != value.content_hash:
            raise SmokeError("installed binding catalog hash differs from independent preimage")
        with io.BytesIO() as stream:
            bindings.dump_source_binding_catalog_v1(value, stream)
            if stream.closed or stream.getvalue() != encoded:
                raise SmokeError("installed binding binary dump differs")
            stream.seek(0)
            if bindings.load_source_binding_catalog_v1(stream) != loaded or stream.closed:
                raise SmokeError("installed binding binary load differs")
        bindings.validate_binding_catalog(loaded, measurement_catalog)
    except (FDAUContractError, ValueError, UnicodeError) as error:
        raise SmokeError("installed binding catalog round trip failed") from error
    bad_reference = replace(direct, measurement_ref=replace(reference, definition_hash="0" * 64))
    bad_output = replace(transformed, transforms=[replace(step, output_representation=ValueRepresentation.INTEGER)])
    bad_policy = replace(direct, failure_policy=replace(policy, stale=bindings.FailureDisposition.ACCEPT_WITHOUT_VALUE))
    for bad, pointer, label in (
        (bad_reference, "/measurement_ref/definition_hash", "stale reference hash"),
        (bad_output, "/transforms/0/output_representation", "incompatible final declaration"),
        (bad_policy, "/failure_policy/stale", "unauthorized failure disposition"),
    ):
        candidate = replace(value, definitions=[bad])
        candidate = bindings.loads_source_binding_catalog_v1(bindings.dumps_source_binding_catalog_v1(candidate))
        try:
            bindings.validate_binding_catalog(candidate, measurement_catalog)
        except ContractValidationError as error:
            if error.path != "/definitions/0" + pointer:
                raise SmokeError("installed binding rejection lost its exact path") from error
        else:
            raise SmokeError("installed binding catalog accepted " + label)
    try:
        data = importlib.resources.files("xplane_fdau.schemas").joinpath("source-binding-catalog-v1.schema.json").read_bytes()
        schema = json.loads(data)
    except (OSError, ValueError, UnicodeError) as error:
        raise SmokeError("installed binding catalog schema is unavailable or invalid") from error
    if (
        schema.get("$id") != "https://tvproductions.github.io/xplane-fdau/schemas/source-binding-catalog-v1.schema.json"
        or schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
        or schema.get("unevaluatedProperties") is not False
        or not data.endswith(b"\n")
        or data.endswith(b"\r\n")
    ):
        raise SmokeError("installed binding catalog schema identity or closure differs")


def smoke_raw_observation() -> None:
    """Verify installed raw-observation bytes, validation, and schema access."""
    import json
    from collections.abc import Mapping
    from dataclasses import replace
    from hashlib import sha256
    from io import BytesIO

    from xplane_fdau import acquisition
    from xplane_fdau.contracts import (
        AdapterIdentity,
        ClockDomain,
        ClockReading,
        ContractValidationError,
        FDAUContractError,
        InlineValue,
        ObservationTiming,
        PayloadReference,
        ProducerIdentity,
        ProviderIdentity,
        UtcInstant,
    )

    family = "https://tvproductions.github.io/xplane-fdau/contracts/raw-observation"
    producer = ProducerIdentity(implementation_id="test.producer", implementation_version="1", producer_instance_id="00000000-0000-4000-8000-000000000002")
    domain = ClockDomain(
        clock_domain_id="00000000-0000-4000-8000-000000000006",
        kind="host_monotonic",
        unit="nanosecond",
        resolution=1,
        origin="test",
        scope="test",
        producer_instance_id=producer.producer_instance_id,
    )
    first = acquisition.RawObservation(
        contract_family=family,
        schema_version=1,
        observation_id="00000000-0000-4000-8000-000000000001",
        producer=producer,
        provider=ProviderIdentity(provider_family_id="test.provider", provider_version="1"),
        adapter=AdapterIdentity(adapter_family_id="test.adapter", adapter_version="1"),
        session_id="00000000-0000-4000-8000-000000000003",
        stream_id="00000000-0000-4000-8000-000000000004",
        epoch_id="00000000-0000-4000-8000-000000000005",
        sequence=0,
        connection_generation=0,
        source_generation=0,
        resource_kind="test.resource",
        resource_id="test/source",
        observed_shape=(),
        observed_representation="boolean",
        value_evidence=acquisition.RawValueEvidence(kind="inline", value=InlineValue(representation="boolean", value=False)),
        timing=ObservationTiming(
            receipt_clock=domain,
            receipt_reading=ClockReading(clock_domain_id=domain.clock_domain_id, value=0),
            receipt_utc=UtcInstant(value="2026-11-22T00:00:00.123456789Z"),
        ),
        applicability_context=(),
        status="ok",
        limitations=(),
    )
    payload = replace(
        first,
        observation_id="00000000-0000-4000-8000-000000000007",
        sequence=1,
        observed_representation="referenced_bytes",
        value_evidence=acquisition.RawValueEvidence(
            kind="payload",
            payload=PayloadReference(
                media_type="application/octet-stream", byte_length=0, sha256="f" * 64, storage_role="test.raw", retention_status="intentionally_omitted"
            ),
        ),
    )
    absent = replace(
        first,
        observation_id="00000000-0000-4000-8000-000000000008",
        sequence=2,
        status="unavailable",
        value_evidence=acquisition.RawValueEvidence(kind="absent", reason="unavailable"),
    )

    def ascii_document(fields: dict[str, object]) -> bytes:
        return (json.dumps(fields, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")

    def signed(fields: Mapping[str, object]) -> bytes:
        body = {name: value for name, value in fields.items() if name != "content_hash"}
        return ascii_document(body | {"content_hash": sha256(ascii_document(body)).hexdigest()})

    for observation in (first, payload, absent):
        try:
            data = acquisition.dumps_raw_observation_v1(observation)
            fields = json.loads(data)
            if type(fields) is not dict or signed(fields) != data or fields["content_hash"] != observation.content_hash:
                raise SmokeError("installed raw observation bytes or hash differ")
            with BytesIO() as stream:
                acquisition.dump_raw_observation_v1(observation, stream)
                if stream.closed or stream.getvalue() != data:
                    raise SmokeError("installed raw observation binary dump differs")
                stream.seek(0)
                if acquisition.load_raw_observation_v1(stream) != observation or stream.closed:
                    raise SmokeError("installed raw observation binary round trip differs")
            if acquisition.loads_raw_observation_v1(data) != observation:
                raise SmokeError("installed raw observation round trip differs")
            if fields["timing"]["receipt_utc"] != first.timing.receipt_utc.value or "source_timing" in fields["timing"]:
                raise SmokeError("installed raw observation lost receipt timing or added source timing")
            if observation is first and sha256(data).hexdigest() != "03b6b3039898418347fc681448134333fdc5a7900650bbeea5ab5f11bb879c03":
                raise SmokeError("installed raw observation differs from independent byte vector")
        except (FDAUContractError, KeyError, TypeError, ValueError) as error:
            raise SmokeError("installed raw observation interchange failed") from error

    original = json.loads(acquisition.dumps_raw_observation_v1(first))
    incompatible_status = dict(original, status="unavailable")
    wrong_clock = dict(original["timing"]["receipt_clock"], producer_instance_id="00000000-0000-4000-8000-000000000009")
    incompatible_timing = dict(original, timing=dict(original["timing"], receipt_clock=wrong_clock))
    for fields, path in ((incompatible_status, "/value_evidence/kind"), (incompatible_timing, "/timing/receipt_clock/producer_instance_id")):
        try:
            acquisition.loads_raw_observation_v1(signed(fields))
        except ContractValidationError as error:
            if error.path != path:
                raise SmokeError("installed raw observation reported the wrong validation path") from error
        except FDAUContractError as error:
            raise SmokeError("installed raw observation reported the wrong error class") from error
        else:
            raise SmokeError("installed raw observation accepted an invalid status or timing claim")

    name = "raw-observation-v1.schema.json"
    try:
        schema_bytes = importlib.resources.files("xplane_fdau.schemas").joinpath(name).read_bytes()
        schema = json.loads(schema_bytes)
    except (OSError, ValueError) as error:
        raise SmokeError("installed raw observation schema is unavailable or invalid") from error
    if (
        type(schema) is not dict
        or schema.get("$id") != "https://tvproductions.github.io/xplane-fdau/schemas/" + name
        or schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
        or schema.get("unevaluatedProperties") is not False
        or not schema_bytes.endswith(b"\n")
    ):
        raise SmokeError("installed raw observation schema identity or closure differs")


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
    _measurement_definition_smoke()
    smoke_measurement_catalog()
    smoke_source_binding_definition()
    smoke_source_binding_catalog()
    smoke_raw_observation()
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
