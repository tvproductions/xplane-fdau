# gz-skills v0.4.0 adoption review

- Decision: Jeff / tvproductions selected review and adoption on 2026-09-20.
- Project pin before: `v0.3.2`; selected pin: `v0.4.0`.
- Source: `https://github.com/tvproductions/gz-skills.git`.
- Official tag: `v0.4.0` -> annotated tag `531504a99847c369a033a2755fadebdc9845d7b4` -> release commit `6633ce3fe4ba88237454f8abb63ee9dc3fe8fc66`.
- Release notes: <https://github.com/tvproductions/gz-skills/releases/tag/v0.4.0>.
- Compared tags: <https://github.com/tvproductions/gz-skills/compare/v0.3.2...v0.4.0> (6 commits).

## Change and compatibility review

The release adds a standard-library-only, read-only `audit_portability.py` helper to `gzs-cross-platform-python`. It checks committed line endings and Python subprocess text decoding. The helper is a fallback; a repository-owned portability gate remains authoritative. The release also requires all 16 skills to state their discovery and fallback path and adds an inventory check for that rule. `gzs-git-sync` and `gzs-session-handoff` relocate existing fallback guidance without changing their action or explicit-only trigger. Other affected skills add discovery guidance and patch their individual versions. The plugin repository adds LF normalization for its own text files.

This project's exact `unittest` and standard-library-only runtime rules remain controlling. No plugin code is vendored, no Python runtime dependency or lockfile changes, and no Git sync or release action is introduced. The new portability helper can be consulted during B1.1's Python path and subprocess work; it is not added as a dependency of this repository's quality gate.

## Local verification

- `codex plugin list --json`: installed and enabled `gz-skills@gz-skills` v0.4.0; source Git URL and ref `v0.4.0` match the reviewed tag.
- `codex plugin marketplace list --json`: `gz-skills` marketplace uses the same official Git URL.
- Focused `unittest` policy assertion failed against the former v0.3.2 config, then passed after `.codex/config.toml` was updated to v0.4.0.
- Strict backlog audit: no findings; B1.1 remains the planned active child.
- The new helper was run read-only against the whole repository. It reported six existing findings: the `* text=auto` rule lacks explicit `eol=lf`, and five text-mode subprocess captures lack `errors=` in `backlog/report.py`, two backlog-report tests, `test_fdr_cli.py`, and `tools/installed_smoke.py`. This helper is not part of the repository quality gate and its result is not represented as a pass. These findings do not change the approved plugin pin; B1.1 must use explicit decoding behavior in its new subprocess test and report any relevant pre-existing findings rather than silently absorbing unrelated fixes.

Historical v0.2.0 adoption artifacts remain historical. The current pin is owned by `.codex/config.toml` and active policy in `AGENTS.md`.