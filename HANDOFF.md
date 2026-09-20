# Project Handoff

## Session checkpoint — 2026-09-20

### Current state and last completed action

The approved plugin-only `gz-skills` migration is complete on local `main`.
Its specification, implementation, and historical plan are commits `d5b1630`,
`bd3656e`, and `112b6f5`. At handoff authoring, `main` was clean at
`112b6f5`, no feature worktree or branch remained, and a fresh fetch showed
`origin/main` 0 commits ahead and local `main` 3 ahead. Jeff explicitly
requested this handoff and an ordinary Git sync; verify the resulting remote
state from live Git because this document precedes its own sync commit.

The repository now enables the `gz-skills@gz-skills` Codex plugin from the
reviewed `v0.2.0` Git marketplace tag. The copied `.agents/skills/gzs-*` trees
and `gz-skills.lock.json` are removed. Local Codex reported one installed,
enabled plugin at `0.2.0`, with tag commit
`21579a545b3bf05339a017c82290ddcea8e9beec`. A new Codex session is
needed to refresh the skill list captured before that removal.

### Important context and constraints

- `ROADMAP.md` owns capability order; `BACKLOG.md` owns delivery state.
  The latest audit had no findings, no local child was selected, and `next`
  returned `write_plan T2.2`.
- T2.2 is `specified` with a **draft** plan. Its prior plan audit failed
  execution readiness because several steps lack executable fixtures or code
  examples. The plugin pin is now included as a separately managed dependency
  surface in that draft, but the draft still needs executable plugin-inventory
  steps. It has no implementation authority.
- B1.1 waits on T2.2; T3.1 is an independent specified peer. T2.1 remains
  verified at 5/5. The canonical vertical slice and release are still gated.
- q4xpcc Phase 24A specification and plan reconciliation is eligible under
  I1.0 and remains a priority. Runtime and fixture adoption wait for C4.4;
  live XPLM acquisition adoption waits for A1.9. Do not edit q4xpcc from this
  repository.
- Use `unittest` only. Runtime remains pure Python and standard-library-only.
  No tag, package publication, or GitHub release is authorized by Git sync.

### Canonical and external gate sequence

Identity and native-FDR-kernel migration: implemented and verified, but unreleased. Completed implementation plan:
`docs/superpowers/plans/2026-08-09-xplane-fdau-identity-fdr-kernel-migration.md`.
The next canonical vertical slice retains measurement, binding, observation, sample, frame, timing, and quality contracts. ARINC and FDM/FOQA support remain
inside the repository's approved scope.

`D1.1` canonical C1-C4 design approval is verified. `D1.2` acquisition,
recording, projection, and pinning contract design is verified. `D1.3`
reviewed q4xpcc Phase 24A consumer handoff is verified. `I1.0` is eligible as
the next reportable external action.

`I1.0` now permits Phase 24A specification and plan reconciliation because
`D1.3` is verified. `I1.1` permits delivered contract-model, schema, fixture,
and runtime adoption only after `C4.4`. `I1.2` permits live XPLM acquisition
adoption only after `A1.9`.

### Decisions

- **Jeff approved:** plugin-only `gz-skills` delivery, with no standalone
  installation alternatives; the project pin belongs in a full
  `gzs-update-dependencies` run. xplane-fdau's current dependency case is
  Python plus the Codex plugin; other ecosystems can be added by adopting
  projects later. Jeff will handle those other projects.
- **Jeff's standing integration choice:** merge reviewed feature work locally
  into `main`, verify it, then remove its temporary worktree and branch.
- **Implementation choice:** `.codex/config.toml` pins the project plugin to
  `v0.2.0`; Codex marketplace owns its updates. The T2.2 Python/uv adapter
  must not mutate the plugin cache.
- `gzs-git-sync` and `gzs-session-handoff` remain explicit-only. This
  checkpoint authorizes an ordinary commit and push, not a release.

### Immediate next actions

1. Read `AGENTS.md`, inspect live Git/worktrees, then run the backlog
   `audit` and `next` commands. Treat this handoff as a snapshot.
2. Finish the T2.2 draft's executable test/code fixtures and plugin-inventory
   steps. Re-run `gzs-plan-audit` and review the plan with Jeff before
   approval, backlog registration, selection, or implementation.
3. Preserve q4xpcc I1.0 Phase 24A planning priority using the reviewed D1.3
   handoff. Respect the C4.4 and A1.9 adoption gates.

### Pending work and open loops

T2.2 has 0/4 gates and no implementation evidence; its draft plan is the next
local planning task. B1.1 and canonical contracts remain behind it. T3.1 is
specified but independent. Other adopting projects have not been changed here.
No release gate has advanced.

### Verification

- On 2026-09-19, the plugin migration passed the full project quality gate,
  strict MkDocs build, focused merged-tree `unittest` checks (24 tests), and
  backlog audit. Independent review found no Critical or Important issue; its
  minor duplicate-plugin test finding was corrected before the passing gate.
- On 2026-09-20, the live backlog `audit` had no findings and `next` returned
  `write_plan T2.2`; Git fetch showed no remote divergence.
- On 2026-09-20, the checkpoint full quality gate passed (468 `unittest`
  tests, 94% coverage) after the handoff's tested gate statements were restored.
  Strict MkDocs passed; the backlog audit had no findings.
- At handoff authoring, the remaining Git-sync steps were the reviewed commit,
  push, and post-push fetch/alignment check. Future T2.2 work requires its own
  plan approval and verification.

### Evidence and artifact references

- Plugin policy: `docs/architecture/gz_skills_plugin_only_specification.md`
- Project pin: `.codex/config.toml`; agent rule: `AGENTS.md`
- Completed migration record:
  `docs/superpowers/plans/2026-09-19-gz-skills-plugin-only-adoption.md`
- T2.2 draft:
  `docs/superpowers/plans/2026-09-19-t2-2-dependency-toolchain-refresh.md`
- q4xpcc D1.3 brief: `docs/architecture/q4xpcc_phase_24a_contract_handoff.md`

### Suggested skills

Use plugin `gzs-session-handoff` to resume, project `backlog-status` for
live state, and plugin `gzs-plan-audit` plus Superpowers writing-plans for
T2.2. Run repository hygiene only when the task or its approved plan calls for
it; this checkpoint needs no separate hygiene pass.
