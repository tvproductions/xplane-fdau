# xplane-fdau Acquisition, Recording, Projection, and Pinning Contract Design

- **Governance:** active
- **Status:** approved
- **Date:** 2026-08-23
- **Decision owner:** Jeff / tvproductions
- **Roadmap epic:** `D1`
- **Roadmap children:** `D1.2`
- **Approval:** 2026-08-23 — Jeff / tvproductions

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
session-causal sequence for failure precedence. Runtime inability is
represented only by a valid outcome or `FailureEvidence`; malformed contract
data never becomes a runtime outcome.

### New family inventory and future resources

Each row fixes the future family URI and schema resource. The packaged schema
path will be `xplane_fdau/schemas/<stem>-v1.schema.json`; the byte-identical
documentation copy will be `docs/schemas/<stem>-v1.schema.json`.

| Family | Stem and family-URI suffix | Kind and identity property | Owning future child |
| --- | --- | --- | --- |
| Acquisition profile | `acquisition-profile` | definition; `profile_id` | `A1.1` |
| Consumer demand | `consumer-demand` | record; `demand_id` | `A1.2` |
| Demand resolution | `demand-resolution` | record; `resolution_id` | `A1.3` |
| Source-retention capability | `source-retention-capability` | definition; `capability_id` | `A1.3` |
| Transform registry | `transform-registry` | definition; `registry_id` | `A1.4` |
| Acquisition-session descriptor | `acquisition-session-descriptor` | record; `acquisition_session_id` | `A1.5` |
| Acquisition-session configuration | `acquisition-session-configuration` | record; `configuration_id` | `A1.5` |
| Acquisition lifecycle event | `acquisition-lifecycle-event` | record; `event_id` | `A1.5` |
| Provider-audit evidence | `provider-audit-evidence` | record; `provider_audit_evidence_id` | `A1.5` |
| Acquisition-session result | `acquisition-session-result` | record; `result_id` | `A1.9` |
| Continuity report | `continuity-report` | record; `continuity_report_id` | `A1.7` |
| Frame-subscriber declaration | `frame-subscriber-declaration` | record; `subscriber_declaration_id` | `A1.8` |
| Fan-out delivery event | `fanout-delivery-event` | record; `delivery_event_id` | `A1.8` |
| Failure closure | `failure-closure` | record; `failure_closure_id` | `A1.9` |
| Recording-session descriptor | `recording-session-descriptor` | record; `recording_session_id` | `R1.1` |
| Raw-retention policy | `raw-retention-policy` | definition; `policy_id` | `R1.2` |
| Archive order entry | `archive-order-entry` | record; `order_entry_id` | `R1.2` |
| Archive checkpoint | `archive-checkpoint` | record; `checkpoint_id` | `R1.3` |
| Artifact content manifest | `artifact-content-manifest` | record; `content_manifest_id` | `R1.4` |
| Artifact manifest | `artifact-manifest` | record; `artifact_manifest_id` | `R1.4` |
| Recording-session result | `recording-session-result` | record; `recording_result_id` | `R1.5` |
| Artifact-state ledger | `artifact-state-ledger` | record; `artifact_state_ledger_id` | `R1.5` |
| Recovery request | `recovery-request` | record; `recovery_request_id` | `R1.5` |
| Recovery result | `recovery-result` | record; `recovery_result_id` | `R1.5` |
| Replay-session descriptor | `replay-session-descriptor` | record; `replay_session_id` | `R1.6` |
| Replay lifecycle event | `replay-lifecycle-event` | record; `replay_event_id` | `R1.6` |
| Replay-session result | `replay-session-result` | record; `replay_result_id` | `R1.6` |
| Native-FDR projection profile | `xplane-fdr-projection-profile` | definition; `projection_profile_id` | `P1.1` |
| Native-FDR projection report | `xplane-fdr-projection-report` | record; `projection_report_id` | `P1.5` |
| Expected deployment pin | `expected-deployment-pin` | definition; `deployment_pin_id` | `A1.9` |
| Deployment policy | `deployment-policy` | definition; `deployment_policy_id` | `A1.9` |
| Consumer deployment receipt | `consumer-deployment-receipt` | record; `deployment_receipt_id` | `A1.9` |

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

The three deployment families are FDAU-owned contracts assigned explicitly to
`A1.9`, whose authoritative roadmap outcome is acquisition-session
orchestration and installed closure and whose dependency chain is downstream
of `C4.4`. This assignment requires the future A1.9 specification and plan to
deliver their immutable models, schemas, conformance corpus, public API, and
installed verification alongside session closure; it does not claim that work
now or mark A1.9 complete. The reviewed `C4.4` minimum threshold for `I1.1`
remains unchanged: D1.2 neither narrows nor expands the roadmap's adoption
boundary. Every family named here becomes adoptable only after its owning
child has delivered its model, schema, corpus, public API, and installed
verification. A1.9 must deliver the three deployment families before their
adoption and before `I1.2` can authorize live XPLM acquisition adoption. No
roadmap or backlog threshold change, silent expansion of `C4.4`, or release
authorization follows from this design assignment.

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
| `transform_registry` | `DefinitionRef` | exact transform-registry revision/hash used by every item algorithm |
| `items` | nonempty array of `AcquisitionProfileItem` | unique `item_id`; declared order is semantic |
| `limitations` | array of `NfcText(1024)` | at most 256; empty permitted |
| `content_hash` | `Sha256` | computed definition hash |

`AcquisitionProfileItem` has exact properties `item_id`, `measurement`,
`binding_candidates`, `binding_selection`, optional
`minimum_successful_bindings`, `cadence`, `continuity`, `acquisition_phase`,
`burst_policy`, ordered `transition_coverage`, `allowed_resampling`,
`resampling_authorizations`, `allowed_interpolation`, `required_validity`,
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
  `maximum_gap_ns: UInt63`, and `interval_distribution`. The latter has exact
  properties literal `kind: "slot_tolerance"`, `early_tolerance_ns: UInt63`,
  and `late_tolerance_ns: UInt63`. Version 1 exhausts interval-distribution
  tolerance through exact rational cadence slots plus those early/late bounds;
  it defines no implicit histogram, percentile, standard-deviation, or host-
  clock tolerance. Gap and staleness are independent constraints; neither
  implies an ordering between their values.
- `acquisition_phase` uses the canonical binding acquisition-phase vocabulary.
- `burst_policy` has exact properties `window: PositiveRationalDuration`,
  `maximum_observations: UInt63`, and literal
  `boundary: "closed_open"`; maximum observations is at least one. For every
  selected binding, it authorizes at most that many accepted observations in
  any same-epoch acquisition-time interval `[t, t + window)`. A cap of one is
  the exact no-burst policy; a larger cap is the complete version-1 burst
  authorization.
- `transition_coverage` is an `ArraySet<TransitionCoverageRequirement>` ordered
  by event kind. Each requirement has exact `event_kind`,
  `pre_window: PositiveRationalDuration`,
  `post_window: PositiveRationalDuration`,
  `minimum_pre_observations: UInt63`, and `minimum_post_observations: UInt63`;
  both minimum counts are positive. Event kind is `demand_replaced`,
  `epoch_started`, `source_restored`, `source_context_changed`, `pause_changed`,
  `replay_state_changed`, `time_speed_changed`, or `clock_discontinuity`.
  The named acquisition lifecycle event is the transition boundary; pre uses
  `[boundary - pre_window, boundary)` and post uses
  `[boundary, boundary + post_window)` in the event's comparable receipt
  domain. Acquisition-phase changes are represented by `demand_replaced` and
  its replacement configuration. Empty coverage means no transition minimum,
  never an inferred default.
- `allowed_resampling` is a nonempty `ArraySet` drawn from `none`, `hold`, `nearest`,
  `linear`, and `aggregate`. `none` is mutually exclusive with every other
  member.
- `resampling_authorizations` is empty exactly when `allowed_resampling` is
  `none`. Otherwise it contains exactly one `ResamplingAuthorization` for each
  allowed mode, in mode order `hold`, `nearest`, `linear`, `aggregate`. Each
  authorization has exact properties `mode`, `algorithm: AlgorithmRef`, and
  variant-selected `window`. The algorithm resolves in the profile's exact
  `transform_registry` and has kind `resampling` for hold/nearest/linear or
  `aggregation` for aggregate. Window kind `lookback` is used only by hold and contains
  `maximum_age_ns: UInt63`; `centered` is used only by nearest and contains
  `before_ns: UInt63`, `after_ns: UInt63`, and literal `tie_break: "earlier"`;
  `bracketing` is used only by linear and contains `maximum_span_ns: UInt63`;
  and `trailing` is used only by aggregate and contains
  `duration: PositiveRationalDuration` and literal
  `boundary: "open_closed"`. Zero bounds are permitted and retain their exact
  meanings. The `AlgorithmRef.parameters` value is the complete executable
  parameter set; no later delivery decision can substitute an algorithm,
  parameter, window, or tie break.
- `allowed_interpolation` is exactly `prohibited`, `hold`, or `linear` and
  cannot broaden the measurement definition: `prohibited` is always valid;
  `hold` requires measurement interpolation policy `hold`; and `linear`
  requires measurement interpolation policy `linear`. A hold resampling
  authorization is present exactly when interpolation is `hold`, and a linear
  authorization is present exactly when interpolation is `linear`; neither
  authorization is permitted when interpolation is `prohibited`. Nearest and
  aggregate do not assert interpolation authority.
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

Changing registry, cadence, continuity, burst, transition coverage,
resampling, interpolation, quality, phase, or binding meaning requires a new
profile revision and hash.

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

Transform loss evidence maps to canonical quality without an open choice:
`exact` contributes no quality flag, `rounded` contributes `rounded`,
`clamped` contributes `saturated`, `precision_lost` contributes
`precision_lost`, `out_of_range` contributes `out_of_declared_range`, and
`conversion_failed` contributes `conversion_failed` plus absent normalization
reason `normalization_failed`. Every applicable non-exact disposition is
retained; mappings do not select only one. Profile/resolution mode `none` and
projection mode `exact` both mean that no resampling algorithm is applied,
but retain their family-specific wire spellings.

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
| `kind` | `activate` or `withdraw` | variant discriminant |
| variant-selected body | exact fields below | no cross-variant properties |
| `requested_at` | `UtcInstant` | evidence timestamp |
| `producer` | `ProducerIdentity` | required |
| `content_hash` | `Sha256` | computed |

The `activate` variant contains `profile: DefinitionRef` and nonempty `items`
in profile order with unique profile-item references. The `withdraw` variant
contains `withdraws: RecordRef` and `reason`, prohibits `profile` and `items`,
and is prohibited at generation zero. `withdraws` equals `replaces`, which is
the immediately prior active `activate` demand for this consumer instance;
`reason` is `consumer_complete`,
`segment_closed`, or `explicit_withdrawal`. A later activate generation may
reactivate the consumer after withdrawal.

Each `DemandItem` has `profile_item_id`, `requirement`, and `retention`.
`requirement` is `required` or `optional`. `retention` is an exact
`RetentionRequirement` with these orthogonal properties:

- `canonical_records` is `samples`, `frames`, or `samples_and_frames`;
- `accepted_raw_observations` is `not_requested`, `when_supplied`, or
  `required`;
- `raw_payloads` is `not_requested`, `when_supplied`, or `required`; and
- `provider_audit` is `not_requested`, `when_supplied`, or `required`.

No total ordering exists among those axes. A resolution can satisfy
`raw_payloads: required` only with selected payload-represented sources whose
pinned retention capabilities support payload retention, and it can satisfy
`provider_audit: required` only when every selected source pins a capability
whose provider-audit variant is `available`. Otherwise the item receives
`retention_conflict`; those capabilities are never inferred from a binding.

`SourceRetentionCapability` is an immutable definition with exact properties
`contract_family`, `schema_version`, `capability_id`, `capability_revision`,
`authority`, nonempty `provenance`, `binding: DefinitionRef`, `provider:
ProviderIdentity`, `adapter: AdapterIdentity`, `resource_kind: Identifier`,
`resource_id: NfcText(2048)`, optional `resource_selection`,
`raw_payload_retention`, `provider_audit`, `limitations`, and `content_hash`.
The binding, provider, adapter, resource, and selection must exactly equal the
resolved canonical source binding; this definition does not add a property to
source-binding schema version 1. `raw_payload_retention` is `unsupported` or
`when_supplied`. `provider_audit` is either exact kind `unavailable` with no
other property or kind `available` with `artifact_role: Identifier`,
`media_type: NfcText(127)`, literal `evidence_scope: "configuration"`, and
`minimum_evidence_count: UInt63` greater than zero. The media type follows the
canonical media-type grammar. A capability revision changes whenever any
support, evidence, or source-identity claim changes.

`ProviderAuditEvidence` is the transport-free FDAU envelope for opaque audit
bytes supplied by a provider adapter. Its exact properties are
`provider_audit_evidence_id: Uuid`, `acquisition_session_id: Uuid`,
`configuration: RecordRef`, `source_acquisition_id: Uuid`,
`capability: DefinitionRef`, `provider: ProviderIdentity`,
`adapter: AdapterIdentity`, `resource_kind: Identifier`,
`resource_id: NfcText(2048)`, optional `resource_selection`, literal
`scope: "configuration"`, `payload: PayloadReference`,
`supplied_at: ObservationTiming`, `producer`, and `content_hash`.

- Configuration is an acquisition-session-configuration for the named
  session, and the source acquisition is activated by that configuration's
  resolution. Capability resolves to its exact pinned source-retention
  capability and its provider-audit variant must be `available`. Provider,
  adapter, resource, optional selection, artifact role, and media type equal
  that capability and source closure.
- `payload.storage_role` equals the capability's artifact role;
  `payload.media_type` equals its media type; and ingress requires
  `retention_status: "unverified"`. The payload hash and length identify the
  exact opaque bytes without interpreting provider-specific content.
- `supplied_at` is canonical `ObservationTiming` in the configuration receipt
  domain. Evidence received after that configuration is superseded or after
  terminal is rejected without relabeling it to another scope.

Updating any item or withdrawing/reactivating creates a new demand record and
generation. Active and withdrawn demand records are never mutated. A consumer
cannot reuse or skip a generation, replace a non-immediate predecessor, or
replace another consumer's demand. Receipt of the identical demand
`RecordRef` is idempotent and returns its existing receipt and resolution
without allocating a receipt sequence or resolution generation. Reuse of the
same consumer generation with a different hash produces acquisition
`FailureEvidence` code `generation_conflict` before active-set mutation and
creates neither a receipt nor a resolution.

`DemandResolution` is a generated record with `resolution_id`,
`resolver_instance_id`, `generation`, optional `replaces`,
`receipt_clock_domain`, `trigger_receipt`, ordered `demands`, ordered
`item_outcomes`, ordered `proposed_source_acquisitions`, ordered
`activated_source_acquisition_ids`, `outcome`, `producer`, and `content_hash`.

- `resolution_id` and `resolver_instance_id` are `Uuid`; `generation` is
  `UInt63`; `receipt_clock_domain` is one canonical `host_monotonic`
  `ClockDomain` whose producer instance equals the resolver instance.
- Resolution generation is contiguous from zero within one resolver instance.
  `replaces` is prohibited at generation zero and otherwise references the
  exact generation-minus-one resolution.
- `trigger_receipt` is the newly allocated `DemandReceipt` whose activate or
  withdraw operation caused this generation. `demands` contains the candidate
  active activate `DemandReceipt` values after applying that operation, in strictly
  increasing `receipt_sequence` order. Each receipt has the exact demand
  `RecordRef`, `receipt_sequence`,
  `receipt_clock`, and optional `receipt_utc`. Receipt sequence, not a
  consumer-supplied timestamp, determines replacement and conflict order.
  Receipt sequence is globally contiguous from zero for the resolver instance;
  the active subset may contain gaps after replacement or withdrawal. A
  withdrawal trigger is not active and therefore appears only as
  `trigger_receipt`; its replaced activate receipt is absent from `demands`.
  `receipt_clock` uses
  one declared monotonic resolver clock domain; `receipt_utc` is correlation
  evidence only. Every receipt reading identifies the resolution's
  `receipt_clock_domain`.
- Every item of every active demand appears exactly once in `item_outcomes`.
  A withdrawal that leaves no active demand may therefore produce empty
  `demands`, `item_outcomes`, and proposed/activated acquisition arrays; those
  arrays are the only permitted empty-resolution case.
- An item outcome contains its demand reference, `profile_item_id`,
  `result`, optional `reason`, and optional ordered
  `selected_source_acquisition_ids`.
- `result` is `accepted` or `rejected`.
- `reason` is required only for rejection and is one of
  `unknown_measurement`, `unknown_binding`, `binding_mismatch`,
  `provider_unavailable`, `source_unavailable`, `phase_conflict`,
  `cadence_conflict`, `resampling_conflict`,
  `validity_conflict`, `quality_conflict`, `retention_conflict`,
  `insufficient_corroboration`, or `capacity_exceeded`.
- `selected_source_acquisition_ids` is nonempty only for acceptance, contains
  every selected binding source, and satisfies the profile item's binding
  selection and minimum-success rules. It is absent for rejection.
- A proposed `SourceAcquisition` fixes one `source_acquisition_id: Uuid`, exact
  binding reference, exact `retention_capability: DefinitionRef`,
  `read_period: PositiveRationalDuration`, acquisition phase, accepted demand
  items, and per-consumer delivery period/resampling decision. The capability
  resolves to the source-retention-capability family and cross-validates the
  binding/provider/adapter/resource closure before retention is evaluated.
  Accepted items are unique pairs of demand `RecordRef` and profile item ID in
  demand-receipt then profile order. Each `DeliveryDecision` has exact
  properties `demand: RecordRef`, `profile_item_id: Identifier`,
  `endpoint_id: Uuid`, `delivery_period: PositiveRationalDuration`, and
  `resampling`. `endpoint_id` equals the demand's consumer-instance ID.
  `resampling` is a tagged `DeliveryResamplingDecision`: kind `none` has no
  other property; kinds `hold`, `nearest`, `linear`, and `aggregate` contain
  the exact `algorithm: AlgorithmRef` and `window` copied from the equal-mode
  profile authorization. A non-none decision is invalid unless algorithm
  identity, revision, definition hash, parameters, and window all equal that
  authorization and the algorithm resolves in the demand profile's pinned
  registry. A cadence requiring a mode absent from the profile produces
  `resampling_conflict`; impossible interpolation combinations are malformed
  profiles and never runtime resolution outcomes. Runtime delivery influenced
  by such a decision creates a
  canonical sample whose algorithm derivation uses that same `AlgorithmRef`
  and whose ordered parent sample references follow the window rule; `none`
  retains direct lineage and has no resampling parent algorithm. Delivery
  decisions use accepted-item order.
- Source acquisition uses the fastest authorized accepted demand. Slower
  delivery is permitted only by a demand's profile.
- `outcome` is `accepted` only when every required item is accepted. Optional
  rejection is retained but does not block activation. Otherwise outcome is
  `rejected`, and no source acquisition may begin from that resolution.
- `proposed_source_acquisitions` retains the complete closed acquisition
  definitions needed by every accepted item outcome, even when atomic required-
  item rejection prevents activation. Every selected source ID resolves
  exactly once in this array. For accepted resolution outcome,
  `activated_source_acquisition_ids` contains every proposal referenced by an
  accepted item, in proposal order. For rejected outcome it is empty. Thus an
  accepted item outcome never dangles, and proposal evidence is never
  mislabeled as an activated read.
- Receipt and demand generations commit independently of acquisition
  feasibility, so a rejected resolution still fixes the next active-demand
  set and remains the predecessor of the next resolution. It cannot become a
  session configuration. A running session presented with that rejected
  generation follows its ordinary `stopping` and `terminal` transitions with
  `required_evidence_unsatisfied`; an accepted later resolution starts a new
  acquisition session rather than reviving the terminal one. Thus stale prior
  acquisition never continues on behalf of a replaced or withdrawn demand.
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
proposed definitions remain immutable decision evidence but
`activated_source_acquisition_ids` is empty; no partially computed acquisition
is activated.

## Acquisition sessions, lifecycle, and terminal results

`AcquisitionSessionDescriptor` freezes session identity and its first
configuration. Its exact properties are `contract_family`, `schema_version`,
`acquisition_session_id`, `initial_configuration`, `opened_at`,
`receipt_clock_domain`, `producer`, and `content_hash`.

- `initial_configuration` references an equal-session
  `AcquisitionSessionConfiguration` at generation zero.
- `opened_at` is canonical `ObservationTiming`; `receipt_clock_domain` equals
  its receipt clock.

Descriptor, initial configuration, resolution, declaration, and structural
reference validation all complete before `opened` is committed. Provider/source
activation and the first epoch occur afterward and can fail. Such a failure is
therefore lifecycle evidence, not an open rejection, and follows the
initializing terminal path below.

`AcquisitionSessionConfiguration` is a generated immutable record with exact
properties `configuration_id`, `acquisition_session_id`,
`configuration_generation`, optional `replaces`, `resolution`,
`effective_epoch_id`, ordered `streams`, ordered `source_contexts`,
`configured_at`, `producer`, and `content_hash`. Generation is contiguous from
zero for the acquisition session. `replaces` is prohibited at zero and
otherwise references the equal-session generation-minus-one configuration.
`resolution` references an accepted `DemandResolution`, including an accepted
empty resolution after final withdrawal. `effective_epoch_id` is `Uuid` and
changes at every configuration generation. `configured_at` is canonical
`ObservationTiming` in the descriptor receipt domain.

- Each `StreamDeclaration` contains `stream_id: Uuid`,
  `source_acquisition_id: Uuid`, `binding: DefinitionRef`,
  `clock_domain_id: Uuid`, `initial_sequence: UInt63`, and
  `initial_generation: UInt63`. It resolves exactly one activated source
  acquisition and its binding. Stream IDs and source-acquisition IDs are
  unique in configuration order; binding references need not be unique because
  phase-distinct source acquisitions may use the same exact binding.
- Exactly one initial `source_contexts` entry exists for each source
  acquisition, in configuration stream order. Each `SourceContextSnapshot`
  has exact properties `source_acquisition_id`,
  `provider`, `adapter`, `source_generation`, `connection_generation`,
  `sources`, and `limitations`. Provider and adapter use `ProviderIdentity`
  and `AdapterIdentity`; both generations are `UInt63`; `sources` is an
  ordered nonempty array of `ProvenanceSource`; and `limitations` is a bounded
  NFC-text array. It contains no connection object, host handle, callback,
  credential, SDK value, or untyped simulator/plugin/replay label. A later
  source-context lifecycle event supplies the next immutable snapshot without
  mutating the configuration.
- Every effective resolution change, including withdrawal, replacement,
  overload relaxation, suspension, or reactivation, creates the next
  configuration before it affects delivery. Streams removed by a configuration
  receive no later observation or delivery event; new streams begin at their
  declared sequence/generation; retained stream IDs may continue only when
  binding, phase, source acquisition, clock domain, and source context are
  byte-identical. The archive retains every effective resolution and
  configuration in causal order. A session owns identities and evidence, not
  simulator lifecycle.
- An accepted withdrawal that removes the final demand produces a zero-stream
  configuration. After its reconfiguration epoch, `consumer_complete` causes
  the ordinary immediate `stopping`/`terminal` close with that reason;
  `segment_closed` or `explicit_withdrawal` leaves the session running idle so
  a later activate generation can install another configuration. A withdrawal
  that leaves other demands active follows the ordinary configuration path.

`AcquisitionLifecycleEvent` has `event_id`, `acquisition_session_id`,
`event_sequence`, `epoch_id`, `timing`, `kind`, variant-selected `detail`,
`producer`, and `content_hash`. Event sequence is contiguous from zero within
the acquisition session.

The closed version-1 `kind` vocabulary is `opened`, `demand_replaced`,
`overload_changed`, `epoch_started`, `source_degraded`, `source_restored`,
`source_context_changed`, `pause_changed`, `replay_state_changed`, `time_speed_changed`,
`clock_discontinuity`, `stopping`, and `terminal`.

`timing` is canonical `ObservationTiming`; its required receipt clock, reading,
and UTC instant record when the core accepted the event. Optional source timing
is present only when the source supplied it. The exact `detail` variants are:

| `kind` | Required detail properties in semantic order | Optional detail properties | Invariants |
| --- | --- | --- | --- |
| `opened` | `descriptor: RecordRef` | — | descriptor names this acquisition-session descriptor; top-level epoch equals its initial configuration's effective epoch |
| `demand_replaced` | `trigger_demand: RecordRef`, `prior_configuration: RecordRef`, `replacement_configuration: RecordRef` | — | trigger is activate or withdraw; configuration generation is prior plus one and its resolution is the resulting resolver generation |
| `overload_changed` | nonempty ordered `items` | — | each item is `demand: RecordRef`, `profile_item_id: Identifier`, prior/current `activation`, and prior/current `delivery_period`; activation is `active`, `relaxed`, or `suspended`, and periods are `PositiveRationalDuration` when the corresponding activation is active or relaxed and otherwise omitted |
| `epoch_started` | `epoch_id: Uuid`, `cause` | `prior_epoch_id: Uuid` | cause is `session_open`, `demand_reconfiguration`, `source_restart`, `provider_replacement`, `connection_replacement`, `aircraft_reload`, `plugin_reload`, `replay_seek`, `clock_regression`, or `explicit_boundary`; prior epoch is prohibited for session open and required otherwise |
| `source_degraded` | `source_acquisition_id: Uuid`, `failure: FailureEvidence` | — | source is declared by the active configuration and was not already degraded |
| `source_restored` | `source_acquisition_id: Uuid`, `degraded_event: RecordRef` | — | reference names the unmatched degradation event for the source |
| `source_context_changed` | `source_acquisition_id: Uuid`, `cause`, `prior: SourceContextSnapshot`, `current: SourceContextSnapshot` | — | source IDs equal; prior equals the active snapshot; cause and generation rules below select a different current snapshot |
| `pause_changed` | `prior: Boolean`, `current: Boolean` | — | values differ |
| `replay_state_changed` | prior and current canonical replay-state values | — | values differ |
| `time_speed_changed` | `prior: Binary64`, `current: Binary64` | — | bit patterns differ after canonical negative-zero normalization |
| `clock_discontinuity` | `cause`, `prior_clock_domain_id: Uuid`, `current_clock_domain_id: Uuid`, `prior_reading: ClockReading`, `current_reading: ClockReading` | — | cause is `regression`, `jump`, or `domain_replaced`; reading IDs match their respective domain IDs; regression/jump requires equal domains and domain replacement requires unequal domains |
| `stopping` | `requested_termination_reason` | `initiating_failure: FailureEvidence` | reason uses the acquisition-result vocabulary; `required_sink_failed` is permitted only after a required prior-configuration close fails while reconfiguring, and failure is present exactly for a requested failure reason |
| `terminal` | `stopping_event: RecordRef`, `termination_reason`, ordered `continuity_reports`, ordered `recording_results`, ordered `recovery_results`, ordered `projection_reports`, `failure_closure: RecordRef` | `primary_failure: FailureEvidence` | emitted only after required endpoint close, continuity evaluation, recording/recovery/projection outcomes, and the final acquisition-scope failure closure are fixed; references close those preterminal results |

Overload items preserve profile order within demand receipt order. State-change
variants never infer a prior value or relabel receipt evidence as source
evidence. A degradation/restoration pair does not create a new epoch by
itself; a separately recorded `epoch_started` event does so when the selected
session policy requires it.

A `source_context_changed` cause is `source_restart`,
`provider_replacement`, or `connection_replacement`. Source restart preserves
provider/adapter identity and increments both source and connection generation
by one. Provider replacement changes provider or adapter identity and also
increments both generations by one. Connection replacement preserves
provider, adapter, sources, limitations, and source generation and increments
only connection generation by one. The change event is immediately followed
by `epoch_started` with the same cause and no intervening frame or delivery;
the current snapshot becomes active for subsequent records. This is the exact
provider/source/connection evidence used by continuity segmentation.

The acquisition lifecycle state machine is closed:

| Prior state | Event | Next state | Cardinality and generation rule |
| --- | --- | --- | --- |
| `not_opened` | `opened` | `initializing` | exactly once at event sequence 0; detail descriptor and top-level session ID agree |
| `initializing` | `epoch_started` with `session_open` | `running` | exactly once at sequence 1; top-level epoch, detail epoch, and initial configuration effective epoch are equal |
| `initializing` | `stopping` | `stopping` | exactly once at sequence 1; `consumer_stop` has no initiating failure, while `required_evidence_unsatisfied` or `internal_failure` requires one; top-level epoch remains the pending initial epoch and no frame/delivery exists |
| `running` | `demand_replaced` | `reconfiguring` | replacement configuration is generation plus one; no frame or delivery is accepted until the next row |
| `reconfiguring` | `overload_changed` | `reconfiguring` | optional at most once and only when the replacement resolution changed overload status; items exactly equal that resolution's changes |
| `reconfiguring` | `stopping` | `stopping` | permitted only when closing the prior configuration's required subscriber/recording/continuity boundary fails; replacement remains the final effective configuration, accepts no frame, and receives its exhaustive zero-delivery report through this stopping event |
| `reconfiguring` | `epoch_started` with `demand_reconfiguration` | `running` | immediately follows demand replacement or its optional overload event; detail epoch equals replacement configuration effective epoch |
| `running` | source/pause/replay/time-speed change, `clock_discontinuity`, or nonconfiguration `epoch_started` | `running` | local variant invariant applies; an epoch event always changes epoch and its top-level/detail epoch IDs agree |
| `running` | `stopping` | `stopping` | exactly once; no later demand, source, state-change, frame, provider-audit, or delivery event is accepted |
| `stopping` | `terminal` | `terminal` | exactly once as the next acquisition lifecycle event after all closure operations; terminal detail references the stopping event and complete preterminal continuity/recording results |

No other transition is valid. Event sequence is gap-free. At `opened`, the
top-level epoch is the pending initial-configuration epoch. If sequence 1 is
`epoch_started`, the active epoch is thereafter the last accepted
`epoch_started` value and every event's top-level `epoch_id` equals the active
value after applying that event. If sequence 1 is an initializing `stopping`
event, the pending initial epoch remains the top-level epoch through terminal;
no active epoch or frame is fabricated. No event follows terminal. A demand
receipt accepted while
the session is stopping or terminal may affect a later session but cannot
reconfigure this one. Result validation requires the complete event closure
from sequence zero through the referenced terminal event and rejects missing,
duplicate, post-terminal, or detail/top-level-mismatched events.

The stopping event is immutable close intent, not the final activity result.
Its requested reason remains final unless preterminal evaluation proves a
stronger required failure: a required recording sink result that is `failed`,
or is `partial` because of a runtime failure and therefore carries
`primary_failure`, selects `required_sink_failed`; required continuity,
subscriber, or provider-audit failure selects
`required_evidence_unsatisfied`. A required sink result that is `partial`
solely because of declared retention/loss policy has no sink primary, allocates
no orchestrator failure, and does not change the requested termination reason.
An already requested failure reason is never replaced by a later failure. The
terminal primary failure is the smallest causal sequence among the outcome-
specific primary-eligible failures across the initiating failure, endpoint
outcomes, continuity reports, and recording results. Optional sink or
subscriber failure remains in the exhaustive causal closure and is disclosed
in those results but is not terminal-primary-eligible unless the immutable
declaration promoted that item to required before the failure occurred. At
each configuration replacement,
the order is demand-replaced boundary, prior endpoint final-delivery closure,
prior exhaustive report, sink commit/abort and publication, prior recording-
session failure-closure snapshot and result, then the replacement epoch unless required closure failure
stops the acquisition. The final order is stopping intent, final endpoint
  closure, final-configuration report, final recording/recovery/projection
  results, the final failure closure, the terminal lifecycle event, final
  artifact manifests for every recording result/sink,
then the aggregate acquisition-session result. No record references a later
record, so the serialization is acyclic.

If a required continuity item is insufficient and no earlier causal failure
already explains it, the orchestrator allocates one acquisition-domain,
`evaluate`, `required_evidence_unsatisfied` `FailureEvidence` whose
`record_ref` names the earliest insufficient continuity report and whose path
names its first insufficient required item. That evidence exists before the
terminal event and is its eligible primary; an indeterminate item does not
fabricate a failure unless the governing required-evidence policy makes the
activity result failed.

`AcquisitionSessionResult` has `result_id`, `acquisition_session_id`,
`opened_descriptor`, ordered `configurations`, `terminal_event`, `outcome`, `termination_reason`,
optional `primary_failure`, ordered `cleanup_failures`, ordered
`continuity_reports`, ordered `recording_results`, ordered
`recovery_results`, ordered `projection_reports`, `failure_closure: RecordRef`, ordered
`artifact_manifests`, `ended_at`, `producer`, and `content_hash`.

`result_id` and `acquisition_session_id` are `Uuid`; `opened_descriptor` and
`terminal_event` are exact equal-session `RecordRef` values; `ended_at` is
canonical `ObservationTiming` not earlier than the terminal event in a
comparable receipt domain.

- `terminal_event` is the exact `RecordRef` of the already-created terminal
  lifecycle event. Its termination reason and primary failure must match the
  result. Its continuity, recording, recovery, projection, and failure-closure
  references exactly equal the corresponding result properties; those records
  predate terminal and contain no terminal reference.
- `artifact_manifests` contains exactly one final artifact-manifest `RecordRef`
  for each sink result, in recording-result then sink order. Every manifest
  names this acquisition descriptor, its matching recording descriptor and
  sink/root identities, and this terminal event. The manifests are created
  after terminal and before this result; the terminal detail does not reference
  them. `ended_at` is not earlier than every final manifest's `delivered_at` in
  a comparable receipt domain. This result is the last in-session record.
- `configurations` contains every equal-session configuration from generation
  zero through the last effective generation in contiguous order. Entry zero
  equals the descriptor's initial configuration, and every demand-replacement
  event resolves to the corresponding next entry. This finite closure is
  required even when the final configuration contains no stream after demand
  withdrawal.

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
- A required recording sink's declared-loss-only `partial` result remains
  visible in `recording_results` but does not by itself prevent a `completed`,
  `stopped`, or `aborted` acquisition result. Only a required sink result that
  is `failed`, or is runtime-failure `partial` with a primary, can select
  `required_sink_failed` and the acquisition failed row.
- Primary failure is selected by the outcome-specific eligibility and causal
  sequence rules fixed under `FailureEvidence`, across lifecycle, delivery,
  continuity, audit, and recording evidence. Cleanup and optional-only
  failures preserve their own evidence and never replace it.

The result's `continuity_reports` is an ordered nonempty array containing
exactly one continuity-report reference per configuration in configuration
order. `recording_results` is an ordered array containing every equal-session
recording result in configuration order then recording-descriptor order; it is
empty only when no recording descriptor was opened. Every reference belongs to
this acquisition session. `recovery_results` contains every recovery result for
those descriptors in request-acceptance order, and each also appears under its
matching sink result. `projection_reports` contains every report whose failure
scope is `in_session` for this acquisition, in projection-start order; a
standalone projection is prohibited. The terminal `failure_closure` is the
final acquisition-scope snapshot and exhaustively cross-checks all failure
copies in these records, the lifecycle, continuity, fan-out, and final
manifests.
`cleanup_failures` preserves attempt order rather than using array-set ordering.

## Generic synchronous ports and fan-out

`FrameSubscriberDeclaration` is the immutable policy record for one generic
subscriber. Its exact top-level properties are `contract_family`,
`schema_version`, `subscriber_declaration_id: Uuid`,
`acquisition_session_descriptor: RecordRef`, `configuration: RecordRef`,
`demand: RecordRef`, `endpoint_id: Uuid`, ordered nonempty `stream_ids`,
ordered nonempty `initial_delivery_positions`, `criticality`,
`backpressure`, `buffer_capacity`, `detachment_policy`, `declared_at`,
`producer`, and `content_hash`.
The configuration is an equal-session acquisition-session-configuration and
its descriptor equals `acquisition_session_descriptor`.
`demand` is the exact activate-demand `RecordRef` in an active `DemandReceipt`
of the configuration's accepted resolution, and `endpoint_id` equals that
demand's consumer-instance ID. Stream IDs are exactly the distinct
configuration streams selected by that
demand's accepted item outcomes, are unique, and preserve configuration order;
a caller cannot declare a subset. Exactly one declaration exists for every
active demand having at least one accepted item, and no declaration exists for
an active demand having none. `declared_at` is
canonical `ObservationTiming` in the acquisition-session receipt domain. A
configuration replacement closes this declaration's delivery ranges; a
subscriber that continues receives a new declaration for the replacement
configuration before accepting its frames. A retained endpoint-plus-stream
pair continues at the prior notice's next sequence; a new pair begins at zero.
Each `initial_delivery_positions` entry has exact `endpoint_id: Uuid`,
`stream_id: Uuid`, and `first_delivery_sequence: UInt63`, occurs once in stream
order, and records that value. It equals zero for a new pair and the prior
declaration's final next sequence for a retained pair; caller memory cannot
choose another report start.
`criticality` is `required` or `optional`; `backpressure` is `block`, `reject`,
or `drop_oldest`; `buffer_capacity: UInt63` uses zero for synchronous and
unbuffered; and `detachment_policy` is `prohibited`, `on_failure`, or
`on_overflow`. `drop_oldest` requires positive capacity; `on_overflow` requires
`drop_oldest`; and a required subscriber cannot permit detachment. The
declaration is the sole subscriber drop/detach authorization and cannot be
replaced by a profile or inferred from host behavior.

For each configuration, the **fan-out tuple universe** is one exact ordered
set of `(endpoint_id, stream_id, policy)` triples. Its consumer prefix is every
subscriber declaration in active-demand receipt order crossed with that
declaration's complete `stream_ids` order; its recording suffix is every
attached recording descriptor in descriptor order, then every sink declaration
in sink order crossed with that descriptor's complete `streams` order. The
policy is the subscriber-declaration `RecordRef` for a consumer tuple and the
recording-session-descriptor `RecordRef` for a sink tuple. Endpoint IDs are
unique across all subscriber and sink declarations attached to one
configuration, so projection to endpoint-plus-stream is also unique. This one
set, without filtering by `ProtectedItem`, governs accepted delivery calls,
fan-out events, continuity ranges, close notices, commit requests, checkpoints,
delivery summaries, and final delivery positions. `protected_items` attributes
which sink tuples affect which demand item's sufficiency; it never changes
which descriptor streams the sink receives.

Ports are synchronous, capability-segregated, and transport-free. Future
public protocol operation names and argument roles are fixed as follows; their
exact Python module placement belongs to the owning child plan:

```python
ObservationIngress.submit(observation: RawObservation) -> IngressOutcome
ProviderAuditIngress.submit(evidence: ProviderAuditEvidence,
                            content: bytes) -> AuditIngressOutcome
FrameSubscriber.open(descriptor: AcquisitionSessionDescriptor,
                     declaration: FrameSubscriberDeclaration) -> OpenOutcome
FrameSubscriber.accept(frame: MeasurementFrame) -> DeliveryOutcome
FrameSubscriber.close(notice: SessionCloseNotice) -> CloseOutcome
RecordingSink.open(descriptor: RecordingSessionDescriptor) -> OpenOutcome
RecordingSink.append(frame: MeasurementFrame) -> DeliveryOutcome
RecordingSink.append_provider_audit(evidence: ProviderAuditEvidence,
                                    content: bytes) -> AuditDeliveryOutcome
RecordingSink.checkpoint() -> CheckpointOutcome
RecordingSink.commit(request: CommitRequest) -> CommitOutcome
RecordingSink.abort(failure: FailureEvidence) -> AbortOutcome
RecordingSink.recover(request: RecoveryRequest) -> RecoveryOutcome
RecordingSink.close() -> CloseOutcome
```

`SessionCloseNotice` has exact properties `acquisition_session_descriptor`,
`subscriber_declaration`, `close_boundary`, and ordered
`final_delivery_positions`.
`CommitRequest` has exact properties `recording_session_descriptor`,
`close_boundary`, ordered `final_delivery_positions`, ordered
`continuity_reports`, and optional `final_checkpoint`. Each final
position has exact `endpoint_id: Uuid`, `stream_id: Uuid`, and
`next_delivery_sequence: UInt63`, appears in declaration/configuration stream
order, and closes one endpoint-plus-stream sequence without a sentinel.

`close_boundary` is an exact tagged value. Kind `configuration_replaced` has
`boundary_event: RecordRef`, `prior_configuration: RecordRef`,
`replacement_configuration: RecordRef`, and literal `reason:
"configuration_replaced"`; the event is the installing `demand_replaced`
event and its two configuration references equal these values. Kind
`acquisition_stopping` has `boundary_event: RecordRef`,
`requested_termination_reason`, and optional `initiating_failure`; the event is
the equal-session stopping event and its detail equals those values. The
configuration-replaced variant prohibits failure evidence. A subscriber or
recording descriptor for a replaced configuration closes exactly once against
that replacement boundary; one for the last configuration closes exactly once
against acquisition stopping. This is the explicit close/reopen boundary, not
an inferred callback lifetime.

The subscriber notice and commit request contain exactly their ordered
projections of the configuration's fan-out tuple universe: the notice contains
every tuple whose policy is its declaration and the commit contains every tuple
whose endpoint is that sink and whose policy is its recording descriptor.
`final_checkpoint` is present exactly when that sink
created at least one checkpoint and then names its greatest checkpoint
sequence. `continuity_reports` is nonempty and contains the already-created
singleton report for the descriptor configuration. Every final position equals
that report's next sequence for the same sink endpoint/stream, and the range's
first expected sequence is zero because sink-session IDs are never reused.
The subscriber notice positions likewise equal the singleton report's consumer
range ends. A sink that publishes a content manifest must retain the exact
report bytes in its artifact graph.
Both are immutable inputs created from the same close-boundary lifecycle event
before close or commit outcomes. Continuity reports are created after final
delivery closure but before commit, and recording results are created from
commit/abort and close outcomes. A replacement boundary proceeds to its next
epoch after that closure. At acquisition stopping, the terminal event is then
created from stopping intent plus every report/result, final artifact manifests
are created from terminal and sink results, and the aggregate acquisition
result is last; no object participates in its own outcome hash.

The operation outcomes are exact tagged values whose discriminant is always
`result` (never `kind`). Their complete property inventories are:

| Type | `result` variants | Other exact properties in semantic order | Variant invariants |
| --- | --- | --- | --- |
| `IngressOutcome` | `accepted`, `rejected` | `observation: RecordRef`, optional `failure: FailureEvidence` | observation names the submitted raw-observation record; failure is required only for rejected |
| `AuditIngressOutcome` | `accepted`, `rejected` | `evidence: RecordRef`, `payload_sha256: Sha256`, optional `failure: FailureEvidence` | evidence names provider-audit-evidence and hash equals its payload; accepted requires exact content length/hash and active configuration/source closure; failure is required only for rejected |
| `OpenOutcome` | `opened`, `rejected`, `failed` | `endpoint_id: Uuid`, optional `failure: FailureEvidence` | failure is prohibited for opened and required otherwise; endpoint equals the declaration's endpoint/sink-session ID |
| `DeliveryOutcome` | `delivered`, `dropped`, `detached`, `failed` | `frame: RecordRef`, nonempty ordered `delivery_event_refs: RecordRef[]`, optional `failure: FailureEvidence` | frame names the submitted measurement frame; references name fan-out-delivery-event records in increasing endpoint-plus-stream sequence; the final event is for the submitted frame and prior events are older frames evicted by this call; failure is required only for failed |
| `AuditDeliveryOutcome` | `stored`, `rejected`, `failed` | `evidence: RecordRef`, `sink_session_id: Uuid`, optional `failure: FailureEvidence` | evidence names provider-audit-evidence; stored means the exact bytes entered this sink's unpublished artifact graph, not that publication succeeded; failure is prohibited for stored and required otherwise |
| `CheckpointOutcome` | `checkpointed`, `not_due`, `failed` | optional `checkpoint: RecordRef`, optional `failure: FailureEvidence` | checkpoint names archive-checkpoint and is required only for checkpointed; failure is required only for failed |
| `CommitOutcome` | `committed`, `conflict`, `failed` | ordered nonempty `artifact_states: ArtifactState[]`, optional `failure: FailureEvidence`, ordered `cleanup_failures: FailureEvidence[]` | artifact states use artifact-ID then state-sequence order and contain every state reached; failure is prohibited for committed and required otherwise; committed may retain cleanup failures without losing commitment |
| `AbortOutcome` | `aborted`, `failed` | ordered `artifact_states: ArtifactState[]`, optional `failure: FailureEvidence`, ordered `cleanup_failures: FailureEvidence[]` | state ordering matches commit; failure is required only for failed |
| `RecoveryOutcome` | `resumed`, `finalized_partial`, `preserved_partial`, `discarded`, `failed` | `recovery_result: RecordRef`, optional `artifact_manifest: RecordRef` | recovery reference names recovery-result and its outcome equals this result; resumed and pre-admission failed prohibit final manifest, finalized/preserved/discarded and admitted failed require the artifact-manifest created after that result |
| `CloseOutcome` | `closed`, `failed` | optional `failure: FailureEvidence`, ordered `cleanup_failures: FailureEvidence[]` | failure is required only for failed; cleanup failures preserve attempt order |

Every array order above is semantic. References are restricted to the stated
family, and no unlisted property is permitted.

Provider-audit submission is synchronous and content-addressed. The core
verifies the supplied immutable `bytes` against the evidence payload before
acceptance, copies only those bytes into the configured sink calls, and retains
no provider stream, callback, credential, locator, or SDK object. Required
provider-audit retention is not satisfied by ingress acceptance or a `stored`
outcome alone; it is satisfied only by the final archive/manifest closure below.

No operation outcome contains a host exception, transport handle, future, or
callback.

These are push boundaries. The core does not sleep, poll, start a thread,
connect to X-Plane, or invoke consumer business logic reentrantly. A future F1
analysis component may implement a subscriber or consume replay/archive
records, but F1's analysis-specific ports remain owned by `F1.1`.

`FanoutDeliveryEvent` records `delivery_event_id`, `acquisition_session_id`,
optional `recording_session_id`, optional `subscriber_declaration`,
`endpoint_id`, `stream_id`, `frame`, `delivery_sequence`, `disposition`,
`backpressure`, optional `failure`, `policy`, `timing`, `producer`, and
`content_hash`.

`endpoint_id: Uuid` equals the consumer instance ID for a frame subscriber and
the sink-session ID for a recording sink. `recording_session_id` is required
for a recording sink and prohibited for a frame subscriber;
`subscriber_declaration` has the inverse presence and names the exact
frame-subscriber declaration. `stream_id` equals the submitted frame stream
and the event's endpoint/stream/policy triple belongs exactly once to the active
configuration's fan-out tuple universe. A call for any other tuple is rejected
before event or delivery-sequence allocation. `frame` is the exact measurement-frame
`RecordRef`; `delivery_sequence: UInt63` starts at the subscriber declaration's
immutable initial position, or zero for a newly allocated sink session, and is
contiguous thereafter for each `(endpoint_id, stream_id)` pair. It has no
endpoint-only or stream-only interpretation. `timing` is canonical
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
policy or failure evidence and contribute to continuity. `policy` is always an
exact `RecordRef`: it names the subscriber declaration for a frame subscriber
or the recording-session descriptor containing the sink declaration for a
recording sink. A dropped/detached event must be authorized by the referenced
declaration; a failed event must carry failure evidence. The core never
silently drops a frame. One endpoint failure does not mutate another endpoint's
result.

## Continuity reports

`ContinuityReport` has `continuity_report_id`, `acquisition_session_id`,
`configuration`, `resolution`, `scope`, ordered `recording_session_descriptors`,
ordered `provider_audit_closures`,
ordered `item_results`, ordered `stream_summaries`, `overall_result`, `evaluated_at`,
`producer`, and `content_hash`.

- `configuration` is the acquisition-session-configuration `RecordRef` under
  evaluation; `resolution` exactly equals its accepted resolution.
  `evaluated_at` is canonical `ObservationTiming`. Exactly one continuity
  report exists for every effective configuration, including an initializing
  failure or accepted zero-stream configuration. Acquisition and terminal
  closures list those reports in configuration-generation order; reports are
  never optional partitions or caller-selected subintervals.
- `recording_session_descriptors` contains every recording session opened for
  this configuration, in allocation order, and no descriptor from another
  configuration. It is empty exactly when the configuration had no recorder.
  The configuration's fan-out tuple universe uses this array as its exhaustive
  recording-descriptor suffix; later aggregate validation cross-checks every
  matching recording result against it.
- `scope` has exactly `first_event: RecordRef`, `last_event: RecordRef`,
  ordered nonempty `epoch_ids: Uuid[]`, ordered `canonical_record_ranges`, and
  ordered `delivery_ranges`. For generation zero, first event is the session's
  `opened` event. For every later generation it is the `demand_replaced` event
  that installs this configuration. Last event is the next `demand_replaced`
  boundary, or the equal-session `stopping` event when no replacement follows.
  A replaced configuration owns the half-open event/evidence lifetime
  `[first_event,last_event)`; the final configuration owns the closed lifetime
  `[first_event,last_event]`. Adjacent reports therefore share the exact
  replacement boundary as prior close/next open, while that lifecycle event is
  counted only in the replacement report. These intervals form one gap-free,
  nonoverlapping evidence partition from `opened` through `stopping` and cannot
  omit the quiet time before a close boundary. Epoch IDs occur in first-
  appearance order and exactly cover the owned events and records in that
  lifetime, followed by the pending effective epoch when initialization or
  reconfiguration fails before its `epoch_started` event.
- Each `CanonicalRecordRange` has common exact properties `kind`,
  `record_kind`, `stream_id: Uuid`, `epoch_id: Uuid`,
  `first_expected_sequence: UInt63`, and `next_sequence: UInt63`.
  `record_kind` is `raw_observation`, `measurement_sample`, or
  `measurement_frame`. Kind `records` additionally has `first_record:
  RecordRef` and `last_record: RecordRef`; those references match the declared
  family/session/stream/epoch, first sequence equals the expected value, last
  plus one equals next, and the supplied closure contains every intervening
  family-scoped sequence. Kind `empty` has no record references and requires
  first expected equals next. Ranges occur in configuration stream order,
  epoch first-appearance order, then the stated record-kind order, with exactly
  one range for every stream/kind in every epoch in which this configuration
  could accept records, including its pending effective epoch when startup or
  reconfiguration fails before `epoch_started`. A prior epoch that appears only
  on the installing boundary event is not a record-acceptance epoch. The
  configuration's effective epoch starts each family at the stream
  declaration's `initial_sequence`; a later epoch starts at zero. No equal-
  configuration accepted observation, sample, or frame may exist outside
  these ranges, including evidence that never entered a frame or was never
  delivered.
- Each `DeliveryEvidenceRange` has common exact properties `kind`,
  `endpoint_id: Uuid`, `stream_id: Uuid`, `policy: RecordRef`,
  `first_expected_delivery_sequence: UInt63`, and
  `next_delivery_sequence: UInt63`. Kind `events` additionally has
  `first_event: RecordRef` and `last_event: RecordRef`; those equal-session
  fan-out events match endpoint/stream/policy, the first sequence equals the
  expected value, the last plus one equals next, and the supplied closure
  contains every intervening event. Kind `empty` has no other property and
  requires first-expected equals next. Its policy/configuration anchor proves
  that the endpoint/stream existed despite producing no delivery event.
  Ranges occur exactly once in the configuration's fan-out tuple-universe
  order and copy each tuple's endpoint, stream, and policy. There is no
  protected-item filter or independently reconstructed endpoint set. A
  consumer range's first expected sequence equals its subscriber declaration's
  immutable initial position; a sink range starts at zero because its sink
  session is newly allocated. Its next sequence is one plus the greatest
  matching equal-configuration delivery sequence, or equals the first expected sequence when
  none exists. For a retained endpoint/stream it also equals the replacement
  subscriber declaration's immutable initial position. For every configuration
  it equals the matching configuration-replaced or acquisition-stopping
  `SessionCloseNotice` or `CommitRequest` final position.
  These equalities close removed as well as retained pairs without caller-
  chosen end positions. No equal-configuration delivery event may exist
  outside the range. A zero-stream configuration has empty canonical and
  delivery arrays; otherwise the immutable tuple universe is exhaustive.
  No fabricated event, omitted middle event, endpoint-only sequence, favorable
  suffix, or manifest summary can substitute for this finite evidence.
- `provider_audit_closures` contains exactly one
  `ProviderAuditSinkClosure` for every recording sink, protected
  demand/item/binding/source tuple, and retention policy whose provider-audit
  axis is `retain_when_supplied` or `required`. Entries use recording-
  descriptor order, sink order, demand/item order, then selected-binding order.
  Each has exact `recording_session_descriptor: RecordRef`,
  `sink_session_id: Uuid`, `root_artifact_id: Uuid`, `criticality`,
  `retention_policy: DefinitionRef`, `demand: RecordRef`,
  `profile_item_id: Identifier`, `binding: DefinitionRef`,
  `source_acquisition_id: Uuid`, `capability: DefinitionRef`,
  `retention_mode`, `minimum_required_count: UInt63`, ordered `evidence`, and
  `classification`. Criticality, root, protection, policy, capability, and
  source/configuration closure equal the immutable descriptors and resolution.
  Retain-when-supplied uses minimum zero; required uses the capability's exact
  positive minimum.
- Each `ProviderAuditClosureEntry` is a tagged result over one accepted ingress
  record. It begins with `kind` and `evidence: RecordRef`; its exact variants
  are:

  | `kind` | Additional required properties in semantic order | Prohibited properties |
  | --- | --- | --- |
  | `stored` | `delivery_outcome: AuditDeliveryOutcome`, `evidence_member_artifact_id: Uuid`, `evidence_record_index: UInt63`, `payload_member_artifact_id: Uuid`, `payload_byte_length: UInt63`, `payload_sha256: Sha256`, `relationship_id: Uuid` | `failure` and every missing-only property |
  | `missing` | `delivery_outcome: AuditDeliveryOutcome`, `failure: FailureEvidence` | every member-artifact, record-index, byte-length, payload-hash, and relationship property |

  Entries contain every accepted evidence record for the
  source/configuration exactly once in supplied-at receipt order then evidence
  UUID; evidence from another tuple may not appear. `delivery_outcome` is the
  complete immutable outcome returned by this sink call. For `stored`, its
  result is `stored`, evidence and sink IDs match, it has no failure, the record
  member/index resolves the evidence in this sink's provider-audit JSONL
  stream, the payload member resolves its exact bytes, length/hash equal the
  evidence payload, and the relationship ID is the exact `provider_audit_for`
  edge. For `missing`, evidence and sink IDs match and the immutable delivery
  result is `stored`, `rejected`, or `failed`. A rejected or failed delivery
  requires `failure` to byte-identically equal the outcome's failure. A stored
  delivery instead requires the later continuity-domain, `evaluate`,
  `sink_failure` evidence created when close-time verification first finds its
  accepted record, payload bytes, sealing state, or relationship unavailable,
  truncated, hash-mismatched, or otherwise unresolvable; its `record_ref`
  names the accepted evidence and its `artifact_id`, when the failed member had
  already been allocated, names the first failing artifact in evidence-record,
  payload, sealing, then relationship validation order. The immutable outcome
  remains `stored`: this later failure records loss from the unpublished graph
  rather than rewriting delivery history. Every missing variant prohibits
  member IDs, record index, byte length/hash, and relationship coordinates
  because none of those coordinates is asserted to resolve. Missing entries
  are valid close-state failure evidence, not malformed storage claims.
  Closure classification is sufficient exactly when every exhaustive entry is
  `stored`, every stored member/byte is already sealed under the declared root,
  and the stored count meets the minimum; otherwise it is insufficient.
- On later serialization, each `ArtifactContentManifest` compares only the
  closures bearing its sink/root identity and must contain exactly the stored
  subset's evidence members, indexed records, payload members, hashes, and
  relationship IDs; no missing entry creates an artifact or relationship. A
  closure whose sink `criticality` is `required` affects protected-item
  sufficiency; an optional-sink closure shortfall is disclosure only.
  `retention_mode` independently selects whether the positive capability
  minimum applies. This per-root equality, not ingress acceptance, a count
  alone, or another sink's graph, proves retention.
- Every accepted required and optional demand item appears once in
  `item_results`; each result is scoped to that demand item's consumer
  endpoint rather than aggregated across unrelated fan-out endpoints.
- An item result has exact properties `demand`, `profile_item_id`,
  `endpoint_id`, `effective_delivery_period`, `continuity_policy`,
  ordered nonempty `binding_results`,
  `observed_count`, `eligible_count`, `delivered_count`,
  `eligible_delivered_count`, `elapsed_span_ns`, `first_slot_ready`, optional
  `minimum_interval_ns`, optional `maximum_interval_ns`, `gap_count`,
  `maximum_gap_ns`, `unmatched_slot_count`, `drop_count`, `detach_count`,
  `duplicate_count`, `reorder_count`, `staleness_count`, `invalid_count`,
  `prohibited_quality_count`, `clock_incomparable_count`,
  `validity_distribution`, `quality_distribution`, `epoch_count`,
  `source_generation_count`, `connection_generation_count`,
  `provider_context_count`, `burst_max_observed_count`,
  `burst_violation_count`, ordered `transition_results`,
  `provider_audit_shortfall_count`,
  `optional_provider_audit_shortfall_count`, `sink_failures`,
  `required_sink_failure_count`, `optional_sink_failure_count`,
  `classification`, and `reasons`. Counts and durations are `UInt63`; the two
  interval properties are present exactly when at least one within-epoch
  interval exists.
- `continuity_policy` has exact properties `profile: DefinitionRef` and
  `profile_item_id: Identifier`. The profile equals the demand's exact profile,
  the item ID equals this result's item ID, and resolving that immutable
  definition supplies the exact continuity body and tolerances. The report
  cannot copy, override, or infer a policy from current configuration.
- Each `BindingContinuityResult` repeats the metric properties from
  `observed_count` through `reasons` and first adds `binding: DefinitionRef`,
  `source_acquisition_id: Uuid`, and `stream_id: Uuid`. Entries follow the
  resolution's selected-source order. Additive item counts and distributions
  are exact sums of mutually attributable binding values. Item interval
  extrema, elapsed span, gap metrics, unmatched slots, readiness, and distinct
  epoch/source-generation/connection-generation/provider-context counts,
  burst metrics, transition results, and sink/audit closure are recomputed over
  the merged scoped evidence, using delivery evidence exactly for the metrics
  that require it; classification and reasons are then derived from those
  merged values. None of those fields is obtained by summing binding
  extrema, booleans, distinct counts, classifications, or reasons. This
  per-binding evidence is mandatory even when selection chose one source.
- `validity_distribution` is `CountDistribution<ValidityState>` and
  `quality_distribution` is `CountDistribution<QualityFlag>`. A sample with
  multiple quality flags contributes once to every matching quality bucket,
  so quality counts do not sum to observed count; `eligible_count` and the
  validity distribution do. `invalid_count` counts observations whose sample
  validity is outside the required set; `prohibited_quality_count` counts
  samples containing at least one prohibited flag; `clock_incomparable_count`
  counts otherwise selected samples that cannot enter slot/interval comparison;
  `provider_context_count` is the number of distinct provider/adapter/version
  tuples; `source_generation_count` and `connection_generation_count` are the
  corresponding distinct generation counts. They traverse the configuration's
  initial source snapshot plus every source-context-change event associated
  with scoped evidence; an unrecorded identity or generation change invalidates
  the report. `sink_failures` equals required plus optional sink-failure counts.
- Consumer delivery counts are derived only from that binding's complete
  consumer endpoint-plus-stream range. `delivered_count`, `drop_count`, and
  `detach_count` count the equal-named dispositions. A duplicate is a delivered
  event whose frame `RecordRef` already appeared earlier in the same endpoint-
  plus-stream range.
  A reorder is a nonduplicate delivered event whose frame's canonical stream
  sequence is less than the greatest previously delivered sequence in that
  range. These tests use delivery sequence for traversal and never timestamps.
  An empty range deterministically contributes zero to every delivery count and
  permits `no_observation`; it never suppresses the item or binding result.
- For each protected sink range, delivery `failed`, `dropped`, or `detached`
  dispositions contribute to
  `required_sink_failure_count` or `optional_sink_failure_count` according to
  the immutable sink criticality. The sink's `protected_items` entry is the
  exact relation to this demand item and binding stream. Required sink failure
  affects sufficiency; optional sink failure is disclosure only. Later
  commit, publication, or close failure is recording-integrity evidence and
  affects the activity terminal result without retroactively changing this
  precommit delivery-continuity report.
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
  event's monotonic reading, or at the configuration-opening event's monotonic
  reading when the configuration begins in its pending initial epoch, and
  advance by the exact rational `effective_delivery_period` strictly before a
  replacement close boundary or through an inclusive stopping boundary.
  `first_slot_ready` is true exactly when the first expected slot is matched.
  A delivered eligible sample satisfies at most one slot when its acquisition
  reading lies within the closed interval from slot minus
  `interval_distribution.early_tolerance_ns` through slot plus
  `interval_distribution.late_tolerance_ns`. Slots and samples
  are matched in increasing exact rational time, then canonical sample order;
  `unmatched_slot_count` is the exact number left unmatched. No binary-float
  rounding is used in slot construction or comparison.
- Intervals, gaps, burst windows, and transition windows are segmented whenever
  epoch, provider/adapter identity, source generation, or connection generation
  changes. No interval crosses a segment boundary. An epoch transition is
  reported as `epoch_boundary`, provider/source change as `provider_change`,
  and connection change as `connection_change`, never as an ordinary gap.
  `elapsed_span_ns` is the sum of the last-minus-first eligible-delivered span
  in each segment. Gap count is the
  number of within-epoch eligible-delivered intervals greater than the policy
  gap threshold; the result property's `maximum_gap_ns` is the greatest
  observed within-epoch gap and is zero when none exists.
- `burst_max_observed_count` is the greatest rolling count under the profile's
  exact closed-open burst window, or zero with no observation.
  `burst_violation_count` increments once for each observation whose inclusion
  makes that rolling count exceed `maximum_observations`; traversal is
  acquisition time then canonical observation order within one segment.
- Each `TransitionCoverageResult` has exact `event_kind`, `boundary_event:
  RecordRef`, `pre_eligible_delivered_count: UInt63`,
  `post_eligible_delivered_count: UInt63`, ordered `prior_closures`,
  `classification`, and `reasons`.
  Entries occur in profile requirement order then lifecycle event sequence and
  cover every matching boundary event in scope. Reasons are an `ArraySet` of
  `pre_transition_shortfall`, `post_transition_shortfall`, and
  `clock_incomparable`; the first two are biconditional with counts below their
  profile minima. Classification is insufficient for either shortfall,
  otherwise indeterminate for clock incomparability, otherwise sufficient.
  A `demand_replaced` requirement is evaluated only when the exact
  profile/item/binding authorization remains accepted in the replacement
  configuration, and it appears in that replacement configuration's report,
  never the already-committed prior report. `prior_closures` is empty for every
  other event kind and contains exactly one `PriorTransitionClosure` per
  selected binding for `demand_replaced`, in selected-binding order.
- Each `PriorTransitionClosure` is one closed tagged object. Its common
  properties, in semantic order, are `kind`, `prior_configuration: RecordRef`,
  `prior_report: RecordRef`, `boundary_event: RecordRef`,
  `prior_demand: RecordRef`, `profile_item_id: Identifier`,
  `binding: DefinitionRef`, and `source_acquisition_id: Uuid`. The variants are:

  | `kind` | Additional required properties in semantic order | Optional properties | Prohibited properties |
  | --- | --- | --- | --- |
  | `available` | `prior_recording_result: RecordRef`, `prior_content_manifest: RecordRef`, `prior_root_artifact_id: Uuid`, `current_link: TransitionArchiveLink`, ordered nonempty `member_ranges` | — | `cause`, `prior_recording_results`, `failure` |
  | `unavailable` | `cause`, ordered `prior_recording_results: RecordRef[]` | `failure: FailureEvidence` | every content-manifest, root-artifact, current-link, and member-range property |

  Prior configuration is exactly generation minus one, prior report is that
  configuration's exhaustive report, and boundary event is the installing
  `demand_replaced` event shared by the two adjacent report scopes. The
  unavailable variant's `prior_recording_results` contains exactly one result
  for every descriptor in the prior report's
  `recording_session_descriptors`, in that order, and is empty with that array.
  Final acquisition-result validation cross-checks this array against its
  equal-configuration recording-result slice; it is not a caller-selected
  subset. `prior_demand` is the prior configuration's active demand and the
  enclosing item result's demand is the replacement configuration's active
  demand. Their profile/item requirement, measurement, binding, phase, and
  retention authorization are byte-identical even when demand IDs or
  generations differ.

- The unavailable `cause` is the first applicable member of this closed order:
  `prior_recorder_absent` when the prior report's descriptor array is empty;
  `prior_retention_unavailable` when no prior descriptor contains a required
  canonical-archive sink protecting the tuple whose policy retains all four
  predecessor record kinds; `prior_publication_unavailable` when none of those
  eligible sinks has a matching published successful/partial recording result
  and content graph. For publication unavailability, the failure is
  byte-identically the lowest descriptor/sink-order eligible runtime failure
  exactly when such a failure exists, and is otherwise prohibited. It is
  prohibited for every other cause. These report,
  lifecycle, descriptor, and result references are the complete evidence that
  the predecessor count is zero; the variant cannot invent storage coordinates
  or artifact/content references.

- The available variant selects the lowest prior descriptor/sink order whose
  published required canonical-archive graph protected this item/binding and
  retained all four member-range kinds. Its recording result proves the exact
  prior content manifest/root. `current_link` is a closed tagged object. Kind
  `planned` has exact `current_recording_session_descriptor: RecordRef`,
  `current_sink_session_id: Uuid`, `current_root_artifact_id: Uuid`, and
  `relationship_id: Uuid`, selecting the identical lowest-order eligible sink
  from the enclosing report's descriptor array. Kind `unavailable` has exactly
  `cause`, equal to `current_recorder_absent` when that array is empty or
  `current_retention_unavailable` when no eligible current sink exists, and
  prohibits every descriptor/sink/root/relationship property. Current-link
  availability never changes the predecessor count. If any prior unavailable
  condition applies, predecessor kind `available` is
  prohibited even when some different optional graph contains useful bytes.
- For predecessor kind `available`, each `TransitionMemberRange` has common
  exact properties `kind`, `record_kind`, `logical_stream_key: NfcText(512)`, ordered
  `member_artifact_ids: Uuid[]`, `first_archive_record_index: UInt63`, and
  `next_archive_record_index: UInt63`. Record kind is `raw_observation`,
  `measurement_sample`, `measurement_frame`, or `fanout_delivery_event`, and
  exactly one range of each kind appears in that order. Kind `records` requires
  nonempty member IDs plus `first_record: RecordRef` and `last_record:
  RecordRef`; member IDs are exactly every segment intersecting the range in
  segment order, and the indexes/references close every matching record in the
  exact pre-window. Kind `empty` prohibits record references, uses equal
  indexes, and names at most the immediately preceding member ending at that
  boundary and immediately following member beginning there, in that order.
  Member IDs may be empty only when the prior report's corresponding exhaustive
  range is empty; otherwise those adjacent member identities and their sealed
  index bounds prove the empty insertion point.
  Record timing lies in `[boundary - pre_window, boundary)`, delivery records
  use the demand consumer endpoint, and all records match stream, epoch,
  binding, source acquisition, and prior authorization. The prior exhaustive
  report plus content-manifest indexes proves both inclusion and absence.
- For predecessor kind `available` with current-link kind `planned`, every
  completed current content manifest contains exactly one
  `transition_predecessor` relationship with the link's `relationship_id`,
  from the local continuity-report artifact to the prior external content-
  manifest root. A current sink failure before content-manifest completion
  leaves that preallocated relationship unmaterialized and does not invalidate
  the already-created report or change its predecessor count.
  Validation resolves the prior content-manifest hash, report/member identities
  and byte hashes, relationship, configuration adjacency, authorization, four
  ranges, then counts. Kind `unavailable` supplies no substitute records and
  makes the pre count zero without any unresolved reference; the shortfall is
  derived from that zero. A rejected resolution
  creates no replacement configuration or boundary result; its ordinary
  stopping failure remains the evidence. Post-window evidence comes only from
  the replacement report's exhaustive ranges. All other item metrics remain
  scoped to that report configuration.
- `provider_audit_shortfall_count` counts this item/binding's required-sink
  provider-audit closures classified insufficient;
  `optional_provider_audit_shortfall_count` counts the optional-sink closures.
  Both are zero when no corresponding closure is required. Evidence from
  another sink, root, source, configuration, role, media type, record index, or
  byte hash never contributes.
- `classification` is `sufficient`, `insufficient`, or `indeterminate`.
- `reasons` is an `ArraySet` drawn from `no_observation`, `count_shortfall`,
  `span_shortfall`, `cadence_shortfall`, `gap_exceeded`, `stale_evidence`,
  `invalid_evidence`, `prohibited_quality`, `drop_observed`,
  `detachment_observed`, `duplicate_observed`, `reordering_observed`,
  `burst_exceeded`, `transition_coverage_shortfall`,
  `provider_audit_missing`, `optional_provider_audit_missing`,
  `epoch_boundary`, `provider_change`,
  `connection_change`, `sink_failure`, `optional_sink_failure`, or
  `clock_incomparable`.

Reason derivation is biconditional—each reason is present exactly under its
row and prohibited otherwise:

| Reason | Exact condition |
| --- | --- |
| `no_observation` | `observed_count == 0` |
| `count_shortfall` | `eligible_delivered_count < minimum_observation_count` |
| `span_shortfall` | `elapsed_span_ns < minimum_elapsed_ns` |
| `cadence_shortfall` | `unmatched_slot_count > 0` (including an unmatched first slot) |
| `gap_exceeded` | `gap_count > 0` |
| `stale_evidence` | `staleness_count > 0` |
| `invalid_evidence` | `invalid_count > 0` |
| `prohibited_quality` | `prohibited_quality_count > 0` |
| `drop_observed` | `drop_count > 0` |
| `detachment_observed` | `detach_count > 0` |
| `duplicate_observed` | `duplicate_count > 0` |
| `reordering_observed` | `reorder_count > 0` |
| `burst_exceeded` | `burst_violation_count > 0` |
| `transition_coverage_shortfall` | at least one transition result is `insufficient` |
| `provider_audit_missing` | `provider_audit_shortfall_count > 0` |
| `optional_provider_audit_missing` | `optional_provider_audit_shortfall_count > 0` |
| `epoch_boundary` | `epoch_count > 1` |
| `provider_change` | `provider_context_count > 1` or `source_generation_count > 1` |
| `connection_change` | `connection_generation_count > 1` |
| `sink_failure` | `required_sink_failure_count > 0` |
| `optional_sink_failure` | `optional_sink_failure_count > 0` |
| `clock_incomparable` | `clock_incomparable_count > 0` |

Classification precedence is closed. For each binding, any of
`no_observation`, `count_shortfall`, `span_shortfall`, `cadence_shortfall`,
`gap_exceeded`, `stale_evidence`, `invalid_evidence`, `prohibited_quality`,
`drop_observed`, `detachment_observed`, `duplicate_observed`,
`reordering_observed`, `burst_exceeded`, `transition_coverage_shortfall`,
`provider_audit_missing`, or `sink_failure` makes it `insufficient`. With
none of those reasons, `clock_incomparable` makes it `indeterminate`; otherwise
it is `sufficient`.
`epoch_boundary`, `provider_change`, `connection_change`, and
`optional_sink_failure` or `optional_provider_audit_missing` are mandatory
disclosures but do not by themselves change classification because all
thresholds are recomputed per exact segment and optional sinks cannot establish
required evidence.

For exact, preferred, or any-compatible selection, item classification equals
its one binding classification. For corroborated selection, let `required` be
the profile's `minimum_successful_bindings`, `passed` the sufficient-binding
count, and `possible` the sufficient-plus-indeterminate count. The item is
`sufficient` when `passed >= required`, `insufficient` when
`possible < required`, and `indeterminate` otherwise. Item reasons are the
canonical union of binding reasons plus any independently derived merged-slot
or delivery reason. This proves the minimum per binding rather than from
aggregate counts. Overall result is `sufficient` only when every required item
is sufficient; an indeterminate required item makes it indeterminate unless
another required item is insufficient. Optional items never improve the
overall result.

Each `StreamSummary` has exact properties `stream_id: Uuid`,
`source_acquisition_id: Uuid`, `first_epoch_id: Uuid`, `last_epoch_id: Uuid`,
`epoch_count: UInt63`, `observed_count: UInt63`, `sample_count: UInt63`,
`frame_count: UInt63`, `delivered_frame_count: UInt63`, `drop_count: UInt63`,
`detach_count: UInt63`, `duplicate_count: UInt63`, `reorder_count: UInt63`,
`source_generation_count: UInt63`, and `connection_generation_count: UInt63`.
Summaries appear in configuration stream order, cover only the report scope, and
reconcile with the item results and referenced delivery events. Counts include
records excluded from eligibility; they never imply continuity sufficiency.

Continuity reports acquisition sufficiency only. They do not contain q4xpcc
performance findings or FDM/FOQA operational findings.

## Recording-session and sink contracts

One recording session is a fan-out group attached to exactly one acquisition
session. An acquisition session may own zero or more recording sessions, and a
recording session owns one or more sink sessions.

`RecordingSessionDescriptor` has `recording_session_id`,
`acquisition_session_descriptor`, `configuration`, `resolution`, ordered
`streams`, literal `configuration_boundary: "close_and_reopen_explicit"`,
ordered `sinks`, `segment_policy`, `opened_at`, `producer`, and `content_hash`.

`recording_session_id` is `Uuid`; the acquisition descriptor, configuration,
and accepted resolution are exact `RecordRef` values and agree with one
another. `streams` is a nonempty ordered subset of the configuration's complete
`StreamDeclaration` values, preserving configuration order. `sinks` is nonempty
and unique by sink-session, endpoint, destination, and planned-root identity.
Every declared sink receives every descriptor stream and therefore contributes
one tuple per descriptor stream to the configuration's fan-out tuple universe;
partial protection never narrows this delivery set. A sink-session ID may not
equal any active demand consumer-instance ID or another attached sink-session
ID in the same configuration.
`opened_at` is canonical `ObservationTiming` and is not earlier than the
acquisition descriptor opening in a comparable receipt domain.

An acquisition configuration replacement closes each attached recording
session through its ordinary commit/abort/close protocol before frames from the
new configuration are accepted. Continued recording requires a newly allocated
recording-session descriptor referencing the replacement configuration; this
is the explicit split and never reuses sink-session or artifact IDs. The
acquisition session may continue, and all descriptors, configurations,
resolutions, lifecycle events, and cross-session relationships remain archived
in causal order.

Each `SinkDeclaration` has `sink_session_id`, `sink_kind`, `artifact_role`,
`criticality`, ordered nonempty `protected_items`, `capabilities`,
`destination`, `data_classification`, optional `profile`,
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
- Each `ProtectedItem` has exact properties `demand: RecordRef`,
  `profile_item_id: Identifier`, and `stream_id: Uuid`. The demand is an
  accepted item in the descriptor's exact resolution, the profile item is that
  accepted item's ID, and the stream resolves its selected binding and source
  acquisition in the descriptor configuration. Entries use demand receipt
  order, profile item order, then selected-source order and are unique by all
  three properties. Every accepted item's selected binding stream is protected
  by at least one sink; protecting a stream for one item does not implicitly
  protect another item on that stream. Every accepted item whose demand
  requirement is `required` is protected by at least one required
  retention-capable sink that independently satisfies its retention body.
  This immutable relation, not sink kind or later delivery, fixes which sink
  can affect each item's continuity; it is sufficiency attribution only and
  does not filter that sink's declared delivery tuples.
- `capabilities` has exact properties `publishes_artifact: Boolean`,
  `supports_checkpoint: Boolean`, `supports_recovery: Boolean`,
  `supports_retention: Boolean`, and optional `required_profile_family` equal
  to one family URI known by the descriptor validator. Profile is required
  exactly when that family is present and must reference it. Retention policy
  is permitted exactly when retention support is true. Checkpoint or recovery
  calls against a false corresponding capability fail before byte mutation or
  a new artifact state through their closed failed outcomes.
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
- `data_classification` is the operator-selected closed value `unspecified`,
  `public`, `internal`, `sensitive`, or `restricted`. It is fixed before sink
  open and is the authoritative value copied to every content and final
  manifest, including discarded, never-created, and failed no-content cases.
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
  artifact-content-manifest `RecordRef` plus its serialized byte length and
  SHA-256.
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
- `provider_audit: retain_when_supplied` requires every accepted audit evidence
  record and exact supplied byte sequence in this recording scope to survive in
  the archive. `provider_audit: required` additionally requires, for every
  protected demand item and selected source acquisition, at least the pinned
  capability's `minimum_evidence_count` records in each referenced
  configuration. Every record, capability, payload member, artifact entry, and
  `provider_audit_for` relationship must validate; ingress acceptance alone
  never satisfies retention. A missing record or byte makes the protected
  required sink and item continuity insufficient.

A recording session may span acquisition epochs. Epoch transitions remain
explicit records. A sink may declare a terminal discontinuity policy, but no
implicit split or identity reset occurs.

## Canonical archive logical format

The canonical archive is an artifact-content-manifest-rooted graph of
immutable artifacts, not a pathname, ZIP byte stream, SQLite database, or
custom binary container.

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
|-- resolutions/
|   `-- <resolver-instance-id>/<generation>-<resolution-id>.json
|-- configurations/
|   `-- <configuration-generation>-<configuration-id>.json
|-- streams/
|   `-- <stream-id>/
|       |-- observations/<segment>.jsonl
|       |-- samples/<segment>.jsonl
|       `-- frames/<segment>.jsonl
|-- events/
|   |-- lifecycle/<segment>.jsonl
|   `-- fanout/<endpoint-id>/<stream-id>/<segment>.jsonl
|-- order/global/<segment>.jsonl
|-- checkpoints/<checkpoint-sequence>.json
|-- payloads/sha256/<first-two-hex>/<remaining-sixty-two-hex>
|-- provider-audit/
|   |-- <source-acquisition-id>/evidence/<segment>.jsonl
|   `-- payloads/sha256/<first-two-hex>/<remaining-sixty-two-hex>
|-- continuity/<continuity-report-id>.json
`-- artifact-content-manifest.json
```

The closed definition-family tokens are `measurement-catalog`,
`source-binding-catalog`, `acquisition-profile`, `transform-registry`,
`source-retention-capability`, and `raw-retention-policy`. Each path uses the
definition family's identity field,
revision rendered as twenty zero-padded decimal digits, and exact definition
hash. Demand, resolution, configuration, and checkpoint generation/sequence
use the same twenty-digit rendering. UUID path components use canonical
lowercase UUID text. The archive contains every demand receipt, resolution,
and acquisition-session configuration referenced by its descriptor, lifecycle
events, frames, continuity, or terminal result in increasing receipt,
resolution, and configuration order, plus the complete definition closure
needed to validate retained records. Duplicate byte-identical definitions
occur once.

The global-order stream contains one `ArchiveOrderEntry` for every retained
raw observation, measurement sample, measurement frame, acquisition lifecycle
event, provider-audit evidence record, and fan-out delivery event. It does not
duplicate the target record.
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

Provider-audit bytes are distinct from raw-observation payloads and use the
provider-audit content-addressed tree. Each evidence record appears in its
source-acquisition stream and its `payload` resolves to exactly one audit byte
member with equal media type, storage role, length, and SHA-256. Evidence and
byte members are checkpointed and reference-closed like every other record and
payload, but never become a canonical measurement value.

A deterministic ZIP may later package the artifact set for transport, and a
SQLite database may later index or project it for analysis. Those artifacts
carry their own identities and `derived_from` relationships and never replace
the artifact-content-manifest-rooted canonical evidence graph.

## Checkpoint, publication, and recovery

`ArchiveCheckpoint` has `checkpoint_id`, `recording_session_id`,
`sink_session_id`, `root_artifact_id`, `descriptor`, `checkpoint_sequence`,
optional `previous_checkpoint`, ordered `sealed_members`, ordered
`open_streams`, `referenced_content`, ordered `delivery_positions`,
`created_at`, `producer`, and `content_hash`.

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
- `referenced_content` has exact `standalone_member_ids`, `payload_member_ids`,
  and `definition_member_ids`, each an `ArraySet<Uuid>`. Every ID resolves to a
  sealed member in this checkpoint. Standalone members include every retained
  descriptor, demand, resolution, configuration, checkpoint predecessor, and
  one-record report referenced from a safe record prefix. Payload members
  include every retained raw or provider-audit payload referenced by those
  records; provider-audit evidence and bytes occur together. Definition
  members include the entire transitive definition closure. A referenced
  record may instead resolve inside another listed sealed JSONL range or open
  safe prefix, but nowhere outside the checkpoint cut.
- Each `delivery_positions` entry fixes `endpoint_id: Uuid`, `stream_id: Uuid`,
  and `next_delivery_sequence: UInt63` for this sink, so zero represents no
  prior delivery without a sentinel. Entries are exactly the sink projection
  of the descriptor configuration's fan-out tuple universe, in descriptor
  stream order, with no protected-item filter.
- A checkpoint is one consistent cut across all listed streams: append is
  quiescent for the synchronous call, every safe prefix is flushed through the
  cut, sealed-member hashes are verified, and the checkpoint file is itself
  published atomically with no replacement. A reported checkpoint never names
  an unverified or partially serialized checkpoint record.

A checkpoint cut is eligible for checkpoint, resume, or checkpoint-capable
finalization only after this deterministic closure validation succeeds:
(1) validate checkpoint identity,
hash, sequence, and predecessor; (2) verify every sealed member's length/hash;
(3) verify every open safe length and prefix hash; (4) parse every complete
record in logical-stream-key then archive-record-index order and verify its
canonical bytes, self-hash, family, and index; (5) resolve every `RecordRef`
against a standalone member or record inside the same cut with exact family,
version, identity, and hash; (6) resolve every retained `PayloadReference` to
its canonical raw or provider-audit hash path and exact length/SHA-256; and (7) resolve every
definition, demand, resolution, configuration, and manifest-independent policy
reference through `referenced_content`. The first failure in that order is the
recovery primary failure. Tail preservation happens only after all seven steps;
a hash-valid prefix with any dangling content reference is ineligible.

The planned root artifact receives its `artifact_id: Uuid` before sink open.
Every dynamically created segment, payload, checkpoint, report, or content-
manifest member receives its own artifact ID before its first byte is written.
Those UUIDs are lifecycle identities and remain stable through recovery. Each
`ArtifactState` has exact properties `artifact_id`, `artifact_ordinal`,
`state_sequence`, `disposition`, variant-selected `content`, optional
`disposition_evidence`, and `recorded_at`.
`artifact_ordinal: UInt63` is allocated gap-free for the sink with root zero
when the artifact ID is preallocated and never changes. `state_sequence` is
contiguous from zero per artifact; within a supplied state history, sequence
*n* supersedes sequence *n - 1* without mutating it.
`disposition` is `planned`, `open`, `sealed`, `preserved_partial`, `published`,
or `discarded`. Content kind `absent` is valid exactly for a planned artifact,
an open logical graph root, or a discarded artifact. An open, sealed,
preserved, or published byte-bearing artifact uses content kind `bytes` with
byte length and SHA-256. A sealed, preserved, or published logical graph root
instead uses content kind `content_manifest` with the artifact-content-manifest
`RecordRef` plus its serialized byte length and SHA-256. `discarded` requires
content kind `absent` plus `disposition_evidence` with exact properties
`authorization: DeletionAuthorization`, `deletion_attempt_sequence: UInt63`,
and `deletion_completed_at: ObservationTiming`; that evidence is prohibited
for every other disposition. Attempt sequence follows the recovery action's
deterministic deletion order—non-root artifacts by descending ordinal, then
root—with a contiguous sequence from zero; completion is not later than
`recorded_at` in a comparable receipt domain. Discarded state prohibits
byte/hash or manifest content. Content state never substitutes for artifact identity.
`recorded_at` is canonical `ObservationTiming`; consecutive states for one
artifact are nondecreasing when receipt clocks are comparable.

`ArtifactStateLedger` is the immutable, self-hashed crash-recovery authority
for one sink's artifact universe. Its exact top-level properties are
`contract_family`, `schema_version`, `artifact_state_ledger_id: Uuid`,
`recording_session_descriptor: RecordRef`, `sink_session_id: Uuid`,
`root_artifact_id: Uuid`, `ledger_sequence: UInt63`, optional
`previous_ledger: RecordRef`, ordered nonempty `entries`,
`recorded_at: ObservationTiming`, `producer`, and `content_hash`.

Each `ArtifactLedgerEntry` has exact properties `artifact_id: Uuid`,
`artifact_ordinal: UInt63`, `role: Identifier`, optional
`relative_path: NfcText(2048)`, and ordered nonempty `states: ArtifactState[]`.
Entry zero is the preallocated root with ordinal zero and absent relative path;
later entries have contiguous ordinals, unique IDs, and the immutable role/path
assigned before creation. Each state repeats the entry ID/ordinal and is the
complete gap-free sequence from state zero through that ledger's state head.
Relative path is absent only for a pathless root and otherwise obeys the
canonical relative-POSIX rules.

Ledger sequence is contiguous from zero. The initial record is durably
published with only the root's `planned` state before sink open or any root-byte
mutation and prohibits `previous_ledger`; every successor references the exact
sequence-minus-one ledger. A successor repeats every prior entry and history
byte-identically except for exactly one of these changes: it adds the next
ordinal with its state-zero `planned` allocation, or it appends the next state
to one existing history. Thus every allocation and state transition is
recoverable from the hash chain without mutable process memory.

Crash-safe operation order is fixed. To allocate an artifact, the sink first
preallocates its UUID/ordinal/role/path, atomically publishes and durably flushes
the next no-replace ledger record, and only then creates a path or writes its
first byte. To append a byte-bearing state, it first durably flushes the exact
bytes and evidence named by that state and then atomically publishes the next
ledger record. An interrupted write therefore leaves either no allocated
artifact or an already inventoried artifact whose extra bytes are recoverable
tail, never an unledgered member. Successful deletion precedes its discarded-
state ledger append; a crash in between remains an inventoried missing member
and fails closed rather than disappearing from the universe. Ledger records
live in the sink's reserved recovery-control namespace, are not content-graph
artifacts, and never recursively allocate themselves.

The uniquely greatest valid contiguous ledger record present in that reserved
namespace is the recovery input head. Recovery admission receives the
namespace's exhaustive delivered ledger-record set, validates canonical bytes,
self-hashes, descriptor/sink/root identity, sequence, predecessor hashes,
successor deltas, and absence of a later/gapped/colliding record, then requires
the request's pinned input head to equal it. This immutable head, not directory
enumeration, a checkpoint cut, a prior result, or implementation-private
memory, is the proven root/member universe. Omission of either a ledger record
or an entry makes the ledger closure invalid.

Ordinary terminal result construction performs the same live exhaustive
reserved-namespace admission after the last publication/discard/planned-state
ledger append and before serializing `SinkResult`. The result pins that exact
head as `artifact_state_ledger`; a final `ArtifactManifest` pins the applicable
ordinary or recovery head under the rules below. Flattening the pinned head's
entries in artifact-ordinal then state-sequence order must be byte-identical to
the terminal publication's `artifact_states`, so a planned allocation whose
path or first byte was never created remains visible and cannot be omitted.

A backward-linked ledger prefix proves its contents and deltas through a
pinned head; by itself it cannot cryptographically prove that a presenter has
not withheld a later successor. Version-1 portable validation therefore
trusts the immutable result producer's recorded live exhaustive-namespace
admission, bound by `ProducerIdentity`, the result self-hash, and the pinned
head. It validates the complete chain through that historical head but does
not claim successor absence from caller-supplied prefix bytes. A later valid
recovery successor does not invalidate the earlier result. A relying party
that will not trust that recorded live decision must obtain a separately
authenticated complete namespace inventory or head assertion outside these
families; no checkpoint, directory listing, backward hash link, or standalone
validator argument may be described as supplying that additional trust.

An immutable content-manifest entry uses the exact tagged `content_state` table
below with kind `sealed`, `preserved_partial`, or `omitted_by_policy`.

- `sealed` requires final byte length and SHA-256 and means the member cannot
  change; it does not predict whether publication of the containing archive
  root will succeed.
- `preserved_partial` requires current byte length, SHA-256, recovery
  eligibility, and failure evidence.
- `omitted_by_policy` references the exact retention policy and prohibits a
  lossless claim.

A terminal sink result separately uses the six exact
`SinkPublicationDisposition` rows fixed below. `published` closes a byte root
or logical content-manifest root through its artifact-state history;
`preserved_partial` retains the causal failure; `discarded` retains deletion
authorization and cleanup evidence; `not_created` retains the earlier failure;
`omitted_by_policy` retains the policy; and `not_applicable` is restricted to a
declared nonpublishing sink. No disposition has fields outside its table row.

Publication atomicity is per sink, not across the recording-session fan-out.
For one sink, all candidate members and the content manifest are sealed before
the publication precondition is evaluated, and the root becomes visible as one
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

`RecoveryRequest` is a generated immutable, self-hashed record with exact
top-level properties `contract_family`, `schema_version`,
`recovery_request_id: Uuid`, `recording_session_descriptor`,
`sink_session_id: Uuid`, `root_artifact_id: Uuid`,
`input_state_ledger: RecordRef`, `destination`, `action`,
optional `discard_authorization`, `requested_at`, `producer`, and
`content_hash`. `action` is `resume`, `finalize_partial`, `preserve`, or
`discard`. A complete `DeletionAuthorization` is required only for `discard`
and is prohibited otherwise; equality with the declaration is an operation-
admission rule below, so a well-formed unauthorized attempt can still produce
failure evidence. The descriptor is a recording-session-descriptor
`RecordRef`; destination has the exact `DestinationIdentity` shape and asserts
the intended sink destination for later cross-validation.
`input_state_ledger` names the claimed greatest persisted artifact-state-ledger
head for the same descriptor/sink/root and is checked against the exhaustive
reserved-namespace ledger set during admission; `requested_at` is
canonical `ObservationTiming`. Request identity/hash equality is the only
idempotency key; reuse of its UUID with different content fails before byte
mutation.

`RecoveryResult` has `recovery_result_id`, `recording_session_id`,
`sink_session_id`, `request`, `input_state_ledger`, optional
`output_state_ledger`, optional `selected_checkpoint`, optional
`prior_recording_result`, ordered
`input_artifact_states`, ordered `output_artifact_states`, ordered
`preserved_tail_artifacts`, `admission`, `outcome`, optional `primary_failure`, ordered
`cleanup_failures`, `failure_closure: RecordRef`, `ended_at`, `producer`, and `content_hash`.

Result, recording-session, and sink-session identities are `Uuid`; `request`
is the exact recovery-request `RecordRef` and closes over destination, action,
request identity, and any discard authorization independently of caller memory.
`input_state_ledger` exactly equals the request's reference.
`output_state_ledger` is prohibited before admission and otherwise required; it
equals the input reference when no history changed and otherwise names the
greatest valid successor created by the action before result serialization.
`ended_at` is canonical `ObservationTiming` not earlier than the resolved
request in a comparable receipt domain.
`failure_closure` is the acquisition-scope snapshot created after this action's
primary and cleanup evidence is fixed. Every failure copied by the recovery
result occurs byte-identically in that closure, and the matching later sink and
acquisition aggregates must resolve a closure having this snapshot as an exact
failure-array prefix.

Each member of `input_artifact_states` and `output_artifact_states` is an
`ArtifactStateHistory` with exact properties `artifact_id: Uuid`,
`artifact_ordinal: UInt63`, `role: Identifier`, optional
`relative_path: NfcText(2048)`, and ordered
nonempty `states: ArtifactState[]`. Artifact ordinal zero is the graph root;
every root/member identity receives the next gap-free ordinal when it is first
preallocated for that sink, before any byte write. Role and path equal the
matching input/output artifact-state-ledger entry, every state repeats
`artifact_id`, and the history's `artifact_ordinal`. The states are the exact complete sequence
from zero through the history's final state with no gap, duplicate, omission,
or later state. Thus a history is not a caller-selected latest-state summary.
When present, relative path obeys the archive's canonical relative-POSIX path
rules; it is absent exactly for a root without a member path.

After request admission and before content validation or mutation, the input
array is byte-identically the ordered entries of `input_state_ledger`. The
output array is byte-identically the entries of `output_state_ledger`. They
therefore contain every root and member artifact in ordinal order, including
unchanged, open, checkpoint, payload, content-manifest, and prior recovery-
created artifacts. For each pre-existing artifact the input history is an
exact prefix of its output history; it is byte-identical when no state was
appended. Every new output history starts at state sequence zero. No root or
member in the proven ledger head may be omitted, renumbered, or replaced in
either applicable array. When `prior_recording_result` is present,
it is the latest matching immutable recording result and, after grouping its
sink result's complete artifact states by artifact ID and state sequence, each
group is an exact prefix of the matching input history. Every selected-
checkpoint root/member identity resolves to the matching input history, and
its recorded byte state equals a prefix endpoint of that history.
For an admitted action, presence is biconditional: the property is required
when any matching prior recording result exists and prohibited when recovery
follows a crash before one was created. A pre-admission failure prohibits it
because the descriptor/sink relation was not established.

Each `PreservedTailArtifact` has exact properties
`preservation_sequence: UInt63`, `source_artifact_id: Uuid`,
`source_state_sequence: UInt63`, `source_start_offset: UInt63`,
`source_end_offset_exclusive: UInt63`, `source_range_sha256: Sha256`,
`tail_artifact_id: Uuid`, `destination: DestinationIdentity`,
`tail_relative_path: NfcText(2048)`,
`byte_length: UInt63`, `sha256: Sha256`, `relationship_id: Uuid`, and
`output_state_sequence: UInt63`. It identifies the source input history's
latest byte state. For an open member named by the selected checkpoint, start
is its safe byte length; for an existing member absent from that checkpoint,
start is zero. End is the input byte length, start is strictly less than end,
and `byte_length` is their difference. The two hashes equal SHA-256 of exactly
that source half-open byte range and the byte-identical sealed tail artifact.
`destination` byte-identically equals the admitted recovery request's
destination. `tail_relative_path` is exactly
`recovery/tails/<preservation-sequence>-<tail-artifact-id>.bin`, with sequence
rendered as twenty zero-padded decimal digits and UUID in canonical lowercase;
it is independent of caller/path enumeration. The matching new output history
has role `xplane_fdau.recovery.preserved_tail` and this exact path.
`relationship_id` preallocates the
later content-manifest `recovery_of` edge from tail to source, and
`output_state_sequence` names the tail history's final sealed state.

The preserved-tail array is the exhaustive sequence of successfully sealed
nonempty tails, ordered by source artifact ordinal with contiguous
`preservation_sequence` from zero. It is empty when no such range exists. Each
entry has exactly one new output history and each sealed recovery-tail output
history has exactly one entry. On `tail_preservation_failed`, all tails sealed
before the failure remain listed and immutable; an incompletely created tail
still appears in output history but not in this array, every source remains
unmodified, and the failed result uses that failure as its recovery-domain
eligible primary.

Before reading content for mutation, changing bytes, deleting a path, or
appending an artifact state, recovery validates in order: request canonical
bytes and self-hash; descriptor reference; recording-, sink-, and root-session
identities; destination equality; input-ledger reference and exhaustive
reserved-namespace chain; `supports_recovery`; action against the declaration's
immutable recovery policy; and discard authorization. A mismatch
returns a `failed` recovery result with both artifact-state arrays and the
preserved-tail array empty, because artifact-state admission was not reached,
prohibits `output_state_ledger`, selected checkpoint, and prior recording
result, and carries the first applicable recovery failure. Request UUID reuse with
different content is `descriptor_mismatch`. A false recovery capability is
`recovery_unsupported`; a disallowed policy/action pair is
`policy_action_prohibited`; and unequal or absent discard authority is
`discard_unauthorized`. An invalid, incomplete, non-greatest, or identity-
mismatched ledger chain is `ledger_chain_invalid`.

After those admission checks, recovery freezes the exhaustive input histories
from the admitted ledger and fixes `output_state_ledger` to the input head
until a later ledger append succeeds. Any checkpoint/current-content validation
failure before tail creation or source mutation has output histories byte-identical to
input histories and an empty preserved-tail array. A failed admitted action
therefore has nonempty equal arrays unless tail creation began; a pre-admission
failure has both arrays empty. These are the only conditions under which an
artifact-state array may be empty.

The policy/action matrix is closed:

| Declared `recovery_policy.mode` | Permitted request action | Additional admission rule |
| --- | --- | --- |
| `preserve_partial` | `preserve` only | no checkpoint required |
| `discard_partial` | `discard` only | request authorization exactly equals the policy's embedded authorization |
| `recovery_required` | `resume` or `finalize_partial` | `resume` requires checkpoint support; finalization follows the checkpoint rule below |

Every other pair fails with `policy_action_prohibited`. `preserve` and
`discard` are prohibited under `recovery_required`; a caller cannot override
the declaration by supplying an authorization.

`admission` is `admitted` or `rejected`; `outcome` is `resumed`,
`finalized_partial`, `preserved_partial`, `discarded`, or `failed`. Their exact
wire-presence matrix is:

| `outcome` | Required request action and admission | `selected_checkpoint` | Ledger/state-array rule | `primary_failure` |
| --- | --- | --- | --- | --- |
| `resumed` | `resume`, `admitted` | required | output ledger required; both state arrays nonempty | prohibited |
| `finalized_partial` | `finalize_partial`, `admitted` | required exactly when checkpoint capable | output ledger required; both state arrays nonempty | prohibited |
| `preserved_partial` | `preserve`, `admitted` | optional and present exactly when a checkpoint was selected | output ledger required; both state arrays nonempty | prohibited |
| `discarded` | `discard`, `admitted` | prohibited | output ledger required; both state arrays nonempty | prohibited |
| `failed` | any action; `rejected` before admission or `admitted` afterward | prohibited when rejected; otherwise present exactly when selected before failure | output ledger and both arrays prohibited/empty when rejected, and required/nonempty when admitted | required |

No other outcome/action/admission/property-presence combination is valid. An
admitted `resume` or checkpoint-capable `finalize_partial`
validates the contiguous self-hashed checkpoint chain, member bytes, safe
record prefixes, and complete referenced-content closure in checkpoint order,
then selects its highest valid consistent cut. `preserve` applies that order to
each contiguous prefix and selects the highest valid prefix; a missing/invalid
suffix is a content-manifest limitation rather than action failure because no
cut is required.
Every sealed member must match.
Every open member must be at least the recorded safe length and have the exact
safe-prefix hash. A shorter or mismatched member fails closed without mutation.
Bytes after a valid safe prefix and members not named by the checkpoint are
preserved under new tail-artifact UUIDs before a resume/finalize source is
truncated; they are never silently discarded.

Every successful action outcome prohibits `primary_failure`; `failed` requires
the smallest recovery-action-eligible causal failure under the global table.
Cleanup failures are permitted for any outcome and never rewrite a successful
primary action into `failed` after its irreversible state change.

Successful action state effects are exact. `preserve` carries every non-root
byte-member input history byte-identically into output and has no preserved
tails.
It creates exactly one new sealed recovery content-manifest history that
inventories the preserved graph without replacing any prior candidate content
manifest, then appends one `preserved_partial` root state whose content is the
unchanged root bytes or that new content-manifest reference. No other pre-
existing history changes. `discard` has no tails and appends one `discarded`
state to every input artifact after deletion succeeds; each state carries the
request's exact authorization and absent content. A checkpoint-incapable
`finalize_partial` has no tails and appends the exact
sealed/preserved-partial terminal states for the validated untruncated bytes.
For checkpoint-based `resume` and `finalize_partial`, every nonempty byte range
after the selected cut is represented by exactly one preserved tail before any
source change. Resume then appends the profile-selected open/sealed state at
the cut to each affected original artifact; finalization appends terminal
`preserved_partial` states at that cut to affected byte artifacts. Unchanged
artifacts retain identical histories. Every successful `finalize_partial`
additionally creates exactly one new sealed recovery content-manifest history
after all member states are final, then appends the terminal logical-root
`preserved_partial` state referencing that record; a byte-addressable root
instead carries its final byte hash in its terminal state and the generic final
manifest references the recovery content manifest separately. No successful
action leaves an unlisted recovery-created artifact.

The remaining failure frontiers are closed. Failure while creating preserve's
recovery content manifest leaves all input histories unchanged, includes the
new incomplete manifest history in output, and has no tail entry. Failure while
discarding appends `discarded` only for the deletion-order prefix whose deletion
succeeded, leaves the remaining histories unchanged, and has no tails; its
eligible primary uses phase `recover` and code `cleanup_failed`, while later
best-effort cleanup failures use phase `cleanup`. Validation, tail creation,
and any recovery content-manifest candidate are completed before resume or
finalize mutates an existing source. Once all selected source states have been
irreversibly changed, publication of their terminal states and the staged
recovery content manifest is one required atomic result step; a sink unable to
guarantee it fails admission before source mutation. The action then retains
its successful outcome and any later failure is cleanup evidence. These rules,
plus pre-admission empty arrays, admitted no-mutation equality, and the tail-
failure rule, exhaust every action/outcome array shape.

`resume` requires `supports_checkpoint: true` and selects the highest valid
consistent checkpoint. `finalize_partial` also selects the highest valid
checkpoint when checkpoint support is true. If no valid checkpoint exists for
either action, the outcome is `failed` with `checkpoint_chain_invalid`, bytes
and prior artifact states remain unchanged, and no tail artifact is created.
When `supports_checkpoint` is false, `resume` is
`recovery_unsupported`; `finalize_partial` instead validates the complete
current byte-artifact length, SHA-256, safe record boundary, and reference
closure fixed by the sink profile, then seals those exact untruncated bytes.
Failure is `current_state_invalid` with no mutation.

Accordingly, `selected_checkpoint` is required for `resume` and for
checkpoint-capable `finalize_partial`, prohibited for checkpoint-incapable
`finalize_partial` and `discard`. For `preserve`, it is present exactly when at
least one independently valid checkpoint exists and names the highest such cut;
it is absent exactly when none exists. `preserve` never fails solely because a
checkpoint is absent or invalid and performs no byte mutation.
Outcomes correspond exactly to resolved request actions: successful `resume`,
`finalize_partial`, `preserve`, and `discard`
produce `resumed`, `finalized_partial`, `preserved_partial`, and `discarded`,
respectively; any unsuccessful action produces `failed`.

`resume` continues the same root and member UUIDs from the selected cut.
`finalize_partial` seals recoverable evidence with disposition
`preserved_partial`; a canonical archive uses the `.fdau.incomplete` suffix,
never `.fdau`, and another sink uses only an incomplete destination form fixed
by its profile. It never makes a completed-acquisition or lossless claim.
`preserve` performs no mutation of pre-existing bytes; its new content
manifest follows the exact rule above. `discard` records the exact authorization
and deletion cleanup outcome. A crash may precede any recording result, so the
prior-result presence rule above represents both cases. Existing checkpoints, results, and
artifact states remain immutable; recovery appends new states and never
rewrites historical terminal evidence.

## Artifact manifests and recording result

`ArtifactContentManifest` is the prepublication content root for one artifact
graph. It has `content_manifest_id`, `recording_session_descriptor`, `sink_session_id`,
`root_artifact_id`, `acquisition_session_descriptor`, `resolution`, ordered
`source_contexts`, ordered `continuity_reports`, ordered `artifacts`, ordered
`relationships`, `close_context`, `recovery_context`,
`data_classification`, ordered `limitations`, `producer`, and `content_hash`.
One content manifest describes exactly one sink candidate graph, not the whole
fan-out transaction or its later terminal status.

`close_context` is tagged by `kind`. Kind `configuration_boundary` contains
`boundary_event: RecordRef`, `prior_configuration: RecordRef`,
`replacement_configuration: RecordRef`, and literal reason
`configuration_replaced`; it exactly copies the commit request's
configuration-replaced close boundary. Kind `stopping_intent` contains
`stopping_event: RecordRef`, `requested_termination_reason`, and optional
`initiating_failure`, all exactly copied from the acquisition stopping event.
It is the truthful source-delivery close input available before this sink's
commit/publication attempt; it never predicts the later activity terminal
result. Kind `interrupted` contains `request: RecordRef`, literal close reason
`interrupted_before_terminal`, and optional `primary_failure`; it is permitted
only for a recovery-created partial manifest when no terminal event exists,
and its request equals the recovery-context request. Thus content serialization
records its available close input without fabricating an acquisition terminal
event.

`recovery_context` is tagged by `kind`. `not_recovered` has no other property.
`resumed` contains `request: RecordRef` and
`selected_checkpoint: RecordRef`. `finalized_partial` contains the request and
requires selected checkpoint exactly for a checkpoint-capable sink, while a
checkpoint-incapable sink prohibits it. `preserved_partial` contains the
request and optional selected checkpoint. Request and checkpoint families are restricted
accordingly, their sink/root/session identities equal this content manifest, and the
resolved request action maps `resume` to `resumed`, `finalize_partial` to
`finalized_partial`, and `preserve` to `preserved_partial`. A discarded graph
has no content manifest.
These fields snapshot close/recovery input already fixed before content-manifest
serialization; they do not claim the later recovery or activity outcome.

Each `ArtifactEntry` has exact properties, in semantic order,
`artifact_id: Uuid`, `role: Identifier`, `media_type: NfcText(255)`, optional
`relative_path: NfcText(2048)`, `content_state: ArtifactContentState`, optional
`schema_version: UInt63`, optional `record_ref: RecordRef`,
`producer: ProducerIdentity`, `created_at: UtcInstant`, optional
`finalized_at: UtcInstant`, ordered `scopes: ArtifactScope[]`, and ordered
`definitions: DefinitionRef[]`.
`relative_path` is required for a graph member and prohibited only when the
root artifact is itself one byte-addressable external file. Artifact entries
are unique by ID and path. The content manifest inventories every created or
policy-omitted member of this sink graph.

`created_at` and `finalized_at` are `UtcInstant` artifact metadata. They do not
establish runtime causal order; lifecycle events, checkpoints, and phase
attempts carry that evidence.

`ArtifactContentState` is a tagged object whose discriminant is `kind`; the
following table is the complete wire inventory. All unlisted properties and
properties from another row are prohibited.

| `kind` | Exact properties in semantic order | Outer-entry presence rules |
| --- | --- | --- |
| `sealed` | `kind: "sealed"`, `byte_length: UInt63`, `sha256: Sha256` | `finalized_at` required; `record_ref` present exactly for a complete self-hashed record |
| `preserved_partial` | `kind: "preserved_partial"`, `byte_length: UInt63`, `sha256: Sha256`, `recovery_eligible: Boolean`, `failure: FailureEvidence` | `finalized_at` required; `record_ref` prohibited |
| `omitted_by_policy` | `kind: "omitted_by_policy"`, `retention_policy: DefinitionRef`, `omission_disposition: enum` | `finalized_at` and `record_ref` prohibited; enum is exactly `normalized` or `projected` and equals the resolved policy |

- `schema_version` is present exactly for an artifact serialized under a
  versioned schema and is prohibited otherwise. `record_ref` is present
  exactly when the complete artifact is one self-hashed contract record.
- Each `scopes` entry is a tagged value with kind `stream`, `epoch`,
  `source_acquisition`, `provider_audit_evidence`, `source_generation`,
  `connection_generation`, or `delivery_generation` and the corresponding
  UUID or `UInt63` value. Scope entries are an `ArraySet` in kind-then-value
  order. `definitions` is an `ArraySet<DefinitionRef>` in
  canonical definition-reference order.
- Byte length and SHA-256 occur only inside the sealed or preserved-partial
  tagged state. Failure and recovery eligibility occur only inside
  preserved-partial; retention policy and omission disposition occur only
  inside omitted-by-policy. Their presence is biconditional with the selected
  `kind`. `recovery_eligible` is true exactly when the declaration permits a
  later recovery action and the required ledger/checkpoint closure exists; it
  is false otherwise and is never inferred from a filename.

`data_classification` is `unspecified`, `public`, `internal`, `sensitive`, or
`restricted`. It is an operator data-handling classification only and never a
claim of statutory protection, privilege, or regulatory compliance. It is
byte-identically the matching sink declaration's immutable value.

Each relationship has `relationship_id: Uuid`, `kind`, `from`, and `to`.
Endpoints are `ArtifactLocator` values: a local locator contains
`scope: "local"` and this content manifest's root or member artifact ID, while
an external locator contains `scope: "external"`, another
artifact-content-manifest `RecordRef`,
and its root or member artifact ID. `kind` is `parent`, `projection_of`,
`derived_from`, `corroborates`, `replay_source`, `recovery_of`,
`provider_audit_for`, `transition_predecessor`, or `related_to`. `from` is the
subject and `to` is its object: a child points to its parent, a projection or
derivation to its source, a corroborating artifact to what it corroborates, a
replay artifact to its source, and a recovery-created artifact to its source.
An audit byte artifact points by `provider_audit_for` to the local evidence
JSONL member. The matching provider-audit closure fixes the exact record index
and `RecordRef`; payload identity and source-acquisition/evidence scopes agree.
A `transition_predecessor` points from the local continuity-report artifact to
the exact prior external content-manifest root and equals the report closure's
planned current link's preallocated relationship ID; an unavailable current
link creates no such relationship.
For recovered content, the `recovery_of` relationships are exactly the
matching recovery result's preserved-tail entries: each entry's preallocated
relationship ID occurs once, from its tail artifact to its source artifact,
with no additional or missing tail relation. Tail byte length/SHA-256 and the
manifest entry's finalized content state equal the corresponding output
history and preserved-tail entry.
`related_to` is symmetric and stores the lexically smaller canonical locator
first. Directed relationships cannot self-reference. `parent`,
`projection_of`, `derived_from`, `replay_source`, `recovery_of`,
`provider_audit_for`, and `transition_predecessor` must be acyclic within the
supplied closure.

An embedded content manifest inventories every archive member except its own
serialized bytes. `root_artifact_id` may also identify a byte-addressable
entry, but a logical directory root has no invented directory-byte hash. The
content manifest does not inventory the later sink, recording, or recovery
result. Its close-boundary and recovery-request/checkpoint references are
already immutable and contain no back-reference to this content manifest,
avoiding self-referential file hashes and publication-status cycles. Its
`content_hash` uses the approved root
self-hash rule; its serialized byte length and SHA-256 are reported later by
the owning sink result.

For a byte-addressable root, this record is a required generic sidecar rather
than bytes embedded in the root. When the matching publication disposition is
`published`, its `artifacts` array contains exactly one local root
`ArtifactEntry` with that root UUID, the sink declaration's exact role, the
produced media type and schema metadata, absent `relative_path`, and a
`sealed` content state whose byte length/SHA-256 equal both the final sealed
candidate state and the later `published` root state. Every published byte
root requires this completed sidecar.

When the matching disposition is `preserved_partial` and that byte-root
result completed a content manifest, the local root identity and outer-entry
metadata follow the published rule, but its content state is
`preserved_partial`, not `sealed`. Its byte length and SHA-256 equal the latest
root state in both the pinned ledger and `publication.artifact_states`; its
`recovery_eligible` value is derived by the general content-state rule above;
and its `failure` is byte-identically the publication failure and the
`SinkResult.primary_failure`, which is mandatory for this runtime-failure
partial row. There is no later `published` root state to compare. Within an
ordinary `SinkResult`, these published and preserved-partial disposition cases
are the only byte-root content-state choices for a completed sidecar.

The sidecar also inventories every created sidecar member other than the
content manifest's own serialized bytes. A native-FDR projection sidecar
additionally contains exactly one `projection_of` relationship from the local
byte-root entry to the external root resolved through the projection report's
input artifact manifest. The relationship can be fixed from immutable
projection inputs before publication. The later final artifact manifest, not
this prepublication content root, references and cross-checks the already-
created projection report, so neither record points to a later record and no
self-reference is introduced.

For an ordinary commit, `continuity_reports` exactly equals the commit request's
singleton report and that report is a sealed one-record artifact entry in this
graph. For a recovery-created content manifest, it instead contains every
continuity report reachable in the selected checkpoint or validated current
referenced-content closure, in configuration order, and is empty when the crash
preceded any such report; recovery never fabricates one. The descriptor,
resolution, source contexts, available reports, artifact scopes, delivery
events, and limitations carry the parent architecture's requested and observed
sampling, source, generation, gap, drop, and discontinuity inventory available
at content finalization.
The content manifest carries only close/recovery input. The final
`ArtifactManifest` below records delivered publication, recovery, and
activity-terminal status and joins by exact record and artifact identities.

`ArtifactManifest` is the delivered integrity/status root. Its exact
properties are `artifact_manifest_id: Uuid`,
`acquisition_session_descriptor: RecordRef`,
`recording_session_descriptor: RecordRef`, `sink_session_id: Uuid`,
`root_artifact_id: Uuid`, `artifact_state_ledger: RecordRef`, optional
`content_manifest: RecordRef`, optional `recording_result: RecordRef`, optional
`recovery_result: RecordRef`, ordered `projection_reports: RecordRef[]`,
`data_classification`, `termination_status`, `recovery_status`, `publication_status`,
`failure_closure: RecordRef`, `delivered_at: ObservationTiming`, `producer`, and
`content_hash`.
Descriptor, sink, root, and every supplied result/content reference agree.
`artifact_state_ledger` always names an equal-descriptor/sink/root
artifact-state-ledger record. For terminal status it byte-identically equals
the matching `SinkResult.artifact_state_ledger`; for interrupted status it
equals the admitted recovery result's required `output_state_ledger`. A
terminal manifest that also names an earlier recovery result requires that
result's output head and histories to be exact prefixes of this head. The
ordinary publication's flattened `artifact_states`, or the interrupted
recovery result's ordered `output_artifact_states`, is byte-identical to this
head's complete entries under the applicable flattening/history shape.
`data_classification` is always required, uses the five-value closed vocabulary
above, and equals the matching sink declaration. When a content manifest is
present it also equals that record; when content is absent it remains the
authoritative operator classification rather than becoming unknown or omitted.
When `content_manifest` is present, its complete transitive entries,
relationships, sampling summaries, limitations, and recovery context are the
content portion of this generic manifest. It is present exactly when the
matching sink result names a completed content manifest or the matching
recovery output contains its final sealed recovery content-manifest history.
It is prohibited for discarded, never-created, or admitted-failed recovery
that completed no content manifest; the final status carries the exact root
history and its resolved recovery result carries the exhaustive ledger-backed
output histories.

`projection_reports` contains every already-fixed
`XPlaneFDRProjectionReport` in the matching terminal or recovery closure whose
`output_artifact` equals this root, in projection-start order, and no other
report. For terminal status it is byte-identically the matching
`SinkResult.projection_reports`; for interrupted status it equals the matching
prior `SinkResult.projection_reports` equal-root subsequence when
`recording_result` is present, and is empty when that prior result is absent.
Recovery does not invent a link to a projection report that was not closed by a
prior recording result. It is empty when no projection produced the root. A
terminal `xplane_fdau.sink.xplane_fdr_projection` result with publication disposition
`published` requires exactly one entry; that report's recording session,
output artifact, profile, and failure scope equal the descriptor/sink closure,
and its outcome is `completed` or `completed_with_loss`. Resolving the report's
`input_manifest` supplies its input content-manifest/root identity. The output
content manifest must then contain the exact local root `ArtifactEntry` and
exactly one `projection_of` relationship from that root to that external input
root. This report reference, artifact identity, and relationship equality make
portable validation of that final manifest close the native projection
provenance.

`termination_status` is tagged by `kind` with this complete wire table:

| `kind` | Remaining exact properties in semantic order | Invariants |
| --- | --- | --- |
| `terminal` | `terminal_event: RecordRef`, `termination_reason`, optional `primary_failure: FailureEvidence` | event is the equal-session acquisition terminal event and reason/failure equal it |
| `interrupted` | `recovery_result: RecordRef`, literal `reason: "interrupted_before_terminal"`, optional `primary_failure: FailureEvidence` | permitted only when no acquisition terminal exists; failure presence/value equals the recovery result |

All cross-row properties are prohibited. Terminal status requires
`recording_result`; interrupted status requires `recovery_result` and permits a
prior recording result only when that record exists.
`failure_closure` equals the terminal event's final acquisition-scope closure
for terminal status and the recovery result's closure for interrupted status.
Every copied status/publication failure must occur byte-identically in it.

`recovery_status` is tagged by `kind`; all unlisted properties are prohibited:

| `kind` | Remaining exact properties in semantic order | Invariants |
| --- | --- | --- |
| `not_recovered` | — | no recovery result exists for this terminal output |
| `resumed` | `recovery_result: RecordRef`, `selected_checkpoint: RecordRef` | result outcome is resumed and checkpoint equals it |
| `finalized_partial` | `recovery_result: RecordRef`, optional `selected_checkpoint: RecordRef` | result outcome is finalized-partial; checkpoint presence equals it |
| `preserved_partial` | `recovery_result: RecordRef`, optional `selected_checkpoint: RecordRef` | result outcome is preserved-partial; checkpoint presence equals it |
| `discarded` | `recovery_result: RecordRef` | result outcome is discarded and has no selected checkpoint |
| `failed` | `recovery_result: RecordRef`, optional `selected_checkpoint: RecordRef` | result outcome is failed with admission admitted; checkpoint presence equals it |

`resumed` is prohibited with interrupted termination and produces no immediate
final manifest; it is required in the later terminal artifact manifest after
the resumed recording terminates.

For terminal status, `publication_status` is byte-identically the complete
matching `SinkResult.publication` value and therefore uses the six-row
`SinkPublicationDisposition` table. For interrupted recovery it is a distinct
`RecoveryPublicationDisposition` tagged by `disposition` and begins with that
property plus `destination: DestinationIdentity`:

| `disposition` | Remaining exact properties in semantic order | Invariants |
| --- | --- | --- |
| `preserved_partial` | `root_history: ArtifactStateHistory`, `completed_at: ObservationTiming`, ordered `cleanup_failures: FailureEvidence[]` | recovery outcome is finalized-partial or preserved-partial; root history is output-ledger ordinal zero and ends preserved-partial |
| `discarded` | `root_history: ArtifactStateHistory`, `authorization: DeletionAuthorization`, `completed_at: ObservationTiming`, ordered `cleanup_failures: FailureEvidence[]` | recovery outcome is discarded; root history ends discarded and authorization equals the request |
| `recovery_failed` | `root_history: ArtifactStateHistory`, `failure: FailureEvidence`, `completed_at: ObservationTiming`, ordered `cleanup_failures: FailureEvidence[]` | recovery was admitted and failed; root history equals output-ledger ordinal zero and failure equals the recovery primary |

Destination equals the request, completed time equals recovery `ended_at`, and
cleanup arrays equal the recovery result. Unlisted and cross-row properties are
prohibited. The resolved recovery result supplies every non-root output history;
the status never predicts an operation that has not completed.

The matching `RecoveryOutcome.artifact_manifest` is byte-identically this
manifest. It is required for finalized, preserved, discarded, and admitted-
failed recovery, and prohibited for resumed or pre-admission failed recovery.
An admitted failed result is terminal for that recovery invocation and records
the unchanged or tail-creation output graph; a later retry is a new immutable
recovery request and cannot rewrite this status record.

For an ordinary session the orchestrator creates one final artifact manifest
per recording sink, in recording-result then sink order, only after the
recording result and terminal event exist. For terminal crash recovery it
creates one after the recovery result, subject to the exact admitted-action
rule above. The manifest never inventories its own
serialized bytes and neither predecessor references it. It is delivered as a
transport-free result record: optional later persistence is a new external
artifact operation whose failure cannot rewrite the already fixed activity or
manifest. This order preserves content-root no-replace publication and all
self-hashes without a cycle.

`RecordingSessionResult` is generated after every sink reaches a terminal
state, after an acquisition-scope failure-closure snapshot is fixed, and before
the acquisition terminal event. It is returned to the caller
and may be persisted as a separate related contract artifact; it is never
inserted retroactively into an immutable sink graph. It has
`recording_result_id`, `recording_session_id`, `descriptor`,
`close_boundary`, `outcome`, `termination_reason`, optional `primary_failure`, ordered
`cleanup_failures`, `failure_closure: RecordRef`, ordered `sink_results`,
`ended_at`, `producer`, and `content_hash`. It contains no continuity-report reference, final artifact
manifest, or aggregate archive-publication field.

`recording_result_id` and `recording_session_id` are `Uuid`; `descriptor` is
the equal-session recording descriptor `RecordRef`; `close_boundary` is
byte-identically the configuration-replaced or acquisition-stopping boundary
fixed before every sink's commit or abort operation; `ended_at` is canonical
`ObservationTiming` not earlier than every sink's terminal phase in a
comparable receipt domain.
`failure_closure` is the acquisition-scope snapshot created after all nested
sink, recovery, phase, primary, and cleanup failures in this result were fixed;
those copies all occur byte-identically in the closure.

Each `SinkResult` has `sink_session_id`, `criticality`, `outcome`,
`artifact_state_ledger: RecordRef`, optional `content_manifest`, optional
`content_manifest_file`, `publication`, ordered `projection_reports: RecordRef[]`, `delivery_summary`,
ordered `recovery_results`, ordered `phase_attempts`, optional `primary_failure`, and ordered
`cleanup_failures`.

- `outcome` is `successful`, `partial`, or `failed`.
- `criticality` must exactly match the declaration. `primary_failure` is
  prohibited for success and required for failure. For partial it is required
  when runtime failure caused the partial output and prohibited when declared
  loss/retention policy alone caused it. When present it is the smallest
  sink-local eligible causal sequence; this local rule is unchanged when the
  sink is optional to its enclosing recording session.
- `artifact_state_ledger` is the exact ordinary terminal head admitted from the
  exhaustive live reserved namespace after the final artifact-state append and
  before this result is serialized. Its descriptor, sink, and root equal the
  enclosing recording descriptor and sink declaration. Flattening every entry's
  complete state history in artifact-ordinal then state-sequence order is
  byte-identical to `publication.artifact_states`; no planned, pathless,
  unchanged, discarded, or failed-to-create allocation may be omitted.
- `content_manifest` is present exactly when a content manifest was completed.
  `content_manifest_file` then records its serialized byte length and SHA-256
  and is otherwise prohibited.
- `projection_reports` contains every already-fixed
  `XPlaneFDRProjectionReport` whose output artifact is this root, in projection-
  start order, and is empty when none exists. A native-FDR projection sink's
  published disposition requires exactly one completed or completed-with-loss
  report; every other current sink kind requires an empty array.
- `publication` is one exact `SinkPublicationDisposition` tagged by
  `disposition`. Every row begins with `disposition` and
  `destination: DestinationIdentity`; all unlisted or cross-row properties are
  prohibited:

  `published_loss` is true exactly when the completed content graph contains an
  `ArtifactEntry` with content state `omitted_by_policy`, a matching continuity
  report contains a `missing` provider-audit closure entry or a dropped,
  detached, or failed delivery for this sink, or a matching entry in
  `projection_reports` has outcome `completed_with_loss`. It is false otherwise.

  | `disposition` | Remaining exact properties in semantic order | Exact latest-state invariant | Content-manifest rule | Required `SinkResult.outcome` |
  | --- | --- | --- | --- | --- |
  | `published` | ordered nonempty `artifact_states: ArtifactState[]`, `completed_at: ObservationTiming`, ordered `cleanup_failures: FailureEvidence[]` | latest root state is `published`; no `failure` or `authorization` | required for both logical and byte roots | `partial` exactly when `published_loss`; otherwise `successful`; `failed` prohibited |
  | `preserved_partial` | ordered nonempty `artifact_states: ArtifactState[]`, `failure: FailureEvidence`, `completed_at: ObservationTiming`, ordered `cleanup_failures: FailureEvidence[]` | latest root state is `preserved_partial`; failure is the matching runtime cause | present exactly when the partial graph completed one | `partial` |
  | `discarded` | ordered nonempty `artifact_states: ArtifactState[]`, `failure: FailureEvidence`, `authorization: DeletionAuthorization`, `completed_at: ObservationTiming`, ordered `cleanup_failures: FailureEvidence[]` | latest state of every allocated artifact is `discarded`; each disposition evidence copies authorization | prohibited | `failed` |
  | `not_created` | ordered nonempty `artifact_states: ArtifactState[]`, `failure: FailureEvidence`, `completed_at: ObservationTiming`, ordered `cleanup_failures: FailureEvidence[]` | every allocated history contains exactly its state-zero `planned` state; no byte-bearing state exists | prohibited | `failed` |
  | `omitted_by_policy` | ordered nonempty `artifact_states: ArtifactState[]`, `retention_policy: DefinitionRef`, `completed_at: ObservationTiming`, ordered `cleanup_failures: FailureEvidence[]` | only root ordinal zero is allocated and it contains exactly its state-zero `planned` state; no `failure` or `authorization` | prohibited | `partial` |
  | `not_applicable` | ordered nonempty `artifact_states: ArtifactState[]`, `completed_at: ObservationTiming`, ordered `cleanup_failures: FailureEvidence[]` | sink declares `publishes_artifact: false`; only root ordinal zero is allocated and it contains exactly its state-zero `planned` state; no failure, policy, or authorization | prohibited | `successful` |

  Destination byte-identically equals the declaration. Artifact states contain
  every allocated artifact's complete state history flattened in artifact-
  ordinal then state-sequence order, with no gap or extra state, and equal the
  entries of `artifact_state_ledger` as specified above. Publication
  cleanup failures are exactly the publication/cleanup-phase subsequence of the
  enclosing sink cleanup array and are byte-identical there and in its failure
  closure. The disposition, content-manifest presence, and sink outcome are
  valid exactly in the table's row; no combination outside it is accepted.
  `content_manifest_file` follows the same presence rule. Published-with-
  cleanup-failure remains `published` and cleanup evidence does not change the
  row's outcome.

  `omitted_by_policy.retention_policy` byte-identically equals the sink
  declaration's top-level retention-policy reference and resolves to
  `RawRetentionPolicy`; the row is permitted only for a retention-capable sink
  when that policy has `canonical_samples: omit`, `canonical_frames: omit`,
  and `not_requested` for accepted raw observations, raw payloads, and provider
  audit, with its required omission disposition. No protected item may require
  this sink to retain an axis. If the policy retains any axis, the sink must
  instead publish or preserve a content manifest whose exact intentionally
  omitted members use `ArtifactContentState.omitted_by_policy`.
- `delivery_summary` contains ordered `stream_summaries`; each has exact
  `endpoint_id`, `stream_id`, optional first/last delivery-event references,
  `next_delivery_sequence`, and delivered, dropped, detached, and failed
  counts. Entries are exactly the matching sink projection of the fan-out
  tuple universe in descriptor stream order and equal the report/commit range
  ends. Empty stream delivery prohibits both references and uses sequence zero;
  otherwise references close the inclusive endpoint-plus-stream range and next
  sequence is last plus one. It summarizes append calls without an
  endpoint-only sequence or unbounded list of per-append outcomes.
- `recovery_results` contains every recovery-result `RecordRef` for this sink
  in request-acceptance order and is empty when no recovery was attempted. The
  acquisition result contains the same records in its cross-sink total order.
- `phase_attempts` contains at most one ordered summary for each attempted
  `open`, `checkpoint`, `commit`, `abort`, `recover`, and `close` phase.
  Unattempted phases are omitted, not reported as successful.
- Sink outcome is derived only by the closed publication table: a loss-free
  published graph or nonpublishing `not_applicable` result is successful;
  published loss, preserved partial, or whole-output policy omission is
  partial; and discard or failure-driven noncreation is failed.

- `RecordingSessionResult.outcome` is `successful`, `partial`, or `failed`.
- Recording outcome derivation is this closed table:

  | Sink/orchestrator condition | `RecordingSessionResult.outcome` |
  | --- | --- |
  | Every sink is `successful` and no non-cleanup recording-orchestrator failure makes the aggregate fail | `successful` |
  | At least one required sink is `failed`; at least one required sink is runtime-failure `partial` and therefore carries `primary_failure`; or a non-cleanup recording-orchestrator failure independently makes the aggregate fail | `failed` |
  | No failed-row condition applies, and at least one sink is `partial` or one optional sink is `failed` | `partial` |

  These rows are exhaustive because every descriptor has at least one sink.
  In particular, a required sink that is `partial` solely because of declared
  retention/loss policy has no sink primary and selects the aggregate
  `partial` row, not `failed`. It does not manufacture either sink or
  recording-orchestrator failure evidence.
- A partial recording result prohibits aggregate `primary_failure`; all
  optional-sink failures remain in their sink results. A failed recording
  result requires the smallest eligible required-sink or orchestrator failure
  fixed by the table below. Thus a causally earlier optional-sink failure never
  displaces the required failure that selected the aggregate failed outcome.
- `termination_reason` is `consumer_complete`, `consumer_stop`, `source_end`,
  `configuration_replaced`,
  `required_evidence_unsatisfied`, `required_sink_failed`,
  `discontinuity_policy`, `explicit_abort`, `recovery_pending`, or
  `internal_failure`. It equals the close-boundary reason unless the aggregate
  failed row is selected by a required sink that is `failed` or runtime-
  failure `partial`, which selects `required_sink_failed`; a required declared-
  loss-only partial and an optional publication conflict retain their sink
  evidence without replacing the requested reason. Its outcome, reason, and
  failure are therefore available for the later acquisition terminal event
  without backward mutation.

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
`causal_position`, `record_ref: RecordRef`, `artifact_id: Uuid`, `path`, and
`diagnostic: NfcText(1024)`. `causal_position` has exact
`causal_scope_id: Uuid` and `causal_sequence: UInt63`. `path` is an RFC 6901 pointer and is present only
when failure concerns a contract property. Record and artifact references are
present whenever the failed operation had already bound those identities and
are otherwise omitted. `phase` is one of `resolve`, `open`, `observe`,
`normalize`, `deliver`, `evaluate`, `append`, `checkpoint`, `commit`, `abort`,
`recover`, `close`, `replay`, `project`, `verify`, or `cleanup`; each domain
permits only phases meaningful to its operations.

Every failure accepted into a resolver, acquisition, recording, recovery,
replay, or projection result requires `causal_position`; a deployment verifier
failure outside those session graphs prohibits it. The one orchestrator for a
causal scope allocates one unique contiguous sequence from zero when it first
accepts a new `failure_id`, before endpoint-local clocks or completion order
can race. A later copy with that `failure_id` must be byte-identical and does
not allocate another position. Acquisition, attached recording, recovery, and
projection failures use the acquisition-session ID as scope; pre-session
resolution uses resolver-instance ID; and standalone replay uses replay-
session ID. Version 1 has no standalone projection scope. Endpoint and sink-
local sequence remains evidence but never substitutes for this total order.

`FailureClosure` is the immutable, self-hashed carrier for that total order.
Its exact top-level properties are `contract_family`, `schema_version`,
`failure_closure_id: Uuid`, `causal_scope_id: Uuid`,
`closure_sequence: UInt63`, optional `previous_closure: RecordRef`,
`next_causal_sequence: UInt63`, ordered `failures: FailureEvidence[]`,
`closed_at: ObservationTiming`, `producer`, and `content_hash`.

- Closure sequence is contiguous from zero per causal scope. Previous closure
  is prohibited at zero and otherwise names the exact sequence-minus-one
  failure-closure record with the same scope. `failures` contains every unique
  failure identity accepted by that orchestrator before `closed_at`, in causal-
  sequence order, including required, optional, cleanup, recovery, projection,
  and independently failing branch evidence. It is empty exactly when
  `next_causal_sequence` is zero; otherwise positions are exactly
  `0 .. next_causal_sequence - 1`, and its length equals that next value.
- A later closure repeats the prior array as a byte-identical prefix and then
  appends every newly allocated failure position; it never removes, rewrites,
  or renumbers a member. A snapshot with no new failure may be shared by
  multiple aggregates or advance the closure sequence with the same array.
  The final acquisition terminal closure contains every failure accepted before
  terminal; earlier recording, recovery, and projection closures are exact
  prefixes of it. Replay uses its independent zero-based closure under its
  explicitly declared scope.
- A closure snapshot is fixed after all failures nested in the aggregate that
  references it and before that aggregate is serialized. Acquisition terminal
  events/results, recording results, recovery results, replay terminal
  events/results, projection reports, and final artifact manifests all resolve
  their required failure-closure reference. A nested `SinkResult` uses its
  enclosing recording result's closure. No aggregate may validate against only
  its primary/cleanup slice, an implicit process registry, or caller-supplied
  failure copies.

The exact standalone failure-aware validator call is
`validate_failure_aggregate(aggregate: bytes, failure_closure: bytes, referenced_records: Sequence[bytes])` in
that positional order. `aggregate` and `failure_closure` are their canonical
serialized bytes. `referenced_records` is the exact complete record closure
required by that aggregate **excluding the current `FailureClosure` bytes
supplied separately as argument two**. Traversal still begins at the
aggregate's first `RecordRef` in semantic property/array order. When it reaches
the equal `failure_closure` reference, it binds that reference to argument two,
does not repeat those bytes in `referenced_records`, and recursively traverses
that closure's references; therefore every required `previous_closure` record
is included. All other records are ordered by first occurrence and recursively
by the same rule; duplicate references contribute bytes only at their first
occurrence and extra records are prohibited. This includes lifecycle and fan-out range evidence,
continuity/recording/recovery/projection results, final manifests, checkpoint
and ledger evidence, and replay events whenever the aggregate contract requires
them. Validation order is fixed: (1) aggregate canonical parse, family, hash,
and exact shape; (2) equality of its `failure_closure` reference; (3) closure
canonical parse, family, hash, scope, sequence, predecessor, and prefix; (4)
complete referenced-record closure; (5) group every recursively reachable
failure copy by identity and require byte equality with the carrier member at
that causal position; (6) reject any nested copy absent from the carrier or any
carrier position outside the aggregate's declared scope/horizon; and (7)
derive outcome-specific eligibility and select the primary from the carrier-
matched nested set. This call is mandatory for standalone validation; resolving
only a local suffix beginning above zero is never valid.

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
| `recovery` | `descriptor_mismatch`, `root_identity_mismatch`, `ledger_chain_invalid`, `recovery_unsupported`, `policy_action_prohibited`, `checkpoint_chain_invalid`, `current_state_invalid`, `member_missing`, `member_shorter_than_checkpoint`, `prefix_hash_mismatch`, `record_invalid`, `record_reference_missing`, `payload_mismatch`, `definition_missing`, `tail_preservation_failed`, `discard_unauthorized`, `cleanup_failed`, `internal_failure` |
| `replay` | `source_manifest_invalid`, `selection_invalid`, `ordering_unavailable`, `pacing_clock_incomparable`, `source_record_invalid`, `delivery_failed`, `internal_failure` |
| `projection` | `profile_mismatch`, `required_measurement_missing`, `required_field_unavailable`, `conversion_failed`, `out_of_range`, `timing_incomparable`, `native_write_failed`, `publication_failed`, `internal_failure` |
| `deployment` | `release_filename_mismatch`, `release_length_mismatch`, `release_hash_mismatch`, `metadata_file_mismatch`, `distribution_identity_mismatch`, `version_mismatch`, `source_revision_mismatch`, `runtime_dependency_present`, `file_missing`, `file_changed`, `file_added`, `import_origin_mismatch`, `conformance_manifest_mismatch`, `conformance_failed`, `unsupported_interpreter`, `internal_failure` |

Demand-resolution rejection reasons and continuity classifications are not
failure codes: they remain valid domain outcomes. Deployment finding codes are
the equal-named deployment failure codes except `internal_failure`; a receipt
uses findings for deterministic verification rejection and reserves
`FailureEvidence` for an attempted verification operation that could not
produce that deterministic comparison. Unknown domains, phases, or codes fail
closed.

Aggregate validation groups every nested failure copy, including cleanup
arrays, by `failure_id` and cross-checks it against the resolved
`FailureClosure` as specified above. Different identities may not reuse a
causal position, and no copy may disagree with its carrier member. The carrier,
not the aggregate's self-declared subset, proves the contiguous zero-based
population. Eligibility never removes, renumbers, or hides a failure.

Primary eligibility is derived from the result being validated, its outcome,
and the criticality/policy that was immutable before the failure. It is not
derived from which failure happened first. The closed rules are:

| Result whose primary is selected | Primary-eligible failure set |
| --- | --- |
| `SinkResult` | For `failed`, every non-cleanup failure causally responsible for that sink's failure. For `partial`, that set only when a runtime failure, rather than declared retention/loss policy alone, caused partial output. For `successful`, none. Sink-local eligibility applies even when this sink is optional to its recording session. |
| `RecordingSessionResult` | For `failed`, non-cleanup failures of required sinks plus recording-orchestrator failures that caused the aggregate failure. For `partial` caused by optional sink partial/failure and/or required declared-loss-only partial, and for `successful`, none. |
| acquisition terminal event and `AcquisitionSessionResult` | For `failed`, the initiating requested-failure evidence and failures of required subscribers, required continuity/provider-audit closure, required sinks, discontinuity policy, or acquisition orchestration that select the terminal reason. For `completed`, `stopped`, or `aborted`, none. An optional endpoint/sink/audit failure is ineligible unless its declaration/policy had been immutably promoted to required before it failed. |
| `RecoveryResult` | For `failed`, non-cleanup failures causally produced by that recovery action. For every successful recovery outcome, none. |
| `ReplaySessionResult` | For `failed`, non-cleanup replay failures causally responsible for failure. For `completed` or `stopped`, none. |
| `XPlaneFDRProjectionReport` | For `failed`, non-cleanup projection failures causally responsible for failure. For `completed` or `completed_with_loss`, none. |

Within the applicable eligible set, `primary_failure` is byte-identically the
member with the smallest causal sequence. It is required exactly when the
result/outcome rule requires a nonempty eligible set and prohibited when that
set is empty. An earlier ineligible optional failure therefore cannot become
an aggregate primary merely because it has a smaller sequence, while it
remains present in the nested result and exhaustive causal closure. Cleanup-
phase failures are never eligible and, when no eligible member exists, remain
cleanup evidence on the successful irreversible action. Abort, close,
recovery, and independent sink failures retain their own evidence and do not
change another result's eligible set. Diagnostics are at most 1024 NFC code
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
  completely. It must contain an artifact-content-manifest reference, and
  graph/member resolution proceeds through that immutable content root;
  final status fields do not invent content. `source_artifacts` is a nonempty
  `ArraySet<Uuid>` containing the exact retained artifacts selected from that
  content graph; every record and payload needed by the selection is included.
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
  their targets as the strict increasing subsequence of the archive's validated
  contiguous global sequence. Selected global sequence values may contain gaps
  when intervening target kinds/ranges were not selected; replay assigns a
  separate contiguous emission ordinal from zero and never relabels source
  global sequence. `per_stream_order` emits ranges in selection order and
  records within each range by archive record index.
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
`primary_failure`; and `terminal` carries the final reason, optional primary
failure, and `failure_closure: RecordRef`. Embedded selections use the
descriptor selection shape. Reasons are
`selection_complete`, `consumer_stop`, `explicit_abort`, or
`internal_failure`; only internal failure requires failure evidence.

Replay state is the closed vocabulary `not_opened`, `running`, `paused`,
`stopping`, and `terminal`, with this complete transition table:

| Prior state | Event | Next state | Delivery-generation rule |
| --- | --- | --- | --- |
| `not_opened` | `opened` | `running` | exactly event sequence 0 with generation 0; descriptor/session IDs agree |
| `running` | `paused` | `paused` | prior/current are exactly `running`/`paused`; generation unchanged |
| `paused` | `resumed` | `running` | prior/current are exactly `paused`/`running`; generation unchanged |
| `running` or `paused` | `seeked` forward | unchanged | current selection starts strictly after the prior next-emission position under the descriptor ordering; generation unchanged |
| `running` or `paused` | `seeked` backward | unchanged | current selection starts strictly before that position; generation increments by one |
| `running` or `paused` | `looped` | unchanged | restart selection equals the descriptor selection, completed selection equals the exhausted active selection, and generation increments by one |
| `running` or `paused` | `stopping` | `stopping` | generation unchanged; emitted reason follows the closed reason/failure rule |
| `stopping` | `terminal` | `terminal` | immediately following event; generation, reason, and failure equal stopping |

No other state pair is valid. Event sequence is gap-free; every event's
`delivery_generation` equals the current generation after applying its row;
forward/backward is derived from the active ordering rather than caller text;
an equal seek target is invalid; and no event or emitted record follows
terminal. Result validation receives the complete lifecycle closure, requires
exactly one stopping and terminal event, and rejects a missing generation,
invalid transition, or post-terminal event.

`ReplaySessionResult` has `replay_result_id`, `replay_session_id`,
`terminal_event`, `outcome`, `delivered_record_counts`,
`last_delivery_generation`, optional
`primary_failure`, ordered `cleanup_failures`, `failure_closure: RecordRef`,
`ended_at`, `producer`, and
`content_hash`. `outcome` is `completed`, `stopped`, or `failed`.

The two identities are `Uuid`; `last_delivery_generation` is `UInt63`;
`ended_at` is canonical `ObservationTiming` not earlier than the terminal
event in a comparable receipt domain.
The terminal event and result reference the same replay-scope failure closure;
it contains exactly the replay and cleanup failure copies accepted before
terminal, including an empty array for a failure-free replay.

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
DefinitionRef`, `binding: DefinitionRef`, `authorization`, optional
`transform: AlgorithmRef`, `source_unit: UnitSpec`, `output_unit: UnitSpec`, `resampling`,
`missing_policy`, optional `placeholder: Binary64`, and `precision_policy`.
The binding resolves to the pinned measurement; source and output units resolve
through the measurement/binding/transform closure. A mapping therefore never
selects an arbitrary corroborating sample at projection time.

`authorization` has exact properties `profile: DefinitionRef` and
`profile_item_id: Identifier`. The profile resolves to acquisition-profile,
the item resolves to the mapping's exact measurement and binding candidate,
and its cadence/resampling declarations authorize the mapping. The projection
report later pins every effective demand resolution used by the selected input
range and proves that each emitted source sample came from a source acquisition
and delivery decision for this same profile/item/binding authorization.

- `trajectory_mappings` contains exactly six mappings in this order:
  `longitude`, `latitude`, `altitude_msl_ft`, `heading_magnetic_deg`,
  `pitch_deg`, and `roll_deg`. No other trajectory field exists in version 1.
  Mapping IDs are jointly unique across the concatenation of trajectory
  mappings followed by DREF mappings; a duplicate in either array or across
  arrays invalidates the profile.
- A trajectory `output_field` is that literal field name. A DREF
  `output_field` is a tagged value with exact properties `kind: "dref"`,
  `dataref_path: NfcText(2048)`, `scale: Binary64`, and optional
  `comment: NfcText(1024)`. Paths are nonempty, contain no whitespace or
  double slash, are unique, and mappings preserve declared DREF order. Scale
  is finite and nonzero. The declaration is native output metadata, not a
  canonical binding identity.
- `resampling` is a tagged value. Kind `exact` has no other property, maps to
  profile mode `none`, and requires a sample at the row instant. Kinds `hold`,
  `nearest`, and `linear` contain `algorithm: AlgorithmRef` and `window` exactly
  equal to the corresponding profile-item `ResamplingAuthorization`; the
  effective demand resolution's delivery decision must contain the same
  values. Every mapping transform and resampling algorithm resolves by exact
  ID, revision, hash, and parameters in the authorizing acquisition profile's
  pinned `transform_registry`. `hold` additionally requires both the profile
  item's `allowed_interpolation: hold` and the measurement's interpolation
  policy `hold`; `linear` requires both values to be `linear`. Exact and
  nearest make no interpolation claim. Those modes use only same-epoch,
  same-domain evidence and cannot
  cross a discontinuity. Nearest tie-breaking is therefore pinned as earlier.
  Linear requires numeric scalar/vector equal-shape values and exact rational
  position before one final binary64 rounding. An already resampled canonical
  source sample must carry this same algorithm and ordered parent references in
  its derivation. Projection-time row alignment instead deterministically
  selects retained canonical parents under the same window; the native cell is
  disclosed loss, not a new canonical sample, and the pinned graph plus profile
  reproduces the selection without inventing an unrecorded algorithm.
- `missing_policy` is `fail`, `placeholder`, or `omit`. Trajectory mappings
  allow `fail` or `placeholder`; DREF mappings allow `fail` or `omit`.
  Placeholder is required exactly for `placeholder` and otherwise prohibited.
  Projection preflight first fixes every planned row's timing disposition, then
  evaluates every candidate-emitted row for every field before any header byte
  is published. For trajectory, a missing or unrepresentable value fails under
  `fail` and emits the exact placeholder under `placeholder`. For DREF, the
  first such value fails under `fail`; under `omit`, any such value selects the
  complete column for omission, but preflight still evaluates and reports all
  candidate rows. An omitted DREF column is absent from the header and every
  row. An included DREF column has exactly one value in every emitted row.
  Per-row DREF omission is prohibited. Placeholder and omission are never
  inferred.
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
ordered `authorizing_configurations`, ordered `authorizing_resolutions`,
`output_artifact`, `selected_range`, `failure_scope`,
`planned_row_count`, `evaluated_row_count`, `emitted_row_count`,
`omitted_row_count`, `timing_result`, ordered `field_results`, `outcome`,
optional `primary_failure`, ordered `cleanup_failures`,
`failure_closure: RecordRef`, `producer`, and `content_hash`.

`projection_report_id` and `recording_session_id` are `Uuid`; all four row
counts are `UInt63`.

`profile` is the exact projection-profile `DefinitionRef`; `input_manifest` is
an artifact-manifest `RecordRef` with an artifact-content-manifest whose graph
validates completely; `input_artifacts` is a nonempty `ArraySet<Uuid>` resolved
through that content graph; and `output_artifact` is the
preallocated native-file artifact `Uuid`. The output sink's required
prepublication sidecar content manifest binds that identity and its sealed
bytes to the input root with `projection_of`; the later final artifact manifest
references both that sidecar and this report and cross-checks their artifact
identities. This report contains no reference to either output manifest, so the
join is acyclic. `selected_range` uses the replay-selection shape and must
resolve to retained frames and their complete sample/observation closure.
`failure_scope` has exactly `kind: "in_session"` and
`acquisition_session_descriptor: RecordRef`; no other kind is valid in version
1. The descriptor names the acquisition whose orchestrator owns this
projection invocation; it need not equal the historical acquisition named by
the input manifest. `recording_session_id` resolves to an attached recording-
session descriptor in that orchestrating acquisition, and `output_artifact`
equals its native-FDR projection sink's planned root. The report appears
exactly once in that sink result and in the orchestrating acquisition
terminal/result closure. `failure_closure` uses the orchestrating acquisition-
session ID and includes every projection primary and cleanup failure copy in
the report.

Version 1 deliberately prohibits standalone projection. An offline caller
projects canonical input by running faithful replay through a normal
acquisition session, attached recording-session descriptor, and declared
native-FDR projection sink. That orchestration supplies the ordinary sink
result, byte-root content sidecar, final artifact manifest, classification,
publication status, failure closure, and producer path without fabricating a
historical acquisition terminal or adding a projection-specific result family.

`field_results` is nonempty and contains exactly one result for every mapping,
in the profile's complete trajectory-then-DREF order. Its mapping IDs equal
that jointly unique profile sequence without omission, insertion, or
reordering; report validation never treats an absent result as zero loss.

`authorizing_configurations` and `authorizing_resolutions` are nonempty aligned
arrays of acquisition-session-configuration and demand-resolution `RecordRef`
values in configuration first-use order across the selected range. Each
configuration's resolution equals the same-index resolution. Every resolution,
its demands, profiles, proposed source acquisitions, activated IDs, and
delivery decisions and every configuration and stream must resolve inside the
input manifest graph. For every mapping and every emitted source sample,
exactly one effective configuration maps its containing stream to an activated
source acquisition whose accepted item and delivery decision contain the same
profile/item/binding authorization. Missing, inactive, or conflicting
authorization is `profile_mismatch`.

Planned rows are the exact cadence instants from the first selected frame
through the inclusive selected end. `evaluated_row_count` is the prefix that
reached a final row disposition: a complete native row was written to the
candidate artifact or the timing policy omitted the row. Semantic preflight may inspect later rows but
does not count them as finally evaluated until that disposition is reached.
`emitted_row_count + omitted_row_count == evaluated_row_count`. A completed
outcome requires evaluated equals planned; a failed outcome permits evaluated
less than or equal to planned. When it is less, `planned_row_count -
evaluated_row_count` is the exact failed and not-attempted suffix whose first
row is identified by the primary failure's RFC 6901 path. Equality is valid
only when native writing or publication fails after every planned row reached
a final row disposition.
`timing_result` has exact properties `gap_omitted_count: UInt63`,
`midnight_wrap_count: UInt63`, optional `affected_planned_rows: RecordRange`,
and `limitations`. Gap omission count equals `omitted_row_count`; midnight
count includes every emitted wrapped row after a date boundary. The affected
range is present exactly when either count is nonzero and spans planned row
indices, while limitations are ordered unique text. Missing UTC or incomparable
clock evidence fails projection and is retained in primary failure rather than
being counted as an omission.

Each `FieldResult` has exact properties `mapping_id: Identifier`,
`evaluation_state`, `column_disposition`, `evaluated_count: UInt63`,
`emitted_count: UInt63`, `omitted_count: UInt63`,
`placeholder_count: UInt63`, `conversion_failed_count: UInt63`,
`out_of_range_count: UInt63`, `rounded_count: UInt63`,
`clamped_count: UInt63`, `interpolated_count: UInt63`,
`resampled_count: UInt63`, optional `affected_rows: RecordRange`, and ordered
unique `limitations`. Field preflight traverses mappings in report order and
candidate-emitted planned rows in increasing row index, so partial evidence has
one deterministic prefix.

`evaluation_state` is `complete`, `failed`, or `not_evaluated`. A complete
result inspected every candidate-emitted row for that mapping. A failed result
inspected the prefix through the row identified by the projection primary
failure and has positive `evaluated_count`. A not-evaluated result has every
count zero, no affected range, an empty limitations array, and
`column_disposition: undecided`. For a failed report the only permitted state
shapes are: all `not_evaluated` for a failure before field preflight; zero or
more `complete`, exactly one `failed`, then only `not_evaluated` for a field
failure; or all `complete` for a later native-write or publication failure.
The primary failure path identifies the failed mapping and row when a failed
field exists. A completed outcome requires every field state to be complete.

For a complete trajectory result, `column_disposition` is `not_applicable`,
emitted equals the report's emitted-row count, and omitted is zero. For a
complete DREF result, disposition is `included` or `omitted`; included has
emitted equal to emitted-row count and zero omitted, while omitted has zero
emitted and omitted equal to emitted-row count. `omitted` is valid exactly
when that DREF mapping's `missing_policy` is `omit` and at least one evaluated
candidate row lacks a representable authorized value; otherwise a complete
DREF result is included. A complete trajectory placeholder count is nonzero
only under its exact `placeholder` policy. `failed` uses `undecided` because
the header is not published; every later not-evaluated mapping does likewise.
Thus the native header and every positional row have exactly the same DREF
cardinality and no result can conceal a policy-disallowed omission.

`evaluated_count` counts candidate-emitted planned rows inspected for that
mapping and may exceed emitted count only for a failed report. It equals
`emitted_row_count` for every complete field in a completed report. Placeholder
is included in emitted. Rounded count can be nonzero only for
`inexact_conversion: round`, clamped count only for `range_overflow: clamp`, interpolated count only
for hold/linear resampling, and resampled count only for a non-exact resampling
mode. A nonzero count prohibited by the corresponding mapping policy invalidates
the report. The remaining loss counts may overlap and do not sum to emitted
count. `affected_rows` is present exactly when any loss or failure
count is nonzero and spans the first through last affected planned-row index.
If timing or field preflight fails, no header byte was published,
`emitted_row_count` is zero, and every failed or not-evaluated field has zero
emitted and omitted counts. If all fields are complete and native writing later
fails, their evaluated counts preserve complete preflight while emitted and
omitted counts cross-validate the safely published row prefix.
`outcome` is `completed`, `completed_with_loss`, or `failed`.

An inexact conversion with policy `reject`, a range overflow with policy
`reject`, or a missing/unrepresentable value with missing policy `fail`
produces the corresponding projection primary failure. Otherwise placeholder,
whole-column omission, round, and clamp follow their exact policies and remain
counted loss. No conversion or range failure can be relabeled as authorized
loss without the applicable profile policy.

`completed` requires all field states complete, zero omitted rows, zero timing
loss, every DREF column included, every field loss count and limitations array
empty, and no primary failure. `completed_with_loss` also requires all field
states complete and is required for any omitted row or DREF column,
midnight wrap, placeholder, conversion, range/clamp, rounding/precision,
interpolation/resampling loss, or limitation and prohibits a primary failure.
`failed` requires a projection-domain
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

`ExpectedDeploymentPin` is the immutable trusted verification input for one
future release. Its exact properties are `contract_family`, `schema_version`,
`deployment_pin_id`, `deployment_pin_revision`, `authority`, nonempty
`provenance`, literal `distribution_name: "xplane-fdau"`,
`distribution_version: VersionText`, `repository_revision: VersionText`,
`release_artifact`, `wheel_metadata`, `conformance_manifest`, `limitations`,
and `content_hash`.

- `release_artifact` has exact `filename: NfcText(255)`, literal
  `media_type: "application/zip"`, `byte_length: UInt63`, and `sha256: Sha256`.
- `wheel_metadata` has exact `dist_info_directory: NfcText(255)`,
  `metadata_member`, `wheel_member`, literal `metadata_name: "xplane-fdau"`,
  `metadata_version: VersionText`, `requires_python: NfcText(128)`, and
  `requires_dist: ArraySet<NfcText(512)>`. Each member has `path`,
  `byte_length: UInt63`, and `sha256: Sha256`; paths are the exact regular wheel members below
  the named `.dist-info/` directory and are respectively `METADATA` and
  `WHEEL`. Metadata version equals distribution version and requires-dist is
  empty under version 1.
- `conformance_manifest` has exact path
  `xplane_fdau/conformance/v1/manifest.json`, `byte_length: UInt63`, and
  `sha256: Sha256`.

The pin is obtained from a consumer-trusted build input or signed/reviewed
release index before artifact verification. It may be referenced by the
consumer's encompassing build manifest, but it is never discovered from the
candidate wheel, delivered namespace, build-identity resource, or conformance
manifest being verified. A new release identity or any changed byte/hash
requires a new pin revision and hash. This design fixes the shape without
inventing a current version, revision, filename, length, or hash.

`DeploymentPolicy` is an immutable definition that specifies how any consumer
must verify a future FDAU release. It contains `deployment_policy_id`,
`deployment_policy_revision`, `authority`, `provenance`,
`allowed_deployment_modes`, literal `distribution_name: "xplane-fdau"`,
literal `import_namespace: "xplane_fdau"`, literal
`expected_pin_family` equal to the expected-deployment-pin URI,
`required_artifact_kind`,
`package_inventory_rule`, `metadata_rule`, `build_identity_resource`, `runtime_dependency_rule`,
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
- `metadata_rule` has exact properties `installed_wheel` with literal value
  `verify_delivered_dist_info_against_pin` and `reproducibly_bundled` with
  literal value `verify_pinned_wheel_members_without_dist_info_delivery`. The installed
  rule requires byte/hash verification of the installed
  `.dist-info/METADATA` and `.dist-info/WHEEL` files against the already pinned
  wheel members and parses name, version, `Requires-Python`, and every
  `Requires-Dist` from that verified METADATA. The bundled rule parses and
  hashes those same two members
  directly from the pinned wheel and fixes `dist_info_delivery:
  "not_delivered"`; a bundle delivers the complete `xplane_fdau/` inventory but
  no copied `.dist-info` tree. In both modes the build-identity resource proves
  only its three declared claims and cannot replace wheel metadata.
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
`expected_pin`, `deployment_mode`, `actual_release_artifact`,
optional `actual_distribution_name`, optional `actual_distribution_version`,
optional `actual_repository_revision`, `metadata_evidence`, `package_inventory`,
optional `runtime_dependencies`, optional `import_origin`, `python_version`, optional
`conformance_manifest_sha256`, optional `conformance_result_sha256`, ordered
`findings`, `outcome`, `verified_at`, `producer`, and `content_hash`.

`deployment_receipt_id` is `Uuid`; `verified_at` is canonical
`ObservationTiming`.

- `policy` is the exact deployment-policy `DefinitionRef`; `expected_pin` is
  the independently supplied expected-deployment-pin `DefinitionRef`;
  `consumer_id` is an `Identifier`; `consumer_build_id` is `VersionText`; and
  `deployment_mode` is allowed by the policy. No expected release field is
  copied from the candidate artifact.
- `actual_release_artifact` has exact properties `filename: NfcText(255)`,
  `media_type: "application/zip"`, `byte_length: UInt63`, and `sha256:
  Sha256` for the exact wheel bytes.
- When present, actual distribution name/version/revision are the values read respectively
  from verified wheel metadata and build identity. Their expected values remain
  addressable through the pin reference; both sides survive in a rejected
  receipt. Each actual identity property is present exactly when its source
  resource was available and parsed under the mode rule; a missing or invalid
  source leaves that property absent and requires the corresponding finding.
- `metadata_evidence` is mode-tagged. `not_evaluated` has exact
  `kind: "not_evaluated"` and `reason: "release_pin_failed"` and requires all
  three actual identity fields to be absent. `installed_wheel` has exact
  `kind`, `dist_info_root: NfcText(2048)`, `metadata_file`, `wheel_file`, and
  optional parsed `distribution_name`, `distribution_version`,
  `requires_python`, and `requires_dist`. `reproducibly_bundled` has exact
  `kind`, `metadata_member`, `wheel_member`, those same optional parsed facts,
  and literal `dist_info_delivery: "not_delivered"`. Each file/member is an
  `ObservedFileState`: kind `missing` contains only its normalized expected
  path; kind `present` contains path, `byte_length: UInt63`, and `sha256:
  Sha256`. The four parsed facts are all present exactly when both observed
  states are present and equal the expected pin, and are otherwise all absent.
  When present they equal the top-level actual distribution name/version and
  determine `runtime_dependencies`. A missing or unequal state requires
  `metadata_file_mismatch`. The bundled import root is not required to expose
  installed metadata, and its member states come from the verified wheel.
- `package_inventory` is tagged. `not_evaluated` contains only
  `kind: "not_evaluated"` and `reason: "release_pin_failed"`.
  `evaluated` contains `kind`, ordered `expected_package_files`, and ordered
  `delivered_package_files`. Package-file entries have exact properties
  `path`, `byte_length: UInt63`, and `sha256: Sha256`. `path` is a normalized
  relative POSIX path below `xplane_fdau/` with no empty, `.`, or `..` segment.
  Entries are unique and sorted by path. `evaluated` is permitted only after
  filename, media type, byte length, and SHA-256 all match the trusted pin;
  expected inventory is then derived from that verified wheel, never from the
  delivered root or caller inventory. Delivered inventory is scanned from the
  exact import root.
- `runtime_dependencies`, when the four metadata facts were parsed, is an
  `ArraySet<NfcText(512)>` of normalized `Requires-Dist` values and must be
  empty for verification. `import_origin` is present exactly when inventory
  was evaluated and is the normalized absolute package-root path as
  `NfcText(2048)` evidence; path spelling is not package identity.
  `python_version` is the verifier's actual `VersionText`. A verified receipt
  requires it to fall in the pinned release metadata's supported range; an
  out-of-range value remains valid rejected-receipt evidence and requires
  `unsupported_interpreter`.
- `conformance_manifest_sha256` and `conformance_result_sha256` are present
  only when package inventory was evaluated and the corresponding resource/run
  was reached. The manifest hash must equal the expected pin before execution;
  the result hash covers canonical conformance-result bytes including final LF.
  Every package and metadata hash is `Sha256`.
- `outcome` is `verified` or `rejected`.
- Findings use the closed codes `release_filename_mismatch`,
  `release_length_mismatch`, `release_hash_mismatch`, `metadata_file_mismatch`,
  `distribution_identity_mismatch`, `version_mismatch`,
  `source_revision_mismatch`, `runtime_dependency_present`, `file_missing`,
  `file_changed`, `file_added`, `import_origin_mismatch`,
  `conformance_manifest_mismatch`, `conformance_failed`, or
  `unsupported_interpreter`.
- A rejected receipt remains audit evidence but cannot establish a deployment
  pin.

Each `DeploymentFinding` has required `code` and optional `path`, `expected`,
and `actual`. `path` is the affected normalized package-relative path, or the
pinned wheel-member path for `metadata_file_mismatch`, and is required for
`file_missing`, `file_changed`, `file_added`, and `metadata_file_mismatch`; it
is prohibited for other codes. `expected` and `actual` are tagged values with
kind `text`, `uint63`, `sha256`, or `file_state` and the equal-named
`NfcText(2048)`, `UInt63`, `Sha256`, or `ObservedFileState` value. Length
mismatches use `uint63`, while filename and identity mismatches use `text`.
For a required but absent file, the actual side is the `missing` observed-file
state; a side is omitted only when it does not exist conceptually, such as the
expected side of `file_added`, and is never `null`. Findings are an `ArraySet`
ordered by code, then path, then canonical expected/actual bytes. `verified`
requires an empty findings array; `rejected` requires at least one finding.

The consumer embeds this portable FDAU-owned receipt in, or references it from,
its own build manifest. FDAU does not own the consumer's complete manifest,
packaging process, or deployment orchestration.

Closed-world proof proceeds in this order:

1. validate the trusted expected pin independently of the candidate artifact;
2. compare candidate wheel filename, media type, byte length, and SHA-256 to
   that pin; a mismatch records actual evidence and leaves package inventory
   `not_evaluated`;
3. only after the complete release-artifact pin matches, verify the exact
   mode-specific metadata files/facts, distribution name, exact version,
   supported interpreter, source revision, empty runtime dependencies, and
   pinned conformance-manifest member;
4. derive the complete expected `xplane_fdau/**` inventory from that verified
   wheel;
5. scan the delivered namespace and reject missing, changed, or additional
   non-cache files;
6. verify import resolution below the one delivered root;
7. run the shared conformance entry point against the pinned corpus;
8. hash the canonical conformance result; and
9. emit a verified receipt only when every step passes.

Verification is fail-collecting within the dependency frontier reached: every
independent deterministic pin mismatch is retained, but no wheel-derived
inventory or metadata is trusted after a release-artifact mismatch; after the
pin succeeds, every independent deterministic metadata, inventory, import, and
conformance mismatch is retained in canonical finding order.
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

`xplane_fdau.contracts.deployment` and its expected-pin, policy, receipt,
schema, corpus, and installed-verification resources are owned by `A1.9` and
must be delivered there before their adoption and before `I1.2`; naming the
target module here does not mark delivery or alter the reviewed `C4.4`/`I1.1`
threshold.

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
| `A1.1` | Acquisition-profile identity, pinned transform registry, cadence/interval distribution, burst, transition coverage, phase, quality, resampling/interpolation, and retention declarations |
| `A1.2` | Immutable activate/withdraw demand lifecycle, contiguous replacement generation, idempotent receipts, required/optional items, and retention strength |
| `A1.3` | Atomic required-item resolution, optional-item rejection, proposed-versus-activated source closure, pinned source-retention capability, delivery periods, and closed incompatibility outcomes |
| `A1.4` | Allow-listed transform registry, data-only parameters, deterministic execution order, and explicit loss/failure evidence |
| `A1.5` | Acquisition-session descriptor, immutable configuration generations, phase-distinct streams, provider-audit ingress/evidence, initialization-failure exit, complete lifecycle state machine, epoch identity, and source-context change boundary |
| `A1.6` | Profile-authorized cadence plus resolution-pinned algorithms, windows, lineage, downsampling, interpolation, aggregation, and resampling policies; no additional family is required |
| `A1.7` | Exhaustive configuration-lifetime event/record/delivery ranges, immutable policy identity, per-binding corroboration, burst/transition metrics, available/unavailable predecessor evidence, delivery/storage-separated stored/missing per-root provider-audit closure including post-store loss, protected-sink attribution, deterministic classification, and closed insufficiency reasons |
| `A1.8` | Synchronous fan-out ports, exact operation outcomes, one declaration/event/report/close/commit endpoint-stream tuple universe, sink/subscriber isolation, endpoint-plus-stream sequence, backpressure, and delivery events |
| `A1.9` | Acyclic configuration-close and stopping/continuity/commit/recording/terminal/final-manifest orchestration, immutable self-hashed failure-closure snapshots, outcome-specific primary eligibility, and immutable terminal results plus expected deployment pin, deployment policy, portable receipt, schemas, corpus, public API, and installed verification required before `I1.2` |
| `R1.1` | Recording-session descriptor, sink declarations, protected demand/stream relations, criticality, recovery policy, and artifact UUID/content identity separation |
| `R1.2` | Artifact-content-manifest-rooted logical archive, canonical JSON/JSONL, ordered demand-resolution/configuration history, global-order entries, separate raw/provider-audit content-addressed payloads, and retention definitions |
| `R1.3` | Immutable segment closure, reference-complete checkpoints, candidate directory, atomic/no-replace publication, and failure cleanup |
| `R1.4` | Acyclic artifact-content-manifest entries/relationships, required generic sidecars for published byte roots, exact content/publication/recovery tagged wire variants, and the classified delivered artifact-manifest termination, projection, ledger-head, publication, and self-hash boundary |
| `R1.5` | Self-hashed crash-safe artifact-state ledger and recovery request, closed action/checkpoint validation, exact ordinary/final-manifest historical head pins with explicit portable successor-absence trust, ledger-proven before/after artifact histories and exact tail byte ranges, recording/recovery terminal results, discard authorization, and outcome-specific causal precedence |
| `R1.6` | Identity-preserving faithful canonical replay, subset ordering, pacing, complete state machine, seek generations, events, and result |
| `R1.7` | Long-session and corruption verification against the fixed checkpoint, recovery, replay, and manifest contracts; no additional family is required |
| `P1.1` | Versioned projection profile, jointly unique mapping IDs, and exact ordered field mappings |
| `P1.2` | Complete mandatory version-4 trajectory-spine mapping and explicit placeholder policy |
| `P1.3` | Ordered version-4 DREF mappings and explicit omission policy |
| `P1.4` | Pinned projection cadence, timing, interpolation, and resampling behavior |
| `P1.5` | Planned/evaluated/emitted/omitted row and timing loss plus exact all-mapping field-result state, column, omission, placeholder, conversion, range, rounding, clamping, interpolation, and resampling evidence |
| `P1.6` | End-to-end canonical-input, pinned-profile, native-artifact, sidecar-content-manifest relationship, exact report reference, and deterministic reproduction closure; no additional family is required |

## Validation and runtime outcome separation

Malformed or semantically invalid contract documents fail before session use
through the approved contract-error precedence. Legitimate runtime inability
is represented by a valid outcome record with a closed code. A failed source,
sink, projection, recovery, or deployment is not converted into malformed JSON
to signal failure.

Within each result record, validation follows property order, then array index.
Cross-record closure follows argument order and canonical record order. Runtime
failures use their required session-wide `causal_position` for dominance;
endpoint-local event order and incomparable clocks never select a primary
failure. Unknown future codes, families, or schema versions fail closed.

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
3. installed-wheel and reproducibly bundled deployment, independently trusted
   expected version/revision/artifact/conformance pins, mode-specific metadata
   evidence, delivered-file hashes, conformance, and closed-world
   no-divergent-subset proof are explicit without requiring or fabricating a
   current release; and
4. independent review reports no unresolved load-bearing ambiguity; native
   FDR, ARINC, FDM/FOQA, q4xpcc, and external-client boundaries remain
   consistent with the approved scope amendment; the approved contract-only
   design is recorded as binding input for later A1/R1/P1 specifications; and
   every implementation, schema, fixture, artifact, adoption, release, push,
   tag, and publication gate remains unsatisfied without advancing any A1,
   R1, P1, S, or F1 child.
