# Task 4 correction round 1 independent review

## Spec compliance

**Spec compliant for the reviewed Task 4 scope.** Both prior Important findings
are closed. No new Critical, Important, or Minor finding was identified in the
Task 4 corrections within `676d52e..db51c61`.

## Per-finding verdicts

1. **Oversized Gate ordinal: resolved.**
   `.codex/skills/backlog-status/scripts/backlog/parse.py:469` now wraps the
   integer conversion and translates `ValueError` into `MarkdownParseError`
   with `evidence.gate-mismatch`, metadata line 4, and preserved exception
   chaining. It retains positive-ordinal syntax without adding an arbitrary
   range. `tests/test_backlog_status_evidence.py:129` checks the contextual
   finding from an actual committed oversized record;
   `tests/test_backlog_status_lifecycle.py:289` proves an independent missing
   review finding survives lifecycle aggregation.

2. **Release-prefix normalization: resolved.**
   `.codex/skills/backlog-status/scripts/backlog/parse_sources.py:172` now
   collects top-level list statements and their continuations, folds whitespace,
   then recognizes the managed prefix. It retains the first source line and
   uses the existing bounded section interval.
   `tests/test_backlog_status_lifecycle.py:301` checks four equivalent forms,
   all sixteen ordered duplicate pairs, original statement/duplicate locations,
   and equivalent prose outside the managed section. This closes both the
   valid-form false positive and folded-duplicate false negative.

## Quality assessment

**Task quality: Approved.** The production changes are small and address the
causes of the failures directly. The regressions verify observable domain
findings, independent-error retention, normalized recognition, and source
context rather than mirroring implementation details.

## Evidence and remaining limits

- Read the supplied correction diff once in bounded sequential chunks and the
  appended Task 4 report. No outside-code inspection, tests, suites, subagents,
  or checkout/index/HEAD mutation was needed; only this report was written.
- Recorded RED has three targeted tests with the two original conversion errors
  and eighteen release-form subtest failures; the same targeted command is
  GREEN after correction. Recorded final verification passes all 358 tests on
  Python 3.12, 3.13, and 3.14, the aggregate quality gate with 94% configured
  runtime coverage, explicit hidden-tooling static checks, and strict MkDocs.
  The existing nonblocking Material advisory remains documented.
- The range includes the independently reviewed native-time compatibility
  correction. Its acceptance is supplied by the controller; this review does
  not duplicate that runtime review.
- Cannot verify here: Task 5's CLI aggregation and malformed-input controls
  through `audit` / `status --json`. D1.2's historical-admission failure remains
  correct pending Task 5's reviewed gate reconciliation. The separately tracked
  oversized BACKLOG gate-count conversion also remains Task 5 work. None of
  these limits is represented as completed by this Task 4 approval.
