### Spec Compliance

- ✅ Spec compliant. `xplane_fdau/formats/xplane_fdr/reader.py:20` restricts the lexical hour to `0`-`23` while accepting both one-digit hours and zero-padded hours. The minute, second, and one-to-six-digit fractional forms are unchanged.
- ✅ The behavioral controls are meaningful reader tests rather than regex mirrors: `tests/test_fdr_reader.py:238` preserves the existing one-digit fractional case, and `tests/test_fdr_reader.py:243` exercises `0:00:00`, `00:00:00`, and `23:59:59.999999` through both v3 and v4 parsing.
- ✅ The unchanged malformed controls cover invalid hour `24` for v3 at `tests/test_fdr_reader.py:506` and invalid hour/minute/second and fractional width for v4 at `tests/test_fdr_reader.py:649`. Their helpers assert source, line, and message context at `tests/test_fdr_reader.py:499` and `tests/test_fdr_reader.py:653`.
- ✅ The change is bounded to the requested reader pattern, behavioral boundary test, and evidence report. No dependency, version-policy, format-authority, or unrelated runtime change appears in the supplied diff.
- ⚠️ Cannot verify from diff: none.

### Strengths

- `xplane_fdau/formats/xplane_fdr/reader.py:20` closes the Python 3.14 normalization gap at the lexical boundary, before `time.fromisoformat`, with a one-line correction and no compatibility branch.
- `xplane_fdau/formats/xplane_fdr/reader.py:378` retains the existing contextual `FDRParseError` path; `xplane_fdau/formats/xplane_fdr/reader.py:382` continues to delegate minute and second validity to `time.fromisoformat`.
- `tests/test_fdr_reader.py:243` checks observable v3/v4 results at both ends of the accepted hour range and includes maximum supported fractional precision.
- `.superpowers/sdd/2026-09-05-t1-3-structural-audit/python314-time-report.md:30` records the required Python 3.14 RED result. The report records the 30-test reader matrix on 3.12/3.13/3.14 at line 65, the 355-test Python 3.14 discovery pass and the initial sandbox launch failure at line 73, the full quality pass with 94% coverage at line 84, the informational MkDocs banner at line 93, and `git diff --check` at line 102.

### Issues

#### Critical (Must Fix)

None.

#### Important (Should Fix)

None.

#### Minor (Nice to Have)

None.

### Assessment

**Task quality:** Approved

**Reasoning:** The correction restores the already-specified `0`-`23` hour contract across supported interpreters without altering the accepted one-digit, minute, second, fractional, or contextual-error behavior. The tests exercise the reader behavior directly, and the recorded verification is complete and transparent about both the sandbox failure and the MkDocs informational banner.

**Focused check run:** Inspected only the relevant existing parser and malformed-test locations with `rg -n -C 8`; no suite was rerun because the supplied evidence answers the compatibility and quality risks.
