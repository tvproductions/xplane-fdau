# q4xpcc Phase 24A contract handoff

- **Purpose:** planning reconciliation only; this is not implementation,
  adoption, deployment, or release authority.
- **Source snapshot:** `f86c6f939f1fdbfd354660c432363b9aa7f8444d`.
  This pins the input documents read for the brief. It is not a release pin and
  does not claim that this brief existed at that revision.
- **Emission revision:** supplied separately in the clean delivery envelope as
  the actual committed `HEAD`, followed by the brief emitted from that `HEAD`.
- **Readiness condition:** q4xpcc may reconcile its Phase 24A specification and
  plans only after `D1.3` has verified evidence in
  [BACKLOG.md](https://github.com/tvproductions/xplane-fdau/blob/HEAD/BACKLOG.md#d13--reviewed-q4xpcc-phase-24a-handoff).
  At this Task 1 emission, `D1.3` remains `specified` at `0/4`.

## Authoritative inputs

| Input | Source state |
| --- | --- |
| [Parent ecosystem architecture](xplane12_virtual_fdau_ecosystem_design.md) | Imported provenance document dated 2026-08-09; its metadata remains `Draft for coordinated q4xpcc and xplane-fdau review`. |
| [Repository scope amendment](xplane_fdau_core_scope_amendment.md) | Approved 2026-08-16. |
| [Canonical measurement-contract design](../superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md) | Approved 2026-08-23. |
| [Acquisition, recording, projection, and pinning design](../superpowers/specs/2026-08-23-xplane-fdau-acquisition-recording-projection-pinning-contracts-design.md) | Approved 2026-08-23. |
| [D1 contract-handoff readiness design](../superpowers/specs/2026-08-22-q4xpcc-contract-handoff-readiness-design.md) | Approved 2026-08-22. |

Committed prerequisite evidence:

- `D1.1`: [accepted review](https://github.com/tvproductions/xplane-fdau/blob/HEAD/.superpowers/sdd/2026-08-23-d1-1-canonical-design-approval/review.md),
  gates [1](https://github.com/tvproductions/xplane-fdau/blob/HEAD/.superpowers/sdd/2026-08-23-d1-1-canonical-design-approval/gate-1.md),
  [2](https://github.com/tvproductions/xplane-fdau/blob/HEAD/.superpowers/sdd/2026-08-23-d1-1-canonical-design-approval/gate-2.md),
  [3](https://github.com/tvproductions/xplane-fdau/blob/HEAD/.superpowers/sdd/2026-08-23-d1-1-canonical-design-approval/gate-3.md), and
  [4](https://github.com/tvproductions/xplane-fdau/blob/HEAD/.superpowers/sdd/2026-08-23-d1-1-canonical-design-approval/gate-4.md), all dated 2026-08-23.
- `D1.2`: [accepted review](https://github.com/tvproductions/xplane-fdau/blob/HEAD/.superpowers/sdd/2026-08-23-d1-2-acquisition-recording-projection-pinning-contracts/review.md),
  gates [1](https://github.com/tvproductions/xplane-fdau/blob/HEAD/.superpowers/sdd/2026-08-23-d1-2-acquisition-recording-projection-pinning-contracts/gate-1.md),
  [2](https://github.com/tvproductions/xplane-fdau/blob/HEAD/.superpowers/sdd/2026-08-23-d1-2-acquisition-recording-projection-pinning-contracts/gate-2.md),
  [3](https://github.com/tvproductions/xplane-fdau/blob/HEAD/.superpowers/sdd/2026-08-23-d1-2-acquisition-recording-projection-pinning-contracts/gate-3.md), and
  [4](https://github.com/tvproductions/xplane-fdau/blob/HEAD/.superpowers/sdd/2026-08-23-d1-2-acquisition-recording-projection-pinning-contracts/gate-4.md), all dated 2026-08-23.

## Identity and boundaries

- Repository: `https://github.com/tvproductions/xplane-fdau.git`.
- Distribution: `xplane-fdau`; import namespace: `xplane_fdau`.
- Version `0.1.0` is unreleased. No push, tag, publication, release artifact,
  or consumer deployment is authorized by this brief.
- The approved Python policy is `>=3.12,<3.15`, verified on 3.12, 3.13, and
  3.14. Current metadata is still `>=3.12`; alignment is pending `T2.2`.
- Runtime dependencies must remain empty and the core standard-library-only.

`xplane-fdau` owns generic measurement and source-binding contracts,
normalization and acquisition, timing, acquisition quality and continuity,
generic fan-out, recording, recovery, deterministic replay, and native-FDR
projection. These capabilities are delivered only by their owning future
children; design ownership is not delivery.

External clients own simulator I/O, XPLM/XPPython3 and Web API adapters,
connections, plugin lifecycle, and concrete application integration. q4xpcc
owns its cards, missions, application orchestration, operational findings,
guidance, action authorization, and q4xpcc-specific definitions and policy.
Acquisition sufficiency describes evidence quality and continuity; it is not a
q4xpcc operational or performance finding.

ARINC codecs and profiles are later local, edition-pinned, licensed-source
work. FDM/FOQA-oriented mechanics are later local `F1.*` work; organizational
identity custody, authorized review, corrective-action authority, protections,
and regulatory or approved-program claims remain external.

## Intended contract and conformance surface — undelivered

The future canonical semantic package roots are:

```text
xplane_fdau/contracts/
xplane_fdau/measurements/
xplane_fdau/bindings/
xplane_fdau/acquisition/
xplane_fdau/schemas/
xplane_fdau/conformance/
```

The byte-identical future schema roots are `xplane_fdau/schemas/` and
`docs/schemas/`. The five canonical version-1 stems are
`measurement-catalog`, `source-binding-catalog`, `raw-observation`,
`measurement-sample`, and `measurement-frame`.

The D1.2 [new-family inventory](../superpowers/specs/2026-08-23-xplane-fdau-acquisition-recording-projection-pinning-contracts-design.md#new-family-inventory-and-future-resources)
is authoritative for all 32 additional family stems and their owning `A1`,
`R1`, or `P1` children. The future conformance roots are:

```text
xplane_fdau/conformance/v1/
tests/fixtures/contracts/v1/
docs/contracts/conformance/v1/
```

Every package, schema, family, fixture, corpus, and runner target in this
section is intended and undelivered. The future Python verification command is:

```console
python -m xplane_fdau.conformance --manifest PATH --output PATH
```

Exit `0` means every valid-manifest case passed, `1` means the corpus was valid
but at least one case failed, and `2` means invocation, unreadable-corpus, or
invalid-manifest failure; exit `2` produces no result document. Installed-wheel
verification resolves the packaged manifest with `importlib.resources`, never
a checkout mirror. The three deployment families and this exact Python runner
spelling are delivered by `A1.9`; `C4.4` does not deliver or imply an acquisition
deployment receipt.

## Future deployment proof — undelivered

A consumer must obtain an `ExpectedDeploymentPin` independently from a trusted
build input or signed/reviewed release index, never from the candidate wheel or
delivered namespace. It pins exact distribution version and source revision;
wheel filename, media type, byte length, and SHA-256; pinned `METADATA` and
`WHEEL` member lengths and hashes; and the conformance-manifest path, length,
and hash.

After the whole wheel matches that trusted pin, verification derives the whole
`xplane_fdau/**` namespace inventory from the pinned wheel, rejects missing,
changed, or extra non-cache files, requires one verified import root, checks
the supported interpreter, and requires empty `Requires-Dist`.

`installed_wheel` verifies delivered `.dist-info/METADATA` and
`.dist-info/WHEEL` bytes against the pin. `reproducibly_bundled` verifies those
exact members inside the pinned wheel, delivers the complete package inventory,
and does not deliver a copied `.dist-info` tree. A verified portable receipt is
created only from a concrete matching artifact. This brief fabricates no wheel,
version pin, revision pin, file hash, conformance hash, or receipt.

## Native X-Plane FDR boundary

Native textual FDR v3/v4 remains a deliberately lossy replay format and
recording sink, not the canonical FDAU archive. The intended schema-v1
canonical-to-native projection contract is itself undelivered and supports
only live, in-session projection tied to the acquisition and recording closure.
It defines no standalone or offline projection operation. Offline projection
from a canonical archive requires a later, separately reviewed versioned
contract.

## Exact Phase 24A plan reconciliation

| q4xpcc plan | Required planning amendment |
| --- | --- |
| `2026-08-08-phase-24a-slice-2a-capability-ledger.md` | Keep the five-kind interface ledger, relevance/disposition accounting, and observed-interface authority in q4xpcc. Replace copied measurement semantics with versioned FDAU `MeasurementDefinition` and `SourceBinding` references; treat observed metadata as adapter input/provenance. |
| `2026-08-08-phase-24a-slice-2b-c172-tester-contracts.md` | Keep profiles, cards, task conditions, cues, observation objectives, and immutable card resolution in q4xpcc. Translate objectives to pinned FDAU profile items and required/optional consumer demands; include the demand record ID, generation, and content hash plus profile, measurement, and binding definition IDs, revisions, and hashes in resolved-card-run identity. |
| `2026-08-08-phase-24a-slice-2c-capture-evidence-engine.md` | Use future FDAU observation ingress, demand resolution, sessions, frames, fan-out, recording, continuity, archive, and terminal results. Keep q4xpcc card/session protocol, application policy, environment interpretation, findings, guidance/authorization, aircraft affinity, and trust/recovery policy. Keep initial cadence thresholds as q4xpcc evidence policy. |
| `2026-08-08-phase-24a-slice-2d-c172-runner-live-acceptance.md` | Keep q4xpcc orchestration, coverage joins, runbook, corroboration, and session control. Compose consumer-owned Web API and XPLM/XPPython3 adapters, correlate FDAU session/archive/projection/deployment identities into coverage, verify exact pins, and keep acquisition sufficiency separate from operational findings. |

Planning may reference these intended contracts and verification steps after `D1.3` verifies. It must not import nonexistent APIs, copy draft schemas, invent fixtures or receipts, or claim delivery.
Contract-model, schema, fixture, and runtime adoption still requires `C4.4` (`I1.1`); live XPLM acquisition adoption still requires `A1.9` (`I1.2`). The canonical vertical slice, release gate, push, tag, publication, and release remain closed.
