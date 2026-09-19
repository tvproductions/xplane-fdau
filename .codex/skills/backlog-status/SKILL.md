---
name: backlog-status
description: Use when reporting or resuming xplane-fdau delivery status, checking roadmap/backlog/spec/plan adherence, asking for the next local action, or performing controlled child selection, lifecycle, suspension, or gate-evidence changes.
---

# xplane-fdau Backlog Status Adapter

`ROADMAP.md` owns node identity, kind, order, and dependencies. `BACKLOG.md`
is the only mutable delivery-state authority.

For status or resume work, run the strict audit and deterministic next action:

```powershell
uv run python .codex/skills/backlog-status/scripts/backlog_status.py audit
uv run python .codex/skills/backlog-status/scripts/backlog_status.py next
```

Use these additional read-only reports when needed:

```powershell
uv run python .codex/skills/backlog-status/scripts/backlog_status.py status
uv run python .codex/skills/backlog-status/scripts/backlog_status.py status --json
```

Controlled state commands are `select`, `transition`, `record-gate`,
`reopen-gate`, `suspend`, and `resume`. Run the complete command without
`--apply` first. Inspect its dry-run diff and audit. Apply only by repeating
the same command with the printed `--target-sha256` value and explicit `--apply`.

The adapter and script may edit only `BACKLOG.md`. They do not change a plan,
specification, evidence file, Git state, remote, tag, package, publication,
release, or another repository. Use `unittest` only and preserve the
standard-library-only runtime boundary.
