### Spec Compliance

- ❌ Issues remain: the first Important finding is improved but not fully closed. `.codex/skills/backlog-status/scripts/backlog/parse_sources.py:292` discards all prose statements whenever the subsection contains any list item, before the managed-reference scan at line 341. A managed reference and a sibling acceptance statement written with different prose/list forms can therefore bypass the required “reference must be the only acceptance statement” failure.
- ✅ Prior Important 2 resolved: `.codex/skills/backlog-status/scripts/backlog/adherence.py:269` accumulates title drift, every differing comparable ordinal, and count drift instead of returning after the first mismatch. `tests/test_backlog_status_adherence.py:397` verifies four independent findings and their source locations.
- ✅ Prior Important 3 resolved: `.codex/skills/backlog-status/scripts/backlog/findings.py:8` owns the single canonical ordering key; audit, adherence, and structural rules import it, and `.codex/skills/backlog-status/scripts/backlog/audit.py:6` continues to re-export the established public name.
- ⚠️ Cannot verify from this rerun: the supplied report records 74 focused tests, 333 full tests at 94% coverage, and successful static/docs checks. Per the review instruction, I did not rerun those suites. macOS and Linux execution remains deferred to CI.

### Strengths

- `.codex/skills/backlog-status/scripts/backlog/model.py:115` adds a frozen, source-located resolution problem without changing the version-1 report surface.
- `.codex/skills/backlog-status/scripts/backlog/parse_sources.py:341` now distinguishes missing/ambiguous sections, mismatched children, missing/ambiguous markers, and invalid four-item sequences. For statements that survive extraction, unresolved references can no longer compare equal to literal backlog text.
- `.codex/skills/backlog-status/scripts/backlog/adherence.py:276` reports title drift independently and line 287 converts a resolution problem into a blocking `artifact.gate-drift` at the reference line while avoiding dependent ordinal/count noise.
- The new tests at `tests/test_backlog_status_adherence.py:341` cover the original missing/ambiguous/wrong-count bypasses, and the expanded real-repository result demonstrates independent enumeration across the same ten reconciliation groups.
- The neutral `findings.py` extraction is small, cycle-safe, and authorized by the updated Task 3 brief; `tests/test_backlog_status_audit.py:22` proves the public audit import retains object identity.

### Issues

#### Critical (Must Fix)

None.

#### Important (Should Fix)

1. `.codex/skills/backlog-status/scripts/backlog/parse_sources.py:292` — `_acceptance_statements` returns only list statements when any list item exists. The resolver at line 341 therefore cannot see all statements in the subsection. For example, a plain managed-reference paragraph followed by a bullet criterion drops the reference and treats the bullet as the complete acceptance list; a bullet-form reference followed by a plain sibling drops the sibling and can resolve the reference as if it were alone. This still violates the explicit requirement that any exact managed reference be resolved and be the subsection's sole acceptance statement. Preserve enough raw/logical statement information to detect the managed form before list-family filtering, then emit the source-located resolution problem whenever any sibling exists. Add both mixed-form cases to `tests/test_backlog_status_adherence.py`, with backlog text chosen to match the currently surviving statements so the fail-closed assertion cannot pass incidentally through ordinary drift.

#### Minor (Nice to Have)

None.

### New Fix Breakage

- No separate regression found beyond the incomplete first-finding correction above.

### Assessment

**Task quality:** Needs fixes

**Reasoning:** Independent drift enumeration and the shared sorting contract are now correct and well tested. Managed-reference failure remains dependent on Markdown presentation, so Task 3 still does not fail closed for every subsection that contains the exact managed form.

### Checks

- Read the complete `review-6a9886f..1255a5d.diff` sequentially in three bounded chunks; no hunk was truncated.
- Read the appended `task-3-report.md` evidence. No test, suite, Git command, or checkout mutation was run.
