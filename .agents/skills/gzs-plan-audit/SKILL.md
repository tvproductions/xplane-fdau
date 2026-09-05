---
name: gzs-plan-audit
description: Audit alignment among declared intent, scoped requirements, and an execution plan before implementation begins. Use when reviewing a plan, leaving plan mode, starting a planned change, or checking for missing requirements, forbidden paths, scope creep, or inadequate verification.
compatibility: Requires readable intent, scope, and plan artifacts in any repository-defined format.
metadata:
  govzero-version: "0.1.0"
  govzero-portability: "portable"
  govzero-origin: "gz-skills"
---

# GovZero Plan Audit

Compare three claims before code is written:

```text
declared intent <-> scoped requirements <-> execution plan
```

The repository decides whether those artifacts are ADRs, issues, briefs, specs,
or plan files. The audit diagnoses alignment; it does not silently rewrite any
of them.

## Workflow

1. Locate the authoritative intent, the scoped work item, and the plan. Record
   missing or ambiguous authority as an audit finding rather than choosing a
   convenient substitute.
2. Read intent first. Extract the problem, promised capabilities, constraints,
   rejected outcomes, integration points, and acceptance conditions without
   reading the proposed implementation.
3. Read the scoped requirements. Check objective match, complete intent
   coverage, explicit exclusions, path or component boundaries, acceptance
   criteria, and verification requirements.
4. Read the plan. Check that every scoped requirement has an executable step,
   every planned edit is allowed, denied surfaces remain untouched, dependencies
   and ordering are feasible in the current tree, and final verification proves
   the acceptance criteria.
5. Record each comparison as Aligned, Drifted, Missing, or Not Applicable with
   file-and-line citations. Separate scope gaps from scope creep.
6. Present a PASS only when no Drifted or Missing item remains. Otherwise return
   FAIL with a specific recommendation to correct the intent, scope, or plan.

## Output

Produce separate intent-to-scope and scope-to-plan tables, a cited gap list,
actionable corrections, and a PASS/FAIL verdict. If the repository defines an
audit receipt format, write it only after the semantic report is complete and
include the audited artifact identities or hashes.
