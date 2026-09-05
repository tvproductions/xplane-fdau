### Finding Verdicts

- **Canonical `S` epic children are falsely rejected** — ADDRESSED. `.codex/skills/backlog-status/scripts/backlog/rules.py:75` now validates the parser-supplied owning epic and that epic's child inventory without deriving an epic ID from the child's dotted identifier. `tests/test_backlog_status_rules.py:124` covers the `S1.1`/`S2.x`/`S3.1`/`S4.1` shape, and the appended report records `load_findings=0 structural_findings=0` on the real repository.
- **One invalid dependency suppresses otherwise valid cycle detection** — ADDRESSED. `.codex/skills/backlog-status/scripts/backlog/rules.py:98` now rejects duplicate, unknown, ambiguous, and nonlocal dependencies edge by edge, while `.codex/skills/backlog-status/scripts/backlog/rules.py:148` retains the remaining valid local edges for a uniquely identified local source. `tests/test_backlog_status_rules.py:145` proves that an unknown sibling dependency and the independently valid cycle are both reported.
- **Invalid or ambiguous roadmap authority causes cascading cross-file findings** — ADDRESSED. `.codex/skills/backlog-status/scripts/backlog/rules.py:198` computes the independent same-file gate-count findings before `.codex/skills/backlog-status/scripts/backlog/rules.py:213` returns on invalid roadmap authority. The cross-file joins now use identity multimaps and unique comparison units at `.codex/skills/backlog-status/scripts/backlog/rules.py:216`, `.codex/skills/backlog-status/scripts/backlog/rules.py:226`, and `.codex/skills/backlog-status/scripts/backlog/rules.py:337`. `tests/test_backlog_status_rules.py:173` covers invalid roadmap isolation, ambiguous local identity isolation, and ambiguous release-gate isolation.
- **Combined identity collisions lose `roadmap.duplicate-id`** — ADDRESSED. `.codex/skills/backlog-status/scripts/backlog/rules.py:67` classifies each later entry against preceding kinds, so the combined case preserves both `roadmap.duplicate-id` and `roadmap.kind-conflict`; `tests/test_backlog_status_rules.py:155` covers both codes together.
- **Required `backlog/audit.py` modification is absent** — ADDRESSED by controller ruling and requirements correction. `.superpowers/sdd/2026-09-05-t1-3-structural-audit/task-2-brief.md:3` now limits Task 2 to the standalone structural API, and `.superpowers/sdd/2026-09-05-t1-3-structural-audit/task-2-brief.md:6` assigns composition in `backlog/audit.py` to Task 5. The plan diff and `progress.md` record the same ruling; no no-op audit edit is required.

### New Breakage in the Fix Diff

- **Important** — `.codex/skills/backlog-status/scripts/backlog/rules.py:363`: after the ambiguity fix, `elif gate_id not in expected: continue` skips every dashboard ID that exists uniquely in the roadmap but is not a release gate. For example, a release-dashboard row keyed `T1.1` has one unambiguous local-child identity, yet it now produces no `release.inventory` finding. That row is not a known release gate and must be classified like the existing unknown-row case; only multiple or cross-kind ambiguous identities should be skipped. Handle `len(entries) == 1 and entries[0].kind != "release_gate"` as `release.inventory`, and add a wrong-kind dashboard-ID regression test alongside the `G9` case.

### Out-of-Scope Observations

- ⚠️ The supported-target matrix remains explicitly scheduled for Task 5. The fix report identifies Python 3.12 for this round and does not claim other runtime verification; this scoped re-review does not reopen that controller-owned cannot-verify item.

### Verdict

**Spec compliance:** ❌ One fix-introduced release-inventory case remains unmet.

**Task quality:** Needs fixes.

**Fix round:** Findings remain open — all five prior findings are addressed, but the new Important wrong-kind release-dashboard regression must be fixed.
