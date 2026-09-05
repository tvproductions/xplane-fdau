- **Referenced acceptance-list ordinal crash — ADDRESSED.**
  `.codex/skills/backlog-status/scripts/backlog/parse_sources.py:321` catches
  integer conversion failure, and line 385 converts it to the existing
  source-located unresolved-reference result. The CLI regression at
  `tests/test_backlog_status_cli.py:303` retains the valid four-gate control,
  checks both audit and JSON, and proves the independent malformed-artifact
  finding survives with the exact ordinal source line and child context.
- **Unlinked active-plan completion eligibility — ADDRESSED.**
  `.codex/skills/backlog-status/scripts/backlog/lifecycle.py:147` validates
  every populated active-plan completion slot against its declared child.
  Line 206 runs that check independently of BACKLOG validity. The former
  linked-only observation is removed, while effective verified linkage still
  requires HEAD bytes. `tests/test_backlog_status_lifecycle.py:120` covers
  unlinked valid, malformed, wrong-kind, wrong-child, wrong-ordinal, dirty,
  staged, missing, and invalid-BACKLOG cases. Line 164 verifies HEAD enforcement
  for verified and suspended-verified linkage without duplicate findings;
  `tests/test_backlog_status_cli.py:336` covers both public report commands.
- **Design task-list marker normalization — ADDRESSED.**
  `.codex/skills/backlog-status/scripts/backlog/parse_sources.py:259` removes
  the exact supported open/checked marker for both ordinary criteria and
  referenced numbered gates. `tests/test_backlog_status_adherence.py:293`
  proves bullet/numbered/task forms preserve statement text, source line,
  punctuation-sensitive disagreement, and unchanged open BACKLOG gates. The
  existing earlier-reference test also covers both task-marker forms.
- **Inherited fixture signing and hooks — ADDRESSED.**
  `tests/test_backlog_status_policy.py:48` uses the shared isolated Git
  initializer; the duplicate uncontrolled helper is removed. The regression
  at line 22 supplies an unavailable signer and a temporary failing hook in
  separate inherited-configuration cases and requires successful policy loading.
  Real project Git configuration and commit-hook behavior are unchanged.

## New breakage in the fix diff

None. No Critical, Important, or Minor finding remains in this correction.

## Out-of-scope observations

None.

## Checks

- Reviewed the sole fix package
  `review-b64c34c..1211466.diff` once in two bounded chunks against all four
  findings in `whole-branch-review.md`, using the scoped re-review prompt.
  Base: `b64c34caed73a00e8b03b423d10249dee5144509`.
  Accepted correction head: `1211466ce84f9129e09e680520a3c444118135a1`.
- Checked the appended Task 5 correction report against the actual code and
  regression assertions. It names six covering regressions and records their
  RED result (11 subtest failures, three errors), then GREEN (six tests, OK),
  followed by 67 covering tests passing. The report also records 374 passing
  tests on each supported Python target, the complete quality gate, explicit
  hidden-tool checks, strict documentation, current audit/JSON, and protected
  byte comparisons. The changes and test assertions support those claims.
- No suite rerun or further focused execution was needed: the named runs and
  inspected assertions answer the four risks. No Git command, subagent,
  source/index/HEAD mutation, or broader review was performed. This receipt
  is the sole retained write. Windows remains observed; Linux/macOS execution
  remains unobserved. The previously recorded MkDocs vendor notice remains
  nonblocking.

## Verdict

**Fix round: All four findings addressed; no new Critical, Important, or Minor
breakage.**

**Whole-branch review is accepted at `1211466ce84f9129e09e680520a3c444118135a1`,
subject to the already planned factual operational closeout.** The prior
rejection's four issues are closed. The implementer may now record the actual
review, completion, and four gate evidence records, commit eligible evidence,
and prove the verified state with the required clean post-commit audit.
Those remaining operations are not asserted complete by this review.
Local integration still requires its separately authorized workflow; this
acceptance grants no remote-write, tag, publication, or release authority.
