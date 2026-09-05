---
name: gzs-cross-platform-python
description: Review or implement Python filesystem, text, subprocess, temporary-resource, and test behavior for Windows, macOS, and Linux portability. Use when Python code handles paths, files, encodings, processes, cleanup, platform branches, or failures seen on only one operating system.
compatibility: Requires Python and the target repository's supported platform and version policy.
metadata:
  govzero-version: "0.1.0"
  govzero-portability: "portable"
  govzero-origin: "gz-skills"
---

# GovZero Cross-Platform Python

Make portability explicit at the operating-system seams. Preserve the project's
supported Python floor and verification tools; these rules do not require a
particular package manager.

## Review and implementation rules

- Use `pathlib.Path` for filesystem paths and join path segments structurally.
  Treat stored or protocol paths separately when their format is intentionally
  POSIX-like.
- Specify text encodings, normally UTF-8. Use `newline=""` for CSV files and
  test newline-sensitive behavior deliberately.
- Use context-managed temporary files and directories. Close files, database
  connections, memory maps, and subprocess handles before cleanup so Windows
  locking semantics are exercised honestly.
- Pass subprocess arguments as a sequence with `shell=False`. Invoke the current
  interpreter with `sys.executable` when a child Python process must match the
  running environment. Use a shell only when shell semantics are the actual
  requirement and quote through a reviewed platform adapter.
- Avoid locale, timezone, executable suffix, path separator, case sensitivity,
  signal, and permission assumptions. Isolate unavoidable differences behind a
  named adapter and test both branches.
- In tests, compare paths as paths, normalize protocol text only at the protocol
  boundary, and clean resources deterministically. A cleanup failure is a test
  failure, not something to hide with `ignore_errors=True`.

## Workflow

1. Read the supported-platform policy and identify the relevant OS seam.
2. Reproduce the behavior on the current platform with a focused test or script.
3. Inspect for assumptions in paths, text, resources, subprocesses, environment,
   and assertions. Change only assumptions evidenced by the code path.
4. Add a regression test that would fail under the alternate platform's
   semantics. Use CI or an actual alternate host when available; otherwise state
   which platform remains unobserved.
5. Run the repository's full quality gate and every configured platform job
   available locally.

## Evidence

Report the portability assumption found, affected platforms, regression test,
commands and results, and any platform that could not be exercised.
