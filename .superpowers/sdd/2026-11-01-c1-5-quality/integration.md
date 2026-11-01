# C1.5 verified local main integration

- **Child:** `C1.5`
- **Gate:** —
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-11-01
- **Subject:** Exact local fast-forward, complete main fallback verification and cleanup.

Jeff selected option 1, local integration, after the completed implementation
and accepted independent review. Both worktrees were clean. Main fast-forwarded
without pulling from `82b1e81a42eab27c47037bc1dc47c4b4378b9476` to the recorded
branch HEAD `227756a4ace67d7b5bee7849b0e92469f94c6837`; equality was confirmed
before verification. Subsequent changes are integration bookkeeping only.

## Main verification and the required fallback

The first raw-input comparison failed for `mkdocs.yml`: the branch's working
copy contained one CRLF line ending and main held canonical LF bytes. Git
content was identical. The other 207 input hashes matched byte-for-byte and all
208 inputs were newline-equivalent. This was not relabeled as a passing exact
input comparison. Under AGENTS.md's failed-check rule, full offline hygiene
was run on main and passed before the branch/worktree were removed.

Passed main checks:

- `uv sync --offline --frozen --all-groups`.
- `uv lock --check --offline`.
- Strict backlog audit and both required live-state unittest tests.
- Fresh external wheel/sdist build, strict Twine metadata and exact inventory.
- External Python 3.12.16 wheel-only installation and the existing installed
  smoke, with site-packages import origin and no runtime requirements.
- `uv run --offline --frozen --all-groups python .codex/skills/hygiene/scripts/hygiene.py`,
  including strict docs, all-files Ruff/format/ty and the full unittest suite.

The canonical main input snapshot remained stable across verification.
The independent external main pair and the hygiene pair both exactly matched
the reviewed branch artifacts:

- Wheel SHA-256:
  `d6eaa482565cecdd47990d8df463da8026978f5912761edc0697f77ee02c0ac1`.
- Sdist SHA-256:
  `bfe6b1456e7a48a9add03e2fddada7a310f920ef02b6c6e3477e462a91f45244`.

The original [completion](completion.md) and [review](review.md) remain the
implementation evidence. The main fallback supplies the required fresh proof
for the raw configuration-byte difference; no runtime or validation change
was needed.

## Evidence preservation and cleanup

All 92 feature receipt/execution files were copied and hash-verified on main
before cleanup. The local integration receipt and raw commands are under
`.superpowers/sdd/c1-5-integration-2026-11-01/`, including
`integration.json`, `main-inputs.json`, the failed-input details and main gate,
live-state, artifact and installed-smoke logs. These raw execution records are
local-only, unavailable from a fresh clone.

Only after main verification passed, the clean native-created worktree at
`C:/Users/Jeff/.codex/worktrees/4d1d/xplane-fdau` was removed with Git's
worktree command, and the integrated temporary branch
`feature/c1-5-quality` was deleted normally. Both successful external C1.5
artifact environments were hash-checked and removed. Their paths in older
verification records are now historical. Hygiene removed its own temporary
artifact pairs through its checked cleanup.

The unrelated dependency-refresh worktree at
`C:/Users/Jeff/.codex/worktrees/c68f/xplane-fdau`, branch
`chore/dependency-refresh-2026-10-18`, remains at `f81c4c2`.

C1.5 remains verified with 4/4 gates; no child is selected. C2.1 planning is the
next canonical local action. STRICT starter gaps, G1 and release authority
remain separate. Local integration granted no remote sync, tag or publication
authority.