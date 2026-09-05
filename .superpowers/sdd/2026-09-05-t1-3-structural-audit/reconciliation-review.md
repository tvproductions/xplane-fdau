# T1.3 governance reconciliation intent review

Date: 2026-09-05. Reviewer: independent bounded reconciliation reviewer.
Observed HEAD: `6c18ca6a58e8d98734decb8eacfd48d4971a192c`.

## Verdict

Accepted for the exact proposed correction population, subject to the precise
scope below. All five items are **corrections**, not enhancements. No proposal
requires new canonical behavior or invented approval/completion evidence.
Preserving D1.2's four checked gates and `verified` / `4/4` inventory state is
supported by the existing committed evidence, including the expanded wording.

No Critical, Important, or Minor finding remains in this document proposal.
This verdict is document reconciliation review only; it does not accept Task 3
code, assert that the audit now passes, satisfy T1.3 gates, or grant Git/release
authority. No implementation code was inspected or modified, no suite was run,
and no remote access occurred.

## Population and method

Applied the repository-owned `.agents/skills/gzs-intent-audit/SKILL.md` to the
five items in `reconciliation-proposal.md`. Their selection signal was the real
repository gate/disposition mismatches recorded in `task-3-reconciliation.md`.
The delivered surface in this review is the governance Markdown itself, not
runtime implementation. I read governing claims before comparing the ledger
and metadata, examined the committed D1.2 evidence contents, and checked raw
working/index/HEAD identity using local `git show` and Python `hashlib`.

The D1.1/D1.3 acceptance-source extraction defects and historical-plan rule
ownership are explicitly outside this review's implementation scope. They do
not justify editing either accepted design or historical D1 records. The T1.3
plan already requires agreement against the child's explicitly linked design
at `docs/superpowers/plans/2026-09-05-t1-3-structural-audit.md:283` and permits
explicit reviewed corrections at line 471 without rewriting completed specs,
fabricating approval, or altering the preserved D1 plans/evidence.

## 1. C2.4 and C3.3: correction

Owning intent: the approved canonical design's C2.4 section at
`docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md:1868`
contains five gates, including payload parity and failure dispositions
compatible with measurement quality/validity authorization. Its C3.3 section
at line 1894 requires every consumed observation, ordered derivation algorithm
inputs, and payload validation. Approval metadata is at line 9.

Observed mismatch: `BACKLOG.md:200` retains four C2.4 gates and omits the
failure-disposition gate; `BACKLOG.md:224` retains the older narrower lineage
formulations. The C2.4 inventory row at `BACKLOG.md:58` says `0/4`.

These requirements are not new design. The accepted D1.1 review explicitly
records payload compatibility, all-input lineage, and quality/validity
authorization corrections and confirms C2.4 agreement in
`.superpowers/sdd/2026-08-23-d1-1-canonical-design-approval/review.md:36`.

Exact route: copy the approved C2.4 and C3.3 gate statements, preserving their
order and punctuation after whitespace folding. Change only C2.4's denominator
to five. Keep all gates open and both children `specified`; retain the same
governing links. Do not alter the canonical semantic requirements or claim a
delivery gate from the existence of an approved design.

## 2. T2.2 and T3.1: correction

Owning intent: the approved and explicitly amended local-workflow design
records Jeff's 2026-09-05 canonical-workflow amendment at
`docs/superpowers/specs/2026-08-15-xplane-fdau-local-workflow-skills-design.md:9`.
Its exact acceptance sections start at lines 358 and 372. `BACKLOG.md:489`
and `BACKLOG.md:503` have older formulations.

The T2.2 change from blanket dirty-state rejection to stale-scope rejection
does not newly permit uncontrolled mutation: the governing body at line 202
already requires a clean or fully scope-reviewed dependency surface and fresh
revalidation. The supported Python matrix remains explicitly 3.12-3.14 at
line 188. T3.1's body at line 258 retains ambiguous-divergence rejection and
forbids published-history or merge-head rewriting, even though its compact
acceptance wording enumerates different examples. Exact gate reconciliation
does not remove those body requirements.

Exact route: replace the four and five backlog gate statements with the linked
design's exact statements. Retain `specified`, `0/4`, and `0/5`, all open gates,
explicit-only sync, fresh alignment proof, and separate release authorization.
Neither child is delivered by this wording correction.

## 3. C4.4: correction to an active acceptance sentence

Current authority is unambiguous. `AGENTS.md:23` separates release authorization
from ordinary requested synchronization, and `AGENTS.md:50` makes Git sync
explicit-only. The dated amendment at `HANDOFF.md:133` supersedes older no-push
wording for explicitly requested ordinary Git synchronization. The approved
adoption record at
`docs/superpowers/specs/2026-09-05-gz-skills-adoption-design.md:32`
records that policy, and its completed plan at
`docs/superpowers/plans/2026-09-05-gz-skills-adoption.md:49`
specifically says C4.4 must not prohibit routine authorized Git sync.

The backlog implements this policy at `BACKLOG.md:283`. The canonical design's
line 1954 retains `no push/tag/publication occurs`, so its acceptance sentence
does not express the current effective policy.

Preservation assessment: the adoption design's lines 46-47 and its plan's
line 23 instructed that completed adoption task not to rewrite accepted D1
designs or evidence. They do not establish a hash lock for the active canonical
C1-C4 specification, whose governance remains `active` / `approved`, nor do
they make the obsolete routine-push prohibition binding after the explicit
current-policy supersession. The approved T1.3 plan now authorizes reviewed
genuine corrections while preserving approved semantics and completed records.
Updating this one active acceptance sentence executes that authorization; it
does not infer a new policy or retrospectively change what D1.1 reviewed.

Exact route: replace only canonical-design line 1954 with the existing backlog
gate, including its ordinary-Git-sync qualification. Keep the other four C4.4
gates, all canonical contract text, and the original approval metadata intact.
Record the correction date, old/new sentence, and the existing amendment's
authority in T1.3's current plan/evidence. Do not relabel the old D1.1 review as
reviewing this new sentence or rewrite any D1 review/gate record. No additional
user approval is inferred or required for this already-authorized correction.

An engine exemption, restoration of the obsolete backlog push ban, a changed
release gate, or a claim that the adoption record authorized a push now would
be unsupported alternatives. None is necessary.

## 4. Four historical dispositions: provenance correction

Owning intent: historical dispositions must name a completed milestone,
replacement artifact, or replacement child under
`docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md:332`.
The approved T1.3 plan at line 280 requires a known milestone/child or an
existing replacement artifact. The four current line-5 dispositions describe
past work but lack the exact path/identity needed to retain that authority
chain in metadata.

Exact supported targets:

| Historical artifact (line 5) | Existing authority path to append | Evidence of relationship |
| --- | --- | --- |
| `docs/superpowers/plans/2026-08-16-xplane-fdau-architecture-propagation.md` | `docs/architecture/xplane_fdau_core_scope_amendment.md` | The same plan's Spec field and architecture/Task 1 identify the amendment as the delivered governing authority. |
| `docs/superpowers/plans/2026-08-22-q4xpcc-contract-handoff-readiness-authority.md` | `docs/superpowers/specs/2026-08-22-q4xpcc-contract-handoff-readiness-design.md` | The same plan's Spec field identifies the authority it registered, while its disposition expressly denies being a D1 implementation plan. |
| `docs/superpowers/plans/2026-09-05-gz-skills-adoption.md` | `AGENTS.md` | Task 1 expressly installs the canonical policy into AGENTS.md; its Global Constraints preserve all downstream states. |
| `docs/superpowers/specs/2026-09-05-gz-skills-adoption-design.md` | `AGENTS.md` | Authority reconciliation at line 34 names AGENTS.md as the canonical catalog/policy routing surface. |

Append, for example, `Current authority: ` followed by the exact backticked
path and a period, without replacing the original disposition. The authority
path is not a claim that a completed child or implementation plan exists.
Keep metadata governance/status and every execution-body byte unchanged.
These four explicitly reviewed metadata clarifications are separate from the
three frozen D1 plans; the latter must remain entirely byte-identical.

Calling any of these artifacts a newly completed roadmap child, supplying a
fabricated approval date, or rewriting an old execution narrative is
unsupported. An exact current-authority path is sufficient; no such expansion
is needed.

## 5. D1.2: correction; retaining all four checks is supported

Owning intent: the directly linked approved D1.2 design fixes the detailed
four-gate contract at
`docs/superpowers/specs/2026-08-23-xplane-fdau-acquisition-recording-projection-pinning-contracts-design.md:3972`.
The shorter `BACKLOG.md:305` formulations derive from the earlier readiness
design. The T1.3 plan explicitly chooses the linked design, not another
unlinked design's coverage, as acceptance authority.

This is not an inference from file presence or metadata. The already committed
review contains an eleven-pass, exact-revision ledger and explicit conclusions
against the expanded claims. Its accepted candidate is revision
`7e8490f4db9fe5b97603c0e0f9d516d2a14d1cd5`, with design SHA-256
`e7a2385d0cded8c2dd76bb40935470fe17857dd97f4dd2ffbc064694a5548975`.
The current detailed design is byte-identical to that exact accepted revision.

Evidence base below is
`.superpowers/sdd/2026-08-23-d1-2-acquisition-recording-projection-pinning-contracts/`.

| Expanded gate | Existing committed evidence and actual design surface | Assessment |
| --- | --- | --- |
| 1: all four consumer plans; acquisition, continuity, fan-out, recording, recovery, replay, native projection, deployment, and conformance planning | `gate-1.md:10` covers the 32-family inventory, all 22 implementation children, and all four Slice 2 consumers; `review.md:49` expressly audits recovery/replay and future schema/conformance ownership; `review.md:286` passes complete coverage. The design's family table at line 137, four-consumer table at line 3889, and full child table at line 3905 are concrete delivered planning surfaces. | Supported. |
| 2: exact versions, fields, invariants, references, runtime outcomes, error/delivery ownership boundaries, future resources, closed failures, deterministic precedence | `gate-2.md:10` expressly records all these properties, runtime-inability separation, and future resource roots; `review.md:287` passes the detailed claim. Design lines 128 and 137 fix validation/family/resource ownership; its failure section at line 3012 and separation section at line 3935 fix the error and causal boundaries. | Supported. |
| 3: installed-wheel and reproducible bundle, independently trusted expected pins, mode metadata, file hashes, conformance, and closed-world proof without a current release | `gate-3.md:10` explicitly covers both modes and every expanded pin/metadata/inventory/conformance clause; `review.md:288` passes them. Design line 3634 defines ExpectedDeploymentPin, line 3656 prohibits candidate-derived trust, and line 3816 fixes the ordered closed-world procedure; line 3846 prohibits fabricated current artifacts or receipts. | Supported; these are reviewed future verification contracts, not a claim of running an installed artifact. |
| 4: accepted independent review; native FDR/ARINC/FDM-FOQA/q4xpcc/client boundaries; binding input; no downstream implementation/adoption/release advancement | `gate-4.md:10` pins the accepted revision and reports all A1/R1/P1/S/F1 rows still at zero gates, including truthful blocked licensed-source children. `review.md:289` and `review.md:333` explicitly cover the ownership and no-delivery boundaries. Design line 22 declares binding future input; lines 35, 3600, 3620, and 3905 fix the boundaries and complete child mapping. | Supported. Preserve its historical D1.3 state statements as historical evidence, not current state. |

The gate-4 push/tag/publication wording says D1.2 supplies no such gate or
authorization. It does not reverse the later explicitly authorized ordinary
Git-sync policy; current HANDOFF makes that historical/current distinction
expressly. Copying the detailed gate with its existing evidence does not claim
that D1.2 authorized a push or that present ordinary synchronization is banned.

Exact route: copy all four detailed design statements into the D1.2 backlog
section; retain all four existing checkmarks, evidence links, `verified`, and
`4/4`. Leave the D1.2 detailed design, every D1 plan, all D1 evidence, and the
approved T1.3 supplement unchanged. No new D1 completion/review artifact or
retrospective verification is needed. The required new verification belongs
to T1.3: prove exact statement/count agreement and preserved historical bytes
on the corrected candidate before its own gate closure.

## Byte verification and handoff limits

Read-only Python compared `Path.read_bytes()` with `git show :<path>` and
`git show HEAD:<path>` without newline normalization. All rows below had
working = index = HEAD:

| D1.2 artifact | SHA-256 |
| --- | --- |
| `review.md` | `b13ca6a5a50b92ba4b29f4bedee6dbfd220b978bd09c11f65fe0738e6ee9f2b3` |
| `gate-1.md` | `5a644bd1f32750a9a11208dc0dafe1c0493ec2504ead2242354a5503a76a5013` |
| `gate-2.md` | `64b8889f15974fff4b9bf8c6ed09ead7f70e2db0eda55570d4bfe3524b102668` |
| `gate-3.md` | `189e6a9d48b7235f2e2bf5e92d59a4b9ed1422bec25d1c35016ebd66496d2bfa` |
| `gate-4.md` | `de26781328c3faa26a9f5ac6d16ab61643701937696f7869151c848874e074e6` |
| Detailed design | `e7a2385d0cded8c2dd76bb40935470fe17857dd97f4dd2ffbc064694a5548975` |
| Historical plan | `9b3c3a2c984f4536730c72c3479577b86707b03e50fca8d3e13f5a50ed80343f` |

The T1.3 approved supplement also matched working/index/HEAD with SHA-256
`f9586a102c34acb39e3afe2b20086ba758964f23b8263324c86f02ccc6e52441`.
No protected artifact was changed by this review. Only this report was written.

The external temporary original review reports are provenance referenced by
the committed D1.2 review; I did not rely on their presence or re-run the
historical eleven-pass review. This review establishes sufficiency of existing
committed design-acceptance evidence for the exact wording reconciliation,
not a new runtime, artifact, release, or comprehensive design certification.
