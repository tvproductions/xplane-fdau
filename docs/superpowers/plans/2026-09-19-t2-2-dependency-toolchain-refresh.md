# T2.2 Governed Dependency and Toolchain Refresh Implementation Plan

- **Governance:** active
- **Status:** draft
- **Date:** 2026-09-19
- **Roadmap child:** `T2.2`
- **Source specification:** `docs/superpowers/specs/2026-08-15-xplane-fdau-local-workflow-skills-design.md`
- **Approval:** —
- **Completion evidence:** —

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an explicit, guarded project adapter for complete dependency and toolchain refresh, align Python metadata to the approved range, and verify the refreshed project on Python 3.12, 3.13, and 3.14.

**Architecture:** A project command under `tools/` supplies read-only human/JSON status and guarded apply beneath canonical `gzs-update-dependencies`. Status gathers live official package and advisory evidence without changing tracked files. Apply revalidates a digest of that evidence and managed files before changing the uv pin, declarations, complete lock, and CI pins; its separate matrix helper runs only during apply and closeout.

**Tech Stack:** Python 3.12 standard library, development-only `packaging` for PEP 440 versions and requirements, `unittest`, uv, PyPI Index JSON, uv's OSV-backed audit, Git, existing hygiene and release tools.

**Spec:** `docs/superpowers/specs/2026-08-15-xplane-fdau-local-workflow-skills-design.md`, `T2.2` sections and four acceptance gates. Python policy: `docs/architecture/xplane_fdau_core_scope_amendment.md`.

## Global Constraints

- Implement only `T2.2`. Do not edit `xplane_fdau/`, q4xpcc, external adapters, the ignored Superpowers checkout, `T3.1`, `B1.1`, or canonical FDAU contracts.
- `ROADMAP.md` owns dependency order; `BACKLOG.md` alone owns child state. A draft plan does not select or advance `T2.2`.
- Preserve empty runtime dependencies and the standard-library-only package. `packaging`, uv, and refresh tooling remain development-only and absent from wheel and sdist runtime payloads.
- Use `unittest` only. Discover live official releases; never bake a newly discovered uv or package version into the adapter.
- Every status and apply invocation begins read-only. Status may use the network but must not edit tracked files, stage, commit, push, tag, publish, release, deploy, or modify another repository.
- Select only a verified, compatible, stable non-yanked uv target. Before mutation, block on missing or invalid official evidence, an incompatible target, unknown uv installer ownership, stale/unreviewed scope, or ambiguous edits. Record outdated, constrained, yanked, and vulnerable packages in the **current** lock as remediation findings; they do not prevent the refresh that may fix them. After refresh, unresolved yanks/advisories, unexplained constraints, resolver failures, and verification failures block successful completion; no silent ignore or gate reduction.
- Apply requires an unchanged report digest and a clean or fully scope-reviewed dependency surface. Reject any dirty path absent from the explicit reviewed list and changed bytes on a reviewed path.
- Update the uv executable through its owning installer before writing `[tool.uv].required-version` as `==` plus the verified stable version. If the installed uv is not standalone-managed, stop with an instruction for its actual owning package manager; do not mutate an unrelated global tool.
- Align `requires-python = ">=3.12,<3.15"`, retain 3.12/3.13/3.14 classifiers and matrix, keep compatible ordinary development requirements, and regenerate complete `uv.lock` with uv. Never edit the lock manually.
- Apply runs focused dependency-policy tests, one full repository hygiene pass, and the separate 3.12–3.14 source/installed-wheel matrix with exact artifact inventory. Each configured commit hook also runs the full quality suite; use focused tests between the three coherent commits in Tasks 0, 3, and 4. The explicit hygiene pass invokes that suite once more. Do not add a standalone `quality.py check` before hygiene or a commit.
- Use argument-vector subprocess calls with `shell=False`, `Path`, UTF-8, bounded network responses/timeouts, and checked temporary-directory cleanup on Windows, macOS, and Linux.
- Version `0.1.0` remains unreleased. No Git sync, push, tag, package publication, GitHub release, or q4xpcc edit is authorized.

## Execution cadence for this repository

The three planned commit checkpoints are Task 0 approved state, Task 3 complete implementation, and Task 4 verified evidence. The configured pre-commit hook runs `tools/quality.py check` at each commit; the single explicit hygiene pass during apply invokes that hook once more. Expect four full-suite executions on the unchanged fast-forward path, plus focused `unittest` runs during TDD. A merge that changes the tested tree requires a new full gate; a fast-forward to the already verified commit does not. Review corrections may require another commit and its hook; record that cost rather than adding speculative full-gate runs.

Between checkpoints, run the named focused `unittest` commands and inspect diffs. Keep intentional red tests uncommitted until the dependent implementation is green. Do not bypass hooks. After review changes, repeat only checks whose evidence was invalidated; repeat hygiene or the Python matrix only when the change affects their verified inputs.

## File responsibilities and live inventory

| File | Responsibility |
| --- | --- |
| `tools/dependency_sources.py` (new) | PyPI Index JSON retrieval and stable/yanked release selection; injected transport |
| `tools/dependency_refresh.py` (new) | Read-only status, digest, scope guard, and ordered apply orchestration |
| `tools/dependency_matrix.py` (new) | Source tests and installed-wheel smoke on 3.12, 3.13, 3.14; owned temporary resources |
| `tests/test_dependency_sources.py`, `tests/test_dependency_refresh.py`, `tests/test_dependency_matrix.py` (new) | Injected official responses and runners; no live registry or global uv mutation |
| `pyproject.toml`, `uv.lock`, `.python-version` | Python policy, exact uv requirement, compatible development/build requirements, universal lock; keep the 3.12 selector |
| `.github/workflows/ci.yml`, `.github/workflows/release-readiness.yml` | Matching verified uv version and existing source/installed-wheel jobs |
| `tools/release.py`, `tests/test_project_metadata.py`, `tests/test_release_tool.py`, `tests/test_release_workflows.py` | Exact Requires-Python metadata and CI pin assertions |
| `AGENTS.md`, `.codex/skills/hygiene/SKILL.md`, `tests/test_project_skills.py` | Route explicit refresh beneath canonical `gzs-update-dependencies`; keep routine hygiene offline |
| `BACKLOG.md`, `HANDOFF.md`, this plan, `.superpowers/sdd/2026-09-19-t2-2-dependency-toolchain-refresh/` | Controlled lifecycle, review, and four evidence gates after approval |

The current tree has `requires-python = ">=3.12"`, no uv `required-version`, `.python-version` at 3.12, `uv_build>=0.12.17,<0.13`, compatible development requirements, `uv.lock`, and uv `0.12.17` in both CI workflows. Inventory current `setup-uv` and `actions/*` revisions as project-managed CI tools, and inspect `.pre-commit-config.yaml`; its hooks are local, with no external hook revision. The imported q4xpcc handoff brief is a historical snapshot and must remain unchanged.

Use the official [uv required-version](https://docs.astral.sh/uv/reference/settings/#required-version), [lock/sync upgrade](https://docs.astral.sh/uv/concepts/projects/sync/), [uv audit](https://docs.astral.sh/uv/reference/cli/#uv-audit), and [PyPI Index JSON](https://docs.pypi.org/api/index-api/) interfaces. Installed uv's tree JSON is a preview interface; validate its schema and fail closed if it changes. The exact uv pin makes that parser version explicit.

### Task 0: Approve and register the single child

**Files:** Modify this plan and `BACKLOG.md` only after user approval; use the guarded backlog script, never hand-edit lifecycle cells.

**Interfaces:** `T2.2` moves from `specified`/0-of-4 to `planned`, then selected `in_progress`; four gates stay open.

- [ ] **Step 1: Record actual approval.** Replace draft status and blank approval with the actual approval date and owner. Do not infer approval from this draft review.
- [ ] **Step 2: Check backlog state.** Run `uv run python .codex/skills/backlog-status/scripts/backlog_status.py audit` and `next`; stop on any audit finding.
- [ ] **Step 3: Preview plan registration.** Dry-run `transition T2.2 planned --expect specified --plan docs/superpowers/plans/2026-09-19-t2-2-dependency-toolchain-refresh.md` and inspect its candidate diff/audit.
- [ ] **Step 4: Register the plan.** Repeat the transition with its printed `--target-sha256` and `--apply`, then audit.
- [ ] **Step 5: Select the child.** Dry-run and apply `select T2.2 --expect-current none` using its printed digest, then audit.
- [ ] **Step 6: Start implementation state.** Dry-run and apply `transition T2.2 in_progress --expect planned` using its printed digest, then audit.
- [ ] **Step 7: Commit the starting state.** Update current-state `unittest` expectations only if a focused red test identifies an obsolete expectation. Commit the approved plan and coherent lifecycle state before implementation.

### Task 1: Produce deterministic read-only status

**Files:** Create `tools/dependency_sources.py`, `tools/dependency_refresh.py`, `tests/test_dependency_sources.py`, and `tests/test_dependency_refresh.py`.

**Interfaces:** `fetch_index(name: str, opener: Opener) -> dict[str, object]`, `newest_stable_release(index: dict[str, object]) -> str`, `release_is_yanked(index: dict[str, object], version: str, sha256: str) -> bool`, `collect_status(root: Path, runner: Runner, opener: Opener) -> dict[str, object]`, `canonical_json(report: dict[str, object]) -> str`, and `main(argv: Sequence[str] | None = None) -> int`.

`Opener` accepts a `urllib.request.Request`, timeout, and byte ceiling; it reads at most ceiling plus one byte and returns response bytes, the final response URL, and content type. `fetch_index` validates that final URL remains on `pypi.org` and the response is Index JSON before parsing. `Runner` accepts an argument tuple and working directory and returns exit code, UTF-8 stdout, and UTF-8 stderr. Define these aliases in `tools/dependency_sources.py` and import them into the CLI.

- [ ] **Step 1: Write source-selection tests.** In `tests/test_dependency_sources.py`, make an injected Index JSON record with stable `0.12.17`/`0.12.18`, newer `0.13.0rc1`, and yanked `0.12.19` files. Assert `newest_stable_release(index) == "0.12.18"`; include a package name normalization case (`My_Package` → `my-package`).
- [ ] **Step 2: Prove source selection red.** Run `uv run --frozen python -m unittest tests.test_dependency_sources -v`. Require a missing function or failing selection assertion, not a live network failure.
- [ ] **Step 3: Declare the parser dependency.** Add `packaging` to the dev group in `pyproject.toml` with a compatible bound. Run `uv lock` without `--upgrade` and inspect that the change adds only this direct requirement and its needed lock edges. The package remains absent from runtime dependencies.
- [ ] **Step 4: Implement source selection.** In `tools/dependency_sources.py` define `SourceError`, `Opener`, `fetch_index`, and `newest_stable_release`. Normalize names per PEP 503, call `https://pypi.org/simple/{name}/` with `Accept: application/vnd.pypi.simple.v1+json`, 15-second timeout, 5 MiB ceiling, and an in-domain redirect check. Parse versions with `packaging.version.Version`; select the highest stable version with a non-yanked file. The transport and response checks begin with:

  ~~~python
  request = Request(f"https://pypi.org/simple/{normalized_name}/", headers={"Accept": "application/vnd.pypi.simple.v1+json"})
  body, final_url, content_type = opener(request, 15, 5 * 1024 * 1024)
  if urlparse(final_url).scheme != "https" or urlparse(final_url).hostname != "pypi.org" or len(body) > 5 * 1024 * 1024:
      raise SourceError("untrusted or oversized Index response")
  if content_type.split(";", 1)[0].strip() != "application/vnd.pypi.simple.v1+json":
      raise SourceError("unexpected Index content type")
  ~~~
- [ ] **Step 5: Prove selection green.** Run `uv run --frozen python -m unittest tests.test_dependency_sources -v`. Inspect `pyproject.toml` and `uv.lock` to confirm no unrelated upgrade.
- [ ] **Step 6: Write source-failure tests.** Add fixtures for malformed/non-object JSON, missing `versions`/`files`, oversized response, outside-domain redirect, invalid artifact filename, prerelease-only releases, and all-yanked releases. Assert `SourceError` with the offending package and reason. Add one locked-artifact hash match and one mismatched SHA-256; only the match may establish a yank state.
- [ ] **Step 7: Prove source failures red.** Run `uv run --frozen python -m unittest tests.test_dependency_sources -v`; require the new assertions to fail.
- [ ] **Step 8: Implement artifact verification.** Add `release_is_yanked(index, version, sha256)` using `packaging.utils` wheel/sdist filename parsers and exact Index JSON SHA-256 evidence. Raise `SourceError` when the locked artifact is absent or its evidence conflicts; do not infer a safe non-yanked state from missing data. Compare the parsed filename version and exact digest:

  ~~~python
  def artifact_identity(filename: str) -> tuple[str, Version]:
      try:
          name, parsed_version, _, _ = parse_wheel_filename(filename)
      except InvalidWheelFilename:
          try:
              name, parsed_version = parse_sdist_filename(filename)
          except InvalidSdistFilename as error:
              raise SourceError("invalid locked artifact filename") from error
      return canonicalize_name(name), parsed_version

  expected = (canonicalize_name(index["name"]), Version(version))
  matches = [file for file in index["files"] if artifact_identity(file["filename"]) == expected and file["hashes"].get("sha256") == sha256]
  if len(matches) != 1:
      raise SourceError("locked artifact has no unique official hash match")
  return bool(matches[0].get("yanked", False))
  ~~~
- [ ] **Step 9: Prove source evidence green.** Run the focused source tests and `git diff --check`. Review `tools/dependency_sources.py`, its tests, `pyproject.toml`, and the lock change as one independently testable source-evidence deliverable. Keep the change in the isolated worktree for the Task 3 implementation commit.
- [ ] **Step 10: Write status-shape tests.** In `tests/test_dependency_refresh.py` inject results for `uv --version`, `uv tree --outdated --all-groups --universal --locked --format json`, `uv workspace metadata --locked`, `uv audit --locked --output-format json`, and PyPI responses. Require deterministic keys `schema_version`, `uv`, `python`, `dependencies`, `current_findings`, `pre_apply_blockers`, `proposed_files`, `proposed_commands`, `reviewed_paths`, and `plan_sha256`. Require every proposed command to be an argument list. Add a universal-only locked package fixture and require its outdated classification in the report; the current-platform tree omits such entries.
- [ ] **Step 11: Write the remediation boundary test.** Inject a valid current-lock advisory plus a yanked locked artifact; assert both appear in `current_findings` and `pre_apply_blockers == []`. Inject malformed advisory JSON and assert a `pre_apply_blockers` source error. Inject a newest stable uv release whose official `requires-python` excludes Python 3.14; assert the verified current pin is retained, the incompatible release is reported, and `pre_apply_blockers` is nonempty. Capture the findings exit code observed for the tested uv version in the injected fixture; accept it only with a valid findings payload. Any other nonzero exit is a source blocker. Use these assertions after collecting the injected report:

  ~~~python
  self.assertEqual({item["kind"] for item in report["current_findings"]}, {"advisory", "yanked"})
  self.assertEqual(report["pre_apply_blockers"], [])
  ~~~
- [ ] **Step 12: Prove status red.** Run `uv run --frozen python -m unittest tests.test_dependency_refresh -v`. Require missing collector/report behavior.
- [ ] **Step 13: Implement locked-graph collection.** In `tools/dependency_refresh.py`, parse `pyproject.toml` with `tomllib` and requirements with `packaging.requirements.Requirement`. Validate the exact preview schemas returned by this pinned uv, enumerate every declared dependency group, match lock artifacts to official Index JSON by package/version/SHA-256, and sort normalized packages and findings. Treat unknown schemas, missing hashes, source failures, and unverified candidate compatibility as `pre_apply_blockers`. Validate the newest stable uv release's official Python metadata against 3.12, 3.13, and 3.14 with `packaging.specifiers.SpecifierSet`; retain the current verified pin with evidence if the newest stable release excludes one. Match every universal-lock package to an outdated result or an explicit no-candidate finding. Use the following compatibility check on the official selected-release metadata before returning the status report:

  ~~~python
  supported = (Version("3.12"), Version("3.13"), Version("3.14"))
  allowed = SpecifierSet(requires_python)
  if any(version not in allowed for version in supported):
      pre_apply_blockers.append({"kind": "incompatible-uv", "version": candidate})
      candidate = current_verified_uv
  ~~~
- [ ] **Step 14: Implement audit classification.** Parse valid `uv audit` JSON into `current_findings` whether the command returns success or the tested uv findings exit code. Record package, locked version, advisory ID, fixed version when present, and source evidence. A malformed response or unrelated command failure becomes a `pre_apply_blockers` entry. Never turn a current finding into a pre-apply blocker.
- [ ] **Step 15: Implement the report digest.** Serialize with the function below; remove `plan_sha256` before hashing the canonical report plus SHA-256 values for managed files and reviewed dirty paths and the Git index blob ID/status for each staged path. Strip machine-specific absolute paths. Two distinct temporary repository roots with equal logical contents must yield identical JSON, exactly one terminal LF, and the same digest.

  ~~~python
  def canonical_json(report: dict[str, object]) -> str:
      return json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
  ~~~

- [ ] **Step 16: Add status CLI modes.** `status` renders the report for a human; `status --json` emits only canonical JSON. Both call the same `collect_status` and neither changes tracked files, staging, remote state, or the external Superpowers checkout.
- [ ] **Step 17: Prove status green.** Run `uv run --frozen python -m unittest tests.test_dependency_sources tests.test_dependency_refresh -v` and `git diff --check`. Review the status CLI/tests without committing yet. Run one real `status --json` read-only and record any live current findings or pre-apply blockers for the later reviewed apply.

### Task 2: Guard apply and run the one closeout matrix

**Files:** Modify `tools/dependency_refresh.py` and `tests/test_dependency_refresh.py`; create `tools/dependency_matrix.py` and `tests/test_dependency_matrix.py`.

**Interfaces:** `apply_status(root: Path, expected_sha256: str, reviewed_paths: tuple[str, ...], runner: Runner, opener: Opener) -> ApplyResult` recollects status and runs ordered update/gates; `main(...) -> int` maps that result to a CLI exit code. `run_matrix(root: Path, runner: Runner, make_temp: TempFactory) -> MatrixResult` builds and verifies the exact pair. Define `ScopeError`, `UpdateError`, and `ApplyResult` in `tools/dependency_refresh.py`, and `MatrixResult` and `TempFactory` in `tools/dependency_matrix.py`. `ApplyResult` records command tuples/exits, initial and refreshed findings, artifact hashes, and preserved failure paths.

The reviewed path list is exact repository-relative paths. Status includes each current dirty path, working-byte SHA-256, and any staged index blob ID in the report digest. Apply permits exact reviewed tracked and untracked implementation paths with recorded SHA-256 values. It rejects an unlisted dirty path, changed listed contents, a newly appearing untracked file under a managed directory after the status token, branch change, source change, or report digest change before its first mutation. Tests inject a runner and temporary directory factory; they never invoke real uv self-update or touch the actual repository.

- [ ] **Step 1: Write scope-guard tests.** In `tests/test_dependency_refresh.py`, inject a temporary repository and runner. Assert that a clean surface or exact `--review-scope` paths with unchanged bytes can proceed. Assert that stale `plan_sha256`, changed official-source response, changed lock bytes, changed staged index blob with identical working bytes, unreviewed dirty path, an unlisted untracked file appearing after status under a managed directory, and branch change return `ScopeError` before the runner sees a mutating command. Include the new `tools/` and `tests/` files created in Tasks 1–2 as reviewed untracked paths and assert they are accepted when their hashes match.
- [ ] **Step 2: Prove the guard red.** Run `uv run --frozen python -m unittest tests.test_dependency_refresh -v`; require failed apply assertions.
- [ ] **Step 3: Implement digest and path guard.** Add `apply --plan-sha256 HEX [--review-scope PATH ...]` and `apply_status(...)`. Recollect `collect_status` immediately, compare its digest, normalize each reviewed path as repository-relative, and verify the exact dirty set plus working-byte hashes and staged index blob IDs before the first mutation. Reject `pre_apply_blockers` only. Validate every proposed metadata/CI anchor and prepare replacement bytes in memory before any uv update or file write; ambiguous edits are pre-apply blockers. Preserve `current_findings` for the refresh report. The guard branch is:

  ~~~python
  if report["plan_sha256"] != expected_sha256:
      raise ScopeError("status digest changed")
  if report["pre_apply_blockers"]:
      raise ScopeError("pre-apply blocker")
  ~~~
- [ ] **Step 4: Prove scope guard green.** Run the focused refresh tests. Confirm every mutating runner call remains absent in stale/unreviewed fixtures and that a current advisory/yank fixture reaches the next apply phase.
- [ ] **Step 5: Write uv-owner tests.** With an injected runner, assert an already-current uv skips self-update. A standalone-managed older uv permits `("uv", "self", "update", "--dry-run", candidate)` before `("uv", "self", "update", candidate)` and verifies `uv --version` afterward. Unknown/non-standalone ownership blocks before writes with the owning-package-manager instruction.
- [ ] **Step 6: Prove uv-owner tests red.** Run the focused refresh tests; require owner/order assertions to fail.
- [ ] **Step 7: Implement the uv-owner phase.** Accept only a verified stable compatible candidate from the status report. Probe the standalone installation with the dry run; update through its owner, verify the resulting version, then set `[tool.uv].required-version` to `==` plus that exact version. Never mutate an unrelated global uv installation. Use the injected runner in this order:

  ~~~python
  if installed_uv != candidate:
      code, _, error = runner(("uv", "self", "update", "--dry-run", candidate), root)
      if code:
          raise ScopeError(f"uv installer ownership could not be proved: {error}")
      code, _, error = runner(("uv", "self", "update", candidate), root)
      if code:
          raise UpdateError(f"uv update failed: {error}")
      code, output, error = runner(("uv", "--version"), root)
      if code or Version(output.split()[1]) != Version(candidate):
          raise UpdateError(f"uv version verification failed: {error}")
  ~~~
- [ ] **Step 8: Prove uv-owner tests green.** Run the focused refresh tests and inspect the injected runner's ordered command tuples.
- [ ] **Step 9: Write metadata-edit tests.** Require a single exact edit of `requires-python = ">=3.12,<3.15"`, preserved 3.12/3.13/3.14 classifiers, compatible `packaging`/`uv_build` bounds, and matching uv `version:` values in both CI workflows. Duplicate/mismatched TOML or workflow pins must fail before any uv update or file write. A test must compare every untouched byte outside the approved anchors.
- [ ] **Step 10: Prove metadata edits red.** Run the focused refresh tests; require the new edit assertions to fail.
- [ ] **Step 11: Implement exact edits.** Implement the preflight preparation called by Step 3: parse `pyproject.toml` to validate expected current values and prepare all new file bytes in memory. Validate every workflow anchor before the uv-owner phase. Write only the prepared bytes after all replacements pass; re-read and compare to them. Use an exact-anchor helper for each allowed text replacement:

  ~~~python
  def replace_exact(source: str, old: str, new: str) -> str:
      if source.count(old) != 1:
          raise ScopeError(f"expected one anchor: {old!r}")
      return source.replace(old, new)
  ~~~

  Preserve compatible ordinary development constraints unless the live official evidence documents a required bound.
- [ ] **Step 12: Prove metadata edits green.** Run the focused refresh tests and inspect the fixture diff for the approved anchors only.
- [ ] **Step 13: Write refresh-outcome tests.** Inject a valid current-lock advisory and yank, then a clean post-upgrade graph: assert apply runs `uv lock --upgrade` once and proceeds. Inject a remaining advisory/yank or unexplained incompatible constraint after upgrade: assert failure with package/version/evidence and preserved changed files. Inject `uv lock --upgrade` resolver failure: assert failure at that command, with the original report and failed command retained.
- [ ] **Step 14: Prove refresh outcomes red.** Run the focused refresh tests; require the new after-refresh assertions to fail.
- [ ] **Step 15: Implement the ordered refresh.** Run `("uv", "lock", "--upgrade")` once, then `("uv", "sync", "--all-groups", "--locked")` and `("uv", "lock", "--check")`. Recollect `uv tree --outdated --all-groups --universal --locked --format json` and `uv audit --locked --output-format json`. Classify the refreshed graph separately from `current_findings`. Fail successful completion for remaining yanks/advisories or unexplained constraints; retain documented compatible constraints in the report. On any resolver, source, or policy failure, preserve changed scope and the exact failed command.
- [ ] **Step 16: Prove refresh outcomes green.** Run `uv run --frozen python -m unittest tests.test_dependency_sources tests.test_dependency_refresh -v`. Confirm no test calls real uv self-update or edits the actual repository.
- [ ] **Step 17: Write matrix artifact tests.** In `tests/test_dependency_matrix.py` inject runner and temporary-directory factory. Require exactly `xplane_fdau-0.1.0-py3-none-any.whl` and `xplane_fdau-0.1.0.tar.gz`, strict Twine validation, `tools/release.py check-dist`, SHA-256 values, and rejection of an injected wheel containing `tools/dependency_refresh.py`.
- [ ] **Step 18: Prove artifact tests red.** Run `uv run --frozen python -m unittest tests.test_dependency_matrix -v`; require missing matrix behavior.
- [ ] **Step 19: Implement build and inventory.** In `tools/dependency_matrix.py`, build once in one external temporary directory, inspect exact artifact names and wheel/sdist members, then run these argument tuples:

  ~~~python
  ("uv", "build", "--offline", "--no-sources", "--out-dir", str(artifact_dir))
  ("uv", "run", "--offline", "--frozen", "twine", "check", "--strict", str(wheel), str(sdist))
  ("uv", "run", "--offline", "--frozen", "python", "tools/release.py", "check-dist", str(artifact_dir))
  ~~~

- [ ] **Step 20: Prove build/inventory green.** Run the focused matrix tests; inspect exact names, hashes, and rejection of the leaked tooling file.
- [ ] **Step 21: Write interpreter and cleanup tests.** For each of `3.12`, `3.13`, and `3.14`, assert a source `unittest` command, isolated venv outside the checkout, installation of the one built wheel, and `tools/installed_smoke.py 0.1.0` from that external directory. Exercise Windows `Scripts/python.exe` and POSIX `bin/python` selection. Require successful cleanup only after resolved-path identity check; preserve failed directories.
- [ ] **Step 22: Prove interpreter tests red.** Run the focused matrix tests; require the new per-version assertions to fail.
- [ ] **Step 23: Implement interpreter runs.** For each version, run `("uv", "run", "--frozen", "--python", version, "python", "-m", "unittest", "discover", "-q")`, create its external venv, install the exact wheel, and call its interpreter on the installed-smoke script. Return `MatrixResult` with per-command exits, artifact hashes, and preserved failure paths. Keep the three versions explicit. Use these command vectors for each external venv, then run the installed smoke script with that interpreter:

  ~~~python
  venv_dir = artifact_dir / f"venv-{version}"
  runner(("uv", "venv", str(venv_dir), "--python", version), root)
  interpreter = venv_dir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
  runner(("uv", "pip", "install", "--python", str(interpreter), str(wheel)), root)
  runner((str(interpreter), str(root / "tools/installed_smoke.py"), "0.1.0"), artifact_dir)
  ~~~
- [ ] **Step 24: Integrate apply gates.** After a clean refreshed graph, apply runs focused dependency-policy tests, then one `uv run --offline --frozen python .codex/skills/hygiene/scripts/hygiene.py`, then `run_matrix`. Stop at the first failed gate. The matrix is one live apply/closeout deliverable; unit tests use the injected runner only.
- [ ] **Step 25: Prove matrix/apply green.** Run `uv run --frozen python -m unittest tests.test_dependency_matrix tests.test_dependency_refresh -v` and `git diff --check`. Review the apply and matrix helpers/tests without committing yet. Do not run the live three-version matrix during this unit-test task.

### Task 3: Align project policy and perform the reviewed live refresh

**Files:** Modify `pyproject.toml` and generated `uv.lock` through apply; modify `tools/release.py`, `tests/test_project_metadata.py`, `tests/test_release_tool.py`, `tests/test_release_workflows.py`, `.github/workflows/ci.yml`, `.github/workflows/release-readiness.yml`, `AGENTS.md`, `.codex/skills/hygiene/SKILL.md`, and `tests/test_project_skills.py`. Do not change the historical q4xpcc brief. Add or change only directly evidenced CI action pins and compatible development/build bounds.

**Interfaces:** The live `status --json` report supplies the uv candidate, package/lock changes, `current_findings`, `pre_apply_blockers`, exact reviewed dirty paths, and `plan_sha256`; Steps 1–3 separately record the official CI-action inventory. The live apply invokes the Task 2 matrix and produces one report with commands, exit codes, hashes, and preserved failure paths.

- [ ] **Step 1: Inventory local targets.** Record `uv --version`, `[tool.uv].required-version` if present, all direct development requirements, `uv_build`, lock graph, `.python-version`, Python classifiers, and both workflows' `setup-uv` pins. Record the exact starting bytes or hashes of managed files.
- [ ] **Step 2: Inventory official package evidence.** Run the read-only status command and inspect the official PyPI/uv/OSV results for stable candidates, current yanks/advisories, compatibility, and constraints. Classify current-lock findings as remediation work. Missing official evidence or an incompatible uv target is a pre-apply blocker.
- [ ] **Step 3: Inventory CI tools.** Read current `setup-uv` and `actions/*` references plus `.pre-commit-config.yaml`. Check current compatible action releases and release notes in their official GitHub repositories. Record justified action changes and unavailable evidence; leave local-only pre-commit hooks alone. Read the newest uv release notes for compatibility with this project and the supported Python range; ambiguous or incompatible evidence blocks the reviewed candidate.
- [ ] **Step 4: Write Python-policy tests.** In `tests/test_project_metadata.py` assert `requires-python == ">=3.12,<3.15"`, all three classifiers, and empty runtime dependencies. Add a wrong-range fixture to `tests/test_release_tool.py`; update only the valid/hostile fixtures' `Requires-Python` values to the approved range.
- [ ] **Step 5: Write workflow-policy tests.** In `tests/test_release_workflows.py` derive the expected uv version from `[tool.uv].required-version` and require each workflow's setup step to use it. Retain source and installed-wheel jobs for 3.12, 3.13, and 3.14. A duplicate or stale setup pin must fail.
- [ ] **Step 6: Write guidance tests.** In `tests/test_project_skills.py` assert that `AGENTS.md` routes explicit complete refresh requests to canonical `gzs-update-dependencies` and `tools/dependency_refresh.py`, while the hygiene skill remains offline. Require no repository-local copy of a canonical `gzs-*` skill.
- [ ] **Step 7: Prove policy red.** Run `uv run --frozen python -m unittest tests.test_project_metadata tests.test_release_tool tests.test_release_workflows tests.test_project_skills -v`. Require only the expected old Python/uv/guidance policy assertions to fail; diagnose unrelated failures before proceeding.
- [ ] **Step 8: Update release metadata validation.** In `tools/release.py`, read the project's `requires-python` from `pyproject.toml` with `tomllib`; require exactly `>=3.12,<3.15` and compare source, wheel, and sdist metadata to that value. Keep hostile metadata fixtures rejecting a different range. This step can remain red until apply changes project metadata. The expected value must come from the validated project metadata:

  ~~~python
  expected_python = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["requires-python"]
  if expected_python != ">=3.12,<3.15":
      raise ReleaseError("unexpected Requires-Python policy")
  ~~~
- [ ] **Step 9: Update explicit-refresh guidance.** Add one project command with separate `status` and `apply --plan-sha256` usage to `AGENTS.md`. Keep `.codex/skills/hygiene/SKILL.md` offline; point complete network-aware refresh requests to the canonical workflow and project command. Do not create a new local canonical skill.
- [ ] **Step 10: Update justified CI action releases.** If Step 3 found compatible newer `actions/*` or `setup-uv` action revisions, edit only their two workflow references and matching tests. Leave the uv executable `version:` values for guarded apply; include every manual action edit in the reviewed dirty scope. If no justified revision exists, record the decision without editing.
- [ ] **Step 11: Stage the new implementation files for full hook coverage.** After focused tests are green and before capturing the status token, run `git add -- tools/dependency_sources.py tools/dependency_refresh.py tools/dependency_matrix.py tests/test_dependency_sources.py tests/test_dependency_refresh.py tests/test_dependency_matrix.py`. Inspect `git diff --cached --name-only`; require exactly these six new paths. This is an operator step so hygiene's `pre-commit --all-files` sees them; the refresh adapter itself never stages. Any later edit to a staged path requires restaging and a new status token.
- [ ] **Step 12: Capture a reviewed status token.** Run `.venv/Scripts/python.exe tools/dependency_refresh.py status --json` on Windows or `.venv/bin/python tools/dependency_refresh.py status --json` on POSIX. Review proposed versions, files, commands, `current_findings`, `pre_apply_blockers`, digest, and exact staged/dirty-path hashes against Steps 1–3. Stop for pre-apply blockers. Preserve current-lock findings in the approved report so apply can remediate them.
- [ ] **Step 13: Run the reviewed apply.** Call the project environment's Python directly with `tools/dependency_refresh.py apply --plan-sha256` followed by the actual Step 12 digest and one `--review-scope` per exact reviewed dirty path. Avoid wrapping apply in `uv run` because its parent uv process can interfere with self-update on Windows. If uv has a different owning installer, update it through that verified owner as a separate operator action, then rerun status and use the new digest.
- [ ] **Step 14: Inspect the refreshed graph.** Check `uv lock --check` and `uv sync --all-groups --locked`. Compare before/after uv version, Python metadata, compatible development/build bounds, full lock graph, and workflow pins. Review the second status report: no yanked/advisory item may remain, and every remaining outdated/constrained item must carry an explicit compatible explanation. Preserve any failed command and changed files for diagnosis.
- [ ] **Step 15: Prove policy tests green.** Run `uv run --frozen python -m unittest tests.test_project_metadata tests.test_release_tool tests.test_release_workflows tests.test_project_skills -v`. The apply result must also contain focused dependency tests, one hygiene pass that included the staged new files, and the 3.12–3.14 source/installed-wheel matrix with exact artifacts.
- [ ] **Step 16: Inspect and commit the implementation.** Run `git diff --check` and inspect the complete source/status/apply/matrix/`pyproject.toml`/`uv.lock`/CI/test/guidance diff. Confirm no runtime dependency or governance-tool payload leak. Record official source links, before/after versions, constraints, commands, artifacts, hashes, and any justified CI action revision. Stage the final reviewed Task 1–3 file bytes, inspect `git diff --cached`, and commit that coherent implementation scope; its configured hook runs the full quality suite. No push or release.

### Task 4: Close the reviewed child and preserve evidence

**Files:** Modify this plan and `BACKLOG.md` via guarded CLI in the feature worktree; update the existing dirty `HANDOFF.md` only in the main checkout after integration. Create `completion.md`, `review.md`, and `gate-1.md` through `gate-4.md` under `.superpowers/sdd/2026-09-19-t2-2-dependency-toolchain-refresh/`. Update current-state `unittest` expectations only if the real lifecycle state makes them fail.

**Interfaces:** A clean `T2.2` closeout is `verified` at 4/4 with committed accepted review and gate links. `T3.1` remains independent and `B1.1` waits only for `T2.2`. I1.0 q4xpcc planning remains eligible; no adoption or release state changes.

- [ ] **Step 1: Verify the unchanged candidate.** Run the full targeted dependency/source/matrix/metadata/workflow/skill `unittest` set. Use the real Task 3 apply result for hygiene and the 3.12–3.14 matrix. Rerun hygiene only if implementation changed after that result; rerun the matrix only if later edits affect metadata, dependencies, wheel contents, or verification behavior. Do not add a standalone quality run before hygiene.
- [ ] **Step 2: Check artifacts and limits.** Require the exact wheel/sdist inventory, three-version source and installed-wheel evidence, and absence of dependency-refresh tooling from both payloads. Record any unexercised operating system and preserve failed artifacts for diagnosis.
- [ ] **Step 3: Write completion evidence.** Create `completion.md` with `Child: T2.2`, `Kind: verification`, `Result: passed`, date, revision, exact commands/results, official source links, before/after versions and constraints, artifact hashes, and no-release statement. Set this plan to completed only when those facts exist.
- [ ] **Step 4: Advance to implemented.** Dry-run `transition T2.2 implemented --expect in_progress`, inspect its candidate audit, apply with its printed digest, and run backlog `audit`.
- [ ] **Step 5: Request independent code review.** Invoke `superpowers:requesting-code-review` against the approved design, this plan, all four gates, source trust, stale-scope behavior, matrix evidence, runtime boundary, and release boundary. Resolve findings and rerun only checks affected by those changes.
- [ ] **Step 6: Accept the review.** Create `review.md` with the reviewed revision, findings, resolutions, and acceptance. Dry-run/apply `transition T2.2 reviewed --expect implemented --review .superpowers/sdd/2026-09-19-t2-2-dependency-toolchain-refresh/review.md` with the printed digest; run backlog `audit`.
- [ ] **Step 7: Write gate 1 and 2 evidence.** Create `gate-1.md` for read-only human/JSON status and official evidence. Create `gate-2.md` for exact uv/Python/development/lock changes plus stale, resolver, and after-refresh advisory/yank tests. Give each file `Child: T2.2`, its gate ordinal, `Kind: verification`, `Result: passed`, date, subject, and exact commands or artifacts.
- [ ] **Step 8: Write gate 3 and 4 evidence.** Create `gate-3.md` for targeted tests, one full hygiene run, the source/installed-wheel matrix, and exact artifact inventory. Create `gate-4.md` for code/payload inventory and absence of Superpowers, deployment, Git sync, or release mutation paths. Use the same evidence fields as Step 7.
- [ ] **Step 9: Link the four gates.** For each gate in order, dry-run `record-gate`, inspect its candidate audit, then apply with its printed digest. Run backlog `audit` after the fourth link; require 4/4 and accepted review.
- [ ] **Step 10: Advance to verified.** Dry-run/apply `transition T2.2 verified --expect reviewed` after all four gate links and accepted review exist. Run backlog `audit` and `next`; require no findings and record the observed next local child.
- [ ] **Step 11: Commit the complete closeout.** Commit this completed plan, `completion.md`, accepted `review.md`, four gate files, and every Task 4 `BACKLOG.md` transition including `verified` in one coherent closeout commit. Run `git status --short` afterward; require no uncommitted branch changes. Its configured hook runs the full quality suite.
- [ ] **Step 12: Integrate locally and reconcile handoff.** Invoke `superpowers:verification-before-completion` and `superpowers:finishing-a-development-branch`. From `main`, use `git merge --ff-only` for the verified branch while preserving the pre-existing uncommitted `HANDOFF.md`; if main diverged, reconcile the branch in its isolated worktree and rerun affected/full gates before retrying. Never overwrite or stage the dirty main handoff. Verify `main` now names the exact already-tested branch commit and tree, run backlog `audit` and `uv run --frozen python -m unittest tests.test_dependency_sources tests.test_dependency_refresh tests.test_dependency_matrix tests.test_project_metadata tests.test_release_tool tests.test_release_workflows tests.test_project_skills -v`, then update that existing main-checkout `HANDOFF.md` with observed T2.2 evidence, next child, and continuing q4xpcc I1.0 priority without absorbing its prior dirty content into a feature commit. If merge resolution changes the tested tree, run the full quality gate on that new tree before claiming completion. Keep runtime adoption gated. Remove the worktree and delete its temporary branch. Do not push, tag, publish, or release.

## Plan audit

| Declared intent to scoped work | Result | Evidence |
| --- | --- | --- |
| Write one T2.2 plan from the approved adapter design, without implementation | Aligned | Local-workflow design:183-230 and BACKLOG.md:503-515; this draft Tasks 0-4 |
| Keep q4xpcc, runtime code, Git sync, and release outside the child | Aligned | Local-workflow design:108-126, 183-230; Global Constraints above |

| Scoped requirement to execution plan | Result | Evidence |
| --- | --- | --- |
| Read-only official status and deterministic human/JSON report | Aligned | Design:190-205; Task 1 Steps 10–17 |
| Guarded uv/Python/development/lock update and failures | Aligned | Design:206-229; Task 2 Steps 1–16 and Task 3 Steps 12–16 |
| Current-lock findings remain remediable; post-refresh findings block completion | Aligned | Design:210-229, 368-374; Task 1 Steps 11–14, Task 2 Steps 13–16 |
| Incompatible newest uv retains the verified pin and blocks apply | Aligned | Design:203-208, 309-312; Task 1 Steps 10–14 and Task 3 Step 3 |
| Universal lock entries receive outdated classifications | Aligned | Design:198-200; Task 1 Steps 10 and 13, Task 2 Step 15 |
| Targeted tests, full hygiene, 3.12-3.14 source/installed wheel, exact artifacts | Aligned | Design:307-313, 366-377; Task 2 Steps 17–25 and Task 4 Steps 1–2 |
| No external Superpowers or release mutation path | Aligned | Design:118-126, 223-229; Global Constraints and Task 4 Gate 4 |
| Concrete test fixtures and code for every implementation step | Missing | Superpowers writing-plans:131-139; several Task 1–3 test/code steps remain prose-only |

**Verdict:** FAIL for execution readiness. Intent and scoped requirements align, and the commit/verification cadence is now explicit, but the remaining prose-only test and code steps need executable examples before approval. This draft has no implementation authority.

## Self-review checklist for the draft

- [x] Every T2.2 design bullet and all four backlog gates map to a task, test, and observed closeout command.
- [x] Status and apply are distinct; status is read-only, while apply is digest-pinned and fails before mutation on stale or unreviewed scope. Current-lock findings remain eligible for remediation; unresolved findings after refresh block successful completion.
- [x] Official package/advisory evidence, uv ownership, compatible declarations, complete lock, Python metadata, CI pins, and artifact boundaries have no unassigned owner.
- [x] No step uses a test framework other than unittest, changes runtime code, edits q4xpcc, mutates Superpowers, or assumes push/release authority.
- [ ] Add exact fixtures and code examples to the remaining prose-only test and implementation steps before requesting approval.
