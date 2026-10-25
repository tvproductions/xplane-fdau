# Skills-first Native Adoption Design

- **Governance:** active
- **Status:** approved
- **Date:** 2026-10-11
- **Decision owner:** Jeff / tvproductions
- **Roadmap epic:** `T2`
- **Roadmap children:** `T2.1`, `T2.2`
- **Approval:** 2026-10-25 — Jeff / tvproductions

## Intent and authority — October 25, 2026

Jeff requires onboarding to `tvproductions/gz-skills-first-starter`, with tight,
strong and aggressive application of its Astral engineering guidance. Alignment
is mandatory. Installing plugins or deferring engineering reconciliation cannot
satisfy this request.

This revision reconciles the October 11/18 proposals and the pre-existing,
uncommitted October 25 alignment review. It supersedes the unreleased 0.3.2
target, zero-template-skill assumption and two-stage proposal that could declare
native adoption complete while leaving engineering alignment pending. Prior
proposals remain in Git history; their findings are carried forward here.
Jeff approved the reconciled design on October 25, explicitly selecting heavy,
keeping Backplane deferred, and requiring STRICT compliance. Implementation
planning proceeds under this approval; the written plan requires review before
execution.

During plan review, Jeff clarified that the originally selected cognitive
complexity library was unsuccessful. Its replacement must be extracted from
gzkit first; that extraction has not occurred. Record the cognitive gap and
continue independent onboarding work, without claiming strict acceptance.
Uniform, reliable behavior across adopting projects remains the goal.

This is brownfield first adoption and a crosscutting maintenance amendment under
T2.1/T2.2, not a new runtime feature. Do not reopen their verified records or
advance a product child. FDAU does not use gzkit. BACKLOG remains the only mutable
delivery ledger; ROADMAP, requirements, domain specifications, historical
evidence and release gates remain authoritative. No other application repository
or upstream implementation is changed.

## Reviewed target and starting state

The latest published stable starter checked October 25 is **v0.6.0**, published
October 24, at `c0a6945b2170e1cf5bee3e80738916f5b62d13a5`.
Its bundle selects:

| Component | Selected immutable source | State |
| --- | --- | --- |
| Superpowers v7.0.0 | `bb92a77741419a4ab5f06e711a283343f1ada0c3` | enabled |
| gz-skills v0.8.0 | `75bcd11ee9371ecff1a7b3432d2af29d4bdbb788` | enabled |
| Backplane prerelease | `d0eeee829c491da02351e793544aa16ad96461bf` | disabled |

Recheck published releases at implementation entry and review any changed target.
Verify tag, full commit, bundle and native catalogs together. Do not adopt
unreleased main or independently replace component pins under an older starter
provenance record. The prior review observed unreleased main declaring 0.7.0,
SP v7.0.1 and blocked cognitive acceptance; that is not the released baseline.

FDAU main is `3a5211bfe3c1ab80e25758fce61356dd6ef7cbef`.
C1.3 is verified, no child is selected and the product recommendation is
`write_plan C1.4`. Mandatory onboarding maintenance proceeds separately.

Observed gaps and existing assets:

- No starter lock, generated instruction fragment, explicit lane settings or
  template-owned `update-gz-template` skill.
- Configuration requests gz-skills v0.5.0; October 25 native inventory reports
  installed/enabled `gz-skills@gz-skills` **0.8.3**, superseding the earlier
  0.8.0 observation. Installed version does not prove adopted provenance.
- Superpowers uses an ignored checkout and junction. Other projects' native
  plugin copies are disabled here and are not FDAU's selected authority.
- Runtime is pure Python and standard-library-only, under `src/xplane_fdau`,
  using uv_build, `py.typed`, unittest and external installed-wheel checks.
- Python selects minor-only `3.12`, with support `>=3.12,<3.13`.
  Ruff selects E/F/W without an explicit target; ty uses error severity without
  an explicit target. Exact execution and effective configuration need proof.
- Hooks omit ty/unittest and include detect-secrets. Routine CI invokes deep
  analysis and repeats full unittest. Branch coverage is disabled.
- Existing dependencies omit part of the required on-demand analyzer assortment.
  Existing coverage/Interrogate floors are 40%; Xenon limits are C/B/A.
- HANDOFF and the BACKLOG introduction have stale C1.3 summaries. The managed
  child ledger and completed evidence own current state.
- The weak-test audit remains unresolved; a passing suite does not resolve it.

## Explicit lane and retained governance

Jeff explicitly selected **heavy** on October 25. Record that choice through
the pinned `gzs-project-setup` workflow during implementation; a specification
entry alone does not establish installed settings or readiness. Both lanes
require the same full Python/Astral
baseline, deeper analysis and release discipline.

For heavy, distinguish intended SP + Backplane + gz-skills composition from
observed readiness. Backplane remains disabled until its readiness and separate
integration decision. Whole-heavy-stack readiness cannot pass while it is
deferred. Python acceptance and SP/gz-skills discovery have independent results.
Do not migrate FDAU requirements, BACKLOG or HANDOFF into Backplane records.

## Required Astral engineering contract

Adopt and verify every applicable requirement in the reviewed starter's
`docs/engineering/astral-alignment.md`, `python.md` and
`astral-acceptance.md`. The default is adoption and verification, not an
optional recommendation. Alternatives and previews need explicit decisions.
A departure needs a demonstrated constraint, evidence, owner and revisit
condition; existing layout or convenience is insufficient.

### Reproducible environment and effective configuration

Retain the XPPython3-bound Python **3.12** family and empty runtime dependencies.
Verify the latest stable host-compatible 3.12 patch against official sources;
record its exact value in `.python-version` and CI. Align
`requires-python = ">=3.12,<3.13"`, Ruff `py312`, ty's 3.12 target and actual
execution. Keep actual embedded-host evidence separate where applicable:
this core does not ship a simulator adapter.

Centralize supported settings in `pyproject.toml`. Inspect uv/Ruff/ty discovery,
configuration precedence, relevant nonsecret overrides, analyzed paths and
executable origins. Document approved tool families, check freshness within
them and verify exact uv, uv_build and tool selections. Keep selected versions
stable between authorized maintenance events; do not copy starter execution
patches as permanent adopter requirements.

Use uv for interpreter/environment management, dependency edits, resolution,
locking, builds and execution. Routine commands and CI use `--locked`, failing
on stale declarations. Frozen offline checks retain an explicit lock check;
frozen alone cannot establish freshness. Exact sync targets only the intended
project environment and reviewed compatible groups. Preserve dependency purpose,
sources, runtime/dev distinctions and build isolation. Never hand-edit locks,
resolve moving latest on every run or use overlays as baseline proof.

### Strict routine gate

Local commands, installed pre-commit hooks and routine CI enforce the same four
checks: **Ruff check, Ruff format --check, ty and unittest**, through locked
project tools and documented scopes. Run full unittest once per aggregate,
not once per changed filename. Retain separate artifact/installed-wheel CI jobs.

Adopt the reviewed Ruff families `E4,E7,E9,F,I,UP,B,SIM,RUF`; review and fix
findings rather than selecting ALL, blanket-ignoring or shrinking scope.
The formatter owns formatting. Keep ty diagnostics at error severity.
Cover runtime, tests, tools and repository-owned Python adapters; exclude
external sources/generated content and document genuinely distinct scopes.

Move deeper analysis, including detect-secrets, outside the four routine hooks
and routine CI without dropping the controls. Keep explicit adoption/release
acceptance and on-demand commands. Reconcile quality/hygiene/dependency-refresh
adapters, instructions, documentation and behavior tests with the new cadence.
Record timings and avoid redundant complete-suite invocations.

CI uses Astral setup-uv, reviewed immutable Action revisions, an explicit uv
version and validation of the exact Python pin. An edited workflow is not an
observed CI pass. Remote verification remains pending until exact-commit CI is
observed following separately authorized ordinary synchronization.

### Mandatory deeper acceptance

Execute applicable minimum tools at adoption and release acceptance, outside
routine hooks/CI:

| Dimension | Required tool and interpretation |
| --- | --- |
| Cyclomatic complexity | Ruff C901, maximum 20 per function |
| Cognitive complexity | OPEN dependency: shared replacement library to be extracted from gzkit; no accepted measurement yet |
| Function/module/project complexity | Lizard, explicit counting population and aggregates |
| Class cohesion | cohesion, scores reviewed against actual responsibilities |
| Documentation | Interrogate and review of usefulness/correctness |
| Dead code | Vulture, investigating consumers before deletion |
| Security | Bandit and retained detect-secrets controls, reviewed findings |
| Coverage | Coverage.py branch and statement measurement through unittest |
| Mutation strength | Cosmic Ray, bounded consequential scope and unittest |
| Dependency declarations | deptry, preserving legitimate dev/dynamic usage |
| Known vulnerabilities | pip-audit against exact uv-lock exports, no second resolver |
| Architectural imports | Import Linter contracts for actual FDAU boundaries |

Verify compatibility on selected Python 3.12 with representative invented
fixtures and actual project scopes; pin/lock tools in appropriate development
groups. Inventory or another project's receipt is not acceptance evidence.
Retain exact commands, tool sources/versions, scope, results and reviewed findings.

#### Cognitive analysis dependency — open

Jeff's October 25 plan-review decision supersedes the released starter's
complexipy selection for this migration. Do not install or configure that
rejected tool as acceptance proof, reproduce a cognitive analyzer locally, or
copy code from gzkit. FDAU remains outside the gzkit governance ecosystem.

Owner of the extraction/readiness decision: Jeff / upstream library and starter
maintainers. The extraction is outside this repository's onboarding scope and
has not occurred. Package name, release, API and compatibility are unverified;
do not invent pins or an integration contract. Revisit when the extracted
library is available and the shared starter has a reviewed adoption contract.
Adopt that common contract so projects receive uniform analyzer behavior.

Keep cognitive analysis and its affected A18 evidence UNKNOWN, blocked by the
external prerequisite; it is not N/A, waived, or PASS. The prior target of 15
is historical policy input, not proof of equivalent counting by the replacement.
Verify the shared tool's counting, thresholds, Python 3.12 compatibility and
actual FDAU results before closing the gap. Other onboarding work may proceed;
strict overall acceptance remains incomplete until this proof exists.

Preserve the existing 40% coverage and Interrogate floors. Report statement and
branch results separately and expose consequential gaps; never lower a floor to
accept new branch measurement. No unrelated gzkit or project threshold applies.

Record legacy Xenon C/B/A scores and comparable Lizard measurements before
retiring Xenon/Radon. Retain the stricter numeric ceilings **20/10/5** under a
reviewed function-based counting contract, rather than silently adopting the
starter's 20/20/20 defaults. The metrics differ: review population, scores and
verdict changes explicitly. Retire Wily after mapping useful history/measurements
to the retained evidence; preserve historical receipts.

Run all required dimensions even if another reports findings. Required failures
remain failures. Remediate necessary onboarding findings with behavior tests and
review. Do not add over-limit functions, raise ceilings, regenerate snapshots or
suppress findings to claim acceptance. A temporary regression baseline does not
establish strict adoption. If a correction requires separate behavioral design,
record the dependency and keep onboarding pending until resolved.

Mutation begins from a clean baseline in an isolated disposable checkout, using
unittest and consequential public seams; classify survivors. Never mutate the
working checkout or add redundant tests for a percentage. Trace changed tests
to requirements, observable failure, realistic defects and legitimate changes
they must allow. Correct affected weak snapshots without claiming the entire
prior weak-test audit resolved.

### Artifacts, code currency and release discipline

Build with `uv build --no-sources`, preserving the sdist-to-wheel path.
Record exact isolated build inputs independently of the runtime lock. Check
metadata, resources, licenses, typing marker, empty Requires-Dist and inventories.
New governance files and tools must respect the reviewed distribution boundary.

Verify imports, CLI, resources and representative public typed APIs in a fresh
Python 3.12 environment outside the checkout without source-path injection.
Review relevant Python 3.12 idioms/stdlib opportunities against versioned official
documentation and record adopt/defer/N/A decisions. Do not apply unavailable
3.14 features or start unrelated modernization.

Adopt independent product SemVer and a newly written PRD for every major,
including 1.0.0, within FDAU planning authority. Minor releases need coherent
selected bundles and compatibility notes. Existing G1 and separate release
authorization remain binding; onboarding does not authorize publication.

## Native sources, provenance and rollback

Use a separate clean checkout of the verified released starter and its existing
helper. Retain the agreed shared `skills-first-starter` catalog; add no FDAU
catalog, lock extension, installer or parallel checker. Review preview before apply.

The managed set includes `.skills-first/bundle.lock.json`,
`AGENTS.skills-first.md`, host configuration and
`.agents/skills/update-gz-template/SKILL.md`. Add the AGENTS pointer and retain
project-owned skills. Keep bundle, catalogs, lock, fragment and selected sources
coherent. Review installed 0.8.3 versus selected 0.8.0 explicitly; do not downgrade
or uninstall another project's shared plugin. Scope activation to FDAU and
disable its old source only with verified replacement. Native managers own caches.

Verify the existing Superpowers junction's real target before detaching only
the link nonrecursively. Keep the old checkout nondiscoverable for rollback.
Fresh-session observation must verify exactly one selected SP/gz-skills source
and actual availability/invocation of the template update skill. Installation
and file scans do not establish discovery.

Record initial Git/dirty state, source configuration and rollback references.
Restore reviewed prior configuration, instruction routing, tool declarations,
lock and discovery link from those references while preserving unrelated work.
Verify recovery in a fresh session. Never delete through junctions, reset user
changes or uninstall other projects' sources. A documented rollback procedure
is not an executed rollback test.

## Implementation sequence

1. Recheck authorities, audit/next, current release and starting dirty state.
2. Approve this reconciled written design and explicitly choose the lane.
   Write/review the executable onboarding plan, then isolate implementation.
3. Establish the A01–A18 record, source-to-target mapping, legacy measurements,
   effective configuration and tool compatibility.
4. Reconcile exact environment, strict routine checks, required on-demand
   tools/analysis and necessary findings in verified implementation tasks.
5. Apply reviewed native configuration/managed files; update project routing,
   packaging exclusions where necessary, adapters and stale current summaries.
6. Execute acceptance analysis, stable-candidate artifact/hygiene proof,
   installed behavior, hook observation and independent review. Avoid duplicate
   complete gates on an unchanged candidate.
7. Observe fresh-session discovery and exact-commit remote CI when ordinary
   synchronization is separately authorized. Keep unavailable proof UNKNOWN.
8. Use the normal finishing/integration workflow; retain rollback until main
   verification passes.

Engineering reconciliation is part of this onboarding objective. Implementing it
in verified slices does not permit a partial completion claim.

## Acceptance record

Keep a dated record under `docs/reviews/`, linked from existing authorities.
Expand every individual A01–A18 row with applicability/reason, actual command
and scope, observed result, evidence location and open work:

| Rows | FDAU proof |
| --- | --- |
| A01 | Identity, revision/dirty work, migration map and rollback |
| A02–A03 | Installed src imports, CLI/backend and pure-Python build |
| A04–A08 | Effective configuration, exact interpreter/tools, freshness, exact sync/lock and actual routine checks |
| A09 | Installed hooks and observed exact-commit CI enforcing routine checks |
| A10 | Dependency/source intent and empty runtime Requires-Dist |
| A11–A13 | Source-independent artifacts, clean installed public behavior, typing |
| A14 | Workspace applicability; verify the current single-distribution scope |
| A15 | Private/special-source applicability from actual metadata and nonsecret settings |
| A16 | Actual deployment/build triggers; separate core from external host adapters |
| A17 | Export/script/tool consumers, including vulnerability-audit export |
| A18 | Exceptions, deeper analysis, code currency and wider obligations |

Results are PASS/FAIL/UNKNOWN/N/A/EXCEPTION. N/A needs an absent triggering
feature. Exceptions need evidence, owner, accepted-by and revisit condition.
Required failed, unknown or stale proof blocks strict acceptance. Accepted
exceptions remain visibly conditional and do not satisfy Jeff's STRICT
compliance completion requirement. The documented Python 3.12 host lane and
disabled Backplane are baseline-defined selections, not waivers of applicable
Astral acceptance. Do not seek reduced compliance merely to close onboarding.

Report lane, helper configuration, Python acceptance, required analysis, native
discovery and deferred Backplane readiness separately. Do not equate an approved
design, configured helper or passing backlog audit with completed adoption.

## Implementation surfaces

| Surface | Responsibility |
| --- | --- |
| `pyproject.toml`, `.python-version`, `uv.lock` | Strict effective configuration, exact runtime/tools and groups |
| `tools/quality.py`, project quality/hygiene/dependency-refresh adapters | Routine versus explicit deeper gates; retained artifact/offline controls |
| Hooks and CI/readiness workflows | Matching routine commands, exact uv/Python, immutable Actions |
| Native config, lock, fragment, template update skill | Consistent starter provenance and fresh-session discovery |
| AGENTS, project skills and engineering guidance | Required policy, ownership and actual commands |
| Release/artifact tooling and meaningful fixture tests | Public behavior and prevention of governance/runtime leakage |
| Review evidence and BACKLOG/HANDOFF current summaries | Honest acceptance state, findings and rollback |

Use existing commands/upstream helpers where sufficient. Necessary composition
belongs in project tooling, not a parallel lifecycle. Exact paths, tests,
verification and commit boundaries belong in the implementation plan.

## Acceptance criteria

### T2.1 — Project repository-hygiene adapter and fresh artifact verification

- Strict Astral runtime/configuration, four routine checks, mandatory deeper
  analysis and installed-artifact proof are implemented and observed.
- Existing numeric limits and domain behavior survive reviewed reconciliation;
  affected tests exercise consuming behavior and realistic negative controls.
- Configuration/provenance/routing agree; fresh-session discovery verifies
  sources without duplicates or accidental Backplane enablement.
- Each A01–A18 row has an honest outcome; unfinished engineering reconciliation
  cannot be reported as completed onboarding.

### T2.2 — Governed dependency and toolchain refresh

- Record exact released starter/component sources, Python 3.12 execution and
  dated family/freshness/compatibility decisions.
- Verify required tools and actual results; preserve dependency intent, native
  cache ownership and other projects' sources.
- Use `update-gz-template` after discovery for template maintenance and canonical
  dependency workflows for tools. Review at adoption, scoped maintenance,
  quarterly on demand and release acceptance; no automatic schedule is created.
- Preserve requirements/backlog/release authorities and distinguish lane intent,
  engineering acceptance and deferred whole-stack readiness.

## Sources and review status

- [Released v0.6.0](https://github.com/tvproductions/gz-skills-first-starter/releases/tag/v0.6.0)
- [Brownfield adoption](https://github.com/tvproductions/gz-skills-first-starter/blob/v0.6.0/docs/adoption-0.5.md)
- [Astral alignment](https://github.com/tvproductions/gz-skills-first-starter/blob/v0.6.0/docs/engineering/astral-alignment.md)
- [A01–A18 acceptance](https://github.com/tvproductions/gz-skills-first-starter/blob/v0.6.0/docs/engineering/astral-acceptance.md)
- [Python engineering](https://github.com/tvproductions/gz-skills-first-starter/blob/v0.6.0/docs/engineering/python.md)
- [Baseline and lanes](https://github.com/tvproductions/gz-skills-first-starter/blob/v0.6.0/docs/baseline-policy.md)
- [Canonical updates](https://github.com/tvproductions/gz-skills-first-starter/blob/v0.6.0/docs/updating.md)
- [Official uv locking/syncing](https://docs.astral.sh/uv/concepts/projects/sync/)
- [Official Ruff selection](https://docs.astral.sh/ruff/linter/#rule-selection)
- [Official ty configuration](https://docs.astral.sh/ty/configuration/)

Self-review: obsolete sources and split-completion claims are removed.
Mandatory engineering reconciliation, explicit heavy selection, actual
acceptance evidence and FDAU constraints are explicit. Approved design authority
does not establish implementation, acceptance or whole-heavy-stack readiness.
