# C1.4 local integration

- **Child:** `C1.4`
- **Gate:** —
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-10-26
- **Subject:** Exact local fast-forward and focused main verification.

Jeff selected option 1, local integration, after branch acceptance. Both
worktrees were clean. Main fast-forwarded from
`a2ef12d411d20017b7099eb6d97f3a12b6c5e4f4` to the exact reviewed branch HEAD
`c754adfe6a7e82ac6a66190bfbbfc70b7f8870d2` using `git merge --ff-only`, without
pulling. That branch had accepted independent review, full offline hygiene,
691 external source unittest tests, strict artifacts/docs, installed-wheel
smoke and passing mandatory final hooks. Main HEAD equaled the recorded branch
HEAD before its focused verification. No second standalone full gate was run
on the identical source tree.

Main passed:

- `uv sync --offline --frozen --all-groups` and offline lock check.
- Strict backlog audit and both repository live-state tests (18.877 seconds
  in the earlier branch closeout; main's own fresh results are in its log).
- A fresh external wheel/sdist build, Twine strict metadata and exact inventory
  checks, and separate Python 3.12.16 wheel-only installed smoke outside main.
- All 130 input-manifest hashes matching the accepted branch.

Main's artifacts match the branch byte-for-byte:

| Artifact | SHA-256 |
| --- | --- |
| `xplane_fdau-0.1.0-py3-none-any.whl` | `f244f18648aff6a686762aae1eb5a69200fb2eb517102f1878bd4790abac5f5d` |
| `xplane_fdau-0.1.0.tar.gz` | `a6de6b6d582944b42672565e897a706d4fe5472c2a254b599e4137467f9a514f` |

The successful external artifact/environment directory
`C:/Users/Jeff/AppData/Local/Temp/xplane-fdau-matrix-dy6vpw4u` was removed only
after its guarded identity check. `integration-main.json` records every
verification command and exit status. Windows checkout newline translations
were restored only after proving exact index-byte equivalence; no Git content
or authored implementation changed.

Before removing the temporary worktree, all 52 local execution files were
copied to main and hash-verified. The temporary worktree
`U:/repos/xp/xplane-fdau/.worktrees/c1-4-timing` and merged branch
`feature/c1-4-timing` were then removed. The unrelated dependency-refresh
worktree remains untouched. The completed selection was cleared using the
guarded dry-run/hash/apply workflow; next action is C1.5 planning.

The final integration record changes only backlog, plan, handoff and evidence.
Its mandatory commit hooks remain enabled. Local integration does not grant
remote-sync, tag, publication, release or starter STRICT-acceptance authority.
