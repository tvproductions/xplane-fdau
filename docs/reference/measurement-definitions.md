# Measurement definitions

`MeasurementDefinition` declares the immutable meaning of one measurement
revision within the X-Plane FDAU. Import it and its supporting metadata from
`xplane_fdau.measurements`; representation and unit models belong to
`xplane_fdau.contracts`. Definitions contain no provider resource identity and
perform no acquisition, unit conversion, interpolation or sample evaluation.
The identities in this example are synthetic; no stock catalog is bundled.

## Construct a synthetic definition

All structural models use keyword-only, frozen, slotted dataclasses. Constructors
validate the complete definition, including relationships between fields. They
copy supported list/tuple inputs to immutable tuples; unordered containers and
arbitrary iterables are rejected. Optional properties are omitted by leaving
out their arguments; explicit `None` is prohibited.

```python
from xplane_fdau.contracts import (
    Authority,
    ProvenanceSource,
    RepresentationSpec,
    UnitSpec,
)
from xplane_fdau.measurements import (
    CoordinateSpec,
    DiscontinuityPolicy,
    FreshnessSpec,
    InterpolationPolicy,
    MeasurementDefinition,
    Sensitivity,
    ValidityState,
)

limitations = ["Synthetic example only"]
definition = MeasurementDefinition(
    definition_id="test.boolean",
    definition_revision=1,
    authority=Authority(authority_id="test.authority", authority_revision=1),
    provenance=[ProvenanceSource(
        source_id="test.source", source_revision=1, scope="Synthetic example",
    )],
    title="Synthetic switch state",
    description="Whether a synthetic switch is asserted.",
    limitations=limitations,
    quantity_id="test.switch_state",
    representation=RepresentationSpec(kind="boolean"),
    unit=UnitSpec(kind="unitless"),
    coordinates=CoordinateSpec(kind="not_applicable"),
    freshness=FreshnessSpec(fresh_for_ns=100_000_000, stale_after_ns=500_000_000),
    interpolation_policy=InterpolationPolicy.PROHIBITED,
    discontinuity_policy=DiscontinuityPolicy.PRESERVE,
    allowed_validity=[ValidityState.UNKNOWN],
    allowed_quality=[],
    sensitivity=Sensitivity.UNKNOWN,
    applicability=[],
)

# Identity is computed once after validation and exposed as a read-only property.
identity_hash = definition.content_hash
assert len(identity_hash) == 64
limitations.append("Caller mutation")
assert definition.limitations == ("Synthetic example only",)
assert definition.content_hash == identity_hash
```

Every definition supplies authority, nonempty ordered provenance, title,
description, limitations, quantity, representation, unit, coordinates,
freshness, interpolation and discontinuity policies, allowed validity/quality,
sensitivity and applicability. Empty limitations and applicability are explicit;
empty applicability adds no restriction. Applicability selectors have unique
`class_id` values in ascending lexical order and never authorize simulator
access. Provenance and limitations preserve their declared order; provenance
identities and limitation strings must be unique.

## Representation, units and coordinates

| Representation | Unit | Numeric metadata | Additional representation metadata |
| --- | --- | --- | --- |
| `boolean`, `string` | Unitless | Prohibited | None |
| `integer` | Unitless or declared unit | Required; integer resolution and bounds | None |
| `real` | Unitless or declared unit | Required; binary64 resolution and bounds | None |
| `vector` | Unitless or declared unit | Required; binary64 resolution and bounds | Length 1–1024 |
| `enumeration` | Unitless | Prohibited | Required enumeration members |
| `referenced_bytes` | Unitless | Prohibited | Required payload media types and storage roles |
| `fixed_array`, `variable_array` of integer or real | Unitless or declared unit | Required; element numeric domain | Scalar element representation and array lengths |
| `fixed_array`, `variable_array` of enumeration | Unitless | Prohibited | Scalar element representation, array lengths and required enumeration members |
| `fixed_array`, `variable_array` of Boolean or string | Unitless | Prohibited | Scalar element representation and array lengths |

Arrays are one-dimensional, contain one scalar representation, and have at
most 65535 elements. A fixed array has length 1–65535; a variable array declares
minimum and maximum lengths, with zero permitted and minimum no greater than
maximum. Vectors and arrays cannot nest. Fields belonging to a different
representation are rejected; for example, adding `NumericSpec` to the Boolean
example raises `ContractValidationError` at `/numeric`.

`UnitSpec(kind="unitless")` explicitly declares no unit. A declared unit uses
`kind="unit"`, `quantity_id` equal to the definition's quantity, and `unit_id`.
Quantity, unit, frame and datum IDs are authority-qualified identities; the
library supplies no universal registry or conversion engine.

| Coordinate variant | Required semantics | Axis constraint |
| --- | --- | --- |
| `not_applicable` | No frame, datum, axes, handedness or sign meaning | Axis fields prohibited |
| `applicable` for a vector | Reference frame, handedness, ordered axes; optional datum | Axis count equals vector length |
| `applicable` for another representation | Reference frame, handedness, ordered axes; optional datum | Exactly one axis |

Use `applicable` whenever a definition assigns any frame, datum, axis,
handedness or sign meaning. Each `AxisSpec` declares an axis ID, direction and
sign convention; IDs are unique and order is preserved. `handedness` is `left`
or `right`. At most 32 coordinate axes are permitted, including on vectors.

`NumericSpec` declares storage precision from 1 through 64 bits, a positive
resolution, and optional inclusive minimum/maximum bounds. Integer metadata
uses signed 64-bit integers; real metadata uses finite binary64 values.
Booleans are rejected as numbers, and integer and real domains are not coerced.
When both bounds exist, minimum cannot exceed maximum. A vector or numeric
array applies the same resolution and bounds independently to every element;
there are no per-axis bounds.

Enumeration members have unique codes in ascending code order. Their kinds
are `known`, `unknown` or `reserved`, with at most one `unknown` member.
Reserved codes are definition metadata. Later normalized sample validation
must resolve the definition and authorize only non-reserved codes; this
increment does not deliver that sample validator. A raw `InlineValue` may
preserve a syntactically valid source enumeration code regardless of its later
resolved meaning.

## Policies, quality and freshness

`allowed_validity` is nonempty and explicitly lists authorized states;
`valid` is never implied. `allowed_quality` lists authorized acquisition
flags; an empty tuple authorizes no degradation flags. Both collections must
be unique and in ascending lexical order. Empty quality neither asserts
validity nor changes `unknown` to `valid`. See
[measurement quality](measurement-quality.md) for the vocabulary and the
later sample compatibility boundary.

`FreshnessSpec` requires at least one nonnegative nanosecond threshold. When
both exist, `fresh_for_ns` cannot exceed `stale_after_ns`. The declared sample
semantics distinguish these boundaries:

- A known primary age at or below `fresh_for_ns` is in the fresh interval.
  When that threshold exists, later validation permits `valid` only with a
  known primary age in that interval.
- An exact same-domain consumed-input age greater than `stale_after_ns`
  establishes staleness. Equality is not stale. Cross-domain evidence alone
  cannot establish or disprove it.
- With both thresholds, the primary interval above `fresh_for_ns` through
  `stale_after_ns` is neither asserted fresh nor stale and cannot be `valid`.

Definitions validate this metadata; they do not calculate ages or classify
samples. Clock/lineage checks and quality corroboration arrive with the later
sample contracts. A missing threshold does not silently acquire a default.

Interpolation is `prohibited`, `hold` or `linear`; `linear` requires a real,
vector or numeric-array representation. Discontinuity policy is `preserve`,
`start_new_epoch` or `reject`. Sensitivity is `public`, `operational`,
`restricted` or `unknown`. These declarations do not execute a policy.

## Revision and identity

A meaning change requires a new `definition_revision`, including changes to
units, sign, reference frame, validity rules or applicability. Schema version
tracks wire shape independently. The cached `content_hash` binds all definition
content, including authority, ordered provenance and revision, to the
measurement-catalog family and schema version. It is neither a constructor
argument nor a mutable field. A stateless constructor cannot compare against
historical revisions or enforce the publisher's revision obligation.

Private canonical-entry readers and serializers are internal integration
details. They validate shape, domains, hash and semantics before constructing
models. They are not public document loaders. Measurement catalogs, their
schema and public family load/dump APIs remain C2.2 work. Shared convenience
APIs for definition serialization, hashing and reference creation remain
pending the later public API closure; use the delivered `content_hash`
property for definition identity.

## Public API

::: xplane_fdau.measurements.models
    options:
      show_root_heading: true
      members:
        - EnumerationMemberKind
        - InterpolationPolicy
        - DiscontinuityPolicy
        - Sensitivity
        - AxisSpec
        - CoordinateSpec
        - NumericSpec
        - EnumerationMember
        - EnumerationSpec
        - FreshnessSpec
        - ApplicabilitySelector
        - MeasurementDefinition
