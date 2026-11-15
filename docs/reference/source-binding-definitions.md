# Source-binding definitions

`SourceBindingDefinition` describes how a declared source and an optional ordered
transform chain map to an exact measurement reference. It is an immutable
declaration. Construction validates local source and transform consistency;
it does not acquire evidence or execute algorithms.

All identities below are synthetic `test.*` values. No provider bindings or
runtime catalogs are bundled.

## Construct a synthetic binding

The keyword-only constructor requires `definition_id`, `definition_revision`,
`authority`, `provenance`, `measurement_ref`, `source`, `applicability`,
`dependencies`, `companions`, `transforms`, `failure_policy`,
`acquisition_phase`, `replay_policy`, and `limitations`, in that declaration
order. There are no optional root constructor fields or policy defaults.
Collections accept ordered lists/tuples and are copied to tuples; provenance is
nonempty. Applicability is sorted by unique class ID. Limitations preserve order
and cannot repeat.

`SourceSpec` requires provider and adapter identities, resource kind and ID,
declared representation and shape, and native unit. Its optional constructor
fields follow those required fields: `owner_signature`, `resource_selection`,
`declared_element_representation`, and `declared_payload`. Omit absent
properties; explicit `None` is prohibited. Array representations require an
element representation; referenced bytes require payload constraints.

```python
from dataclasses import replace

from xplane_fdau.bindings import (
    FailurePolicy, SourceBindingDefinition, SourceSpec, TransformInput,
    TransformStep,
)
from xplane_fdau.contracts import (
    AdapterIdentity, AlgorithmRef, Authority, DefinitionRef, ProvenanceSource,
    ProviderIdentity, ShapeSpec, UnitSpec,
)

unit = UnitSpec(kind="unit", quantity_id="test.length", unit_id="test.feet")
source = SourceSpec(
    provider=ProviderIdentity(provider_family_id="test.provider", provider_version="1"),
    adapter=AdapterIdentity(adapter_family_id="test.adapter", adapter_version="1"),
    resource_kind="test.resource", resource_id="synthetic/height",
    declared_representation="real", declared_shape=ShapeSpec(kind="scalar"),
    native_unit=unit, resource_selection={"kind": "index", "index": 0},
)
measurement = DefinitionRef(
    definition_id="test.height", definition_revision=1, definition_hash="b" * 64,
)
policy = FailurePolicy(
    unavailable="reject", orphaned="reject", stale="accept_raw_only",
    read_error="reject", type_mismatch="accept_without_value",
    provider_degraded="accept_flagged",
)
direct = SourceBindingDefinition(
    definition_id="test.height_binding", definition_revision=1,
    authority=Authority(authority_id="test.authority", authority_revision=1),
    provenance=[ProvenanceSource(
        source_id="test.source", scope="Synthetic example", source_revision=1,
    )],
    measurement_ref=measurement, source=source, applicability=[],
    dependencies=[], companions=[], transforms=[], failure_policy=policy,
    acquisition_phase="unknown", replay_policy="preserve",
    limitations=["Synthetic example; measurement compatibility is unresolved."],
)
step = TransformStep(
    step_id="test.adjust",
    algorithm=AlgorithmRef(
        definition_id="test.adjustment", definition_revision=1,
        definition_hash="a" * 64, parameters={"test.offset": 1.0},
    ),
    inputs=[TransformInput(
        input_id="binding.primary", representation="real",
        shape=ShapeSpec(kind="scalar"), unit=unit,
    )],
    output_representation="real", output_shape=ShapeSpec(kind="scalar"),
    output_unit=unit,
)
converted = replace(direct, transforms=[step])
assert converted.measurement_ref == measurement
assert len(converted.transforms) == 1
assert converted.content_hash != direct.content_hash
assert len(converted.content_hash) == 64
```

## Declared sources and local transform checks

Source metadata is **declared** configuration. An **observed** representation
or shape belongs to later acquisition evidence; `observed_representation` and
`observed_shape` are not SourceSpec or binding-entry fields.

Selection is omitted for the whole resource, or an immutable mapping with
`kind="index"` and nonnegative `index`, or `kind="slice"`, nonnegative
`start` and positive `length`. Primary, dependency and companion source
tuples must be unique within a binding. The tuple uses provider family, adapter
family, resource kind, resource ID and selection; versions and owner signatures
do not distinguish duplicates. Different bindings may reuse a source.

Dependencies and companions have distinct, unique input IDs. Companions describe
status/validity evidence and cannot supply transform values. Transforms may
consume `binding.primary`, declared dependencies and preceding step IDs.
Unknown, companion, self and forward references fail. Every transform input must
exactly match the resolved declared representation, element, payload, shape and
unit. Dependencies require at least one transform. Algorithms remain opaque
exact references with immutable data-only parameters; numerical correctness and
execution are deferred to A1.4.

Every failure condition has an explicit disposition. `accept_flagged` is
forbidden for unavailable, orphaned and read-error evidence. These declarations
do not evaluate samples; C3 owns that behavior.

## Identity, errors and delivery boundary

The read-only cached `content_hash` binds the complete definition, including
measurement and algorithm reference triples and parameters, to the
source-binding-catalog family and integer schema version 1. Its own hash is
excluded from the preimage, which ends in LF. The constructor cannot accept a
caller-supplied self-hash. Fields are frozen; selections and parameters are
defensively owned.

Semantic error order differs from constructor optional-field order and canonical
JSON lexical key order. Within each validation tier, the root order is identity,
authority, provenance, measurement reference, source, applicability, dependencies,
companions, transforms, failure policy, acquisition phase, replay policy and
limitations. Source semantic order places owner signature and selection before
declared metadata. Entry reading checks duplicates, complete shape, canonical
domains, a well-formed declared hash and semantics before construction.

C2.4 will provide the binding catalog, schema and public family I/O, and resolve
measurement existence/hash, direct/final compatibility, applicability narrowing
and measurement-authorized failure outcomes. The private entry reader is not a
public interchange API. C4.3 retains the shared convenience API closure:
`definition_ref`, `record_ref`, `compute_content_hash` and structural-model
dispatch in public `canonical_bytes` are not introduced here.

See [measurement definitions](measurement-definitions.md),
[measurement catalogs](measurement-catalogs.md), and the
[approved canonical design](../superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md).
