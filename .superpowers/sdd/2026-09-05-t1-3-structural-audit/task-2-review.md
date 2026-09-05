### Spec Compliance

- ❌ Issues found. The structural rules do not accept the repository's declared `S` epic structure, do not preserve independently valid cycle edges when one dependency on the same child is invalid, and do not reliably suppress cross-file findings when roadmap authority is invalid or semantically ambiguous. The combined-collision case also loses the required `roadmap.duplicate-id` code, and the required `backlog/audit.py` modification is absent from the diff.
- ⚠️ Cannot verify from diff: execution on every repository-supported Python target. The report evidences one full local quality run but does not identify the interpreter or a supported-target matrix. No other Task 2 requirement is deferred as unverifiable; the issues below are visible in the supplied diff and focused authority check.

### Strengths

- `.codex/skills/backlog-status/scripts/backlog/rules.py:22` centralizes finding construction, keeps severity and gate context consistent, and preserves source path/line context for present rows.
- `.codex/skills/backlog-status/scripts/backlog/rules.py:26` and `.codex/skills/backlog-status/scripts/backlog/rules.py:155` provide stable output ordering and a terminating white/gray/black traversal. For an otherwise valid graph, self-cycles and ordinary multi-child cycles are reported at the closing dependency row deterministically.
- `.codex/skills/backlog-status/scripts/backlog/rules.py:73` uses an identity multimap, and `.codex/skills/backlog-status/scripts/backlog/rules.py:88` accepts `M0` only when it is a unique milestone, matching two central requirements.
- `tests/backlog_audit_support.py:10` gives each test a real copied fixture, while `tests/backlog_audit_support.py:14` enforces exactly one UTF-8 replacement and LF output.
- `tests/test_backlog_status_rules.py:49` has a valid-fixture control, and the parameterized cases cover every named trigger in the Task 2 matrix with code, path, node, line-presence, and null-gate assertions. The report records clean focused and full quality evidence with no warning noise.

### Issues

#### Critical (Must Fix)

None.

#### Important (Should Fix)

1. `.codex/skills/backlog-status/scripts/backlog/rules.py:63` derives the owning epic by removing only the final dotted component and requires that value to equal `child.epic`. This rejects valid children whose identifiers introduce a subseries beneath a broader epic. Focused outside-diff check for the named real-ledger risk: `ROADMAP.md:218` declares epic `S`, and `ROADMAP.md:226` through `ROADMAP.md:230` validly list `S1.1`, `S2.1`, `S2.2`, `S3.1`, and `S4.1` under it. The controller's integration evidence confirms five false `roadmap.epic-mismatch` errors at those exact rows. Because every error blocks success, the current repository can never pass this structural audit. Determine membership from the parsed owning epic and its child inventory; remove the unsupported `rsplit` equality assumption, then add a valid canonical `S`-epic regression test.

2. `.codex/skills/backlog-status/scripts/backlog/rules.py:94` uses one `source_valid` flag for the entire dependency list, sets it false for any duplicate, unknown, ambiguous, or nonlocal dependency, and `.codex/skills/backlog-status/scripts/backlog/rules.py:145` then drops every otherwise valid edge from that child. A child participating in a real cycle plus one unrelated bad dependency therefore reports the bad dependency but silently loses `roadmap.dependency-cycle`. This conflicts with the requirement to traverse validated local edges and retain independent same-file findings. Validate the source identity once, retain each individually valid local edge, exclude only the invalid edge, and add a cycle-plus-invalid-edge regression test.

3. `.codex/skills/backlog-status/scripts/backlog/rules.py:183` builds collapsed `all_nodes` and `expected` dictionaries before checking roadmap validity; `.codex/skills/backlog-status/scripts/backlog/rules.py:196` emits inventory/kind findings and `.codex/skills/backlog-status/scripts/backlog/rules.py:260` emits selection findings even when `ROADMAP.md` is invalid. Existing `load_audit` behavior replaces an unparseable roadmap with an empty snapshot, so a valid backlog then cascades into false `backlog.unknown-child` and `backlog.invalid-selection` errors. When the roadmap parses but contains duplicate identities, the dictionaries silently choose one ambiguous definition and cross-file drift/order/title checks still run; `.codex/skills/backlog-status/scripts/backlog/rules.py:311` similarly collapses ambiguous release gates. Guard every cross-file rule with the authority it needs and exclude ambiguous identities at the comparison-unit level, while leaving independent backlog gate-count checks active. Add invalid-roadmap and duplicate-roadmap-identity isolation tests that assert the absence of secondary findings.

4. `.codex/skills/backlog-status/scripts/backlog/rules.py:45` chooses the identity finding code from the set of kinds across the whole multimap. For two same-kind entries plus one cross-kind entry, every later entry receives `roadmap.kind-conflict`, so the repeated same-kind trigger never produces its required stable `roadmap.duplicate-id` code. Classify each collision against prior entries, emitting `roadmap.duplicate-id` for a repeated kind and `roadmap.kind-conflict` for a reused different kind, and cover the combined case.

5. `.superpowers/sdd/2026-09-05-t1-3-structural-audit/task-2-brief.md:3` explicitly lists `backlog/audit.py` for modification, but the review package contains no hunk for that file. The reviewer rubric treats an explicitly listed file with no corresponding hunk as a missing requirement. Add the intended Task 2 audit-layer change or obtain a controller ruling that corrects the brief before accepting the task.

#### Minor (Nice to Have)

None.

### Assessment

**Task quality:** Needs fixes

**Reasoning:** The implementation is organized, deterministic on valid graphs, and broadly tested, but it currently emits blocking false positives on the canonical roadmap and violates the task's error-isolation rules in several invalid-input combinations. Those defects, plus the missing required file change, prevent both spec and quality approval.
