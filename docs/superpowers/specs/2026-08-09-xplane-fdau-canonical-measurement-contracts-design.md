# xplane-fdau Canonical Measurement Contract Kernel Design

- **Status:** Draft for written review
- **Date:** 2026-08-09
- **Decision owner:** Jeff / tvproductions

## Authority and purpose

The authoritative parent architecture is
`docs/architecture/xplane12_virtual_fdau_ecosystem_design.md`. The completed
identity and native-format migration is specified in
`docs/superpowers/specs/2026-08-09-xplane-fdau-identity-fdr-kernel-migration-design.md`.

This specification defines the first canonical FDAU contract increment after
that migration. It establishes provider-neutral measurement, binding, raw
observation, measurement sample, measurement frame, timing, quality, lineage,
canonical JSON, schema, and conformance-fixture contracts. It does not acquire
data or perform recording.

The increment is intentionally schema-first. Versioned JSON schemas and shared
fixtures are the language-neutral wire authority. Frozen Python values, strict
loaders, serializers, and semantic validators implement that authority using
only the standard library.

Version `0.1.0` remains unreleased. The release prohibition remains in force
until the complete canonical vertical slice named by `HANDOFF.md` exists and is
independently reviewed.

## Decision summary

The project will add a layered canonical contract kernel:

1. `xplane_fdau.contracts` owns common identity, provenance, value, timing,
   canonical JSON, hashing, and error primitives.
2. `xplane_fdau.measurements` owns measurement definitions, catalogs,
   representation semantics, validity, and quality vocabulary.
3. `xplane_fdau.bindings` owns provider-neutral source-binding definitions and
   catalogs containing references to named transformation or calibration
   algorithms.
4. `xplane_fdau.acquisition` owns immutable raw observations, measurement
   samples, frames, and pure cross-contract validation.
5. `xplane_fdau.schemas` packages the normative schema resources.

No package in this increment polls, schedules, resolves acquisition demand,
executes a transform, retains a payload, assembles a frame, manages a session,
fans data out, or writes an archive. Those behaviors remain later reviewed
increments.

## Goals

This increment will:

1. give measurements stable provider-neutral semantic identities;
2. distinguish semantic measurements from provider-specific source bindings;
3. preserve exactly what an adapter knew in each accepted raw observation;
4. represent normalized samples without losing raw-observation lineage;
5. represent deterministic frames without implying ARINC 717 framing;
6. keep UTC, monotonic, source, simulator, and cycle timing distinct;
7. define closed validity and acquisition-quality vocabularies;
8. define deterministic canonical JSON and content identity;
9. publish independently versioned schemas and language-neutral fixtures;
10. provide strict standard-library-only Python values and validators;
11. preserve extension seams for later acquisition, recording, replay, native
    FDR projection, and edition-pinned ARINC profiles; and
12. keep the existing native X-Plane FDR kernel unchanged and fully tested.

## Non-goals

This increment will not:

- ship stock X-Plane measurement definitions or DataRef bindings;
- ship aircraft-, plugin-, q4xpcc-, or provider-specific catalog content;
- discover, read, subscribe to, write, or command a simulator resource;
- execute transformation, calibration, interpolation, or resampling logic;
- implement acquisition profiles, demand resolution, continuity evaluation,
  lifecycle-event production, or generic fan-out;
- implement a recording session, canonical archive, artifact manifest,
  recovery, deterministic replay, or native FDR projection;
- retrieve or store content-addressed payloads;
- add ARINC labels, words, sync patterns, frame layouts, encoders, decoders,
  tables, profiles, or conformance claims;
- add FDM/FOQA thresholds, analysis, workflow, or governance;
- add compatibility aliases at the package root;
- add a runtime dependency, host import, network client, thread, event loop, or
  plugin loader; or
- push, tag, publish, or create a release.

## Package and dependency boundaries

The target package organization is:

```text
xplane_fdau/
|-- __init__.py
|-- contracts/
|   |-- __init__.py
|   |-- errors.py
|   |-- identity.py
|   |-- provenance.py
|   |-- values.py
|   |-- timing.py
|   `-- canonical_json.py
|-- measurements/
|   |-- __init__.py
|   |-- models.py
|   |-- quality.py
|   `-- catalog.py
|-- bindings/
|   |-- __init__.py
|   |-- models.py
|   `-- catalog.py
|-- acquisition/
|   |-- __init__.py
|   |-- observations.py
|   |-- samples.py
|   |-- frames.py
|   `-- validation.py
|-- schemas/
|   |-- __init__.py
|   |-- measurement-catalog-v1.schema.json
|   |-- source-binding-catalog-v1.schema.json
|   |-- raw-observation-v1.schema.json
|   |-- measurement-sample-v1.schema.json
|   `-- measurement-frame-v1.schema.json
|-- formats/
|   `-- xplane_fdr/                         existing native kernel
`-- sinks/
    `-- xplane_fdr.py                       existing native sink
```

The root `xplane_fdau.__init__` continues to export only `__version__`.
Consumers import each contract from its semantic package.

Dependency direction is:

```text
contracts
   ^
   +-- measurements
   ^       ^
   |       |
   +-- bindings
   ^       ^
   |       |
   +-- acquisition

formats.xplane_fdr     sinks.xplane_fdr
        existing siblings; no canonical dependency in this increment
```

`bindings` may depend on measurement reference types but not on acquisition.
`acquisition` may depend on contracts, measurements, and bindings. Canonical
packages do not depend on the native FDR format or sink. A later native FDR
projection may depend inward on canonical contracts after its own reviewed
specification.

## Contract families and versions

Version 1 defines five independently versioned top-level families:

| Family | Family URI | Schema resource |
| --- | --- | --- |
| Measurement catalog | `https://tvproductions.github.io/xplane-fdau/contracts/measurement-catalog` | `measurement-catalog-v1.schema.json` |
| Source-binding catalog | `https://tvproductions.github.io/xplane-fdau/contracts/source-binding-catalog` | `source-binding-catalog-v1.schema.json` |
| Raw observation | `https://tvproductions.github.io/xplane-fdau/contracts/raw-observation` | `raw-observation-v1.schema.json` |
| Measurement sample | `https://tvproductions.github.io/xplane-fdau/contracts/measurement-sample` | `measurement-sample-v1.schema.json` |
| Measurement frame | `https://tvproductions.github.io/xplane-fdau/contracts/measurement-frame` | `measurement-frame-v1.schema.json` |

Each top-level document contains `$schema`, `contract_family`,
`schema_version`, and a lowercase hexadecimal SHA-256 `content_hash`.
Definition catalogs additionally contain a semantic catalog ID, catalog
revision, authority, provenance, and ordered definitions. Generated evidence
records contain their instance identity, producer identity, and their
meaning-bearing timing and lineage fields.

Schema version describes wire shape. Definition revision describes semantic
meaning. A unit, sign convention, transform reference, validity rule,
reference frame, applicability rule, or other meaning change requires a new
definition revision even when the schema version is unchanged.

There is no implicit latest-version loader. Each public loader accepts exactly
the schema version named in its function and rejects unknown versions.

## Shared identity and provenance

### Semantic identities

Catalog, measurement, binding, algorithm, provider-family, adapter-family,
quantity, unit, reference-frame, datum, axis, and applicability identifiers
use lowercase dotted ASCII text matching:

```text
[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+
```

The required dot prevents unqualified local names from becoming accidental
global contracts. Revisions are integers from 1 through `2^63 - 1`.

`DefinitionRef` pins `definition_id`, `definition_revision`, and
`definition_hash`. A friendly ID without its revision and hash is not a valid
reference. `AlgorithmRef` uses the same three-part identity and adds immutable,
strictly JSON-compatible parameters; it does not contain executable code.

### Runtime identities

Acquisition session, stream, epoch, observation, sample, frame, clock-domain,
and producer-instance identities are canonical lowercase RFC 9562 UUID text.
The contract kernel validates identities but does not generate them. A future
session or adapter owns identity creation. Replay preserves recorded identities
unless its future contract explicitly establishes a new replay epoch.

Sequence numbers and generation numbers are integers from 0 through
`2^63 - 1`. A sequence is meaningful only with its session, stream, and epoch
identity. Restart, reconnect, reload, or replay cannot silently continue a
prior sequence.

### Provenance

`Authority` records an authority ID and authority revision. `ProvenanceSource`
records a source identifier, source revision or version, optional locator,
optional SHA-256, and a concise limitation or scope note. Licensed source text
is never required in a public contract.

`ProducerIdentity` records an implementation ID and version, producer-instance
UUID, and optional source or build revision. Provider and adapter identities
remain separate fields on raw observations; producer identity does not collapse
their provenance.

Static definition catalogs do not acquire generated timestamps. Generated
records contain only timestamps that are evidence, not nondeterministic
serialization metadata.

## Canonical JSON and content hashing

Canonical JSON is a project-owned profile, not incidental `json.dumps()`
output. The same profile governs schemas' examples, fixture bytes, hashes, and
future Python/native parity.

The profile is:

- UTF-8 without a byte-order mark;
- one JSON value per document followed by one LF byte;
- no insignificant whitespace;
- object keys ordered by Unicode scalar-value sequence;
- array order preserved exactly;
- strings required to be Unicode NFC and free of unpaired surrogates;
- quotation mark and reverse solidus escaped;
- the standard short escapes used for backspace, tab, LF, form feed, and CR;
- other U+0000 through U+001F controls encoded as lowercase `\u00xx`;
- solidus and non-ASCII Unicode emitted unescaped;
- signed 64-bit JSON integers serialized in ordinary base-10 form with no
  leading zeroes;
- finite IEEE-754 binary64 real values serialized with the RFC 8785 / ECMAScript
  shortest-round-trip number algorithm, except that an integral real retains
  a decimal or exponent marker so it cannot be confused lexically with an
  integer;
- negative real zero normalized to `0.0`;
- lowercase `e`, the algorithm-selected exponent sign, and no exponent leading
  zeroes; and
- rejection of NaN, infinities, values outside the signed 64-bit integer range,
  duplicate object properties, and non-string object keys.

For a finite real, first obtain the RFC 8785 / ECMAScript shortest-round-trip
number token. If the value is negative zero, emit `0.0`. Otherwise, if that token
contains neither a decimal point nor `e`, append `.0`; if it already contains a
decimal point or `e`, emit it unchanged. This is the complete integral-real
adaptation and preserves the real-versus-integer lexical distinction. The
implementation and golden vectors enforce this rule rather than relying on the
host JSON encoder. Boundary fixtures include both signed integer limits,
negative zero, subnormal and maximum finite binary64 values,
precision-sensitive adjacent values, exponent boundaries, Unicode, nested
objects, and ordered arrays.

Every top-level record and every catalog definition has a computed content
hash. A top-level record's preimage is the canonical JSON encoding of that
object with only its own `content_hash` property omitted, including the final
LF. A catalog definition's preimage is the canonical encoding of
`{"contract_family": <catalog-family>, "schema_version": <catalog-version>,
"definition": <entry-without-its-content_hash>}`. Nested objects keep their
hashes when an enclosing hash is computed. Static definition hashes therefore
cover family/version context, ID, revision, authority, provenance, and semantic
body. Generated-record hashes cover identity, timing, producer, value/status,
and lineage. No model can hold a caller-supplied stale self-hash: Python models
compute it from validated fields, serializers inject it, and loaders recompute
and compare the declared value.

Loaders may accept noncanonical property order and whitespace, but they reject
duplicate properties and noncanonical semantic values such as non-NFC text.
Successful serialization always emits canonical bytes.

## Shared values and payload references

The contract value vocabulary distinguishes:

- Boolean;
- signed 64-bit integer;
- finite binary64 real;
- Unicode string;
- enumeration code and label;
- vector;
- fixed-length array;
- variable-length array; and
- referenced bytes.

Booleans are never accepted as integers or reals. Strings are never coerced to
enumeration values. Arrays preserve declared order and exact shape. `null`
appears only where a schema explicitly authorizes absence; it is never a
replacement for an unavailable value.

Binary source data is represented by `PayloadReference`, containing media type,
byte length, lowercase SHA-256, storage role, and retention status. Retention
status is one of `retained`, `intentionally_omitted`, `missing`, or
`unverified`. The contract validates the claim but does not resolve, read, or
store the payload.

## Measurement catalog

`MeasurementCatalog` is an immutable semantic definition document with:

- catalog ID, revision, and computed hash;
- authority and ordered provenance;
- optional descriptive title and scope;
- a canonical tuple of `MeasurementDefinition` entries; and
- no provider resource identities.

Definitions are unique by `(definition_id, definition_revision)` and appear in
ascending ID then revision order. The loader rejects unsorted or duplicate
definitions rather than silently rewriting their order.

Each `MeasurementDefinition` contains:

- definition ID, revision, and computed hash;
- authority and ordered provenance;
- title, description, semantic quantity, and limitations;
- one declared value representation;
- canonical quantity/dimension and unit identities, or explicit unitless
  status;
- reference frame, datum, ordered axes, handedness, and sign convention when
  applicable;
- storage precision, meaningful resolution, inclusive documented range, and
  array/vector shape constraints when applicable;
- enumeration members with explicit known, unknown, and reserved handling;
- freshness and staleness interpretation;
- allowed interpolation and discontinuity policy;
- allowed validity states and quality flags;
- sensitivity classification;
- ordered aircraft/simulator applicability classes; and
- supporting provenance and source authority.

Unit, quantity, frame, and datum fields are authority-qualified identities.
This increment does not invent a universal unit registry or execute conversion.
A measurement claiming unitless status cannot also declare a unit. Numeric,
enumeration, vector, array, and byte-only fields are rejected when irrelevant
to the selected representation.

No stock-X-Plane or aircraft-specific definition ships in the catalog. Test
fixtures use clearly synthetic `test.*` identities.

## Source-binding catalog

`SourceBindingCatalog` is an immutable semantic definition document with its
own catalog identity, revision, computed hash, authority, provenance, scope,
and canonically ordered `SourceBindingDefinition` entries.

Each binding contains:

- definition ID, revision, and computed hash;
- an exact `DefinitionRef` to one measurement definition;
- provider-family and adapter-family identities and versions/applicability;
- exact source resource kind and identity;
- expected source owner or signature when one exists;
- declared source representation and shape;
- native quantity/unit or explicit unitless status;
- aircraft, plugin, simulator, and version applicability selectors;
- an ordered tuple of source dependencies for multi-source or derived values;
- optional ordered status/validity companion sources;
- an ordered tuple of named `AlgorithmRef` transform/calibration steps;
- policies for absent, orphaned, stale, and read-error input;
- expected acquisition phase relative to the flight model;
- replay policy; and
- provenance and limitations.

Failure disposition is a closed declaration: `reject`, `accept_raw_only`,
`accept_flagged`, or `accept_without_value`. Replay policy is `preserve`,
`rederive`, or `prohibit`. These values describe future behavior; this increment
does not execute it.

`validate_binding_catalog(binding_catalog, measurement_catalog)` is a pure
operation that resolves every measurement reference. For a binding without a
transform it checks direct unit, representation, shape, and applicability
compatibility. For a binding with transforms it checks reference structure,
ordering, and declared input/output compatibility but does not claim that the
referenced algorithm produces the declared result. It neither registers
catalogs globally nor executes algorithms. An algorithm reference cannot be
claimed as implemented until a later reviewed algorithm registry and
conformance corpus exists.

No actual DataRef path, XPLM handle, Web API resource, plugin owner, or aircraft
binding ships in this increment.

## Timing model

Requested cadence is not part of this increment. Timing values record evidence
that an adapter or future acquisition layer actually possesses.

`ClockDomain` records:

- clock-domain UUID;
- kind: `host_monotonic`, `source`, or `simulator`;
- integer unit: `nanosecond`, `microsecond`, `millisecond`, or `tick`;
- advertised positive resolution in that unit;
- origin and scope descriptions;
- producer-instance UUID; and
- optional tick period when the unit is `tick`.

`ClockReading` contains an exact clock-domain identity and a signed 64-bit
integer value. Direct subtraction or ordering is valid only for readings in the
same domain. The contract layer exposes an explicit checked comparison helper
that rejects unrelated domains.

`UtcInstant` uses a normalized UTC RFC 3339 representation with `Z` and exactly
nine fractional-second digits. It preserves nanosecond text even though a
Python `datetime` exposes only microseconds; conversion helpers report rather
than silently discard sub-microsecond precision.

`ClockAnchor` pairs one host-monotonic reading with one UTC instant and a
non-negative nanosecond uncertainty. Cross-process or restarted-process
correlation requires anchors; the contract never subtracts unrelated monotonic
clocks or pretends the mapping is exact.

`ObservationTiming` contains:

- required host-monotonic receipt domain and reading;
- required UTC receipt instant;
- optional source clock domain, reading, and source sequence when genuinely
  supplied;
- optional inline `ClockAnchor` for receipt-clock to UTC correlation;
- optional X-Plane cycle number;
- optional simulator flight time in integer nanoseconds;
- optional acquisition phase: `before_flight_model`, `after_flight_model`, or
  `unknown`;
- optional pause state;
- optional replay state: `live`, `replay`, `seeking`, or `unknown`; and
- optional finite binary64 time-speed factor.

Unavailable timing values remain absent. Receiver time is never relabeled as a
source timestamp. Simulator, wall-clock, source, and monotonic time remain
separate fields.

## Raw observation

`RawObservation` is a generated immutable record containing:

- family/version and computed record hash;
- observation UUID;
- producer, provider, and adapter identities and versions;
- acquisition-session, stream, and epoch UUIDs;
- non-negative stream sequence, connection generation, and source generation;
- exact source resource kind, identity, index/shape, and observed raw type;
- exactly one inline JSON-safe raw value, `PayloadReference`, or explicit absent
  value state;
- `ObservationTiming`;
- adapter status and optional bounded diagnostic text; and
- optional ordered limitations.

Adapter status is one of `ok`, `unavailable`, `orphaned`, `type_mismatch`,
`read_error`, or `provider_degraded`. `ok` requires a value. `unavailable`,
`orphaned`, and `read_error` prohibit a value. `type_mismatch` and
`provider_degraded` may preserve the raw value actually received.

Observed raw type and shape never overwrite the binding's declared type and
shape. The two are compared only by pure cross-contract validation.

## Validity and quality

Validity and acquisition quality are separate axes.

`ValidityState` is one of:

- `valid`;
- `invalid`;
- `unknown`; or
- `not_applicable`.

`QualityFlag` is one of:

- `conversion_failed`;
- `discontinuous`;
- `dropped`;
- `duplicate`;
- `orphaned`;
- `out_of_declared_range`;
- `precision_lost`;
- `provider_degraded`;
- `read_error`;
- `reordered`;
- `rounded`;
- `saturated`;
- `stale`;
- `type_mismatch`; or
- `unavailable`.

Quality flags use array-set semantics: values are unique and serialized in
ascending lexical order. Loaders and programmatic constructors reject duplicate
or noncanonical order rather than silently sorting. An empty tuple means no
known acquisition degradation; it does not assert validity.

Operational evaluation such as within tolerance, outside tolerance, or a FOQA
finding is not a validity or quality flag and remains outside this project
increment.

## Measurement sample

`MeasurementSample` is a generated immutable record containing:

- family/version and computed record hash;
- sample UUID;
- acquisition-session, stream, and epoch UUIDs plus stream sequence;
- exact measurement and binding `DefinitionRef` values;
- normalized representation and canonical unit identity when a normalized
  value exists;
- normalized value or explicit absent-normalized-value state;
- ordered applied transform/calibration references;
- `ValidityState` and canonically ordered `QualityFlag` values;
- freshness age in non-negative integer nanoseconds at evaluation, when known;
- either one complete `RawObservation` or one immutable observation reference;
- ordered derivation-parent sample references; and
- producer identity.

`RecordRef` pins a runtime UUID, family URI, schema version, and content hash.
Every sample reaches a complete raw observation or immutable observation
reference. A provider-specific exhaustive audit stream is not a substitute for
this lineage.

A normalized value is prohibited when conversion failed or the observation is
unavailable, orphaned, or a read error. An absent normalized value requires
non-valid validity and at least one explanatory quality flag. Values outside a
declared range may be preserved with explicit validity and quality rather than
silently clipped. Saturation, rounding, and precision loss are explicit flags.

`validate_sample(sample, measurement_catalog, binding_catalog)` is a pure
operation that resolves pinned references and checks representation, shape,
unit, range, binding compatibility, status-to-quality mapping, and lineage. It
does not normalize the observation or execute transforms.

## Measurement frame

`MeasurementFrame` is a generated deterministic evaluation snapshot containing:

- family/version and computed record hash;
- frame UUID;
- acquisition-session, stream, and epoch UUIDs plus frame sequence;
- declared acquisition instant using a host-monotonic clock domain and reading;
- optional correlated UTC instant and inline `ClockAnchor`;
- a canonical tuple of complete `MeasurementSample` values;
- an arrival-ordered tuple of complete `RawObservation` values;
- producer identity; and
- optional ordered limitations.

Samples are unique by sample UUID and by the tuple of measurement reference,
binding reference, and sample sequence. They appear in ascending order by
measurement ID/revision, binding ID/revision, sample sequence, then sample UUID.
The constructor and loader reject noncanonical order. This permits more than
one corroborating binding for a measurement without making tuple order
nondeterministic.

Raw observations preserve actual arrival order and have unique observation
identities. Samples embedded in a frame use `RecordRef` lineage to observations
in that frame rather than duplicating them inline. A repeated provider value is
represented by a distinct observation identity, with the `duplicate` quality
condition reflected in affected samples when the producer classifies it as a
duplicate. A frame does not imply an ARINC 717 frame, resampling, simultaneity,
or successful continuity.

`validate_frame(frame, measurement_catalog, binding_catalog)` recursively
validates samples and observations, identities, ordering, sample-to-observation
reference closure, and acquisition-instant compatibility. It does not build or
mutate a frame.

## Lifecycle and epoch boundary

This increment represents lifecycle evidence without implementing lifecycle
behavior. Aircraft reload, plugin reload, connection replacement, source
generation change, replay, seek, or clock regression requires a new epoch in a
future acquisition implementation. Samples crossing a known discontinuity use
the `discontinuous` quality flag.

The separate acquisition-lifecycle-event family, rules for automatically
advancing an epoch, and continuity consequences belong to the next acquisition
profiles/demand/continuity/fan-out specification. This increment does not create
a partial lifecycle engine.

## Public API and errors

Public package APIs expose owned immutable values and explicit operations. The
initial surface includes family-specific load/loads/dump/dumps functions,
canonical byte serialization, computed content hashes, checked clock comparison,
catalog cross-validation, sample validation, and frame validation. It does not
expose a reflection-driven serializer, dynamic registry, entry-point loader, or
generic caller-code hook.

Definition and record objects compute their own content hashes. `DefinitionRef`
and `RecordRef` factories accept validated objects and copy exact identities and
hashes.

Contract errors derive from one `FDAUContractError` and distinguish:

- `ContractParseError` for JSON syntax and duplicate properties;
- `ContractShapeError` for family/schema structure and unknown properties;
- `ContractValidationError` for semantic and cross-field violations;
- `CanonicalJSONError` for unsupported canonical values;
- `UnsupportedContractVersionError` for an unknown family/version; and
- `ContractHashError` for declared/computed hash mismatch.

Loaded-document errors retain source, line and column where the parser supplies
them, JSON property path, contract family, and definition or record identity
when known. Programmatic construction uses the same property paths without
inventing source locations. Errors never expose payload contents beyond the
bounded field already being validated.

Unknown properties, unknown enum values, incompatible references, and future
schema versions fail closed. There is no implicit migration or best-effort
coercion.

## Schema and conformance corpus

Each schema is JSON Schema Draft 2020-12, carries the exact project URL as
`$id`, rejects unevaluated properties, and references shared `$defs` without a
runtime schema-validator dependency. Packaged resources under
`xplane_fdau.schemas` and published documentation copies under `docs/schemas`
are byte-identical.

The language-neutral corpus lives under:

```text
tests/fixtures/contracts/v1/
|-- manifest.json
|-- accepted/
|-- rejected/
`-- canonical/
```

The manifest records for every case:

- contract family and schema version;
- input resource;
- accepted or rejected disposition;
- expected error class and JSON property path for rejected cases;
- expected canonical resource and SHA-256 for accepted cases; and
- a concise requirement identifier.

Fixtures use synthetic `test.*` definitions and deterministic UUIDs. They do
not become product catalog content. Canonical files are exact byte vectors,
including their final LF.

Schemas express wire shape. Python semantic validators and fixture requirements
express invariants that JSON Schema cannot state reliably, including computed
hashes, catalog reference resolution, canonical ordering, same-clock-domain
comparison, and sample lineage.

## ARINC extension boundary

ARINC adoption remains an explicit project objective, but no ARINC behavior is
implemented in this increment. Generic contracts preserve the semantic fields
that a later standards mapping needs: quantity, unit, representation, scaling,
resolution, range, sign, status/validity, timing, provenance, and loss policy.

The dependency path remains:

```text
X-Plane source binding
        -> canonical MeasurementSample
        -> edition-pinned ARINC mapping/profile
        -> ARINC word/subframe/recording adapter
```

ARINC identity never replaces canonical measurement identity. One measurement
may map to zero, one, or multiple standards profiles. A standards decoder later
produces canonical samples while retaining its exact profile as provenance.

The expected first recording profile is ARINC 717 with the applicable ARINC
647A/FRED configuration-document boundary. ARINC 429 follows only where a real
source, target, fixture, or educational profile uses its word semantics. Before
any such implementation, a separately reviewed `StandardsBaseline` must pin the
licensed normative edition, applicable clauses, mappings, traceability, golden
vectors, and claim boundary. Public catalog descriptions are not substitutes
for normative sources.

No generic measurement, binding, observation, sample, or frame schema contains
ARINC labels, SDI/SSM bits, sync words, subframe placement, or recorder-specific
constants.

## Verification strategy

All tests use `unittest`; pytest remains prohibited.

### Family tests

Each contract family receives tests for:

- programmatic construction and immutable tuple freezing;
- strict JSON loading with duplicate and unknown-property rejection;
- canonical serialization and round trip;
- computed and mismatched hashes;
- every enum and representation branch;
- every applicable cross-field invariant;
- source and JSON-property-path error context; and
- unsupported family and schema versions.

### Canonical JSON tests

Golden vectors cover:

- signed 64-bit boundaries and overflow;
- Boolean-versus-number rejection;
- integral, fractional, subnormal, maximum, and adjacent binary64 values;
- negative zero normalization and non-finite rejection;
- exponent thresholds and lexical normalization;
- NFC and non-NFC Unicode, supplementary characters, controls, and surrogates;
- nested key ordering and array-order preservation;
- duplicate keys and non-string keys; and
- exact UTF-8 bytes, final LF, and SHA-256.

### Timing and lineage tests

Tests prove:

- unrelated monotonic domains cannot be compared;
- same-domain readings retain exact integer differences;
- UTC uses exactly nine fractional digits and explicit `Z`;
- UTC/monotonic anchor uncertainty survives round trip;
- unavailable source timing is never synthesized;
- raw status and value presence remain consistent;
- every sample has complete or referenced raw lineage;
- failed normalization cannot carry a normalized value;
- derivation parents preserve order;
- frame samples are unique and canonically ordered; and
- observation arrival order is preserved.

### Cross-contract tests

Pure validators are tested for:

- missing and mismatched measurement references;
- binding representation, shape, unit, and applicability conflicts;
- sample representation, unit, range, status, quality, and lineage conflicts;
- frame identity, epoch, order, closure, and timing conflicts; and
- acceptance of multiple corroborating bindings for one measurement.

### Repository gates

The complete verification matrix includes:

- the existing native FDR `unittest` regression suite;
- public API and root-namespace tests;
- static and adversarial runtime import-boundary tests;
- Ruff lint and formatting;
- type checking;
- coverage, security, documentation, dead-code, cohesion, maintainability, and
  complexity gates already orchestrated by `tools/quality.py`;
- strict MkDocs build;
- clean wheel and sdist validation;
- exact schema and fixture resource inspection; and
- installed-wheel smoke tests on Python 3.12, 3.13, and 3.14 outside the
  checkout.

Artifact inspection must prove `dependencies = []`, no provider or network
package ships, no stock catalog content ships, and no ARINC implementation is
present.

## Documentation and compatibility

README and MkDocs gain a canonical-contract overview and API reference. The
documentation distinguishes:

- canonical measurements from DataRef bindings;
- observations from normalized samples;
- frames from ARINC framing;
- validity/quality from operational evaluation;
- canonical contract evidence from the later canonical archive; and
- generic standards-ready semantics from actual ARINC conformance.

The existing native FDR documentation and APIs remain stable. The root package
does not flatten new contract names. There is no previously released canonical
wire format, so version 1 requires no compatibility alias or migration shim.

## Delivery sequence and plan boundaries

`ROADMAP.md` and `BACKLOG.md` track this increment as four separately
executable slices beneath this one normative semantic specification. This keeps
the wire model coherent without creating one oversized implementation plan.

### C1 — Canonical contract foundation

Plan:
`docs/superpowers/plans/2026-08-09-xplane-fdau-contract-foundation.md`

The plan implements common errors, identity, provenance, canonical JSON,
content hashing, shared values, payload references, timing, validity, and
quality. It ends with a usable, independently testable foundation and golden
canonical vectors.

### C2 — Measurement and source-binding catalogs

Plan:
`docs/superpowers/plans/2026-08-09-xplane-fdau-measurement-binding-catalogs.md`

The plan implements measurement and source-binding definitions, their catalog
schemas, exact references, and pure cross-catalog validation. It ends with
provider-neutral synthetic fixtures and proves no stock/provider content ships.

### C3 — Observation, sample, and frame records

Plan:
`docs/superpowers/plans/2026-08-09-xplane-fdau-observation-sample-frame-contracts.md`

The plan implements raw observations, measurement samples, measurement frames,
their schemas, lineage, ordering, and pure cross-contract validation. It does
not introduce acquisition behavior.

### C4 — Contract conformance and artifact closure

Plan:
`docs/superpowers/plans/2026-08-09-xplane-fdau-contract-conformance-closure.md`

The plan completes the shared accepted/rejected/canonical corpus,
documentation, resource parity, release-boundary hardening, fresh artifacts,
installed-wheel verification, and independent review.

Every plan uses test-first `unittest` steps, frequent scoped commits, focused
and complete verification, and its exact `BACKLOG.md` acceptance gates. A later
plan cannot weaken an earlier plan's verified contract. No release action is
part of any plan.

## Acceptance criteria

This increment is complete only when:

1. the five version-1 contract families have normative packaged schemas;
2. frozen Python values and strict loaders implement the same wire shapes;
3. canonical JSON bytes and content hashes match the shared golden vectors;
4. catalogs distinguish semantic definitions from source bindings and ship no
   real provider content;
5. every binding pins one exact measurement definition;
6. raw observations preserve provider, resource, type, shape, timing, status,
   and value evidence without invention;
7. samples preserve exact definition references, normalized value/status,
   validity, quality, timing, and raw lineage;
8. frames are deterministic, preserve observation order, and make no ARINC
   framing claim;
9. UTC, monotonic, source, simulator, and cycle timing cannot be confused;
10. cross-contract validators reject incompatible references and semantics
    without executing transforms;
11. accepted and rejected language-neutral fixtures cover boundary and failure
    behavior with exact canonical bytes and hashes;
12. all runtime modules remain standard-library-only, synchronous,
    capture-neutral, and free of provider/network/host imports;
13. the complete native FDR regression suite remains green;
14. built and installed artifacts contain the exact new schemas and no stock
    catalogs, adapters, ARINC behavior, or runtime dependencies;
15. all repository quality and installed-wheel gates pass on supported Python
    versions; and
16. no push, tag, publication, or release occurs.

## Required following increments

After independent review, the next specifications remain:

1. acquisition profiles, demand resolution, lifecycle events, continuity, and
   generic fan-out;
2. canonical archive, artifact manifest, recovery, and deterministic replay;
3. projection from canonical samples to the native X-Plane FDR sink with
   explicit loss reporting; and
4. later edition-pinned standards profiles and downstream FDM/FOQA work under
   their separate governance.
