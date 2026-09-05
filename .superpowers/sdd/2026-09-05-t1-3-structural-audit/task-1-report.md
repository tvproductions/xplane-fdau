# Task 1 report: lossless audit input and isolated parse failures

## Outcome

Implemented the Task 1 loading boundary from base `e082ebd23ce307138d7552c6d7b8b4e84f48dfe5`.
The implementation and tests are commit `cbd58d45ce008188d59917d787397f5356d2d271`.
The strict `parse_repository()` and version-1 status/JSON behavior remain intact. The new
audit loader parses ROADMAP, BACKLOG, each sorted governance artifact, and the approved
policy independently, retaining successful inputs while recording typed findings and
invalid paths for failures.

The approved source-fact split was applied after self-review: strict Markdown parsing
remains in `backlog/parse.py`, while the new audit-only extraction lives in
`backlog/parse_sources.py`. This avoids further growth of the existing large parser and
does not create another authority or mutable model.

## Interfaces delivered

- `backlog/model.py` defines frozen `AuditLoad`, `AuditPolicy`,
  `HistoricalAdmission`, `AuditSources`, the three source-family containers, and
  explicit facts for selection, inventory outcomes, release-dashboard rows, gate
  headings, artifact metadata, design acceptance sections/statements, and managed
  release statements.
- `backlog/parse.py` retains `parse_repository(root) -> RepositorySnapshot`, exposes
  `parse_artifact(root, path, family)`, and gives every `MarkdownParseError` a stable
  dotted code plus optional node/gate context without changing its rendered text.
- `backlog/parse_sources.py` exposes `parse_roadmap_sources(path)`,
  `parse_backlog_sources(path, backlog)`, and
  `parse_artifact_sources(root, path, artifact)`. These preserve source order,
  duplicates, one-based lines, wrapped statement punctuation, and LF/CRLF behavior.
- `backlog/audit.py` exposes `load_audit(root) -> AuditLoad` and the shared
  `finding_key()`. Failed authorities receive empty typed report-shape values and are
  listed in `invalid_paths`; independent inputs continue loading.
- `backlog/policy.py` exposes `load_policy(root)`, typed `PolicyError`,
  `EvidenceSlot`, and `allowed_kinds()`. Policy loading requires approved/implemented
  metadata, a valid approval, and exact working-tree/index/HEAD byte identity. The
  historical admission table is parsed as policy data, with unique children/paths,
  contained plan paths, and lowercase 64-digit SHA-256 values.

## TDD evidence

RED was observed before implementation:

```text
uv run python -m unittest tests.test_backlog_status_model tests.test_backlog_status_parse tests.test_backlog_status_audit -v
exit 1: expected import failures for missing AuditLoad, parse_artifact, and backlog.audit

uv run python -m unittest tests.test_backlog_status_policy -v
exit 1: expected import failure for missing backlog.policy
```

The first GREEN attempt exposed two fixture defects: inherited Windows line-ending
conversion violated exact Git byte identity, and temporary Git object cleanup needed
read-only handling. The fixtures now disable `core.autocrlf`, write explicit UTF-8/LF,
and make read-only Git objects writable during deterministic cleanup.

Fresh focused GREEN evidence:

```text
uv run python -m unittest tests.test_backlog_status_model tests.test_backlog_status_parse tests.test_backlog_status_audit -v
Ran 37 tests — OK

uv run python -m unittest tests.test_backlog_status_policy -v
Ran 7 tests — OK

uv run python -m unittest tests.test_backlog_status_report -v
Ran 8 tests — OK
```

The malformed fixture-copy test reports both `ROADMAP.md:6` and the independent plan
failure at line 4, retains the valid backlog, emits no invented missing-child finding,
and marks only failed paths invalid. The current repository smoke check loaded 64
roadmap children, 64 backlog children, 7 active specifications, 4 active plans, and 33
design acceptance sections with zero load findings. The three historical plan bytes
matched every reviewed policy pin before policy implementation.

## Verification evidence

```text
$task1Files = @(
  '.codex/skills/backlog-status/scripts/backlog/model.py',
  '.codex/skills/backlog-status/scripts/backlog/parse.py',
  '.codex/skills/backlog-status/scripts/backlog/parse_sources.py',
  '.codex/skills/backlog-status/scripts/backlog/audit.py',
  '.codex/skills/backlog-status/scripts/backlog/policy.py',
  'tests/test_backlog_status_model.py',
  'tests/test_backlog_status_parse.py',
  'tests/test_backlog_status_audit.py',
  'tests/test_backlog_status_policy.py'
)

uv run ruff check $task1Files
All checks passed

uv run ruff format --check $task1Files
9 files already formatted

uv run ty check $task1Files
All checks passed

uv run detect-secrets-hook --baseline .secrets.baseline .codex/skills/backlog-status/scripts/backlog/audit.py .codex/skills/backlog-status/scripts/backlog/parse_sources.py .codex/skills/backlog-status/scripts/backlog/policy.py tests/test_backlog_status_audit.py tests/test_backlog_status_policy.py
exit 0

uv run python tools/quality.py check
exit 0; Ruff, formatting, ty, 295 unittests, 94% coverage, Bandit, detect-secrets,
Interrogate, Vulture, and Xenon passed

uv run mkdocs build --strict
exit 0; documentation built successfully

git diff --check
exit 0
```

A direct detect-secrets scan of files not yet tracked initially identified the three
published SHA-256 test pins as high-entropy false positives. Each literal now has the
repository-standard inline allowlist marker; the final scan is recorded after that
correction.

## Self-review

- Existing strict parser exception behavior and rendered error strings remain unchanged;
  audit-only loading converts typed exception fields directly and never matches English
  messages.
- `RepositorySnapshot`, status rendering, and schema-version-1 JSON receive no source
  fields or extra keys; the exact report regression remains green.
- Source facts retain raw duplicate rows/headings for later structural diagnosis and
  preserve exact one-based statement locations after whitespace folding.
- Policy absence or invalidity is explicit as `AuditLoad.policy is None` plus a blocking
  finding; other structural input continues loading.
- Filesystem work uses `Path`, explicit UTF-8, byte reads where byte identity matters,
  argument-vector subprocess calls, and deterministic Windows-safe temporary cleanup.
- The approved policy supplement bytes were not modified. Controller-owned BACKLOG,
  plan-status, and CLI-expectation edits were left intact and excluded from this task's
  commit.
- This task supplies loading and source facts only. It does not claim the later
  structural, adherence, evidence, lifecycle, report-wiring, or CLI tasks.

No unresolved Task 1 concern remains.
