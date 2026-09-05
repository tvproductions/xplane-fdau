### Finding Verdicts

- **Known child context is lost for row-local parse failures** — ADDRESSED. `.codex/skills/backlog-status/scripts/backlog/parse.py:739-750` now preserves errors that already carry context and rethrows every other inventory-row `MarkdownParseError` with the parsed `child_id`, original code/path/line/message, and any gate context. `tests/test_backlog_status_parse.py:456-474` covers status, dependency, link, and gate-count failures and asserts `node == "T1.2"` for each.
- **Source-fact tests omit required exact heading and acceptance fields/lines** — ADDRESSED. `tests/test_backlog_status_audit.py:62-69` now asserts every fixture gate heading's child, title, and exact line, while `tests/test_backlog_status_audit.py:72-101` asserts both design-acceptance sections' child, title, exact section line, punctuation-preserving folded statement, and exact statement line.
- **Fixture tests use `mkdtemp()` instead of required `TemporaryDirectory`** — ADDRESSED. `tests/test_backlog_status_audit.py:20-24` and `tests/test_backlog_status_policy.py:20-23,73-76` now register context-managed `TemporaryDirectory` instances through `self.enterContext`; the reported Windows run completed cleanup successfully.
- **Git process-launch `OSError` escapes the typed policy boundary** — ADDRESSED. `.codex/skills/backlog-status/scripts/backlog/policy.py:42-52` catches process-launch `OSError` and chains it into `PolicyError("policy.unavailable", ...)`. `tests/test_backlog_status_policy.py:82-91` proves the typed error and cause, and `tests/test_backlog_status_audit.py:138-149` proves `load_audit()` records the policy finding, leaves `policy` absent, and retains independently parsed ROADMAP/BACKLOG inputs.

### New Breakage in the Fix Diff

- None. The `parse_backlog()` wrapper at `.codex/skills/backlog-status/scripts/backlog/parse.py:739-750` leaves existing node-bearing gate/reason failures unchanged and preserves the original rendered exception components when enriching context. The policy adapter retains argument-vector, byte-oriented, read-only Git behavior.
- Test-evidence check: the appended report names the exact four-method RED/GREEN command, the 44-test affected-module run, Ruff, formatting, and ty checks, plus a fresh full quality gate and 298-test discovery run; all final outputs are reported clean. No suite was rerun for this re-review.

### Out-of-Scope Observations

- None. `BACKLOG.md:17,106`, `docs/superpowers/plans/2026-09-05-t1-3-structural-audit.md:4,86-90,513-528`, and `tests/test_backlog_status_cli.py:91,186` are controller-owned lifecycle, structure-ruling, and CLI-expectation changes from commit `6f5090f`; they were identified and excluded from Task 1 fix assessment.

### Verdict

**Fix round:** All findings addressed, no new Critical/Important breakage.

**Spec verdict:** ✅ Task 1 compliant for the four re-reviewed findings.

**Quality verdict:** Approved for the scoped fix round.
