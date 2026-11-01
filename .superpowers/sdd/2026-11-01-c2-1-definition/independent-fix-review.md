**I1. Null-resolution numeric-domain inference and constructor/reader path mismatch — ADDRESSED.**

- `src/xplane_fdau/measurements/_definition_validation.py:115`: null resolution now selects each present value's own primitive shape rather than imposing the integer domain on real bounds. The domain pass rejects resolution at `/resolution`; non-null resolution still selects one homogeneous numeric domain. Unsupported bound types remain shape failures, including a later malformed maximum after a valid real minimum.
- `tests/test_measurement_definition.py:153` checks both real bound variants, exact CanonicalJSONError/path, unsupported bound shapes, and the competing later shape failure. `tests/test_measurement_definition_io.py:294` establishes the same constructor/reader path relationship and preserves later entry-shape precedence. The specific original defect no longer exists.

**I2. Cyclic raw dictionary/array preprocessing nontermination — ADDRESSED.**

- `src/xplane_fdau/measurements/_definition_io.py:116`: `_plain` tracks active ancestor identities, projects a back-edge to an unsupported scalar, and removes identities on exit. The original `_ObjectPairs` object is retained in exit frames, so temporary dictionary conversion does not corrupt ancestor bookkeeping. Finite sibling projections and repeated acyclic aliases retain their ordinary copies.
- `src/xplane_fdau/measurements/_definition_io.py:312`: `_duplicates` now uses matching entry/exit frames and ancestor tracking. Back-edges add no new properties and are skipped; remaining siblings are still visited before shape validation. Neither traversal imposes the canonical depth tier early. Cyclic inputs therefore terminate and reach the existing deterministic shape rejection, while later duplicates retain parse priority.
- `tests/test_measurement_definition_io.py:468` adds timeout-bounded subprocess checks with explicit kill/reap and context-managed pipe cleanup. Both dict/list cycles are tested through complete/incomplete entries and the direct shape seam; later duplicates are checked independently. Shared acyclic containers remain accepted and copied, including unchanged bytes after caller mutation. The specific original nontermination is removed from both walks.

### New Breakage in the Fix Diff

None found. No new Critical, Important or Minor issue was identified in the four-file fix. Numeric validation changes only the null-selection case; active-path cycle tracking does not mistake repeated acyclic aliases for cycles. Public interfaces, finite accepted wire content and runtime dependencies are unchanged.

### Out-of-Scope Observations

- The supplemental portability log reports existing text-decoding warnings at `tests/test_backlog_status_report.py:109`, `tests/test_backlog_status_report.py:116`, and `tests/test_fdr_cli.py:315`. None of these paths changed in this fix; the controller has already recorded them. They do not block or extend this fix wave. No warning targets the new subprocess helper.
- Final whole-branch hygiene/artifact/installed-wheel evidence and gate/lifecycle closeout remain controller obligations. This review does not claim they passed or grant integration/release authority.

### Checks and Evidence

- Reviewed `review-5ab8530..594d741.diff` once in two contiguous segments, against the exact findings in `final-fix-brief.md` and the implementer's `final-fix-report.md`. Scope was `5ab8530a5f088044eb94257a23d1e25ea2db6490..594d7414ec67c323d18e6bdc29a4aa47de118d60`; no unchanged-code re-review or Git command was used.
- Confirmed the recorded I1 RED output: two tests, five assertion failures, including exact exception-class mismatch. I1 GREEN: two tests, OK.
- Confirmed the recorded I2 RED output: three tests, eight bounded timeout assertion failures. I2 GREEN: three tests, OK, including the positive acyclic-alias control.
- Confirmed `final-fix-focused.log`: 49 tests in 2.528 seconds, OK. The named modules cover amended numeric/reader behavior and retain the finite deep-input, duplicate-priority, mixed-domain, semantic-order and build-barrier regressions.
- Confirmed `final-fix-commit-hooks.log`: Ruff check, Ruff format check, ty and unittest all Passed; commit `594d741` contains exactly the four reported files. The report records final successful static checks and retains the corrected intermediate typing diagnostic rather than claiming it passed.
- No additional execution probe or suite rerun was warranted: the code and named negative/positive regression evidence resolve both original doubts. No source, index, HEAD, branch or cache mutation was performed; only this authorized report was written.

### Verdict

**Fix round: All findings addressed, no new Critical/Important breakage.** I1 and I2 are closed for candidate `594d7414ec67c323d18e6bdc29a4aa47de118d60`. No source-review finding remains open from the original whole-branch review; final acceptance evidence remains pending as stated above.

Report: `.superpowers/sdd/2026-11-01-c2-1-measurement-definition/final-fix-review.md`.
