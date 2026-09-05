---
name: gzs-update-dependencies
description: Refresh all project-managed dependencies, runtime pins, package-manager tooling, lockfiles, and version-pinned development tools to current supported releases, then run the repository's full verification. Use when the user asks to update all dependencies and tools, upgrade packages, refresh lockfiles, bump runtimes, or bring a project's toolchain current.
compatibility: Requires network access to authoritative package and tool sources plus the package managers used by the target repository.
metadata:
  govzero-version: "0.1.0"
  govzero-portability: "portable"
  govzero-origin: "gz-skills"
---

# GovZero Update Dependencies

Refresh the complete project-managed dependency and toolchain surface as one
reviewable maintenance change. Discover the repository's actual ecosystems and
policy first; do not assume Python, Node, a particular runtime version, or a
particular quality command.

This skill covers versions recorded by the project. Updating unrelated global
machine tools, operating-system packages, editor extensions, cloud resources, or
deployed environments requires separate explicit authorization.

## Workflow

1. Read the repository's applicable agent guidance and inspect the worktree.
   Identify pre-existing changes that overlap dependency surfaces before any
   metadata or lockfile mutation.
2. Inventory every project-managed dependency surface. Read
   [references/inventory.md](references/inventory.md) and retain only categories
   evidenced by the repository. Completion means every manifest, lockfile,
   runtime pin, package-manager pin, CI action, hook, container base, and bundled
   external tool in use is either included or explicitly classified as outside
   the user's requested project scope.
3. Capture current versions and constraints. Identify the repository's stated
   compatibility floors, intentional pins, generated files, update commands,
   and complete verification command. Preserve an intentional compatibility
   range unless current project policy says to advance it.
4. Resolve target versions from authoritative live sources: official package
   registries, runtime release indexes, vendor release metadata, or the
   package-manager's own current-version command. Read release notes for major
   versions and for any release whose compatibility is uncertain. Record
   unavailable or ambiguous evidence rather than guessing.
5. Update the package manager or project-pinned tool that performs resolution
   before using it to regenerate dependency state. Update declared manifests
   intentionally, then regenerate lockfiles with their owning tools. Never edit
   a generated lockfile by hand.
6. Apply updates in coherent ecosystem-sized batches so a failure can be traced
   to its owner. Adapt source and tests for breaking changes supported by release
   evidence. Do not weaken a quality rule, lower a tested floor, or silently pin
   an offender merely to make the upgrade appear green.
7. Synchronize all declared dependency groups and verify that a second lock or
   resolution check produces no unexplained churn. Run the package manager's
   outdated and vulnerability checks when available, and classify constrained,
   yanked, vulnerable, or unverifiable results precisely.
8. Run the repository's complete required verification, including generated
   artifact or packaging checks when dependency changes can affect shipped
   output. Fix failures caused by the update and rerun from the first affected
   gate.
9. Inspect the final manifest, lockfile, code, documentation, and generated-file
   diffs. Confirm no dependency surface was silently omitted and no unrelated
   user change was absorbed.

## Failure posture

- A network, registry, parse, resolver, vulnerability, compatibility, or
  verification failure blocks a claim that the project is current.
- When one release is incompatible, keep the last verified compatible version,
  state the precise constraint, and leave the rest of the completed upgrade in a
  reviewable state when project policy permits.
- Do not delete lockfiles, caches, or environments as a first response. Diagnose
  the owning tool and preserve recoverable user state.
- Do not expand a project dependency refresh into deployment or machine-wide
  maintenance.

## Evidence

Report each discovered ecosystem, before/after runtime and tool versions,
manifest and direct-dependency changes, lockfile changes, constrained or skipped
updates with reasons, vulnerability results, verification commands and results,
and final worktree scope. Never describe the project as fully current when an
inventoried surface lacks authoritative status evidence.
