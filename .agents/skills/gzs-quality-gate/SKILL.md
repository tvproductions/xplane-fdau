---
name: gzs-quality-gate
description: Run and evidence the repository's complete required quality gate for the current change. Use for pre-handoff, pre-merge, pre-release, or explicit full-verification requests; use the project's declared commands rather than assuming a language or toolchain.
compatibility: Requires the target repository's documented verification tools.
metadata:
  govzero-version: "0.1.0"
  govzero-portability: "portable"
  govzero-origin: "gz-skills"
---

# GovZero Quality Gate

Prove the current tree satisfies the repository's own completion contract. The
portable invariant is complete, observed verification; the project supplies the
commands, thresholds, and required evidence.

## Workflow

1. Read applicable repository guidance and inspect the current diff. Determine
   which verification policy governs the changed scope.
2. Discover the canonical aggregate quality command. Prefer a documented
   repository script or task that already sequences lint, formatting checks,
   types, tests, builds, documentation, generated surfaces, and policy checks.
   Read its implementation or help before assuming what it covers.
3. If no aggregate exists, construct the smallest complete sequence from the
   repository's documented commands. Record each required dimension and its
   owning command before running anything; completion means no required
   dimension is silently omitted.
4. Run the gate without filters that mask its exit status. Capture the command,
   exit code, relevant counts, warnings, and generated receipts or reports.
5. When the request includes fixing failures, diagnose and correct failures
   caused by the current work, then rerun from the first affected gate. Preserve
   unrelated user changes and do not weaken thresholds or suppress findings to
   manufacture a pass.
6. Run the final canonical aggregate gate on the unchanged candidate tree.
   Completion requires its observed exit status to be successful and every
   required artifact or report to exist.

## Evidence

Report the verified tree identity or worktree scope, commands and exit codes,
test and coverage counts when available, warnings, generated evidence paths,
and every skipped or unavailable dimension. A partial or unavailable gate is
not a full pass.
