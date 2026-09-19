# T2.1 gate 2 — One fresh exact artifact pair

- **Child:** `T2.1`
- **Gate:** `2`
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-09-19
- **Subject:** Fresh external wheel and sdist with strict metadata and exact-content validation

Observed reviewed revision: `149392f33b404e13722ada199ab49e52f8c5f792`. The corrected-tree real hygiene run created `C:\Users\Jeff\AppData\Local\Temp\xplane-fdau-hygiene-kryk1qzd`, outside the checkout, built exactly `xplane_fdau-0.1.0-py3-none-any.whl` and `xplane_fdau-0.1.0.tar.gz` through `uv build --offline --no-sources`, then passed `twine check --strict` and `tools/release.py check-dist`. The separate closeout build in `C:\Users\Jeff\AppData\Local\Temp\xplane-fdau-t2-1-matrix-_lh_f555` passed the same checks. Both runs produced wheel SHA-256 `f9b45865a8d3433e0f4ecf783ddcde42f3a26e984055c4a2984db9a77018363a` and sdist SHA-256 `643b785d85d958329583754c1cde4d23edb3de90ba3b7798544a8d652c987798`.

`HygieneArtifactTests.test_each_success_builds_one_fresh_exact_pair_then_checks_final_status` proves distinct owned directories per invocation and exact command/filename construction. `tests/test_release_tool.py` exercises the existing validator's exact metadata, member, payload-byte, and governance-tool exclusion checks, including hostile synthetic members. Actual fresh artifacts passed that validator. Twine is a locked development dependency only; runtime dependencies remain empty.
