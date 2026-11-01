# Measurement validity and acquisition quality

Validity and quality describe different aspects of acquisition evidence.
Import their closed vocabularies from `xplane_fdau.measurements`.

## Explicit validity

A producer supplies one `ValidityState` for the measurement's declared use:

| State | Meaning |
| --- | --- |
| `valid` | The sample satisfies its resolved definition and binding. |
| `invalid` | Evidence proves that it does not satisfy them. |
| `unknown` | Available evidence cannot establish either valid or invalid. |
| `not_applicable` | The resolved applicability selectors exclude the sample context. |

An empty quality collection means no known acquisition degradation. It never
supplies a validity assertion or changes `unknown` to `valid`.

```python
from xplane_fdau.measurements import QualityFlag, ValidityState

validity = ValidityState.UNKNOWN
quality = (QualityFlag.ROUNDED, QualityFlag.STALE)
no_known_degradation: tuple[QualityFlag, ...] = ()

assert validity.value == "unknown"
assert tuple(flag.value for flag in quality) == ("rounded", "stale")
```

Individual enum construction checks a spelling. A tuple of enums is ordinary
Python data; it does not perform complete sample validation. These vocabulary
types are not standalone canonical contract documents and have no family JSON
loader or dumper.

## Acquisition-quality flags

Quality arrays must contain unique values in ascending lexical order.
Contract validation rejects duplicates and noncanonical order rather than
silently sorting or deduplicating input.

| Flag | Acquisition evidence |
| --- | --- |
| `conversion_failed` | A declared normalization step produced no value. |
| `discontinuous` | The value crosses or follows a declared source/time epoch discontinuity. |
| `dropped` | An expected acquisition item was not delivered. |
| `duplicate` | Distinct raw evidence repeats an already classified source item. |
| `orphaned` | The resource identity remains known but its owner/source is no longer valid. |
| `out_of_declared_range` | The preserved value violates the measurement range. |
| `precision_lost` | Destination storage discarded binary/numeric precision. |
| `provider_degraded` | The provider reported degraded service. |
| `read_error` | Acquisition failed while reading. |
| `reordered` | Source sequence/arrival evidence is out of declared order. |
| `rounded` | A declared rounding rule changed the value. |
| `saturated` | A value was replaced by a declared boundary. |
| `stale` | Age is greater than the definition's stale threshold. |
| `type_mismatch` | Observed representation/shape differs from the binding. |
| `unavailable` | No source value was available. |

Operational tolerance, flight performance, event severity and finding states
are outside this acquisition vocabulary. Good acquisition quality does not
imply an acceptable operational result.

Complete sample compatibility checks, measurement authorization and lineage
corroboration belong to the later sample contracts (C3). For example,
`not_applicable` requires empty quality and an absent-normalization reason of
`not_applicable`; a nonempty quality collection must obey the specification's
validity compatibility matrix. The enums alone do not establish those facts.

## Public API

::: xplane_fdau.measurements.models.ValidityState
    options:
      show_root_heading: true
      members: true

::: xplane_fdau.measurements.models.QualityFlag
    options:
      show_root_heading: true
      members: true