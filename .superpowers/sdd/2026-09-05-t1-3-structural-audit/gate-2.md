# T1.3 gate-2 evidence

- **Child:** `T1.3`
- **Gate:** `2`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-09-05
- **Subject:** Multi-child governing designs, single-child plans, and historical artifacts follow the exact metadata contract.

`tests.test_backlog_status_adherence`: `test_plan_rejects_zero_or_multiple_children_with_stable_codes`, `test_historical_disposition_names_known_node_or_existing_replacement`, `test_gate_drift_reports_title_each_ordinal_and_count_independently`, and `test_design_task_markers_are_formatting_and_do_not_deliver_backlog_gates` cover exact metadata, source context, and agreement. Historical D1 and queued F1 controls preserve the approved exceptions.

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
