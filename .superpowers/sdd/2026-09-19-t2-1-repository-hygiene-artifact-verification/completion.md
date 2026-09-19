# T2.1 implementation and closeout verification

- **Child:** `T2.1`
- **Gate:** —
- **Kind:** verification
- **Result:** passed
- **Date:** 2026-09-19
- **Subject:** Complete offline project hygiene, fresh exact artifacts, safe cleanup, and separate Python compatibility evidence.

Implementation range: `16961cac8a906d354d0eabfa87ab1bb8cb8d5a49..8d291c3161569986beb06587b2f1b431ef55ce58` on temporary branch `feature/t2-1-hygiene-plan`. The range contains approved lifecycle setup `62313cd`, the ordered offline gate `f76b8f5`, exact artifact validation `3860622`, adapter guidance `d563c00`, and independent-review correction `8d291c3`. No runtime package file changed. Twine 7.0.0 and its transitive packages were added only to the development lock; no previously locked package version changed.

## Real routine hygiene

`uv run --offline --frozen python .codex/skills/hygiene/scripts/hygiene.py` exited 0 on Windows at the implementation checkpoint and again after the review correction. The corrected-tree run passed offline lock, strict backlog audit, strict MkDocs, all four local pre-commit hooks (quality check, detect-secrets baseline, lizard, cohesion), one fresh wheel/sdist build, strict Twine, exact `tools/release.py check-dist`, and both final Git status commands. The command removed only its verified directory `C:\Users\Jeff\AppData\Local\Temp\xplane-fdau-hygiene-kryk1qzd`. Tracked and untracked Git status before and after that run were identical. The corrected-tree wheel SHA-256 was `f9b45865a8d3433e0f4ecf783ddcde42f3a26e984055c4a2984db9a77018363a`; sdist SHA-256 was `643b785d85d958329583754c1cde4d23edb3de90ba3b7798544a8d652c987798`.

Injected `unittest` cases cover exact command order, offline child environment, OSError and nonzero fail-fast behavior, one distinct external artifact directory per successful run, exact filenames, final status before cleanup, per-phase failure preservation, child and parent identity replacement, rename, checkout containment, link/junction refusal, creation identity failure, and truthful cleanup failure reporting. The review correction was RED then GREEN in `HygieneArtifactTests.test_creation_and_cleanup_errors_report_and_preserve`; the subsequent real hygiene run exited 0.

## Separate child closeout matrix

The separate matrix command exited 0 on Windows. It built one new external wheel and sdist pair in `C:\Users\Jeff\AppData\Local\Temp\xplane-fdau-t2-1-matrix-_lh_f555`, passed `uv run --offline --frozen twine check --strict` and `tools/release.py check-dist`, and recorded the same wheel and sdist SHA-256 values above. Source `uv run --frozen --python <version> python -m unittest discover -q` passed **467 tests** on each CPython 3.12.13 (312.945 s), 3.13.14 (315.423 s), and 3.14.4 (314.986 s). Each version also passed `uv venv --python`, installation of that wheel into its own external venv, and `tools/installed_smoke.py 0.1.0` from outside the checkout. Matrix environments are under `C:\Users\Jeff\AppData\Local\Temp\xplane-fdau-t2-1-venvs-3l7wj0vv`. The matrix directories were retained through evidence capture; routine hygiene does not run this matrix.

Windows was directly exercised, including real directory-symlink creation. Junction refusal was tested through an injected predicate. macOS and Linux were not exercised on this host. The existing exact distribution validator, not source-tree inference, checked metadata, members, payload bytes, and governance-tool exclusion. No release, tag, package publication, Git push, or external-repository action occurred.
