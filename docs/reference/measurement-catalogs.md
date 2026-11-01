# Measurement catalogs

`MeasurementCatalog` groups exact, immutable measurement definitions under one
catalog identity. It describes measurement meaning within the X-Plane FDAU.
Catalogs do not authorize acquisition, execute conversions, check historical
revisions against a global registry, or resolve binding/sample closure.
No stock X-Plane or provider catalog is bundled.

## Construct and round-trip a synthetic catalog

The constructor requires `contract_family`, integer `schema_version=1`,
`catalog_id`, `catalog_revision`, `authority`, nonempty ordered `provenance`, and
nonempty `definitions`. Optional `title` and `scope` are omitted when absent;
explicit `None` is prohibited. The catalog computes `content_hash`, which is
read-only and cannot be supplied to the constructor. Models are frozen,
slotted, and keyword-only, and defensively copy supported list/tuple inputs.

The following example is self-contained and uses synthetic `test.*` identities:

```python
from io import BytesIO

from xplane_fdau.contracts import (
    Authority, DefinitionRef, ProvenanceSource, RepresentationSpec, UnitSpec,
)
from xplane_fdau.measurements import (
    CoordinateSpec, FreshnessSpec, MeasurementCatalog, MeasurementDefinition,
    dump_measurement_catalog_v1, dumps_measurement_catalog_v1,
    load_measurement_catalog_v1, loads_measurement_catalog_v1,
)

authority = Authority(authority_id="test.authority", authority_revision=1)
provenance = [ProvenanceSource(
    source_id="test.source", source_revision=1, scope="Synthetic example",
)]
definition = MeasurementDefinition(
    definition_id="test.switch_state", definition_revision=1,
    authority=authority, provenance=provenance,
    title="Synthetic switch", description="Whether a synthetic switch is asserted.",
    limitations=[], quantity_id="test.state",
    representation=RepresentationSpec(kind="boolean"),
    unit=UnitSpec(kind="unitless"), coordinates=CoordinateSpec(kind="not_applicable"),
    freshness=FreshnessSpec(fresh_for_ns=0), interpolation_policy="prohibited",
    discontinuity_policy="preserve", allowed_validity=["unknown"],
    allowed_quality=[], sensitivity="unknown", applicability=[],
)
catalog = MeasurementCatalog(
    contract_family="https://tvproductions.github.io/xplane-fdau/contracts/measurement-catalog",
    schema_version=1, catalog_id="test.catalog", catalog_revision=1,
    authority=authority, provenance=provenance, definitions=[definition],
)
reference_before = DefinitionRef(
    definition_id=definition.definition_id,
    definition_revision=definition.definition_revision,
    definition_hash=definition.content_hash,
)
encoded = dumps_measurement_catalog_v1(catalog)
loaded = loads_measurement_catalog_v1(encoded)
stream = BytesIO()
dump_measurement_catalog_v1(catalog, stream)
stream.seek(0)
assert load_measurement_catalog_v1(stream) == loaded
assert not stream.closed
reference_after = DefinitionRef(
    definition_id=loaded.definitions[0].definition_id,
    definition_revision=loaded.definitions[0].definition_revision,
    definition_hash=loaded.definitions[0].content_hash,
)
assert reference_before == reference_after
assert loaded.content_hash == catalog.content_hash
assert encoded.endswith(b"\n")
```

The four explicit versioned APIs are exported by both
`xplane_fdau.measurements` and `xplane_fdau.measurements.io`:

| Function | Input / output |
| --- | --- |
| `loads_measurement_catalog_v1(data, *, source="<memory>")` | Unicode JSON text or UTF-8 bytes → catalog |
| `load_measurement_catalog_v1(binary_file, *, source="<memory>")` | Caller-owned binary stream → catalog |
| `dumps_measurement_catalog_v1(catalog)` | Catalog → canonical UTF-8 bytes |
| `dump_measurement_catalog_v1(catalog, binary_file)` | Writes canonical bytes to a caller-owned binary stream |

Streams need not be seekable. Load/dump do not accept paths or text streams and
never close caller-owned streams. Ordinary I/O errors propagate. `source` is
an explicit diagnostic display name; loaders do not infer it from a stream.
There is no unversioned alias or implicit latest-version loader. Serialization
uses canonical object-key order, preserves semantic array order, and writes
exactly one final LF. UTF-8 BOM, duplicate properties and JSON null are rejected.

## Ordering and exact identity

Definitions must be unique by `(definition_id, definition_revision)` in
ascending ID then revision order. Several revisions of the same ID are valid,
for example `(test.a, 1), (test.a, 2), (test.b, 1)`. Duplicate pairs, descending
revisions and descending IDs fail; the library never sorts or deduplicates.
Provenance preserves declared authority order and has unique source identities.
Catalogs allow at most 256 provenance entries and 65535 definitions.

A `DefinitionRef` pins all three values: ID, revision, and definition hash.
The root catalog hash covers catalog metadata and complete entries, including
nested entry hashes, with only the root `content_hash` omitted from its
canonical preimage. An entry hash instead covers the catalog family/version
context and that definition with its own hash omitted. Changing catalog
metadata alone preserves an unchanged entry's hash; changing the entry changes
both its identity and the enclosing catalog hash. Definition revisions remain
caller-owned semantic decisions; the library cannot infer a historical revision
change from another document it has not been given.

Loading validates complete-document syntax, envelope dispatch, all shapes,
all canonical domains, all declared hashes, then local semantics before
constructing models. Errors preserve source, JSON Pointer, family and known
catalog/definition identity. Syntax locations appear only when supplied by the
parser. A well-formed incorrect hash is a `ContractHashError`; malformed hash
spelling is checked at its semantic field position.

## Schema and later closure

The [version-1 schema](../schemas/measurement-catalog-v1.schema.json) is
byte-identical to the packaged resource. It is read through the resource API,
without assuming an installed filesystem path:

```python
from importlib.resources import files

schema_bytes = files("xplane_fdau.schemas").joinpath(
    "measurement-catalog-v1.schema.json",
).read_bytes()
```

The Draft 2020-12 schema describes representable wire shape, variants and
bounds. Runtime Python validation additionally enforces lexical integer/real
distinctions, NFC, ordering, hashes and cross-field semantic policies. JSON
Schema treats mathematically integral real values as integers and cannot detect
JSON duplicate properties after parsing. Schema validation alone does not
establish acceptance by the loader. The runtime does not import a schema
validator or retrieve external resources.

Shared `definition_ref`, `record_ref`, `compute_content_hash` and common
`canonical_bytes` model dispatch remain pending C4.3 work. Use the explicit
catalog APIs and model hash properties delivered here. See
[measurement definitions](measurement-definitions.md) for entry invariants.
