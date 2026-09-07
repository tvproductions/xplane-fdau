# T1.6 gate 1

- **Child:** `T1.6`
- **Gate:** `1`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-09-07
- **Subject:** Project-local backlog skill triggers

Observed revision: `3a274fdd5c83954c9b5ecc8ddab6b5e588baec8d`, including
skill implementation `a4a042326ea50e39e33f58a8c8f9e309807c9264` and independently
accepted correction `ee2805f7357f901f63a0ae44e39ef83625091d8b`.

`.codex/skills/backlog-status/SKILL.md` has discoverable `name: backlog-status`
frontmatter. Its description routes status/resume, roadmap/backlog/spec/plan
adherence, next local action, and controlled selection/lifecycle/suspension/
gate changes. ROADMAP owns identity/order/dependencies; BACKLOG alone owns
mutable delivery state. Status/resume routes audit then next; a finding stops
progress. Additional status and JSON reports remain read-only.

Task 1's status/adherence/mutation behavioral evaluations demonstrated the
prior missing routing and then the corrected exact commands. Adherence RED
used an unrelated `uv run gz status --table`; GREEN used strict backlog audit.
Mutation RED suggested direct document edits; GREEN used separate guarded
selection/transition commands, inspected preview/audit, repeated each with its
printed original SHA-256 and explicit apply, and invented no prerequisites.

```powershell
uv run python -m unittest tests.test_project_skills tests.test_backlog_governance tests.test_backlog_status_cli tests.test_release_tool tests.test_installed_smoke tests.test_documentation -v
uv run python .codex/skills/backlog-status/scripts/backlog_status.py audit
uv run python .codex/skills/backlog-status/scripts/backlog_status.py status --json
uv run python .codex/skills/backlog-status/scripts/backlog_status.py next
```

The six-module implementation checkpoint passed 101 tests in 113.259s.
`ProjectSkillTests.test_project_skills_are_scoped_to_unreleased_xplane_fdau`
checks all five discoverable project adapters; CLI/governance tests exercise
current state and managed authority. Reviewed-state reports exited 0, no
findings, selected T1.6 reviewed, next verify. The reviewed transition itself
observed the exact safeguarded protocol; its original BACKLOG SHA-256 was
`ba6f5f176a05c26ae87962539ca4b84d81260824d37bf02be93336cc8c4b9f55`,
candidate `a8dafce420059a3bbca82d13e2f857743e2aea935a77580bad11a1bd194ee802`.

Mutation commands are limited to BACKLOG, not plans/specs/evidence/Git/remotes/
tags/releases/packages/other repositories. Engine behavior is unchanged.
Independent review is accepted in sibling `review.md`, including the stable
Current position authority pointer instead of duplicated volatile prose.

Final artifact identity, validated independently of skill packaging: wheel
SHA-256 `25ac6660fa3b4b1bfd5e431d0a3d7126a126012ad998509639d3f18465802afb`;
sdist `5429361eb3d1569cba926bcc0f95c72dda41caa2069bb30f2ed924f6ec52bce6`.
Exact new paths and installed matrix are in gate-4.md. Windows was directly
observed; Linux/macOS were not executed. No runtime or release authority changed.
