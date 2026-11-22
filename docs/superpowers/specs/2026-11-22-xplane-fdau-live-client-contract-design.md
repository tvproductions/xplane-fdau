# FDAU Client Contract Design Amendment

- **Governance:** active
- **Status:** draft
- **Date:** 2026-11-22
- **Decision owner:** Jeff / tvproductions
- **Roadmap epic:** `A1`
- **Roadmap children:** `A1.5`, `A1.7`, `A1.9`
- **Approval:** —

## Client contract at a glance

Configure a session, then submit observations or subscribe to its outputs. Every capture client identifies its source, preserves the type, shape, timing and status it actually received, and reports known capture loss. FDAU interprets accepted observations using pinned bindings, preserves their lineage, evaluates evidence quality and delivers frames according to the configured policy. Clients own their host connections and schedule calls. FDAU supplies the shared acquisition and recording rules. Its sinks distinguish delivery, checkpoints and published output. Replay, format adapters and FDM/FOQA analysis consume that shared evidence.

## Authority and scope

This draft proposes an amendment to the [approved acquisition, recording, projection and pinning design](2026-08-23-xplane-fdau-acquisition-recording-projection-pinning-contracts-design.md). The [core scope amendment](../../architecture/xplane_fdau_core_scope_amendment.md#ports-and-external-clients) owns the simulator and transport boundary. The [canonical measurement design](2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md#raw-observation) owns observation shape and identity. The [original provider analysis](../../architecture/xplane12_virtual_fdau_ecosystem_design.md#17-provider-semantics) describes the two principal live X-Plane integration profiles, Web API and XPPython3. A client can use either profile or compose both under their declared source identities.

Obligations follow the port a client uses. A source adapter implements the observation-side contract, including the applicable loss-reporting rules. A client that uses a subscriber or recording port meets that port's delivery and lifecycle contract. The same public ports can serve live, replay and fixture sources with the appropriate evidence and configuration. The proposed capture-loss event and continuity fields apply to the planned acquisition bundle. C3.2 continues to deliver the sample model, schema and interchange for the initial contract-kernel bundle.

Transport, capture-buffer implementation and clock reading stay with the caller. FDAU calls are synchronous, and callers serialize state-changing calls for a session. Each client project governs its own dependencies. Client-side modeling objects are translated to FDAU-owned records or standard-library values at the port.

### Pydantic and the domain boundary

The [adopted starter policy](https://github.com/tvproductions/gz-skills-first-starter/blob/e0b752fcc13b87ec7868fe0b0f85badefdb6bf52/docs/engineering/python.md#L157) permits Pydantic. [gzkit's architecture audit](https://gzkit.readthedocs.io/en/stable/governance/advisory-rules-audit/) records its explicit core allowlist. For FDAU, Jeff reaffirmed the [standard-library-only runtime](../../architecture/xplane_fdau_core_scope_amendment.md#python-compatibility-policy) on November 22, 2026 so the same dependency-free wheel serves XPPython3 plugins and standalone clients. The [canonical design](2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md#public-api-and-errors) specifies the public dataclasses and wire semantics.

An independently deployed Web API client may use Pydantic under its own policy. It translates its data to FDAU-owned types at the port. An XPPython3 adopter uses the `reproducibly_bundled` deployment mode. Its build verifies the exact version and SHA-256 of the published PyPI wheel, derives the complete `xplane_fdau` package inventory from it, and bundles those files byte-for-byte. The plugin and its bundled dependency run on the embedded Python 3.12 standard library. The adopter proves the delivered build in XPPython3. The public contract applies across deployment modes.

## Shared acquisition contract

| Boundary | Client preconditions | FDAU postconditions |
| --- | --- | --- |
| Configure a source | Supply the exact demanded profile and applicable binding pins, the actual provider and adapter identity, and available source capabilities and limitations. Operate against the accepted stream, acquisition phase and cadence resolution. | Resolve the demands against the declared sources. Reject incompatible requirements with the applicable resolution reason. Pin the accepted configuration, source context, and epoch. |
| Submit an observation | Submit an owned `RawObservation` against the active session, stream and epoch. Preserve resource identity and selection, observed type and shape, value or explicit absence, and the client receipt clock and time. Supply source clock, sequence, cycle or phase only with supporting evidence. | Return the existing `IngressOutcome`. Acceptance pins the exact observation and admits it to the session's evidence. Rejection identifies the failure and leaves the accepted-observation history intact. |
| Change source context | Report a reconnect, provider replacement or source restart through the session boundary before submitting observations under the replacement context. Use the effective epoch and generations granted by FDAU. | Apply the existing lifecycle and generation rules. Keep the previous and replacement evidence distinct. Reject submissions that use a stale context. |
| Retain and deliver | Respect the accepted delivery and retention policy. Keep each handoff in its appropriate session and consume delivery and recording outcomes. | Apply the configured normalization and quality policy. Preserve raw lineage and disclose sink-specific delivery, loss and persistence. `accepted`, `delivered`, `checkpointed` and `committed` retain their distinct meanings. |

### Live X-Plane integration profiles

| Case | Web API client | XPPython3 client |
| --- | --- | --- |
| Resource identity | Resolve session-scoped numeric IDs into the configured resource identity. Rediscover and report the new context on reconnect where the session rules require it. | Resolve DataRef names in the live simulator and keep opaque handles inside the client. Revalidate affected handles on a relevant source change. |
| Timing and update behavior | Timestamp an update at client receipt. An omitted value in a change-only update creates no raw observation and does not refresh an older observation. A later authorized resampling operation may refer to the original evidence. | Timestamp the actual read. Preserve cycle and callback phase when available. Capture the observed array length even when it differs from the requested length. |
| Status and loss | Preserve transport or source degradation as evidence. A disconnect or an undelivered server update can leave an observed gap with unknown cause or count. | Use explicit orphaning evidence when present, even when reading the DataRef yielded zero. Keep XPLM calls on their permitted thread and copy only the capture data needed by the caller's handoff. |

Each source declares what it can actually supply. For example, a demand requiring a specific flight-model phase can be rejected for a source unable to observe that phase. A client that satisfies a different accepted profile can still conform to the shared contract. Configured capabilities and submitted evidence determine admission and outcomes for every source.

## Proposed capture-loss operation

Use a dedicated synchronous operation `CaptureLossIngress.report(notice: CaptureLossNotice) -> CaptureLossOutcome`. It records discarded observations through the existing `AcquisitionLifecycleEvent` family, with a new `capture_loss` kind and notice-shaped detail. FDAU creates the event and owns its receipt timing, lifecycle sequence and hash. The client owns the factual assertion that it discarded the observations and the time at which it detected the loss.

`CaptureLossNotice` is an immutable input value. These are its proposed fields in semantic order:

| Field | Type and meaning |
| --- | --- |
| `notice_id` | `Uuid` allocated by the client and reused for an exact retry. Unique within the acquisition session. |
| `acquisition_session_id` | `Uuid` of the session that was to receive the discarded observations. |
| `configuration` | Exact `RecordRef` to the acquisition configuration at the loss boundary. |
| `epoch_id` | `Uuid` of the epoch affected by the loss. |
| `stream_id` | `Uuid` of the affected stream in the pinned configuration. One notice covers one stream and epoch. |
| `reporter` | `ProducerIdentity` of the client reporting the loss. |
| `detection_clock` | Host-monotonic `ClockDomain` used by the reporting client. Its producer instance identifies the reporter and its domain ID equals the affected stream's declared clock domain ID. |
| `detected_at` | `ClockReading` on `detection_clock`. The reading marks detection, including when a discarded value's specific capture time is unknown. |
| `dropped_observation_count` | Positive `UInt63`. Count each discarded input that would have become one raw observation for this stream. An array-valued observation counts once. |

### Admission and ordering

1. A notice covers observations the adapter actually captured and then discarded before submitting them. A client must count each discarded observation once. A client that can prove a disruption but cannot attribute an exact count to a stream reports the applicable source degradation and preserves the limitation. Continuity can still identify gaps and unmatched slots from the evidence it receives.
2. Submit the notice while the session is running under the affected configuration and epoch, before advancing that context or requesting stop. Within that stream, deliver the notice before resuming submission of readings captured after the discarded batch. A final notice is valid even if no later observation arrives.
3. An exact retry of an accepted `notice_id` returns the original event reference with no new event or increment. Reuse of that ID with changed fields is a contract validation error at `/notice_id`. Exact retries remain readable through the same session instance after the active epoch closes. New notices for inactive sessions, configurations, epochs or streams are rejected.
4. A structurally malformed notice raises the established contract error for the first failing field. For a well-formed new notice, return `accepted` with `notice_id` and `event: RecordRef`, or `rejected` with `notice_id` and `failure: FailureEvidence`. A rejection appends no lifecycle event and changes no capture-loss count. Use acquisition-domain failure evidence in phase `observe`: `session_state_invalid` for a session outside `running`, `generation_conflict` for a stale configuration or epoch, `source_unavailable` for an undeclared stream, and `binding_mismatch` for a clock inconsistent with the affected stream or reporter. Check in that order after identity and retry handling.
5. FDAU keeps accepted raw, sample and frame sequences contiguous under the approved range rules. A capture-loss event advances the lifecycle sequence and leaves the session `running`. For example, after accepted raw sequence 40, a notice reporting three discarded readings followed by the next accepted raw observation produces raw sequence 41. The notice creates no placeholder observation. `detected_at` stays distinct from the FDAU receipt time for the notice.

### Continuity and recording consequences

- FDAU derives `capture_loss_count: UInt63` for each binding result from accepted `capture_loss` events scoped to its configuration, stream and epoch coverage. The demand item count sums its distinct covered streams. The same stream serving two demands may appear in each demand's result. Session-wide reporting counts its underlying events once. Computed counts outside `UInt63` fail validation.
- Keep the explicit count visible even when cadence satisfies the profile. Expected-slot gaps, explicit capture loss and downstream sink drops use their own evidence and counts. An accepted notice alone creates no failure or stop directive. The existing configured continuity and required-sink policies determine the session's disposition.
- Canonical archive and replay use the existing lifecycle-event lane. A checkpoint covers the notice when its event is in that checkpoint's validated prefix. Replay preserves the original report, sequence, timing and hash and submits no fresh live loss claim. Exercise this at the recording and replay closure milestone `R1.7`.

## Alternatives considered

- **Use provider audit bytes.** They can preserve client diagnostics but have provider-specific contents and retention semantics. Core continuity cannot derive a common count from that envelope.
- **Infer all capture loss from cadence.** This uses an existing metric, but source pauses, change-only updates and buffering can produce the same observed intervals. A final discarded burst can have no later reading that identifies its cause.
- **Add a typed lifecycle event through a separate ingress operation.** This is the proposed approach. The event carries the same meaning for every capture adapter and uses existing lifecycle ordering, archive and replay machinery. It adds a version-1 event variant and two continuity projections before those families are delivered.

## Acceptance criteria

### A1.5 — Source/session lifecycle and epoch transitions

- Exercise source-context validation with synthetic Web API and XPPython3 observations. A stale-context observation is rejected after a context change. Verify the composed public observation port under A1.9.
- Accept an exact capture-loss notice, including a notice immediately before session stop with no subsequent raw observation. Reject inactive context, wrong stream or reporter clock, zero or out-of-range count, and changed-body reuse of a report ID. Return the same event and count on exact retry. Verify that the accepted raw sequence stays contiguous across the notice.

### A1.7 — Continuity evaluator and continuity report

- In a session that still meets its cadence requirement, report an explicit capture loss of three and keep the existing sufficiency result. A separate sink drop increments only delivery drop evidence. A cadence gap with no matching notice creates no exact capture-loss count.
- Validate attribution to the correct configuration, stream and epoch, including one source serving multiple demand items. Verify exact report identity and count overflow rejection with a supplied event closure.

### A1.9 — Acquisition-session orchestration and installed closure

- Use the same installed FDAU public session interface with a Web API–shaped fake client and an XPPython3–shaped fake client. Give both adapters equivalent admissible evidence and compare measurement, quality and delivery decisions while preserving distinct provenance. Exercise a change-only omission, known orphaning, explicit capture loss, and a stalled fake sink without importing a simulator, network, or client module.
- Bind the common cases to the pinned SDK-independent FDAU conformance evidence. Each consuming build runs its adapter translation tests against the exact FDAU artifact it deploys. The recording closure subsequently proves exact checkpoint and replay preservation under `R1.7`.
- Include the [plugin deployment checks](../../architecture/q4xpcc_phase_24a_contract_handoff.md#future-deployment-proof-undelivered) in the consuming plugin's evidence. Qualify the selected `PythonPlugins/PI_<name>/` bundle on XPPython3 4.8.0. Prove offline startup and check the effective FDAU import origin with different pins in both plugin load orders.
