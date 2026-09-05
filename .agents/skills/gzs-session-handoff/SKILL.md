---
name: gzs-session-handoff
description: Create or resume a durable engineering-session handoff that preserves state, decisions, evidence, and next actions without duplicating existing artifacts. Use when the user explicitly asks to hand off, checkpoint, resume, or preserve work for another session or agent.
compatibility: Works in any repository that can store or reference a Markdown handoff document.
metadata:
  govzero-version: "0.1.0"
  govzero-portability: "portable"
  govzero-origin: "gz-skills"
---

# GovZero Session Handoff

A handoff is an evidence-backed continuity artifact. It advises the next session;
it does not authorize the next action.

## Create

1. Discover the repository's handoff command, template, and canonical storage
   location. Use them when present. Otherwise write one Markdown document to the
   repository's existing session-notes location; if none exists and the user did
   not request a durable project artifact, use the operating system's temporary
   directory.
2. Capture observed state before summarizing: branch, HEAD, worktree, completed
   verification, active plan or work item, and material artifact paths.
3. Reference existing specs, plans, issues, ADRs, commits, diffs, and reports by
   path or URL. Summarize only the context not already durable elsewhere.
4. Include these populated sections:

   - Current state and last completed action
   - Important context and constraints
   - Decisions, distinguishing user rulings from agent choices
   - Immediate next actions in order
   - Pending work, blockers, and open loops
   - Verification already run and verification still required
   - Evidence and artifact references
   - Suggested skills for the next session

5. Redact credentials, tokens, authentication headers, private personal data,
   and sensitive captured output. Verify every referenced local path exists.
6. Report the handoff path and its first advised next action.

## Resume

1. Read the selected handoff and every artifact it identifies as current truth.
2. Compare its branch, HEAD, worktree assumptions, external issue state, and
   evidence paths with current state. Increase verification with age and drift.
3. Present the current state, stale assumptions, and advised next actions to the
   user. Obtain authorization before mutating the repository or executing the
   advised plan.

Completion requires a successor to distinguish settled decisions, observed
state, proposed actions, and unresolved uncertainty without reconstructing the
previous conversation.
