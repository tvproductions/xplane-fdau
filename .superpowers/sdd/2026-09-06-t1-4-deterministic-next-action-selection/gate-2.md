# T1.4 gate-2 evidence

- **Child:** `T1.4`
- **Gate:** `2`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-09-06
- **Subject:** With no selection, the first dependency-ready local child is recommended in roadmap order.

`tests.test_backlog_status_next_action.NextActionTests.test_unselected_child_uses_roadmap_order_and_skips_terminal_children`
creates two simultaneously eligible unfinished children in reversed backlog order
and proves the roadmap-first child wins. The corrected test failed when the
selector was temporarily mutated to iterate backlog order (`T1.2` observed
instead of `T1.1`) and passed after restoring roadmap iteration.
`test_unselected_child_skips_unready_earlier_child_for_ready_later_child` proves
an earlier unready child is skipped for the later ready child.

Reviewed implementation: `972a36767aa2e372ac6d742a5fe92716509cafad`.
The independent review is recorded in [review.md](review.md); no finding remains
open, waived, parked, or deferred.

Fresh verification of the reviewed implementation and ledger state:

- `uv run python -m unittest tests.test_backlog_status_next_action tests.test_backlog_status_report tests.test_backlog_status_cli -q`: exit 0; 33 tests passed in 55.108 seconds.
- `uv run python tools/quality.py check`: exit 0; Ruff lint/format, ty, 382 discovered tests in 111.886 seconds, 382 coverage tests in 110.398 seconds at 94%, Bandit, detect-secrets, Interrogate at 43.6%, Vulture, and Xenon all passed.
- `uv run mkdocs build --strict`: exit 0; strict documentation built in 2.95 seconds.

These commands perform verification only. They do not authorize release,
publication, deployment, or consumer adoption.
