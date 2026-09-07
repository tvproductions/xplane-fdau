# T1.5 gate-1 evidence

- **Child:** `T1.5`
- **Gate:** `1`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-09-06
- **Subject:** Dry-run and explicit apply authority

The public mutation commands default to a no-write candidate report and publish
only when `--apply` is explicit. The Phase A dogfood confirmed that dry-run
preserved `BACKLOG.md`, then an identical pinned command changed only the
intended T1.5 row. Coverage includes
`test_all_mutation_dry_runs_render_candidate_and_preserve_every_file` and
`test_apply_changes_only_backlog_and_returns_ordinary_valid_audit`.

Reviewed implementation: `3cef7da35378bfce855565b618adf6d34c7a80db`.
[review.md](review.md) records an accepted rereview with zero unresolved
findings. The correction quality run passed 449 discovery and 449 coverage
tests at 94%; the accepted rereview passed 106 focused tests.

Windows directly exercised the write and atomic-replacement path. Ubuntu and
Python 3.12 through 3.14 CI remain unobserved pending a separately authorized
push. This evidence authorizes no release, publication, or downstream work.
