# Lizard inline-suite parser qualification

Observed October 26, 2026, against FDAU main `8bcef36` plus documentation-only
acceptance updates. Jeff directed deferring cognitive analysis and addressing
the four Lizard errors. Cognitive work remains deferred/UNKNOWN, not waived or
accepted. This record qualifies an upstream patch; it does not adopt an analyzer
version or close the installed FDAU gate.

## Cause and governing boundary

The four error records describe ten omitted methods, all inline protocol
definitions with an ellipsis body:

| Source | Original lines | Missing definitions |
| --- | --- | --- |
| `src/xplane_fdau/formats/xplane_fdr/config.py` | 41 | `read` |
| `src/xplane_fdau/formats/xplane_fdr/reader.py` | 94, 96 | `read`, `close` |
| `src/xplane_fdau/sinks/xplane_fdr.py` | 35, 42, 45, 47, 49, 51 | `__iter__`, two path properties, `write_sample`, `commit`, `abort` |
| `tests/test_contract_identity.py` | 16 | `__call__` |

The native reader records a pending function when it sees the declaration, but
activates it only when indentation increases. An inline suite never creates
that indentation. At a following definition or EOF, the pending function is
lost; nested inline suites can also interfere with enclosing-function state.

The adopted `lizard-functions-v1` contract requires original-source native
scores and complete AST/native discovery agreement. It explicitly requires
upstream parser remediation or a reviewed analyzer version, and prohibits
rewriting application source solely for the checker. FDAU's 20/10/5 ceilings,
discovery reconciliation and source files remain unchanged.

## Reviewable upstream correction

The [portable patch](2026-10-26-lizard-inline-suites.patch) targets upstream
[`01afe9c228ba2a3dc5253259d8415d2ef47f0b71`](https://github.com/terryyin/lizard/commit/01afe9c228ba2a3dc5253259d8415d2ef47f0b71).
SHA-256: `86b330f93bab1da0e51f042d8a4af61f9b1f3cde8a664527ce377d37b7c730dc`.

The patch finalizes a pending inline function before an equal indentation or
dedent, preserving its parent. Continuation tracking prevents parentheses,
brackets, braces and backslash continuation from ending the suite prematurely.
F-string interpolation tokens still contribute native complexity but do not
change surrounding indentation. Recovery at later definitions remains intact.
One existing disabled regression is enabled and twelve new unittest cases cover
native behavior, including protocol annotations, decorators, async methods,
sibling/nested functions, EOF, semicolons, continuations and interpolation.

The initial eight new cases failed against unmodified upstream. Broader testing
caught malformed-declaration recovery; independent review then found a multiline
f-string boundary hole. Both were corrected, with a failing regression preceding
the interpolation fix. Re-review found no remaining actionable findings.

## Observed qualification

All execution used the existing locked FDAU environment through uv on Windows
with Python 3.12.15. The draft was imported from an isolated ignored upstream
checkout, never installed over FDAU's selected Lizard 1.24.3. Analyzer import
origin was asserted before consumer qualification.

| Check | Observed result |
| --- | --- |
| Upstream Python-reader unittest discovery | 128 tests passed |
| FDAU `LizardMeasurementTests` against draft parser | Nine tests passed |
| FDAU original-source complete analysis scope | 1,528 functions; zero discovery errors; evaluator exit 0 |
| Baseline comparison | Exactly ten functions added; no previous function removed or name/line/score changed |
| Complexity ceilings | Maximum 20; overall mean 3.3972513089005236; all module means within 10 |
| Focused Ruff syntax/undefined-name/line-length checks | Passed |
| Patch whitespace and reverse-application check | Passed |
| Broad upstream unittest discovery | 1,594 entries; five import errors, seven skips, no assertion failures; overall exit 1 |

The broad run cannot establish complete upstream acceptance. Five existing
modules require pytest, prohibited by this project's explicit unittest-only
instruction; it was not installed or run. Nix is unavailable here. The native
upstream harness therefore remains unverified. Existing warnings remain in the
raw logs. A pre-existing tokenizer limitation also remains: a multiline f-string
ending in interpolation can report `end_line` before its closing quotes because
no closing-quote token is emitted. This affects block suites too and is separate
from the fixed discovery failure.

Focused reproduction from the draft upstream checkout:

```powershell
uv run --project U:/repos/xp/xplane-fdau --locked --all-groups python -m unittest discover -s test/test_languages -t . -p 'testPython*.py' -q
```

Consumer qualification uses the existing `tools.quality_analysis.measure_lizard`
and `evaluate_lizard` over `tools.quality.SOURCE_PATHS`, asserting that the imported
Lizard originates in the draft checkout. It compares each `(path, original line)`
record against a freshly measured installed baseline. The metadata package
version remains 1.24.3, so the candidate receipt also records its explicit draft
source and upstream base; the version label alone is not its provenance.

Raw local-only logs, reports, review and PR text are under
`.superpowers/sdd/2026-10-25-strict-heavy-starter-onboarding/lizard-inline-2026-10-26/`.
The portable patch and this record preserve the reviewed result outside that
ignored workspace.

## Adoption status

The four errors are resolved by the qualified patch, but remain present in the
installed released analyzer. Jeff subsequently authorized upstream submission.
[Lizard PR #530](https://github.com/terryyin/lizard/pull/530) is open against
`terryyin/lizard:master`, from `ahuimanu:fix/python-inline-suites` at
`2948b38ed0bf70c5a4c39163b45dfa50c3020314`. The fork branch contains exactly
the four reviewed files. Post-push fetch confirmed local/remote ahead and behind
counts of zero and a clean upstream checkout. The PR includes the reproduction,
observed tests and explicit full-harness limitations.

No FDAU dependency, plugin, runtime-source or acceptance-policy change occurred,
and no release was published. The next delivery step is upstream review and
publication, followed by reviewed FDAU adoption of the resulting analyzer version
and fresh affected gates. Until then A18 remains incomplete, independently of
the explicitly deferred cognitive work.
