# X-Plane 12 Virtual FDAU/FDIU Ecosystem Design

**Status:** Draft for coordinated q4xpcc and `xplane-fdau` review  
**Date:** 2026-08-09  
**Decision owner:** Jeff / tvproductions  
**Affected projects:** q4xpcc, the existing `tvproductions/xplane-fdr`
repository to be renamed `xplane-fdau`, and `xpwebapi` adapter work

## 1. Document Authority

This document is the cross-project architecture kernel for a virtual Flight
Data Acquisition Unit / Flight Data Interface Unit for X-Plane 12. It replaces
the narrow assumption that the reusable domain is only X-Plane's `.fdr` file
format.

It also supersedes the architectural and technical claims in
`docs/xplane12_foqa_fdr_addon_design_spec_v2.md`. That earlier document came
from a short exploratory engagement and remains valuable as the source of the
system-shape imperative:

```text
simulator sources -> acquisition and normalization -> multiple recorders
                  -> live consumers -> ground analysis
```

The earlier document is not a normative standards, regulatory, algorithm, or
implementation specification. In particular, its fixed FOQA thresholds,
ARINC bit layouts, `.ssfdr` container, ARINC 839 characterization, and legal
protection claims are not requirements.

This design is an architecture specification, not an implementation plan. The
renamed project requires its own reviewed Superpowers specification and exact
implementation plan before restructuring the active sibling worktree.

## 2. Architectural Decision

The existing `xplane-fdr` repository was split at the wrong seam. The reusable
domain is flight-data acquisition, semantic normalization, continuity, and
distribution. Native X-Plane FDR support is one deliberately lossy format and
sink inside that domain.

The project identity will become:

- repository: `tvproductions/xplane-fdau`;
- distribution: `xplane-fdau`;
- import namespace: `xplane_fdau`; and
- expanded name: **Virtual Flight Data Acquisition Unit / Flight Data
  Interface Unit for X-Plane**.

The existing narrow implementation is not discarded. Its parser, writer,
models, recording lifecycle, profiles, configuration, GeoJSON conversion,
CLI, tests, and release engineering become the first native-format kernel
under `xplane_fdau.formats.xplane_fdr` and `xplane_fdau.sinks.xplane_fdr`.

No compatibility `xplane_fdr` namespace is required merely because the GitHub
repository exists. Release and consumer state must be checked before the
rename. If no public distribution or external consumer exists, the project
should make a clean identity correction rather than preserve the accidental
boundary indefinitely.

## 3. Why This Decision Is Required Now

Phase 24A is defining how q4xpcc measures X-Plane and aircraft state. Those
decisions create durable meanings for recorded evidence. A raw DataRef path is
an interface address, not a complete measurement definition. It does not by
itself specify units, reference frame, scale, validity, source ownership,
clock, quality, cadence, calibration, or discontinuity behavior.

If those semantics remain q4xpcc-local or are inferred after capture:

- historical recordings cannot be interpreted without undocumented
  assumptions;
- Web API, XPLM, replay, and future native adapters can disagree silently;
- the native `.fdr` projection can be mistaken for the complete record;
- acquisition sufficiency can be confused with operational performance;
- q4xpcc and downstream FDM/FOQA tools will duplicate conversion and continuity
  logic; and
- Python and native implementations cannot prove semantic parity.

The provider-neutral measurement, acquisition, and recording contracts are
therefore current Phase 24A prerequisites even though full QAR, FDM, FOQA, and
ARINC implementations remain future work.

## 4. Goals

The virtual FDAU/FDIU will:

1. define stable, provider-neutral measurement identities and semantics;
2. bind X-Plane and aircraft-specific interfaces to those measurements;
3. accept observations from XPLM/XPPython3, `xpwebapi`, replay, fixtures, and
   future native adapters without importing those providers;
4. preserve raw and normalized values with explicit lineage;
5. record actual timing, cadence, quality, validity, gaps, drops, and
   discontinuities;
6. merge compatible acquisition demands so one read can serve multiple
   consumers;
7. fan one canonical stream out to independent recorder and live-consumer
   ports;
8. produce a rich, replayable canonical artifact set that losslessly preserves
   every accepted observation within its declared source representation and
   retention policy;
9. generate native X-Plane `.fdr` as a documented lossy projection;
10. correlate q4xpcc domain evidence without absorbing q4xpcc business logic;
11. support deterministic Python/native conformance through shared JSON
    fixtures and traces;
12. adopt applicable ARINC standards through licensed, edition-pinned,
    requirements-traced profiles and verified source/sink adapters; and
13. ship one modular runtime distribution whose every importable module uses
    only the Python standard library, remains capture-neutral and synchronous
    at its push boundary, and is testable without X-Plane or a network.

## 5. Non-Goals

The project will not:

- claim to create a certified or crash-survivable recorder;
- claim FAA-approved FOQA, Part 193 protection, or ICAO Annex 13 custody;
- emulate every aircraft bus merely because an ARINC standard exists;
- claim ARINC conformance from public catalog descriptions;
- ingest every DataRef exposed by X-Plane;
- decide which interfaces are relevant to q4xpcc;
- bundle XPPython3, XPLM, `xpwebapi`, aircraft-vendor, or application adapters;
- hide runtime dependencies behind optional extras or lazy imports;
- own BIT, test-flight cards, missions, ACS claims, procedures, guidance, or
  aircraft-control authorization;
- hard-code generic stabilized-approach, hard-landing, aircraft-limit, or SOP
  thresholds;
- perform longitudinal safety analysis or reviewer workflow;
- import `xpwebapi`, XPPython3, XPLM, q4xpcc, or a network client;
- start a thread, event loop, connection, or simulator process on import;
- introduce an arbitrary expression evaluator; or
- treat transport availability or apparent DataRef writability as authority to
  manipulate an aircraft.

## 6. Terminology

### 6.1 FDAU, DFDAU, and FDIU

FAA AC 120-82 describes a DFDAU as acquiring aircraft data from digital buses
and analog inputs, formatting data for the FDR, and potentially providing data
to ACARS, aircraft-condition monitoring, cockpit reports, or a QAR. FDIU is
used by some aircraft and recorder documentation for the corresponding
interface/formatting role. This project uses **virtual FDAU/FDIU** as a useful
functional analogy, not as a claim that X-Plane implements the physical unit.

### 6.2 Measurement

A provider-neutral semantic quantity or discrete state. A measurement has a
stable identity and explicit units, representation, reference, validity, and
quality semantics. `aircraft.pressure_altitude` is a measurement concept;
`sim/flightmodel/...` is a possible source interface.

### 6.3 Source interface and binding

A source interface is a concrete DataRef, array element, callback, command
phase, message, replay field, or fixture field. A binding is the versioned,
reviewed mapping from one or more concrete interfaces to one measurement.

### 6.4 Observation, sample, and frame

- A **raw observation** is what an adapter received from a source, with the
  best available source and receipt context.
- A **measurement sample** is a validated raw observation plus its normalized
  value, measurement identity, binding identity, timing, sequence, and quality.
- A **measurement frame** is a deterministic evaluation snapshot containing a
  set of samples and ordered observations for a declared acquisition instant.

Frames do not imply ARINC 717 framing.

### 6.5 FDR and X-Plane `.fdr`

A real FDR is a regulated, crash-survivable recorder used primarily for
accident and incident reconstruction. X-Plane's `.fdr` is a plain-text import
format used to visualize a flight in replay. This project will call the latter
the **native X-Plane FDR format** and will not confuse it with certified
recorder media.

### 6.6 QAR-like archive

A QAR provides readily accessible recorded data for routine ground processing.
The project's rich archive may be called **QAR-like** while it is only a
simulation-oriented capability. It must not be represented as a conforming
ARINC QAR until separately specified and verified.

### 6.7 FDM and FOQA

Flight Data Monitoring/Analysis is the generic downstream practice of routine
flight-data analysis. FAA FOQA is a voluntary organizational safety program
with approval, governance, validation, review, corrective-action, and legal
boundaries. FOQA is not a recorder and is not implemented merely by detecting
an exceedance.

## 7. System Context

```text
                               SYSTEM CONTEXT

      +----------------+       +----------------+       +----------------+
      | xpwebapi       |       | fixtures and   |       | replay/import  |
      | Web API adapter|       | deterministic  |       | adapters       |
      +-------+--------+       | fakes          |       +-------+--------+
              |                +-------+--------+               |
              +------------------------+------------------------+
                                       |
                              raw observation port
                                       |
                                       v
 +----------------+       +----------------------------------------------+
 | XPLM/XPPython3 |------>|             xplane-fdau core                |
 | runtime adapter|       | catalog -> bindings -> acquisition -> frames |
 +----------------+       |       quality -> continuity -> fan-out       |
                          +-----+---------+---------+---------+-----+
                                |         |         |         |
                     canonical  | native  | live    | replay  | artifact
                     archive    | `.fdr`  | frames  | traces  | manifest
                                v         v         v         v
                         +----------+  +--------+  +------+  +--------+
                         | QAR-like |  |X-Plane |  |tests |  |index / |
                         | artifact |  | replay |  |tools |  | hashes |
                         +----+-----+  +--------+  +------+  +--------+
                              |              |
                              |              v
                              |       +----------------------+
                              |       | q4xpcc live domain   |
                              |       | procedures, cards,   |
                              |       | missions, guidance,  |
                              |       | findings, evidence   |
                              |       +----------+-----------+
                              |                  |
                              +--------+---------+
                                       |
                                       v
                              +----------------------+
                              | future FDM/FOQA      |
                              | postflight analysis, |
                              | trends, review,      |
                              | governance           |
                              +----------------------+
```

The in-process XPLM/XPPython3 or future native collector is the authoritative
live acquisition path when exact callback, cycle, or transition fidelity
matters. The Web API is a valuable independent supervisor and corroboration
adapter, but its documented change-only update stream and lack of source
timestamps prevent it from being the sole lossless recorder.

## 8. Ownership Boundaries

| Concern | Authority |
| --- | --- |
| Measurement-definition contract, generic catalog content, units, frames, validity, quality, and lineage | `xplane-fdau` |
| Source-binding contract and allow-listed calibration/conversion algorithms | `xplane-fdau` |
| Q4XP/q4xpcc-specific measurement and binding definitions | q4xpcc, conforming to pinned `xplane-fdau` contracts |
| Acquisition profiles, frames, continuity, and generic fan-out | `xplane-fdau` |
| Native X-Plane FDR parser/writer/export and GeoJSON | `xplane-fdau` format/export modules |
| Rich canonical archive, replay source, and generic artifact manifest | `xplane-fdau` |
| Relevant-interface capability ledger and tested capability status | q4xpcc |
| Cards, sessions, missions, procedure/phase FSMs, guidance, and findings | q4xpcc |
| Aircraft-state write/command authorization and interlocks | q4xpcc session policy |
| X-Plane Web API transport and connection behavior | `xpwebapi` adapter project |
| XPLM/XPPython3 lifecycle and callbacks | consuming plugin adapter |
| Postflight segmentation, exceedances, trends, review, and governance | future FDM/FOQA consumer |
| Edition-pinned ARINC encoders/decoders and profile mappings | `xplane-fdau` standards/codec modules |

Dependency arrows point inward toward `xplane-fdau` contracts:

```text
xpwebapi adapter ------+
q4xpcc XPLM adapter ---+--> xplane-fdau public contracts
replay/test adapter ---+

xplane-fdau -X-> xpwebapi / XPPython3 / XPLM / q4xpcc
```

Consumer-owned host adapters may import `xplane_fdau`; `xplane_fdau` never
imports them. Package-owned adapters are limited to host-neutral formats and
sinks—such as canonical JSONL, native X-Plane FDR, GeoJSON, replay, and future
edition-pinned ARINC codecs—and remain standard-library-only.

Contract ownership does not require every catalog entry to ship in the core
distribution. `xplane-fdau` may ship reviewed stock-X-Plane definitions and
generic transforms. Aircraft/vendor/application-specific definitions remain
with the project that can establish their provenance, while conforming to the
same schemas and conformance corpus.

## 9. Hexagonal Architecture

The core is pure domain behavior. Ports are small capability-segregated
interfaces; adapters own transport and host behavior.

### 9.1 Source ports

- resource discovery and metadata observation;
- synchronous scalar/array observation;
- callback/update delivery;
- command-phase observation when an adapter can provide it;
- lifecycle/epoch notification;
- clock and cycle context; and
- deterministic replay.

No source port promises metadata the provider cannot supply. Unknown remains
unknown with provenance; it is not guessed.

### 9.2 Sink and subscriber ports

- canonical archive sink;
- native X-Plane FDR projection sink;
- generic JSONL audit sink;
- in-memory deterministic test sink;
- replay-trace sink;
- live measurement-frame subscriber; and
- generic artifact-manifest sink.

### 9.3 Push-first execution

Adapters push observations or frames into an explicitly opened acquisition or
recording session. Core methods do not sleep, poll the network, start threads,
or call simulator APIs. Pull and asynchronous conveniences may be adapter
composition over the same synchronous boundary.

### 9.4 Runtime distribution and dependency boundary

`xplane-fdau` is one distribution with many cohesive internal packages, not one
monolithic module and not a family of prematurely version-coupled
distributions. Its runtime dependency list is empty. Every module included in
the wheel—including contracts, CLI, native FDR, GeoJSON, replay, canonical
recording, and standards profiles/codecs—imports only the Python standard
library or another `xplane_fdau` module.

Development tools may use isolated, pinned dependency groups, but those tools
and dependencies are absent from the wheel and may not be reached through lazy,
conditional, plugin, entry-point, or optional-extra imports. Installed-wheel
tests and static import-boundary checks enforce this rule.

XPPython3/XPLM lifecycle, `xpwebapi` transport, simulator discovery, aircraft
bindings, q4xpcc policy, and other application integration remain in the
consumer. A consumer implements the small source/sink/subscriber protocols it
needs and translates host objects into FDAU-owned immutable values at the
boundary. No XPPython3 or SDK object crosses into the core domain.

This permits the same release artifact to support offline utilities and an
XPPython3 plugin. A consumer may install the pinned wheel into its Python
environment or bundle the exact first-party package files into its deliverable.
Bundling must be produced from one pinned release artifact, record its version
and hashes, and pass the same conformance corpus; it may not become an
independently edited fork.

## 10. Contract Families

The following JSON-compatible families are independently versioned:

1. measurement catalog;
2. source-binding catalog;
3. acquisition profile;
4. raw observation;
5. measurement sample;
6. measurement frame;
7. acquisition lifecycle event;
8. recording session descriptor/result;
9. continuity report; and
10. artifact manifest.

Every definition document carries:

- contract-family name or URI;
- wire/schema version;
- semantic definition ID and revision;
- canonical content hash;
- provenance and authority revision;
- creation time when it is a generated artifact; and
- producer implementation and source versions.

Schema version describes wire shape. Definition revision describes semantic
content. Changing a unit, sign convention, transform, validity rule, or
reference frame is a semantic revision even when the JSON shape is unchanged.

## 11. Measurement Catalog

Each `MeasurementDefinition` declares all assumptions explicitly:

- stable measurement ID, revision, and hash;
- human-readable title and description;
- semantic quantity or discrete-state meaning;
- representation: boolean, integer, finite real, string/bytes, enumeration,
  vector, or fixed/variable array;
- canonical physical dimension/quantity and canonical unit, or explicit
  unitless status;
- reference frame, datum, axis, handedness, and sign convention when relevant;
- numeric precision, meaningful resolution, and documented range;
- enumeration labels and unknown/reserved handling;
- quality and validity vocabulary;
- freshness and staleness interpretation;
- discontinuity and interpolation policy;
- sensitivity/data-classification annotation;
- aircraft/simulator applicability classes; and
- source authority and supporting documentation.

A catalog definition does not name a DataRef unless the DataRef name is part of
the measurement's semantic provenance. Concrete provider details belong in a
binding.

## 12. Source Bindings

Each `SourceBinding` declares:

- stable binding ID, revision, and hash;
- exact measurement ID and revision;
- provider and adapter family;
- source resource identity and expected owner/signature;
- DataRef path, command/message name, array indices, or source field;
- declared and observed source type/shape kept separately;
- aircraft, plugin, simulator, and version applicability;
- native unit and representation;
- allow-listed transform and calibration identity;
- ordered dependencies for a multi-source or derived binding;
- optional status/validity companion sources;
- absent, orphaned, stale, and read-error behavior;
- expected acquisition phase relative to the flight model;
- replay policy; and
- provenance and limitations.

Transforms are versioned named algorithms with explicit parameters. Arbitrary
expressions and caller-supplied code are prohibited. Saturation, rounding,
precision loss, out-of-range input, and failed calibration produce quality
information; they are not silent conversions.

## 13. Raw Observations and Measurement Samples

A raw observation preserves what the adapter actually knew:

- provider/adapter identity and version;
- connection and source generations;
- exact source resource identity;
- raw type, index/shape, and JSON-safe raw value or referenced byte payload;
- source timestamp and source sequence only when genuinely supplied;
- host monotonic receipt timestamp plus its clock-domain identity;
- UTC receipt timestamp;
- X-Plane cycle number when available;
- pre/post-flight-model acquisition phase when available;
- simulator flight time and time-speed state when available;
- pause and replay state when available; and
- adapter status or error.

A measurement sample adds:

- measurement and binding identities/revisions/hashes;
- acquisition-session, stream, epoch, and sequence identities;
- normalized value and canonical unit;
- transform/calibration identity;
- quality and validity flags;
- freshness/age at evaluation;
- raw-observation reference; and
- derivation parent references when applicable.

Every accepted sample retains either its complete JSON-safe raw observation or
an immutable, content-addressed reference to the raw payload. A reference
records media type, byte length, SHA-256, storage role, and retention status.
Provider-specific exhaustive audit streams may be optional, but they are not a
substitute for this sample-to-raw lineage. If a retention policy intentionally
omits a source representation, the artifact is described as normalized or
projected—not lossless.

Missing values are never replaced with plausible zeroes. Boolean values are
not accepted as numeric values unless the measurement definition explicitly
declares a Boolean/discrete representation. Non-finite JSON numbers are
rejected or represented as an explicit quality/status condition rather than
serialized as non-standard JSON.

## 14. Timing Model

Requested cadence is policy; observed timestamps are evidence.

Every authoritative live stream records, when available:

- high-resolution host monotonic time for interval measurement, including a
  stable `clock_domain_id`, clock kind, integer unit (normally nanoseconds),
  advertised resolution, origin/scope, and producer process/session identity;
- aware UTC receipt time for cross-artifact correlation;
- project acquisition sequence;
- adapter/source sequence;
- X-Plane cycle number;
- simulator flight time;
- pause, replay, and time-compression state;
- acquisition phase relative to the flight model; and
- discontinuity/epoch generation.

Monotonic values are directly comparable only inside the same clock domain.
Cross-process or restarted-process correlation requires explicit UTC/monotonic
anchor pairs and records the uncertainty of that mapping; it never subtracts
unrelated monotonic clocks.

No unavailable clock is invented. A Web API receiver timestamp is not relabeled
as a simulator source timestamp. Wall-clock, simulator-time, and monotonic-time
semantics remain separate.

Replay, seek, aircraft reload, plugin reload, connection replacement, clock
regression, pause, and time-speed changes are explicit lifecycle or
discontinuity observations. Replayed observations are not appended as fresh
live-flight facts by default.

## 15. Acquisition Profiles and Demand Resolution

An `AcquisitionProfile` declares per measurement or cadence class:

- requested and minimum acceptable rate;
- minimum observation count and elapsed span;
- maximum staleness and gap;
- interval-distribution tolerance;
- allowed burst, aggregation, interpolation, and resampling policy;
- acquisition phase;
- required quality/validity states;
- bounded window or continuous-stream role;
- pre/post-transition coverage requirements; and
- overload/degradation priority.

Multiple active consumers submit immutable, predeclared demands. The resolver:

1. validates compatibility;
2. acquires each concrete source no more often than the highest authorized
   demand requires;
3. distributes the same accepted sample identities to every consumer;
4. applies consumer-specific downsampling only when explicitly permitted;
5. records every demand/profile transition and generation; and
6. rejects contradictory unit, binding, validity, or retention definitions.

q4xpcc cards may open and close predefined acquisition segments at task or
phase boundaries. They do not mutate a hidden global sampling rate.

## 16. Continuity and Quality

Acquisition quality and operational evaluation are different axes.

Continuity evaluates whether evidence is sufficiently complete and trustworthy:

- requested versus observed cadence;
- accepted count and elapsed span;
- first-value readiness;
- interval distribution;
- gaps, drops, duplicates, and reorderings;
- staleness;
- discontinuities and epoch boundaries;
- provider/connection changes;
- quality/validity distribution; and
- source and sink failures.

Operational evaluation determines what the measurements show: within a
configured tolerance, outside it, indeterminate, or not evaluated. A recording
can have excellent continuity and contain an out-of-tolerance observation.
Conversely, an apparently in-range value with insufficient or invalid evidence
cannot support a trustworthy finding.

Suggested acquisition quality vocabulary includes:

- `valid`;
- `unavailable`;
- `orphaned`;
- `type_mismatch`;
- `read_error`;
- `stale`;
- `out_of_declared_range`;
- `conversion_failed`;
- `discontinuous`;
- `dropped`;
- `duplicate`;
- `reordered`; and
- `provider_degraded`.

The exact closed vocabulary belongs to the reviewed contract and must be shared
by Python and native implementations.

## 17. Provider Semantics

### 17.1 XPLM/XPPython3

XPLM DataRef string names are the stable lookup identities; opaque handles are
resolved per simulator run and cached. One DataRef may advertise multiple
types. Array reads may return fewer elements than requested. Writable status
does not prove that a write will have durable effect.

Plugin-provided DataRefs can become orphaned and read as zero after their owner
is disabled. Availability and owner evidence are therefore distinct from the
numeric value. Aircraft/plugin load order is not assumed. Aircraft load,
unload, plugin, livery, and relevant DataRef-registration messages create
acquisition epochs or revalidation triggers.

DataRefs are observations, not events. State transitions are derived and retain
references to their source samples. Command begin/continue/end phases and
plugin messages are event-like observations but do not prove aircraft-state
effects. Commands must be correlated with outcome measurements.

Callbacks execute synchronously inside X-Plane. Adapters copy the minimum
observation into bounded internal state and return promptly; they do not perform
blocking serialization or analysis in the callback.

### 17.2 X-Plane Web API

The adapter probes `/api/capabilities` and records the selected API version.
Runtime numeric resource IDs are session-scoped and rediscovered after restart.
The documented DataRef schema does not currently supply units, descriptions,
array dimensions, or read/write status, so semantic bindings cannot be derived
from Web API discovery alone.

WebSocket DataRef updates are currently sent at approximately 10 Hz. The first
message supplies subscribed values; later messages contain changed values
only. The documented payload does not provide simulator source timestamps or
source sequence numbers. Consequently:

- absence from an update means unchanged, not missing;
- repeated same-value writes may be unobservable;
- multiple transitions inside one update interval may collapse;
- short pulses may be missed; and
- receiver timing cannot reconstruct exact simulator ordering.

The Web API is suitable for external discovery, supervisor health, guidance,
coarse telemetry, controlled test actions, and independent corroboration. It is
not the sole authoritative source for high-fidelity transition or command
evidence.

### 17.3 Replay and fixtures

Replay supplies an explicitly identified source epoch. It preserves the same
measurement/sample contracts but never claims live provenance. Fixtures use the
same contracts and clocks with deterministic injected values.

## 18. Canonical Recording and Multi-Sink Fan-Out

One accepted measurement stream may feed multiple independent consumers:

1. rich canonical QAR-like archive;
2. native X-Plane `.fdr` projection;
3. q4xpcc live frame subscriber;
4. q4xpcc evidence correlation;
5. deterministic replay trace;
6. diagnostic/audit stream; and
7. future standards-oriented encoders.

Sink failures are isolated and classified. A non-required visualization sink
must not corrupt the canonical archive. A card or mission may declare a sink
required; in that case its failure affects that activity's evidence result.
The session descriptor records sink criticality before acquisition starts.

Each sink has explicit open, append, flush/checkpoint, commit, abort, recovery,
and close semantics. Atomic publication, no-replace defaults, preserved partial
artifacts, and primary-plus-cleanup failure reporting from the narrow FDR
implementation remain design requirements.

Backpressure policy is explicit per sink. The core never silently drops a
sample. A drop, blocked writer, bounded-buffer overflow, or sink detachment is a
recorded continuity event and may invalidate required evidence.

## 19. Artifact Set and Integrity Manifest

A completed acquisition session can produce:

- immutable session descriptor;
- measurement-catalog projection;
- source-binding projection;
- acquisition-profile/demand projection;
- canonical accepted raw observations or immutable content-addressed raw
  payloads required by sample lineage;
- optional provider-specific exhaustive audit streams;
- canonical measurement samples/frames;
- acquisition lifecycle and continuity events;
- continuity report;
- q4xpcc domain-event artifact references;
- native X-Plane `.fdr` projection and projection report;
- optional GeoJSON projection;
- terminal recording/session result; and
- artifact manifest.

The generic manifest records:

- artifact ID, role, media type, schema version, size, and SHA-256;
- producer and implementation version;
- creation/finalization times;
- session, stream, epoch, and generation identities;
- catalog, binding, and acquisition-profile identities/hashes;
- source/provider/simulator/aircraft context;
- requested and observed sampling summaries;
- gaps, drops, discontinuities, and limitations;
- termination and recovery status;
- parent, projection-of, derived-from, corroborates, and related-to links; and
- privacy/sensitivity classification without asserting legal protection.

Artifacts are append-only or immutable after publication. Corrections,
resegmentation, or reevaluation create new related artifacts; they never rewrite
the original observation or decision history.

In this design, `lossless` is deliberately bounded: all accepted source values,
types, shapes, ordering, timing context actually supplied to the core, and
sample lineage survive canonical archive/replay without silent coercion. It does
not promise recovery of values the provider never delivered, discarded traffic
outside the declared acquisition profile, or information a lossy source API did
not expose.

## 20. Native X-Plane FDR Projection

Laminar documents `.fdr` as a plain-text format that X-Plane can load for
replay/visualization. Version 3 uses a fixed positional trajectory and
aircraft-state layout and therefore requires placeholders for unavailable fixed
fields. Version 4 retains a mandatory trajectory spine and adds declared
`DREF` extension columns; those columns increase native-format flexibility but
do not encode the complete FDAU quality, timing, provenance, lifecycle, event,
or mission model.

Therefore:

- the canonical archive is the source of truth;
- `.fdr` generation is an explicit project-owned exporter;
- projection records exactly which measurements and bindings supplied each
  field;
- dummy/default values are disclosed as projection limitations;
- omitted canonical measurements are reported;
- conversion and precision loss are reported;
- read/write round-trip tests prove only native-format behavior, not canonical
  data preservation; and
- X-Plane replay fidelity for plugin-owned state, commands, messages, failures,
  and custom DataRefs is not assumed.

The existing reader accepts X-Plane FDR versions 3 and 4. The writer emits
canonical version 4 only; a version 3 input therefore undergoes an explicit,
documented, potentially lossy v3-to-v4 normalization when rewritten. That
parser/canonical-v4-writer work remains valuable within this boundary, but it
must not define the general `MeasurementSample` or canonical recording-session
API.

## 21. q4xpcc Integration

### 21.1 Capability ledger versus measurement catalog

The q4xpcc capability ledger answers:

- what interface exists;
- who provides it;
- where and when it applies;
- what q4xpcc capability depends on it;
- whether observation, command, or write behavior has been characterized;
- what operations are authorized; and
- what evidence is required to verify it.

The FDAU measurement catalog answers:

- what quantity/state is being measured;
- how it is represented and normalized;
- how timing, quality, and validity are interpreted; and
- how it can be recorded consistently across providers.

A q4xpcc ledger DataRef or derived item references exact FDAU measurement and
binding IDs, revisions, and hashes. It does not duplicate generic units,
conversion, sampling, continuity, or quality definitions. q4xpcc-specific
operational derivations remain q4xpcc domain items.

### 21.2 Cards, sessions, and missions

An observation plan selects:

- q4xpcc ledger capabilities for testing/evaluation; and
- FDAU measurements and acquisition profiles for capture.

The resolved card run snapshots both projections. Card task boundaries may
activate predeclared FDAU demand segments. q4xpcc evaluates immutable
measurement frames and returns domain events, findings, guidance intents, and
authorized action intents. Callback arrival never re-enters a q4xpcc FSM.

Session/mission orchestration remains the sole state-motion authority. Multiple
active cards can request compatible measurements. Acquisition requests merge;
contradictory measurement/binding semantics fail validation. Competing writes
or commands are never resolved by the FDAU and execute neither unless q4xpcc's
explicit authorization policy selects a safe action.

### 21.3 Separate evidence streams

q4xpcc retains its operational JSONL domain events. The FDAU canonical archive
retains measurements. Provider-specific raw audit, FDAU samples, and q4xpcc
events are separate correlated artifacts rather than one overloaded log.

The plugin uses live measurements operationally for procedures, monitoring,
evaluation, guidance, and evidence generation. It is not merely a data gatherer.
Evidence emitted by the plugin remains append-only/write-only from the plugin's
perspective; postflight analysis and correction facilities live downstream.

### 21.4 Development versus deployed runtime

`xpwebapi` and the local supervisor remain development-time assistive tools.
They are not delivered inside q4xpcc. Phase 24A may use the published
`xpwebapi` package for corroboration and controlled test actions.

The q4xpcc deployed runtime permits standard-library-only product code.
`xplane-fdau` satisfies the technical side of that constraint by guaranteeing
an empty runtime dependency list across the complete distribution, not merely
its nominal core. q4xpcc still requires an explicit repository-governance and
build decision before adding the sibling project to its deployed artifact.

Integration is contract-first and consumer-adapted:

- shared versioned JSON schemas and conformance fixtures remain the
  cross-language authority;
- the q4xpcc-owned XPPython3/XPLM adapter implements pinned FDAU ports;
- the `xpwebapi` adapter remains development-only in q4xpcc;
- an approved deployed integration uses the complete pinned `xplane_fdau`
  runtime package, either installed or reproducibly bundled from its release
  artifact; and
- q4xpcc does not reimplement a Python subset of the FDAU domain. The later C++
  implementation is a deliberate second implementation proven against the
  shared JSON contracts and conformance fixtures.

No dependency is smuggled into the plugin artifact through the supervisor.

## 22. Immediate Phase 24A Reconciliation

The approved Phase 24A Slice 2 design and plans cannot be executed unchanged.
They must be amended after the `xplane-fdau` contract is reviewed.

Required changes include:

1. add provider-neutral measurement-catalog and binding contracts;
2. add exact measurement/binding projections to resolved card-run hashes;
3. keep the ledger interface-centric and reference FDAU definitions;
4. move generic cadence, timed-sample, continuity, conversion, and recording
   semantics to `xplane-fdau`;
5. keep q4xpcc task activation, card FSM, evidence objectives, findings,
   guidance, session trust, and recovery semantics in q4xpcc;
6. replace provider-specific mandatory artifact names such as raw xpwebapi
   observation logs with transport-neutral FDAU canonical artifacts plus
   optional provider audits;
7. separate acquisition coverage from verification/performance findings;
8. add FDAU artifact IDs/hashes to q4xpcc evidence and future mission claims;
9. update the future mission specification's assertion that no Phase 24A
   amendment is needed; and
10. update project-spec phases that currently treat measurement recording as a
    q4xpcc-only concern.

The four active Slice 2 plans require this exact amendment pass before any of
them is executed:

| Plan | FDAU reconciliation required |
| --- | --- |
| `2026-08-08-phase-24a-slice-2a-capability-ledger.md` | Keep the five-kind, interface-centric ledger, relevance/disposition accounting, and observed-interface authority. Replace measurement semantics embedded in ledger rows with versioned references to FDAU `MeasurementDefinition` and `SourceBinding` contracts; make observed metadata an FDAU adapter input/provenance surface rather than a competing measurement catalog. |
| `2026-08-08-phase-24a-slice-2b-c172-tester-contracts.md` | Keep aircraft profiles, tester cards, task conditions, cues, observation objectives, and immutable card resolution in q4xpcc. Replace local cadence/measurement definitions with pinned FDAU acquisition demands and measurement/binding projections; include their revisions and hashes in the resolved-card-run identity. |
| `2026-08-08-phase-24a-slice-2c-capture-evidence-engine.md` | Move generic timed observations, clocks, fixed-cadence scheduling, continuity, canonical sample/frame production, raw lineage, recording sessions, sink lifecycle, and generic artifact manifests behind FDAU contracts/ports. Keep q4xpcc session/card protocol, environment interpretation, guidance/action authorization, task/findings evidence, aircraft affinity, and session trust/recovery policy. Its exact initial cadence acceptance numbers remain q4xpcc evidence policy until empirical sorties justify revision; they are not universal FDAU semantics. |
| `2026-08-08-phase-24a-slice-2d-c172-runner-live-acceptance.md` | Keep orchestration, coverage joins, pilot runbook, headless corroboration, deployment verification, and one-aircraft session control. Compose Web API and XPLM/XPPython3 FDAU adapters, correlate FDAU artifacts into coverage without merging acquisition coverage with performance findings, and verify the pinned FDAU contract/artifact identities in live acceptance. |

The earlier Phase 24A shakedown, diagnostic-interface, and progressive-BIT plans
remain historical inputs. If an active plan reuses their recorder, timing, or
evidence terminology, the same ownership rules apply; those historical plans do
not override this matrix.

The immediate C172 BIT/discovery/flight objective remains unchanged: acquire
the complete q4xpcc-relevant standard-interface inventory at proven cadences,
with environment context, pilot guidance, and trustworthy continuity evidence.
The change is that reusable measurement semantics come from the coordinated
FDAU architecture instead of becoming q4xpcc-private contracts.

## 23. Future FDM/FOQA Boundary

A later ground-analysis system consumes canonical FDAU artifacts and optional
q4xpcc domain-event/evidence artifacts. It may implement:

- flight/phase segmentation;
- aircraft/operator-specific event sets;
- evidence validation and event confirmation;
- SOP/limit exceedance logic;
- statistical trend and fleet analysis;
- review and annotation workflows;
- corrective-action tracking and effectiveness monitoring;
- identity handling, de-identification, access control, and retention policy;
- maintenance and condition-monitoring analytics; and
- exports for research or other approved consumers.

Thresholds are versioned, aircraft/profile/operator-specific rules backed by
authoritative publications and validation evidence. They are not universal FAA
numbers and do not belong in the FDAU.

An actual FAA-approved FOQA program would require organizational approval,
governance, and legal processes beyond this simulation software. Part 193 does
not automatically protect local data, and hashing an identifier does not by
itself guarantee de-identification.

## 24. Standards Alignment Without Premature Conformance

Public standards catalogs establish scope but do not supply all normative
encoding details. The project may use their architecture concepts now and add
conforming adapters only after access to the applicable licensed editions,
aircraft recorder documentation, and conformance fixtures.

| Standard | Supported relevance | Current boundary |
| --- | --- | --- |
| ARINC 429 Part 1 | avionics bus, electrical and word/label concepts | X-Plane DataRefs are not ARINC 429 words; no encoder claim now |
| ARINC 573 | legacy acquisition/recording system concepts | historical/reference only until licensed need exists |
| ARINC 717 | digital acquisition and recording-system concepts, up to 1024 words/s in public scope | no bit-level framing or conformance claim now |
| ARINC 747 | FDR equipment/interchangeability/retrieval guidance | does not define a project `.ssfdr` container |
| ARINC 591 | QAR role for accessible FDAU output and ground processing | informs QAR-like sink purpose |
| ARINC 647A-2 | Flight Recorder Electronic Documentation (FRED) | informs future documentation exchange, not a generic decoder claim |
| ARINC 834/834A | aircraft-network data interface services | architectural analogy for adapter services only |
| ARINC 822A | on-ground aircraft wireless connectivity | transport consideration; application transfer is out of scope |
| ARINC 839 | MAGIC IP air/ground communication management | not a wQAR offload state machine |
| ARINC 600 | physical LRU/rack/connector interfaces | irrelevant to software-only core |
| ARINC 664 Part 7 | deterministic aircraft Ethernet/AFDX | include only if a real simulated source models it |
| ARINC 767 | enhanced combined recorder architecture | optional future study, not a replacement for ARINC 747 |

The previous document's one-second-major-frame/four-250-ms-minor-frame ARINC
717 model and hand-written 16-bit packing are removed. Exact subframe/frame
terminology, sync words, encodings, status matrices, and label assignments must
come from normative sources and verified implementations.

## 25. ARINC Adoption Program

Actual ARINC adoption is a design objective. The project will not stop at
ARINC-inspired names, but it will also not claim broad conformance from a few
hand-coded constants. Adoption is profile-based, edition-pinned, and supported
by reproducible evidence.

### 25.1 Standards baseline

An immutable `StandardsBaseline` records:

- standard identifier, part, supplement/revision, publication date, and
  publisher;
- licensed normative source used by the implementers;
- source-access/provenance record without redistributing protected text;
- exact clauses and tables in the adopted profile;
- excluded or not-applicable clauses with rationale;
- aircraft/recorder/configuration applicability;
- implementation modules and public contract versions;
- requirements-to-test traceability matrix;
- conformance-vector and external-tool identities/hashes; and
- review, implementation, verification, and supersession status.

Public catalog pages can justify project scope. They cannot substitute for the
licensed normative source in a conformance baseline.

### 25.2 Adoption levels

Every standards capability reports one of these controlled states:

- `scope_researched`: public scope and project relevance are established;
- `normative_source_acquired`: an exact licensed edition is available;
- `profile_specified`: included/excluded requirements and mappings are frozen;
- `implemented`: the profile has a test-first implementation;
- `verified`: normative trace tests and independent/golden vectors pass; or
- `conformance_claimed`: the project publishes a precisely bounded claim and
  its conformance report.

No lower state is described as compliant. `verified` does not mean FAA/EASA
certified equipment, and the conformance claim applies only to its named
software profile and edition.

### 25.3 Target standards capabilities

The likely adoption order is:

1. **ARINC 717:** define an edition-pinned flight-data acquisition/recording
   framing profile and implement deterministic encode/decode adapters around
   canonical FDAU measurements.
2. **ARINC 647A FRED:** represent or exchange the recorder-configuration
   documentation needed to decode an adopted recording profile, subject to the
   exact licensed schema and redistribution terms.
3. **ARINC 429:** provide optional word encode/decode and label/status mapping
   where a source, target, fixture, or educational profile genuinely uses
   ARINC 429 semantics. X-Plane DataRefs remain source bindings rather than
   pretending to be bus words.
4. **ARINC 591:** use its QAR role to shape an accessible operational-recorder
   profile; do not invent file requirements absent from the standard.
5. **ARINC 747:** model applicable recorder interface, interchangeability, and
   retrieval behavior without claiming physical crash survivability.
6. **ARINC 834/834A, 822A, and 839:** adopt only when the project implements the
   corresponding aircraft-data-service or air/ground communication boundary.
   They are not prerequisites for local recording.
7. **ARINC 573, 664 Part 7, and 767:** add only for a concrete legacy,
   AFDX-backed, or enhanced-recorder profile.

This order may change after normative review. The baseline, not this overview,
is authoritative for implementation scope.

### 25.4 Mapping architecture

ARINC identity does not replace canonical measurement identity:

```text
X-Plane source binding
        -> canonical MeasurementSample
        -> edition-pinned ARINC mapping/profile
        -> ARINC word/subframe/recording adapter
```

The mapping declares label/parameter identity, representation, scaling,
resolution, range, sign/status behavior, sampling placement, source validity,
and loss policy. A canonical measurement may map to zero, one, or multiple
standards profiles. A standards decoder produces canonical samples with the
exact standards profile retained as provenance.

### 25.5 Verification evidence

Each implemented profile requires:

- requirements traceability to named tests;
- positive, boundary, invalid, reserved, parity/status, timing, rollover, and
  synchronization cases as applicable;
- encode/decode round trips that do not hide quantization loss;
- golden byte/word/frame vectors derived under the licensed standard;
- independent implementation or tool comparison where available;
- malformed and truncated-stream recovery tests;
- cross-language Python/C++ parity fixtures;
- deterministic artifact hashes; and
- a published profile-specific conformance report.

Copyrighted standards text and extensive protected tables are not copied into
the public repository. Project-owned profiles, mappings, trace IDs, test
vectors, and results are published only to the extent permitted by the
applicable license.

## 26. Regulatory Boundary

- FAA AC 120-82 describes one acceptable means for a voluntary FOQA program;
  it does not add or change regulation.
- 14 CFR 121.344 applicability and parameter requirements depend on aircraft,
  manufacture date, installed sources, and other conditions. There is no
  universal “91 parameters” profile for this project.
- Appendix M uses parameter-specific ranges, accuracies, resolutions, and
  intervals rather than one blanket sampling range.
- Real FDR retention and accident-preservation rules do not turn an ordinary
  simulation file into certified crash-survivable media.
- 14 CFR Part 193 concerns protected voluntarily submitted information under a
  designated FAA program; it is not an automatic local-database privacy rule.
- Section 13.401 enforcement-use protection applies to approved FOQA programs
  under its conditions, not to this software by naming convention.

Regulatory references guide vocabulary and caution. The product describes
simulation behavior factually and does not market legal, certification, or
regulatory compliance without a separate supported case.

## 27. Shared JSON and Cross-Language Conformance

JSON is the shared interchange and conformance language, not a requirement to
serialize every internal function call.

The design requires one documented canonical JSON profile covering:

- UTF-8 encoding;
- permitted whitespace/line-ending rules for hashed documents;
- object-key ordering;
- array-order semantics;
- finite-number-only behavior;
- negative-zero handling;
- exact number lexicalization;
- Unicode normalization policy;
- fields excluded from self-hashing;
- lowercase hexadecimal SHA-256; and
- media type and schema/version identifiers.

Python's incidental `json.dumps()` float spelling is not silently promoted to
the C++ wire contract. Canonicalization fixtures include boundary integers,
precision-sensitive finite values, negative zero, Unicode, nested maps,
ordered arrays, and rejected non-finite values.

The shared FDAU conformance corpus asserts:

- identical normalized input envelopes;
- identical sample/frame quality and timing classifications;
- identical continuity results;
- identical recording/session lifecycle and sink classifications; and
- compatible artifact identities and hashes.

A separate q4xpcc consumer-parity suite consumes the pinned FDAU fixtures and
asserts identical q4xpcc FSM transitions and domain events, action intents and
authorization decisions, findings, terminal classifications, and correlations
to FDAU artifact identities. Those assertions protect the consumer boundary;
they are not requirements of the reusable FDAU package.

Numeric measurement contracts state their own precision and tolerance. There
is no undocumented global epsilon.

## 28. Package Shape

The target package organization is illustrative but establishes dependency
direction and keeps independently understandable modules within one pure-stdlib
distribution:

```text
xplane_fdau/
|-- __init__.py
|-- errors.py
|-- ports.py
|-- measurements/
|   |-- models.py
|   |-- catalog.py
|   `-- quality.py
|-- bindings/
|   |-- models.py
|   `-- transforms.py
|-- acquisition/
|   |-- observations.py
|   |-- frames.py
|   |-- profiles.py
|   |-- demand.py
|   |-- continuity.py
|   `-- session.py
|-- recording/
|   |-- fanout.py
|   |-- artifacts.py
|   `-- manifest.py
|-- formats/
|   `-- xplane_fdr/
|       |-- models.py
|       |-- reader.py
|       |-- writer.py
|       `-- validation.py
|-- sinks/
|   |-- canonical_jsonl.py
|   `-- xplane_fdr.py
|-- standards/
|   |-- baseline.py
|   |-- profiles.py
|   |-- arinc429/
|   |-- arinc717/
|   `-- arinc647a/
|-- replay.py
|-- geojson.py
|-- config.py
|-- cli.py
`-- schemas/
```

The exact modules will be finalized in the sibling specification. Public APIs
must distinguish canonical measurement samples from native-format FDR samples.
The distribution has no runtime dependency extras. If a future integration
genuinely needs a third-party library, it belongs in a consumer-owned adapter or
a separately governed adapter distribution; it does not weaken the runtime
wheel's standard-library guarantee.

## 29. Migration of Existing Work

### 29.1 Retain

- standard-library-only and capture-neutral core discipline;
- immutable models and strict validation;
- push-first recording;
- no threads/network/host imports in the core;
- deterministic parsing and serialization;
- atomic partial/no-replace publication;
- native X-Plane FDR v3/v4 reader and canonical-v4-only writer, including
  explicit lossy v3-to-v4 normalization reporting;
- profiles and strict JSON configuration;
- GeoJSON conversion and offline CLI;
- deterministic tests, distribution inspection, and release hygiene; and
- adapter ownership outside the core.

### 29.2 Expand

- measurement catalog and source bindings;
- raw-observation and canonical-sample contracts;
- clocks, generations, quality, validity, and lineage;
- acquisition profiles and demand merge;
- frames, continuity, and discontinuity handling;
- multi-sink fan-out and backpressure evidence;
- rich canonical QAR-like archive;
- generic artifact manifest and relationships;
- replay source; and
- cross-language conformance fixtures.

### 29.3 Move or reinterpret

- current `FDRSample` becomes a native-format sample, not the canonical sample;
- current recording session becomes the X-Plane FDR sink/session or is adapted
  behind the generic sink port;
- current mandatory navigation spine becomes an X-Plane FDR projection
  requirement, not a universal acquisition requirement;
- native FDR profiles become projection profiles;
- GeoJSON consumes canonical or native recordings through explicit adapters;
- Web API live-record behavior remains in `xpwebapi`; and
- XPLM/XPPython3 acquisition remains in consumer adapters.

### 29.4 Reject

- native `.fdr` as the universal persistence/interchange boundary;
- DataRef path as universal semantic identity;
- consumer-specific q4xpcc or FOQA business logic in the FDAU;
- provider-specific network configuration in core recording contracts;
- unsupported ARINC/regulatory claims; and
- public release under the narrow identity before the redesign is reconciled.

## 30. Rename and Active-Worktree Coordination

The existing repository and active feature worktree contain substantial narrow
implementation. Its dirty/clean state is transient and must be verified with the
active agent at the coordination checkpoint. Do not rename the local root, move
linked worktrees, rewrite imports, or edit that checkout from a second agent
while the active agent is working.

The safe coordination sequence is:

1. the active sibling agent reaches and reports a safe checkpoint without
   publishing the narrow distribution;
2. this ecosystem design is reviewed with that agent;
3. the sibling design and implementation plan are superseded or amended with a
   retain/expand/move map;
4. publication and external-consumer state are verified;
5. GitHub repository, local checkout, distribution, import namespace, CLI,
   schema IDs, docs, workflows, artifact names, and dependent references are
   renamed as one controlled change;
6. linked worktree metadata is handled deliberately;
7. existing commits are preserved and code is relocated under the FDAU
   package structure;
8. release and installed-wheel tests prove the new identity; and
9. q4xpcc and `xpwebapi` update through their own reviewed plans.

The repository rename is recoverable. The danger is not Git history; it is
releasing or depending on the narrow public API before the semantic boundary is
corrected.

## 31. Delivery Sequence

### Stage 0: Coordinated redesign and standards-ready contracts

- approve this ecosystem boundary;
- review it with the active sibling agent;
- verify release/name state;
- rename and respecify `xplane-fdau`;
- create the standards registry, edition-pinned baseline shape,
  requirements-trace shape, and adapter/profile extension seams without
  claiming or implementing a standard;
- amend affected q4xpcc Phase 24A and future mission documents.

### Stage 1: Contract and native-format kernel

- implement measurement, binding, observation, sample, frame, quality, clock,
  continuity, recording, sink, and manifest contracts test-first;
- relocate and preserve native X-Plane FDR functionality;
- publish shared schemas and conformance fixtures;
- prove the built and installed distribution has an empty runtime dependency
  list and no hidden host/adapter imports.

### Stage 2: q4xpcc Phase 24A integration

- make the supervisor and XPLM harness adapters emit pinned FDAU contracts;
- choose installed-wheel or reproducibly bundled-package deployment explicitly;
- record the FDAU distribution version, release-artifact hash, and delivered
  package-file hashes in the q4xpcc build manifest;
- verify the delivered FDAU files match the pinned release, pass the shared FDAU
  conformance corpus through the q4xpcc adapter, and contain no divergent subset
  or undeclared runtime dependency;
- complete relevant C172 inventory and BIT/ground/flight acquisition;
- corroborate Web API and in-process observations;
- retain trustworthy canonical evidence and native `.fdr` projections where
  useful;
- progress later through Baron 58, C90, and Q4XP sessions/cards.

### Stage 3: Rich recording and replay

- mature the QAR-like canonical archive;
- add replay/trace tools and artifact review;
- prove long-session recovery, backpressure, and discontinuity behavior.

### Stage 4: Downstream FDM analysis

- define a separate postflight analysis project;
- implement configurable event sets, segmentation, trends, review, and
  correction lineage;
- keep regulatory/FOQA terminology conditional and accurate.

### Stage 5: Verified standards profiles and adapters

- select the first concrete standards profile (expected to begin with ARINC 717
  plus the applicable ARINC 647A/FRED configuration boundary);
- obtain and pin the applicable licensed normative editions and aircraft
  recorder/configuration documentation before specifying or coding that
  profile;
- specify precise profiles and mappings;
- implement encoders/decoders with independent conformance evidence;
- claim only the verified standard/profile subset.

## 32. Acceptance Criteria for the Expanded Design

The coordinated architecture is ready for implementation planning when:

1. `xplane-fdau` is accepted as the project identity and FDAU/FDIU scope;
2. native X-Plane FDR is explicitly a format/sink, not the canonical model;
3. measurement, binding, sample/frame, timing, quality, continuity, session,
   sink, and artifact-manifest ownership is unambiguous;
4. q4xpcc operational ownership remains intact;
5. Web API and XPLM fidelity differences are represented in contracts;
6. canonical recording and q4xpcc domain evidence are separate but correlated;
7. acquisition sufficiency and operational performance are separate axes;
8. the active narrow implementation has a complete retain/move migration map;
9. unsupported ARINC, FAA, QAR, FDR, and FOQA claims are removed;
10. shared JSON versioning and Python/native conformance are specified;
11. Phase 24A specs/plans identify exact amendments before execution;
12. ARINC adoption has an edition-pinned baseline, scoped-profile model, and
    conformance-evidence contract;
13. no rename/restructure collides with the active sibling worktree;
14. the sibling implementation plan requires built- and installed-wheel tests
    proving every `xplane-fdau` module is standard-library-only and no host,
    simulator, network, or optional-extra dependency leaks into it; and
15. the q4xpcc integration plan requires consumer-owned XPPython3/XPLM and
    `xpwebapi` adapters plus exact pinned-release identity, hashes, conformance,
    dependency, and no-divergent-subset verification.

## 33. Delivery Acceptance Gates

The implementation is not delivered merely because the design criteria above
are satisfied. The completed sibling and q4xpcc plans must prove:

1. the built and installed `xplane-fdau` wheel declares no runtime dependencies;
2. every importable wheel module passes the standard-library and package-local
   import boundary, including CLI, GeoJSON, FDR, replay, and standards modules;
3. development-only dependency groups and tools are absent from wheel metadata
   and contents;
4. q4xpcc declares whether it installs or reproducibly bundles the package;
5. the plugin build manifest records the exact FDAU version, release-artifact
   SHA-256, and delivered package-file hashes;
6. delivered package files match that pinned release byte-for-byte;
7. the q4xpcc adapter passes the shared FDAU conformance corpus;
8. artifact inspection finds no separately edited FDAU subset, host adapter in
   the FDAU package, or undeclared dependency; and
9. Python/native parity remains grounded in the same versioned JSON contracts
   and fixtures rather than implementation-specific object identity.

## 34. Authoritative References

### X-Plane and SDK

- [X-Plane local Web API](https://developer.x-plane.com/article/x-plane-web-api/)
- [XPLM Data Access API](https://developer.x-plane.com/sdk/XPLMDataAccess/)
- [XPLM Plugin API and messages](https://developer.x-plane.com/sdk/XPLMPlugin/)
- [XPLM Processing and flight loops](https://developer.x-plane.com/sdk/XPLMProcessing/)
- [XPLM Utilities and commands](https://developer.x-plane.com/sdk/XPLMUtilities/)
- [Developing Plugins](https://developer.x-plane.com/article/developing-plugins/)
- [Official X-Plane DataRef catalog](https://developer.x-plane.com/datarefs/)
- [Creating X-Plane FDR files](https://www.x-plane.com/kb/creating-fdr-files/)
- [X-Plane 12 desktop manual](https://x-plane.com/manuals/desktop/12/)

### FAA and investigation context

- [FAA AC 120-82, Flight Operational Quality Assurance](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_120-82.pdf)
- [14 CFR 121.344](https://www.ecfr.gov/current/title-14/chapter-I/subchapter-G/part-121/subpart-K/section-121.344)
- [Appendix M to 14 CFR Part 121](https://www.ecfr.gov/current/title-14/chapter-I/subchapter-G/part-121/appendix-Appendix%20M%20to%20Part%20121)
- [14 CFR Part 193](https://www.ecfr.gov/current/title-14/chapter-I/subchapter-K/part-193)
- [14 CFR 13.401](https://www.govinfo.gov/app/details/CFR-2025-title14-vol1/CFR-2025-title14-vol1-sec13-401)
- [NTSB recorder overview](https://www.ntsb.gov/news/Pages/cvr_fdr.aspx)

### Official ARINC catalog scope

- [ARINC 429 Part 1](https://saemobilus.sae.org/standards/arinc429p1-19-429p1-19-digital-information-transfer-system-dits-part-1-functional-description-electrical-interfaces-label-assignments-word-formats)
- [ARINC 573-7](https://saemobilus.sae.org/standards/arinc573-7-573-7-aircraft-integrated-data-system-mark-2-aids-mark-2)
- [ARINC 717-15](https://saemobilus.sae.org/standards/arinc717-15-717-15-flight-data-acquisition-recording-system)
- [ARINC 747-3](https://saemobilus.sae.org/standards/arinc747-3-747-3-flight-data-recorder)
- [ARINC 591](https://saemobilus.sae.org/standards/arinc591-591-quick-access-recorder-aids-system-qar)
- [ARINC 647A-2 FRED](https://saemobilus.sae.org/standards/arinc647a-2-647a-2-flight-recorder-electronic-documentation-fred)
- [ARINC 834A-1 ADIF](https://saemobilus.sae.org/standards/arinc834a-1-internet-protocol-based-aircraft-data-interface-function-adif)
- [ARINC 834-8 ADIF (superseded family reference)](https://saemobilus.sae.org/standards/arinc834-8-834-8-aircraft-data-interface-function-adif)
- [ARINC 822A-1](https://saemobilus.sae.org/standards/arinc822a-1-822a-1-ground-aircraft-wireless-communication)
- [ARINC 839 MAGIC](https://saemobilus.sae.org/standards/arinc839-839-function-definition-airborne-manager-air-ground-interface-communications-magic)
- [ARINC 600-20](https://saemobilus.sae.org/standards/arinc600-20-600-20-air-transport-avionics-equipment-interfaces)
- [ARINC 767-1](https://saemobilus.sae.org/standards/arinc767-1-767-1-enhanced-airborne-flight-recorder)
