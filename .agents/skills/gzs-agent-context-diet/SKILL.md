---
name: gzs-agent-context-diet
description: Reduce always-loaded agent instruction weight while preserving every binding invariant through progressive disclosure and precise context pointers. Use when AGENTS.md, CLAUDE.md, repository rules, or skill descriptions have accumulated duplicated rationale or exceed an enforced context budget.
compatibility: Works with repositories that maintain durable agent guidance or generated instruction mirrors.
metadata:
  govzero-version: "0.1.0"
  govzero-portability: "portable"
  govzero-origin: "gz-skills"
---

# GovZero Agent Context Diet

Reduce per-turn context load without relaxing policy. The operation is a
delivery refactor: binding decisions remain reachable and generated surfaces
remain coherent.

## Workflow

1. Identify authored sources and generated mirrors before editing. Read the
   repository's synchronization commands and context-budget checks.
2. Measure each always-loaded surface by bytes and lines. Inventory every
   binding rule, trigger pointer, repeated rationale, embedded example, and
   duplicated command list.
3. Classify content:

   - keep immediate actions, hard guardrails, and frequently needed invariants
     in the always-loaded file;
   - move conditional procedure and substantial rationale behind a one-line
     pointer that names the exact condition for reading it;
   - remove duplicates, stale caches of discoverable configuration, and
     instructions that add no behavior beyond the agent default;
   - preserve one authoritative home for each meaning.

4. Edit authored sources only. Regenerate mirrors through the repository's
   owning tool.
5. Verify every moved rule remains reachable through a discriminating pointer,
   every relative link resolves, every generated mirror matches its source, and
   no binding invariant disappeared or weakened.
6. Rerun budget and repository documentation checks. Compare before and after
   measurements and review the semantic diff, not only the byte reduction.

## Evidence

Report authored and generated surfaces, bytes and lines before/after, content
moved or deleted by category, new pointers and their trigger conditions,
invariant-retention evidence, mirror validation, and unresolved budget pressure.
