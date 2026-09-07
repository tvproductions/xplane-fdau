# Project Handoff

## Session entry

`ROADMAP.md` is the capability-order authority and `BACKLOG.md` is the only
mutable delivery-state authority. Do not infer current state from this file;
after reading the required architecture and governance documents, run:

```powershell
uv run python .codex/skills/backlog-status/scripts/backlog_status.py audit
uv run python .codex/skills/backlog-status/scripts/backlog_status.py next
```

Stop on a finding. Otherwise follow the exact reported local-child lifecycle
action.

## Architecture and release boundary

The parent architecture is
`docs/architecture/xplane12_virtual_fdau_ecosystem_design.md`; the approved
repository amendment is
`docs/architecture/xplane_fdau_core_scope_amendment.md`. `xplane-fdau` is the
X-Plane-specific, transport-free, standard-library-only core. XPLM,
XPPython3, `xpwebapi`, network clients, and simulator I/O remain external.
Use `unittest`, never pytest. Local ARINC and FDM/FOQA-support behavior remains
inside this boundary.

Identity and native-FDR-kernel migration: implemented and verified, but unreleased. Completed implementation plan:
`docs/superpowers/plans/2026-08-09-xplane-fdau-identity-fdr-kernel-migration.md`.
The next canonical vertical slice retains measurement, binding, observation, sample, frame, timing, and quality contracts. Version `0.1.0`, tags, package
publication, and GitHub releases remain separately gated. Ordinary Git sync
requires an explicit request and does not grant release authority. `gzs-git-sync`
and `gzs-session-handoff` are explicit-only workflows.

## Current delivery path

T1.5 is verified and integrated. T1.6 closes skill discovery, session entry,
hygiene audit integration, and artifact exclusion. The governed path remains
`T1.6 -> T2.1 -> T2.2/T3.1 -> B1.1 -> C1.1` and then through `C4.4`.

## q4xpcc readiness

`D1.1` canonical C1-C4 design approval is verified. `D1.2` acquisition,
recording, projection, and pinning contract design is verified. `D1.3`
reviewed q4xpcc Phase 24A consumer handoff is verified. `I1.0` is eligible as
the next reportable external action for planning reconciliation.

`I1.1` permits delivered contract-model, schema, fixture, and runtime adoption
only after `C4.4`. `I1.2` permits live XPLM acquisition adoption only after
`A1.9`. Do not modify q4xpcc from this repository.

`I1.0` now permits Phase 24A specification and plan reconciliation because
`D1.3` is verified.

## Evidence pointers

- T1 design:
  `docs/superpowers/specs/2026-08-09-xplane-fdau-backlog-status-skill-design.md`
- T1.6 plan:
  `docs/superpowers/plans/2026-09-07-t1-6-skill-session-hygiene-artifact-closure.md`
- q4xpcc brief: `docs/architecture/q4xpcc_phase_24a_contract_handoff.md`
