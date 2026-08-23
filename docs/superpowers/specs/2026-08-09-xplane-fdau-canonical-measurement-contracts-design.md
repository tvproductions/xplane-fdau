# xplane-fdau Canonical Measurement Contract Kernel Design

- **Governance:** active
- **Status:** draft
- **Date:** 2026-08-09
- **Decision owner:** Jeff / tvproductions
- **Roadmap epic:** `C1`
- **Roadmap children:** `C1.1`, `C1.2`, `C1.3`, `C1.4`, `C1.5`, `C2.1`, `C2.2`, `C2.3`, `C2.4`, `C3.1`, `C3.2`, `C3.3`, `C3.4`, `C3.5`, `C4.1`, `C4.2`, `C4.3`, `C4.4`
- **Approval:** —

## Authority and purpose

The authoritative parent architecture is
`docs/architecture/xplane12_virtual_fdau_ecosystem_design.md`. The completed
identity and native-format migration is specified in
`docs/superpowers/specs/2026-08-09-xplane-fdau-identity-fdr-kernel-migration-design.md`.
The later
`docs/architecture/xplane_fdau_core_scope_amendment.md` is authoritative for
the X-Plane-specific core purpose, external client/adapter boundary, local
ARINC and FDM/FOQA ownership, and Python compatibility policy.

This specification defines the first canonical FDAU contract increment after
that migration. Here, provider-neutral means neutral among X-Plane access
paths and recorded evidence; it does not mean simulator-neutral. The increment
establishes provider-neutral measurement, binding, raw
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
  tables, profiles, or conformance claims in this increment;
- add FDM/FOQA analysis profiles, derived parameters, event processing,
  aggregation, reports, review records, or policy ports in this increment;
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
|-- conformance/
|   |-- __init__.py
|   `-- v1/                                  packaged language-neutral corpus
|       |-- manifest.json
|       |-- accepted/
|       |-- rejected/
|       `-- canonical/
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

Version 1 defines five independently versioned top-level families. These
strings and resource paths are normative:

| Family | `contract_family` | `schema_version` | Schema `$id` and published resource |
| --- | --- | --- | --- |
| Measurement catalog | `https://tvproductions.github.io/xplane-fdau/contracts/measurement-catalog` | integer `1` | `https://tvproductions.github.io/xplane-fdau/schemas/measurement-catalog-v1.schema.json` |
| Source-binding catalog | `https://tvproductions.github.io/xplane-fdau/contracts/source-binding-catalog` | integer `1` | `https://tvproductions.github.io/xplane-fdau/schemas/source-binding-catalog-v1.schema.json` |
| Raw observation | `https://tvproductions.github.io/xplane-fdau/contracts/raw-observation` | integer `1` | `https://tvproductions.github.io/xplane-fdau/schemas/raw-observation-v1.schema.json` |
| Measurement sample | `https://tvproductions.github.io/xplane-fdau/contracts/measurement-sample` | integer `1` | `https://tvproductions.github.io/xplane-fdau/schemas/measurement-sample-v1.schema.json` |
| Measurement frame | `https://tvproductions.github.io/xplane-fdau/contracts/measurement-frame` | integer `1` | `https://tvproductions.github.io/xplane-fdau/schemas/measurement-frame-v1.schema.json` |

Contract instances do not contain a `$schema` property. `$schema` is reserved
for schema resources, where it is exactly
`https://json-schema.org/draft/2020-12/schema`; each schema resource uses the
exact `$id` above. Every contract instance contains `contract_family`, integer
`schema_version`, and lowercase hexadecimal SHA-256 `content_hash`. No family
URI contains a version and no loader infers a version from a schema resource
filename. The media type for contract instances, canonical fixture documents,
and conformance results is `application/json`; UTF-8 is mandatory and a
`charset` parameter has no contract meaning.

JSON object property order is never semantic. Array order is semantic unless
an exact section below calls the array an array-set; canonical serialization
orders object properties independently of their input order. Optional
properties are omitted when absent. JSON `null` is prohibited throughout
version 1. Tagged unions use a required `kind` property and the exact variant
properties stated below; properties belonging to another variant are
prohibited.

The type notation in this specification is normative:

- `Int64` is a JSON integer from `-9223372036854775808` through
  `9223372036854775807`; `UInt63` is a JSON integer from `0` through
  `9223372036854775807`; and `Revision` is a JSON integer from `1` through
  `9223372036854775807`.
- `Binary64` is a finite IEEE-754 binary64 JSON real. Its JSON token must
  contain `.` or `e` after canonical serialization, even when its mathematical
  value is integral.
- `Sha256` is a string matching `[0-9a-f]{64}`.
- `NfcText(N)` is a Unicode-scalar string in NFC with between 1 and `N` code
  points, inclusive. `OptionalText(N)` means the property is omitted or is an
  `NfcText(N)`; it never means `null` or an empty string.
- `Identifier` is the semantic identifier syntax defined below. `Uuid` is the
  runtime identity syntax defined below. `VersionText` is `NfcText(128)` with
  no Unicode category `Cc` or `Cf` code point.
- `ArraySet<T>` is an array of unique `T` values in ascending canonical lexical
  order. A loader or constructor rejects duplicates and noncanonical order; it
  never silently sorts or deduplicates.

Unless a tighter bound is stated, a version-1 array or object contains at most
65535 elements/properties. Provenance, limitations, applicability,
dependencies, companions, transforms, and derivation-parent arrays contain at
most 256 entries; coordinate axes contain at most 32; frame samples and
observations contain at most 65535. Contract JSON nesting depth is at most 64,
counting the root container as one. These are shape limits, not acquisition or
recording capacity claims.

Each family schema lists properties in the semantic validation order used by
loaders and errors, but that listing does not make wire-property order
semantic. The exact family property inventories are the tables in this
specification; schemas may factor repeated shapes into `$defs` but may not add
an undocumented property or default.

Schema version describes wire shape. Definition revision describes semantic
meaning. A unit, sign convention, transform reference, validity rule,
reference frame, applicability rule, or other meaning change requires a new
definition revision even when the schema version is unchanged.

There is no implicit latest-version loader. Each public loader accepts exactly
the family and schema version named in its function and rejects a different
family or version. Schema-version dispatch occurs before family-body shape or
semantic validation.

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

The entire identifier is limited to 255 ASCII characters. It is compared
byte-for-byte and is never case-folded or Unicode-normalized because only the
ASCII grammar is accepted. The generic grammar applies to catalog,
measurement, binding, algorithm, provider-family, adapter-family, quantity,
unit, reference-frame, datum, axis, applicability, resource-kind, storage-role,
and implementation identifiers. Concrete provider resource identities are
`NfcText(2048)` instead; forcing a path or URI into the dotted grammar would
destroy source evidence.

The exact reference objects are:

| Type | Required properties in semantic validation order | Invariants |
| --- | --- | --- |
| `DefinitionRef` | `definition_id: Identifier`, `definition_revision: Revision`, `definition_hash: Sha256` | all three properties pin one immutable definition |
| `RecordRef` | `record_id: Uuid`, `contract_family: family URI`, `schema_version: integer 1`, `content_hash: Sha256` | family URI must name one of the five families; validators may further restrict the referenced family |
| `AlgorithmRef` | the three `DefinitionRef` properties, then `parameters: object` | parameters use the data-only parameter domain below; the kernel never resolves or executes their contents |

A friendly ID without its revision and hash is not a reference. Reference
factories copy these exact values from an already validated object; callers
cannot override the copied hash.

For `AlgorithmRef`, `definition_hash` is the canonical hash published by the
future allow-listed algorithm registry. This increment treats it as an opaque
`Sha256` and can compare references for equality, but cannot resolve or claim
algorithm conformance before that registry is specified and delivered.

### Runtime identities

Acquisition session, stream, epoch, observation, sample, frame, clock-domain,
and producer-instance identities are canonical lowercase RFC 9562 UUID text.
The accepted grammar is
`[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}`;
the nil and max UUIDs are therefore rejected. The contract kernel validates
identities but does not generate them.
A future session or adapter owns identity creation. Replay preserves recorded
identities unless its future contract explicitly establishes a new replay
epoch.

Sequence numbers and generation numbers are integers from 0 through
`2^63 - 1`. A sequence is meaningful only with its record family, session,
stream, and epoch identity. Restart, reconnect, reload, or replay cannot
silently continue a prior sequence.

### Provenance

The provenance objects have these exact properties:

| Type | Required properties | Optional properties | Invariants |
| --- | --- | --- | --- |
| `Authority` | `authority_id: Identifier`, `authority_revision: Revision` | — | both properties identify the authority contract, not a person display name |
| `ProvenanceSource` | `source_id: Identifier`, `scope: NfcText(1024)` | exactly one of `source_revision: Revision` or `source_version: VersionText`; `locator: NfcText(2048)`; `sha256: Sha256` | exactly one revision/version property is present; locator and hash are independently optional |
| `ProducerIdentity` | `implementation_id: Identifier`, `implementation_version: VersionText`, `producer_instance_id: Uuid` | `source_revision: VersionText` | source revision is a VCS/build identifier, not a semantic `Revision` |
| `ProviderIdentity` | `provider_family_id: Identifier`, `provider_version: VersionText` | — | identifies the observed X-Plane access provider family |
| `AdapterIdentity` | `adapter_family_id: Identifier`, `adapter_version: VersionText` | — | identifies the external adapter implementation family |

Catalog `provenance` arrays contain at least one `ProvenanceSource`, preserve
declared authority order, and reject duplicate `(source_id, source_revision or
source_version)` identities. Generated records carry `ProducerIdentity`.
Provider and adapter identities remain separate fields on raw observations;
producer identity does not collapse their provenance. Licensed source text is
never required in a public contract.

Static definition catalogs do not acquire generated timestamps. Generated
records contain only timestamps that are evidence, not nondeterministic
serialization metadata.

## Canonical JSON and content hashing

Canonical JSON is a project-owned profile, not incidental `json.dumps()`
output. The same profile governs documentation examples, fixture bytes, hashes, and
future Python/native parity.

The profile adopts RFC 8785 section 3.2.2.3 number serialization only. It does
not claim full JSON Canonicalization Scheme compatibility: this project adds
an integer/real lexical type distinction, requires NFC, appends LF, and sorts
property names by Unicode scalar values rather than RFC 8785's UTF-16 code
units. Cross-language implementations conform to this section and its golden
vectors, not to an unqualified “JCS” label.

The profile is:

- UTF-8 without a byte-order mark;
- one JSON value per document followed by one LF byte;
- no insignificant whitespace;
- object keys ordered recursively by the unsigned Unicode scalar-value
  sequence of their unescaped NFC names, with the shorter name first when one
  is a prefix; locale and UTF-16/UTF-8 encoded-byte ordering are prohibited;
- array order preserved exactly;
- strings required to be Unicode NFC and free of unpaired surrogates;
- quotation mark and reverse solidus escaped;
- the standard short escapes used for backspace, tab, LF, form feed, and CR;
- other U+0000 through U+001F controls encoded as lowercase `\u00xx`;
- solidus and non-ASCII Unicode emitted unescaped;
- signed 64-bit JSON integers serialized in ordinary base-10 form with no
  leading zeroes; integer zero is `0`, so accepted input token `-0`
  canonicalizes to `0`;
- finite IEEE-754 binary64 real values serialized with the RFC 8785 / ECMAScript
  shortest-round-trip number algorithm, except that an integral real retains
  a decimal or exponent marker so it cannot be confused lexically with an
  integer;
- negative real zero normalized to `0.0`;
- lowercase `e`; a positive exponent includes `+`, a negative exponent includes
  `-`, and an exponent has no leading zeroes;
- rejection of NaN, infinities, values outside the signed 64-bit integer range,
  duplicate object properties, and non-string object keys.

Input number classification is lexical and precedes host conversion. A JSON
number token containing `.` or `e`/`E` enters the `Binary64` domain; a token
containing neither enters the `Int64` domain. Integers are parsed with
unbounded intermediate precision and then range-checked, so a host overflow
cannot change the error class. Reals are correctly rounded to binary64;
overflow to infinity and underflow of a nonzero token to signed or unsigned
zero are rejected. Exact zero tokens remain valid. This rule means `1`, `1.0`,
and `1e0` denote integer 1, real 1, and real 1 respectively.

For a finite real, obtain the exact ECMAScript `Number::toString` token used by
RFC 8785 section 3.2.2.3 and its Appendix B vectors. If the binary64 value is
negative zero, emit `0.0`. Otherwise, if that token contains neither a decimal
point nor `e`, append `.0`; if it already contains a decimal point or `e`, emit
it unchanged. ECMAScript therefore fixes plain-versus-exponent thresholds and
the positive exponent sign; an implementation may use Ryu or another algorithm
only when its output matches every bit-pattern vector. This is the complete
integral-real adaptation and preserves the real-versus-integer lexical
distinction. The implementation and golden vectors enforce this rule rather
than relying on the host JSON encoder. Boundary fixtures include both signed
integer limits, accepted integer `-0`, real negative zero, the minimum positive
subnormal, maximum finite binary64, precision-sensitive adjacent values, the
plain/exponent boundaries at `1e-6`/`1e-7` and `1e20`/`1e21`, Unicode scalar
ordering cases that differ from UTF-16 ordering, nested objects, and ordered
arrays.

Every top-level record and every catalog definition has a computed content
hash. A top-level record's preimage is the canonical JSON encoding of that
object with only its root `content_hash` property omitted, including the final
LF. A catalog definition's preimage is the canonical encoding of an object
whose `contract_family` is its containing catalog's literal family URI, whose
`schema_version` is integer `1`, and whose `definition` is the complete entry
with only that entry's `content_hash` omitted. Nested objects keep their
hashes when an enclosing hash is computed. Static definition hashes therefore
cover family/version context, ID, revision, authority, provenance, and semantic
body. Generated-record hashes cover identity, timing, producer, value/status,
and lineage. No model can hold a caller-supplied stale self-hash: Python models
compute it from validated fields, serializers inject it, and loaders recompute
and compare the declared value.

`content_hash` is required on every loaded wire instance and definition entry.
It is not a constructor argument for a new programmatic object. Schema resource
files and the conformance manifest are integrity-checked by their containing
artifact/corpus but do not gain self-referential `content_hash` properties.
SHA-256 is computed over bytes, and lowercase hexadecimal is the only wire
spelling.

Loaders may accept noncanonical property order and whitespace, but they reject
duplicate properties and noncanonical semantic values, including non-NFC text.
Successful serialization always emits canonical bytes.

## Shared values and payload references

`ValueRepresentation` is the closed string vocabulary `boolean`, `integer`,
`real`, `string`, `enumeration`, `vector`, `fixed_array`, `variable_array`, and
`referenced_bytes`. `ScalarRepresentation` is the first five values only.

`InlineValue` is a tagged object:

| `representation` | Other required properties | Exact value domain |
| --- | --- | --- |
| `boolean` | `value` | JSON Boolean |
| `integer` | `value` | `Int64`; JSON Boolean is rejected before integer validation |
| `real` | `value` | `Binary64`; an integer JSON token is rejected rather than coerced |
| `string` | `value` | `NfcText(16384)` |
| `enumeration` | `value` | an enumeration member `Identifier`; labels never appear in sample values |
| `vector` | `value` | nonempty array of `Binary64`, with order preserved |
| `fixed_array` or `variable_array` | `element_representation`, `value` | `element_representation` is a `ScalarRepresentation`; `value` is an ordered array whose every element has that exact primitive domain |

`referenced_bytes` is never an `InlineValue`. It uses `PayloadReference` with
the exact properties `media_type: NfcText(127)`, `byte_length: UInt63`,
`sha256: Sha256`, `storage_role: Identifier`, and `retention_status`. Media type
is lowercase RFC 6838 type/subtype text without parameters and must match
`[a-z0-9!#$&^_.+-]+/[a-z0-9!#$&^_.+-]+`. `retention_status` is one of
`retained`, `intentionally_omitted`, `missing`, or `unverified`. Length and hash
describe the claimed original byte sequence even when it was omitted, is now
missing, or has not been verified. The contract validates the claim but does
not resolve, read, retain, or store the payload.

Algorithm `parameters` are an object whose keys are `Identifier` values and
whose values recursively contain Boolean, `Int64`, `Binary64`, `NfcText(16384)`,
arrays, or objects in the same domain. `null`, byte payloads, duplicate keys,
and a nesting depth greater than 32 are prohibited. This domain is data-only:
the contract kernel never evaluates strings or resolves imports/callables, and
a later allow-listed algorithm registry must supply and validate each
algorithm's permitted parameter schema before execution exists.

Booleans are never accepted as integers or reals. Strings are never coerced to
enumeration values. Arrays preserve declared order and exact shape. Version 1
contains no authorized JSON `null`; absence is represented by an omitted
optional property or an explicit tagged absent-value variant.

All public Python value types are frozen, slotted dataclasses. Sequence inputs
are defensively copied to tuples before validation. Data-only object inputs are
defensively copied recursively and exposed through read-only mappings;
subsequent caller mutation cannot change a model or its hash. Constructors and
loaders run the same field validators and produce the same RFC 6901 paths.
Definition and record self-hashes are computed cached properties, never
init-fields. Python `bool` is rejected before `int` checks, and no public model
uses a bare `dict`, mutable list, `datetime` in place of `UtcInstant`, or host
object identity as wire semantics.

## Measurement catalog

`MeasurementCatalog` is an immutable semantic definition document with:

- catalog ID, revision, and computed hash;
- authority and ordered provenance;
- optional descriptive title and scope;
- a canonical tuple of `MeasurementDefinition` entries; and
- no provider resource identities.

Its exact version-1 properties, in semantic validation order, are
`contract_family`, `schema_version`, `catalog_id: Identifier`,
`catalog_revision: Revision`, `authority: Authority`, `provenance` (a nonempty
array), optional `title: NfcText(256)`, optional `scope: NfcText(2048)`,
`definitions` (a nonempty array), and `content_hash`. No generated timestamp,
producer, provider, adapter, or resource property is permitted.

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
  representation-selected array/vector shape constraints;
- enumeration members with explicit known, unknown, and reserved handling;
- freshness and staleness interpretation;
- allowed interpolation and discontinuity policy;
- allowed validity states and quality flags;
- sensitivity classification;
- ordered aircraft/simulator applicability classes; and
- supporting provenance and source authority.

The bullets above map to these exact version-1 properties:

| Property | Type | Rule |
| --- | --- | --- |
| `definition_id`, `definition_revision`, `content_hash` | `Identifier`, `Revision`, `Sha256` | immutable semantic identity |
| `authority`, `provenance` | `Authority`, nonempty provenance array | definition-level source authority; provenance identity is unique |
| `title`, `description`, `limitations` | `NfcText(256)`, `NfcText(4096)`, array of unique `NfcText(1024)` | limitations preserve declared order and may be empty |
| `quantity_id` | `Identifier` | semantic quantity or discrete-state identity |
| `representation` | `RepresentationSpec` | exact value representation and shape |
| `unit` | `UnitSpec` | exact unit or explicit unitless declaration |
| `coordinates` | `CoordinateSpec` | explicitly declares coordinate semantics or their absence |
| `numeric` | optional `NumericSpec` | required for integer, real, vector, and numeric arrays; prohibited otherwise |
| `enumeration` | optional `EnumerationSpec` | required only for enumeration; prohibited otherwise |
| `freshness` | `FreshnessSpec` | freshness and stale classification semantics |
| `interpolation_policy` | closed string | `prohibited`, `hold`, or `linear`; `linear` requires real/vector/numeric-array representation |
| `discontinuity_policy` | closed string | `preserve`, `start_new_epoch`, or `reject` |
| `allowed_validity` | nonempty `ArraySet<ValidityState>` | `valid` is not implied |
| `allowed_quality` | `ArraySet<QualityFlag>` | empty means no degradation flag is authorized by this definition |
| `sensitivity` | closed string | `public`, `operational`, `restricted`, or `unknown` |
| `applicability` | `ArraySet<ApplicabilitySelector>` | empty means no additional applicability restriction |

`RepresentationSpec` contains `kind: ValueRepresentation`. For `vector` it
also contains `length: UInt63`, restricted to 1 through 1024. For
`fixed_array` it contains `element_representation: ScalarRepresentation` and
`length: UInt63`, restricted to 1 through 65535. For `variable_array` it
contains `element_representation`, `minimum_length: UInt63`, and
`maximum_length: UInt63`, with maximum at most 65535 and minimum not greater
than maximum. Version-1 vectors and arrays are one-dimensional; nested arrays
are rejected. `referenced_bytes` contains `payload: PayloadSpec`.
`PayloadSpec` contains `allowed_media_types`, a nonempty `ArraySet` of
lowercase media-type strings, and `allowed_storage_roles`, a nonempty
`ArraySet<Identifier>`. Other representations contain only `kind`.

`UnitSpec` is either `{"kind":"unitless"}` or
`{"kind":"unit","quantity_id":Identifier,"unit_id":Identifier}`.
For the unit variant its `quantity_id` must equal the definition's
`quantity_id`. `CoordinateSpec` is either `{"kind":"not_applicable"}` or the
`applicable` variant containing `kind: "applicable"`, `reference_frame_id: Identifier`,
optional `datum_id: Identifier`, `handedness` (`left` or `right`), and a
nonempty ordered `axes` array. Each axis contains `axis_id: Identifier`,
`direction: NfcText(256)`, and `sign_convention: NfcText(512)`; axis IDs are
unique. The applicable variant is required whenever the definition assigns a
reference frame, datum, axis, handedness, or sign meaning; those meanings are
prohibited in the not-applicable variant.

Boolean, string, enumeration, referenced-byte, and arrays of those scalar
representations require the unitless variant. Integer, real, vector, and
numeric-array definitions may be unitless or declare a unit. For a vector with
applicable coordinate semantics, axis count equals vector length; every other
representation may use at most one axis.

`NumericSpec` contains `storage_precision_bits: UInt63`, `resolution`, and
optional `minimum` and `maximum`; precision is 1 through 64, resolution is
greater than zero, and minimum is not greater than maximum. For integer
definitions those three numeric properties are `Int64`. For real, vector, and
real-array definitions they are `Binary64`. Numeric arrays whose element
representation is integer use the integer domain. Mixed numeric element types
are prohibited.
`EnumerationSpec` contains a nonempty array of members ordered by member code.
Each member contains `code: Identifier`, `label: NfcText(256)`, and `kind`
(`known`, `unknown`, or `reserved`); codes are unique and at most one member is
`unknown`. `FreshnessSpec` contains optional `fresh_for_ns: UInt63` and
optional `stale_after_ns: UInt63`; at least one is present and, when both are
present, `fresh_for_ns` is not greater than `stale_after_ns`.

`ApplicabilitySelector` contains `class_id: Identifier` and
`value: NfcText(256)`. Its canonical lexical key is the pair `(class_id,
value)`; duplicate or noncanonical selector order fails. These selectors state
semantic applicability only and never authorize simulator access.

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

It uses the same top-level property inventory and invariants as
`MeasurementCatalog`, substituting the source-binding family URI and binding
definitions. Binding definitions are unique by `(definition_id,
definition_revision)` and sorted by that pair.

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

The exact `SourceBindingDefinition` properties are `definition_id`,
`definition_revision`, `content_hash`, `authority`, nonempty `provenance`,
`measurement_ref: DefinitionRef`, `source: SourceSpec`, `applicability`,
`dependencies`, `companions`, `transforms`, `failure_policy`,
`acquisition_phase`, `replay_policy`, and ordered `limitations`.

`SourceSpec` contains `provider: ProviderIdentity`, `adapter: AdapterIdentity`,
`resource_kind: Identifier`, `resource_id: NfcText(2048)`, optional
`owner_signature: NfcText(1024)`, optional `resource_selection`,
`declared_representation: ValueRepresentation`,
optional `declared_element_representation: ScalarRepresentation`,
`declared_shape: ShapeSpec`, and
`native_unit: UnitSpec`, plus `declared_payload: PayloadSpec` exactly when the
declared representation is referenced bytes. `resource_selection` is either
`{"kind":"index","index":UInt63}` or
`{"kind":"slice","start":UInt63,"length":UInt63}` with positive length.
Element representation is present exactly
for fixed/variable arrays. `ShapeSpec` is `{"kind":"scalar"}` for scalar and
referenced-byte representations, `{"kind":"fixed","length":UInt63}` for
vector/fixed-array representations, or
`{"kind":"variable","minimum_length":UInt63,"maximum_length":UInt63}` for
variable arrays. Lengths use the same positive/maximum rules as
`RepresentationSpec`. The observed representation and
shape are not binding properties; they belong only to `RawObservation`.
Boolean, string, enumeration, referenced-byte, and arrays of those source
representations require a unitless native unit; numeric source representations
may declare a unit or be unitless.

The primary source has the reserved input identity `binding.primary`.
`dependencies` is an ordered array of `BindingInputRef`; each contains
`input_id: Identifier`, `source: SourceSpec`, and `required: Boolean`. Input IDs
are unique and cannot equal `binding.primary`. `companions` is an ordered array
containing `role` (`status`, `validity`, or `status_and_validity`) plus a
`source: SourceSpec`; the source tuple `(provider family, adapter family,
resource kind, resource ID, resource selection)` is unique. Dependency order is algorithm input order;
companion order is evidence interpretation order. Neither is sorted by a
loader.

`transforms` is an ordered acyclic array of `TransformStep`. Each step contains
`step_id: Identifier`, `algorithm: AlgorithmRef`, a nonempty ordered `inputs`
array, `output_representation: ValueRepresentation`, optional
`output_element_representation`, `output_shape: ShapeSpec`, and `output_unit:
UnitSpec`. Step IDs are unique and cannot equal any source input ID. Each
`TransformInput` contains `input_id`, `representation`, optional
`element_representation`, `shape`, and `unit`. Its input ID resolves to
`binding.primary`, one dependency input, or a preceding step; forward and self
references are prohibited. Its declared representation/element/shape/unit must
equal the resolved source or step output. Element-representation presence
follows the array rules. The last step output matches the referenced
measurement. Dependencies require at least one transform; a direct binding has
no dependency and no transform. Repeated algorithm references are allowed
because step identity, order, inputs, and parameters distinguish them.

`failure_policy` contains exactly `absent`, `orphaned`, `stale`, and
`read_error`; each value is one of `reject`, `accept_raw_only`,
`accept_flagged`, or `accept_without_value`. `acquisition_phase` is one of
`before_flight_model`, `after_flight_model`, `either`, or `unknown`.
`replay_policy` is `preserve`, `rederive`, or `prohibit`. Applicability uses the
same canonical array-set as measurements. Limitations use the same ordered,
unique text array as measurement definitions.

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

Resolution uses the exact `(definition_id, definition_revision)` pair and then
compares `definition_hash`; missing identity raises a validation error at the
reference pointer and a mismatched hash raises a validation error at its
`definition_hash` pointer. Direct bindings require exact representation,
element representation, shape, unit, and every measurement applicability
selector; a binding may add narrower applicability selectors but may not
contradict an equal `class_id`. Transformed bindings perform those same checks
against the declared final transform output. No validator imports, discovers,
or executes an algorithm.

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

Its exact properties are `clock_domain_id: Uuid`, `kind`, `unit`,
`resolution: UInt63`, `origin: NfcText(512)`, `scope: NfcText(512)`,
`producer_instance_id: Uuid`, and optional `tick_period`. `kind` is
`host_monotonic`, `source`, or `simulator`; `unit` is `nanosecond`,
`microsecond`, `millisecond`, or `tick`; resolution is greater than zero.
`tick_period` is present exactly when unit is `tick` and contains
`numerator_ns: UInt63` and `denominator: UInt63`, both greater than zero and in
lowest terms. This rational expresses nanoseconds per tick without binary64
rounding.

`ClockReading` contains exactly `clock_domain_id: Uuid` and `value: Int64`.
Direct subtraction or ordering is valid only for readings in the same domain.
The contract layer exposes explicit checked comparison and difference helpers;
both reject unrelated domains, and difference rejects an `Int64` overflow
rather than wrapping.

`UtcInstant` is a JSON string matching
`[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{9}Z` and a
valid proleptic-Gregorian date/time from year 0001 through 9999. Hours are
00–23, minutes and seconds 00–59; leap-second `60`, offsets, lowercase `t`/`z`,
and `24:00:00` are rejected. It preserves nanosecond text even though a Python
`datetime` exposes only microseconds. `to_datetime()` succeeds only when the
last three fractional digits are `000`; otherwise it raises an explicit
precision-loss validation error. `to_datetime_truncated()` is deliberately not
part of the public contract.

`ClockAnchor` contains `monotonic_reading: ClockReading`, `utc: UtcInstant`,
and `uncertainty_ns: UInt63`. When a domain object is supplied for validation,
the reading must resolve to a `host_monotonic` domain. Cross-process or
restarted-process correlation requires anchors; the contract never subtracts
unrelated monotonic clocks or pretends the mapping is exact.

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

The exact properties are `receipt_clock: ClockDomain`, `receipt_reading:
ClockReading`, `receipt_utc: UtcInstant`, optional `source_timing`, optional
`receipt_anchor: ClockAnchor`, optional `xplane_cycle: UInt63`, optional
`simulator_flight_time_ns: Int64`, optional `acquisition_phase`, optional
`paused: Boolean`, optional `replay_state`, and optional `time_speed:
Binary64`. `receipt_clock` must be `host_monotonic` and its ID and producer
instance must match the receipt reading and record producer. `source_timing`
contains `clock: ClockDomain`, `reading: ClockReading`, and optional
`source_sequence: UInt63`; its IDs must match, and its clock kind is `source`
or `simulator`. Receipt anchor, when present, must reference the receipt domain
and its UTC must equal `receipt_utc`.

`acquisition_phase` is `before_flight_model`, `after_flight_model`, or
`unknown`. `replay_state` is `live`, `replay`, `seeking`, or `unknown`.
`time_speed` records evidence without imposing a sign: negative replay, zero,
and positive finite values are representable. No combination of paused,
replay state, simulator time, or time speed is inferred from another field.

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

Its exact version-1 properties are `contract_family`, `schema_version`,
`observation_id: Uuid`, `producer: ProducerIdentity`, `provider:
ProviderIdentity`, `adapter: AdapterIdentity`, `session_id: Uuid`, `stream_id:
Uuid`, `epoch_id: Uuid`, `sequence: UInt63`, `connection_generation: UInt63`,
`source_generation: UInt63`, `resource_kind: Identifier`, `resource_id:
NfcText(2048)`, optional `resource_selection` using the `SourceSpec` selection
shape, ordered `observed_shape` (zero or one `UInt63` dimension, at most
65535), `observed_representation:
ValueRepresentation`, `value_evidence: RawValueEvidence`, `timing:
ObservationTiming`, `applicability_context: ArraySet<ApplicabilitySelector>`,
`status`, optional `diagnostic: NfcText(1024)`, ordered
unique `limitations`, and `content_hash`. For array observations,
`observed_element_representation` is additionally required; it is prohibited
for every other representation.

`RawValueEvidence` is exactly one tagged variant:

- `{"kind":"inline","value":InlineValue}`;
- `{"kind":"payload","payload":PayloadReference}`; or
- `{"kind":"absent","reason":RawAbsentReason}`.

Inline representation and shape must equal the observation's reported
representation and shape. Payload is allowed exactly for
`observed_representation == "referenced_bytes"`. `RawAbsentReason` is
`unavailable`, `orphaned`, or `read_error`.

Adapter status is one of `ok`, `unavailable`, `orphaned`, `type_mismatch`,
`read_error`, or `provider_degraded`. `ok` requires a value. `unavailable`,
`orphaned`, and `read_error` prohibit a value. `type_mismatch` and
`provider_degraded` may preserve the raw value actually received.

The complete status/value matrix is:

| Status | Allowed evidence | Additional invariant |
| --- | --- | --- |
| `ok` | inline or payload | diagnostic is omitted |
| `unavailable` | absent reason `unavailable` | diagnostic is optional |
| `orphaned` | absent reason `orphaned` | diagnostic is optional |
| `read_error` | absent reason `read_error` | diagnostic is required |
| `type_mismatch` | inline or payload | diagnostic is required and preserves the received type/shape |
| `provider_degraded` | inline, payload, or an absent reason matching the underlying unavailable/orphaned/read-error condition | diagnostic is required |

An absent `provider_degraded` observation does not lose the underlying reason.
The record status remains provider-degraded while sample quality contains both
`provider_degraded` and the flag corresponding to the absent reason.

Observed raw type and shape never overwrite the binding's declared type and
shape. The two are compared only by pure cross-contract validation.

## Validity and quality

Validity and acquisition quality are separate axes.

`ValidityState` is one of:

- `valid`;
- `invalid`;
- `unknown`; or
- `not_applicable`.

`valid` means the sample satisfies the resolved definition and binding for its
declared use; `invalid` means evidence proves that it does not; `unknown` means
available evidence cannot establish either valid or invalid; and
`not_applicable` means the resolved applicability selectors exclude the sample
context. Validity is an assertion carried by the producer and checked against
local invariants; the contract validator does not infer `valid` from an empty
quality array.

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

Their version-1 meanings are exact: `conversion_failed` means a declared
normalization step produced no value; `discontinuous` means the value crosses
or follows a declared source/time epoch discontinuity; `dropped` means an
expected acquisition item was not delivered; `duplicate` means distinct raw
evidence repeats an already classified source item; `orphaned` means the
resource identity remains known but its owner/source is no longer valid;
`out_of_declared_range` means the preserved value violates the measurement
range; `precision_lost` means destination storage discarded binary/numeric
precision; `provider_degraded` means the provider reported degraded service;
`read_error` means acquisition failed while reading; `reordered` means source
sequence/arrival evidence is out of declared order; `rounded` means a declared
rounding rule changed the value; `saturated` means a value was replaced by a
declared boundary; `stale` means age exceeded the definition's stale threshold;
`type_mismatch` means observed representation/shape differs from the binding;
and `unavailable` means no source value was available. These flags describe
acquisition evidence only; no tolerance, flight-performance, event-severity,
or finding state is permitted.

Quality flags use array-set semantics: values are unique and serialized in
ascending lexical order. Loaders and programmatic constructors reject duplicate
or noncanonical order rather than silently sorting. An empty tuple means no
known acquisition degradation; it does not assert validity.

For every raw-observation lineage entry, status implies these minimum
quality flags: `unavailable`, `orphaned`, `read_error`, `type_mismatch`, and
`provider_degraded` each require the equal-named flag; absent
provider-degraded evidence additionally requires the flag matching its absent
reason. `ok` implies no flag. Other flags arise only from declared validation,
transform, timing, or acquisition evidence. `valid` is prohibited with
`conversion_failed`, `unavailable`, `orphaned`, `read_error`, or
`type_mismatch`; other quality flags may coexist with any validity state when
the measurement definition authorizes them. No quality flag is invented from
an empty array.

Operational evaluation—within tolerance, outside tolerance, indeterminate, or
a later FOQA-oriented finding—is not a validity or quality flag and remains
outside this project increment.

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
- ordered raw-observation lineage containing complete observations or immutable
  observation references;
- ordered derivation-parent sample references; and
- producer identity.

Its exact version-1 properties are `contract_family`, `schema_version`,
`sample_id: Uuid`, `producer: ProducerIdentity`, `session_id: Uuid`,
`stream_id: Uuid`, `epoch_id: Uuid`, `sequence: UInt63`, `measurement_ref:
DefinitionRef`, `binding_ref: DefinitionRef`, `normalization`, ordered
`applied_transforms`, `validity`, `quality`, optional `freshness_age_ns:
UInt63`, nonempty ordered `observation_lineage`, ordered `derivation_parents`, and
`content_hash`.

`normalization` is exactly one tagged variant:

- `{"kind":"succeeded","value":InlineValue,"unit":UnitSpec}` or, for a
  referenced-byte measurement,
  `{"kind":"succeeded","payload":PayloadReference,"unit":{"kind":"unitless"}}`;
- `{"kind":"absent","reason":NormalizedAbsentReason}`; the
  `normalization_failed` reason additionally requires `failed_step_id:
  Identifier`, which is prohibited for every other reason.

`NormalizedAbsentReason` is `source_absent`, `normalization_not_attempted`,
`normalization_failed`, or `not_applicable`. Successful representation and
unit must equal the resolved measurement definition. `source_absent` requires
an absent primary raw observation; `normalization_not_attempted` requires the binding
disposition `accept_raw_only`; `normalization_failed` requires
`conversion_failed` and a failed step present in the resolved binding; and
`not_applicable` requires validity
`not_applicable`. Any absent normalization prohibits validity `valid` and
requires at least one quality flag.

`applied_transforms` is an ordered array of `AppliedTransform`; each contains
`step_id: Identifier` and `algorithm: AlgorithmRef`. The entries must exactly
equal the step-ID/algorithm prefix declared by the resolved binding. It is
empty for a direct binding and for normalization not attempted. This contract
validates the declaration and lineage; it never executes the algorithm. A
succeeded normalization contains the complete binding transform list. A failed
normalization contains only completed steps preceding `failed_step_id`. Every
other absent-normalization reason has an empty applied-transform array.

Each `observation_lineage` entry is exactly one variant:

- `{"kind":"inline","observation":RawObservation}`; or
- `{"kind":"reference","observation_ref":RecordRef}`.

Each record reference must name the raw-observation family/version and every
observation identity is unique in the array. Entry zero is the binding's
primary source. It is followed by one entry for every required dependency in
binding order, then any present optional dependencies in binding order, then
any present companions in companion order. Every entry's provider, adapter,
resource identity, and resource selection must match its binding declaration.
An optional input that is absent has no fabricated lineage entry.
`derivation_parents` is an ordered array of unique `RecordRef` values naming
measurement-sample version 1 and cannot contain the sample's own identity.
Order is algorithm input order, not lexical order.

`RecordRef` pins a runtime UUID, family URI, schema version, and content hash.
Every sample reaches all raw observations it consumed through complete records
or immutable references. A provider-specific exhaustive audit stream is not a
substitute for this lineage.

A normalized value is prohibited when conversion failed or any required raw
lineage entry is unavailable, orphaned, or a read error. An absent normalized value requires
non-valid validity and at least one explanatory quality flag. Values outside a
declared range may be preserved with `out_of_declared_range` and non-valid
validity; a value changed to the boundary requires `saturated`. Rounding and
binary/storage precision loss require `rounded` and `precision_lost`
respectively.

`validate_sample(sample, measurement_catalog, binding_catalog, *,
observations=(), parent_samples=())` is a pure operation. The two closure
arguments are finite sequences indexed by validated record identity; duplicate
identities fail. It resolves pinned references and checks representation,
shape, unit, range, binding provider/adapter/resource identity and selection,
observed-versus-declared type/shape compatibility, applicability,
status-to-quality mapping, and lineage. An inline lineage entry is validated
directly; a reference must resolve in `observations`; every derivation parent
must resolve in `parent_samples`. It does not normalize the observation or
execute transforms.

Applicability validation uses the primary raw observation's
`applicability_context`. Unless validity is `not_applicable`, every measurement
and binding selector must have an equal `(class_id, value)` entry. For
`not_applicable`, at least one required selector's class must be present with a
different value and normalization must use the equal-named absent reason.
Missing selector context yields `unknown`, not `not_applicable`. Extra context
entries are allowed. Two lineage observations that carry the same `class_id`
with different values conflict and invalidate the sample. Empty
definition/binding applicability imposes no selector requirement and cannot
support `not_applicable`.

`validate_sample_closure(samples, observations, measurement_catalog,
binding_catalog)` validates each sample as above, rejects a missing or
hash-mismatched target, and performs depth-first cycle detection over
derivation parents. It does not consult a global registry or storage. A
reference outside the supplied closure is a missing-lineage error, not an
implicitly trusted external edge.

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

Its exact version-1 properties are `contract_family`, `schema_version`,
`frame_id: Uuid`, `producer: ProducerIdentity`, `session_id: Uuid`, `stream_id:
Uuid`, `epoch_id: Uuid`, `sequence: UInt63`, `acquisition_clock:
ClockDomain`, `acquisition_reading: ClockReading`, optional `acquisition_utc:
UtcInstant`, optional `acquisition_anchor: ClockAnchor`, canonical `samples`,
arrival-ordered `observations`, ordered unique `limitations`, and
`content_hash`. The acquisition clock is `host_monotonic`; its ID matches the
reading and anchor, and its producer instance matches the frame producer.
`acquisition_utc` and `acquisition_anchor` are either both
absent or both present, and the anchor UTC equals the acquisition UTC.

Samples are unique by sample UUID and by the tuple of measurement reference,
binding reference, and sample sequence. They appear in ascending order by
measurement ID/revision, binding ID/revision, sample sequence, then sample UUID.
The constructor and loader reject noncanonical order. This permits more than
one corroborating binding for a measurement without making tuple order
nondeterministic.

Raw observations preserve actual arrival order and have unique observation
identities. Samples embedded in a frame use only `RecordRef` lineage entries to observations
in that frame rather than duplicating them inline. A repeated provider value is
represented by a distinct observation identity, with the `duplicate` quality
condition reflected in affected samples when the producer classifies it as a
duplicate. A frame does not imply an ARINC 717 frame, resampling, simultaneity,
or successful continuity.

`validate_frame(frame, measurement_catalog, binding_catalog)` recursively
validates samples and observations, identities, ordering, sample-to-observation
reference closure, and acquisition-instant compatibility. It does not build or
mutate a frame.

Every embedded sample and observation must match the frame's session, stream,
and epoch IDs. Producer identities remain those of the component that created
each record and need not equal the frame producer. Sample, observation, and
frame sequences are each scoped by record family as well as session, stream,
and epoch; no ordering or contiguity is inferred across record families. Each
observation reference resolves by record ID, family, version,
and hash to exactly one frame observation. Every derivation-parent reference
resolves to a frame sample, so the frame is a complete validation closure.
Unreferenced observations are allowed because they preserve accepted arrival
evidence; their order remains significant.

When a receipt reading shares the acquisition clock domain, it must not be
later than the acquisition reading. When domains differ, both timing values
must have anchors; validation converts each reading to an exact rational UTC
nanosecond estimate from its unit/tick period and accepts it only when the
observation's lower uncertainty bound is not later than the frame's upper
uncertainty bound. The validator never claims exact cross-domain ordering. A
sample freshness age is permitted only for a same-domain primary observation and
must equal the non-negative checked difference converted exactly to integer
nanoseconds; a fractional-tick result, overflow, negative result, or
cross-domain age is rejected.

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

The exact function stems are `measurement_catalog`, `source_binding_catalog`,
`raw_observation`, `measurement_sample`, and `measurement_frame`. Each exposes
`load_{stem}_v1(binary_file)`, `loads_{stem}_v1(bytes_or_str)`,
`dump_{stem}_v1(value, binary_file)`, and `dumps_{stem}_v1(value) -> bytes`;
braces here denote the five literal stems just listed, not a runtime generic
dispatcher. A string input is Unicode JSON text; byte
input must be UTF-8 without BOM. Dump functions always write the canonical
UTF-8 document including one final LF and never close a caller-owned stream.
There is no unversioned `load`, `loads`, `dump`, or `dumps` alias. Canonical
JSON primitives remain under `xplane_fdau.contracts`; family loaders live in
their owning semantic packages.

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

JSON property paths use RFC 6901 JSON Pointer. The root is the empty string;
property tokens escape `~` as `~0` and `/` as `~1`; array indices use canonical
base-10 with no leading zero. Source is a caller-supplied display name or
`<memory>`. Line and column are one-based and appear only for JSON syntax or a
duplicate property for which the parser supplies an exact location.

For one load operation, error precedence is deterministic:

1. malformed UTF-8/BOM, JSON syntax, or duplicate property:
   `ContractParseError`;
2. recognized envelope with a different family or schema version:
   `UnsupportedContractVersionError`;
3. missing, unknown, or wrong-JSON-type property/tag variant:
   `ContractShapeError`;
4. unsupported canonical-domain value, including integer overflow, binary64
   overflow/underflow, non-finite programmatic value, non-NFC/surrogate text,
   invalid object key, document/parameter-depth overflow, or illegal `null`:
   `CanonicalJSONError`;
5. declared/computed self-hash mismatch: `ContractHashError`;
6. local semantic or cross-field invariant: `ContractValidationError`.

Within one tier, validation follows the semantic property order stated for the
containing type, then increasing array index; pure cross-document validators
follow their argument order and the canonical definition/sample order. They
report the first failure only. Programmatic construction starts at tier 3 and
uses the identical JSON Pointer. Diagnostics quote at most 160 Unicode code
points of a non-payload scalar; raw inline values, algorithm parameter values,
and payload content are never echoed.

Unknown properties, unknown enum values, incompatible references, and future
schema versions fail closed. There is no implicit migration or best-effort
coercion.

## Schema and conformance corpus

Each schema is JSON Schema Draft 2020-12, carries the exact project URL as
`$id`, rejects unevaluated properties, and references shared `$defs` without a
runtime schema-validator dependency. Packaged resources under
`xplane_fdau.schemas` and published documentation copies under `docs/schemas`
are byte-identical.

Every schema contains exactly `$schema`, `$id`, `title`, `type`, `$defs`,
`properties`, `required`, and `unevaluatedProperties` at its root. Conditional
and union rules live inside `properties` references and `$defs`; no other root
keyword is permitted. `$schema` and `$id` use
the exact URIs fixed above, root type is `object`, and
`unevaluatedProperties` is `false`. Cross-resource `$ref` is prohibited in
version 1: each file carries the shared named `$defs`, and equal named
definitions are byte-identical canonical JSON subtrees across resources,
avoiding resolution or packaging ambiguity. Schemas contain no defaults and do not
claim semantic validation for ordering, hashing, reference closure, clock
comparison, or cross-field policies. Schema files are UTF-8 without BOM,
canonical project JSON with one final LF; their documentation copy is compared
byte-for-byte with the packaged resource.

The authoritative installed corpus lives under:

```text
xplane_fdau/conformance/v1/
|-- manifest.json
|-- accepted/
|-- rejected/
`-- canonical/
```

The source-test mirror is `tests/fixtures/contracts/v1/`; the published
documentation mirror is `docs/contracts/conformance/v1/`. At C4.2 closure all
three trees are byte-identical by relative path. The wheel contains the
packaged tree, the sdist contains all three, and installed-wheel conformance
uses `importlib.resources` without reaching the checkout. No corpus resource
is created during D1.1 design approval.

The manifest records for every case:

- contract family and schema version;
- input resource;
- accepted or rejected disposition;
- expected error class and JSON property path for rejected cases;
- expected canonical resource and SHA-256 for accepted cases; and
- a concise requirement identifier.

`manifest.json` is canonical project JSON with exactly
`corpus_schema_version: 1` and `cases`. Cases are sorted by `case_id`, which is
an `Identifier` beginning `test.`. Each case contains `case_id`,
`requirement_id: Identifier`, `contract_family`, `schema_version: 1`,
`disposition`, and repository-relative POSIX `input_resource`. Paths contain no
empty, `.` or `..` segment and remain below the corpus root.

The exact case variants are:

| `disposition` | Additional properties | Meaning |
| --- | --- | --- |
| `accepted` | `canonical_resource`, `canonical_sha256: Sha256` | input may be noncanonical JSON but loads successfully and emits the named canonical bytes/hash |
| `canonical` | `canonical_resource`, `canonical_sha256: Sha256` | input bytes are already identical to the named canonical bytes and hash |
| `rejected` | `expected_error_class`, `expected_path` | load fails with the exact public error class name and RFC 6901 pointer |

`expected_error_class` is exactly one of `ContractParseError`,
`ContractShapeError`, `ContractValidationError`, `CanonicalJSONError`,
`UnsupportedContractVersionError`, or `ContractHashError`; `expected_path` is
a syntactically valid RFC 6901 pointer, including the empty root pointer.

Accepted and canonical cases prohibit error properties; rejected cases
prohibit canonical properties. An input resource lives under `accepted/`,
`canonical/`, or `rejected/` matching disposition; every canonical resource
lives under `canonical/`. Case IDs and input paths are unique; canonical paths
may be shared only when their bytes/hash expectation is equal. The manifest
itself is not a contract family and has no
`content_hash`; artifact/corpus verification records its SHA-256 externally.

Fixtures use synthetic `test.*` definitions and deterministic UUIDs. They do
not become product catalog content. Canonical files are exact byte vectors,
including their final LF.

Schemas express wire shape. Python semantic validators and fixture requirements
express invariants that JSON Schema cannot state reliably, including computed
hashes, catalog reference resolution, canonical ordering, same-clock-domain
comparison, and sample lineage.

### Python/native conformance protocol

Here “native” means a future non-Python implementation, not the native X-Plane
FDR format. Every implementation exposes a corpus runner that consumes one
manifest path and produces one conformance-result document. CLI spelling is
implementation-owned; input corpus bytes and output document shape are shared.

The result document has exact properties `protocol_version: 1`,
`implementation_id: Identifier`, `implementation_version: VersionText`, and
`results`. Results preserve manifest case order and each contains `case_id`,
`result` (`passed` or `failed`), and optional failure-only `actual_error_class`,
`actual_path`, `actual_sha256`, and `diagnostic`. A passed result has no optional
failure property. A failed result contains only the properties relevant to the
case expectation: either both `actual_error_class` and `actual_path`, or
`actual_sha256`, but never both alternatives. `diagnostic` is independently
optional bounded `NfcText(1024)` and is not compared for parity. An unexpected
successful load reports the emitted canonical hash; an unexpected rejection or
wrong rejection reports its error class/path; a canonical-byte mismatch reports
the actual hash. The result protocol is not a contract family and has no
`content_hash`. The document uses the canonical JSON profile and one final LF.

Runner process status is 0 when every manifest case passed, 1 when the corpus
was valid but at least one case failed, and 2 for invocation, unreadable-corpus,
or invalid-manifest failure. Status 2 produces no conformance-result document.
Python/native parity requires byte-identical canonical resources and SHA-256,
equal accepted/rejected classification, and equal rejected error class and
JSON Pointer. Implementation IDs, versions, and diagnostics are deliberately
not equal across implementations.

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

## FDM/FOQA extension boundary

FDM and FOQA-support mechanics are firm local product responsibilities under
the core-scope amendment, but are not implemented by this canonical-contract
increment. Later analysis contracts consume canonical samples, frames,
archives, quality, timing, continuity, lineage, and replay without changing
their meaning or adding analysis policy to acquisition records.

The dependency path remains:

```text
X-Plane client observation
        -> canonical qualified evidence
        -> flight/phase segmentation and derived parameters
        -> versioned event-set evaluation
        -> candidate and validated findings
        -> aggregation, trends, and report projections
```

Acquisition validity describes the evidence. An operational finding describes
an analysis result under a versioned profile. The later FDM/FOQA layer must
preserve that distinction, declare parameter and continuity prerequisites,
carry derivation and event-definition provenance, and refuse to silently treat
inadequate evidence as valid. FAA AC 120-82 informs the analysis and review
model through the governing amendment; approved-program governance,
de-identification authority, identity custody, corrective-action decisions,
and regulatory claims remain external organizational responsibilities.

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

## Normative technical references

- RFC 8785, section 3.2.2.3 and Appendix B, fixes binary64 number
  serialization only: `https://www.rfc-editor.org/rfc/rfc8785.html`.
- RFC 6901 fixes JSON Pointer syntax: `https://www.rfc-editor.org/rfc/rfc6901.html`.
- JSON Schema Draft 2020-12 Core and Validation fix schema dialect and keyword
  semantics: `https://json-schema.org/draft/2020-12/json-schema-core` and
  `https://json-schema.org/draft/2020-12/json-schema-validation`.
- RFC 9562 fixes UUID layout/version terminology:
  `https://www.rfc-editor.org/rfc/rfc9562.html`.
- RFC 6838 fixes media-type type/subtype terminology:
  `https://www.rfc-editor.org/rfc/rfc6838.html`.

Later revisions of these references do not silently change version 1. A
contract revision must deliberately adopt changed behavior and add new
conformance vectors.

## Delivery sequence and plan boundaries

`ROADMAP.md` treats `C1` through `C4` as architectural epics. `BACKLOG.md`
decomposes them into eighteen run-sized child slices:

1. `C1.1` canonical JSON and number encoding;
2. `C1.2` identity, hashing, references, authority, and provenance;
3. `C1.3` typed values and payload references;
4. `C1.4` clock domains, UTC, anchors, and simulator timing;
5. `C1.5` validity and quality vocabulary;
6. `C2.1` measurement-definition model;
7. `C2.2` measurement catalog and schema;
8. `C2.3` source-binding definition;
9. `C2.4` binding catalog and cross-catalog validation;
10. `C3.1` raw-observation record and schema;
11. `C3.2` measurement-sample record and schema;
12. `C3.3` raw/sample lineage and validation;
13. `C3.4` measurement-frame record and schema;
14. `C3.5` frame closure, ordering, and validation;
15. `C4.1` schema resource parity and version inventory;
16. `C4.2` cross-language conformance corpus;
17. `C4.3` public API and documentation closure; and
18. `C4.4` artifact matrix and independent review.

Each child receives one focused implementation plan when selected. One agent
run advances one primary child slice; cross-cutting documentation and backlog
updates do not silently complete another child. Plan tasks remain beneath their
child slice rather than becoming substitute backlog items.

Every plan uses test-first `unittest` steps, frequent scoped commits, focused
and complete verification, and the exact acceptance gates in `BACKLOG.md`. A
later plan cannot weaken an earlier child slice's verified contract. No release
action is part of any plan.

## Acceptance criteria

The cross-epic design is complete only when every separately planned child
satisfies its exact acceptance subsection below.

### C1.1 — Canonical JSON and binary64/integer encoding

- Exact UTF-8, Unicode, object-key, array, string-escaping, and final-LF
  vectors pass.
- Signed 64-bit integer and finite binary64 canonical lexical vectors pass.
- Duplicate keys, non-NFC/surrogate text, overflow, and non-finite values fail
  with exact error context.
- Canonical bytes and SHA-256 results are deterministic without relying on
  incidental `json.dumps()` float spelling.

### C1.2 — Identity, hashing, references, authority, and provenance

- Semantic IDs, revisions, UUIDs, generations, and sequences enforce exact
  syntax and range.
- Definition and record self-hashes use the specified canonical preimages.
- Definition/record references pin identity, revision/version, and hash.
- Authority, provenance, and producer values are immutable and round-trip.

### C1.3 — Typed values and content-addressed payload references

- Boolean, integer, real, string, enumeration, vector, array, and byte-only
  representations retain exact type and order.
- Boolean/numeric coercion, unauthorized nulls, invalid shapes, and invalid
  enum values fail closed.
- Payload references preserve media type, length, hash, role, and retention
  status without reading storage.
- Programmatic and loaded validation produce equivalent property paths.

### C1.4 — Clock domains, UTC instants, anchors, and simulator timing

- Clock domains/readings preserve unit, resolution, origin, scope, and
  producer identity.
- UTC instants preserve exact nanosecond text and explicit `Z`.
- Same-domain comparison succeeds while unrelated-domain comparison fails.
- Clock anchors, uncertainty, source timing, simulator timing, replay/pause,
  cycle, and acquisition-phase values round-trip without invention.

### C1.5 — Validity states and acquisition-quality vocabulary

- Validity is a closed state independent of quality flags.
- Quality flags are closed, unique, and lexically ordered.
- Empty quality flags do not manufacture validity.
- Operational findings and tolerances cannot enter acquisition quality.

### C2.1 — Measurement-definition model and semantic invariants

- Representation-specific, unit/unitless, frame/datum/axis, precision,
  resolution, range, and enumeration invariants pass.
- Freshness, interpolation, discontinuity, sensitivity, applicability, and
  provenance fields are explicit.
- Irrelevant representation fields and semantic revision mismatches fail.
- Synthetic definitions are immutable, hash-stable, and round-trip.

### C2.2 — Measurement catalog, schema, ordering, and references

- Catalog ID/revision/hash, authority, provenance, scope, and definition
  ordering are exact.
- Duplicate or noncanonical definition order fails closed.
- Version-1 measurement-catalog schema matches runtime shape.
- No provider resource identity or stock X-Plane catalog content ships.

### C2.3 — Source-binding definition and transform references

- Each binding pins one exact measurement reference.
- Provider/adapter, resource, expected/observed shape boundary, native unit,
  applicability, dependencies, companions, phase, and replay policy are
  explicit.
- Transform/calibration references contain identity and data-only parameters,
  never executable expressions.
- Failure dispositions and irrelevant fields fail closed.

### C2.4 — Binding catalog and pure cross-catalog validation

- Binding catalog identity, ordering, uniqueness, schema, and hashes pass.
- Missing or mismatched measurement references fail.
- Direct bindings enforce unit/representation/shape/applicability parity.
- Transformed bindings validate declarations without executing or claiming
  algorithm conformance.

### C3.1 — Raw-observation record and schema

- Provider/adapter/resource, generations, type/shape, timing, status, and value
  evidence round-trip exactly.
- Inline value, payload reference, and absent value are mutually exclusive.
- Status/value combinations enforce the approved matrix.
- Receiver timing is never relabeled as source timing.

### C3.2 — Measurement-sample record and schema

- Sample/session/stream/epoch/sequence and exact definition references pass.
- Normalized value/unit, applied transforms, validity, quality, and freshness
  obey local invariants.
- Absent or failed normalization cannot contain a fabricated value.
- Version-1 sample schema matches runtime shape and canonical hash.

### C3.3 — Raw/sample lineage and cross-contract validation

- Every sample reaches every consumed observation through a complete record or
  immutable record reference.
- Ordered derivation-parent references remain intact and cycle-free within the
  supplied validation closure.
- Catalog-resolved sample representation, unit, range, binding, status, and
  quality validation passes.
- Missing, mismatched, or stale lineage fails with exact context.

### C3.4 — Measurement-frame record and schema

- Frame identity, acquisition instant, samples, observations, producer, and
  limitations round-trip.
- Complete raw observations preserve arrival order.
- Samples preserve canonical semantic order and use frame-local observation
  references.
- Version-1 frame schema matches runtime shape and canonical hash.

### C3.5 — Frame closure, canonical ordering, and validation

- Sample and observation identities are unique and reference closure is
  complete.
- Noncanonical sample order fails rather than being silently rewritten.
- Frame/session/stream/epoch/timing conflicts fail with exact context.
- Multiple corroborating bindings for one measurement are accepted.

### C4.1 — Schema resource parity and version inventory

- All five version-1 schema resources have exact IDs and family mappings.
- Packaged and documentation schema copies are byte-identical.
- Schema inventory rejects missing, duplicate, or unrecognized families.
- Installed resources contain no provider or standards implementation.

### C4.2 — Accepted, rejected, and canonical conformance corpus

- Manifest covers accepted, rejected, and canonical cases for every family.
- Rejected cases pin expected error class and JSON property path.
- Accepted cases pin canonical bytes and SHA-256.
- Boundary corpus covers numeric, Unicode, timing, ordering, lineage, and
  reference semantics.

### C4.3 — Public API and contract documentation closure

- Root package remains version-only; semantic packages expose exact owned
  names.
- Documentation distinguishes measurement/binding, observation/sample,
  FDAU/ARINC frames, and acquisition/operational quality.
- Native FDR APIs and documentation remain unchanged and green.
- Runtime import-boundary tests reject providers, hosts, networks, and
  third-party imports.

### C4.4 — Built/installed artifact matrix and independent review

- Complete `unittest` and repository quality gates pass.
- Fresh wheel/sdist contain exact schemas, fixtures/resources, and no runtime
  dependency or provider content.
- Installed-wheel smoke passes on Python 3.12, 3.13, and 3.14 outside the
  checkout.
- Independent review has no unresolved load-bearing finding.
- Version `0.1.0` remains unreleased and no push/tag/publication occurs.

## Required following increments

After independent review, the next specifications remain:

1. acquisition profiles, demand resolution, lifecycle events, continuity, and
   generic fan-out;
2. canonical archive, artifact manifest, recovery, and deterministic replay;
3. projection from canonical samples to the native X-Plane FDR sink with
   explicit loss reporting; and
4. later edition-pinned standards profiles and local FDM/FOQA-support work,
   each under a separately reviewed local increment.
