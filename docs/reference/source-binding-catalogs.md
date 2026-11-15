# Source-binding catalogs

`SourceBindingCatalog` is an immutable, ordered document of source-binding
**declarations**. Loading validates the complete document locally. Call
`validate_binding_catalog(binding_catalog, measurement_catalog)` separately to
resolve exact measurement references and check compatibility. Neither operation
acquires a source value or executes an algorithm.

The keyword-only catalog constructor requires `contract_family`, `schema_version`,
`catalog_id`, `catalog_revision`, `authority`, `provenance`, and `definitions`,
then accepts optional `title` and `scope`. Omit absent properties; `None` is
prohibited. Lists and tuples are defensively copied to tuples. Definitions must
already be unique and ordered by `(definition_id, definition_revision)`;
multiple revisions and corroborating bindings are allowed. Resources may be
shared across different bindings.

## Construct and validate a synthetic pair

All identities in this runnable example are synthetic `test.*` values.

```python
from dataclasses import replace
from io import BytesIO

from xplane_fdau.bindings import (
    FailurePolicy, SourceBindingCatalog, SourceBindingDefinition, SourceSpec,
    TransformInput, TransformStep, dump_source_binding_catalog_v1,
    dumps_source_binding_catalog_v1, load_source_binding_catalog_v1,
    loads_source_binding_catalog_v1, validate_binding_catalog,
)
from xplane_fdau.contracts import (
    AdapterIdentity, AlgorithmRef, Authority, ContractValidationError,
    DefinitionRef, ProvenanceSource, ProviderIdentity, RepresentationSpec,
    ShapeSpec, UnitSpec,
)
from xplane_fdau.measurements import (
    ApplicabilitySelector, CoordinateSpec, FreshnessSpec, MeasurementCatalog,
    MeasurementDefinition,
)

authority = Authority(authority_id="test.authority", authority_revision=1)
provenance = [ProvenanceSource(
    source_id="test.source", scope="Synthetic example", source_revision=1,
)]
unit = UnitSpec(kind="unitless")
aircraft = ApplicabilitySelector(class_id="test.aircraft", value="Synthetic")
plugin = ApplicabilitySelector(class_id="test.plugin", value="Synthetic")
measurement = MeasurementDefinition(
    definition_id="test.flag", definition_revision=1, authority=authority,
    provenance=provenance, title="Synthetic flag", description="Example meaning",
    limitations=[], quantity_id="test.state",
    representation=RepresentationSpec(kind="boolean"), unit=unit,
    coordinates=CoordinateSpec(kind="not_applicable"),
    freshness=FreshnessSpec(fresh_for_ns=1, stale_after_ns=2),
    interpolation_policy="prohibited", discontinuity_policy="preserve",
    allowed_validity=["unknown"], allowed_quality=["stale"],
    sensitivity="unknown", applicability=[aircraft],
)
measurement_catalog = MeasurementCatalog(
    contract_family="https://tvproductions.github.io/xplane-fdau/contracts/measurement-catalog",
    schema_version=1, catalog_id="test.measurements", catalog_revision=1,
    authority=authority, provenance=provenance, definitions=[measurement],
)
reference = DefinitionRef(
    definition_id=measurement.definition_id,
    definition_revision=measurement.definition_revision,
    definition_hash=measurement.content_hash,
)
source = SourceSpec(
    provider=ProviderIdentity(provider_family_id="test.provider", provider_version="1"),
    adapter=AdapterIdentity(adapter_family_id="test.adapter", adapter_version="1"),
    resource_kind="test.resource", resource_id="test.synthetic_flag",
    declared_representation="boolean", declared_shape=ShapeSpec(kind="scalar"),
    native_unit=unit, resource_selection={"kind": "index", "index": 0},
)
policy = FailurePolicy(
    unavailable="reject", orphaned="reject", stale="accept_without_value",
    read_error="reject", type_mismatch="reject", provider_degraded="reject",
)
direct = SourceBindingDefinition(
    definition_id="test.direct", definition_revision=1, authority=authority,
    provenance=provenance, measurement_ref=reference, source=source,
    applicability=[aircraft, plugin], dependencies=[], companions=[], transforms=[],
    failure_policy=policy, acquisition_phase="unknown", replay_policy="preserve",
    limitations=[],
)
step = TransformStep(
    step_id="test.identity",
    algorithm=AlgorithmRef(
        definition_id="test.opaque_identity", definition_revision=1,
        definition_hash="a" * 64, parameters={"test.marker": 1},
    ),
    inputs=[TransformInput(
        input_id="binding.primary", representation="boolean",
        shape=ShapeSpec(kind="scalar"), unit=unit,
    )],
    output_representation="boolean", output_shape=ShapeSpec(kind="scalar"),
    output_unit=unit,
)
converted = replace(direct, definition_id="test.transformed", transforms=[step])
binding_catalog = SourceBindingCatalog(
    contract_family="https://tvproductions.github.io/xplane-fdau/contracts/source-binding-catalog",
    schema_version=1, catalog_id="test.bindings", catalog_revision=1,
    authority=authority, provenance=provenance, definitions=[direct, converted],
    title="Synthetic binding catalog", scope="Example declarations only",
)
encoded = dumps_source_binding_catalog_v1(binding_catalog)
assert encoded.endswith(b"\n")
assert loads_source_binding_catalog_v1(encoded) == binding_catalog
with BytesIO() as stream:
    dump_source_binding_catalog_v1(binding_catalog, stream)
    assert not stream.closed and stream.getvalue() == encoded
    stream.seek(0)
    restored_catalog = load_source_binding_catalog_v1(stream, source="example.json")
    assert not stream.closed
validate_binding_catalog(restored_catalog, measurement_catalog)
assert restored_catalog.content_hash == binding_catalog.content_hash

# A locally valid catalog can still have an unresolved or stale reference.
bad = replace(direct, measurement_ref=replace(reference, definition_hash="0" * 64))
local_only = loads_source_binding_catalog_v1(dumps_source_binding_catalog_v1(
    replace(binding_catalog, definitions=[bad]),
))
stale_reference_rejected = False
try:
    validate_binding_catalog(local_only, measurement_catalog)
except ContractValidationError as error:
    assert error.path == "/definitions/0/measurement_ref/definition_hash"
    stale_reference_rejected = True
assert stale_reference_rejected
```

The extra plugin selector narrows the measurement's aircraft applicability.
Every measurement selector must remain present with its exact value. Direct
bindings require exact representation, element type, shape, unit and byte-payload
allow-lists. Transformed bindings compare the final declared output instead;
intermediate units or representations may differ when the local chain agrees.
No unit conversion or overlapping-array-shape relaxation occurs here.

The stale disposition is authorized because the measurement allows the `stale`
quality flag and `unknown` validity. Every non-reject disposition needs its
same-named allowed quality flag and a compatible validity state. Raw-only and
without-value outcomes additionally require `invalid` or `unknown`. Declaring
such a policy does not evaluate a sample; C3 owns sample evidence and outcomes.

## Interchange, identity and schema

The four versioned load/loads/dump/dumps functions live in
`xplane_fdau.bindings.io` and are re-exported by `xplane_fdau.bindings`.
Stream functions use caller-owned binary streams. Dumping emits canonical UTF-8
without BOM and with one final LF. Loading accepts noncanonical JSON member order
and whitespace, while preserving declared array order and rejecting duplicates.

The cached read-only catalog `content_hash` covers catalog metadata and complete
hashed entries. Only the root self-hash is omitted from its preimage; nested
hashes remain. Entry hashes also bind their family and schema version. A caller
cannot supply a self-hash to a constructor. Measurement and algorithm references
retain ID, revision and hash exactly.

Loading stages the whole document through parse/duplicates, family/version,
shape, canonical domains, well-formed self-hash comparisons and local semantics
before constructing any structural models. Errors retain the supplied source,
binding family, bounded identity and catalog-relative JSON Pointer. Syntax
locations appear only when known; algorithm parameter values are not echoed.

The [normative schema](../schemas/source-binding-catalog-v1.schema.json) is also
available through `importlib.resources.files("xplane_fdau.schemas")`.
JSON Schema establishes structural constraints. Runtime validation additionally
checks lexical numeric domains, NFC, identities, ordering, hashes and local
links. Explicit cross-catalog validation checks reference closure and measurement
compatibility. Successful loading alone proves neither compatibility nor an
implemented algorithm.

Algorithm references and data-only parameters remain opaque. A1.4 owns the
allow-listed registry and execution; C3 owns samples. C4.3 retains shared
`definition_ref`, `compute_content_hash` and public `canonical_bytes` model
dispatch closure. Use the versioned family dumper for these canonical bytes.

See [binding definitions](source-binding-definitions.md) and
[measurement catalogs](measurement-catalogs.md).
