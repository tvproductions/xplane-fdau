# Project Handoff

## Resume point — 2026-09-20

**Current objective:** The local quality-control cadence correction follows
the 2026-09-20 design and plan. T2.2 remains verified, and the next roadmap
action is `write_plan B1.1` after this tooling correction is closed.

**Exact next action on return:** Read AGENTS.md and the linked authorities,
then run the backlog audit and next commands. Follow the stable-closeout
quality workflow described below before routine B1.1 implementation.

## Observed state and evidence

- T2.2 was integrated into `main` at commit `431c195`. Its verified backlog
  state and evidence remain unchanged by the local quality-cadence correction.
- The approved plan is
  `docs/superpowers/plans/2026-09-19-t2-2-dependency-toolchain-refresh.md`.
  Completion, review, and four gate records are under
  `.superpowers/sdd/2026-09-19-t2-2-dependency-toolchain-refresh/`.
- The adapter pins uv 0.12.17, inventories 98 registry packages, and records
  five constrained package versions with their upstream owners. It reported no
  yanks, advisories, or blockers. Runtime remains pure Python and
  standard-library-only.
- One wheel/sdist pair passed exact inventory checks. CPython 3.12, 3.13,
  and 3.14 each passed 511 source `unittest` tests and an installed-wheel
  smoke test. The final active-Python quality gate passed 516 tests and 43.9%
  coverage against a 40% minimum. Review accepted the implementation with no
  remaining Critical or Important findings. A minor matrix subprocess-timeout
  concern is recorded in `review.md`.
- The installed and enabled `gz-skills@gz-skills` plugin was verified in this
  session at version 0.3.2 from the pinned official Git marketplace. T2.2's
  Python/uv adapter does not mutate the plugin cache.

## Quality-control follow-up

Jeff narrowed the fix to the local development cadence; GitHub Actions
remains unchanged. During edits, run focused `unittest`, Ruff, and ty checks.
Pre-commit runs staged-file Ruff lint/format and detect-secrets checks without
a full test suite or metrics reports. At stable closeout, run the complete
active-version quality gate once. Edits to existing source files use the
standalone gate. Full offline hygiene is for package layout, shipped resources,
metadata, lockfiles, build rules, or artifact-validation changes; it invokes
the quality gate directly once, then checks docs, hooks, and a fresh artifact
pair. Documentation and governance edits use their focused checks. Reserve
the local Python 3.12–3.14 source/installed-wheel matrix for
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
