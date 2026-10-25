# Strict Heavy Starter Onboarding Implementation Plan

- **Governance:** active
- **Status:** in_progress
- **Date:** 2026-10-25
- **Roadmap child:** `T2.1`
- **Source specification:** `docs/superpowers/specs/2026-10-11-skills-first-native-adoption-design.md`
- **Approval:** 2026-10-25 — Jeff / tvproductions
- **Completion evidence:** —

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax.

**Goal:** Onboard FDAU to the released starter's heavy lane with strict applicable Astral acceptance and Backplane explicitly deferred.

**Architecture:** Reconcile existing project tooling and native configuration against one immutable released starter. Keep four routine checks separate from explicit deeper acceptance; record observed evidence in FDAU's existing review authority. No runtime feature or parallel delivery lifecycle is introduced.

**Tech Stack:** Python 3.12, uv/uv_build, Ruff, ty, unittest, pre-commit, starter native plugins and required on-demand analyzers.

**Spec:** `docs/superpowers/specs/2026-10-11-skills-first-native-adoption-design.md`

**Scope:** Crosscutting T2.1/T2.2 maintenance; the metadata anchor is T2.1. This plan does not replace its completed delivery plan, reopen verified gates or select a product child. Product next remains C1.4.

## Global Constraints

- Heavy was explicitly selected by Jeff on 2026-10-25; Backplane remains disabled.
- Runtime remains standard-library-only, with `requires-python = ">=3.12,<3.13"`.
- Exact Python/tool pins are selected using dated official release and compatibility evidence; no invented freshness claims or silent family changes.
- Adopt released starter v0.6.0 / `c0a6945b2170e1cf5bee3e80738916f5b62d13a5`; recheck release status before execution and review a changed target before using it.
- Preserve the shared catalog and its component pins: SP v7.0.0, gz-skills v0.8.0, Backplane disabled. Inventory newer upstream releases without silently substituting them.
- Four routine checks: Ruff check, Ruff format --check, ty, unittest. Ruff families: E4/E7/E9/F/I/UP/B/SIM/RUF.
- Explicit deeper acceptance: C901 20, Lizard function/module/project ceilings 20/10/5; coverage and Interrogate floors remain 40%. Cognitive analysis is an OPEN dependency on the shared library extraction from gzkit, not an accepted complexipy measurement.
- Every applicable A01–A18 row needs actual passing evidence. Required FAIL/UNKNOWN/stale results or conditional exceptions cannot satisfy STRICT completion.
- Python 3.12 is a documented baseline lane, and deferred Backplane is baseline-defined; neither waives Astral acceptance.
- Preserve FDAU requirements, BACKLOG/HANDOFF authority, original dependency intent, operational data, public behavior and historical evidence.
- No copied upstream SP/gz-skills trees, project-specific catalog, cache edits, lock extension or independent onboarding checker.
- Git push, local integration and releases retain their separate authorization gates. A draft plan does not authorize execution.

## Open dependency: cognitive analyzer

Jeff clarified during plan review that the original cognitive library was a
bust and the replacement must first be extracted from gzkit. That work has not
occurred and is outside FDAU onboarding scope. Do not install complexipy as a
substitute, copy gzkit code, invent a package/API, or build a project-specific
analyzer. Jeff/upstream maintainers own extraction and the shared starter contract.

Continue independent tasks. Record cognitive measurement and affected A18 proof
UNKNOWN with this external dependency; strict overall acceptance remains open.
Revisit when the shared library and reviewed starter integration are available.
Use that uniform integration, verifying counting/threshold semantics, exact
release, Python 3.12 compatibility and actual results. The old ceiling of 15
does not establish equivalence for an unselected replacement.

## Review Focus

1. A future dependency refresh must preserve exact pins, locked execution, build family and immutable Action inputs; test real candidate edits rather than current version strings.
2. A command returning no analyzer results must fail closed; missing definitions, errors and unperformed checks cannot become PASS.
3. Full unittest must run once through the routine/hook/hygiene composition, including zero staged Python files when validating all files.
4. Shared plugins, user defaults, source junction targets and dirty project work must survive activation/rollback; native observation is required.
5. Installed artifacts must reject governance leakage and source-path fallback while retaining typed APIs and native CLI behavior.

## Task 1: Preserve the baseline and bind the acceptance record

**Files:** Create `docs/reviews/2026-10-25-strict-heavy-starter-adoption.md`; later completion updates this plan. Ignored scratch lives under `.superpowers/sdd/2026-10-25-strict-heavy-starter-onboarding/`.

**Interfaces:** Consumes approved spec and current repository/native state. Produces the A01–A18 record, exact source/environment selections, source-to-target ownership map, legacy measurements and rollback references used by all tasks.

- [x] **Step 1: Verify authority and isolation.** Read session-entry authorities and this spec/plan. Run backlog audit then next and stop on findings. Record branch, HEAD, worktrees, tracked/index/dirty state and the full pre-existing specification diff. Use the governing worktree workflow after plan approval; do not discard or accidentally omit the approved uncommitted spec/plan when preparing the isolated branch.
- [x] **Step 2: Obtain the exact released starter separately.** Use a task-specific temporary checkout, resolve its v0.6.0 tag to the full reviewed SHA, check cleanliness and GitHub release status. Read bundle, both catalogs, update skill, adoption/update runbooks, baseline policy, engineering/alignment/acceptance and C/C/C counting contract. Validate using the starter's own pinned environment; do not install its Python 3.14 tools into FDAU.
- [x] **Step 3: Create all 18 individual evidence rows.** Start unperformed rows UNKNOWN, with requirement, applicability, command/scope, observed result, evidence, owner and remaining work. Record heavy selection separately from settings, configuration, Python acceptance, analysis, discovery, CI and deferred Backplane. No PASS is inferred from this plan.
- [x] **Step 4: Inventory actual tools/configuration.** Run native plugin/marketplace JSON listings, inspect source identities and the Superpowers junction target, and record relevant nonsecret uv/Ruff/ty configuration precedence. Record current interpreter/implementation/architecture/base executable, uv and executable origins. Avoid whole user-config/environment dumps.
- [x] **Step 5: Select exact execution versions.** Verify latest stable host-compatible Python 3.12 patch and releases in reviewed uv/uv_build/Ruff/ty/pre-commit/analyzer families from official sources. Record exact selected versions, checked dates, sources and compatibility proof. Do not upgrade unrelated dependencies. Preserve the required ty beta-family disclosure while checking its current release status.
- [x] **Step 6: Capture a meaningful before baseline.** Run existing focused public-contract tests and the existing Xenon C/B/A measurements; collect Ruff C901 and Lizard findings using isolated tool environments as diagnostic evidence only. Record cognitive analysis UNKNOWN with its external extraction dependency, not a fabricated score. Record original file/function identities, hashes, counting differences and measured scope. Diagnostic overlays are not final acceptance. Preserve any failure; never regenerate a success baseline.
- [x] **Step 7: Record ownership and scope.** Map each change below to its acceptance rows and affected files. Explicitly classify workspace/private index/native/host/deployment/export triggers. The core is a single pure-Python distribution; independently verify which A14–A17 triggers are absent.
- [x] **Step 8: Commit boundary.** After focused governance checks, commit the approved design, reviewed plan and initial evidence as `docs: bind strict heavy starter onboarding`. Keep evidence UNKNOWN where work remains. No push.

## Task 2: Reconcile exact environments, strict lint/type configuration and refresh preservation

**Files:** Modify `pyproject.toml`, `.python-version`, `uv.lock`, `tools/dependency_refresh.py`, `tools/dependency_matrix.py`, `tests/test_dependency_refresh.py`, `tests/test_dependency_matrix.py`, `tests/test_project_metadata.py`; source/test/tool/adapter files requiring behavior-preserving Ruff changes are explicitly recorded in the Task 1 mapping.

**Interfaces:** Preserve the signatures and mutation guards of `collect_status(root, runner, opener)`, `apply_status(...)`, `_prepare_edits(root, report)` and `_workflow_edit(source, allowed_current)`. Change their policy behavior so updates preserve exact uv/backend/Python selection and change workflow pins coherently, rather than deleting them.

- [x] **Step 1: Write failing consuming-behavior tests.** In dependency-refresh fixtures, give a project exact uv/backend pins and setup-uv version inputs with unrelated comments. Apply a reviewed candidate and assert new exact declarations and every intended CI version agree; unrelated bytes remain. A stale digest, mismatched workflow pin or changed dirty path must refuse before writes. Add a named-index/source fixture demonstrating status commands honor reviewed project configuration instead of blanket `--no-config`. For metadata, validate actual execution/targets against a fixture pin, accepting a legitimate later 3.12 patch and rejecting 3.13 or inconsistent Ruff/ty targets. Do not hard-code today's version into permanent tests.
- [x] **Step 2: Prove RED.** Run `uv run --locked python -m unittest tests.test_dependency_refresh tests.test_dependency_matrix tests.test_project_metadata -q`; expect specific assertion failures from current pin-removal/minor-only behavior. Use the current environment directly if its old uv invocation cannot run; record that diagnostic limitation.
- [x] **Step 3: Implement environment declarations.** Set exact selected Python patch; `[tool.uv]` exact required uv and managed-Python preference; exact selected uv_build; Ruff `target-version = "py312"`, reviewed family selection and C901 ceiling 20. Keep line length 160 unless a reviewed requirement changes it. Set ty Python 3.12, error severity and explicit source/test/tool/project-adapter scopes. Reconcile current Ruff exclusion of `.codex` so repository-owned scripts are covered while external caches/checkouts stay excluded.
- [x] **Step 4: Reconcile groups through uv.** Routine tools belong in `dev`; required deeper tools belong in `hygiene`; preserve docs/artifact tools and dependencies with their actual purpose. Include cosmic-ray, Lizard, cohesion, Interrogate, Vulture, Bandit, Coverage, deptry, pip-audit, Import Linter and retained detect-secrets. Leave the cognitive dependency unresolved until its shared replacement contract exists; do not add complexipy or a placeholder package. Select exact verified releases from Task 1, regenerate via uv and inspect every lock change. Retire Xenon/Wily/Radon only after Task 1 comparison and replacement verification; keep them temporarily if still needed for comparison.
- [x] **Step 5: Implement refresh preservation.** Replace assumptions that turn exact uv pins into floors and strip setup-uv versions. Respect project configuration for status/lock/source inquiry. Update guarded refresh verification to select the correct groups/runtime and new routine/acceptance commands without mutating native plugin caches. Inventory starter/component provenance alongside native observations; native updates remain native-owned. Preserve review-scope/digest guards.
- [x] **Step 6: Fix strict Ruff findings.** Run the actual selected rules over runtime/tests/tools/project-owned adapter scripts; apply reviewed safe fixes and inspect changes. Behavior changes need a failing unittest first. No ALL, blanket ignores, new runtime packages or excluded problem files. Record Python 3.12 idiom/stdlib decisions at changed seams.
- [x] **Step 7: Prove GREEN and exact provenance.** Focused tests above, Ruff check/format and ty on affected scopes must pass. Run lock check, exact reviewed group sync, managed interpreter/version and executable-origin checks, Ruff representative `--show-settings`/`--show-files` and ty verbose diagnostics. Update A04–A08/A10/A18 with actual evidence.
- [x] **Step 8: Commit.** `build: enforce exact Astral environment policy`; review lock and source diff before staging.

## Task 3: Make the routine gate identical across local commands, hooks and CI

**Files:** Modify `tools/quality.py`, `.pre-commit-config.yaml`, `.github/workflows/ci.yml`, `.github/workflows/release-readiness.yml`, `.codex/skills/hygiene/scripts/hygiene.py`, `tests/test_quality_tool.py`, `tests/test_hygiene_tool.py`, `tests/test_release_workflows.py`, `tests/test_project_skills.py`.

**Interfaces:** Retain `Step`, `run_steps(steps, runner)` and existing quality CLI entry. `check` becomes the four-check routine aggregate; `pre-commit` executes those same checks through installed hook configuration. Hygiene uses the all-files hook run as its single routine execution and does not repeat `check`.

- [x] **Step 1: Write assertion-level RED tests.** Use injected runners to demonstrate order and failure propagation in the actual routine executor. Assert four invocations in order, exactly one unittest discovery and no deeper analyzer. Test a nonzero lint/type/test exit stops later routine work. Load actual hook YAML with pre-commit and assert ty/unittest use `pass_filenames: false`, `always_run: true`, locked commands and whole reviewed scopes; Ruff handles Python files. Do not preserve prose/snapshot assertions about the old cadence.
- [x] **Step 2: Test composition and workflow semantics.** Hygiene fake-runner tests must count one full unittest through all-files hooks, no second direct routine gate, and no build after a hook failure. Parse workflow YAML for shared exact Python/uv inputs, immutable Action SHAs, only routine quality commands, preserved artifact dependencies and no publishing permissions/triggers. Replace the test requiring version overrides to be absent with a fixture test that mismatched exact inputs fail. Test legitimate reviewed patch changes.
- [x] **Step 3: Prove RED.** Run the four affected tooling test modules and `tests.test_project_skills`; failures must concern the changed routine contract, not missing files.
- [x] **Step 4: Implement.** Use `uv run --locked` for routine steps. Configure the four hooks and remove detect-secrets from routine hooks. Replace CI's duplicate compatibility test job with the single reviewed routine aggregate; retain artifact/installed-wheel verification. Pin each Action at its independently verified immutable commit and setup-uv's version to the Task 1 selection. Read exact Python from the project pin; remove minor-only CLI overrides. Release-readiness stays manual/nonpublishing; deeper release acceptance is explicit outside routine CI.
- [x] **Step 5: Preserve offline hygiene.** Lock check precedes frozen/offline child commands. Strict docs, backlog and artifact checks remain. All-files hooks supply one routine execution; propagate offline/locked intent to nested tools without a second suite. Tests verify failure preserves the exact artifact directory and cleanup guards remain unchanged.
- [x] **Step 6: Prove GREEN.** Run affected unittest, Ruff and ty. Install hooks in the isolated repository and observe one all-files run; capture actual timing and command count for A09. Remote exact-commit CI stays UNKNOWN until observed, regardless of local YAML checks.
- [x] **Step 7: Commit.** `build: align routine Astral hooks and CI`.

## Task 4: Implement explicit deeper analysis with fail-closed measurements

**Files:** Modify `tools/quality.py`, `pyproject.toml`, `tests/test_quality_tool.py`; create cohesive support module `tools/quality_analysis.py` and `tests/test_quality_analysis.py`. Store bounded Cosmic Ray settings in `pyproject.toml`; document commands in Task 6.

**Interfaces:** Add quality commands `analysis` (offline-capable selected static/deep checks), `vulnerabilities` (explicit network audit) and `mutation` (isolated selected scope). Existing focused security/docs/coverage commands remain available. In support module:
`measure_lizard(root: Path, paths: Sequence[str]) -> dict[str, object]`;
`evaluate_lizard(report: Mapping[str, object]) -> int`;
`run_analysis(steps: Sequence[Step], runner: Runner) -> int`.
`Runner` means `Callable[..., subprocess.CompletedProcess[str]]`. Keep `Step`
owned by `tools/quality.py`; support code accepts its structural command/name
attributes through a small Protocol, avoiding an import back to the CLI.
The analysis CLI accepts `--output PATH` for its JSON report and returns 0 only
on clean complete measurement, 1 for findings, and 2 for execution/report errors.
The existing routine fail-fast runner retains its prior return-code behavior.

- [x] **Step 1: Write failing real-measurement fixtures.** Feed original invented source through Lizard, compare AST function discoveries and measure functions/async/methods/nested functions once each. Exclude class-body/lambda/module code from function means. Assert 20 passes and 21 fails for a function; module means 10 versus greater than 10; overall means 5 versus greater than 5; no rounding before comparison. Assert missing/discovered-location mismatch, unsupported inline suite, invalid syntax, symlink/escaping/missing scope and no Python files return error rather than PASS. A valid no-function module reports null, no synthetic zeros.
- [x] **Step 2: Test complete failure reporting.** For injected analysis commands returning success, violation, missing executable and invalid report, assert every available independent dimension still runs and aggregate remains nonzero. Assert an explicitly unavailable required cognitive dimension reports UNKNOWN with its prerequisite, preserves absent scores and prevents overall PASS/exit 0. Missing class scores cannot become zero. Do not assert unverified replacement counting or invent a cognitive executable.
- [x] **Step 3: Test export/import boundaries.** Test exact uv export selection, hashes, `--no-deps --disable-pip` auditor invocation, failure propagation and temporary export cleanup without exposing secrets. Define Import Linter forbidden contracts: `xplane_fdau.contracts` cannot import formats/sinks/CLI; formats cannot import sinks/CLI; sinks cannot import CLI. Prove positive actual package graph and synthetic direct/indirect forbidden edges using the real selected analyzer. Existing AST/runtime import checks still enforce standard-library-only boundaries.
- [x] **Step 4: Prove RED then implement minimal composition.** Extend existing tooling, not a new lifecycle/acceptance certifier. Follow starter lizard-functions-v1 semantics with FDAU's stricter 20/10/5 ceilings; retain original hashes/identities/errors. Run available offline dimensions even after failures; record the cognitive prerequisite UNKNOWN without a fake command, ignored result or local analyzer. CLI exits nonzero on any failure/error/required unknown. Network audit remains separate from offline hygiene.
- [ ] **Step 5: Configure mutation.** Select `contracts.values`, canonical JSON and identity/reference validation public seams for bounded Cosmic Ray work. Use unittest command, finite per-mutant timeout and a disposable checkout; ensure original suite is green before mutation. Verify one realistic deliberately altered behavior is killed. Review all survivors in selected scope; unresolved consequential survivors block acceptance, without an invented universal percentage.
- [x] **Step 6: Verify available analysis.** Run focused analysis/quality unittest, strict Ruff/ty, and actual available analyzer fixture probes on Python 3.12. Run available project dimensions over declared runtime/test/tool/adapter scopes; security/dead-code/import tools use their semantically applicable scopes, recorded per tool. Update A18 with actual versions/scores/errors/findings and the open cognitive dependency. The tests may pass while overall acceptance remains nonzero/incomplete. Do not call configured commands executed analysis.
- [ ] **Step 7: Remediate required findings.** For each actual finding, record exact file/function, requirement and observable negative control before its correction. Apply minimal behavior-preserving fixes and focused tests. Broad semantic changes require their owning design before implementation; keep this task open until required findings pass. No snapshot/threshold/ignore workaround. Rerun affected dimensions after each correction and all dimensions on the final candidate.
- [ ] **Step 8: Commit.** `build: verify required deep engineering analysis`, splitting independently reviewed remediation commits by affected behavior.
- [ ] **Deferred cognitive integration:** After the external extraction and shared starter adoption contract exist, review that contract and add its exact supported dependency/invocation. Prove real counting/boundary/invalid-input behavior on Python 3.12, run FDAU analysis and resolve required findings. Keep this item unchecked and strict acceptance open until those conditions are observed.

## Task 5: Reconcile native starter sources and preserve packaging boundaries

**Files:** Modify `.codex/config.toml`, `pyproject.toml`, `tools/release.py`, `tests/test_release_tool.py`, `tests/test_project_skills.py`, `tests/test_installed_smoke.py`; generate `.skills-first/bundle.lock.json`, `AGENTS.skills-first.md`, `.agents/skills/update-gz-template/SKILL.md`, `.gz-skills/settings.json`. The ignored old junction/checkout are local rollback state.

**Interfaces:** Use the released starter's configure/backport/status helper and native manager. No new project source validator. Existing `release.check_dist(directory)` rejects leaked governance; `tools/installed_smoke.py` remains the external smoke entry.

- [x] **Step 1: Prepare the candidate and negatives.** From the clean released starter, run read-only backport and configure preview. If the current junction/config conflicts, generate candidates in a separate empty disposable directory; inspect rather than force-overwrite FDAU. Exercise actual upstream helper refusal against conflicting/symlinked managed outputs and verify original fixture bytes survive. Compare legitimate same-version/no-op and reviewed target changes without hard-coded filename inventories.
- [x] **Step 2: Write packaging RED controls.** Extend the existing realistic wheel/sdist fixtures with the starter lock, generated instructions, profile settings and update skill. Each injected governance family must cause `release.check_dist` to raise; the clean pair remains accepted. Installed-smoke regression must reject checkout fallback and missing/incorrect typing/resource/public-value behavior, preserving existing CLI and canonical tests.
- [x] **Step 3: Prove RED then implement exclusions.** Add explicit source exclusions for `.agents/**`, `.skills-first/**`, `.gz-skills/**`, generated instruction fragment and other new governance surfaces as needed by actual sdist inventory. Extend forbidden-member validation; do not whitelist governance to make exact inventories pass.
- [x] **Step 4: Apply reviewed native configuration.** Reconcile only scoped source/activation tables and managed candidates through the supported helper method. Keep the one shared catalog and exact selected revisions. Explicitly disable FDAU's old gz-skills source; preserve shared installed 0.8.3 and unrelated user defaults. Verify the junction's resolved path before a nonrecursive link-only detach; keep its target checkout untouched for rollback.
- [x] **Step 5: Install through native manager.** Verify project trust/loading and marketplace inventory, then use supported `codex plugin add superpowers@skills-first-starter` and `codex plugin add gz-skills@skills-first-starter` operations. Inspect user-level deltas; a host that cannot preserve intended project scope blocks activation. No cache edits/global enablement workaround.
- [x] **Step 6: Record explicit heavy settings.** Through selected pinned setup helper, inspect project, initialize if absent, then select heavy. Verify settings contain only schema_version/profile with profile heavy; Backplane remains disabled and no FDAU requirements migrate.
- [x] **Step 7: Prove packaging GREEN and native distinctions.** Run release/project-skills/installed-smoke fixtures plus actual preview/status. Record configured/install/discovery separately. Fresh-session observation verifies exact source commits/bytes and actual entry skills/update skill invocation; until then discovery is UNKNOWN. Check outside-project control retains its previous defaults.
- [ ] **Step 8: Commit.** `build: adopt released starter native sources`; preserve rollback references and do not claim completed onboarding.

## Task 6: Bind project guidance and permanent maintenance to the strict contract

**Files:** Modify `AGENTS.md`, `BACKLOG.md` current prose only, `HANDOFF.md` current summary only, `.codex/skills/code-quality/SKILL.md`, `.codex/skills/hygiene/SKILL.md`, `.codex/skills/documentation/SKILL.md`, `.codex/skills/release/SKILL.md`, `docs/architecture/gz_skills_plugin_only_specification.md`, `mkdocs.yml`; create `docs/agents/skills-first.md` and `docs/engineering/python.md`.

**Interfaces:** Documentation points to actual native sources and tested commands; dated immutable starter source is policy provenance. Existing backlog parser, project tools and upstream template update skill consume those declarations.

- [x] **Step 1: Reconcile instructions.** Replace old plugin ID/tag and checkout authority with selected native sources/AGENTS fragment. Preserve all domain, unittest, requirements, review and release boundaries. Record heavy lane and deferred Backplane separately. Document exact routine/deep commands, scope, Python 3.12 policy and version-aware idiom decisions. Update old local-workflow authority with a dated supersession pointer, without rewriting its historical result.
- [x] **Step 2: Define permanent maintenance/release obligations.** Template update uses selected `update-gz-template`; dependency tools use canonical maintenance. Inventory starter/SP/Backplane/gz-skills independently. Record dated adoption/scoped/quarterly-on-demand reviews and exact affected-input release evidence. No automatic schedule. Product SemVer and a newly written PRD for each major including 1.0.0 become explicit; G1 remains waiting.
- [x] **Step 3: Correct current summaries.** BACKLOG/HANDOFF current prose reflects verified C1.3, mandatory maintenance in progress and product next C1.4. Leave managed delivery states, completed gate evidence and dated historical checkpoints intact. Do not mark C1.4 selected or onboarding complete.
- [x] **Step 4: Remove affected weak guidance tests.** Replace phrase/inventory snapshots with consuming configuration/CLI/fixture checks already specified in Tasks 2–5. Do not add tests requiring current draft/approval/version state or text-presence claims. Retain durable policy negative controls. Broader weak-test audit remains separately open.
- [x] **Step 5: Verify.** Focused governance/documentation/public API/project-skills tests, strict backlog audit and MkDocs build, documentation analysis and whitespace check. Use reviewer assessment of clarity/accuracy rather than keyword-presence tests.
- [ ] **Step 6: Commit.** `docs: bind strict starter engineering authority`.

## Task 7: Execute strict acceptance, review and integration gates

**Files:** Update `docs/reviews/2026-10-25-strict-heavy-starter-adoption.md`, this plan's checks/completion evidence and the source spec's implementation note only after actual proof.

**Interfaces:** Consumes the unchanged final candidate, all 18 acceptance rows and exact installed/native/CI observations. Produces an honest strict result and a separately gated integration choice.

- [x] **Step 1: Review the complete branch.** Use the required independent whole-branch review against the approved spec, all A01–A18 and review-focus controls. Resolve load-bearing findings through reproducing tests; rerun affected checks. Record reviewer source/HEAD and disposition.
- [x] **Step 2: Run one stable-candidate offline hygiene.** Use the reconciled project command: lock, backlog, strict docs, installed all-files hooks (one routine suite), retained safe artifact pair and inventory validation. Run required offline deep analysis explicitly once on this candidate, including statement/branch coverage through unittest. This separate coverage measurement is acceptance work, not a second routine gate. Capture duration and exact HEAD/dirty diff.
- [ ] **Step 3: Run network and mutation acceptance.** Execute exact-lock dependency audit with hashes/no second resolver; record scope/advisory results. Run the bounded isolated Cosmic Ray session after its unmodified baseline. Investigate unresolved security findings or meaningful survivors; strict acceptance stays open until resolved.
- [x] **Step 4: Verify fresh external delivery.** Preserve the fresh artifact pair/digests and test built wheel outside checkout on the exact selected Python 3.12 patch with runtime dependencies only. Validate CLI/resources/public typed APIs and import origin. Verify a wheel rebuilt from the sdist as part of the default no-sources build path; record isolated backend inputs.
- [x] **Step 5: Observe native acceptance in a fresh session.** Verify scoped SP/gz-skills owning sources and update skill invocation; retain outside-project control and rollback results. No file scan or old-session skill list substitutes for the new session.
- [ ] **Step 6: Obtain remote evidence when separately authorized.** Ordinary Git sync may be needed for exact-commit CI. Do not push from onboarding authority alone. Record A09 UNKNOWN until the candidate's routine/artifact jobs actually pass. Any changed input invalidates affected prior proof.
- [x] **Step 7: Decide strict status from evidence.** All applicable required rows and deeper results must pass; N/A requires absent triggers. While the cognitive extraction/integration prerequisite is open, overall strict acceptance remains incomplete even if all other work passes. Conditional exceptions cannot satisfy STRICT completion. Report heavy intent and deferred Backplane whole-stack readiness separately even when Astral acceptance passes. Do not falsely certify the whole heavy stack.
- [ ] **Step 8: Finish only after acceptance.** Use the normal finishing choice. After the user selects local integration, follow exact fast-forward verification, retain worktree until main passes, then remove temporary branch/worktree. No tag/publication/release or implied remote sync.
- [ ] **Step 9: Final evidence commit.** Record completion and independent review only when achieved; leave pending tasks and unknown observations open otherwise. Archive the crosscutting execution record using existing governance conventions after completion, preserving the prior T2.1/T2.2 delivery evidence.

## Plan audit and execution handoff

Using `gzs-plan-audit`, compare Jeff's October 25 instruction with the approved
spec and this plan. Citations below refer to the spec unless prefixed Plan;
the complete spec path is in the header.

| Intent-to-scope | Result | Evidence |
| --- | --- | --- |
| Mandatory strict Astral onboarding | Aligned | Spec:11, Spec:99, Spec:294; no partial completion claim |
| Explicit heavy, Backplane not ready | Aligned | Spec:85; independent readiness dimensions |
| Existing FDAU requirements and no gzkit | Aligned | Spec:11, Spec:85; crosscutting maintenance |
| Native source/provenance migration | Aligned | Spec:245; scoped sources and rollback |
| No unknown/failing evidence accepted as compliance | Aligned | Spec:294; strict closure rule |
| Cognitive replacement pending external extraction | Aligned with open dependency | Spec:181; Plan:38; no local substitute or false PASS |

| Scope-to-plan | Result | Executable ownership |
| --- | --- | --- |
| Exact environment, tool freshness, effective configuration | Aligned | Tasks 1–2 (Plan:61, Plan:76); A04–A08/A10 |
| Four routine checks, hooks/CI, no duplicate routine suite | Aligned | Task 3 (Plan:91); A08–A09 |
| Available deeper analysis and explicit cognitive prerequisite | Aligned with open dependency | Task 4 (Plan:105); A18 cannot pass yet |
| Shared native sources, explicit settings, safe rollback | Aligned | Task 5; A01/A18 and native discovery |
| Installed src/backend/artifact/typing proof | Aligned | Tasks 2/5/7; A02–A03/A11–A13 |
| Applicability of workspace/source/host/export variants | Aligned | Tasks 1/4/7; A14–A17 individually |
| Persistent policy and release discipline | Aligned | Task 6; source-owned update and major PRDs |
| Actual final acceptance and independent review | Aligned | Task 7; all A01–A18 and external observations |

Open dependency: cognitive analysis cannot be implemented or accepted until the
gzkit extraction and shared starter integration contract exist. Jeff explicitly
directed leaving this gap open while independent work proceeds. No FDAU-local
replacement or acceptance waiver is planned.
Verdict: intent/scope/plan alignment includes this explicit unresolved prerequisite;
strict implementation acceptance remains blocked on cognitive proof.
Actual compatibility, measurements and external CI/discovery are execution inputs
and remain unproven until their tasks run. The plan was subsequently approved as recorded below.

Jeff approved this plan on October 25 after review, including the explicit
cognitive-library dependency. Execute natively with one independent whole-branch
review because environment, gate and native-source tasks share configuration
and evidence. The cognitive integration and strict-acceptance items remain open
until their external prerequisites and verification are satisfied.
