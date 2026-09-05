# SDD ledger — plan: docs/superpowers/plans/2026-09-05-t1-3-structural-audit.md

User approved revised plan and policy supplement on 2026-09-05 by saying
continue after the explicit combined approval question. Work is isolated on
t1-3-structural-audit. Base: eac980afe5cec66a3ac55cb3774f49bafa4c3466.

## Preflight interface scan

| Tasks | Producer / consumer | Finding |
| --- | --- | --- |
| 1 | Typed loading, parsing, policy / its tests | Source facts require named typed fields chosen within the planned model scope |
| 2 | Structural rules / matrix tests | Consistent |
| 3 | Governing link rules / lifecycle reference tests | Consistent with approved supplement |
| 4 | Evidence slots and effective lifecycle / Git fixture tests | Consistent after reviewed corrections |
| 5 | CLI integration / reports and closure | Consistent; source evidence committed before verified state |
| 1,2 | AuditLoad and source facts / structural rules | Sequential; publish types before Task 2 |
| 1,3 | Source facts and artifact parser / adherence | Sequential; independent artifact failures retained |
| 1,4 | AuditPolicy and evidence metadata parser / lifecycle and Git checks | Sequential; policy committed before loading |
| 1,5 | AuditLoad / report composition | Preserve v1 serialized fields |
| 2,3 | Structural identities / artifact joins | Skip ambiguous joins, retain independent findings |
| 2,4 | rules.py / lifecycle functions | Sequential ownership, no concurrent edits |
| 2,5 | structural_findings / CLI | Wire only at Task 5 |
| 3,4 | Governing artifact facts / lifecycle requirements | Historical admission is explicitly separate |
| 3,5 | adherence_findings / CLI | Wire only at Task 5 |
| 4,5 | evidence and lifecycle / CLI, committed gates | Verify index then HEAD; never fabricate metadata |

## Verification policy

Unittest only. Full repository quality gate plus focused hidden-tool Ruff/ty
and strict MkDocs before task commits; focused iteration tests first. Use uv
with escalation where the sandbox cannot execute the installed binary. Git
commits/worktree metadata require escalation. No remote writes authorized.

## Task status

- Approval record: committed e082ebd; full quality and strict MkDocs passed.
- Task 1: complete; accepted final review at 46df78f.
- Task 2: complete; accepted final review at 837f143.
- Task 3: complete; accepted final review at 5882bb4.
- Task 4: complete; accepted final review at db51c61.
- Task 5: implementation and task review complete; whole-branch re-review
  accepted 1211466 with all four findings addressed. Operational evidence and
  HEAD-backed verified 4/4 closure are complete. Local integration awaits user selection.

Independent draft review closed both lifecycle findings with no remaining
Critical, Important, or Minor issue before user approval.

Task 1: Ruling: Move newly added source-fact extraction into parse_sources.py
with public parse_roadmap_sources, parse_backlog_sources, and
parse_artifact_sources functions — the existing strict parser was already
about 670 lines and the new extraction adds about 230, so the separation keeps
each responsibility reviewable without changing the approved behavior — if
wrong, the cost is moving the extraction back and adjusting its imports.

Task 1: initial GREEN evidence reported: 37 parser/model/audit tests and 7
policy tests; focused split and final verification remain before task review.

Task 1: final implementation evidence: 295 unittest tests, 94% coverage,
focused Ruff/format/ty and secrets checks, full quality and strict MkDocs pass.
Review package e082ebd..0209135.diff dispatched to t1_3_review1.

Task 1 review: spec not compliant / quality needs fixes, no Critical or Minor.
Open Important findings: known child parse context lost; exact source titles
and lines incompletely asserted; use TemporaryDirectory for copied fixtures;
translate Git launch OSError into isolated policy.unavailable with chaining.
All four sent to original implementer in one fix dispatch. No finding waived.

Task 1: fix round 1/5 (4 addressed, 0 open; commits 0209135..46df78f).
Task 1: complete (commits e082ebd..46df78f, review clean).
Task 2: dispatch preparation; requirements and source interfaces ready.

Task 2: implemented 2ae2853..56a3050; 53 focused tests/full quality passed.
Task 2: review dispatched to t1_3_review2 with review-2ae2853..56a3050.diff.
Controller integration check: load_audit has 0 findings; structural_findings
reports 5 roadmap.epic-mismatch findings for standards children owned by S.
Sent concrete finding to reviewer; do not advance before review disposition.

Task 2: Ruling: Remove the mandatory audit.py edit from Task 2; Task 5 owns
rule composition and Task 2's standalone structural_findings API needs no
loader change — the file list requested a change without any corresponding
behavior, and a no-op edit would add no value — if wrong, the cost is adding
the missing loader integration in Task 5 before completion.
Task 2: fix round 1/5, four functional Important findings plus the above
plan-file-list correction. Base 56a3050. Original implementer resumes.
Task 2 review cannot-verify supported-runtime matrix: scheduled expressly
in Task 5 before final closure; installed 3.12/3.13/3.14 confirmed by controller.

Task 2: fix round 1/5 (5 addressed, 1 new Important open; commits
56a3050..a89da31). New breakage: release dashboard wrong-kind unique ID
silently skipped at rules.py:363. Original findings closed. Fix round 2/5
starts at a89da31 with original implementer.

Task 2: fix round 2/5 (1 addressed, 0 open; commits a89da31..837f143).
Task 2: complete (commits 2ae2853..837f143, review clean).

Task 3: started at 9798a52 with t1_3_task3 (gpt-5.6-sol high), task-3-brief.md and global constraints. Own adherence implementation and tests; structural task closed.

Task 3: Ruling: Add model.py and parse_sources.py to Task 3 ownership for
CrossEpicDesignSource and its RoadmapSources/AuditSources fields — the task
requires typed declarations with source lines, and Task 1 placed extraction
in these modules — if wrong, the cost is relocating those facts and imports
without changing the declaration policy or serialized report schema.

Task 3: Ruling: Resolve the exact managed four-earlier-gates reference to the
unique preceding same-child section's explicit four-item acceptance list —
D1.1 and D1.3 already declare those exact gates and the summary is a reference,
not a replacement gate — if wrong, the cost is narrowing or removing this
source-extraction form and reconciling the document's explicit reference.
Require missing/ambiguous-target regressions and no child-ID special cases.

Task 3 real-repository integration: initial15 findings included3 historical
plan-admission false positives and2 acceptance-reference extraction defects.
Actual remaining drift is recorded in task-3-reconciliation.md. No authority
or historical evidence silently changed. Reconciliation proposal written and
independently dispatched to t1_3_reconcile_review (gpt-6-astra high), scoped
only to governance/doc/evidence correction route; Task3 code review remains
separate. Reviewer must assess existing authority/evidence, especially D1.2.

Task 3 document reconciliation review: accepted all five exact correction
routes, no findings. D1.2 expanded clauses independently supported by existing
committed records, raw bytes checked against index/HEAD and accepted revision.
Task 5: Ruling: Apply the five reviewed reconciliation routes in the updated
plan, including one obsolete C4.4 sentence and historical provenance headers —
the independent intent audit confirms these implement existing authority
without new approvals, completion claims, or changed D1 evidence — if wrong,
the cost is reverting the narrow documentation alignment and rechecking the
owning policy/evidence, not altering runtime behavior or releasing anything.
Task 3: implementation 9798a52..6a9886f; code review dispatched t1_3_review3.

Task 3: review failed with3 Important: unresolved reference can match BACKLOG
and pass; gate comparison stops after first mismatch; sorting contract copied.
Task 3: Ruling: Move finding_key to neutral backlog/findings.py and reuse it
from audit, adherence, and structural rules, preserving audit's public import —
Task5 composition would make importing audit from rules cyclic and one shared
key prevents drift — if wrong, the cost is relocating a small helper/imports;
serialized ordering and behavior remain fixed by existing tests.
Task 3: fix round1/5 starts at b7f0417 with t1_3_task3; reviewedhead6a9886f.
Platform cannot-verify: Windows observed; macOS/Linux unavailable locally,
report CI limitation; source Python3.12/3.13/3.14 matrix remains Task5.

Task 3 fix round1 GREEN milestone:23 adherence tests and50 prior regression
tests; explicit unresolved-reference source problems; every independent gate
mismatch retained; one shared findings.finding_key with audit reexport.
Real document findings now22 (same reviewed correction population, fuller
ordinal reporting). Final checks/commit pending before scoped re-review.

Task 3: fix round1/5 (2 addressed,1 open; commits6a9886f..1255a5d).
Reference fail-closed finding remains for mixed prose/list subsections:
_acceptance_statements drops prose if any list exists, hiding managed
reference or sibling from sole-statement validation. Drift enumeration and
shared sorting closed. Round2/5 resumes original implementer at1255a5d.

Task 3: fix round 2/5 (1 addressed, 0 open; commits 1255a5d..5882bb4).
Task 3: complete (commits 9798a52..5882bb4, review clean).
Task 3 final verification: 334 tests, 94% coverage; genuine document reconciliation remains assigned to Task 5 with accepted review.

Task 4: started at 1e00bdd with t1_3_task4 (gpt-6-astra high for Git trust/lifecycle/historical-policy judgment). Task 4 brief and shared source APIs dispatched; no authority document edits. Task 5 remains pending.

Task 4: Ruling: Put lifecycle/historical admission in new lifecycle.py,
consumed directly by Task5 rather than forcing circular rules reexports;
retain release rules in rules.py and add managed release-section source
locations/parsing in model/parse_sources — rules.py is already about400 lines,
and required missing-section errors need source facts — if wrong, the cost
is moving functions/imports and source fields; public CLI/schema unchanged.

Task 4 milestone: evidence8/8, lifecycle11/12; remaining real D1.2 historical
admission correctly fails because linked acceptance agreement is a required
admission condition. Controller confirmed exact approved requirement: retain
real finding, normalize only isolated fixture BACKLOG to approved detailed
gates for positive controls, preserve policy/plan/evidence bytes. Task5's
accepted reconciliation resolves this actual mismatch; no exemption granted.

Task 4: implemented1e00bdd..676d52e, independent review t1_3_review4.
Aggregate3.12 and full3.13 pass354 tests;3.14 exposes2 native reader failures
reproduced on isolated1e00bdd, unrelated to tooling. See task-4-report.md.
Verification prerequisite: Ruling: Restore the existing native FDR hour0-23
contract in a separately reviewed compatibility commit — existing v3/v4 tests
and declared3.12-3.14 support require rejection of24:00:00, while installed
3.14 normalizes it; this reversible correction is necessary for final required
checks and does not add a T1.3 runtime feature — if wrong, the cost is reverting
the explicit hour guard and its companion commit and revisiting the existing
format tests. Scope and RED/GREEN proof are in python314-time-brief.md.

Task 4 review:2 Important,0 Critical/Minor. Oversized Gate int conversion
escapes typed finding; release candidate prefix filtering before whitespace
folding rejects valid wrapped forms and loses duplicates. Full report in
task-4-review.md. Fix round1/5 queued until compatibility implementer finishes
(single implementation worker at a time). CLI cannot-verify belongs Task5;
Linux/macOS unobserved; known nonblocking MkDocs Material banner recorded.
Compatibility worker python314_time_fix owns reader/tests only, base3d6e0a1.

Compatibility correction implemented3d6e0a1..6022dda: reader30 tests pass on
3.12/3.13/3.14; full3.14 and aggregate355 tests/94% pass. Independent
python314_time_review dispatched with review-3d6e0a1..6022dda.diff.
Task4 fix round1/5 starts at6022dda with original t1_3_task4; prior reviewed
head676d52e. Both Important findings sent verbatim via task-4-review.md;
no native or authority edits. Task5 owns separate oversized BACKLOG count
conversion regression confirmed in integration-notes.md.

Compatibility prerequisite: complete (commits 3d6e0a1..6022dda, independent review clean; no Critical/Important/Minor). Review receipt python314-time-review.md must be retained with final evidence.

Task4: fix round1/5 (2 addressed,0 open; commits676d52e..db51c61).
Task4: complete (commits1e00bdd..db51c61, review clean). Full358 tests all
supported Python targets passed; D1.2 data correction remains Task5.
Task5: Ruling: Add parse.py's gate-count conversion to CLI integration repair
scope — a confirmed oversized count bypasses domain errors and aborts the
required JSON/independent-finding path — if wrong, the cost is reverting the
narrow exception translation and its regression, not changing count syntax.
Task5 closeout stays with same implementer after controller-owned task and
whole-branch reviews; no premature verified state or fabricated receipts.

Task5: started at f92a88f with t1_3_task5 (gpt-6-astra high). Code+reviewed reconciliation candidate first; controller task/whole-branch reviews next; same implementer resumes for factual gate evidence and clean HEAD-backed verified closeout. No main integration authorized.
Task5 candidate f92a88f..b64c34c: scoped spec and quality review clean,
no Critical/Important/Minor. Current368 tests all3.12/3.13/3.14 and fullgate
pass. Unchanged family/evidence concerns are covered by Tasks1–4 reviews
and carried into whole-branch review; Linux/macOS remain unobserved.
Task5 operational closure remains pending actual final review receipt.
Whole-branch review dispatched t1_3_final_review (gpt-6-astra high),
base eac980a, head b64c34c, no waived/parked/deferred findings.
Whole-branch review b64c34c: four Important, no Critical/Minor. See
whole-branch-review.md. One consolidated final fix wave dispatched to original
t1_3_task5: reference ordinal conversion, every active-plan completion slot,
task-list statement normalization, isolated policy fixture signing/hooks.
All are approved-contract corrections; no new design or policy change.
No evidence closure before accepted scoped re-review. Fix base b64c34c.
Final fix wave b64c34c..1211466: all four confirmed findings corrected,
67 covering tests and374 tests on each3.12/3.13/3.14 passed. Full quality,
hidden scripts checks, docs, real audit/status pass. Scoped final re-review
dispatched to original t1_3_final_review, no broad review repetition.
Final scoped re-review b64c34c..1211466:4 addressed,0 open, no new or
out-of-scope findings. Whole-branch review accepted at1211466 subject to
factual operational closeout. Original t1_3_task5 resumed for six records,
evidence-first commits, verified state, HANDOFF pointer, fresh quality/audit.
No main integration or remote action authorized. No findings waived/parked.
Closeout: Ruling: Update the governance test's hardcoded T1.3 selection to
empty selection when T1.3 becomes verified, and verify it with the full
closure aggregate — the approved lifecycle ends active selection without
starting T1.4; production source is unchanged, so repeating its already-green
three-version matrix adds no new evidence — if wrong, the cost is correcting
the selection expectation and rerunning the affected verification.

Task 5 operational closeout: complete. Evidence/actual review receipts committed
first in c4b2758; verified links and empty selection published in 492dc03. The
first clean audit rejected bare Gate ordinal metadata; bb26233 corrected the
four lines. Corrected clean audit/status pass with no findings and HEAD-backed
six-slot evidence. Closure aggregate passes374 tests (76.371s), coverage374
(78.175s),94%; required scripts/docs checks pass. Exact first-failure and final
results are recorded in task-5-report.md. All20 protected files retain exact
working/index/HEAD/1211466 bytes. T1.4 remains specified and not started.
Finishing-a-development-branch invoked; local integration awaits user selection.
No merge, remote action, or release performed; no review finding remains open.
