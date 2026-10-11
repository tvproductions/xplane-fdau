# SDD ledger — plan: docs/superpowers/plans/2026-10-04-c1-3-typed-values-payload-references.md

Approval: 2026-10-11, Jeff: "let's proceed with C1.3".
Baseline: main 1a993f3753fafcd3a50f720ce7e58fafad42c02a; isolated feature/c1-3-typed-values.
Plan audit: intent and scope align with four BACKLOG gates; Tasks 1/3 produce
values consumed by Task 4 wire readers and serialization; Task 5 consumes
serialization and the same public models. No interface conflict.
Ruling: Execute inline with one independent whole-branch review as recommended
by the plan. Cost if wrong: fewer independent checks during implementation.
Ruling: Remove temporary C1.3/predecessor delivery snapshots obstructing this
approved lifecycle; retain the existing fixture-based lifecycle/adherence
positive and negative controls. The broader 19-method audit remains unresolved
separate work. Cost if wrong: an uncovered governance rule could be lost;
check actual fixture coverage before removal.
Ruling: Use native PowerShell/Python equivalents for upstream Bash workspace
scripts where the ignored external checkout is absent in the new worktree.
Preserve task briefs, base commits, test logs and completion lines here.
Cost if wrong: bookkeeping could differ from upstream scripts.
Todo: entry governance, Tasks 1–5, independent review, full offline hygiene,
external installed wheel, committed gates, finishing options.

Entry complete: guarded selection/planned/in_progress; logs retained. Governance 31 tests pass. Baseline 82 tests pass on Python 3.12.15.
Ruling: Group Tasks 1–4 in one cohesive primitive/reader commit because their tests and module inventory share files; preserve separate RED evidence and task outcomes. Cost if wrong: less granular history for bisecting.
Task 1: RED 20 assertion failures against an importable unvalidated InlineValue; GREEN exact numeric domains, order, immutable tuple copying and 65535 bound.
Task 2: RED invalid claim fields/media accepted; GREEN eight primitive/claim tests, Ruff and ty. Initial test context nesting was corrected so missing exceptions produce failures rather than secondary errors.
Task 3: RED 12 failures for declaration validation and defensive copies; GREEN 11 primitive/claim/declaration tests, Ruff and ty.
Task 4: RED passthrough readers/unsupported serialization (wire-red.log); additional mixed-invalid and null cases reproduced path/class differences, corrected before final GREEN.
Tasks 1–4: complete; final focused C1.3/native/import/smoke regression 86 tests passed (focused.log), Ruff lint/format and ty passed. Xenon affected files passed.
Task 5: installed checks RED wrong-order/payload fault injection produced no SmokeError; GREEN both now detected. Focused green above. Review/full gate/external wheel/evidence remain.

Independent review: 1a993f3..1c443ea, two Important findings, no Critical/Minor.
Final: fixed omission marker reconstruction — deepcopy and pickle literal-byte regressions RED→GREEN (negative control against reviewed values.py retained). Private Enum marker preserves omission identity.
Final: fixed shape precedence — constructors/materialized/parsed readers test irrelevant fields and null element tags in semantic order RED→GREEN.
Final focused regressions: 88/88 pass, Ruff/ty/Xenon pass. Full suite will run once under hygiene.
Final: Ruling: concurrent input mutation is outside the synchronous single-owner contract; ordinary caller mutation after construction is covered. Cost if wrong: caller racing constructor could capture inconsistent inputs.
Final: Ruling: broader pre-existing test audit remains separate scoped work; C1.3 lifecycle obstruction was corrected. Cost if wrong: remaining weak tests can still miss unrelated regressions.
Final: Ruling: live simulator and later-family integration remain later-child work; this child has no I/O or family loaders. Cost if wrong: downstream integration defects await their own gates.
Closeout preparation: Bandit detected type-narrowing asserts; replaced with casts after explicit checks, unchanged validation. Private reader docstrings restore documentation coverage above 40%; no thresholds changed.

Closeout: complete offline hygiene passed on 0b25c7c: 606 tests, 95% coverage; external installed smoke Python 3.12.15 passed with identical wheel/sdist digests. Evidence receipts prepared for guarded lifecycle and gate recording. Final branch finishing choice remains pending.

Final: all four gates recorded through inspected dry-run/hash/apply; review, completion and plan are HEAD-backed. C1.3 transitioned to verified. Final 46 focused governance/documentation/live-state tests and strict MkDocs pass. Finishing skill invoked; local integration decision pending.
