# Canonical gz-skills Adoption Implementation Plan

- **Governance:** historical
- **Status:** completed
- **Disposition:** The 2026-09-05 user-approved canonical gz-skills installation and policy amendment completed without a roadmap-child completion, Git push, tag, publication, or release claim.

> **For agentic workers:** Use superpowers:subagent-driven-development for this single integrated task and independent review.

**Goal:** Adopt all eleven canonical gz-skills, retire local Git-sync, and reconcile project policy.

**Architecture:** Unmodified pinned .agents snapshots and a generated lock provide portable authority; existing local tools supply project commands. Git sync includes explicit-authorized pushes, while release gates remain separate.

**Tech Stack:** Upstream gz-skills installer, Markdown, Git attributes, existing Python unittest and quality tooling.

**Spec:** docs/superpowers/specs/2026-09-05-gz-skills-adoption-design.md

## Global Constraints

- Adopt upstream e925081362eec2517ab429517e250ecca6877cdc verbatim, all eleven skills, one .agents/skills installation, generated gz-skills.lock.json.
- Remove the local Git-sync skill without an alias; retained local guidance supplies only project-specific adapters.
- No actual push, tag, package publication or release. Explicit future git sync permits ordinary push and requires fresh ahead=0/behind=0 proof.
- Preserve unittest-only testing, pure-Python standard-library runtime, existing dependencies, Superpowers external discovery and all downstream delivery states.
- T1.3 remains selected; no T2/T3 completion claim. Do not modify approved D1 designs, historical evidence or provenance-locked parent architecture.

## Task 1: Install canonical suite and reconcile project adapters and policy

**Files:**
- Create: .agents/skills/gzs-*/ complete upstream trees and gz-skills.lock.json.
- Modify: .gitattributes; AGENTS.md; HANDOFF.md; ROADMAP.md; BACKLOG.md.
- Delete: .codex/skills/git-sync/SKILL.md (remove resulting empty directory only).
- Modify: .codex/skills/code-quality/SKILL.md; .codex/skills/hygiene/SKILL.md; .codex/skills/release/SKILL.md; .codex/skills/documentation/SKILL.md only if a pointer is necessary.
- Modify: docs/superpowers/specs/2026-08-15-xplane-fdau-local-workflow-skills-design.md.
- Modify: tests/test_project_skills.py; tests/test_backlog_governance.py only if an actual structured expectation changes.
- Finalize: this plan and its source specification metadata/verification notes.
- Ignored report: .superpowers/sdd/2026-09-05-gz-skills-adoption/task-1-report.md.

**Interfaces:** Source is the exact Git revision above; consumer is this repository's agent discovery, governance parser, and existing quality/packaging tools. No dependency on a sibling checkout may remain in committed instructions.

- [x] Update tests/test_project_skills.py first. Remove git-sync from expected local discovery inventory; replace obsolete no-push prose assertion with real installed-catalog/lock integrity checks. Assert lock exists before parsing (RED is a failure, not a file-not-found error). Expected eleven names are gzs-agent-context-diet, gzs-cross-platform-python, gzs-git-sync, gzs-intent-audit, gzs-plan-audit, gzs-quality-gate, gzs-repository-hygiene, gzs-router, gzs-session-handoff, gzs-tech-debt-review, gzs-update-dependencies. Check schema_version1, source repository/revision/path, exact safe relative installation paths, discovered catalog equality, and actual full-tree bytes against locked hashes. Hash sorted UTF-8 POSIX relative path + NUL + raw bytes + NUL for every durable file. No import of external gz-skills in repository tests. No new assertions on human prose.
- [x] Run .venv/Scripts/python.exe -m unittest tests.test_project_skills -q and capture expected failing installation checks before installation.
- [x] Run the upstream immutable installer:
  uvx --from git+https://github.com/tvproductions/gz-skills.git@e925081362eec2517ab429517e250ecca6877cdc gz-skills install --project <this worktree absolute path> --all
  Use require_escalated for network/uv. No --force, no manual lock writes. Upstream source already verified clean and matches remote; if remote installer is unavailable, report exact failure before choosing supported local-checkout CLI fallback.
- [x] Add .gitattributes rule .agents/skills/gzs-*/** -text to preserve full-tree hash bytes. Keep .agents/skills/superpowers ignored and untouched. Remove only old git-sync skill via apply_patch and its empty directory with native Remove-Item after validating it is empty.
- [x] Make AGENTS.md name gz-skills canonical, route all eleven skills via catalog/lock with exact discovery root, and distinguish explicit-only sync/handoff from automatic triggers. Link project quality/hygiene commands (existing tools), unittest and runtime rules. Remove push prohibition tied to vertical-slice delivery; ordinary sync follows canonical safeguards; tags/releases/package publication remain separate and gated. No permission to push from mere adoption.
- [x] Turn code-quality and hygiene SKILL.md into concise project adapters naming gzs-quality-gate and gzs-repository-hygiene and preserving current commands. Keep domain documentation/release guidance; clarify release-readiness never pushes itself and does not prohibit a separately requested gzs-git-sync.
- [x] Amend current local-workflow design with dated user-authorized canonical ownership. T2.1/T2.2/T3.1 are future deterministic project adapters, not new canonical/local workflow skills. Replace active no-push logic with explicit-authorized push and final fetch/alignment; rebase only unpublished history, no automatic merge-head rewriting required by portable skill. Keep unchanged relevant quality/artifact/dependency/T1 boundaries. Do not mark any future capability delivered.
- [x] Reconcile ROADMAP/BACKLOG T3.1 title to Guarded Git synchronization adapter and its fourth gate to explicitly authorized ordinary push with final alignment, preserving five gates and specified0/5. Reconcile T2.1's first gate to a project hygiene adapter for gzs-repository-hygiene, preserving five gates/spec status. C4.4 release gate must not prohibit routine authorized Git sync. Preserve historical D1 acceptance statements/evidence. Update HANDOFF current policy/catalog/adoption and clarify historical no-push statements are past activity, not present sync prohibition.
- [x] Run focused project-skills and governance/status tests; upstream gz-skills status --lock <worktree>/gz-skills.lock.json using same pinned tool; git diff --check.
- [x] Run full uv run python tools/quality.py check; uv run mkdocs build --strict; uv run python tools/quality.py pre-commit, with offline/frozen environment for project tools. Capture exit status/counts/warnings. Do not update project dependency versions.
- [x] Build fresh wheel/sdist into a uniquely created system-temp directory via uv build --no-sources --out-dir <exact temp>; run tools/release.py check-dist <exact temp> and explicitly inspect members for .agents/, .codex/, gz-skills.lock.json exclusion. Preserve artifacts at a reported exact path for parent inspection. Do not claim release readiness/matrix.
- [x] Mark plan/spec completed historical only after actual implementation/checks; record report commands, RED/GREEN, installer pin/hash proof, file scope, warnings, artifact path and limitations. Stage only listed paths (no ignored scratch), inspect staged whitespace/scope, commit with build: adopt canonical gz-skills workflows. Parent owns independent behavior/task/final review, local merge and worktree cleanup.
