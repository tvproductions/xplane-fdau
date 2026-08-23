# xplane-fdau Acquisition, Recording, Projection, and Pinning Contract Design

- **Governance:** active
- **Status:** draft
- **Date:** 2026-08-23
- **Decision owner:** Jeff / tvproductions
- **Roadmap epic:** `D1`
- **Roadmap children:** `D1.2`
- **Approval:** —

## Authority and purpose

This design completes the contract-only planning surface required by `D1.2`.
It is subordinate to `ROADMAP.md`, the approved repository-owned scope
amendment, and the approved canonical measurement-contract design:

- `docs/architecture/xplane_fdau_core_scope_amendment.md`;
- `docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md`;
  and
- `docs/superpowers/specs/2026-08-22-q4xpcc-contract-handoff-readiness-design.md`.

The design fixes the version-1 contract shapes and policies that q4xpcc needs
to reconcile its four Phase 24A Slice 2 plans. It is binding architecture input
for later, separately reviewed `A1`, `R1`, and `P1` specifications. It does not
implement those contracts, create schemas or fixtures, build an archive, emit a
native FDR file, produce a release artifact, or authorize consumer adoption.

The approved canonical design remains authoritative for canonical JSON,
number encoding, hashing, references, UUIDs, provenance, values, timing,
validity, quality, observations, samples, and frames. This design uses those
types without redefining them.

## Decisions carried forward

The following decisions are fixed:

1. `xplane-fdau` is an X-Plane-specific, transport-free,
   standard-library-only core. External clients own concrete XPPython3/XPLM,
   Web API, network, process, callback, and simulator lifecycle behavior.
2. Acquisition policy, continuity, generic fan-out, canonical recording,
   recovery, deterministic replay, native FDR projection, and reusable
   deployment-integrity evidence are FDAU-owned.
3. q4xpcc owns cards, missions, application sessions, BIT policy, procedures,
   guidance, action authorization, and q4xpcc operational findings.
4. Native X-Plane FDR is a first-class package-owned format and sink, but not
   the canonical archive. New canonical-to-native exports target version 4.
5. Native-FDR-to-canonical mapping is not specified by the current roadmap.
   This design records that future adapter seam but does not invent its mapping
   contract or claim that a native `FDRSample` is canonical evidence.
6. Edition-pinned ARINC decoders and encoders are later package-owned
   representation adapters. Concrete buses, devices, networks, and simulator
   I/O remain external. No ARINC layout or conformance claim is added here.
7. Reusable FDM/FOQA analysis is later local `F1` work. This design preserves
   generic subscriber, archive, continuity, lineage, and replay seams for F1,
   but does not preempt the exact analysis ports assigned to `F1.1`.
8. Approved-program governance, identity custody, corrective-action authority,
   protections, and regulatory claims remain external.

## Non-goals

This increment does not:

- modify runtime code, package metadata, existing schemas, fixtures, or public
  APIs;
- define provider-specific discovery, connection, scheduling, callbacks, or
  error recovery;
- define q4xpcc cards, FSMs, findings, or authorization policy;
- implement acquisition, recording, replay, projection, ARINC, or FDM/FOQA;
- define native-FDR-to-canonical semantic mappings;
- create an implementation plan for an `A1`, `R1`, `P1`, or `F1` child;
- produce a wheel, sdist, archive, native FDR file, manifest, deployment
  receipt, or conformance result;
- select a future release version or fabricate a source revision or artifact
  hash; or
- push, tag, publish, or release.

## Shared version-1 rules

Every top-level family below inherits the approved canonical rules:

- `contract_family`, integer `schema_version: 1`, and computed
  `content_hash` are mandatory;
- generated records carry `ProducerIdentity` and one family-specific UUID;
- definition records carry an `Identifier`, `Revision`, `Authority`, nonempty
  provenance, and computed definition hash;
- no JSON `null`, unknown property, unknown enum value, implicit default,
  best-effort coercion, or implicit version migration is accepted;
- array order is semantic unless the property is explicitly an `ArraySet`;
- `DefinitionRef` pins identifier, revision, and definition hash;
- `RecordRef` pins UUID, family URI, schema version, and content hash;
- JSON fields use the semantic validation order in their property tables;
- canonical JSON is UTF-8 without BOM, uses the approved number and Unicode
  rules, and ends with one LF; and
- structural and semantic rejection uses the approved six-leaf
  `FDAUContractError` hierarchy and RFC 6901 paths.

The existing `RecordRef` version-1 family allow-list expands only when the
corresponding future implementation child delivers a family below. D1.2 does
not change the implemented allow-list.

This design uses the following additional exact notation:

- `PositiveRational` has exactly `numerator: UInt63` and
  `denominator: UInt63`; both are greater than zero and their greatest common
  divisor is one. `PositiveRationalDuration` instead has
  `numerator_ns: UInt63` and `denominator: UInt63` under the same constraints
  and represents `numerator_ns / denominator` nanoseconds. Both are compared
  with arbitrary-precision cross multiplication, never binary64.
- `CountDistribution<K>` is an object with exactly one `UInt63` property for
  every member of the stated closed vocabulary `K`, including zero-valued
  members. Its containing section states whether members are exclusive and
  therefore whether the values must sum to a named population.
- `RecordRange` has exactly `first_index: UInt63` and `last_index: UInt63`,
  with first not greater than last. Both ends are inclusive.
- `RecordRef` values introduced by this design use the canonical reference
  shape. Their family allow-list expands transactionally with the owning
  schema/model child; a reference to a family not yet delivered remains
  invalid in the current runtime.
- A property described as variant-selected is a tagged object with required
  `kind` followed by exactly the properties listed for that kind. Properties
  from another variant are prohibited.
- When a family inventory below begins with its family-specific fields, the
  exact top-level order is always `contract_family`, `schema_version`, those
  fields in the stated order, then `producer` for a generated record and
  finally `content_hash`. Definition families instead contain their stated
  identity, authority, provenance, body, limitations, and `content_hash`.

Unless a tighter limit is stated here, the canonical design's collection,
text, nesting, and property-count limits apply. Validation first performs
canonical parse, family/version dispatch, exact shape, primitive value checks,
and root hash verification. It then follows the semantic property order stated
here, array index order, referenced-record argument order, and finally recorded
event order for causal precedence. Runtime inability is represented only by a
valid outcome or `FailureEvidence`; malformed contract data never becomes a
runtime outcome.

### New family inventory and future resources

Each row fixes the future family URI and schema resource. The packaged schema
path will be `xplane_fdau/schemas/<stem>-v1.schema.json`; the byte-identical
documentation copy will be `docs/schemas/<stem>-v1.schema.json`.

| Family | Stem and family-URI suffix | Kind and identity property | Owning future child |
| --- | --- | --- | --- |
| Acquisition profile | `acquisition-profile` | definition; `profile_id` | `A1.1` |
| Consumer demand | `consumer-demand` | record; `demand_id` | `A1.2` |
| Demand resolution | `demand-resolution` | record; `resolution_id` | `A1.3` |
| Transform registry | `transform-registry` | definition; `registry_id` | `A1.4` |
| Acquisition-session descriptor | `acquisition-session-descriptor` | record; `acquisition_session_id` | `A1.5` |
| Acquisition lifecycle event | `acquisition-lifecycle-event` | record; `event_id` | `A1.5` |
| Acquisition-session result | `acquisition-session-result` | record; `result_id` | `A1.9` |
| Continuity report | `continuity-report` | record; `continuity_report_id` | `A1.7` |
| Fan-out delivery event | `fanout-delivery-event` | record; `delivery_event_id` | `A1.8` |
| Recording-session descriptor | `recording-session-descriptor` | record; `recording_session_id` | `R1.1` |
| Raw-retention policy | `raw-retention-policy` | definition; `policy_id` | `R1.2` |
| Archive order entry | `archive-order-entry` | record; `order_entry_id` | `R1.2` |
| Archive checkpoint | `archive-checkpoint` | record; `checkpoint_id` | `R1.3` |
| Artifact manifest | `artifact-manifest` | record; `artifact_manifest_id` | `R1.4` |
| Recording-session result | `recording-session-result` | record; `recording_result_id` | `R1.5` |
| Recovery result | `recovery-result` | record; `recovery_result_id` | `R1.5` |
| Replay-session descriptor | `replay-session-descriptor` | record; `replay_session_id` | `R1.6` |
| Replay lifecycle event | `replay-lifecycle-event` | record; `replay_event_id` | `R1.6` |
| Replay-session result | `replay-session-result` | record; `replay_result_id` | `R1.6` |
| Native-FDR projection profile | `xplane-fdr-projection-profile` | definition; `projection_profile_id` | `P1.1` |
| Native-FDR projection report | `xplane-fdr-projection-report` | record; `projection_report_id` | `P1.5` |
| Deployment policy | `deployment-policy` | definition; `deployment_policy_id` | delivery ownership must be assigned before implementation |
| Consumer deployment receipt | `consumer-deployment-receipt` | record; `deployment_receipt_id` | delivery ownership must be assigned before implementation |

The full family URI is
`https://tvproductions.github.io/xplane-fdau/contracts/<stem>`. The schema
`$id` is
`https://tvproductions.github.io/xplane-fdau/schemas/<stem>-v1.schema.json`.

Future accepted, rejected, and canonical cases use the approved corpus trees
and filenames beginning `<stem>-`. The three byte-identical roots remain:

- `xplane_fdau/conformance/v1/`;
- `tests/fixtures/contracts/v1/`; and
- `docs/contracts/conformance/v1/`.

No schema or fixture resource is created by D1.2.

The two deployment families are FDAU-owned handoff contracts, but the current
roadmap does not assign their implementation to `C4.4`, `A1`, `R1`, or `P1`.
D1.2 fixes their planning shape without silently expanding an already approved
child. Before implementation, repository governance must assign their schema,
fixture, and API delivery to an explicit dependency-correct local child. That
later assignment cannot make q4xpcc runtime adoption earlier than `I1.1` or
live acquisition adoption earlier than `I1.2`.

## Acquisition profiles

`AcquisitionProfile` is an immutable semantic definition. Its properties are:

| Property | Type | Rule |
| --- | --- | --- |
| `contract_family` | literal family URI | acquisition-profile URI |
| `schema_version` | integer `1` | exact |
| `profile_id` | `Identifier` | definition identity |
| `profile_revision` | `Revision` | semantic revision |
| `authority` | `Authority` | required |
| `provenance` | nonempty array of `ProvenanceSource` | declared authority order |
| `items` | nonempty array of `AcquisitionProfileItem` | unique `item_id`; declared order is semantic |
| `limitations` | array of `NfcText(1024)` | at most 256; empty permitted |
| `content_hash` | `Sha256` | computed definition hash |

`AcquisitionProfileItem` has exact properties `item_id`, `measurement`,
`binding_candidates`, `binding_selection`, optional
`minimum_successful_bindings`, `cadence`, `continuity`, `acquisition_phase`,
`allowed_resampling`, `allowed_interpolation`, `required_validity`,
`prohibited_quality`, `stream_role`, `degradation_priority`, and
`overload_disposition`.

- `measurement` is an exact `DefinitionRef`. `binding_candidates` is a
  nonempty ordered array of unique exact `DefinitionRef` values, each of
  which resolves to that measurement revision and hash.
- `binding_selection` is `exact`, `preferred_with_fallback`,
  `any_compatible`, or `corroborated`. `exact` requires exactly one candidate.
  `preferred_with_fallback` selects the first compatible available candidate
  in semantic candidate order. `any_compatible` selects the first compatible
  available candidate in canonical `(definition_id, definition_revision,
  definition_hash)` order. Those three modes select exactly one source.
  `corroborated` requires at least two candidates, selects every compatible
  available candidate in canonical order, and requires
  `minimum_successful_bindings` from two through the candidate count. That
  field is prohibited for the other modes.
- `cadence` has exactly `requested_period: PositiveRationalDuration` and
  `maximum_period: PositiveRationalDuration`. Requested period must not be
  greater than maximum period.
- `continuity` contains `minimum_observation_count: UInt63`,
  `minimum_elapsed_ns: UInt63`, `maximum_staleness_ns: UInt63`,
  `maximum_gap_ns: UInt63`, `early_tolerance_ns: UInt63`, and
  `late_tolerance_ns: UInt63`. Gap and staleness are independent constraints;
  neither implies an ordering between their values.
- `acquisition_phase` uses the canonical binding acquisition-phase vocabulary.
- `allowed_resampling` is an `ArraySet` drawn from `none`, `hold`, `nearest`,
  `linear`, and `aggregate`. `none` is mutually exclusive with every other
  member.
- `allowed_interpolation` is an `ArraySet` of the measurement definition's
  allowed interpolation policies and cannot broaden that definition.
- `required_validity` is a nonempty `ArraySet<ValidityState>`.
- `prohibited_quality` is an `ArraySet<QualityFlag>`.
- `stream_role` is `bounded` or `continuous`.
- `degradation_priority` is an integer from 0 through 255; a lower value is
  acted on first, with canonical `item_id` order breaking ties.
- `overload_disposition` is `reject_item`,
  `relax_to_maximum_period`, or `suspend_optional`. A required item cannot use
  `suspend_optional` during resolution. Relaxation never exceeds
  `maximum_period`; suspension or relaxation is explicit in a replacement
  demand resolution and `overload_changed` lifecycle event. That event records
  affected item identifiers plus prior and current status and cadence. No
  overload path silently sheds an item or changes its cadence.

Changing cadence, continuity, resampling, interpolation, quality, phase, or
binding meaning requires a new profile revision and hash.

## Allow-listed transform registry

`TransformRegistry` is an immutable catalog definition with exact properties
`contract_family`, `schema_version`, `registry_id`, `registry_revision`,
`authority`, `provenance`, ordered `transforms`, `limitations`, and
`content_hash`.

Each `TransformDefinition` has `algorithm_id`, `algorithm_revision`,
`authority`, nonempty `provenance`, `kind`, ordered `inputs`, `parameters`,
`output`, `determinism`, `loss_dispositions`, and its computed `content_hash`.

- `kind` is `normalization`, `calibration`, `aggregation`, `interpolation`, or
  `resampling`.
- Each input and output fixes representation, shape, payload allowance, and
  unit requirements using the approved canonical value types.
- Each parameter definition has `parameter_id`, `required`, `kind`, and the
  variant selected by `kind`. `kind` is `integer`, `real`, `boolean`,
  `string`, or `enum`. Integer and real variants require inclusive `minimum`
  and `maximum` canonical scalar values of the same representation. Boolean
  has no variant properties. String requires `maximum_code_points: UInt63`.
  Enum requires a nonempty `ArraySet<NfcText>` of `allowed_values`.
  Parameters are data only, and undeclared parameters are rejected.
- `determinism` is the literal `deterministic` in version 1.
- `loss_dispositions` is an `ArraySet` drawn from `exact`, `rounded`,
  `clamped`, `precision_lost`, `out_of_range`, and `conversion_failed`.
  When `exact` is present it is the sole member; otherwise `exact` is
  prohibited and at least one loss disposition is required.
- Arbitrary expressions, import paths, callbacks, source text, bytecode, and
  caller-supplied executable code are prohibited.
- An `AlgorithmRef` resolves only when identifier, revision, hash, parameter
  names, parameter types, and parameter values all match one registry entry.

Execution order is the binding's declared transform-step order. A failed step
records the existing canonical normalization failure and quality evidence; it
never substitutes a plausible value. A registry can validate declarations
before execution exists, but cannot claim algorithm conformance until A1.4
delivers its implementation and fixtures.

## Consumer demands and atomic resolution

`ConsumerDemand` is an immutable generated record with exact properties:

| Property | Type | Rule |
| --- | --- | --- |
| envelope | canonical family/version | required |
| `demand_id` | `Uuid` | record identity |
| `consumer_id` | `Identifier` | consumer contract identity, not a display name |
| `consumer_instance_id` | `Uuid` | one running consumer instance |
| `generation` | `UInt63` | contiguous from zero for that consumer instance |
| `replaces` | optional `RecordRef` | prohibited at generation zero; otherwise the exact generation-minus-one demand |
| `profile` | `DefinitionRef` | exact acquisition profile |
| `items` | nonempty array of `DemandItem` | profile order; unique profile item reference |
| `requested_at` | `UtcInstant` | evidence timestamp |
| `producer` | `ProducerIdentity` | required |
| `content_hash` | `Sha256` | computed |

Each `DemandItem` has `profile_item_id`, `requirement`, and `retention`.
`requirement` is `required` or `optional`. `retention` is an exact
`RetentionRequirement` with these orthogonal properties:

- `canonical_records` is `samples`, `frames`, or `samples_and_frames`;
- `accepted_raw_observations` is `not_requested`, `when_supplied`, or
  `required`;
- `raw_payloads` is `not_requested`, `when_supplied`, or `required`; and
- `provider_audit` is `not_requested`, `when_supplied`, or `required`.

No total ordering exists among those axes. A resolution can satisfy
`raw_payloads: required` only with selected payload-represented sources, and it
can satisfy `provider_audit: required` only when every selected binding
declares that capability. Otherwise the item receives `retention_conflict`;
those capabilities are never inferred.

Updating any item creates a new demand record and generation. Active demand
records are never mutated. A consumer cannot reuse or skip a generation,
replace a non-immediate predecessor, or replace another consumer's demand.

`DemandResolution` is a generated record with `resolution_id`,
`resolver_instance_id`, `generation`, optional `replaces`,
`receipt_clock_domain`, nonempty ordered `demands`, ordered `item_outcomes`,
ordered `source_acquisitions`, `outcome`, `producer`, and `content_hash`.

- `resolution_id` and `resolver_instance_id` are `Uuid`; `generation` is
  `UInt63`; `receipt_clock_domain` is one canonical `host_monotonic`
  `ClockDomain` whose producer instance equals the resolver instance.
- Resolution generation is contiguous from zero within one resolver instance.
  `replaces` is prohibited at generation zero and otherwise references the
  exact generation-minus-one resolution.
- `demands` contains the currently active `DemandReceipt` values in strictly
  increasing `receipt_sequence` order. Each receipt has the exact demand
  `RecordRef`, `receipt_sequence`,
  `receipt_clock`, and optional `receipt_utc`. Receipt sequence, not a
  consumer-supplied timestamp, determines replacement and conflict order.
  Receipt sequence is globally contiguous from zero for the resolver instance;
  the active subset may contain gaps after replacement. `receipt_clock` uses
  one declared monotonic resolver clock domain; `receipt_utc` is correlation
  evidence only. Every receipt reading identifies the resolution's
  `receipt_clock_domain`.
- Every demand item appears exactly once in `item_outcomes`.
- An item outcome contains its demand reference, `profile_item_id`,
  `result`, optional `reason`, and optional ordered
  `selected_source_acquisition_ids`.
- `result` is `accepted` or `rejected`.
- `reason` is required only for rejection and is one of
  `unknown_measurement`, `unknown_binding`, `binding_mismatch`,
  `provider_unavailable`, `source_unavailable`, `phase_conflict`,
  `cadence_conflict`, `resampling_conflict`, `interpolation_conflict`,
  `validity_conflict`, `quality_conflict`, `retention_conflict`,
  `insufficient_corroboration`, `capacity_exceeded`, or
  `incompatible_generation`.
- `selected_source_acquisition_ids` is nonempty only for acceptance, contains
  every selected binding source, and satisfies the profile item's binding
  selection and minimum-success rules. It is absent for rejection.
- A `SourceAcquisition` fixes one `source_acquisition_id: Uuid`, exact binding
  reference, `read_period: PositiveRationalDuration`, acquisition phase,
  accepted demand items, and per-consumer delivery period/resampling decision.
  Accepted items are unique pairs of demand `RecordRef` and profile item ID in
  demand-receipt then profile order. Each `DeliveryDecision` has exact
  properties `demand: RecordRef`, `profile_item_id: Identifier`,
  `endpoint_id: Uuid`, `delivery_period: PositiveRationalDuration`, and
  `resampling`. `endpoint_id` equals the demand's consumer-instance ID;
  resampling is `none`, `hold`, `nearest`, `linear`, or `aggregate` and must be
  allowed by that profile item. Delivery decisions use accepted-item order.
- Source acquisition uses the fastest authorized accepted demand. Slower
  delivery is permitted only by a demand's profile.
- `outcome` is `accepted` only when every required item is accepted. Optional
  rejection is retained but does not block activation. Otherwise outcome is
  `rejected`, and no source acquisition may begin from that resolution.
- Resolution never changes units, bindings, validity, retention, cadence, or
  quality requirements silently.

Compatibility is evaluated in demand receipt order and profile item order,
but selection does not depend on host mapping order. Bindings merge only when
their exact reference, phase, source resource, native representation/shape,
and transform closure agree. The selected read period is the minimum requested
period among merged accepted items, bounded independently by every item's
maximum period. Any authorized overload relaxation is applied by degradation
priority then profile item ID and is recorded in item outcomes and the next
lifecycle event. If required-item rejection makes the resolution rejected,
`source_acquisitions` is empty; no partially computed acquisition is activated.

## Acquisition sessions, lifecycle, and terminal results

`AcquisitionSessionDescriptor` freezes one accepted resolution. Its exact
properties are `contract_family`, `schema_version`, `acquisition_session_id`,
`resolution`, `opened_at`, `receipt_clock_domain`, ordered `streams`,
`initial_epoch_id`, ordered `source_contexts`, `producer`, and `content_hash`.

- `resolution` references an accepted `DemandResolution`.
- `opened_at` is canonical `ObservationTiming`; `receipt_clock_domain` equals
  its receipt clock; `initial_epoch_id` is `Uuid`.
- Each `StreamDeclaration` contains `stream_id: Uuid`,
  `source_acquisition_id: Uuid`, `binding: DefinitionRef`,
  `clock_domain_id: Uuid`, `initial_sequence: UInt63`, and
  `initial_generation: UInt63`. It resolves exactly one source acquisition and
  its binding; stream IDs, source-acquisition IDs, and binding references are
  unique in descriptor order.
- Exactly one `source_contexts` entry exists for each source acquisition, in
  stream declaration order. It has exact properties `source_acquisition_id`,
  `provider`, `adapter`, `source_generation`, `connection_generation`,
  `sources`, and `limitations`. Provider and adapter use `ProviderIdentity`
  and `AdapterIdentity`; both generations are `UInt63`; `sources` is an
  ordered nonempty array of `ProvenanceSource`; and `limitations` is a bounded
  NFC-text array. It contains no connection object, host handle, callback,
  credential, SDK value, or untyped simulator/plugin/replay label.
- A session owns identities and evidence, not simulator lifecycle.

`AcquisitionLifecycleEvent` has `event_id`, `acquisition_session_id`,
`event_sequence`, `epoch_id`, `timing`, `kind`, variant-selected `detail`,
`producer`, and `content_hash`. Event sequence is contiguous from zero within
the acquisition session.

The closed version-1 `kind` vocabulary is `opened`, `demand_replaced`,
`overload_changed`, `epoch_started`, `source_degraded`, `source_restored`,
`pause_changed`, `replay_state_changed`, `time_speed_changed`,
`clock_discontinuity`, `stopping`, and `terminal`.

`timing` is canonical `ObservationTiming`; its required receipt clock, reading,
and UTC instant record when the core accepted the event. Optional source timing
is present only when the source supplied it. The exact `detail` variants are:

| `kind` | Required detail properties in semantic order | Optional detail properties | Invariants |
| --- | --- | --- | --- |
| `opened` | `descriptor: RecordRef` | — | descriptor names this acquisition-session descriptor |
| `demand_replaced` | `prior_resolution: RecordRef`, `replacement_resolution: RecordRef` | — | same resolver instance; replacement generation is prior plus one |
| `overload_changed` | nonempty ordered `items` | — | each item is `demand: RecordRef`, `profile_item_id: Identifier`, prior/current `activation`, and prior/current `delivery_period`; activation is `active`, `relaxed`, or `suspended`, and periods are `PositiveRationalDuration` when the corresponding activation is active or relaxed and otherwise omitted |
| `epoch_started` | `epoch_id: Uuid`, `cause` | `prior_epoch_id: Uuid` | cause is `session_open`, `source_restart`, `connection_replacement`, `aircraft_reload`, `plugin_reload`, `replay_seek`, `clock_regression`, or `explicit_boundary`; prior epoch is prohibited for session open and required otherwise |
| `source_degraded` | `source_acquisition_id: Uuid`, `failure: FailureEvidence` | — | source is declared by the descriptor and was not already degraded |
| `source_restored` | `source_acquisition_id: Uuid`, `degraded_event: RecordRef` | — | reference names the unmatched degradation event for the source |
| `pause_changed` | `prior: Boolean`, `current: Boolean` | — | values differ |
| `replay_state_changed` | prior and current canonical replay-state values | — | values differ |
| `time_speed_changed` | `prior: Binary64`, `current: Binary64` | — | bit patterns differ after canonical negative-zero normalization |
| `clock_discontinuity` | `cause`, `prior_clock_domain_id: Uuid`, `current_clock_domain_id: Uuid`, `prior_reading: ClockReading`, `current_reading: ClockReading` | — | cause is `regression`, `jump`, or `domain_replaced`; reading IDs match their respective domain IDs; regression/jump requires equal domains and domain replacement requires unequal domains |
| `stopping` | `termination_reason` | `primary_failure: FailureEvidence` | reason uses the acquisition-result vocabulary; failure presence obeys that result's reason/outcome rules |
| `terminal` | `termination_reason` | `primary_failure: FailureEvidence` | emitted after delivery stops; it never references the later session result |

Overload items preserve profile order within demand receipt order. State-change
variants never infer a prior value or relabel receipt evidence as source
evidence. A degradation/restoration pair does not create a new epoch by
itself; a separately recorded `epoch_started` event does so when the selected
session policy requires it.

`AcquisitionSessionResult` has `result_id`, `acquisition_session_id`,
`opened_descriptor`, `terminal_event`, `outcome`, `termination_reason`,
optional `primary_failure`, ordered `cleanup_failures`, ordered
`continuity_reports`, ordered `recording_results`, `ended_at`, `producer`, and
`content_hash`.

`result_id` and `acquisition_session_id` are `Uuid`; `opened_descriptor` and
`terminal_event` are exact equal-session `RecordRef` values; `ended_at` is
canonical `ObservationTiming` not earlier than the terminal event in a
comparable receipt domain.

- `terminal_event` is the exact `RecordRef` of the already-created terminal
  lifecycle event. Its termination reason and primary failure must match the
  result.

- `outcome` is `completed`, `stopped`, `aborted`, or `failed`.
- `termination_reason` is `consumer_complete`, `consumer_stop`, `source_end`,
  `required_evidence_unsatisfied`, `required_sink_failed`,
  `discontinuity_policy`, `explicit_abort`, or `internal_failure`.
- `completed` requires `consumer_complete` and no primary failure.
- `stopped` requires `consumer_stop` or `source_end` and no primary failure.
  `aborted` requires `explicit_abort` and no primary failure. `failed` requires
  one of `required_evidence_unsatisfied`, `required_sink_failed`,
  `discontinuity_policy`, or `internal_failure` plus a primary failure whose
  domain/code supports that reason.
- The first causal failure in lifecycle-event order is primary. Cleanup
  failures preserve their own phase and never replace it.

The result's `continuity_reports` and `recording_results` are `ArraySet<RecordRef>`
values restricted to their equal-named families. Every reference belongs to
this acquisition session. `cleanup_failures` preserves attempt order rather
than using array-set ordering.

## Generic synchronous ports and fan-out

Ports are synchronous, capability-segregated, and transport-free. Future
public protocol operation names and argument roles are fixed as follows; their
exact Python module placement belongs to the owning child plan:

```python
ObservationIngress.submit(observation: RawObservation) -> IngressOutcome
FrameSubscriber.open(descriptor: AcquisitionSessionDescriptor) -> OpenOutcome
FrameSubscriber.accept(frame: MeasurementFrame) -> DeliveryOutcome
FrameSubscriber.close(notice: SessionCloseNotice) -> CloseOutcome
RecordingSink.open(descriptor: RecordingSessionDescriptor) -> OpenOutcome
RecordingSink.append(frame: MeasurementFrame) -> DeliveryOutcome
RecordingSink.checkpoint() -> CheckpointOutcome
RecordingSink.commit(request: CommitRequest) -> CommitOutcome
RecordingSink.abort(failure: FailureEvidence) -> AbortOutcome
RecordingSink.recover(request: RecoveryRequest) -> RecoveryOutcome
RecordingSink.close() -> CloseOutcome
```

`SessionCloseNotice` has the acquisition-session descriptor reference,
terminal lifecycle-event reference, termination reason, final delivery
sequence by stream, and optional primary failure. `CommitRequest` has the
recording-session descriptor reference, terminal lifecycle-event reference,
termination reason, final delivery sequence by stream, final checkpoint when
one exists, and optional primary failure. Both are immutable inputs created
before close or commit outcomes; aggregate acquisition and recording results
are created afterward and therefore cannot participate in their own outcome
hashes.

The operation outcomes are exact tagged values:

- `IngressOutcome` contains `result` (`accepted` or `rejected`), the submitted
  observation reference, and `failure` only when rejected.
- `OpenOutcome` contains `result` (`opened`, `rejected`, or `failed`), endpoint
  identity, and `failure` only when not opened.
- `DeliveryOutcome` contains `result` (`delivered`, `dropped`, `detached`, or
  `failed`) for the submitted frame and ordered nonempty
  `delivery_event_refs`. The final reference describes the submitted frame;
  any preceding reference describes an older frame evicted by the same call.
- `CheckpointOutcome` contains `result` (`checkpointed`, `not_due`, or
  `failed`), a checkpoint reference only when checkpointed, and failure only
  when failed.
- `CommitOutcome` contains `result` (`committed`, `conflict`, or `failed`),
  every artifact state reached by the attempt, and failure only for conflict
  or `failed`. A conflict or failure may therefore retain preserved-partial
  state without claiming commit.
- `AbortOutcome` contains `result` (`aborted` or `failed`) and failure only
  when failed.
- `RecoveryOutcome` contains `result` (`resumed`, `finalized_partial`,
  `preserved_partial`, `discarded`, or `failed`) and an exact recovery-result
  reference.
- `CloseOutcome` contains `result` (`closed` or `failed`) and failure only when
  failed.

No operation outcome contains a host exception, transport handle, future, or
callback.

These are push boundaries. The core does not sleep, poll, start a thread,
connect to X-Plane, or invoke consumer business logic reentrantly. A future F1
analysis component may implement a subscriber or consume replay/archive
records, but F1's analysis-specific ports remain owned by `F1.1`.

`FanoutDeliveryEvent` records `delivery_event_id`, `acquisition_session_id`,
optional `recording_session_id`, `endpoint_id`, `frame`,
`delivery_sequence`, `disposition`, `backpressure`, optional `failure`,
optional `policy`, `timing`, `producer`, and `content_hash`.

`endpoint_id: Uuid` equals the consumer instance ID for a frame subscriber and
the sink-session ID for a recording sink. `recording_session_id` is required
for a recording sink and prohibited for a frame subscriber. `frame` is the
exact measurement-frame `RecordRef`; `delivery_sequence: UInt63` is contiguous
from zero independently per endpoint. `timing` is canonical
`ObservationTiming` used as receipt evidence for the delivery decision.

`disposition` is the final value `delivered`, `dropped`, `detached`, or
`failed`. `backpressure` is a `BackpressureEvidence` value with `kind`
(`none`, `waited`, or `overflow`), `queue_depth_before`, `queue_depth_after`,
`wait_duration_ns`, and `overflow_action`. Wait duration is positive exactly
when kind is `waited` and is zero otherwise. Queue depths are `UInt63`.
`overflow_action` is `none`, `rejected_new`, or `dropped_oldest`; it is
`none` exactly when kind is not `overflow`.

Blocking therefore ends in a delivered or failed disposition and records
`waited`; it is not itself a disposition or failure. Rejecting an incoming
frame records that frame as dropped with `rejected_new`. Dropping the oldest
records a dropped event for the evicted frame and a separate event for the
incoming frame. Dropped, detached, and failed dispositions require explicit
policy or failure evidence and contribute to continuity. `policy`, when
present, is the exact descriptor or profile `RecordRef` authorizing the
decision. The core never silently drops a frame. One endpoint failure does not
mutate another endpoint's result.

## Continuity reports

`ContinuityReport` has `continuity_report_id`, `acquisition_session_id`,
`resolution`, `scope`, ordered `item_results`, ordered `stream_summaries`,
`overall_result`, `evaluated_at`, `producer`, and `content_hash`.

- `resolution` is the accepted demand-resolution `RecordRef` under evaluation.
  `evaluated_at` is canonical `ObservationTiming`.
- `scope` has exactly `first_event: RecordRef`, `last_event: RecordRef`,
  optional `first_frame: RecordRef`, optional `last_frame: RecordRef`, and
  nonempty ordered `epoch_ids: Uuid[]`. Event references are acquisition
  lifecycle events and bound an inclusive event-sequence interval. Frame
  references are both present or both absent, are measurement-frame
  references, and bound the inclusive delivered-frame interval. Epoch IDs
  occur in first-appearance order and exactly cover the selected events and
  frames.
- Every accepted required and optional demand item appears once in
  `item_results`; each result is scoped to that demand item's consumer
  endpoint rather than aggregated across unrelated fan-out endpoints.
- An item result has exact properties `demand`, `profile_item_id`,
  `endpoint_id`, `effective_delivery_period`, `continuity_policy`,
  `observed_count`, `eligible_count`, `delivered_count`,
  `eligible_delivered_count`, `elapsed_span_ns`, `first_slot_ready`, optional
  `minimum_interval_ns`, optional `maximum_interval_ns`, `gap_count`,
  `maximum_gap_ns`, `drop_count`, `duplicate_count`, `reorder_count`,
  `staleness_count`, `validity_distribution`, `quality_distribution`,
  `epoch_count`, `source_generation_count`, `sink_failures`,
  `classification`, and `reasons`. Counts and durations are `UInt63`; the two
  interval properties are present exactly when at least one within-epoch
  interval exists.
- `validity_distribution` is `CountDistribution<ValidityState>` and
  `quality_distribution` is `CountDistribution<QualityFlag>`. A sample with
  multiple quality flags contributes once to every matching quality bucket,
  so quality counts do not sum to observed count; `eligible_count` and the
  validity distribution do. `sink_failures: UInt63` counts failed delivery
  events for this endpoint and scope.
- A sample is eligible only when its validity is allowed by
  `required_validity`, it contains none of `prohibited_quality`, its age at the
  containing frame's acquisition time is represented by `freshness_age_ns`
  and is no greater than `maximum_staleness_ns`, and its timing is comparable
  within the same clock domain and epoch. Continuity count, readiness, span,
  cadence, and gap tests
  use samples whose delivery disposition to that consumer endpoint is
  `delivered`; excluded observations remain visible in the validity, quality,
  staleness, and delivery distributions.
- Within each epoch, expected slots start at the epoch-start lifecycle
  event's monotonic reading, or the report scope's first included monotonic
  reading when the scope begins inside an epoch, and advance by the exact
  rational `effective_delivery_period` through the inclusive scope end.
  `first_slot_ready` is true exactly when the first expected slot is matched.
  A delivered eligible sample satisfies at most one slot when its acquisition
  reading lies within the closed interval from slot minus
  `early_tolerance_ns` through slot plus `late_tolerance_ns`. Slots and samples
  are matched in increasing exact rational time, then canonical sample order;
  unmatched slots produce `cadence_shortfall`. No binary-float rounding is
  used in slot construction or comparison.
- Intervals and gaps are evaluated independently within each epoch. No
  interval crosses an epoch boundary, and an epoch transition is reported as
  `epoch_boundary`, never as an ordinary gap. `elapsed_span_ns` is the sum of
  the last-minus-first eligible-delivered span in each epoch. Gap count is the
  number of within-epoch eligible-delivered intervals greater than
  `maximum_gap_ns`; `maximum_gap_ns` is zero when none exists. `no_observation`
  makes the item insufficient. `clock_incomparable` makes it indeterminate
  unless an independently provable shortfall already makes it insufficient.
- `classification` is `sufficient`, `insufficient`, or `indeterminate`.
- `reasons` is an `ArraySet` drawn from `no_observation`, `count_shortfall`,
  `span_shortfall`, `cadence_shortfall`, `gap_exceeded`, `stale_evidence`,
  `invalid_evidence`, `prohibited_quality`, `drop_observed`,
  `duplicate_observed`, `reordering_observed`, `epoch_boundary`,
  `provider_change`, `sink_failure`, or `clock_incomparable`.
- Overall result is `sufficient` only when every required item is sufficient;
  an indeterminate required item makes it indeterminate unless another required
  item is insufficient. Optional items never improve the overall result.

Each `StreamSummary` has exact properties `stream_id: Uuid`,
`source_acquisition_id: Uuid`, `first_epoch_id: Uuid`, `last_epoch_id: Uuid`,
`epoch_count: UInt63`, `observed_count: UInt63`, `sample_count: UInt63`,
`frame_count: UInt63`, `delivered_frame_count: UInt63`, `drop_count: UInt63`,
`duplicate_count: UInt63`, `reorder_count: UInt63`,
`source_generation_count: UInt63`, and `connection_generation_count: UInt63`.
Summaries appear in descriptor stream order, cover only the report scope, and
reconcile with the item results and referenced delivery events. Counts include
records excluded from eligibility; they never imply continuity sufficiency.

Continuity reports acquisition sufficiency only. They do not contain q4xpcc
performance findings or FDM/FOQA operational findings.

## Recording-session and sink contracts

One recording session is a fan-out group attached to exactly one acquisition
session. An acquisition session may own zero or more recording sessions, and a
recording session owns one or more sink sessions.

`RecordingSessionDescriptor` has `recording_session_id`,
`acquisition_session_descriptor`, `resolution`, ordered `streams`, ordered
`sinks`, `segment_policy`, `opened_at`, `producer`, and `content_hash`.

`recording_session_id` is `Uuid`; the acquisition descriptor and accepted
resolution are exact `RecordRef` values and agree with one another. `streams`
is a nonempty ordered subset of the acquisition descriptor's complete
`StreamDeclaration` values, preserving descriptor order. `sinks` is nonempty
and unique by sink-session, endpoint, destination, and planned-root identity.
`opened_at` is canonical `ObservationTiming` and is not earlier than the
acquisition descriptor opening in a comparable receipt domain.

Each `SinkDeclaration` has `sink_session_id`, `sink_kind`, `artifact_role`,
`criticality`, `capabilities`, `destination`, optional `profile`,
`planned_root_artifact_id`, `backpressure`, `buffer_capacity`, `publication`,
`recovery_policy`, and `discontinuity_policy`, plus optional
`retention_policy`.

- `sink_session_id` and `planned_root_artifact_id` are `Uuid`; `sink_kind` and
  `artifact_role` are `Identifier` values. The reserved package kinds are
  `xplane_fdau.sink.canonical_archive`,
  `xplane_fdau.sink.xplane_fdr_projection`, and
  `xplane_fdau.sink.canonical_jsonl_audit`. Another kind is permitted only
  when its capabilities are fully declared and it introduces no host object or
  new contract family.
- `criticality` is `required` or `optional`.
- `capabilities` has exact properties `publishes_artifact: Boolean`,
  `supports_checkpoint: Boolean`, `supports_recovery: Boolean`,
  `supports_retention: Boolean`, and optional `required_profile_family` equal
  to one family URI known by the descriptor validator. Profile is required
  exactly when that family is present and must reference it. Retention policy
  is permitted exactly when retention support is true. Checkpoint or recovery
  calls against a false capability are rejected before the sink is opened.
  Reserved-kind capabilities are exact: canonical archive is
  `(publishes_artifact=true, supports_checkpoint=true,
  supports_recovery=true, supports_retention=true)` with no required profile;
  native-FDR projection is `(true, false, true, false)` and requires the
  native-FDR projection-profile family; canonical JSONL audit is
  `(true, true, true, true)` with no required profile. Capability declarations
  are validated by the sink at `open`; a mismatch yields a rejected outcome
  rather than silent degradation.
- `destination` is a `DestinationIdentity` with exact properties
  `destination_id: Identifier`, `kind: Identifier`, and optional
  `locator: NfcText(2048)`. The locator is evidence, not identity, and cannot
  contain credentials, a host handle, or an open stream object.
- `profile` is an exact `DefinitionRef` and is present exactly when
  `required_profile_family` is present.
- `retention_policy` is an exact `DefinitionRef`. It is required for the
  canonical archive kind, permitted only when `supports_retention` is true,
  and prohibited otherwise. Across the required sink
  declarations, at least one retention policy independently satisfies every
  accepted demand item's `RetentionRequirement`; optional sinks cannot satisfy
  required retention evidence.
- `planned_root_artifact_id: Uuid` is allocated before sink open and identifies
  that sink's artifact graph through publication and recovery.
- `backpressure` is `block`, `reject`, or `drop_oldest`. Any drop produces a
  fan-out event and continuity evidence. `drop_oldest` is prohibited for a
  required canonical archive sink.
- `buffer_capacity` is `UInt63`; zero means the sink is synchronous and
  unbuffered, not unbounded.
- `publication` has `mode` exactly `no_replace`, `replace_if_match`, or
  `not_applicable`. `no_replace` and `not_applicable` prohibit
  `expected_prior`; `replace_if_match` requires an `expected_prior` containing
  exactly one prior-state variant. A `byte_artifact` variant contains exact
  byte length and SHA-256; an `artifact_graph` variant contains the prior
  manifest `RecordRef` plus its serialized byte length and SHA-256.
  `not_applicable` is valid only when `publishes_artifact` is false. Publication
  fails with `publication_conflict` if the destination's observed state does
  not match. Unconditional replacement is prohibited.
- `recovery_policy` has `mode` exactly `preserve_partial`, `discard_partial`,
  or `recovery_required`. `discard_partial` requires an embedded
  `DeletionAuthorization` containing `authorization_id: Uuid`, the root
  artifact ID, `authority: Authority`, `reason: NfcText(1024)`, and
  `authorized_at: UtcInstant`; the authorization is prohibited for other
  modes.
- `discontinuity_policy` is `continue`, `stop_sink`, or `stop_recording`.
  `stop_sink` on a required sink has the same recording-result consequence as
  sink failure. No policy implicitly splits an artifact or resets session,
  stream, artifact, or segment identity.

`segment_policy` has exact `maximum_record_count: UInt63` and
`maximum_byte_count: UInt63`. The first reached positive boundary closes the
segment; zero disables only that boundary, and both cannot be zero. It applies
independently to every JSONL logical stream.

Each sink `retention_policy` is an exact `DefinitionRef` to a
`RawRetentionPolicy`. That immutable definition has `contract_family`,
`schema_version`, `policy_id`, `policy_revision`, `authority`, `provenance`,
`canonical_samples`, `canonical_frames`, `accepted_raw_observations`,
`raw_payloads`, `provider_audit`,
`omission_disposition`, `limitations`, and `content_hash`.

- `canonical_samples` and `canonical_frames` are `retain` or `omit`.
- `accepted_raw_observations`, `raw_payloads`, and `provider_audit` are
  `not_requested`, `retain_when_supplied`, or `required`.
- `omission_disposition` is `normalized` or `projected`; it is required when
  any available source representation is omitted and prohibited when all are
  retained.
- The policy satisfies a resolved `RetentionRequirement` only when every
  requested axis is independently satisfied: requested canonical sample and
  frame forms are retained; `when_supplied` permits `retain_when_supplied` or
  `required`; and `required` requires the identical policy value. One retained
  axis never compensates for omission on another axis.
- Canonical frames retain their immutable embedded samples and observations.
  The sample and observation policy axes govern preservation of the complete
  accepted standalone streams, including records that never entered a retained
  frame; they never authorize rewriting an embedded frame closure.
- If an accepted source representation is omitted intentionally, the archive
  uses the declared omission disposition and is never described as `lossless`.

A recording session may span acquisition epochs. Epoch transitions remain
explicit records. A sink may declare a terminal discontinuity policy, but no
implicit split or identity reset occurs.

## Canonical archive logical format

The canonical archive is a manifest-rooted graph of immutable artifacts, not a
pathname, ZIP byte stream, SQLite database, or custom binary container.

The normative version-1 checkpoint and recovery representation is a directory
artifact set:

```text
<recording-session-id>.fdau.partial/
|-- acquisition-session-descriptor.json
|-- recording-session-descriptor.json
|-- definitions/
|   `-- <family-token>/<definition-id>/<revision>-<definition-hash>.json
|-- demands/
|   `-- <consumer-instance-id>/<generation>-<demand-id>.json
|-- demand-resolution.json
|-- streams/
|   `-- <stream-id>/
|       |-- observations/<segment>.jsonl
|       |-- samples/<segment>.jsonl
|       `-- frames/<segment>.jsonl
|-- events/
|   |-- lifecycle/<segment>.jsonl
|   `-- fanout/<sink-session-id>/<segment>.jsonl
|-- order/global/<segment>.jsonl
|-- checkpoints/<checkpoint-sequence>.json
|-- payloads/sha256/<first-two-hex>/<remaining-sixty-two-hex>
|-- continuity/<continuity-report-id>.json
`-- artifact-manifest.json
```

The closed definition-family tokens are `measurement-catalog`,
`source-binding-catalog`, `acquisition-profile`, `transform-registry`, and
`raw-retention-policy`. Each path uses the definition family's identity field,
revision rendered as twenty zero-padded decimal digits, and exact definition
hash. Demand generation and checkpoint sequence use the same twenty-digit
rendering. UUID path components use canonical lowercase UUID text. The archive
contains every demand receipt referenced by its resolution and the complete
definition closure needed to validate retained records; duplicate byte-identical
definitions occur once.

The global-order stream contains one `ArchiveOrderEntry` for every retained
raw observation, measurement sample, measurement frame, acquisition lifecycle
event, and fan-out delivery event. It does not duplicate the target record.
Its exact properties are `contract_family`, `schema_version`,
`order_entry_id: Uuid`, `recording_session_id: Uuid`,
`global_sequence: UInt63`, `logical_stream_key: NfcText(512)`,
`record_index: UInt63`, `record: RecordRef`, `producer`, and `content_hash`.
Global sequence is contiguous from zero for the recording session. The logical
stream key is the target's archive-relative logical stream path without the
segment filename; record index is the target stream's contiguous archive
record index. The referenced target must exist at that key and index with an
equal hash. Order-entry segmenting follows the descriptor's segment policy.
This stream is the sole authority for `recorded_global_order` replay; directory
enumeration, path sorting, timestamps, and manifest member order are not replay
ordering evidence.

Paths are relative POSIX paths with no empty, `.`, or `..` segment. Path
components are NFC, case-sensitive contract values even on a case-insensitive
filesystem, and two paths that collide under Unicode case folding are rejected.
The destination suffix changes from `.fdau.partial` to `.fdau` only after the
selected publication precondition succeeds. The suffix and destination path
are not archive identity.

Stream segment filenames are sixteen lowercase hexadecimal digits naming the
zero-based segment sequence, followed by `.jsonl`. Segment sequence is
contiguous independently for each stream/family or event/sink path. Records
inside a segment are complete canonical JSON records concatenated in append
order. Each already ends in one LF; no additional separator or blank line is
inserted. The descriptor's segment policy closes the segment before appending
a record that would exceed a positive boundary, except that one record larger
than the byte boundary occupies a segment by itself. A closed segment is
immutable.

Large, byte-valued, or provider-native raw payloads remain exact bytes in the
content-addressed payload tree. JSON records reference them using the approved
`PayloadReference`. Base64 is not the canonical raw-payload representation.
Every referenced payload required by the retention policy exists at its hash
path and exactly matches its declared length and SHA-256. An intentionally
omitted payload remains an explicit manifest limitation rather than a dangling
claim that the archive is self-contained or lossless.

A deterministic ZIP may later package the artifact set for transport, and a
SQLite database may later index or project it for analysis. Those artifacts
carry their own identities and `derived_from` relationships and never replace
the manifest-rooted canonical evidence graph.

## Checkpoint, publication, and recovery

`ArchiveCheckpoint` has `checkpoint_id`, `recording_session_id`,
`sink_session_id`, `root_artifact_id`, `descriptor`, `checkpoint_sequence`,
optional `previous_checkpoint`, ordered `sealed_members`, ordered
`open_streams`, ordered `delivery_positions`, `created_at`, `producer`,
and `content_hash`.

The four identity properties are `Uuid`; `descriptor` is the exact
recording-session-descriptor `RecordRef`; `created_at` is canonical
`ObservationTiming`.

- Checkpoint sequence is contiguous from zero per sink session.
  `previous_checkpoint` is prohibited at zero and otherwise references the
  exact sequence-minus-one checkpoint.
- A `SealedMember` records artifact ID, relative path, role, byte length, and
  SHA-256. A JSONL segment additionally records its logical stream key, segment
  sequence, first and last archive record index, first and last record
  `RecordRef`, and record count. Every sealed member named by the prior
  checkpoint appears byte-identically in every later checkpoint.
- An `OpenStream` records artifact ID, relative path, logical stream key,
  segment sequence, first archive record index, next archive record index,
  complete record count, safe byte length, and SHA-256 of exactly that safe
  prefix. Archive record indexes are contiguous from zero per logical stream
  and do not reset at an acquisition epoch. The safe length ends after a
  complete canonical JSON LF and never claims bytes written later.
- Each `delivery_positions` entry fixes one descriptor stream ID and its
  `next_delivery_sequence: UInt63` for this sink, so zero represents no prior
  delivery without a sentinel. Entries use descriptor stream order and are
  unique by stream ID.
- A checkpoint is one consistent cut across all listed streams: append is
  quiescent for the synchronous call, every safe prefix is flushed through the
  cut, sealed-member hashes are verified, and the checkpoint file is itself
  published atomically with no replacement. A reported checkpoint never names
  an unverified or partially serialized checkpoint record.

The planned root artifact receives its `artifact_id: Uuid` before sink open.
Every dynamically created segment, payload, checkpoint, report, or manifest
member receives its own artifact ID before its first byte is written. Those
UUIDs are lifecycle identities and remain stable through recovery. Each
`ArtifactState` has exact properties `artifact_id`, `state_sequence`,
`disposition`, variant-selected `content`, and `recorded_at`.
`state_sequence` is contiguous from zero per artifact; within a supplied state
history, sequence *n* supersedes sequence *n - 1* without mutating it.
`disposition` is `planned`, `open`, `sealed`, `preserved_partial`, or
`published`. Content kind `absent` is valid exactly for a planned artifact or
an open logical graph root. An open, sealed, preserved, or published
byte-bearing artifact uses content kind `bytes` with byte length and SHA-256. A
sealed, preserved, or published logical graph root instead uses content kind
`manifest` with the manifest `RecordRef` plus serialized manifest byte length
and SHA-256. Content state never substitutes for artifact identity.
`recorded_at` is canonical `ObservationTiming`; consecutive states for one
artifact are nondecreasing when receipt clocks are comparable.

An immutable manifest entry uses `content_state` exactly `sealed`,
`preserved_partial`, or `omitted_by_policy`.

- `sealed` requires final byte length and SHA-256 and means the member cannot
  change; it does not predict whether publication of the containing archive
  root will succeed.
- `preserved_partial` requires current byte length, SHA-256, recovery
  eligibility, and failure evidence.
- `omitted_by_policy` references the exact retention policy and prohibits a
  lossless claim.

A terminal sink result separately uses disposition `published`,
`preserved_partial`, `discarded`, `not_created`, `omitted_by_policy`, or
`not_applicable`. `published` requires final byte length and SHA-256 for a byte
root, or the final manifest record and serialized manifest state for a logical
graph root. `discarded` records explicit deletion authorization and cleanup
outcome and contains no content hash claim. `not_created` records the causal
policy or earlier failure. `not_applicable` is restricted to a declared
nonpublishing sink.

Publication atomicity is per sink, not across the recording-session fan-out.
For one sink, all candidate members and the manifest are sealed before the
publication precondition is evaluated, and the root becomes visible as one
completed artifact or remains unpublished. An implementation that cannot
provide the declared no-replace or compare-and-replace semantics fails before
exposing a completed root. A sink published before an independent sink fails
remains published.

Publication success is irreversible evidence. Failure to remove a candidate
alias or other temporary state after successful publication yields a committed
outcome plus cleanup failure; it never relabels the root as unpublished or
invites publication retry. This preserves the existing native-FDR post-link
cleanup rule. Abort, close, and cleanup failures remain separate from the first
causal failure.

`RecoveryRequest` is an immutable value with exact properties
`recovery_attempt_id`, `recording_session_descriptor`, `sink_session_id`,
`root_artifact_id`, `destination`, `action`, optional `discard_authorization`,
`requested_at`, and `producer`. `action` is `resume`, `finalize_partial`,
`preserve`, or `discard`. The authorization is required only for `discard`,
must exactly equal the declaration's authorization, and is prohibited
otherwise.

Its three operation/artifact identities are `Uuid`; the descriptor is a
recording-session-descriptor `RecordRef`; destination exactly equals the sink
declaration; `requested_at` is canonical `ObservationTiming`.

`RecoveryResult` has `recovery_result_id`, `recording_session_id`,
`sink_session_id`, `recovery_attempt_id`, `action`, optional
`selected_checkpoint`, optional `prior_recording_result`, ordered
`input_artifact_states`, ordered `output_artifact_states`, ordered
`preserved_tail_artifacts`, `outcome`, optional `primary_failure`, ordered
`cleanup_failures`, `ended_at`, `producer`, and `content_hash`.

Result, recording-session, sink-session, and recovery-attempt identities are
`Uuid`; `ended_at` is canonical `ObservationTiming` not earlier than the
request in a comparable receipt domain.

`outcome` is `resumed`, `finalized_partial`, `preserved_partial`, `discarded`,
or `failed`. Recovery validates the contiguous self-hashed checkpoint chain and
selects its highest valid consistent cut. Every sealed member must match.
Every open member must be at least the recorded safe length and have the exact
safe-prefix hash. A shorter or mismatched member fails closed without mutation.
Bytes after a valid safe prefix and members not named by the checkpoint are
preserved under new tail-artifact UUIDs before a resumed member is truncated;
they are never silently discarded.

Every successful action outcome prohibits `primary_failure`; `failed` requires
one recovery-domain primary failure. Cleanup failures are permitted for any
outcome and never rewrite a successful primary action into `failed` after its
irreversible state change.

`selected_checkpoint` is required for `resume` and `finalize_partial`, optional
for `preserve`, and prohibited for `discard`. Outcomes correspond exactly to
actions: successful `resume`, `finalize_partial`, `preserve`, and `discard`
produce `resumed`, `finalized_partial`, `preserved_partial`, and `discarded`,
respectively; any unsuccessful action produces `failed`.

`resume` continues the same root and member UUIDs from the selected cut.
`finalize_partial` seals recoverable evidence with disposition
`preserved_partial`; a canonical archive uses the `.fdau.incomplete` suffix,
never `.fdau`, and another sink uses only an incomplete destination form fixed
by its profile. It never makes a completed-acquisition or lossless claim.
`preserve` performs no byte mutation. `discard` records the exact authorization
and deletion cleanup outcome. A crash may precede any recording result, so
`prior_recording_result` is optional. Existing checkpoints, results, and
artifact states remain immutable; recovery appends new states and never
rewrites historical terminal evidence.

## Artifact manifest and recording result

`ArtifactManifest` is the root record for one artifact graph. It has
`artifact_manifest_id`, `recording_session_descriptor`, `sink_session_id`,
`root_artifact_id`, `acquisition_session_descriptor`, `resolution`, ordered
`source_contexts`, ordered `continuity_reports`, ordered `artifacts`, ordered
`relationships`, `data_classification`, ordered `limitations`, `producer`, and
`content_hash`. One manifest describes exactly one sink artifact graph, not the
whole fan-out transaction.

Each `ArtifactEntry` has `artifact_id`, `role`, `media_type`, optional
`relative_path`, `content_state`, variant-selected byte
length/SHA-256/failure/retention fields, optional `schema_version`, optional
`record_ref`, `producer`, `created_at`, optional `finalized_at`, ordered
`scopes`, and ordered `definitions`.
`relative_path` is required for a graph member and prohibited only when the
root artifact is itself one byte-addressable external file. Artifact entries
are unique by ID and path. The manifest inventories every created or
policy-omitted member of this sink graph.

`created_at` and `finalized_at` are `UtcInstant` artifact metadata. They do not
establish runtime causal order; lifecycle events, checkpoints, and phase
attempts carry that evidence.

- `schema_version` is present exactly for an artifact serialized under a
  versioned schema and is prohibited otherwise. `record_ref` is present
  exactly when the complete artifact is one self-hashed contract record.
- Each `scopes` entry is a tagged value with kind `stream`, `epoch`,
  `source_generation`, `connection_generation`, or `delivery_generation` and
  the corresponding UUID or `UInt63` value. Scope entries are an `ArraySet` in
  kind-then-value order. `definitions` is an `ArraySet<DefinitionRef>` in
  canonical definition-reference order.
- `sealed` and `preserved_partial` require `finalized_at`, byte length, and
  SHA-256. `preserved_partial` additionally requires failure evidence and
  recovery eligibility. `omitted_by_policy` prohibits byte state and
  `finalized_at` and requires the exact retention-policy reference.

`data_classification` is `unspecified`, `public`, `internal`, `sensitive`, or
`restricted`. It is an operator data-handling classification only and never a
claim of statutory protection, privilege, or regulatory compliance.

Each relationship has `relationship_id: Uuid`, `kind`, `from`, and `to`.
Endpoints are `ArtifactLocator` values: a local locator contains
`scope: "local"` and this manifest's root or member artifact ID, while an
external locator contains `scope: "external"`, another manifest `RecordRef`,
and its root or member artifact ID. `kind` is `parent`, `projection_of`,
`derived_from`, `corroborates`, `replay_source`, `recovery_of`, or
`related_to`. `from` is the
subject and `to` is its object: a child points to its parent, a projection or
derivation to its source, a corroborating artifact to what it corroborates, a
replay artifact to its source, and a recovery-created artifact to its source.
`related_to` is symmetric and stores the lexically smaller canonical locator
first. Directed relationships cannot self-reference. `parent`,
`projection_of`, `derived_from`, `replay_source`, and `recovery_of` must be
acyclic within the supplied local closure.

An embedded manifest inventories every archive member except its own serialized
bytes. `root_artifact_id` may also identify a byte-addressable entry, but a
logical directory root has no invented directory-byte hash. The manifest does
not inventory the later sink or recording result. This avoids self-referential
file hashes and publication-status cycles. The manifest's `content_hash` uses
the approved root self-hash rule; its serialized byte length and SHA-256 are
reported later by the owning sink result.

The descriptor, resolution, source contexts, continuity-report references,
artifact scopes, and limitations carry the parent architecture's requested and
observed sampling, source, generation, gap, drop, and discontinuity inventory.
Termination, publication, and recovery status occur later and therefore live
in immutable `SinkResult`, `RecordingSessionResult`, and `RecoveryResult`
records. They are joined by exact record and artifact identities rather than
copied backward into the prepublication manifest.

`RecordingSessionResult` is generated after every sink reaches a terminal
state. It is returned to the caller and may be persisted as a separate related
contract artifact; it is never inserted retroactively into an immutable sink
graph. It has `recording_result_id`, `recording_session_id`, `descriptor`,
`outcome`, `termination_reason`, optional `primary_failure`, ordered
`cleanup_failures`, ordered `sink_results`, ordered `continuity_reports`,
`ended_at`, `producer`, and `content_hash`. It contains no singular manifest or
archive-publication field.

`recording_result_id` and `recording_session_id` are `Uuid`; `descriptor` is
the equal-session recording descriptor `RecordRef`; `ended_at` is canonical
`ObservationTiming` not earlier than every sink's terminal phase in a
comparable receipt domain.

Each `SinkResult` has `sink_session_id`, `criticality`, `outcome`, optional
`manifest`, optional `manifest_file`, `publication`, `delivery_summary`,
ordered `phase_attempts`, optional `primary_failure`, and ordered
`cleanup_failures`.

- `outcome` is `successful`, `partial`, or `failed`.
- `criticality` must exactly match the declaration. `primary_failure` is
  prohibited for success and required for failure; it is optional for partial
  only when declared loss rather than a runtime failure caused the partial
  result.
- `manifest` is present exactly when a manifest was completed.
  `manifest_file` then records the serialized manifest byte length and SHA-256
  and is otherwise prohibited.
- `publication` has disposition `published`, `preserved_partial`, `discarded`,
  `not_created`, `omitted_by_policy`, or `not_applicable`, the declared
  destination identity, and disposition-selected artifact states, failure,
  authorization, and cleanup evidence. `not_applicable` is valid only for a
  declared nonpublishing sink. Published-with-cleanup-failure remains
  `published`.
- `delivery_summary` records first and last delivery event references and
  delivered, dropped, detached, and failed counts. It summarizes append calls;
  it never embeds an unbounded list of per-append outcomes.
- `phase_attempts` contains at most one ordered summary for each attempted
  `open`, `checkpoint`, `commit`, `abort`, `recover`, and `close` phase.
  Unattempted phases are omitted, not reported as successful.
- A successful sink has published or explicitly nonpublishing committed output,
  no loss disposition, and no primary failure. A published graph with declared
  loss, or a preserved-partial graph, is partial. Failure, discard after work
  began, or declared output never created because of failure is failed.

- `RecordingSessionResult.outcome` is `successful`, `partial`, or `failed`.
- A successful recording result requires every sink result to be successful
  and contains no primary failure. An optional partial or failed sink produces
  a partial recording result. A required partial or failed sink produces a
  failed recording result even when other artifacts were published
  successfully.
- `termination_reason` is `consumer_complete`, `consumer_stop`,
  `required_sink_failed`, `explicit_abort`, `recovery_pending`, or
  `internal_failure`. An optional publication conflict is retained in its sink
  result without replacing the session's actual termination reason.

A `PhaseAttempt` has exact properties `phase`, `attempt_sequence: UInt63`,
`started_at: ObservationTiming`, `ended_at: ObservationTiming`, `result`, and
optional `failure: FailureEvidence`. Phase order is `open`, zero or more
checkpoint calls summarized as one aggregate checkpoint attempt, then exactly
one of commit or abort when either was attempted, optional recover, and close.
Attempt sequence is contiguous from zero for the sink session. `result` is
`succeeded`, `not_due`, `conflict`, or `failed`; `not_due` is valid only for
checkpoint, `conflict` only for commit, failure is required for conflict or
failed and prohibited otherwise. A checkpoint summary additionally has
`call_count: UInt63`, `checkpointed_count: UInt63`, and
`not_due_count: UInt63`, whose successful counts sum to call count when result
is not failed. Phase timing must be same-domain comparable and nondecreasing.

## Failure evidence and precedence

Runtime failure evidence is data, not a serialized Python exception name.
`FailureEvidence` has exact required properties `failure_id: Uuid`, `domain`,
`phase`, `code`, and `timing: ObservationTiming`; optional properties are
`record_ref: RecordRef`, `artifact_id: Uuid`, `path`, and
`diagnostic: NfcText(1024)`. `path` is an RFC 6901 pointer and is present only
when failure concerns a contract property. Record and artifact references are
present whenever the failed operation had already bound those identities and
are otherwise omitted. `phase` is one of `resolve`, `open`, `observe`,
`normalize`, `deliver`, `evaluate`, `append`, `checkpoint`, `commit`, `abort`,
`recover`, `close`, `replay`, `project`, `verify`, or `cleanup`; each domain
permits only phases meaningful to its operations.

`domain` is `acquisition`, `continuity`, `fanout`, `recording`, `publication`,
`recovery`, `replay`, `projection`, or `deployment`. Each domain owns a closed
version-1 code vocabulary:

| Domain | Closed `code` vocabulary |
| --- | --- |
| `acquisition` | `provider_unavailable`, `source_unavailable`, `binding_mismatch`, `generation_conflict`, `source_failed`, `session_state_invalid`, `required_evidence_unsatisfied`, `internal_failure` |
| `continuity` | `scope_invalid`, `clock_incomparable`, `cadence_shortfall`, `gap_exceeded`, `stale_evidence`, `invalid_evidence`, `drop_observed`, `sink_failure`, `internal_failure` |
| `fanout` | `endpoint_rejected`, `endpoint_failed`, `backpressure_overflow`, `endpoint_detached`, `delivery_sequence_conflict`, `internal_failure` |
| `recording` | `sink_open_failed`, `append_failed`, `checkpoint_failed`, `commit_failed`, `abort_failed`, `close_failed`, `required_sink_failed`, `recovery_pending`, `internal_failure` |
| `publication` | `destination_unsupported`, `publication_conflict`, `atomicity_unavailable`, `verification_failed`, `cleanup_failed`, `internal_failure` |
| `recovery` | `descriptor_mismatch`, `root_identity_mismatch`, `checkpoint_chain_invalid`, `member_missing`, `member_shorter_than_checkpoint`, `prefix_hash_mismatch`, `tail_preservation_failed`, `discard_unauthorized`, `cleanup_failed`, `internal_failure` |
| `replay` | `source_manifest_invalid`, `selection_invalid`, `ordering_unavailable`, `pacing_clock_incomparable`, `source_record_invalid`, `delivery_failed`, `internal_failure` |
| `projection` | `profile_mismatch`, `required_measurement_missing`, `required_field_unavailable`, `conversion_failed`, `out_of_range`, `timing_incomparable`, `native_write_failed`, `publication_failed`, `internal_failure` |
| `deployment` | `release_hash_mismatch`, `distribution_identity_mismatch`, `version_mismatch`, `source_revision_mismatch`, `runtime_dependency_present`, `file_missing`, `file_changed`, `file_added`, `import_origin_mismatch`, `conformance_manifest_mismatch`, `conformance_failed`, `unsupported_interpreter`, `internal_failure` |

Demand-resolution rejection reasons and continuity classifications are not
failure codes: they remain valid domain outcomes. Deployment finding codes are
the equal-named deployment failure codes except `internal_failure`; a receipt
uses findings for deterministic verification rejection and reserves
`FailureEvidence` for an attempted verification operation that could not
produce that deterministic comparison. Unknown domains, phases, or codes fail
closed.

The first causal failure in recorded event order is primary. Cleanup, abort,
close, recovery, and independent sink failures retain their own evidence and
never replace the primary failure. Diagnostics are at most 1024 NFC code
points and never include raw inline values, payload bytes, credentials, or host
objects. Adding an outcome or failure code that version-1 consumers cannot
interpret requires a new schema version.

## Faithful deterministic replay

Version 1 defines one replay mode: `faithful_canonical`.

`ReplaySessionDescriptor` has `replay_session_id`, `source_manifest`, ordered
`source_artifacts`, `selection`, `ordering`, `pacing`, `opened_at`, `producer`,
and `content_hash`.

`replay_session_id` is `Uuid`; `opened_at` is canonical
`ObservationTiming`.

- Stored observations, samples, frames, sequence numbers, epochs, timestamps,
  and hashes are emitted unchanged.
- `source_manifest` is an artifact-manifest `RecordRef` whose graph validates
  completely. `source_artifacts` is a nonempty `ArraySet<Uuid>` containing the
  exact retained artifacts selected from that manifest; every record and
  payload needed by the selection is included.
- `selection` has exactly nonempty ordered `ranges` and
  `include_record_kinds: ArraySet`. Each `ReplayRange` has
  `logical_stream_key: NfcText(512)`, `records: RecordRange`, and optional
  `epoch_ids: ArraySet<Uuid>`. Ranges are unique and sorted by stream key then
  first index, cannot overlap for one stream, and resolve within the manifest.
  Record kinds are drawn from `raw_observation`, `measurement_sample`,
  `measurement_frame`, `acquisition_lifecycle_event`, and
  `fanout_delivery_event`.
- `ordering` is `recorded_global_order` or `per_stream_order`.
  `recorded_global_order` requires the selected archive-order entries and emits
  their targets by contiguous global sequence. `per_stream_order` emits ranges
  in selection order and records within each range by archive record index.
  Missing or inconsistent order evidence fails with `ordering_unavailable`;
  path or manifest enumeration never substitutes for it.
- `pacing` is a tagged value. `unpaced` has no other property.
  `recorded_monotonic` has `reference: "first_emitted"`. `scaled` has
  `reference: "first_emitted"` and `multiplier: PositiveRational`.
  Recorded/scaled pacing requires same-domain monotonic
  evidence for consecutive emitted items; an incomparable boundary produces a
  replay failure rather than UTC or wall-clock approximation. Pacing affects
  delivery timing only.
- The replay session identity describes execution and never replaces source
  evidence identities.

`ReplayLifecycleEvent` has `replay_event_id`, `replay_session_id`,
`event_sequence`, `delivery_generation`, `kind`, variant-selected `detail`,
`timing`, `producer`, and `content_hash`. `kind` is `opened`, `paused`,
`resumed`, `seeked`, `looped`, `stopping`, or `terminal`. Backward seek and loop
increment delivery generation. They do not rewrite source epochs or records.

The two identities are `Uuid`; event sequence and delivery generation are
`UInt63`; `timing` is canonical `ObservationTiming`.

The exact replay detail variants are: `opened` carries `descriptor: RecordRef`;
`paused` and `resumed` carry `prior_state` and `current_state` with the exact
transition; `seeked` carries `prior_selection`, `current_selection`, and
`direction` (`forward` or `backward`); `looped` carries `completed_selection`
and `restart_selection`; `stopping` carries `reason` and optional
`primary_failure`; and `terminal` carries the final reason and optional primary
failure. Embedded selections use the descriptor selection shape. Reasons are
`selection_complete`, `consumer_stop`, `explicit_abort`, or
`internal_failure`; only internal failure requires failure evidence.

`ReplaySessionResult` has `replay_result_id`, `replay_session_id`,
`terminal_event`, `outcome`, `delivered_record_counts`,
`last_delivery_generation`, optional
`primary_failure`, ordered `cleanup_failures`, `ended_at`, `producer`, and
`content_hash`. `outcome` is `completed`, `stopped`, or `failed`.

The two identities are `Uuid`; `last_delivery_generation` is `UInt63`;
`ended_at` is canonical `ObservationTiming` not earlier than the terminal
event in a comparable receipt domain.

`delivered_record_counts` is `CountDistribution` over the five replay record
kinds. The members are exclusive and their sum is the number of emitted target
records. `completed` requires terminal reason `selection_complete` and no
primary failure; `stopped` requires `consumer_stop` or `explicit_abort` and no
primary failure; `failed` requires a replay-domain primary failure. The result
references the terminal replay event immediately before `outcome` using
`terminal_event: RecordRef`; its reason and failure must match.

Replay never appends emitted records to the source archive as new live facts by
default. A future native-FDR-to-canonical adapter is not faithful replay because
native FDR lacks canonical identity, quality, and lineage; it must generate new
canonical evidence with exact native-file provenance under separate authority.

## Native X-Plane FDR projection

`XPlaneFDRProjectionProfile` is an immutable definition with
`projection_profile_id`, `projection_profile_revision`, `authority`,
`provenance`, literal `target_version: 4`, `row_cadence`, ordered
`trajectory_mappings`, ordered `dref_mappings`, `timing_policy`,
`header_policy`, `formatting_policy`, `limitations`, and `content_hash`.

`row_cadence` is `PositiveRationalDuration`. Each `FieldMapping` has exact
properties `mapping_id: Identifier`, `output_field`, `measurement:
DefinitionRef`, `binding: DefinitionRef`, optional `transform: AlgorithmRef`,
`source_unit: UnitSpec`, `output_unit: UnitSpec`, `resampling`,
`missing_policy`, optional `placeholder: Binary64`, and `precision_policy`.
The binding resolves to the pinned measurement; source and output units resolve
through the measurement/binding/transform closure. A mapping therefore never
selects an arbitrary corroborating sample at projection time.

- `trajectory_mappings` contains exactly six mappings in this order:
  `longitude`, `latitude`, `altitude_msl_ft`, `heading_magnetic_deg`,
  `pitch_deg`, and `roll_deg`. No other trajectory field exists in version 1.
- A trajectory `output_field` is that literal field name. A DREF
  `output_field` is a tagged value with exact properties `kind: "dref"`,
  `dataref_path: NfcText(2048)`, `scale: Binary64`, and optional
  `comment: NfcText(1024)`. Paths are nonempty, contain no whitespace or
  double slash, are unique, and mappings preserve declared DREF order. Scale
  is finite and nonzero. The declaration is native output metadata, not a
  canonical binding identity.
- `resampling` is `exact`, `hold`, `nearest`, or `linear`; it must be allowed
  by the measurement definition and acquisition profile. `exact` requires a
  sample at the row instant. Other modes use only same-epoch, same-domain
  evidence and cannot cross a discontinuity. Tie-breaking for nearest chooses
  the earlier sample. Linear requires numeric scalar/vector equal-shape values
  and exact rational position before one final binary64 rounding.
- `missing_policy` is `fail`, `placeholder`, or `omit`. Trajectory mappings
  allow `fail` or `placeholder`; DREF mappings allow `fail` or `omit`.
  Placeholder is required exactly for `placeholder` and otherwise prohibited.
  Placeholder and omission are never inferred.
- `precision_policy` has exactly `lexical_mode: "shortest_round_trip"`,
  `inexact_conversion` (`reject` or `round`), and `range_overflow` (`reject` or
  `clamp`). Round and clamp are always loss. Native lexical emission uses the
  existing finite int/binary64 version-4 writer contract and LF endings.
- `timing_policy` has exactly `clock_basis: "frame_acquisition_clock"`,
  `utc_source: "frame_acquisition_utc"`, `alignment:
  "first_selected_frame"`, `gap_disposition` (`fail` or `omit_row`), and
  `midnight_disposition` (`fail` or `wrap_with_date_metadata`). Row instants
  advance from the first selected frame by exact row cadence. Every selected
  frame clock domain must be comparable within its epoch. UTC is mandatory for
  every emitted row; receiver UTC or extrapolated anchors cannot replace a
  missing frame acquisition UTC. A wrapped midnight is disclosed as native
  date-boundary loss.
- `header_policy` has exact properties `origin: "A"`, `date_metadata:
  "first_row_utc_date"`, ordered unique `comments: NfcText(1024)[]`, and
  ordered unique `metadata`. Each metadata item has the existing native
  four-character key and single-line value restrictions; `COMM`, `DREF`, and
  `DATE` are prohibited because comments, mappings, and date policy own them.
- `formatting_policy` has exact properties `encoding: "utf-8"`,
  `line_ending: "lf"`, `field_separator: "comma_space"`, and
  `writer_profile: "xplane_fdau.native_fdr_v4.v1"`. No locale, platform
  newline, or caller formatting callback can alter bytes.
- The existing native reader continues accepting versions 3 and 4. New
  canonical projection emits version 4 only.

`XPlaneFDRProjectionReport` has `projection_report_id`, `profile`,
`recording_session_id`, `input_manifest`, ordered `input_artifacts`,
`output_artifact`, `selected_range`, ordered `field_results`,
`row_count`, `outcome`, optional `primary_failure`, ordered
`cleanup_failures`, `producer`, and `content_hash`.

`projection_report_id` and `recording_session_id` are `Uuid`; `row_count` is
`UInt63`.

`profile` is the exact projection-profile `DefinitionRef`; `input_manifest` is
an artifact-manifest `RecordRef`; `input_artifacts` is a nonempty
`ArraySet<Uuid>` resolved in that manifest; and `output_artifact` is the
preallocated native-file artifact `Uuid`. The output sink's later manifest and
result bind that identity to final bytes without creating a report/manifest
self-reference. `selected_range` uses the replay-selection shape and must
resolve to retained frames and their complete sample/observation closure.

Each `FieldResult` has exact properties `mapping_id: Identifier`,
`emitted_count: UInt63`, `omitted_count: UInt63`,
`placeholder_count: UInt63`, `conversion_failed_count: UInt63`,
`out_of_range_count: UInt63`, `rounded_count: UInt63`,
`clamped_count: UInt63`, `interpolated_count: UInt63`,
`resampled_count: UInt63`, optional `affected_rows: RecordRange`, and ordered
unique `limitations`. Emitted plus omitted equals row count for a DREF mapping;
emitted equals row count and omitted is zero for a trajectory mapping.
Placeholder is included in emitted. The remaining loss counts may overlap and
do not sum to emitted count. `affected_rows` is present exactly when any loss
count is nonzero and spans the first through last row affected by any loss.
`outcome` is `completed`, `completed_with_loss`, or `failed`.

`completed` requires every loss count and limitations array to be empty and no
primary failure. `completed_with_loss` requires at least one disclosed loss or
limitation and no primary failure. `failed` requires a projection-domain
primary failure; any safely published partial native artifact remains explicit
artifact evidence and never becomes a completed projection. Cleanup failures
do not replace the primary result and a successfully published output remains
published.

The report does not duplicate source-sample lineage for every native cell.
Exact reproduction uses the immutable canonical input graph plus the pinned
deterministic profile. The native FDR artifact remains a lossy projection and
never becomes canonical evidence merely because projection succeeds.

## ARINC representation-adapter seam

This design reserves bidirectional package-owned representation adapters:

```text
edition-pinned ARINC representation
        -> decoder/profile
        -> canonical observation/sample with raw provenance

canonical measurement sample
        -> edition-pinned mapping/profile
        -> ARINC encoder and explicit quantization/loss evidence
```

ARINC 717 framing/recording, ARINC 647A/FRED configuration interchange, and
ARINC 429 word/label behavior require later `S` specifications based on exact
licensed editions. Raw ARINC bytes may be retained as content-addressed
payloads. No generic contract here contains an ARINC label, status-bit layout,
sync word, subframe position, or conformance claim.

## FDM/FOQA analysis seam

FDM/FOQA is a first-class local capability, not an external generic library.
Later `F1` contracts consume canonical samples, frames, archives, continuity,
quality, timing, lineage, and replay and produce versioned analysis evidence
and findings. D1.2 requires its generic fan-out and archive surfaces to retain
the evidence needed by F1, but does not choose live-versus-postflight analysis
ports, profile models, finding models, or review workflow ahead of `F1.1`.

Acquisition quality remains distinct from operational findings. q4xpcc
findings remain q4xpcc-owned; FDAU FDM/FOQA findings will be F1-owned.

## Deployment policy and portable receipt

`DeploymentPolicy` is an immutable definition that specifies how any consumer
must verify a future FDAU release. It contains `deployment_policy_id`,
`deployment_policy_revision`, `authority`, `provenance`,
`allowed_deployment_modes`, literal `distribution_name: "xplane-fdau"`,
literal `import_namespace: "xplane_fdau"`, `required_artifact_kind`,
`package_inventory_rule`, `build_identity_resource`, `runtime_dependency_rule`,
`import_origin_rule`, `conformance_rule`, `generated_cache_exclusions`,
`limitations`, and `content_hash`.

- Allowed modes are `installed_wheel` and `reproducibly_bundled`.
- `allowed_deployment_modes` is the nonempty `ArraySet` of
  `installed_wheel` and/or `reproducibly_bundled`.
- `required_artifact_kind` is literal `wheel`; an sdist is not deployment
  proof. `package_inventory_rule` is literal `complete_namespace_inventory`.
  The package inventory is every regular wheel member below
  `xplane_fdau/`, including schemas, conformance resources, formats, sinks, and
  data files.
- `build_identity_resource` is literal
  `xplane_fdau/build-identity.json`. That canonical JSON resource has exactly
  `distribution_name: "xplane-fdau"`, `distribution_version: VersionText`, and
  `repository_revision: VersionText`. It has no self-hash or release-artifact
  hash because embedding the enclosing wheel hash would be cyclic. Its bytes
  are covered by the wheel and package-file hashes.
- `runtime_dependency_rule` is literal `empty_requires_dist`; runtime
  dependencies must be empty in wheel metadata.
- `import_origin_rule` is literal `single_verified_namespace_root`; imports
  must resolve exclusively below the verified installed or bundled package
  root.
- `conformance_rule` has exact properties `protocol_version: 1`,
  `python_module: "xplane_fdau.conformance"`, `manifest_resource:
  "xplane_fdau/conformance/v1/manifest.json"`, and `required_exit_status: 0`.
  The Python runner accepts `--manifest PATH --output PATH`, writes the
  canonical conformance-result shape fixed by the canonical design, and uses
  exit status 0/1/2 with those existing meanings. Installed-wheel verification
  resolves the packaged manifest with `importlib.resources`; a caller cannot
  substitute a checkout mirror.
- `generated_cache_exclusions` is exactly the `ArraySet` containing
  `__pycache__` and `*.pyc`.
- Only `__pycache__` directories and `.pyc` files generated by the interpreter
  are excluded. No source, schema, fixture, resource, or native extension below
  the namespace may be added, removed, or changed.

`ConsumerDeploymentReceipt` is generated only against a concrete artifact. It
has `deployment_receipt_id`, `policy`, `consumer_id`, `consumer_build_id`,
`deployment_mode`, `distribution_name`, `distribution_version`,
`repository_revision`, `release_artifact`, ordered `expected_package_files`,
ordered `delivered_package_files`, `runtime_dependencies`, `import_origin`,
`python_version`, `conformance_manifest_sha256`,
`conformance_result_sha256`, ordered `findings`, `outcome`, `verified_at`,
`producer`, and `content_hash`.

`deployment_receipt_id` is `Uuid`; `verified_at` is canonical
`ObservationTiming`.

- `policy` is the exact deployment-policy `DefinitionRef`; `consumer_id` is an
  `Identifier`; `consumer_build_id` and `repository_revision` are
  `VersionText`; `deployment_mode` is allowed by the policy;
  `distribution_name` is literal `xplane-fdau`; and
  `distribution_version` is `VersionText` equal to the installed metadata.
- `release_artifact` has exact properties `filename: NfcText(255)`,
  `media_type: "application/zip"`, `byte_length: UInt63`, and `sha256:
  Sha256` for the exact wheel bytes.
- Expected and delivered package-file entries have exact properties
  `path`, `byte_length: UInt63`, and `sha256: Sha256`. `path` is a normalized
  relative POSIX path below `xplane_fdau/` with no empty, `.`, or `..` segment.
  Entries are unique and sorted by path.
- Expected inventory is derived from the verified wheel, never caller input.
- Delivered inventory is scanned from the exact import root.
- `runtime_dependencies` is an `ArraySet<NfcText(512)>` of normalized
  `Requires-Dist` values and must be empty for verification. `import_origin`
  is the normalized absolute package-root path as `NfcText(2048)` evidence;
  path spelling is not package identity. `python_version` is `VersionText` and
  must fall in the release metadata's supported range.
- `conformance_manifest_sha256`, `conformance_result_sha256`, and every package
  hash are `Sha256`. The result hash covers the canonical conformance-result
  bytes including final LF.
- `outcome` is `verified` or `rejected`.
- Findings use the closed codes `release_hash_mismatch`,
  `distribution_identity_mismatch`, `version_mismatch`,
  `source_revision_mismatch`, `runtime_dependency_present`, `file_missing`,
  `file_changed`, `file_added`, `import_origin_mismatch`,
  `conformance_manifest_mismatch`, `conformance_failed`, or
  `unsupported_interpreter`.
- A rejected receipt remains audit evidence but cannot establish a deployment
  pin.

Each `DeploymentFinding` has required `code` and optional `path`, `expected`,
and `actual`. `path` is the affected package-relative path and is required for
`file_missing`, `file_changed`, and `file_added`; it is prohibited for other
codes. `expected` and `actual` are tagged values with kind `text`, `sha256`, or
`file_state` and the equal-named `VersionText`, `Sha256`, or package-file entry
value. A missing side is omitted, never `null`. Findings are an `ArraySet`
ordered by code, then path, then canonical expected/actual bytes. `verified`
requires an empty findings array; `rejected` requires at least one finding.

The consumer embeds this portable FDAU-owned receipt in, or references it from,
its own build manifest. FDAU does not own the consumer's complete manifest,
packaging process, or deployment orchestration.

Closed-world proof proceeds in this order:

1. verify wheel byte length and SHA-256;
2. verify distribution name, exact version, source revision, and empty runtime
   dependencies;
3. derive the complete expected `xplane_fdau/**` inventory from the wheel;
4. scan the delivered namespace and reject missing, changed, or additional
   non-cache files;
5. verify import resolution below the one delivered root;
6. run the shared conformance entry point against the pinned corpus;
7. hash the canonical conformance result; and
8. emit a verified receipt only when every step passes.

Verification is fail-collecting after the wheel itself is readable: every
independent deterministic mismatch is retained in canonical finding order.
An unreadable wheel or an inability to execute verification yields deployment
`FailureEvidence` and no fabricated receipt. A conformance runner exit status
1 yields `conformance_failed` and a rejected receipt; status 2 is an attempted
verification failure and produces no receipt. The receipt's producer identity
names the verifier, not the consumer package.

The policy exists before a release. A concrete receipt, version, revision,
wheel hash, file hash, or conformance-result hash is never fabricated to make a
planning document appear complete.

## Public modules and dependency direction

Future implementation follows this dependency direction:

```text
contracts / measurements / bindings
              |
              v
         acquisition
          /       \
         v         v
    recording    replay
         |
         v
  formats.xplane_fdr projection

future standards and FDM/FOQA consume canonical contracts and archives
```

The target semantic modules are `xplane_fdau.acquisition.profiles`,
`xplane_fdau.acquisition.demand`, `xplane_fdau.acquisition.continuity`,
`xplane_fdau.acquisition.session`, `xplane_fdau.recording.fanout`,
`xplane_fdau.recording.archive`, `xplane_fdau.recording.manifest`,
`xplane_fdau.recording.recovery`, `xplane_fdau.replay`,
`xplane_fdau.formats.xplane_fdr.projection`, and
`xplane_fdau.contracts.deployment`. Exact public `__all__` values and Python
constructor signatures belong to each owning child specification and cannot
weaken the wire contracts fixed here.

Canonical acquisition and recording never depend on native FDR, ARINC, FDM,
FOQA, q4xpcc, or provider adapters. Projection and analysis depend inward on
canonical evidence.

## q4xpcc Phase 24A reconciliation

The four Slice 2 plans use the design as follows:

| Plan | Required use |
| --- | --- |
| Slice 2A capability ledger | Keep interface identity and tested capability authority in q4xpcc; reference exact FDAU measurement and binding definitions rather than copying units, cadence, quality, or transforms. |
| Slice 2B C172 tester contracts | Translate observation objectives into pinned profile items and required/optional consumer demands; include demand, profile, measurement, and binding hashes in resolved card-run identity. |
| Slice 2C capture/evidence engine | Use FDAU observation ingress, demand resolution, acquisition sessions, frames, fan-out, recording, continuity, archive, and terminal results; retain q4xpcc findings and application-session policy outside FDAU. |
| Slice 2D live acceptance | Correlate FDAU session, archive, projection, and deployment receipt identities into coverage; keep XPLM and Web API adapters consumer-owned and keep acquisition sufficiency separate from operational findings. |

Planning reconciliation after `D1.3` may name these future contracts and exact
verification steps. It may not import nonexistent runtime APIs, copy draft
schemas, invent fixtures, or claim delivery before the owning local children
are verified.

## Complete A1/R1/P1 child coverage

The contract design covers every later implementation child without treating
this document as that child's implementation plan:

| Child | Binding D1.2 input |
| --- | --- |
| `A1.1` | Acquisition-profile identity, cadence, continuity, phase, quality, resampling, and retention declarations |
| `A1.2` | Immutable consumer demand, replacement generation, required/optional items, and retention strength |
| `A1.3` | Atomic required-item resolution, optional-item rejection, source merge, delivery periods, and closed incompatibility outcomes |
| `A1.4` | Allow-listed transform registry, data-only parameters, deterministic execution order, and explicit loss/failure evidence |
| `A1.5` | Acquisition-session descriptor, stream and epoch identity, lifecycle events, and source-context boundary |
| `A1.6` | Profile cadence plus resolution-selected downsampling, interpolation, aggregation, and resampling policies; no additional family is required |
| `A1.7` | Continuity scope, requested-versus-observed metrics, classifications, and closed insufficiency reasons |
| `A1.8` | Synchronous fan-out ports, sink/subscriber isolation, backpressure, and delivery events |
| `A1.9` | Session orchestration inputs and immutable terminal result closure |
| `R1.1` | Recording-session descriptor, sink declarations, criticality, and artifact UUID/content identity separation |
| `R1.2` | Manifest-rooted logical archive, canonical JSON/JSONL, global-order entries, content-addressed payloads, and raw-retention definition |
| `R1.3` | Immutable segment closure, checkpoints, candidate directory, atomic/no-replace publication, and failure cleanup |
| `R1.4` | Artifact entries, roles, hashes, record references, graph relationships, and manifest self-hash boundary |
| `R1.5` | Recording terminal results, stable artifact identity through recovery, partial preservation, and primary/cleanup failure precedence |
| `R1.6` | Identity-preserving faithful canonical replay, selection, ordering, pacing, seek generations, events, and result |
| `R1.7` | Long-session and corruption verification against the fixed checkpoint, recovery, replay, and manifest contracts; no additional family is required |
| `P1.1` | Versioned projection profile and exact ordered field mappings |
| `P1.2` | Complete mandatory version-4 trajectory-spine mapping and explicit placeholder policy |
| `P1.3` | Ordered version-4 DREF mappings and explicit omission policy |
| `P1.4` | Pinned projection cadence, timing, interpolation, and resampling behavior |
| `P1.5` | Per-field omission, placeholder, conversion, range, rounding, clamping, interpolation, and resampling loss report |
| `P1.6` | End-to-end canonical-input, pinned-profile, native-artifact, report, and deterministic reproduction closure; no additional family is required |

## Validation and runtime outcome separation

Malformed or semantically invalid contract documents fail before session use
through the approved contract-error precedence. Legitimate runtime inability
is represented by a valid outcome record with a closed code. A failed source,
sink, projection, recovery, or deployment is not converted into malformed JSON
to signal failure.

Within each result record, validation follows property order, then array index.
Cross-record closure follows argument order and canonical record order. Runtime
events use their recorded sequence for causal dominance. Unknown future codes,
families, or schema versions fail closed.

## Verification requirements for future children

Every owning child must eventually deliver:

- immutable models and exact versioned loaders/dumpers;
- byte-identical packaged and documentation schemas;
- accepted, rejected, and canonical corpus cases covering every tagged variant
  and closed outcome;
- deterministic hashes and Python/native conformance;
- cross-contract reference, lifecycle, ordering, and failure-precedence tests;
- source and installed-wheel verification on Python 3.12, 3.13, and 3.14;
- standard-library-only and provider-import boundary checks; and
- independent review with no unresolved load-bearing finding.

Tests use Python's `unittest` framework. No child may weaken the canonical JSON,
identity, lineage, timing, quality, release, or publication rules.

## Acceptance criteria

### D1.2 — Acquisition, recording, projection, and pinning contract design

D1.2 is complete only when:

1. this one approved design fixes the A1/R1/P1 contract shapes and policies
   needed by all four q4xpcc Phase 24A Slice 2 plans, including acquisition,
   continuity, fan-out, recording, recovery, replay, native-FDR projection,
   deployment, and conformance planning surfaces;
2. every family has an exact identity/version boundary, fields, invariants,
   references, runtime outcomes, error boundary, delivery ownership boundary,
   and future schema/conformance path, with closed failure codes and
   deterministic validation/causal precedence;
3. installed-wheel and reproducibly bundled deployment, revision pinning,
   release-artifact and delivered-file hashes, conformance, and closed-world
   no-divergent-subset proof are explicit without requiring or fabricating a
   current release; and
4. independent review reports no unresolved load-bearing ambiguity; native
   FDR, ARINC, FDM/FOQA, q4xpcc, and external-client boundaries remain
   consistent with the approved scope amendment; the approved contract-only
   design is recorded as binding input for later A1/R1/P1 specifications; and
   every implementation, schema, fixture, artifact, adoption, release, push,
   tag, and publication gate remains unsatisfied without advancing any A1,
   R1, P1, S, or F1 child.
