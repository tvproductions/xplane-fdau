# T2.1 Repository Hygiene and Fresh Artifact Verification Implementation Plan

- **Governance:** active
- **Status:** completed
- **Date:** 2026-09-19
- **Roadmap child:** `T2.1`
- **Source specification:** `docs/superpowers/specs/2026-08-15-xplane-fdau-local-workflow-skills-design.md`
- **Approval:** 2026-09-19 — Jeff / tvproductions
- **Completion evidence:** `.superpowers/sdd/2026-09-19-t2-1-repository-hygiene-artifact-verification/completion.md`

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the project hygiene command run the complete offline repository gate and validate one fresh wheel and sdist pair on every invocation.

**Architecture:** Extend the existing `.codex/skills/hygiene/scripts/hygiene.py` adapter beneath canonical `gzs-repository-hygiene`; keep `tools/quality.py` and `tools/release.py` as the quality and exact-artifact authorities. Run strict documentation and all pre-commit hooks before building into a uniquely created operating-system temporary directory. Preserve that directory after any failure and remove it only after the final repository check succeeds and the deletion target is verified.

**Tech Stack:** Python 3.12 standard library, `unittest`, uv, Twine, pre-commit, MkDocs, Git, existing release validator.

**Spec:** `docs/superpowers/specs/2026-08-15-xplane-fdau-local-workflow-skills-design.md` (including the approved 2026-09-19 single-pass verification correction).

## Global Constraints

- Implement only `T2.1`. `T2.2`, `T3.1`, `B1.1`, canonical FDAU runtime behavior, q4xpcc, and external adapters remain outside this plan.
- `ROADMAP.md` owns dependencies; `BACKLOG.md` alone owns mutable delivery state. Follow its dry-run-first controlled mutation workflow for lifecycle and gate evidence.
- Every hygiene invocation checks status and ignored/generated scope, offline lock, strict backlog audit, strict MkDocs, all pre-commit hooks once, a fresh wheel/sdist pair, strict metadata, exact artifact contents, governance exclusion, and final status, in that order. Stop at the first blocking failure.
- The `quality-check` pre-commit hook is the only invocation of `tools/quality.py check` inside routine hygiene. Do not add a preceding standalone full-suite run. `tools/quality.py test` remains available separately.
- Routine hygiene makes no network inquiry or tracked repository mutation. The existing `--dependencies` probe remains explicit and separate; T2.2 owns complete dependency refresh.
- Use `unittest` only. Runtime package code remains pure Python and standard-library-only. The hygiene tool and Twine remain development-only and absent from both distribution artifacts.
- A normal hygiene run does not run the Python 3.12–3.14 source/installed-wheel matrix. Run that matrix at T2.1 closeout under the project release workflow.
- Version `0.1.0` remains unreleased. No Git sync, push, tag, package publication, GitHub release, or q4xpcc edit is authorized by this plan.
- On Windows, macOS, and Linux, use `Path` for filesystem paths, subprocess argument tuples with `shell=False`, UTF-8 text, explicit resource closure, and checked temporary cleanup.

## File responsibilities

| File | Responsibility |
| --- | --- |
| `.codex/skills/hygiene/scripts/hygiene.py` | Ordered offline command adapter, command failure reports, fresh artifact directory lifecycle, final status |
| `tests/test_hygiene_tool.py` (new) | Injected runner/temp directory tests for order, offline scope, failure propagation, artifact naming, cleanup and preservation |
| `tests/test_project_skills.py` | Discovery, supporting-skill guidance, pre-commit quality-hook and governance-exclusion assertions |
| `pyproject.toml`, `uv.lock` | Lock Twine as a development tool so strict metadata checks run offline without an on-demand tool download |
| `.codex/skills/hygiene/SKILL.md`, `AGENTS.md` | Exact offline full-strength local command and reporting guidance beneath canonical `gzs-repository-hygiene` |
| `tests/test_release_tool.py` | Existing exact wheel/sdist validation and hostile governance-member cases; extend only if a missing artifact exclusion is demonstrated |
| `BACKLOG.md` | T2.1 plan link, lifecycle, review and five gate-evidence links through guarded state commands after approval and execution |
| `HANDOFF.md`, `tests/test_backlog_governance.py`, `tests/test_backlog_status_cli.py` | Reflect the verified T2.1 result and the next dependency-ready action at closeout |
| `.superpowers/sdd/2026-09-19-t2-1-repository-hygiene-artifact-verification/` | Task logs, independent review, completion and five gate receipts after implementation |

### Task 0: Establish the approved plan and active child

**Files:** Modify this plan, `BACKLOG.md` through the guarded backlog CLI, and current-state assertions in `tests/test_backlog_governance.py` and `tests/test_backlog_status_cli.py`. Do this only after the user approves the reviewed plan; do not begin Tasks 1–3 while this plan is draft. Every `transition`, `select`, `record-gate`, `audit`, and `next` below is a subcommand of `uv run python .codex/skills/backlog-status/scripts/backlog_status.py`.

- [x] **Step 1: Register approval and plan link.** Record the actual approval date and approver in this plan and change `Status` to `approved`. Run `transition T2.1 planned --expect specified --plan docs/superpowers/plans/2026-09-19-t2-1-repository-hygiene-artifact-verification.md` without `--apply`. Inspect its diff and candidate audit; repeat with the printed `--target-sha256` and `--apply`.
- [x] **Step 2: Select and start T2.1.** Dry-run/apply `select T2.1 --expect-current none`. Change this plan to `Status: in_progress`, then dry-run/apply `transition T2.1 in_progress --expect planned`. After each applied state change run backlog `audit` and `next`; require no findings and the expected T2.1 action. Update the current-repository tests to include this active plan and assert T2.1 `in_progress`/`execute_plan`; watch the former assertions fail first, then run `uv run python -m unittest tests.test_backlog_governance.GovernanceArtifactTests.test_active_artifact_assignments_match_current_roadmap_children tests.test_backlog_status_cli.BacklogStatusCliTests.test_current_repository_status_reports_human_and_json -v` to prove the new state. Run the complete quality gate and commit this plan, the coherent in-progress `BACKLOG.md`, and those two current-state tests before any implementation commit.

### Task 1: Complete the offline repository gate

**Files:** Modify `.codex/skills/hygiene/scripts/hygiene.py`, `tests/test_project_skills.py`; create `tests/test_hygiene_tool.py`.

**Interfaces:** Preserve `main(argv: Sequence[str] | None = None) -> int`, `run_local_hygiene(runner: Runner = subprocess.run) -> int`, and the explicit `--dependencies` mode. Task 2 adds temporary-directory and cleanup injection when it introduces artifacts.

- [x] **Step 1: Add failing command-order and no-network tests.** In `tests/test_hygiene_tool.py`, import the script with `importlib.util.spec_from_file_location` as the existing skill test does. Inject a runner that records `tuple(command)`, `cwd`, `env`, and `check`. Assert this ordered prefix:

  ```python
  expected = [
      ("git", "status", "--short", "--branch"),
      ("git", "status", "--short", "--branch", "--ignored=matching"),
      ("uv", "lock", "--check", "--offline"),
      ("uv", "run", "--offline", "--frozen", "python", ".codex/skills/backlog-status/scripts/backlog_status.py", "audit"),
      ("uv", "run", "--offline", "--frozen", "mkdocs", "build", "--strict"),
      ("uv", "run", "--offline", "--frozen", "python", "tools/quality.py", "pre-commit"),
  ]
  ```

  Assert every **direct hygiene subprocess** receives `cwd=ROOT`, `check=False`, `shell=False`, and child environment `UV_OFFLINE=1`. The injected runner cannot observe subprocesses later launched by pre-commit: separately inspect `.pre-commit-config.yaml` in `tests/test_project_skills.py` to require only local, `language: system` hooks, `uv run` entries, and exactly one `quality-check` hook. Task 3 runs the real pre-commit chain through an offline launcher so the inherited environment and local-hook configuration are exercised. Assert the prefix has no direct `tools/quality.py check`, `uv tree`, `git add`, `git commit`, or simulator command. Inject an `OSError` for a direct pre-artifact command; assert a nonzero result, the exact failed command and error, and no later calls. Update the existing `test_hygiene_audits_backlog_then_runs_one_quality_gate_through_pre_commit` expected commands to this prefix.

- [x] **Step 2: Prove RED.** Run `uv run python -m unittest tests.test_hygiene_tool tests.test_project_skills -v`. Expect the new order and offline-environment assertions to fail while existing skill discovery passes.

- [x] **Step 3: Implement the ordered prefix and failure report.** Keep `LOCAL_COMMANDS` as immutable argument tuples. Add the ignored-status and MkDocs commands above, change existing `uv run` calls to `--offline --frozen`, and use this command boundary. Keep `audit_dependencies` only behind `--dependencies`:

  ```python
  def run_command(command: tuple[str, ...], runner: Runner) -> int:
      print("+ " + " ".join(command), flush=True)
      try:
          result = runner(command, cwd=ROOT, check=False, shell=False, env={**os.environ, "UV_OFFLINE": "1"})
      except OSError as error:
          print(f"hygiene failed: {' '.join(command)} (could not start: {error})", file=sys.stderr)
          return 1
      if result.returncode != 0:
          print(f"hygiene failed: {' '.join(command)} (exit {result.returncode})", file=sys.stderr)
      return result.returncode

  for command in LOCAL_COMMANDS:
      code = run_command(command, runner)
      if code != 0:
          return code
  ```

  Preserve `run_local_hygiene` as the entry point; Task 2 appends its artifact and final-status phases. Do not catch a failed command and continue.

- [x] **Step 4: Verify the gate and commit.** Run:

  ```powershell
  uv run python -m unittest tests.test_hygiene_tool tests.test_project_skills -v
  uv run ruff check .codex/skills/hygiene/scripts/hygiene.py tests/test_hygiene_tool.py tests/test_project_skills.py
  uv run ruff format --check .codex/skills/hygiene/scripts/hygiene.py tests/test_hygiene_tool.py tests/test_project_skills.py
  uv run ty check
  git diff --check
  git add .codex/skills/hygiene/scripts/hygiene.py tests/test_hygiene_tool.py tests/test_project_skills.py
  git commit -m "feat: run complete offline hygiene gates"
  ```

  Expect all commands to exit zero. `ruff` may explicitly name the script because `.codex` is excluded from its default tree scan.

### Task 2: Build, validate and safely dispose of one fresh artifact pair

**Files:** Modify `.codex/skills/hygiene/scripts/hygiene.py`, `tests/test_hygiene_tool.py`, `pyproject.toml`, `uv.lock`; modify `tests/test_release_tool.py` only if Task 2 RED reveals an exclusion gap.

**Interfaces:** Produce an `ArtifactDirectory` ownership record holding the exact created `Path`, resolved parent `Path`, and `os.stat_result` identities of both, captured immediately after `tempfile.mkdtemp(prefix="xplane-fdau-hygiene-", dir=parent)`. Implement `create_artifact_dir() -> ArtifactDirectory`, `artifact_commands(directory: Path, version: str) -> tuple[tuple[str, ...], ...]`, and `verified_cleanup_target(owned: ArtifactDirectory) -> Path`. The hygiene runner accepts injected directory creation and deletion functions for deterministic tests.

- [x] **Step 1: Write failing artifact lifecycle tests.** Use `TemporaryDirectory` in `tests/test_hygiene_tool.py` for test-owned fixtures and inject a path outside the test checkout as the hygiene-created directory. Read `version` from `pyproject.toml` with `tomllib`; for each successful call, require one distinct `owned.path` and exactly these artifact command tuples in order:

  ```python
  directory = owned.path
  wheel = directory / f"xplane_fdau-{version}-py3-none-any.whl"
  sdist = directory / f"xplane_fdau-{version}.tar.gz"
  expected = (
      ("uv", "build", "--offline", "--no-sources", "--out-dir", str(directory)),
      ("uv", "run", "--offline", "--frozen", "twine", "check", "--strict", str(wheel), str(sdist)),
      ("uv", "run", "--offline", "--frozen", "python", "tools/release.py", "check-dist", str(directory)),
  )
  ```

  Assert the final two status commands execute before cleanup.

- [x] **Step 2: Write failing preservation and cleanup-safety tests.** For each of build, Twine, release-validator, and final-status failure, inject a runner that returns `7`, then one that raises `OSError`; assert immediate nonzero return, the exact failed command and error, no later command or cleanup, and stderr naming the exact preserved directory. On success, assert cleanup receives the exact created path once. Use a `TemporaryDirectory` **outside the checkout** containing a separate, test-owned parent and created child; inject an `ArtifactDirectory` record with their captured identities. Move or replace only these fixture-owned paths, never `tempfile.gettempdir()` or another shared OS temp parent. Test checkout containment, symlink and Windows junction predicates, a renamed child, a same-path replacement child, a changed resolved parent, and a same-path replacement parent; require refusal before deletion and assert both moved originals and replacements survive. Exercise real links only where creation is permitted; use `unittest.mock` for link predicates otherwise and record the unexercised host capability. Inject directory-creation, post-creation identity capture, and cleanup `OSError` failures; assert a nonzero result and exact path/error report when a path was created, with no false cleanup success. Close handles before cleanup and never use `ignore_errors=True`.

- [x] **Step 3: Prove RED.** Run `uv run python -m unittest tests.test_hygiene_tool -v`. Expect missing artifact command and cleanup interfaces to fail.

- [x] **Step 4: Add the offline metadata tool.** Add compatible `twine>=7.0.0` to the `dev` dependency group in `pyproject.toml`, refresh `uv.lock` for that single addition, and check its declaration and lock diff. Do not refresh unrelated packages. Use `uv run --offline --frozen twine check --strict` during routine hygiene; do not use `uv tool run`, which can require an uncached tool download.

- [x] **Step 5: Implement the artifact phase.** Use the following directory and command construction. Read `version` from `tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]` and require a nonempty string. The two final status commands are the same tuples used at the start:

  ```python
  @dataclass(frozen=True, slots=True)
  class ArtifactDirectory:
      path: Path
      parent: Path
      directory_identity: os.stat_result
      parent_identity: os.stat_result

  def create_artifact_dir() -> ArtifactDirectory:
      parent = Path(tempfile.gettempdir()).resolve()
      root = ROOT.resolve()
      if parent == root or root in parent.parents:
          raise ValueError(f"temporary directory is inside the checkout: {parent}")
      parent_identity = parent.stat(follow_symlinks=False)
      created = Path(tempfile.mkdtemp(prefix="xplane-fdau-hygiene-", dir=parent))
      try:
          directory_identity = created.stat(follow_symlinks=False)
      except OSError as error:
          raise RuntimeError(f"artifact directory created but not inspected; preserved {created}: {error}") from error
      return ArtifactDirectory(created, parent, directory_identity, parent_identity)

  def artifact_commands(directory: Path, version: str) -> tuple[tuple[str, ...], ...]:
      wheel = directory / f"xplane_fdau-{version}-py3-none-any.whl"
      sdist = directory / f"xplane_fdau-{version}.tar.gz"
      return (
          ("uv", "build", "--offline", "--no-sources", "--out-dir", str(directory)),
          ("uv", "run", "--offline", "--frozen", "twine", "check", "--strict", str(wheel), str(sdist)),
          ("uv", "run", "--offline", "--frozen", "python", "tools/release.py", "check-dist", str(directory)),
      )
  ```

  Keep the ownership record from creation through cleanup. If directory creation or identity capture raises, report the exception (including the created path when one exists) and return nonzero without deletion. Run the three artifact commands and final normal/ignored Git status through `run_command`; its nonzero return for either an exit code or `OSError` stops the sequence and reports the exact preserved path. Cleanup only after all commands succeed: `verified_cleanup_target(owned: ArtifactDirectory) -> Path` must reject absent or renamed paths, changed resolved paths or parents, checkout containment, and `Path.is_symlink()` or `Path.is_junction()` for the directory and parent. Use `stat(follow_symlinks=False)` and `stat.S_ISDIR` for both, and require `os.path.samestat` against both captured identities immediately before deletion; a same-path replacement must fail. Then call injected `cleanup(target)` (production default `shutil.rmtree`). Report cleanup failure and the exact remaining path; never use `ignore_errors=True`.

- [x] **Step 6: Verify and commit.** Run:

  ```powershell
  uv run python -m unittest tests.test_hygiene_tool tests.test_project_skills tests.test_release_tool -v
  uv run ruff check .codex/skills/hygiene/scripts/hygiene.py tests/test_hygiene_tool.py tests/test_project_skills.py
  uv run ruff format --check .codex/skills/hygiene/scripts/hygiene.py tests/test_hygiene_tool.py tests/test_project_skills.py
  uv run ty check
  uv lock --check --offline
  git diff --check
  git add .codex/skills/hygiene/scripts/hygiene.py tests/test_hygiene_tool.py tests/test_project_skills.py tests/test_release_tool.py pyproject.toml uv.lock
  git commit -m "feat: validate fresh hygiene artifacts offline"
  ```

  Expect all commands to exit zero. Confirm `git show --stat --oneline HEAD` contains no runtime package file.

### Task 3: Integrate the project adapter and prove the real repository run

**Files:** Modify `.codex/skills/hygiene/SKILL.md`, `AGENTS.md`, and `tests/test_project_skills.py`; create gate receipts under `.superpowers/sdd/2026-09-19-t2-1-repository-hygiene-artifact-verification/` during closeout.

**Interfaces:** Document `uv run --offline --frozen python .codex/skills/hygiene/scripts/hygiene.py` as the public project command, so the outer uv invocation and every command launched by the script are offline. Canonical `gzs-repository-hygiene` remains the portable workflow owner. Keep `code-quality`, `documentation`, and `release` as focused supporting skills.

- [x] **Step 1: Add a failing guidance assertion.** In `tests/test_project_skills.py`, assert the hygiene skill and `AGENTS.md` agree on the exact offline/frozen project command. Require the skill to name canonical `gzs-repository-hygiene`, strict MkDocs, the single pre-commit quality hook, one fresh external temporary artifact pair, strict Twine and `tools/release.py check-dist`, safe successful cleanup, failed-artifact preservation, offline routine behavior, and the separate closeout Python matrix. Assert it does not claim to implement `gzs-update-dependencies` or authorize Git sync/release.

- [x] **Step 2: Prove RED.** Run `uv run python -m unittest tests.test_project_skills -v`; expect the new guidance assertion to fail.

- [x] **Step 3: Update the skill and entry guidance.** Document the exact offline/frozen invocation and command order, the optional `--dependencies` network probe, temporary artifact handling, and retained supporting skills in `.codex/skills/hygiene/SKILL.md`. Update the current hygiene command in `AGENTS.md` to the same offline/frozen invocation and keep its explicit-only Git-sync and release boundaries. Assert these two command references agree in `tests/test_project_skills.py`. State that the full 3.12–3.14 installed-wheel matrix belongs to child closeout rather than routine hygiene. Do not create another local `gzs-*` skill.

- [x] **Step 4: Verify the integration.** Run from the worktree root:

  ```powershell
  uv run python -m unittest tests.test_hygiene_tool tests.test_project_skills -v
  uv run --offline --frozen python .codex/skills/hygiene/scripts/hygiene.py
  git diff --check
  git status --short --branch
  ```

  Capture `git status --porcelain=v1 --untracked-files=all` before and after the hygiene command and require identical output, allowing only ignored caches outside that tracked scope. Expect the command to report the one external directory, one wheel and sdist, successful Twine and exact release validation, and successful cleanup. If it fails, preserve and report the artifact directory, correct the evidenced cause test-first, and repeat on the changed tree.

- [x] **Step 5: Commit guidance.** Run `git add .codex/skills/hygiene/SKILL.md AGENTS.md tests/test_project_skills.py` and `git commit -m "docs: route full hygiene through project adapter"`. Task 4 requests independent review of the committed implementation.

### Task 4: Close T2.1 with distinct verification evidence

**Files:** Modify this plan, `BACKLOG.md` only through the guarded backlog CLI, `HANDOFF.md`, and any current-state assertions in `tests/test_backlog_governance.py` and `tests/test_backlog_status_cli.py`; create `completion.md`, `review.md`, and `gate-1.md` through `gate-5.md` under `.superpowers/sdd/2026-09-19-t2-1-repository-hygiene-artifact-verification/`.

**Interfaces:** Produce a reviewed, verified `T2.1` with 5/5 linked acceptance gates and no selected child. Report `T2.2` or `T3.1` according to the actual next-action result; leave both as separate specified peers. No release state changes. For every `select`, `transition`, and `record-gate` below, run the full command without `--apply`, inspect its diff and candidate audit, then repeat that command with its printed `--target-sha256` and `--apply`. Run backlog `audit` and `next` after each applied mutation and stop on a finding.

- [x] **Step 1: Verify the implemented candidate and preserve exact results.** Run `uv run --offline --frozen python .codex/skills/hygiene/scripts/hygiene.py` once and `git diff --check`. Hygiene supplies quality, strict MkDocs, one fresh artifact pair, and safe cleanup. For the separate closeout source/installed-wheel matrix, run this PowerShell script from the worktree root; stop on any failure and preserve both external directories for diagnosis:

  ```powershell
  $ErrorActionPreference = 'Stop'
  function Assert-LastExit([string]$label) {
      if ($LASTEXITCODE -ne 0) { throw "$label failed with exit $LASTEXITCODE" }
  }
  $sourceRoot = (Resolve-Path .).Path
  $matrixDir = uv run --offline --frozen python -c "from pathlib import Path; import tempfile; root=Path.cwd().resolve(); parent=Path(tempfile.gettempdir()).resolve(); assert root != parent and root not in parent.parents; print(tempfile.mkdtemp(prefix='xplane-fdau-t2-1-matrix-', dir=parent))"
  Assert-LastExit 'create matrix artifact directory'
  $venvRoot = uv run --offline --frozen python -c "from pathlib import Path; import tempfile; root=Path.cwd().resolve(); parent=Path(tempfile.gettempdir()).resolve(); assert root != parent and root not in parent.parents; print(tempfile.mkdtemp(prefix='xplane-fdau-t2-1-venvs-', dir=parent))"
  Assert-LastExit 'create matrix environment directory'
  $wheel = Join-Path $matrixDir 'xplane_fdau-0.1.0-py3-none-any.whl'
  $sdist = Join-Path $matrixDir 'xplane_fdau-0.1.0.tar.gz'
  $smoke = Join-Path $sourceRoot 'tools/installed_smoke.py'
  uv build --offline --no-sources --out-dir $matrixDir
  Assert-LastExit 'build matrix artifact pair'
  uv run --offline --frozen twine check --strict $wheel $sdist
  Assert-LastExit 'strict Twine check'
  uv run --offline --frozen python tools/release.py check-dist $matrixDir
  Assert-LastExit 'exact distribution check'
  Get-FileHash -Algorithm SHA256 -Path $wheel, $sdist
  foreach ($pyVersion in @('3.12', '3.13', '3.14')) {
      uv run --frozen --python $pyVersion python -m unittest discover -q
      Assert-LastExit "source unittest $pyVersion"
      $venvPath = Join-Path $venvRoot ('py' + $pyVersion.Replace('.', ''))
      uv venv --python $pyVersion $venvPath
      Assert-LastExit "create venv $pyVersion"
      $venvPython = if ([System.IO.Path]::DirectorySeparatorChar -eq '\') { Join-Path $venvPath 'Scripts/python.exe' } else { Join-Path $venvPath 'bin/python' }
      uv pip install --python $venvPython $wheel
      Assert-LastExit "install wheel $pyVersion"
      Push-Location -LiteralPath $matrixDir
      try {
          & $venvPython $smoke 0.1.0
          Assert-LastExit "installed smoke $pyVersion"
      } finally {
          Pop-Location
      }
  }
  ```

  Record commands, exit codes, artifact hashes, the hygiene and matrix artifact directory paths, matrix environment paths, hygiene cleanup result, Git state, and any unexercised operating system in the completion receipt. Do not add a separate `quality.py check` before hygiene: its `quality-check` hook supplies that run. Retain a failed artifact directory and report its exact path.

- [x] **Step 2: Commit completion and transition to implemented.** Create `completion.md` with `Child: T2.1`, `Gate: —`, `Kind: verification`, `Result: passed`, date, subject, implementation commit range, and Step 1 results. Set this plan's `Status` to `completed` and `Completion evidence` to that path. Stage the plan and receipt so the audit sees exact index/worktree bytes. Dry-run/apply `transition T2.1 implemented --expect in_progress`; require no findings, then commit the plan, receipt, and `BACKLOG.md` together.

- [x] **Step 3: Obtain and commit accepted independent review.** Invoke `superpowers:requesting-code-review` on the committed implementation against the approved T2.1 specification, this plan, the five backlog gates, offline/no-mutation behavior, artifact ownership and exact contents, cross-platform paths, runtime boundary, and release prohibition. Record findings and disposition in `review.md` with `Child: T2.1`, `Gate: —`, `Kind: review`, `Result: accepted`, date, and subject only after all load-bearing findings are resolved. Use `superpowers:receiving-code-review` and failing `unittest` first for accepted corrections; rerun Step 1 on any changed artifact, command, package, or test behavior, update and commit the completion receipt with the new results, and request rereview. Stage the accepted receipt, dry-run/apply `transition T2.1 reviewed --expect implemented --review .superpowers/sdd/2026-09-19-t2-1-repository-hygiene-artifact-verification/review.md`, audit, and commit the receipt with `BACKLOG.md`.

- [x] **Step 4: Create and link five gate receipts.** Use `Child: T2.1`, the matching gate ordinal, `Kind: verification`, `Result: passed`, date, and subject in each `gate-N.md`. Cite exact tests, command output, observed revision, artifact hashes, review result, and unexercised platforms where relevant:

  | Gate | Subject | Required proof |
  | --- | --- | --- |
  | 1 | Complete deterministic offline hygiene gate | Ordered status/ignored status, offline lock, strict backlog audit, one quality hook, strict MkDocs, all pre-commit hooks, fail-fast tests, and full-strength integration |
  | 2 | One fresh exact wheel and sdist | Distinct external directory per run, exact names and strict Twine, `check-dist` metadata/member/payload/governance-exclusion checks, and closeout hashes |
  | 3 | Safe cleanup and failure preservation | Success removal, per-phase failure preservation and exact path, same-path directory/parent replacement refusal, symlink/junction and checkout containment refusal |
  | 4 | Offline scope and supporting skills | No implicit network/mutation/matrix in routine hygiene, explicit dependency probe, focused adapter guidance, and unchanged runtime package |
  | 5 | Tests, integration, artifacts, and review | `unittest`, real current-repository hygiene, separate 3.12–3.14 source/installed-wheel matrix, accepted independent review, and unchanged release authorization |

  Stage all five receipts before linking them. Run each of the following full commands first as a dry run, inspect its diff and audit, then rerun it with the printed `--target-sha256` and `--apply`; audit after each apply:

  ```powershell
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py record-gate T2.1 1 --expect-open --evidence .superpowers/sdd/2026-09-19-t2-1-repository-hygiene-artifact-verification/gate-1.md
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py record-gate T2.1 2 --expect-open --evidence .superpowers/sdd/2026-09-19-t2-1-repository-hygiene-artifact-verification/gate-2.md
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py record-gate T2.1 3 --expect-open --evidence .superpowers/sdd/2026-09-19-t2-1-repository-hygiene-artifact-verification/gate-3.md
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py record-gate T2.1 4 --expect-open --evidence .superpowers/sdd/2026-09-19-t2-1-repository-hygiene-artifact-verification/gate-4.md
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py record-gate T2.1 5 --expect-open --evidence .superpowers/sdd/2026-09-19-t2-1-repository-hygiene-artifact-verification/gate-5.md
  ```

  Confirm the inventory row reaches 5/5, and commit the five receipts with the corresponding `BACKLOG.md` changes. A `verified` transition is premature until these exact receipt bytes are in `HEAD`.

- [x] **Step 5: Transition from committed evidence and update the handoff.** With completion, review, and all five gate receipts in `HEAD`, dry-run/apply `transition T2.1 verified --expect reviewed`, then dry-run/apply `select none --expect-current T2.1`. Update `HANDOFF.md` to state T2.1 is verified at 5/5 and direct readers to the live audit/next result for the next child. Update any current-state tests to match the verified T2.1 and actual next recommendation. Keep `BACKLOG.md` authoritative; do not edit it by hand.

- [x] **Step 6: Run the final gate on the closeout candidate and commit.** Run from the worktree root:

  ```powershell
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py audit
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py status --json
  uv run python .codex/skills/backlog-status/scripts/backlog_status.py next
  uv run python -m unittest tests.test_backlog_governance tests.test_backlog_status_cli tests.test_hygiene_tool tests.test_project_skills tests.test_release_tool -v
  uv run --offline --frozen python .codex/skills/hygiene/scripts/hygiene.py
  git diff --check
  git status --short --branch
  ```

  Require no audit findings, `T2.1` verified at 5/5 and unselected, the actual dependency-ready recommendation, a complete offline hygiene pass on the final tree, and no release or external-repository action. Stage and commit `BACKLOG.md`, `HANDOFF.md`, and any changed current-state tests. Confirm a clean worktree, rerun `audit` and `next` on `HEAD`, and use `superpowers:verification-before-completion`.

- [ ] **Step 7: Finish the temporary branch.** Inspect the commit range and invoke `superpowers:finishing-a-development-branch`. After the user selects local integration, merge to `main`, verify the merged result with the full hygiene command and backlog audit/next, remove the worktree, and delete the temporary branch. Do not push, tag, publish, or release as part of this child.

## Plan self-review

- Task 0 establishes approved/in-progress governance before Tasks 1–3; every T2.1 acceptance gate maps to Tasks 1–4: ordered offline gate, fresh exact artifacts, cleanup/preservation, supporting skills/no implicit network, and full closeout/review.
- The September 19 single-pass correction is explicit in Tasks 1, 3, and 4. Full-suite coverage runs through one `quality-check` pre-commit hook per routine hygiene invocation.
- `T2.2` dependency refresh, `T3.1` Git sync, and `B1.1` source migration are excluded from edits and completion claims.
