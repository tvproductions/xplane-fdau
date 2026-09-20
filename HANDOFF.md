# Project Handoff

## Resume point — 2026-09-20

**Current objective:** T2.2 Python/uv dependency refresh has completed its
review and verification. Jeff requested this handoff and an ordinary Git sync,
then intends to revisit the costly quality-control workflow.

**Exact next action on return:** Read AGENTS.md and the linked authorities,
then run the backlog audit and next commands. T2.2 is verified with 4/4 gates,
no local child is selected, and the current next recommendation is
`write_plan B1.1`. Before routine feature work, investigate and design the
quality/hygiene cadence change described below. Seek review of a concrete
design before changing gate policy.

## Observed state and evidence

- T2.2 implementation and review are on temporary branch
  `t2-2-dependency-refresh`, based on `main`. This handoff and the final
  backlog transition are the intended closeout changes for local integration
  and the explicitly requested ordinary sync. Check live Git status and remote
  alignment; this paragraph is a dated observation, not proof of a push.
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
- Installed and enabled `gz-skills@gz-skills` is 0.4.0 from the official Git
  marketplace; project `.codex/config.toml` still pins reviewed tag 0.3.2.
  T2.2's Python/uv adapter does not mutate the plugin cache. The full
  project-managed plugin inventory remains unreconciled; do not describe T2.2
  as a complete portable plugin refresh.

## Quality-control follow-up

Jeff observed that repeated full hygiene and 3-version matrices consumed far
too much time. The current pre-commit `quality-check` hook runs
`tools/quality.py check`; hygiene invokes all pre-commit hooks and therefore
runs that full gate again. Manual quality runs add more duplication, and CI's
3.14 quality and compatibility jobs overlap.

Design a leaner edit loop using Ruff lint/format, ty, and focused `unittest`.
Run the full active-version quality gate once at stable closeout. Run hygiene
and artifact checks when their inputs change, and keep the broad 3.12–3.14
matrix in parallel CI or for version-sensitive changes and release readiness.
Make pre-commit fast, remove CI duplication, and time-bound matrix
subprocesses. Do not silently weaken the release gate. This is Jeff's next
requested topic, ahead of routine B1.1 feature work.

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
