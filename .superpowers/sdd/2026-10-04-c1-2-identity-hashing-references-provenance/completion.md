# C1.2 completion

- **Child:** `C1.2`
- **Gate:** —
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-10-04
- **Subject:** Completed identity, hashing, reference, authority, and provenance primitives.

C1.2 adds three immutable reference classes, five immutable authority/provenance classes, exact private scalar validators, private wire converters, and canonical definition/record self-hash preimages. Algorithm parameters are recursively copied into read-only mappings and tuples. Reference equality retains canonical primitive distinctions. Constructors enforce shape, canonical-domain, then semantic error tiers. Runtime code remains pure Python and standard-library-only. Later model factories, public model hash dispatch, family loaders, schemas, and corpus resources retain their approved later-child ownership.

The independent whole-branch review found five Important issues and no Critical or Minor issues. The executor reproduced and resolved all five with RED-to-GREEN regressions in `c0cc603`; the final focused integration command passed 41 tests. `review.md` records the review and executor disposition without claiming a second independent review. The complete suite verified all fixes: 581/581 tests pass. Gate receipts 1–4 provide separate acceptance evidence.

The complete offline hygiene command exited 0 on candidate `127eaa41eadb0c59e7ab674620e04e8eb72ff905` with plan task checkboxes updated in the worktree:

```text
uv run --offline --frozen python .codex/skills/hygiene/scripts/hygiene.py
581 unittest tests; 95% coverage (2,090 statements, 112 missed)
offline lock and backlog audit; strict MkDocs; all-files pre-commit
Ruff lint/format; ty; Bandit; detect-secrets; docstrings; dead code; complexity
fresh external wheel/sdist; strict Twine metadata; exact inventory and payloads
```

The earlier complete-suite attempt found two stale C1.1-only governance assertions, corrected in `127eaa4`. Earlier pre-suite checks also identified literal digest false positives, a runtime assertion, and missing public model docstrings; all were corrected without weakening gates. The successful docstring gate reports 41.6%. Material for MkDocs emitted its generic future-version advisory; the strict build passed. No required verification dimension was skipped.

External installed-wheel smoke passed on Python 3.12.14 outside the checkout. The wheel was built from `8fadcded73994a1de8c8e5cbd82787de4b18a1e0`; subsequent changes affected only governance tests and plan tracking. The runtime and installed-smoke files are unchanged. The hygiene build and the installed build produced identical artifact hashes:

| Artifact | SHA-256 |
| --- | --- |
| `xplane_fdau-0.1.0-py3-none-any.whl` | `5fd6d71e559f929e13e17622dfca985457a5bcf067ef4f1a2acfc28c3c68770d` |
| `xplane_fdau-0.1.0.tar.gz` | `be4b2bf0b15219e84102709393e40defcc45fa3c9674f1a385d72747b62b32b6` |

The installed artifact pair and isolated environment are retained at `C:\Users\Jeff\AppData\Local\Temp\xplane-fdau-c1-2-755d087f0efc424892382cb2f2a51cb8`. The hygiene-owned temporary pair was removed by its guarded cleanup. Final changes after this full gate are plan/backlog/evidence updates. The final focused governance and live-state run passed 34 tests; the backlog audit reports no findings, C1.2 verified with 4/4 gates, and G1 waiting. Task 5's final focused command passed 41 tests. Local integration is pending the user's branch-finishing choice.
