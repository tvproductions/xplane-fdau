# Project Handoff

## Resume point — 2026-09-20, 11:15 CDT

**Current objective:** Continue xplane-fdau from its governed backlog, with the
`gz-skills` plugin refreshed to 0.3.2 and the backlog-method research available
for later consideration in gzkit and airlineops.

**Exact local step:** The backlog audit has no findings, no child is selected,
and `next` recommends `write_plan T2.2`. The T2.2 plan at
`docs/superpowers/plans/2026-09-19-t2-2-dependency-toolchain-refresh.md`
is still a draft and lacks implementation authority. It needs executable
test/code fixtures and plugin-inventory steps before plan audit and human
review.

**First permissible action:** Read `AGENTS.md` and the current authorities;
run the backlog `audit` and `next` commands; inspect the T2.2 draft and
its approved specification; then improve the single-child plan. The expected
result is a reviewable plan whose commands, fixtures, and verification cover
the project-managed plugin pin as well as Python/uv. Stop before approval,
backlog selection, or implementation unless the plan review and project
workflow authorize those transitions.

## Observed repository state

- At handoff authoring, local `main` and fetched `origin/main` both pointed
  to `6fba05f5458228e33972bdd8f2b550689cbf6701` (ahead 0, behind 0).
  One worktree existed, on `main`. This handoff precedes its own requested
  Git-sync commit; verify live Git state when resuming.
- The local changes prepared for that sync are the plugin 0.3.2 pin and its
  agent/test references, `README.md` and `mkdocs.yml` navigation, the two
  new `docs/project/` backlog guides, and this handoff. These are local-only
  until the requested Git sync finishes and its remote alignment is checked.
- `codex plugin list --json` reported `gz-skills@gz-skills` installed and
  enabled at 0.3.2 from
  `https://github.com/tvproductions/gz-skills.git` ref `v0.3.2`.
  `codex plugin marketplace list --json` reported the Git marketplace.
  The project pin in `.codex/config.toml` now names that reviewed tag.

## Decisions and boundaries

- Jeff explicitly requested this fresh handoff and an ordinary Git sync.
  That authorizes the checkpoint commit and push, not a tag, package
  publication, GitHub release, or adoption changes in sibling repositories.
- The completed plugin-only migration remains historical authority in
  `docs/architecture/gz_skills_plugin_only_specification.md` and
  `docs/superpowers/plans/2026-09-19-gz-skills-plugin-only-adoption.md`.
  The new plugin version changes the project-managed pin; the T2.2 Python/uv
  adapter must not mutate the plugin cache.
- `ROADMAP.md` owns node identity and dependency order; `BACKLOG.md` owns
  mutable delivery state. B1.1 waits on T2.2. T3.1 is an independent
  specified peer. The canonical vertical slice and release remain gated.
  Runtime remains pure Python and standard-library-only; tests use
  `unittest`, never pytest.
- The two backlog guides document the present xplane-fdau method and a
  candidate distinction among ADR decisions, feature records, and releases.
  The gzkit and airlineops inspection was read-only; neither repository was
  changed. Their adoption, taxonomy, and migration choices are unresolved
  human decisions. No xplane-fdau backlog state or release gate changed.

## Canonical and external thresholds

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

## Verification and evidence

- On 2026-09-20, backlog `audit` and `next` both reported no findings
  and `write_plan T2.2`.
- The plugin pin and backlog documentation passed the focused public API and
  documentation `unittest` suite (15 tests), strict MkDocs build, and the
  complete `uv run python tools/quality.py check` gate before this handoff
  edit. The Git-sync workflow must verify the final handoff-containing tree
  before committing.
- The short guide is `docs/project/backlog-method.md`; the researched
  retrospective is `docs/project/backlog-governance-model.md`. The latter
  records sources, actual gzkit and airlineops examples, the ADR/feature/release
  distinction, minimum schemas, and a migration pilot.
- The active T2.2 specification is
  `docs/superpowers/specs/2026-08-15-xplane-fdau-local-workflow-skills-design.md`.
  Its draft plan is the exact next local planning artifact.

## Follow-on actions

1. After the requested sync, confirm `main` equals `origin/main`, with no
   unintended staged or unstaged changes. On a later session, re-run backlog
   `audit` and `next`; this handoff is a dated snapshot.
2. Make the T2.2 draft executable and reviewable, then run
   `gzs-plan-audit` and seek the plan approval required by the project
   workflow before selecting or implementing T2.2.
3. If Jeff chooses to pursue gzkit or airlineops adoption, start with the
   retrospective's bounded crosswalk and slip/supersession pilot. Preserve
   historical ADR, OBPI, REQ, receipt, and tag identities.

Suggested skills: plugin `gzs-session-handoff` to resume,
project `backlog-status` for live state, and `gzs-plan-audit` plus
Superpowers writing-plans for T2.2.
