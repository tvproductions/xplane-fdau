# T1.4 gate-4 evidence

- **Child:** `T1.4`
- **Gate:** `4`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-09-06
- **Subject:** Milestones, epics, release gates, and external boundaries are never recommended as implementation children.

The selector iterates only `RepositorySnapshot.roadmap.local_children` and
resolves candidates only through the parsed local-child backlog inventory.
`tests.test_backlog_status_next_action.NextActionTests.test_recommendation_never_selects_a_nonlocal_roadmap_node`
exercises the terminal local inventory. CLI tests additionally prove `next` is
human-only and informational, rejects mutation options, and preserves repository
sources, index, and HEAD. The independent whole-change scan confirmed no q4xpcc,
runtime, package, dependency, deployment, or release surface changed.

Reviewed implementation: `972a36767aa2e372ac6d742a5fe92716509cafad`.
The independent review is recorded in [review.md](review.md); no finding remains
open, waived, parked, or deferred.

Fresh verification of the reviewed implementation and ledger state:

- `uv run python -m unittest tests.test_backlog_status_next_action tests.test_backlog_status_report tests.test_backlog_status_cli -q`: exit 0; 33 tests passed in 55.108 seconds.
- `uv run python tools/quality.py check`: exit 0; Ruff lint/format, ty, 382 discovered tests in 111.886 seconds, 382 coverage tests in 110.398 seconds at 94%, Bandit, detect-secrets, Interrogate at 43.6%, Vulture, and Xenon all passed.
- `uv run mkdocs build --strict`: exit 0; strict documentation built in 2.95 seconds.

These commands perform verification only. They do not authorize release,
publication, deployment, or consumer adoption.
