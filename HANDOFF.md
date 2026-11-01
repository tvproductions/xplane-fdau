# Project Handoff

## Coordinated refresh locally integrated — 2026-11-01

**Observed:** 2026-11-01 13:37 UTC, before this requested handoff/sync.
This section supersedes older current-state and tooling observations below;
retain those sections as history. Jeff authorized the coordinated refresh,
selected local integration, and subsequently requested this handoff and ordinary
Git sync. No release authority was granted.

**Resume point:** The refresh is complete and locally integrated. No product
child is selected. The strict backlog audit has no findings; `next` reports
`action=write_plan child=C1.5`. C1.5 remains specified with 0/4 gates. After
session-entry authorities and a fresh audit/next, read the approved canonical
contract specification linked from BACKLOG and draft its single-child C1.5
plan with `superpowers:writing-plans`. Obtain plan approval before selecting
or implementing it. Stop on audit findings or authority drift. Do not repeat
the refresh, C1.4, or their completed verification merely because the session
changes; compare relevant inputs and evidence first.

**Git state at observation:** Main was clean at
`fdf9d7b18944c6b7eac89e5dec9b17768f6ee6d8`
(`chore: refresh toolchain and project-scoped starter adoption`), one commit
ahead of freshly fetched `origin/main`. This handoff's sync will create a later
HEAD; recheck local/remote state on resume. The temporary refresh worktree and
branch were removed only after exact fast-forward and main verification passed.
The unrelated worktree at `C:/Users/Jeff/.codex/worktrees/c68f/xplane-fdau`,
branch `chore/dependency-refresh-2026-10-18`, remains at `f81c4c2`, untouched.

**Verified baseline:** Python 3.12.16; uv/uv_build 0.13.6; Ruff 0.17.3;
ty 0.0.95; setup-uv 10.3.3. Runtime dependencies remain empty and support stays
`>=3.12,<3.13`. Ten locked packages were updated. Four older transitives remain
explained by Wily/Radon constraints. The old Python download-catalog override
was removed after disposable provisioning proved uv's built-in catalog works.
That temporary Python copy was removed; existing Python aliases, PATH and the
Windows registry were unchanged.

Starter 0.8.0 is selected at `e0b752fcc13b87ec7868fe0b0f85badefdb6bf52`;
Superpowers 7.0.1 at `2ce8aa15d05bd57213e6f746f953aafb7ded7a8b` and gz-skills
0.8.3 at `d6acc26e28ca1c4f43e5bb46d8973021d7d006c3` were verified through
native inventory, actual checkouts and fresh-session discovery. Project-local
overrides suppress duplicate sources; user configuration stayed byte-identical.
Heavy selection and disabled Backplane are unchanged. The local installed
pre-commit launcher now uses the current checkout's locked/all-group uv
environment, rather than a hard-coded main path; all four hooks remain enabled.

**Evidence:** The committed
[refresh review](docs/reviews/2026-11-01-coordinated-refresh.md),
[specification](docs/superpowers/specs/2026-11-01-coordinated-refresh-design.md)
and [completed crosscutting plan](docs/superpowers/plans/2026-11-01-coordinated-refresh.md)
record scope, provenance, failures and corrections. Complete offline hygiene,
all commit hooks, independent review, 693 external source unittest tests and
wheel-only smoke passed. Final audit covered 133 packages with zero known
vulnerabilities/adverse statuses. A rebuilt sdist produced an identical wheel.
Main passed frozen all-group sync, lock check, backlog audit, both live-state
tests, fresh strict artifacts and external installed-wheel smoke. Its artifact
hashes exactly match the verified branch.

The integration receipt is
`.superpowers/sdd/coordinated-refresh-2026-11-01/integration.json`; 55 execution
receipt files were copied and hash-verified there before worktree removal.
These receipts are **local-only**, unavailable from a fresh clone. Successful
matrix and main artifact environments were removed after verification; their
recorded paths are historical, not existing inputs.

**Open limitations:** Starter `status` has an upstream Windows path-separator
false positive (`duplicate template update skill at .agents/skills`). Do not
delete the sole project skill or patch shared caches to silence it; managed
bytes, actual sources and native discovery passed independently. Cognitive
analysis remains UNKNOWN/deferred, existing Lizard acceptance limitations remain
open, STRICT starter acceptance is incomplete, and G1/release gates still wait.
The refresh and ordinary sync close none of those gates. No automatic schedule,
upstream issue/PR submission, tag or package publication is authorized.

## C1.4 locally integrated — 2026-10-26

This section supersedes the earlier C1.4 plan-review resume point below.
Jeff approved the plan and inline execution, authorized local baseline
checkpoints, accepted installed Superpowers 7.0.1 for the remainder after the
shared cache changed, and selected option 1: local integration.

C1.4 is **verified, 4/4 gates**, with accepted independent review. Main
fast-forwarded exactly to reviewed branch HEAD
`c754adfe6a7e82ac6a66190bfbbfc70b7f8870d2`; subsequent changes are integration
records only. The temporary C1.4 worktree and branch were removed after main
verification passed. No child is selected. The next local action is to review
and write a single-child C1.5 implementation plan from the approved canonical
specification; C1.5 remains specified with 0/4 gates. Do not repeat C1.4.

The branch passed 691 external source unittest tests, full offline hygiene,
strict documentation/artifacts and wheel-only smoke on Python 3.12.16. Main
passed frozen offline all-group sync, lock check, backlog audit, both live-state
tests, a fresh strict artifact pair and external wheel-only smoke. All 130
relevant input hashes and both artifact SHA-256 hashes match the verified
branch. Exact evidence is in
[the integration receipt](.superpowers/sdd/2026-10-26-c1-4-timing/integration.md),
alongside the committed completion/review/gate receipts and input manifest.
Raw execution logs were copied and hash-verified on main before worktree removal;
they remain local-only under that receipt directory's `execution/` subdirectory.

The earlier maintenance, README and Lizard work is preserved in baseline
`a2ef12d`. The unrelated dependency-refresh worktree at
`C:/Users/Jeff/.codex/worktrees/c68f/xplane-fdau`, branch
`chore/dependency-refresh-2026-10-18`, remains untouched. Cognitive analysis
remains deferred, STRICT starter acceptance remains incomplete, Backplane stays
disabled, and G1/release gates remain waiting. No push, tag or publication was
authorized by local integration. Recheck native plugin sources on resume;
this session's bounded source exception did not update shared bundle pins.

## Fresh-session resume — C1.4 plan review, 2026-10-26

**Observed:** 2026-10-26 21:46 UTC. Jeff explicitly requested this handoff for a
fresh session. This section supersedes older resume instructions and current-state
claims below; retain the older sections as dated history.

**Resume point:** Review the existing [C1.4 implementation plan](docs/superpowers/plans/2026-10-26-c1-4-clock-domains-utc-anchors-simulator-timing.md).
It is a **draft**, already written, audited and explained in chat. Jeff asked to
write the plan and then to review it here; neither message approved implementation
or selected an execution method. Native execution was recommended because the
five tasks share validators and wire readers; it was not selected. No C1.4 code,
worktree, selection, lifecycle transition or acceptance gate has been created.

**First concrete action:** Read AGENTS.md and its governing authorities, then run
the backlog audit and next action through the project's required uv version.
Read this draft and the approved canonical specification's timing/public-API
sections, then continue the user's plan review and obtain the still-pending plan
approval/execution choice. Expected current result: audit has no findings, no
child is selected, and C1.4 is `specified`, 0/4 gates. The tool still recommends
`write_plan C1.4` because the draft is unapproved/unlinked; **do not rewrite or
duplicate the existing plan**. Stop on audit findings or material authority drift.

The [approved canonical specification](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md)
already supplies implementation authority for the design, not approval of this
draft execution plan. Its C1.4 requirements are clocks/readings, exact UTC,
checked comparison/differences, and explicit anchor/source/simulator timing.
The draft records two implementation choices for review: acquisition phase stays
a closed string without moving its future bindings enum into contracts; matching
an enclosing observation's producer uses a private context check, with record
integration remaining C3.1. No new product design or repeated brainstorming is
needed unless review identifies an actual specification gap.

### Workspace and pending execution prerequisites

- Worktree: `U:/repos/xp/xplane-fdau`, branch `main`, HEAD
  `8bcef360b2728ea4c07b3d41874bc3dd661f051f`. The tree is dirty and the index is
  empty. The verified dependency refresh, documentation changes, Lizard evidence
  and C1.4 draft are **uncommitted**. Preserve all of them.
- The unrelated worktree
  `C:/Users/Jeff/.codex/worktrees/c68f/xplane-fdau`, branch
  `chore/dependency-refresh-2026-10-18`, remains at `f81c4c2`; leave it alone.
- Before feature execution, establish the clean reviewed baseline and temporary
  C1.4 worktree described by the draft. Do not silently stash, discard, commit or
  absorb the pending maintenance into the feature. A save/integration route is
  still pending; this handoff authorizes neither Git sync nor a commit/push.
- Keep Python 3.12, stdlib-only runtime, unittest-only testing, and all Python
  execution through locked/all-group uv. Preserve mandatory hooks.
- Cognitive analysis is explicitly deferred. STRICT starter acceptance remains
  incomplete; Backplane stays disabled. C1.4 planning does not close those gaps,
  select another child, or grant a release/tag/publication exception.

### Completed work to preserve, not repeat

**Python/tool refresh:** Jeff authorized bringing dependencies current. The
working tree now selects Python **3.12.16**, ty **0.0.92**, and 19 updated packages,
including Material 9.8.0 and the documentation plugins. Four older transitive
packages remain constrained by Wily/Radon: colorlog, mando, Plotly and Radon.
Runtime dependencies remain empty; uv/uv_build remain 0.13.5. Project uv config
pins Astral's immutable download catalog for the newer Python patch, with CI
aligned to 3.12.16. The shared Python minor-version junction was restored to its
original 3.12.15 target; FDAU's own environment uses exact 3.12.16.

Refresh/hygiene child commands now retain `--all-groups`. An external console
test now selects its actual interpreter using `--no-project`; its stderr
assertion was preserved. These fixes were necessary for reliable verification.
Final offline hygiene passed, including all-files Ruff/format/ty/full unittest,
backlog/docs and fresh strict artifacts. External source verification passed
**656 tests in 368.399 seconds** on Python 3.12.16; wheel-only smoke passed.
Native uv audit reported **133 packages, zero vulnerabilities/adverse statuses**;
installed consistency checked 129 packages. Independent scoped review found no
actionable findings. Initial failed attempts remain recorded, not relabeled.

The complete local receipt is
`.superpowers/sdd/dependency-update-2026-10-26/result.json`; its final candidate
hashes bind 12 changed files. It also proves the six earlier edited files were
preserved byte-for-byte before this new handoff text. The initial failed matrix
directory `C:/Users/Jeff/AppData/Local/Temp/xplane-fdau-matrix-xs3vbn43` was retained
for diagnosis; successful final temporary directories were safely removed.
Prior exact-commit CI describes committed HEAD, not these uncommitted inputs.
Do not repeat the full refresh or full gates merely because the session changes;
check evidence age and relevant input drift first.

**Lizard:** [Upstream PR #530](https://github.com/terryyin/lizard/pull/530) was
explicitly authorized and submitted. Read-only handoff verification found it open
and unmerged at head `2948b38ed0bf70c5a4c39163b45dfa50c3020314`. Its reviewed patch
discovers all ten omitted methods across the four FDAU error scopes, with 1,528
functions and unchanged prior scores. Released/installed Lizard 1.24.3 remains
unchanged. Upstream review and reviewed analyzer adoption remain pending. The
[qualification](docs/reviews/2026-10-26-lizard-inline-qualification.md) and
[portable patch](docs/reviews/2026-10-26-lizard-inline-suites.patch) are durable
untracked files; retain them. Do not submit a duplicate PR or reformat FDAU to
accommodate the parser. Upstream broad testing had five unavailable-framework
import errors; the passing 128-reader-test result is not a full upstream pass.

**README:** FDAU and FDIU are now expanded as Flight Data Acquisition Unit and
Flight Data Interface Unit, with the virtual role explained. This edit is also
uncommitted.

### Starter and tool observations — verify afresh

The project lock/config still selects starter **0.6.0** at
`c0a6945b2170e1cf5bee3e80738916f5b62d13a5`, SP 7.0.0 at `bb92a77`, and gz-skills
0.8.0 at `75bcd11`; the marketplace checkout matches that starter SHA. At this
handoff, native inventory and actual SP checkout again report **7.0.0**; the
7.0.1 cache path seen during planning is now absent. The session advertisement
and installed observations changed during the conversation. The draft's 7.0.1
observation is dated planning evidence, **not a current installation claim**.
Verify ID/version/enabled state, actual checkout and fresh-session discovery
before choosing workflow instructions. Do not edit caches or create a private
marketplace as a workaround.

Jeff correctly challenged the claim that starter guidance required retaining
old component versions. The live check found released starter 0.6.0 still latest,
while published main `35ac0578dab0c7b603a9545d9b6b630ee006e551` identified itself
as **0.7.0 unreleased**, selected SP 7.0.1, and still pinned gz-skills 0.8.0.
Its guidance recommends independent latest-stable component review; gz-skills
0.8.3 was the latest component release. FDAU's shared-source/provenance policy
still needs reconciliation with an explicitly reviewed target. The assistant's
earlier explanation was too categorical; do not repeat it as upstream policy.
No starter/plugin adoption was applied by this session's dependency refresh.

The uv executable also reported 0.13.1 temporarily while the project required
0.13.5. Plan verification succeeded with the cached isolated command prefix
`uv tool run --offline --from uv==0.13.5 uv run --offline --locked --all-groups`.
At handoff, normal `uv --version` reports 0.13.5 again. Recheck origin/version;
do not bypass uv with direct Python or weaken `required-version`.

### Plan verification and local evidence

Draft plan SHA-256:
`ba883a719715201b4df360e988c752086053208e2f119593ad037130a9635be5`.
Plan audit found no missing/drifted scoped requirement. Backlog audit, 18
documentation/API tests, strict MkDocs and whitespace checks passed. Drafting
evidence is `.superpowers/sdd/2026-10-26-c1-4-timing-plan/plan-audit.json` and its
sibling logs. No implementation tests for C1.4 have run because no implementation
exists.

All `.superpowers/sdd/` records and preserved temporary environments are
**local-only**. Keep this workspace/evidence when starting the fresh session;
they are not available from a fresh Git clone. Relevant earlier receipt roots
are `dependency-review-2026-10-26/`, `dependency-update-2026-10-26/`,
`2026-10-26-c1-4-timing-plan/`, and
`2026-10-25-strict-heavy-starter-onboarding/` beneath that directory. The plan,
Lizard qualification and patch are durable project files but remain untracked.

Suggested next workflows: project `backlog-status`, `gzs-session-handoff` resume,
`gzs-plan-audit` if the plan changes, then the user's chosen execution workflow
after approval and baseline reconciliation. This request writes handoff text
only; it performs no implementation, Git sync, plugin update or release.

## Lizard remediation candidate — 2026-10-26

Jeff deferred cognitive analysis and requested the four Lizard errors be
addressed. A reviewed upstream parser patch now discovers all ten omitted
protocol methods: FDAU qualification finds 1,528 functions, zero discovery
errors, and no changes to prior function names, lines or scores. See the
[qualification and portable patch](docs/reviews/2026-10-26-lizard-inline-qualification.md).
Jeff subsequently authorized upstream submission. The patch is now
[Lizard PR #530](https://github.com/terryyin/lizard/pull/530), from
`ahuimanu:fix/python-inline-suites` at `2948b38`. The installed Lizard 1.24.3
remains unchanged; upstream review and reviewed analyzer adoption remain the
delivery path. Cognitive remains deferred/UNKNOWN and STRICT acceptance incomplete.

## STRICT acceptance continuation — 2026-10-26

The integrated candidate remains `8bcef36`. Read-only GitHub inspection now
confirms exact-commit CI run `40251399123`: quality (656 tests), artifacts and
installed-wheel all passed. Native pip-audit also passed the exact hashed lock
export with a fresh isolated HTTP cache: 128 applicable dependencies, zero
skipped and zero known vulnerabilities. Its old default-cache path hangs in
temporary-file creation; preserve that cache and use the recorded isolated-cache
invocation. No dependency or source change was needed.

The [current acceptance record](docs/reviews/2026-10-25-strict-heavy-starter-adoption.md#current-acceptance-continuation-october-26-2026)
contains commands, hashes, CI links and diagnostic limits. This supersedes older
claims below that network proof and exact-commit CI are unobserved. Cognitive
extraction/shared integration and four Lizard discovery errors remain open;
STRICT acceptance is incomplete. Backplane remains separately deferred. This
continuation performs no commit, push, workflow dispatch or release.

## Local integration complete — resume-session closeout

The onboarding implementation is locally integrated into main at `9a71569`.
The disposable onboarding worktree and temporary branch were removed after
main verification. Do not recreate them or repeat completed remediation.
Jeff directed this durable integration; STRICT acceptance remains incomplete.
The approved specification remains
`docs/superpowers/specs/2026-10-11-skills-first-native-adoption-design.md`;
the plan's Task 7 step 8 records this subsequent integration direction.

The live release review still selects published starter v0.6.0 and its SP
7.0.0/gz-skills 0.8.0 bundle. Upstream SP 7.0.1 and gz-skills 0.8.3 are newer
components; no independent pin substitution was authorized or applied.
Shared plugins live outside the worktree. Main now has the project routing,
synced uv-managed environment and uv-only hook pointing to main. Its old
Superpowers discovery junction was detached nonrecursively; the rollback
checkout target remains intact. Native inventory verifies the selected sources
enabled and competing sources/Backplane disabled. This active session's earlier
skill advertisement is not fresh-session discovery proof for main.

Preserve the ignored execution evidence under main's
`.superpowers/sdd/2026-10-25-strict-heavy-starter-onboarding/`, including the
original main files. Do not repeat completed mutation/coverage remediation.
Cognitive-library integration, four Lizard discovery omissions, network audit
proof and exact-commit CI remain open. This integration is no STRICT acceptance,
product-child completion, Git push, tag or release claim.

The fresh mandatory hook suite, whole-source Ruff/format and ty passed before
integration. Main's exact fast-forward, frozen all-groups sync, lock check,
backlog audit, two live-state tests, strict docs, fresh source-independent
artifacts, strict metadata/inventory and external uv wheel-only smoke passed.
Local-only results and hashes are in
`.superpowers/sdd/2026-10-25-strict-heavy-starter-onboarding/integration-main-verification.json`;
the copied-evidence manifest and `integration-main-resume-originals/` preserve
the original main edits. The unrelated dependency-refresh worktree is retained.
This closeout adds only documentation; its final save runs main's mandatory
hooks. No remote operation occurred. The remaining onboarding work is the open
acceptance proof above, not another installation or integration.

## Restart after workflow failure — 2026-10-26

Observed **2026-10-26 00:27 UTC**. Jeff requested this handoff and a fresh start
after the agent repeatedly confused specification authority, integration timing
and approval. This section supersedes the older resume instructions below.
No merge, push, PR, tag or release occurred. This handoff performs no upgrade.

**Objective:** Complete the mandatory template alignment. First resolve the
Superpowers source/version concern and explain the governing specification
clearly; do not start another implementation slice or repeat completed work.

**Workspace:** The agent owns the existing feature worktree:
`U:/repos/xp/xplane-fdau/.worktrees/strict-heavy-onboarding`, branch
`chore/strict-heavy-onboarding`, source HEAD
`528ff96381e69219005950ad267374540e63c8d8`
(`fix: enforce collection shape limits and uv verification paths`). The tree
was clean before this handoff; the new handoff text is uncommitted. Do not ask
Jeff to reopen or manage a different worktree. Main remains at `3a5211b`, with
its preserved HANDOFF/design/approved-step-document edits. The unrelated
dependency-refresh worktree remains at `f81c4c2` and is outside scope.

### Governing specification and source selection

The work was **not performed without a specification**. The approved semantic
authority is [Skills-first Native Adoption Design](docs/superpowers/specs/2026-10-11-skills-first-native-adoption-design.md),
whose metadata records Jeff's October 25 approval. Its lines 28–31 explicitly
permit independent work while the cognitive prerequisite is unavailable, without
claiming STRICT acceptance. The approved executable steps are in
[Strict Heavy Starter Onboarding](docs/superpowers/plans/2026-10-25-strict-heavy-starter-onboarding.md).
Its Task 7 step 8 currently says “Finish only after acceptance.” Do not substitute
vague references to a “plan” for identifying the source specification and the
exact requirement. Neither tests nor skill invocation certify acceptance.

The feature bundle and native configuration select released starter **v0.6.0**,
revision `c0a6945b2170e1cf5bee3e80738916f5b62d13a5`, whose catalog pins
**Superpowers 7.0.0**, revision `bb92a77741419a4ab5f06e711a283343f1ada0c3`,
and gz-skills 0.8.0. Backplane is disabled. The prior
[adoption review](docs/reviews/2026-10-25-strict-heavy-starter-adoption.md)
already knew SP 7.0.1 and gz-skills 0.8.3 existed, but retained the reviewed
released catalog instead of substituting independent components. The design
also records an earlier observation of unreleased starter main selecting SP
7.0.1. These are dated observations, not a new latest-release review.

**Jeff's unresolved concern:** Why is 7.0.1 not active here, and is Superpowers
actually being followed? A cached 7.0.1 copy exists under
`C:/Users/Jeff/.codex/plugins/cache/xplane-health-skills-first/superpowers/7.0.1`,
at `2ce8aa15d05bd57213e6f746f953aafb7ded7a8b`. Its presence does not activate
it for FDAU. The active feature source remains the starter-selected 7.0.0.
The session's advertised skill catalog is still main-derived; selected installed
7.0.0/0.8.0 sources were read explicitly. Do not claim a fresh discovery from
that file inspection, silently use main's older skills, or modify managed caches.

**First concrete action on resume:** Read this section and the governing spec,
then verify actual native source selection from the feature directory. Use the
project `update-gz-template` guidance for a bounded read-only check of published
starter/component releases and compare the reviewed bundle with SP 7.0.1. Report
why the current pin exists and whether it still meets Jeff's current direction.
Do not repeat the full tool refresh or silently upgrade one component under
the old bundle. A review request is not an instruction to edit caches, activate
another project's source, or change user defaults. Own the source reconciliation.

### What failed in this session

- The agent did not name and distinguish the approved specification clearly.
- It proposed a draft PR to obtain CI because `ci.yml` runs on main pushes and
  PRs, then presented Superpowers' optional finishing routes while STRICT
  acceptance was still incomplete. Superpowers offers local merge, push/PR or
  keep-as-is; it does not mandate a PR or draft status.
- Jeff initially answered yes to feature push/draft PR, then selected **1**
  (local merge) after the discussion of those alternatives. Local integration
  is his latest selected route. The agent repeatedly asked whether that changed
  acceptance timing, then alternated between saying it would merge and saying
  it was holding. It did not execute either route. Do not ask Jeff to repeat
  his basic choice merely because a new session began, or treat that choice as
  evidence that STRICT acceptance passed. Reconcile the specification's open
  requirements and the recorded integration direction consistently before acting.
- One external smoke setup used a relative receipt path from Temp. PowerShell
  continued after the read failed and uv created an unintended empty Temp/.venv.
  Its exact path, creation time, contents and absence of links were verified;
  only that newly created empty environment was removed. Absolute paths and
  fail-fast PowerShell corrected the retry. No direct Python fallback occurred.

### Verified implementation and evidence — do not redo

Commit `528ff96` corrects the general 65,535 collection ceiling to
`ContractShapeError` before element domain/semantic validation, as Jeff explicitly
selected. Constructors and nested readers share the check. Semantic minima and
declaration-specific lengths remain distinct. It also routes external matrix
source/wheel commands and installed-smoke console children through uv, preserving
external installed origin, and adds only five individually approved public Git
pin false positives to the secrets baseline. Existing entries/settings/timestamp
were structurally verified unchanged. Independent bounded review found no defect.

The existing local-only execution workspace is
`.superpowers/sdd/2026-10-25-strict-heavy-starter-onboarding/`:

- `continue-acceptance-current.json` binds the exact source HEAD, results,
  source hashes, artifacts and remaining prerequisites.
- Mandatory installed uv-only hooks passed Ruff, format, ty and full unittest:
  `continue-commit.log`. No hook was bypassed.
- `continue-coverage.log/json`: **656 tests passed**, 304.238 seconds;
  statement coverage **95.31%**, branch **92.37%**, combined **94.52%**.
- `continue-mutation-complete.json/log`: a **fresh complete** native batch,
  baseline 79 tests, **1,430 normal jobs: 1,316 killed, 114 survived**, zero
  abnormal/incompetent executions. Raw exit 1 is preserved. Every survivor has
  an individually bounded equivalence rationale; none is unmatched in
  `continue-mutation-review.json`. The mapping checks mutation and surrounding
  diff context; shifted contexts are in `continue-manual-dispositions.json`.
  Private-introspection, supported-interpreter and future-API limits remain
  explicit. Do not relabel this as every mutation killed or universal equivalence.
- `continue-remediation-review.md`, `continue-endpoint-alias-review.md` and
  `continue-empty-vector-equivalence.md` retain scoped reviews. The former
  endpoint/count uncertainty is resolved for the stated public paths; do not
  repeat those investigations or add private-state snapshots.
- `continue-analysis-final.json/log`: native Lizard 1,518 functions, maximum 20,
  weighted mean 3.4130; four original discovery errors and cognitive UNKNOWN
  still force exit 2. Reviewed Bandit warnings remain visible. Strict docs,
  whole-source Ruff/format/ty and final actual backlog audit passed.

Fresh external artifacts and wheel-only Python 3.12.15 smoke passed, including
installed collection-error controls. Verified retained locations:
`C:/Users/Jeff/AppData/Local/Temp/fdau-alignment-current-a5e76508335f444f98063a3ddb99dc86/dist`
and sibling `installed`. Digests are in the current JSON receipt and ledger.
These paths and ignored reports are local-only; preserve them before eventual
worktree retirement. Older dated gates are not substitutes for current proof.

### Remaining boundaries and restart rules

Tasks 4/7 and STRICT acceptance remain incomplete: the shared cognitive library
is still unavailable (Jeff reconfirmed), native Lizard has four discovery
omissions, network audit proof remains timed out, and exact-commit remote CI is
unobserved. Do not retry unchanged network timeouts, rewrite sound source for
Lizard, substitute a cognitive analyzer or claim acceptance from routine tests.

All project Python execution goes through locked all-groups uv in this feature
directory. External wheel-only checks use explicitly selected uv environments
with `--no-project` to prevent editable fallback. Cache-lock denial requires
narrow sandbox escalation; never use python/py/venv executables directly.
The shared Git hook is a corrected uv-only launcher pointing to this feature
environment; retain it and the worktree until verified main reinstallation.

Main's three preserved files were compared and copied to local
`integration-main-originals/` under this execution workspace. The design matches
feature byte-for-byte; the executable-steps document differs only in recorded
progress/status, scratch path and approval note; main HANDOFF is an older pointer.
Main remains dirty. Do not discard its files, remove a dirty worktree, silently
merge over them or touch the unrelated worktree. A future local integration must
preserve these originals, reconcile current authority, verify main, retain uv-only
hooks, and preserve ignored evidence before cleanup.

This request ends the session with **handoff text only**. No implementation,
integration, remote operation or plugin/version update follows it in this session.

## Task 4 resumed checkpoint — 2026-10-25

The restart below was followed in the existing feature worktree. The retained
twelve tooling/test edits were preserved, and remediation proceeded in bounded
groups. See the [current evidence](docs/reviews/2026-10-25-strict-heavy-starter-adoption.md#resumed-task-4-remediation-checkpoint)
and the existing ignored plan ledger for exact commands and raw results.

Current result: 23 additional inherited mutation survivors are killed by native
differential controls; 95 have individually mapped, bounded equivalence reviews;
two endpoint-alias questions and collection-count error taxonomy remain open.
All 22 retained Bandit findings have scoped dispositions, including two retained
trust advisories. No runtime library source changed. Current focused contract
verification passed 76 tests; focused analysis/mutation checks passed 20, and
whole-source Ruff/format/ty passed. Mandatory installed hooks supply the final
checkpoint save gate; check `task4-resume-commit.log`, the ledger and Git history
for its observed result. The first `task4-resume-commit.log` attempt was stopped:
the inherited native hook launcher invoked the venv interpreter directly. Its
preserved original and corrected uv-only launcher are local state, and only
`task4-resume-commit-uv.log` can establish the compliant save. Earlier 644-test
evidence is historical.

Interactive Python commands and native mutation test children used locked
all-groups uv. The inherited hook-launcher violation above was corrected before
the save retry. Preserve its uv-only launch when reinstalling from verified main;
the default generated pre-commit launcher uses a direct interpreter. Five subprocess test modules and mutation/audit
composition were reconciled accordingly. Existing provenance tests are now in
the selected mutation suite. The external dependency matrix still constructs
direct interpreter commands: reconcile it before invoking it under the current
all-Python-through-uv instruction. No network audit or full mutation batch was
rerun. Native installed-source inspection passed; no new discovery claim follows.

Next bounded action: reconcile general collection-limit error taxonomy against
the canonical specification and completed C1.3 plan, including existing inline
and allow-list count assertions, before changing runtime behavior or freezing an
error priority. Retain endpoint-alias uncertainty unless a meaningful public
control or bounded equivalence argument resolves it. Do not repeat the completed
Unicode/exact-type/payload groups or the 22-finding security review.

Task 4/7 and STRICT acceptance remain incomplete. Cognitive extraction, four
Lizard discovery omissions, timed-out network proof and exact-commit CI remain
open. Main/unrelated worktrees remain untouched; no integration, push or release
is authorized. Verify current feature HEAD and cleanliness because saving this
checkpoint creates a later commit than the restart's `ea50bf0`.

## Restart point — 2026-10-25 22:15 UTC, failed resume corrected

Jeff requested this refreshed handoff after stopping a failed resume. **Start
from the existing work, not from a new implementation or template migration.**
The Task 4 resume point and retained evidence below remain applicable. STRICT
acceptance is incomplete; no plan task was completed in the failed resume.

### What happened and what was verified

- The agent incorrectly told Jeff to open the feature worktree in another
  session because the advertised skills came from main. Jeff had already
  started a fresh session and explicitly directed the agent to manage the
  worktree and source mismatch itself. That instruction is binding.
- The agent then bypassed uv's cache-lock permission failure by invoking
  `.venv/Scripts/python.exe` directly. Jeff explicitly restated that **ALL
  Python execution must go through uv**. The direct runs are workflow
  violations and must not be used as onboarding acceptance evidence.
- A subsequent authorized `uv run --locked --all-groups python
  .codex/skills/backlog-status/scripts/backlog_status.py audit` exited 0,
  with no findings. Its local log is
  `.superpowers/sdd/2026-10-25-strict-heavy-starter-onboarding/resume-uv-audit.log`.
  Handoff closeout reran both `audit` and `next` through that same uv prefix;
  both exited 0 with no findings. Their local logs are
  `restart-handoff-uv-audit.log` and `restart-handoff-uv-next.log` in the same
  directory. Both recommend `write_plan C1.4`; this does not displace the
  authorized crosscutting onboarding work or select C1.4. Earlier direct
  runs do not supply acceptance evidence.
- Native plugin listings from the feature directory showed the selected
  SP 7.0.0 and gz-skills 0.8.0 installed/enabled, Backplane disabled and the
  legacy gz-skills source disabled. Actual cached Git HEADs matched the
  bundle pins. Reading these installed sources is possible here. This is
  installation/provenance evidence; it does not re-prove fresh discovery.
  Verified installed skill roots are
  `C:/Users/Jeff/.codex/plugins/cache/skills-first-starter/superpowers/7.0.0/skills`
  and `C:/Users/Jeff/.codex/plugins/cache/skills-first-starter/gz-skills/0.8.0/skills`.
- Feature HEAD remains `ea50bf03824dd37ceaacfbc21dcf7f4d87ae7b28`; main
  remains `3a5211bfe3c1ab80e25758fce61356dd6ef7cbef`. The twelve existing
  tooling/test edits remain uncommitted. No implementation edits, commits,
  merges, pushes or dependency changes occurred in the failed resume.
- A read-only Bandit reviewer was interrupted when Jeff stopped execution.
  It produced preliminary observations, no completed review artifact or
  accepted disposition. All 22 findings remain open. No reviewer is running.
- The ledger, round-2 mutation results, raw Bandit report, prior 644-test
  quality log, prior native-discovery result and both external artifact/test
  directories named below were checked present at this checkpoint.
  Their earlier results are dated evidence, not new candidate verification.

### Required approach for the restart

1. **Own the workspace.** Set every project command's working directory to
   `U:/repos/xp/xplane-fdau/.worktrees/strict-heavy-onboarding`. Verify its
   branch, HEAD and diff. Jeff need not open, switch, create or repair a
   worktree for the agent. Preserve main's original design/plan edits and
   the unrelated dependency-refresh worktree.
2. **Enter once, deliberately.** Read this handoff, the applicable feature
   instructions and required authorities, then the approved onboarding
   design/plan and existing ledger. Read long authorities in bounded parts
   so output truncation cannot masquerade as a completed read. Load the
   selected native skills and project adapters; never silently substitute
   main's legacy skill versions. Diagnose a source mismatch using native
   observations and installed-source provenance, preserving user defaults
   and managed caches. Ask only for a specific unresolved required action,
   after exhausting authorized ways to resolve it here.
3. **Use uv for every Python execution.** This includes inspection snippets,
   scratch scripts, tests and verification. Use the exact locked/all-groups
   environment required by the feature policy. If uv cannot access its
   configured cache, request the tool's narrowly scoped sandbox escalation;
   the uv audit above succeeded that way. Never fall back to `python`,
   `py`, a venv executable, or an unreviewed alternate environment. Check
   existing direct-interpreter tooling against this instruction before
   using it; do not invent an exemption. Use PowerShell for simple file/Git
   inspection. Unsupported CLI flags are not evidence: audit/next do not
   accept `--json`.
4. **Bound the work.** Jeff objected that template alignment had grown into
   an oversized implementation slice. Resume only Task 4's retained
   remediation: one reviewable survivor group or security finding at a
   time, with ledgered result and next action. Do not repeat completed
   Tasks 1–3/5–6, refresh templates/tools, start C1.4, or broaden the weak-test
   audit. A context window ending is not itself a technical defect; avoid
   making successors reconstruct repeated exploration or unfinished claims.
5. **Prove the behavior.** Follow the approved tests-first workflow for
   actual corrections. Derive expected behavior from the governing
   contract, demonstrate a realistic negative control, then verify the
   correction. Preserve existing edits. Do not add private-signature,
   prose or temporary-state snapshots merely to kill mutations. Keep raw
   mutation results and individual survivor dispositions linked.
6. **Keep proof precise.** Run focused unittest/Ruff/ty during remediation.
   Run the required stable-candidate gate at closeout; installed commit
   hooks are mandatory. Do not repeat multi-minute complete gates without
   a changed candidate or unresolved reason. Scope reviews explicitly;
   interrupted reviews and passing tests do not establish security or
   STRICT acceptance. Keep commentary brief and candid about findings.
7. **Separate external dependencies from local work.** Cognitive extraction,
   the four Lizard omissions, timed-out pip-audit proof and exact-commit CI
   remain open as described below. Finish independent authorized work,
   preserve UNKNOWN/FAIL, and report the exact prerequisite. Do not invent
   analyzers, change thresholds, retry unchanged timeouts, or claim whole
   onboarding completion to close a checkpoint.
8. **Finish the temporary branch deliberately.** After required work and
   review are ready, present a concrete result for the separate integration
   decision. If Jeff selects local integration, follow exact-fast-forward
   main verification, reinstall hooks from verified main, then remove the
   temporary worktree/branch through Git. Do not remove this dirty worktree
   or leave it as a permanent delivery path. Merge, push and release authority
   remain separate; this handoff request authorizes none of them.

**First implementation step after entry:** inspect the retained round-2
survivors and the Unicode boundary/error-precedence requirements identified
below. Complete one bounded group with focused evidence before moving on.
This refreshed handoff ends the failed session; it does not authorize further
implementation before the next resume. Only handoff text and ignored resume
diagnostics were changed for continuity. No new acceptance claim is made.

## Resume point — 2026-10-25, strict heavy onboarding / Task 4

Observed **2026-10-25 21:36 UTC**. Jeff requested a handoff because context was
nearly full after a long execution session. This section supersedes older resume
points below. Work is preserved locally; **STRICT acceptance is incomplete**.

Use this retained worktree as the working directory:
`U:/repos/xp/xplane-fdau/.worktrees/strict-heavy-onboarding`.
Branch: `chore/strict-heavy-onboarding`.
HEAD: `ea50bf03824dd37ceaacfbc21dcf7f4d87ae7b28`
(`build: adopt strict heavy starter tooling and policy`). Main remains at
`3a5211bfe3c1ab80e25758fce61356dd6ef7cbef`; it has not been integrated or pushed.
Main's pre-existing approved spec/plan edits are preserved. The unrelated
`chore/dependency-refresh-2026-10-18` worktree remains untouched.

**First action:** read session authorities, the
[approved plan](docs/superpowers/plans/2026-10-25-strict-heavy-starter-onboarding.md),
[design](docs/superpowers/specs/2026-10-11-skills-first-native-adoption-design.md),
and [evidence](docs/reviews/2026-10-25-strict-heavy-starter-adoption.md); compare
HEAD and `git diff`, then run backlog audit/next. Stop on findings. Expected next
product action is `write_plan C1.4`, but do not select it: the active authorized
work is onboarding Task 4 remediation, followed by Task 7 acceptance.
C1.3 is already verified at 4/4 gates. Do not reopen it or repeat Tasks 1–3/5–6.

### Settled decisions and committed work

- Jeff approved strict heavy adoption; Backplane stays disabled and FDAU delivery
  authority stays local. No gzkit lifecycle or runtime feature is introduced.
- Selected starter v0.6.0/full SHA and shared SP 7.0.0/gz-skills 0.8.0 pins are
  recorded in `.skills-first/bundle.lock.json`. Exact environment: managed
  Python 3.12.15, uv/uv_build 0.13.5, Ruff 0.17.2 (`py312`), ty 0.0.91 (`3.12`).
- Native installation, restored user defaults, outside-project control and fresh
  selected-source discovery passed in the earlier execution. The agent owns
  resuming in the feature worktree and reconciling its selected sources;
  main intentionally retains its old configuration until verified integration.
- Foundation offline hygiene passed. Its separate coverage run passed 630 tests:
  95.08% statements, 91.75% branches, 94.18% combined. External wheel-only exact
  Python smoke and real valid/invalid typing consumers passed. The source-independent
  build explicitly built the wheel from the sdist. These are foundation observations,
  not a claim that all later acceptance work is finished.
- Native pre-commit runs four checks, including full unittest. No hook was bypassed.
  Its shared launcher points to this feature environment: retain the worktree and
  reinstall from verified main before eventual removal. Main's old junction and
  its target are rollback state, not deletion targets.

### Uncommitted remediation, already verified

Twelve code/test files remain modified: backlog `adherence.py`, `edit.py`,
`lifecycle.py`, `rules.py`; hygiene's script; `tools/runtime_imports.py`; and
`test_backlog_status_edit`, `test_backlog_status_lifecycle`, `test_release_tool`,
`test_canonical_json`, `test_contract_identity`, `test_contract_values`.
They separate existing validation/fixture responsibilities and add missing tests
for existing public contracts. **No runtime library implementation changed in
this checkpoint.** Do not discard or reimplement this diff.

The final existing-source aggregate passed **644 unittest tests in 405.539 seconds**,
Ruff check/format and ty. Focused backlog checks passed 107 tests; related
archive/hygiene/rules/import checks passed 45. Ruff C901 has no findings and
native Lizard has no discovered function/module/project limit violations under
20/10/5. Its original four discovery errors remain errors. Independent review
of this remediation retained no new Critical/Important/Minor defects; it ran no
tests and did not certify STRICT acceptance. A formatting-only annotation wrap
was corrected before the passing final aggregate.

The selected mutation baseline now passes 62 tests. Original native batch:
1,436 cases = 1,199 killed, 236 survivors, one encoding-incompetent case.
That encoding case was reproduced, fixed in the test bootstrap, and rerun
natively as normal/killed. Differential reruns killed 97, then another 18 of the
original survivors; **121 remain under review**. These are incremental controls,
not a newly executed complete batch. Runtime source hashes remained unchanged.
Do not relabel the retained batch as a fresh passing mutation measurement.

### Exact remaining work

1. Resume survivor review from the raw round-2 results. Three likely next
   regressions were identified but **not added**: valid Unicode scalars U+D7FF
   and U+E000 adjacent to the surrogate range. Add positive direct-text/parameter
   cases and rerun the corresponding surviving boundary mutations. Also assess
   the array-count check moved from phase 2 to phase 1 against the approved
   deterministic error-order contract (design around line 1413); do not invent
   a new error priority merely to kill a mutation.
2. Disposition every remaining meaningful survivor. Several concern private
   signatures, deferred private annotations, closed vocabularies, Enum/Boolean
   identities, literal identities, redundant guards or repeated pure phases.
   Do not declare all harmless without checking reachable public behavior.
   CPython 3.12.15's `Objects/unicodeobject.c` was inspected for Latin-1 iteration
   caching; that evidence does not establish arbitrary string-identity equivalence.
3. Review the 22 retained Bandit findings in context: 11 B404, eight B603, one
   B607, one B105 path-string false-positive candidate, one medium B310 opener
   advisory. There were no analyzer errors. Subprocess argument vectors/ownership
   and the bounded fixed-origin PyPI caller checks were inspected, but no clean
   security measurement was declared. Preserve raw findings; no blanket suppression,
   scope narrowing or threshold workaround was applied.
4. Update the existing evidence/plan after dispositions, verify affected changes,
   and save the remediation through normal installed hooks. It is intentionally
   **uncommitted** at this handoff. Final measurements must track affected inputs.

**External/open acceptance:** cognitive UNKNOWN until Jeff/upstream extracts the
shared library from gzkit and integrates its contract into the starter. The old
library was a bust: no complexipy substitute, copied gzkit code, local analyzer,
or invented equivalent threshold. Lizard 1.24.3 omits inline definitions in
`formats/xplane_fdr/config.py`, `reader.py`, `sinks/xplane_fdr.py`, and the identity
test Protocol; do not rewrite sound code for that parser. Two native pip-audit
attempts timed out at 600 seconds; bounded Windows tree cleanup is corrected and
proved, but network proof is UNKNOWN. Do not retry without a relevant change.
Exact-commit remote CI is UNKNOWN; Git sync, main integration and releases retain
separate authorization gates. No release is authorized. The broader weak-test
audit is still open.

### Local evidence and continuity

All execution evidence is local-only under
`.superpowers/sdd/2026-10-25-strict-heavy-starter-onboarding/`:
`progress.md` records completed Tasks 1–3/5–6 and the still-open Task 4;
`task4-remediation-quality-retry.log` proves the 644-test aggregate;
`task4-backlog-all-focused.log` and `task4-tooling-fixtures-focused.log` hold the
focused checks. `task4-survivor-rerun.jsonl` and `task4-survivor-round2.jsonl`
retain work IDs/diffs/results; their summary JSON files prove 97/18 additional
kills. `task4-bandit-current.json`, `review.md` and
`review-remediation.md` preserve analysis/review context. Foundation evidence is
`task7-offline-hygiene.log`, `task7-coverage.json`,
`task7-native-fresh-result.json`, and `task7-installed-typing.json`.

Retained external artifacts:
`C:/Users/Jeff/AppData/Local/Temp/fdau-strict-artifacts-93a10c233f364f4da2cd32a1aac741e7`.
Installed test environment:
`C:/Users/Jeff/AppData/Local/Temp/fdau-strict-wheel-a715d8a733a047aba95a5a7795e6fe7f`.
They were checked present at handoff; recheck before reuse. Detailed hashes and
provenance are in the dated review. Preserve the ignored ledger while work is
open. No verification process remains intentionally running.

Standing authorization covers the approved onboarding plan and necessary
tooling/test remediation; it survives the handoff. It does not grant a merge,
push, publication, Backplane activation or cognitive-library implementation.
Use the project adapters, `superpowers:executing-plans`, TDD/verification and
the selected gz-skills review/quality workflows; do not restart planning.

## Historical checkpoint — 2026-10-04, C1.3 draft review and test-quality concern

Observed 2026-10-05 01:02 UTC before this checkpoint: `main` at
`e56e6a9de3ba961315f2d60d5ba22c5daca1ddc0`, with only the primary worktree.
The fetched remote and final save-point state must be rechecked on return.

**Current objective:** Preserve the unapproved
[C1.3 draft plan](docs/superpowers/plans/2026-10-04-c1-3-typed-values-payload-references.md)
and the unresolved test-quality/workflow reliability concern. C1.3 remains
`specified`, unselected, at 0/4 gates. No C1.3 implementation or plan approval
occurred. C1.2 remains verified and locally integrated as recorded below.

**Latest result and correction:** Review initially treated the assertions in
`tests/test_backlog_governance.py:977` requiring C1.3 to remain draft, without
approval or completion evidence, as a plan-maintenance obligation. Jeff
challenged that recommendation. The agent withdrew it: those assertions freeze
temporary state rather than test approval/evidence rules. They remain in the
checkpoint's existing draft-related test edits; they are unresolved, not an
accepted enduring test requirement. The draft's self-review PASS does not close
this finding or grant execution authority.

The durable [test-quality audit](docs/reviews/2026-10-04-test-quality-audit.json)
inventories 581 methods in 41 test modules and identifies a conservative lower
bound of 19 additional weak methods: ten documentation wording/metadata checks,
six skill-guidance phrase checks, and three delivery-state/handoff snapshots.
It lists exact locations, correction shapes, other candidates, and exclusions.
This was static screening with candidate inspection, not an exhaustive mutation
audit or certification of unflagged tests. Two in-memory demonstrations showed
a keyword-only document passing an explanatory-documentation check and approved
C1.3 metadata failing the draft snapshot. Neither modified repository files.

**User concern:** Jeff questioned how repeated Superpowers use can coexist with
these failures. Current `writing-good-tests.md` explicitly prohibits change
detectors and replacing behavior checks with text presence. Older plans
prescribed some of the offending assertions; later implementation and review
preserved the pattern. The agent acknowledged that procedural checkpoints did
not enforce substantive test quality here. No upstream skill defect, historical
skill-version explanation, or approved workflow redesign was established.
Do not treat another declaration of skill compliance or a passing suite as
resolution. Trace proposed tests to requirements, observable failure, a realistic
defect they detect, and legitimate changes they must allow.

**First permissible action on return:** Read project authorities and run backlog
`audit`/`next`, then address the test-quality finding with Jeff before treating
the C1.3 draft as ready for execution. Inspect the audit's cited assertions and
distinguish stable contracts from temporary-state or prose snapshots. A corrected
test must exercise the consuming behavior; deleting every governance test is
not the proposed correction. Test remediation and any workflow change still
need their appropriate authorized scope. C1.3 selection and implementation
require explicit plan approval. Stop on audit findings or changed authority.

**Verification and local state:** Checkpoint verification passed 63 focused
documentation/governance/public-API/project-skill tests, strict MkDocs build,
the documentation coverage gate (41.6% against 40%), focused Ruff lint/format,
and ty. Backlog audit/next found no findings and recommend `write_plan C1.3`.
The project-skill tests emit intentional failure messages from injected runners;
they did not execute a real full hygiene gate. The complete quality/hygiene
gate was not required for this documentation/governance-only save point.
Explicit checkpoint hooks passed Ruff lint/format and detect-secrets after
removing optional source-file checksum fields from the audit report. Those
generated hashes were verified false positives; the secret baseline was not
changed. The initial checkpoint excluded the pre-existing `uv.lock` changes.
Jeff subsequently requested that they also be handled and synced. Their origin
remains unestablished, but their contents were reviewed and validated unchanged:
lock revision 3 to 5, ten development/transitive version updates, no packages
added or removed, and one new `virtualenv` dependency edge to the already-locked
`packaging` package. Runtime dependencies remain empty. Offline lock check and
frozen sync passed with uv 0.12.23 and Python 3.12.15. The complete offline hygiene
gate passed all 581 tests with 95% coverage, code/documentation/backlog checks,
and fresh wheel/sdist metadata and inventory checks. This validates the retained
lock update; it does not resolve the test-quality findings above or establish a
complete dependency refresh. The follow-up save point includes `uv.lock` and
this handoff update. Recheck its final Git state on return. The temporary audit
copy under Jeff's system temp directory is
local-only; the linked repository copy is the durable report.

**Authorization:** Jeff explicitly requested this handoff and ordinary Git sync.
He also explicitly requested handling the remaining lockfile. That authorizes
its reviewed, verified follow-up commit/push, not test remediation completion,
C1.3 implementation, dependency refresh, tags, publication, release, or edits
to another repository. Release gate G1 remains waiting.

## Prior resume point — 2026-10-04, after C1.2 local integration

Observed 2026-10-05 00:01 UTC, before this handoff and requested ordinary Git
sync: `main` was clean at `c7785870e74c16966794352527fb6a28b8a4fa17`,
15 commits ahead of the freshly fetched `origin/main`, with no remote
divergence. Only the main worktree exists. Recheck Git on return because this
handoff's sync creates a later commit.

**Current objective:** C1.2 identity, hashing, references, authority, and
provenance is complete, `verified` at 4/4 gates, and integrated into `main`.
Its [completed plan](docs/superpowers/plans/2026-10-04-c1-2-identity-hashing-references-provenance.md),
[completion record](.superpowers/sdd/2026-10-04-c1-2-identity-hashing-references-provenance/completion.md),
and [review disposition](.superpowers/sdd/2026-10-04-c1-2-identity-hashing-references-provenance/review.md)
are durable evidence. The completed selection was cleared through the guarded
backlog adapter; no child is selected. The resulting audit has no findings and
reports `action=write_plan child=C1.3`. C1.3 typed values and content-addressed
payload references remains `specified`, at 0/4 gates, with no plan.

**Latest result:** The independent whole-branch review identified five
Important findings; all were reproduced and resolved with regression tests.
The final complete offline hygiene gate passed 581 `unittest` tests with 95%
coverage on Python 3.12.14, strict documentation and code checks, and fresh
wheel/sdist metadata and inventory checks. After the user chose local
integration, main fast-forwarded to the exact reviewed branch HEAD. Frozen
offline sync, lock check, backlog audit, two live-state tests, a fresh external
artifact pair, and external installed-wheel smoke all passed on main. Its
artifact hashes match the branch gate. The temporary feature worktree and
branch were then removed. The complete gate was not repeated on the identical
merged tree, following the repository's exact fast-forward verification rule.

**Local-only evidence:** The verified main artifact pair and isolated Python
3.12.14 environment remain at
`C:\Users\Jeff\AppData\Local\Temp\xplane-fdau-merge-8cc468f4616f4b34910d0a58a8198793`.
Its `main-verification.json` records the main HEAD and artifact digests. The
ignored receipt at
`.superpowers/sdd/2026-10-04-c1-2-identity-hashing-references-provenance/local-integration.json`
adds focused main-check results. These paths were verified locally and are
not available from a fresh clone; the tracked completion and gate receipts
remain the portable evidence. The completion record's pending-integration
sentence describes its earlier observation and is superseded by this handoff.

**First permissible action on return:** Read `AGENTS.md` and its linked
authorities, then run backlog `audit` and `next`. Use
`superpowers:writing-plans` to draft one reviewable C1.3 implementation plan
under the approved
[canonical-contract design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md).
Expected result: exact files, test-first `unittest` steps, verification commands,
and commit boundaries for C1.3. Obtain plan approval before selecting C1.3 or
implementing it. Stop on an audit finding, changed authority, or missing
approval.

**Decisions and boundaries:** The user approved native implementation followed
by one independent whole-branch review, selected local integration, and then
explicitly requested this handoff and ordinary Git sync. These approvals cover
the completed C1.2 work and its save point. Later model factories, public model
hash dispatch, family loaders, schemas, and corpus resources retain their
approved later-child ownership. Python 3.12 is the sole supported minor;
runtime remains pure Python and standard-library-only. Release gate `G1`
remains waiting, with tags and publication separately gated.

## Prior resume point — 2026-09-28, Python tooling survey

Observed 2026-09-28 00:45 UTC, before this handoff and requested ordinary Git
sync: `main` was clean at `d1d1cadf778e2f614a877fa13c5d124af97a137e`
and matched `origin/main`; only the main worktree existed. Recheck Git state on
return because this handoff's sync will create a later commit.

**Current objective:** `C1.2` identity, hashing, references, authority, and
provenance is `specified`, dependency-ready, and at 0/4 gates with no plan. No
child is selected. Its approved
[canonical-contract design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md)
governs planning; `BACKLOG.md` owns current delivery state. `C1.1` is verified
at 4/4 gates with accepted review; see its
[completed plan](docs/superpowers/plans/2026-09-27-c1-1-canonical-json-number-encoding.md)
and [completion evidence](.superpowers/sdd/2026-09-27-c1-1-canonical-json-number-encoding/completion.md).

**Latest result:** This checkout's uv-managed `.venv` now uses CPython 3.12.14
through ordinary `uv run python`; `.python-version` intentionally selects the
3.12 minor line and `pyproject.toml` requires `>=3.12,<3.13`. The complete
quality gate passed 554 `unittest` tests with 94% coverage on 3.12.14. A fresh
external wheel/sdist passed strict metadata and inventory checks, and the wheel
passed installed smoke in a separate uv-managed 3.12.14 environment. The
temporary artifact directory was removed on success. No tracked file changed
for the interpreter switch, and no Python-version Git commit was needed.

**Cross-project survey:** Five of the ten local repositories under the sibling
`xp` directory have Python manifests. `q4xpcc` is the direct XPPython3 plugin;
this repository is the future canonical core. XPPython3 4.x includes its own
private Python 3.12 runtime, independent of uv's local development interpreter
([upstream documentation](https://xppython3.readthedocs.io/en/latest/)).
`xplane-webapi` supplies a separate Web API client consumed by q4xpcc's local
supervisor; Ortho4XP is a scenery generator; xpcl is an NNG/PySide6 telemetry
client. Read-only file and existing-environment observations:

| Repository | `.python-version` | `requires-python` | Existing `.venv` |
| --- | --- | --- | --- |
| `q4xpcc` | `3.12.13` | `==3.12.*` | 3.12.14 |
| `xplane-fdau` | `3.12` | `>=3.12,<3.13` | 3.12.14 |
| `xplane-webapi` | `3.13` | `>=3.12,<3.14` | 3.13.14 |
| `Ortho4XP` | `3.13.14` | `>=3.13,<3.14` | 3.13.15 |
| `xpcl` | absent | `>=3.9` | 3.13.14 |

The exact local selectors for q4xpcc and Ortho4XP trail their observed
interpreters; their `pyproject.toml` ranges admit those patches. No sibling
repository was edited. `xplane-webapi` already had a modified `BACKLOG.md`
when inspected; preserve that unrelated work. All observations above are
local-only and must be rechecked before a cross-repository change.

**First permissible action on return:** Read `AGENTS.md` and its linked
authorities; run backlog `audit` and `next`. Use `superpowers:writing-plans` to
draft one reviewable C1.2 implementation plan from the approved design. Obtain
plan approval before selecting C1.2 or implementing it. If the next request is
to align other repositories' exact Python selectors, inspect each repository's
own instructions and state first; this handoff grants no cross-repository edit
authority. Stop on an audit finding or changed authority. Release gate `G1`
remains waiting; no tag or publication was authorized.

## Prior resume point — 2026-09-27, after C1.1

Observed 2026-09-27 23:28 UTC, before this handoff and Git-sync commit: `main`
was clean at `93a04156d460e920e2711ae97e514ca53f6bac3b`, one commit ahead
of `origin/main`. Only the main worktree existed. Recheck Git and backlog state
on return because the requested ordinary sync will create a later commit.

**Current objective:** `C1.2` identity, hashing, references, authority, and
provenance is the first dependency-ready local child. It is `specified`, has
0/4 delivery gates, and has no implementation plan. The governing
[canonical-contract design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md)
is approved. `BACKLOG.md` remains the delivery-state authority; no child is
currently selected.

**Latest result:** `C1.1` canonical JSON and binary64/integer encoding is
`verified` with 4/4 gates and accepted independent review. Its
[completed plan](docs/superpowers/plans/2026-09-27-c1-1-canonical-json-number-encoding.md),
[completion record](.superpowers/sdd/2026-09-27-c1-1-canonical-json-number-encoding/completion.md),
and [review](.superpowers/sdd/2026-09-27-c1-1-canonical-json-number-encoding/review.md)
are committed. The completed C1.1 selection was cleared in `93a0415`; this
local commit is the one pending sync at observation time. Strict backlog
`audit` and `next` on 2026-09-27 found no findings and recommended
`action=write_plan child=C1.2`.

**First permissible action on return:** Read `AGENTS.md` and its linked
authorities; run backlog `audit` and `next`. Use
`superpowers:writing-plans` to create a single-child C1.2 implementation plan
from the approved design. Expected result: a reviewable plan with exact files,
test-first steps, verification, and commit boundaries. Obtain plan approval
before selecting C1.2 or starting implementation. Stop on an audit finding,
changed authority, or missing approval.

**Maintenance and boundaries:** The explicit 2026-09-27 dependency refresh
passed its guarded apply, focused `unittest`, full offline hygiene, and external
Python 3.12 source and installed-wheel checks. `uv lock --upgrade` changed no
tracked files. Four older transitive packages remain explained by Wily/Radon
version constraints. The project supports only Python 3.12
(`>=3.12,<3.13`); the local virtual environment uses 3.12.13. The installed
`gz-skills@gz-skills` plugin remains verified at the project pin v0.5.0.
Temporary refresh artifacts under the system temp directory are local-only.
No tag, package publication, GitHub release, or q4xpcc edit was authorized.
Release gate `G1` remains waiting.

## Prior resume point — 2026-09-27, before C1.1

Observed 2026-09-27 20:58 UTC, before this handoff commit: `main` was clean at
`b6f55eb92ede85df07fe8125d0cd419d00ae59ac` and matched `origin/main`.
`git worktree list` showed only the `main` checkout; no C1.1 feature branch or
worktree exists. Recheck Git state on return because this handoff's Git sync
will create a later commit.

**Current objective:** C1.1 canonical JSON and number encoding. Its approved
[cross-epic design](docs/superpowers/specs/2026-08-09-xplane-fdau-canonical-measurement-contracts-design.md)
has a reviewed but still
[draft implementation plan](docs/superpowers/plans/2026-09-27-c1-1-canonical-json-number-encoding.md).
`BACKLOG.md` remains authoritative: C1.1 is `specified`, has 0/4 gates, and
has not entered implementation. No C1.1 runtime code or delivery evidence was
created by the planning reviews or Git sync.

**Last completed action:** The Python 3.12-only compatibility and dependency/
tooling maintenance, together with the C1.1 draft plan, was committed as
`b6f55eb` and synced to `origin/main`. Full offline hygiene passed with 94%
coverage; a fresh wheel/sdist passed strict metadata and exact-inventory
checks, and an external Python 3.12.13 installed-wheel smoke passed. Its
temporary artifact directory is local-only:
`C:\Users\Jeff\AppData\Local\Temp\xplane-fdau-sync-5254e7536f78456abfe6153ccc766e17`.
No tag, package publication, GitHub release, or q4xpcc edit occurred.

**First permissible action on return:** Read `AGENTS.md` and its linked
authorities; run backlog `audit` and `next`. Obtain Jeff's explicit approval
of the C1.1 plan before selecting the child or starting Task 1. With that
approval and a clean current `main`, use `superpowers:using-git-worktrees` to
create the temporary C1.1 branch/worktree from the verified HEAD, then follow
the plan's guarded lifecycle and test-first execution steps. Stop on an audit
finding, changed baseline, or missing approval; this handoff and ordinary Git
sync do not themselves authorize implementation or release.

## Prior resume point — 2026-09-20

2026-09-27 maintenance update: support the Python 3.12 minor line only for
now, matching XPPython3's embedded interpreter. The dependency refresh includes
the reviewed gz-skills v0.5.0 project pin and ignored Superpowers checkout
v6.4.2. Direct full offline hygiene passed. The guarded refresh also exited
successfully after its external Python 3.12 source tests and installed-wheel
smoke. Four older transitive packages remain constrained by Wily/Radon; no
release or Git sync was performed.

**Current objective:** `B1.1` source-layout migration is verified with 5/5
gates and accepted independent review, and was locally integrated into `main`
at `1f66a0f`. The temporary worktree and branch were removed. The project
reviewed and adopted `gz-skills` v0.4.0 before implementation; the project pin
has since advanced to reviewed v0.5.0. `T2.2` remains
verified. `C1.1` is the next canonical local child.

**Exact next action on return:** Read AGENTS.md and the linked authorities,
then run the backlog audit and next commands. The reported action is to write
an approved single-child `C1.1` implementation plan from its approved
canonical-contract design.

## Observed state and evidence

- B1.1's 17 runtime files moved byte-for-byte to `src/xplane_fdau`; the
  flat package root is gone. The completed plan and five gate receipts are
  under `docs/superpowers/plans/2026-08-09-src-layout-migration.md` and
  `.superpowers/sdd/2026-08-09-src-layout-migration/`. Full offline hygiene
  passed 521 `unittest` tests, 43.9% coverage, strict docs, and exact wheel/sdist
  checks. External Python 3.12.13 installed-wheel smoke passed. The merged
  `main` checkout passed full offline hygiene: 521 tests in 292.904 seconds,
  43.9% coverage, strict docs, pre-commit, and exact artifacts. The old flat
  checkout held only ignored Python bytecode after merge; its verified cache
  tree was removed before the final green gate. No release or Git push occurred.
- T2.2 was integrated into `main` at commit `431c195`. Its verified backlog
  state and evidence remain unchanged by the local quality-cadence correction.
- The approved plan is
  `docs/superpowers/plans/2026-09-19-t2-2-dependency-toolchain-refresh.md`.
  Completion, review, and four gate records are under
  `.superpowers/sdd/2026-09-19-t2-2-dependency-toolchain-refresh/`.
- T2.2 originally pinned uv 0.12.17; the 2026-09-27 tooling-policy correction
  retains a supported minimum so newer uv releases can run. The adapter inventories 98 registry packages and records
  five constrained package versions with their upstream owners. It reported no
  yanks, advisories, or blockers. Runtime remains pure Python and
  standard-library-only.
- One wheel/sdist pair passed exact inventory checks. CPython 3.12, 3.13,
  and 3.14 each passed 511 source `unittest` tests and an installed-wheel
  smoke test. The final active-Python quality gate passed 516 tests and 43.9%
  coverage against a 40% minimum. Review accepted the implementation with no
  remaining Critical or Important findings. A minor matrix subprocess-timeout
  concern is recorded in `review.md`.
- The installed and enabled `gz-skills@gz-skills` plugin was verified at
  version 0.5.0 from the pinned official Git marketplace. The original v0.4.0
  adoption evidence is in
  `.superpowers/sdd/2026-09-20-gz-skills-v0-4-0/review.md`. T2.2's Python/uv
  adapter does not mutate the plugin cache.
- The ignored Superpowers checkout was fast-forwarded from v6.3.0 to upstream
  v6.4.2 for the 2026-09-27 dependency refresh.

## Fast local closeout follow-up

Jeff approved a limited correction after B1.1's repeated multi-minute gates:
move existing static, security, docs, hook, and live-state checks ahead of
coverage; keep one complete branch gate; and use documented focused checks
after an exact local fast-forward. The implementation uses existing commands
and adds no merge verifier. Independent review found no code defect; its plan
checklist finding was corrected. The single full offline hygiene gate passed
on branch commit `af2bfc2`, with 94% coverage and an exact wheel/sdist pair.
Jeff selected local integration. Main fast-forwarded to `ed10665`; frozen
sync, lock, strict backlog audit, both live-state tests, and one fresh external
wheel/sdist pair passed on that exact commit. The temporary worktree and branch
were removed. No Git push or release action occurred. The approved design and
plan are under
`docs/superpowers/specs/2026-09-20-fast-local-closeout-design.md` and
`docs/superpowers/plans/2026-09-20-fast-local-closeout.md`. C1.1 remains
the next canonical child planning action after this maintenance correction.

## Quality-control follow-up

Jeff flagged the repeated multi-minute full gates during B1.1 as too costly
for ordinary implementation work. The required full suite took 314.236 seconds
on the feature branch and 292.904 seconds after local integration; failed
closeout runs repeated it while exposing a live-state assertion, a generated
secrets baseline update, and stale bytecode in the pre-existing main checkout.
The current cadence still calls for focused checks during edits and one full
gate at stable closeout. The gate order and state-sensitive preflight were revised in the fast local
closeout change above. Measuring the slow unittest cases remains a separate
follow-up before any suite-policy change.

Jeff narrowed the fix to the local development cadence; GitHub Actions
remains unchanged. During edits, run focused `unittest`, Ruff, and ty checks.
Pre-commit runs staged-file Ruff lint/format and detect-secrets checks without
a full test suite or metrics reports. At stable closeout, run the complete
active-version quality gate once. Edits to existing source files use the
standalone gate. Full offline hygiene is for package layout, shipped resources,
metadata, lockfiles, build rules, or artifact-validation changes; it invokes
the quality gate directly once, then checks docs, hooks, and a fresh artifact
pair. Documentation and governance edits use their focused checks. Reserve
the Python 3.12 source/installed-wheel check for
version-sensitive changes and release readiness. The matrix subprocess-timeout
concern from T2.2 review remains a separate follow-up.

## Decisions and boundaries

Jeff explicitly authorized this handoff and ordinary Git sync. That covers a
checkpoint commit and ordinary push; it does not authorize a tag, package
publication, GitHub release, or q4xpcc edits. T3.1 guarded Git-sync tooling
remains a separate specified child. No release is authorized.

Identity and native-FDR-kernel migration: implemented and verified, but unreleased.
Completed implementation plan:
`docs/superpowers/plans/2026-08-09-xplane-fdau-identity-fdr-kernel-migration.md`.
The next canonical vertical slice retains measurement, binding, observation, sample, frame, timing, and quality contracts. ARINC and FDM/FOQA support remain
inside this repository's approved scope.

`D1.1` canonical C1-C4 design approval is verified.
`D1.2` acquisition, recording, projection, and pinning contract design is verified.
`D1.3` reviewed q4xpcc Phase 24A consumer handoff is verified.
`I1.0` is eligible as the next reportable external action.

`I1.0` now permits Phase 24A specification and plan reconciliation because `D1.3` is verified.
`I1.1` permits delivered contract-model, schema, fixture, and runtime adoption only after `C4.4`.
`I1.2` permits live XPLM acquisition adoption only after `A1.9`.
The reviewed brief is `docs/architecture/q4xpcc_phase_24a_contract_handoff.md`.
Do not edit q4xpcc from this repository.
