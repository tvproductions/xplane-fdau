# D1.2 Acquisition, Recording, Projection, and Pinning Contract Design Review

- **Child:** `D1.2`
- **Gate:** —
- **Kind:** review
- **Result:** accepted
- **Date:** 2026-08-23
- **Subject:** Independent acquisition, recording, projection, and pinning contract design review

## Final accepted candidate

- **Revision:** `7e8490f4db9fe5b97603c0e0f9d516d2a14d1cd5`
- **Subject:** `docs: close D1.2 tenth review findings`
- **Design:** `docs/superpowers/specs/2026-08-23-xplane-fdau-acquisition-recording-projection-pinning-contracts-design.md`
- **Length:** 3,991 lines
- **SHA-256:** `e7a2385d0cded8c2dd76bb40935470fe17857dd97f4dd2ffbc064694a5548975`
- **Final review:** `C:\tmp\d1-2-independent-review-11.md`
- **Assessment:** **ACCEPTED** — 0 Critical, 0 Important, 0 Minor, no required correction, and no unresolved load-bearing ambiguity.

The accepted revision is contract-only architecture input. It fixes the future
A1/R1/P1 identity, acquisition, continuity, fan-out, recording, recovery,
replay, native-FDR projection, failure, deployment, and portable-receipt
boundaries. It does not implement or deliver those contracts.

## Exact review scope and method

The eleven review passes were independent, read-only, start-to-finish audits
of the complete candidate at each reviewed revision, rather than diff-only
checks. The final pass read all 3,991 candidate lines and every line of the
zero-context `HEAD^..HEAD` diff: 202 insertions, 51 deletions, 253 changed
candidate lines, and 289 diff-output lines.

Across the review sequence, the authority and supporting scope comprised:

- `AGENTS.md`, `HANDOFF.md`, `ROADMAP.md`, and `BACKLOG.md`;
- `docs/architecture/xplane12_virtual_fdau_ecosystem_design.md` and
  `docs/architecture/xplane_fdau_core_scope_amendment.md`;
- the completed identity/FDR-kernel migration design and plan;
- the approved canonical measurement-contract design;
- the q4xpcc Phase 24A contract-handoff-readiness design;
- the active D1.2 plan, Task 2 Step 0, its four rulings, the Task 1 and Task 2
  reports, the Task 2 brief, and the ignored progress ledger;
- all eleven independent whole-design reports preserved at
  `C:\tmp\d1-2-independent-review-1.md` through
  `C:\tmp\d1-2-independent-review-11.md`; and
- the complete design and applicable correction diff at every reviewed
  revision.

The audits covered all 32 new-family inventory rows, all 22 A1/R1/P1 child
coverage rows, every A1.1-A1.9, R1.1-R1.7, and P1.1-P1.6 identity and
cross-family invariant, and all four q4xpcc Slice 2 consumers. They checked
exact fields and tagged variants, family/version/self-hash identity, reference
and definition closure, lifecycle and ledger sequences, runtime outcomes,
closed failure vocabularies and reason-first precedence, checkpoint/recovery/
replay stress paths, artifact/content identity, native projection causality,
future schema/conformance ownership, and deployment pinning. They also audited
the canonical/native-FDR, provider/client, XPLM/XPPython3/Web API, q4xpcc,
ARINC, FDM/FOQA, adoption, and release boundaries.

## Complete reviewed-revision ledger

| Pass | Reviewed revision | Design SHA-256 | Result and exact counts | Following resolution wave |
| --- | --- | --- | --- | --- |
| 1 | `461a054aa2d498b27d46a1605c605fdfcd28ab46` | `1621f54e909a8eb23ea3560f708ff502452019fe0175626ed7b80d4ba5b7f0b9` | NOT ACCEPTED — 1 Critical, 17 Important, 1 Minor | `d623b801a1b48bc88f7586eb163c8a6994c8ea71` |
| 2 | `d623b801a1b48bc88f7586eb163c8a6994c8ea71` | `2de4b192fb58b4b98dec8e342402ac91809409aa85985a7a3e212c59f3a8afdb` | NOT ACCEPTED — 0 Critical, 11 Important, 0 Minor | `90952e371b18ae19129b39ffc9a496b89f30c111` |
| 3 | `90952e371b18ae19129b39ffc9a496b89f30c111` | `e75b23d907fc629e0624b58575ddb9e01277ef5138aef0ad4325975fcd1c79c1` | NOT ACCEPTED — 0 Critical, 6 Important, 0 Minor | `4a7a697db958a23e27a205e5a18fcf893ae916b9` |
| 4 | `4a7a697db958a23e27a205e5a18fcf893ae916b9` | `af47c73b7e7d051894be0378305d3d307c73f77242d2093758f48eda8f5f1039` | NOT ACCEPTED — 0 Critical, 6 Important, 0 Minor | `38b3b44857a0127184ab39f82c752e3433426a59` |
| 5 | `38b3b44857a0127184ab39f82c752e3433426a59` | `fa661dd79ec669d341a37bb072a9ba9bd5fb3078902ad8b094f09de2c8aafcac` | NOT ACCEPTED — 0 Critical, 4 Important, 1 Minor | `e89313a5a91ac2cf7801eb31ba9218f7e02f8085` |
| 6 | `e89313a5a91ac2cf7801eb31ba9218f7e02f8085` | `8ce668d8e8f7af3208f59a2275fb4d7796fee7ecd8bd1241221798f53eca5583` | NOT ACCEPTED — 0 Critical, 2 Important, 1 Minor | `0a473226a1b396fc6de8a81bb075dd4563b3a174` |
| 7 | `0a473226a1b396fc6de8a81bb075dd4563b3a174` | `05ae742b115196c13b1959ad0b1f1e33459826f46f1aad3dbd8ecdd7e3ee2581` | NOT ACCEPTED — 0 Critical, 4 Important, 0 Minor | `51bc1d2be4f9e4fd2a207759eba0973293d64d05` |
| 8 | `51bc1d2be4f9e4fd2a207759eba0973293d64d05` | `5657e3a2208cd8efbb8fab4291fa8eb1a9ba7e8b02976e0860b1c759a90f1b6a` | NOT ACCEPTED — 0 Critical, 2 Important, 0 Minor | `ba479c2d3f2f7b146af52d9e53cab326ee180164` |
| 9 | `ba479c2d3f2f7b146af52d9e53cab326ee180164` | `e54c3154ca0c1d1755ce96bd18547b8d426cc138f6dc92fdeb590d21c0555e92` | NOT ACCEPTED — 0 Critical, 2 Important, 0 Minor | `df86619ff8d7d2b3e0d23ec9b511b444219ad8c2` |
| 10 | `df86619ff8d7d2b3e0d23ec9b511b444219ad8c2` | `58dc72f05d68a2cc9bc1fa000e21fc4f2f5a99457780f41f4b786c9faa465af6` | NOT ACCEPTED — 0 Critical, 2 Important, 0 Minor | `7e8490f4db9fe5b97603c0e0f9d516d2a14d1cd5` |
| 11 | `7e8490f4db9fe5b97603c0e0f9d516d2a14d1cd5` | `e7a2385d0cded8c2dd76bb40935470fe17857dd97f4dd2ffbc064694a5548975` | **ACCEPTED — 0 Critical, 0 Important, 0 Minor** | None required |

## Exact findings by review pass

### Pass 1 — initial whole-design review

- C1: deployment receipt had no authoritative expected release pin.
- I1: consumer demand had replacement but no withdrawal/closure operation.
- I2: rejected atomic resolution could contain accepted outcomes with dangling
  selected-source identities.
- I3: required provider audit depended on an undeclared binding capability.
- I4: downsampling/resampling/aggregation did not pin the canonical-lineage
  transform algorithm.
- I5: the acquisition-session descriptor could not represent every valid
  resolution or demand replacement.
- I6: acquisition and replay lacked complete lifecycle state machines.
- I7: generic fan-out lacked subscriber policy and one delivery-sequence scope.
- I8: continuity did not pin the delivery evidence behind its counts.
- I9: continuity classification and corroboration were incomplete.
- I10: checkpoint safe prefixes did not close referenced payloads/definitions.
- I11: recovery results could not retain discard authorization.
- I12: the artifact manifest omitted parent-required termination/recovery
  status.
- I13: first causal failure was not deterministic across independent endpoints
  and sinks.
- I14: projection mapping did not reference the authorizing profile item.
- I15: native-FDR omission and timing-loss policies were not faithfully
  representable in the projection report.
- I16: reproducibly bundled verification relied on unavailable installed
  metadata.
- I17: deployment families had no dependency-correct implementation owner.
- M1: operation outcomes lacked exact property names and variant invariants.

### Pass 2 — first complete correction re-review

- I1: acquisition profile omitted burst and transition-coverage policy.
- I2: resampling claimed an unpinned transform registry and unresolved
  interpolation authorization.
- I3: provider-audit retention had capability authority but no evidence ingress
  or archive reference path.
- I4: acquisition lifecycle had no terminal path after `opened` but before the
  initial epoch.
- I5: continuity could not represent the zero-delivery case.
- I6: continuity omitted connection changes and could not attribute recording-
  sink failures.
- I7: commit request and acquisition terminal event formed a causal cycle for
  required-sink commit failure.
- I8: repeated copies of one primary failure collided with the causal-position
  rule.
- I9: recovery requests were not constrained by declared recovery policy.
- I10: projection field results did not exhaustively cover profile mappings.
- I11: the A1.9 ownership correction impermissibly narrowed `I1.1`.

### Pass 3 — second correction re-review

- I1: continuity scope did not cover the complete configuration evidence
  lifetime.
- I2: cross-configuration transition coverage depended on an unidentified
  external closure.
- I3: provider-audit continuity could not identify the retained evidence set
  and sink graph.
- I4: the generic manifest recorded stopping intent rather than final
  termination status.
- I5: optional non-cleanup failures contradicted primary selection and optional-
  sink isolation.
- I6: `RecoveryResult` did not fix artifact-state array shapes, coverage, or
  ordering.

### Pass 4 — third correction re-review

- F1: fan-out close objects and continuity required different endpoint/stream
  universes.
- F2: mandatory transition closure required optional recording and retention.
- F3: provider-audit closure could not represent accepted evidence a sink
  failed to store.
- F4: acquisition-wide causal closure had no exact carrier or validator input.
- F5: recovery history exhaustiveness relied on an undefined mutable allocation
  ledger.
- F6: artifact-entry and publication tagged variants lacked exact wire shapes.

### Pass 5 — fourth correction re-review

- I1: provider-audit closure could not represent post-`stored` loss.
- I2: ordinary terminal sink histories were not anchored to the artifact-state
  ledger.
- I3: `omitted_by_policy` had neither a valid `ArtifactState` invariant nor a
  closed `SinkResult` outcome.
- I4: a published byte root could not carry the parent-required generic manifest
  content.
- M1: failure-aware validator input did not say whether referenced records
  repeated the separately supplied closure.

### Pass 6 — fifth correction re-review

- I1: a required sink partial solely from declared loss had no legal recording-
  result primary failure.
- I2: completed standalone native-FDR projection could not bind output bytes to
  a generic final artifact manifest.
- M1: the byte-root sidecar sealed/published invariant was not scoped to the
  published disposition.

### Pass 7 — breaker review after the five Task 1 waves

- I1: recording-orchestrator-only failure had no exact acquisition-terminal
  reason/primary propagation row.
- I2: projection report could not pin its recording descriptor and sink root.
- I3: the replacement offline-projection path had no identity-preserving
  operation contract.
- I4: preserved-partial byte-root sidecar required future failure/ledger state
  before its immutable prepublication seal.

### Pass 8 — Task 2 Step 0 carryover re-review

- I1: `RecordingSessionResult.termination_reason` had two incompatible exact
  values for orchestrator-only failure.
- I2: schema-v1 in-session projection still required an unavailable historical
  artifact manifest and had no supplying operation.

### Pass 9 — Task 2 Fix Round 1 re-review

- I1: reason precedence did not select a reason-compatible primary under mixed
  failures or an existing failure stopping intent.
- I2: native publication was irreversible before the mandatory successful
  projection report was fixed.

### Pass 10 — Task 2 Fix Round 2 re-review

- I1: acquisition-orchestrator `internal_failure` remained globally eligible
  but absent from the non-intent terminal matrix.
- I2: authorized same-session discard made completed native content required
  and prohibited in `SinkResult`.

### Pass 11 — final whole-design re-review

No Critical, Important, or Minor finding remained. No correction was required.

## Resolution waves and commits

Every correction commit changed only the D1.2 design. The active plan remained
parent-owned, untracked, and untouched throughout those waves.

1. `d623b801a1b48bc88f7586eb163c8a6994c8ea71` —
   `docs: close D1.2 contract review findings` — addressed pass-1 C1/I1-I17/M1
   with the independent expected deployment pin; activate/withdraw demand;
   proposed/activated resolution closure; source-retention capability;
   pinned resampling algorithms; versioned configurations; closed acquisition/
   replay lifecycles; subscriber policy and endpoint-stream sequencing;
   delivery-backed continuity; per-binding classification; checkpoint reference
   closure; self-hashed recovery requests; manifest status; global causal
   positions; projection authorization/loss accounting; mode-specific metadata;
   A1.9 ownership; and exact operation outcomes.
2. `90952e371b18ae19129b39ffc9a496b89f30c111` —
   `docs: close D1.2 re-review findings` — addressed pass-2 I1-I11 with burst/
   transition policy; transform-registry/interpolation closure; provider-audit
   ingress/archive evidence; initialization failure exit; zero-event ranges;
   connection and protected-sink continuity; acyclic stopping-before-commit
   order; failure-copy deduplication; recovery-policy admission; exhaustive
   projection field results; and restoration of the unchanged `I1.1` boundary.
3. `4a7a697db958a23e27a205e5a18fcf893ae916b9` —
   `docs: close D1.2 third review findings` — addressed pass-3 I1-I6 with one
   exhaustive report per configuration; exact predecessor transition closure;
   per-sink provider-audit closure; separate content and final manifests;
   outcome-specific primary eligibility; and exact recovery histories/tails.
4. `38b3b44857a0127184ab39f82c752e3433426a59` —
   `docs: close D1.2 fourth review findings` — addressed pass-4 F1-F6 with one
   immutable fan-out tuple universe; available/unavailable transition evidence;
   stored/missing provider-audit states; self-hashed `FailureClosure`;
   hash-chained `ArtifactStateLedger`; and exact content/publication/recovery/
   classification variants.
5. `e89313a5a91ac2cf7801eb31ba9218f7e02f8085` —
   `docs: close D1.2 fifth review findings` — addressed pass-5 I1-I4/M1 with
   post-store audit loss; ordinary/final ledger-head pins and explicit portable
   trust; closed policy omission; generic byte-root sidecars and projection
   linkage; and unambiguous failure-validator traversal.
6. `0a473226a1b396fc6de8a81bb075dd4563b3a174` —
   `docs: close D1.2 sixth review findings` — addressed pass-6 I1/I2/M1 by
   making declared-loss-only required partial nonfailing, removing the
   standalone projection variant while initially routing offline projection
   through ordinary orchestration, and selecting distinct published and
   preserved-partial sidecar rules. Pass 7 found the replacement offline path
   unimplementable and the preserved-partial sidecar temporally contradictory;
   those defects were carried into Task 2 Step 0.
7. `51bc1d2be4f9e4fd2a207759eba0973293d64d05` —
   `docs: close D1.2 carryover findings` — addressed pass-7 I1-I4 with exact
   recording-orchestrator acquisition propagation; required
   `recording_descriptor` on projection reports; complete removal of schema-v1
   offline/replay-through projection; and immutable sealed candidate semantics
   for preserved-partial sidecars.
8. `ba479c2d3f2f7b146af52d9e53cab326ee180164` —
   `docs: close D1.2 eighth review findings` — addressed pass-8 I1/I2 with one
   recording-reason precedence rule and a current-session prepublication
   canonical `input_content_manifest` reached only by live append and close-time
   cross-validation.
9. `df86619ff8d7d2b3e0d23ec9b511b444219ad8c2` —
   `docs: close D1.2 ninth review findings` — addressed pass-9 I1/I2 with a
   reason-first reason/primary matrix and a final-byte protocol in which whole-
   range preflight, root/report-member fixation, and sidecar admission all
   precede atomic native publication.
10. `7e8490f4db9fe5b97603c0e0f9d516d2a14d1cd5` —
    `docs: close D1.2 tenth review findings` — addressed pass-10 I1/I2 with a
    disjoint acquisition-orchestrator row before recording-orchestrator
    eligibility and one historical-content-after-authorized-discard rule across
    `SinkResult`, recovery/ledger histories, interrupted and terminal manifests,
    report retention, phase order, and replay exclusion.

Pass 11 independently confirmed every pass-10 target and all earlier rulings
closed at the final revision. It required no further design change.

## Acceptance-gate conclusions

| Gate | Result | Final review conclusion |
| --- | --- | --- |
| 1. One approved design fixes every A1/R1/P1 contract needed by all four q4xpcc Slice 2 plans | **PASS** | The 32-family inventory, 22-child coverage table, and four-row q4xpcc reconciliation are complete and preserve q4xpcc ownership of capability identity, tester policy, application orchestration, findings, and build/adoption evidence. |
| 2. Every family has exact identity/version, fields, invariants, references, outcomes, errors, ownership, and deterministic precedence | **PASS** | Canonical family dispatch, exact shapes, self-hashes, record/definition identities, lifecycle and ledger sequences, reference closure, tagged outcomes, closed failure vocabularies, and reason-first causal eligibility are fixed. The two pass-10 ambiguities are closed. |
| 3. Deployment proof is explicit and closed-world without fabricating a release | **PASS** | Independently trusted expected pins, exact wheel/metadata/conformance hashes, installed-wheel and reproducibly bundled modes, delivered namespace inventory, import-origin proof, standard-library runtime dependency proof, and fail-collecting receipts are exact. No current version, artifact, hash, release, or receipt is invented. |
| 4. Independent review finds no unresolved load-bearing ambiguity and all delivery boundaries remain closed | **PASS** | Finding counts are 0 Critical, 0 Important, and 0 Minor. Native FDR remains a lossy inward projection; ARINC and FDM/FOQA remain later repository-owned seams; adapters and q4xpcc adoption remain consumer-owned; implementation and release gates remain unsatisfied. |

## Final stress-path disposition

- Acquisition-orchestrator `internal_failure` has its own disjoint ordered row
  after required-sink/evidence failure and before recording-orchestrator
  failure. Initialization, configuration replacement, ordinary nonfailure
  stopping intent, existing failure intent, mixed orchestrators, exact copy
  equality, and validator recomputation all use that same matrix.
- Ordinary post-completion discard retains immutable content-manifest file/
  record evidence and an already-fixed successful native report. Exhaustive
  recovery input histories prove the sealed pre-discard graph; output histories
  and the greatest ledger head alone prove authorized deletion and current
  absence. Recovery-time interrupted and later terminal manifests are distinct,
  immutable, acyclic records.
- A discarded final manifest is historical integrity evidence, not availability
  or replay evidence. Replay remains invalid unless separately supplied live
  artifacts satisfy the complete selected graph closure.
- Published, published-with-loss, preserved-partial, pre-content discard,
  not-created, omitted-by-policy, not-applicable, report-failure, publication-
  failure, and admitted-failed-recovery paths retain mutually exclusive exact
  result and manifest shapes.

## Final independent verification evidence

Pass 11 freshly established the exact accepted identity and review shape:

- `git rev-parse HEAD` returned
  `7e8490f4db9fe5b97603c0e0f9d516d2a14d1cd5`;
- the candidate contained 3,991 lines and its SHA-256 was
  `e7a2385d0cded8c2dd76bb40935470fe17857dd97f4dd2ffbc064694a5548975`;
- `git diff --numstat HEAD^ HEAD -- <candidate>` reported 202 insertions and
  51 deletions;
- the exact placeholder scan found zero matches, and the inventory scan found
  32 family rows and 22 A1/R1/P1 coverage rows;
- the boundary scan found no `pytest`, `xpwebapi`, or `xplane-webapi` mention;
  every standards, native, q4xpcc, deployment, push, tag, and publication match
  was manually reviewed in context and preserved its boundary;
- `git diff --check HEAD^ HEAD` and
  `git show --check --stat --oneline HEAD` both exited zero; and
- `git status --short` named only the pre-existing parent-owned untracked D1.2
  plan. The reviewer edited, staged, committed, pushed, tagged, published, and
  released nothing.

## Result and authority boundary

Accepted at the exact final revision and SHA-256 above. The review records
contract-design acceptance only. It creates no runtime implementation, model,
schema, fixture, conformance corpus, wheel, sdist, archive, native-FDR output,
deployment artifact or receipt, A1/R1/P1/S/F1 child delivery, q4xpcc adoption,
G1 evidence, release, push, tag, or publication claim. All implementation,
schema, fixture, artifact, adoption, and release gates remain unsatisfied until
their separately governed future work supplies evidence.
