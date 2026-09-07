# T1.5 gate-5 evidence

- **Child:** `T1.5`
- **Gate:** `5`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-09-06
- **Subject:** Candidate validation and atomic Markdown publication

Apply revalidates the complete in-memory candidate, writes through a uniquely
owned same-directory partial, flushes, syncs, closes, validates the exact staged
bytes, rechecks staleness, and atomically replaces `BACKLOG.md`. It preserves
unmanaged Markdown bytes and cleans only its owned partial on refusal. Coverage
includes `test_success_publishes_exact_bytes_preserves_mode_and_closes_before_replace`,
both same-file partial-corruption refusal tests,
`test_failure_cleans_only_owned_partial_and_leaves_other_siblings`, and
`test_publication_orders_durability_stale_checks_and_fresh_audits`.

Reviewed implementation: `3cef7da35378bfce855565b618adf6d34c7a80db`.
[review.md](review.md) records an accepted rereview with zero unresolved
findings. The correction quality run passed 449 discovery tests in 260.582
seconds and 449 coverage tests in 261.039 seconds at 94%; the accepted rereview
passed 106 focused tests in 181.469 seconds.

Exact executable verification records at reviewed implementation revision
`3cef7da35378bfce855565b618adf6d34c7a80db`:

```powershell
uv run python -m unittest tests.test_backlog_status_edit tests.test_backlog_status_lifecycle tests.test_backlog_status_adherence tests.test_backlog_status_audit -v
uv run python tools/quality.py check
```

The first command passed 106 tests in 181.469 seconds during the accepted
rereview, including the named publication, corruption, ownership, cleanup, and
ordering cases. The second passed 449 discovery tests in 260.582 seconds and
449 coverage tests in 261.039 seconds at 94%, with every configured analyzer
passing.

Windows directly exercised close-before-replace, post-close partial reads,
corruption refusal, cleanup, and replacement. Ubuntu and Python 3.12 through
3.14 CI remain unobserved pending a separately authorized push. No release,
publication, push, or external-client work is authorized.
