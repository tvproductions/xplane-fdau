# T1.3 whole-branch independent review

Date: 2026-09-05. Base: `eac980afe5cec66a3ac55cb3774f49bafa4c3466`.
Reviewed head: `b64c34caed73a00e8b03b423d10249dee5144509`.
Reviewer seat: independent whole-branch reviewer, GPT-6 Astra.

## Strengths

- The implementation keeps source facts, structural checks, artifact adherence,
  lifecycle rules, evidence observation, and reporting in distinct repository-only
  modules. The runtime remains standard-library-only; no consumer, transport,
  recommendation, mutation, or release capability entered this slice.
- Evidence observation uses literal pathspecs, NUL-delimited stage/tree entries,
  regular-file modes, and binary worktree/index/HEAD comparisons. It does not
  mistake porcelain cleanliness, file existence, or recent commits for proof.
  Git status disables optional index refresh, with an actual index-byte regression.
- Frozen historical-plan admissions come from the approved policy table and
  retain exact plan hashes, review/gate requirements, and suspension semantics.
  The ordinary lifecycle correctly limits selection to current in-progress work.
- Both CLI commands share the audit result and preserve version-1 reporting,
  contextual errors, deterministic sorting, UTF-8/LF output, and blocking exits.
  The tests cover real Git fixtures and many independent malformed-input cases.
- The document reconciliation matches the separately accepted correction routes.
  D1 records are preserved, previously open downstream gates remain open, and
  ordinary Git sync remains distinct from release authority. The separately
  reviewed native hour guard restores the existing v3/v4 contract on Python 3.14.

## Issues

### Critical

None.

### Important

1. **Referenced acceptance-list ordinals can escape the audit as ValueError.**
   File: `.codex/skills/backlog-status/scripts/backlog/parse_sources.py:316`.
   `_numbered_gate_statements` converts the unrestricted numeric list prefix
   with `int()` without translating conversion failure. In an otherwise valid
   four-earlier-gates fixture, replacing the first ordinal with 4,301 digits
   raises Python's integer-conversion-limit ValueError through `load_audit`
   and `backlog_status.main`. `status --json` emits no report and loses the
   independently malformed historical artifact's finding. This violates T1.3's
   fail-closed contextual reporting contract and is the same conversion seam
   already corrected for BACKLOG counts and evidence Gate values.

   Translate this failure into a source-located domain finding or unresolved
   managed-reference result without changing Python's conversion limit. Add a
   regression through audit and JSON with an independent malformed artifact;
   preserve the valid four-item reference control.

2. **Unlinked active plans bypass completion-evidence eligibility.**
   Files: `.codex/skills/backlog-status/scripts/backlog/lifecycle.py:130`,
   `:142`, and `:197`; the artifact-wide check in `adherence.py:101` checks
   only whether the field is present.
   Completion evidence is validated only while visiting a BACKLOG child's
   currently linked plan. A separately discovered active `completed` plan can
   point to a missing completion file and the whole audit returns no findings.
   I reproduced this by copying the valid completed fixture plan to
   `docs/superpowers/plans/unlinked-completed.md`, keeping its valid child,
   source design, and approval, and changing only Completion evidence to
   `.superpowers/sdd/absent-completion.md`. `audit_repository` returned `()`.

   The parent design requires completed active plans' completion references to
   resolve to regular files, and the supplement's slot matrix explicitly owns
   Active-plan Completion evidence, not only BACKLOG-linked plan references.
   Validate populated completion slots for every discovered active plan using
   its declared child and child-level ordinal. Preserve the stronger HEAD rule
   where lifecycle requires it and avoid duplicate findings for linked plans.
   Cover an unlinked valid control plus missing, malformed/wrong-kind, and dirty
   completion evidence. This must not reinterpret frozen historical plans.

3. **Design task-list markers are retained as acceptance statement text.**
   File: `.codex/skills/backlog-status/scripts/backlog/parse_sources.py:283`.
   `_LIST_ITEM` removes the leading bullet but leaves `[ ]` or `[x]` in the
   extracted criterion. Replacing only the valid fixture's
   `- Frozen parser remains open.` with `- [ ] Frozen parser remains open.`
   produces blocking `artifact.gate-drift` at design line 22, child T1.2,
   gate 1, although the statement is unchanged. The parent design at line 273
   explicitly requires matching after task-list removal and whitespace folding.

   Normalize the supported task-list marker at extraction before exact statement
   comparison, retaining source lines and punctuation. Add plain-bullet/open-task/
   checked-task positive controls and retain the changed-wording negative control.
   This formatting normalization must not infer delivered gate state from a design.

4. **Policy-test repositories still inherit user signing and hook behavior.**
   File: `tests/test_backlog_status_policy.py:44`.
   This new test helper invokes Git without the per-command signing/hooks controls
   used by `tests/backlog_audit_support.py`. With inherited `commit.gpgsign=true`
   and a deliberately unavailable `gpg.program`, `make_repository()` fails at
   its fixture commit with exit 128 and `gpg failed to sign the data`. A configured
   hooks path is likewise not disabled by this helper. This contradicts the
   approved plan at line 364 and makes tests depend on interactive/user tooling.

   Use the isolated shared Git helper, or supply the same explicit per-command
   `commit.gpgsign=false`, disabled hooks path, and fixture newline settings.
   Add a focused inherited-configuration control; do not alter global Git config
   or bypass hooks for actual project commits.

### Minor

None.

## Review method and verification

Read the complete supplied review package in sequential bounded character
chunks, covering all 46 changed files and the complete branch diff. Reviewed
the approved parent T1 design, supplement, current plan, parent architecture,
scope amendment, completed migration authority, controller rulings, document
reconciliation receipt, and compatibility evidence. Earlier scoped reviews
were context, not substitutes for this pass. No subagents were dispatched.

The supplied Task 5 evidence records 368 passing unittest tests on each of
Python 3.12.13, 3.13.14, and 3.14.4; full aggregate quality, explicit hidden-tool
Ruff/format/ty, strict MkDocs, documentation checks, and valid current audit/JSON.
I did not rerun aggregate checks or the supported-version matrix. Windows is
observed; Linux/macOS execution remains unobserved. The recorded MkDocs vendor
notice is nonblocking. Runtime coverage is 94%; it is not tooling coverage.

Focused checks used Python 3.12.13 with `-B`, in-memory unittest definitions,
existing fixture helpers, and context-managed temporary repositories. Valid
audit controls passed before each production-input mutation. The first focused
harness also discovered eight imported policy unittest controls; those passed.
The three production risks above then reproduced as two assertion failures and
one uncaught ValueError. The first signing probe had an invalid empty environment
configuration value and was discarded. Its corrected, one-test probe passed
only two inherited configuration entries and failed at the actual fixture commit
with the expected unavailable-signing-program diagnostic. All temporary fixtures
were cleaned; no actual user signer or hook was invoked by that focused probe.

After inspection and focused checks, read-only Git status was empty and HEAD
still matched the reviewed hash. No source, index, HEAD, branch, policy, or
historical evidence was changed. This receipt is the only retained review write.

## Recommendations

Route these four confirmed findings together for one bounded correction round.
They require implementation/test corrections, not new architecture, policy
approval, or document reconciliation. Run their focused regression controls,
then the required final checks for the changed candidate and review the fix diff.

The candidate's intentional T1.3 `in_progress` / 0-of-4 state is truthful and
is not a finding. Accepted review, completion, four factual gate records,
eligible-evidence commit, and verified-state post-commit audit must follow an
accepted final review. They cannot be fabricated or inferred from this receipt.

## Assessment

**Ready to merge? No — with the four fixes above, followed by the planned
factual evidence closeout and clean post-commit audit.**

The architecture and main behavior align with the approved scope, but the
remaining parser and completion-evidence gaps violate the audit's acceptance
contract. This receipt is a review rejection for the named candidate, not
accepted completion evidence or authorization to merge, push, tag, or release.
