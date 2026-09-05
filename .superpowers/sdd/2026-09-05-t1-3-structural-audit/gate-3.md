# T1.3 gate-3 evidence

- **Child:** `T1.3`
- **Gate:** 3
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-09-05
- **Subject:** Lifecycle prerequisites and eligible evidence are validated without treating presence as proof.

`tests.test_backlog_status_lifecycle`: `test_stage_specific_positive_controls`, `test_unlinked_active_completion_slots_validate_declared_child_and_index_bytes`, `test_linked_completion_keeps_head_requirement_without_duplicate_findings`, and `test_historical_rejects_pin_identity_state_and_evidence_mutations` exercise stage prerequisites, declared completion slots, index and HEAD eligibility, and frozen historical admission. `tests.test_backlog_status_policy.AuditPolicyTests.test_fixture_commits_ignore_inherited_signing_and_hooks` proves isolated fixture commits.

Reviewed source: `1211466ce84f9129e09e680520a3c444118135a1`.
The independent whole-branch review accepted this corrected source in
[the final re-review](whole-branch-rereview.md); the original rejected review
remains in [the historical receipt](whole-branch-review.md).

Executed verification on Windows with `UV_OFFLINE=1`,
`UV_PYTHON_DOWNLOADS=never`, and matching `UV_PYTHON`:

- `uv run python tools/quality.py check`: exit 0 on Python 3.12.13;
  full unittest discovery passed 374 tests in 77.207 seconds; coverage ran
  374 tests in 78.083 seconds and passed at 94%. All aggregate components passed.
- `uv run --python 3.12 python -m unittest discover -v`: exit 0,
  Python 3.12.13, 374 tests in 74.954 seconds, OK.
- `uv run --python 3.13 python -m unittest discover -v`: exit 0,
  Python 3.13.14, 374 tests in 76.522 seconds, OK.
- `uv run --python 3.14 python -m unittest discover -v`: exit 0,
  Python 3.14.4, 374 tests in 78.257 seconds, OK.
- `uv run python .codex/skills/backlog-status/scripts/backlog_status.py audit`
  and `uv run python .codex/skills/backlog-status/scripts/backlog_status.py status --json`:
  both exit 0; no findings, version 1 JSON valid=true, recommendation=null.

[The implementation report](task-5-report.md) records the exact focused
RED/GREEN selectors, six regression tests, the 67-test covering run, full
quality/docs commands, and inspected outcomes. This record describes executed
source verification; the separate operational closeout report records the
subsequent committed-evidence publication and clean HEAD-backed audit.
