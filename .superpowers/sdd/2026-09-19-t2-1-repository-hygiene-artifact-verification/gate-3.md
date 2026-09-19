# T2.1 gate 3 — Safe cleanup and preservation

- **Child:** `T2.1`
- **Gate:** `3`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-09-19
- **Subject:** Identity-checked successful cleanup and exact failure reporting

Observed reviewed revision: `149392f33b404e13722ada199ab49e52f8c5f792`. The real corrected-tree hygiene run removed only `C:\Users\Jeff\AppData\Local\Temp\xplane-fdau-hygiene-kryk1qzd` after both final Git status commands; a later `Test-Path` returned `False`. Production cleanup compares the created path and resolved parent against their captured `stat(follow_symlinks=False)` identities, rejects checkout containment and link/junction paths, and invokes `shutil.rmtree` only after all checks succeed.

`HygieneArtifactTests` covers exit-7 and launch-`OSError` failures at build, Twine, release validation, and both final-status commands; it asserts immediate stop, no cleanup, exact failed command, and the preserved path. Additional cases cover a renamed child, same-path replacement child and parent, changed resolved parent, checkout containment, mocked symlink/junction predicates, real directory symlink on this Windows host, identity-capture failure, and cleanup `OSError`. The independent review corrected cleanup-failure wording in `8d291c3`: recursive deletion may be partial, so this exception reports an incomplete cleanup at the exact path and makes no false preservation claim. Real junction creation and macOS/Linux behavior were not exercised.
