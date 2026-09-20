# gz-skills plugin-only adoption specification

- **Status:** Approved
- **Approval:** 2026-09-19 — Jeff / tvproductions
- **Date:** 2026-09-19
- **Scope:** Codex projects that use the `tvproductions/gz-skills` portable workflows

## Purpose

Use the `gz-skills@gz-skills` Codex plugin as the sole installed source of
GovZero portable skills. Each project keeps its own adapters and pins a reviewed
plugin release. A project does not copy, symlink, vendor, or install individual
`gzs-*` skills through another mechanism. This specification is a reusable
pattern; each adopting project records its own file inventory, gates, and
integration evidence.

This changes skill delivery and discovery, not the ownership or semantics of a
project's product backlog, runtime package, or release gates. Installing or
updating the plugin never authorizes Git sync, handoff, a tag, publication, or a
release. The explicit-only rules in the plugin still govern those workflows.

## Initial scope and extension rule

The first xplane-fdau adoption covers the pinned `gz-skills` Codex plugin and
this repository's Python dependency surfaces: `pyproject.toml`, `uv.lock`, the
uv tool pin, supported Python range, and related CI and development tooling.
The plugin update stays a Codex marketplace operation within a complete
`gzs-update-dependencies` run; the T2.2 Python/uv adapter owns its Python
surface. Both results join every other evidenced managed surface in the full
project dependency report.

`gzs-update-dependencies` remains ecosystem-neutral. An adopting project adds
another ecosystem to its inventory only when that ecosystem is present in the
repository and a project-owned adapter or package manager can verify it. This
specification does not define Node, Rust, .NET, or other future adapters.
## Portable contract

| Parameter | Required value or project choice |
| --- | --- |
| Plugin ID | `gz-skills@gz-skills` |
| Marketplace name | `gz-skills` |
| Marketplace source | `https://github.com/tvproductions/gz-skills.git` |
| Marketplace ref | A reviewed versioned release tag, chosen by the adopting project; record its resolved commit |
| Project configuration | Trusted repository `.codex/config.toml` |
| Project adapters | Repository-owned skills and commands that supply local paths and gates beneath plugin workflows |
| Dependency refresh | `gzs-update-dependencies` includes the project-pinned plugin in a full dependency update; Codex owns plugin installation |
| Quality gate | The adopting repository's declared command, run once on the final change unless a failure requires a rerun |

Each project stores the marketplace source, release ref, and enabled plugin in
its trusted-project configuration. For the first xplane-fdau migration, the
reviewed starting ref is `v0.2.0`:

```toml
[marketplaces.gz-skills]
source_type = "git"
source = "https://github.com/tvproductions/gz-skills.git"
ref = "v0.2.0"

[plugins."gz-skills@gz-skills"]
enabled = true
```

A trusted-project configuration can define a Git marketplace and enable its
plugin; it overrides user-level settings subject to managed requirements.
Codex discovers skills from the plugin package. The project does not freeze an
expected skill count: additions and changes arrive through reviewed plugin
releases. References: [Codex configuration](https://learn.chatgpt.com/docs/config-file/config-reference#configtoml),
[plugin marketplace setup](https://developers.openai.com/plugins/build/plugins#add-a-marketplace-from-the-cli),
and [project plugin enablement](https://developers.openai.com/plugins/build/plugins#enable-or-disable-a-plugin-for-a-repo).

## Installation and availability

1. Trust the repository in Codex so its `.codex/config.toml` is loaded.
2. Use Codex's plugin mechanism to install the configured plugin when it is
   absent: `codex plugin add gz-skills@gz-skills`.
3. Run `codex plugin list --json` in the project and verify that
   `gz-skills@gz-skills` is installed, enabled, and at the release selected by
   the project configuration. Check `codex plugin marketplace list --json` for
   the intended Git source.
4. Start work only when the plugin skills are discoverable. If plugin install,
   enablement, or version verification fails, stop and repair the plugin setup.
   Do not fall back to standalone skill installation or a copied catalog.

A project's agent guidance names the plugin as the sole portable workflow
authority and states its explicit-only workflow boundaries. Local adapters
remain under that project's existing skill or tooling root and supply exact
commands; they must not redefine or duplicate a `gzs-*` workflow. Other
unrelated skill systems, such as this repository's external Superpowers
checkout, are outside this rule.

## Forbidden alternative installations

An adopting repository does not contain `gzs-*` directories under
`.agents/skills`, `.codex/skills`, or another standalone skill discovery root.
It does not retain a standalone `gz-skills` installer command, generated
`gz-skills.lock.json`, vendored checkout, submodule, junction, symlink, or
project-local plugin copy as an alternate source. It does not configure a
second marketplace name for the same plugin. Old installation instructions
remain only in clearly marked historical records; current guidance points to
this plugin-only contract.

Repository checks must reject tracked or untracked standalone `gzs-*` copies in
known project discovery roots and reject a retained standalone lock. CI can
verify repository contents and configuration without depending on a developer's
Codex installation. A separate local acceptance check verifies that the plugin
is actually installed and enabled. No repository test can prevent a user's
unrelated global skill installations; agent guidance must ignore those as an
authority for this project.

## Updating the plugin as a dependency

The project-pinned plugin is a project-managed agent workflow dependency.
`gzs-update-dependencies` explicitly inventories separately pinned agent skill
or helper repositories. A request to refresh all project dependencies and
tools therefore includes the `gz-skills` plugin pin. A request limited to a
narrower ecosystem may leave it unchanged only when that scope is explicit.
The plugin does not update itself merely because its skill is invoked.
For a Python project, this pin sits beside `pyproject.toml` and `uv.lock` in
the managed-dependency inventory; it does not become a Python package or a
`uv.lock` entry.

Each adopting project owns its release ref. A new upstream release does not
silently change the project. During a full project dependency refresh or an
explicit plugin update:

1. Use the currently installed `gzs-update-dependencies` workflow to inventory
   the plugin pin alongside the project's other managed dependencies. Review
   the upstream release and skill changes, then check the new tag, plugin
   version, and resolved commit against the intended source.
2. Change the project's `.codex/config.toml` `ref` to the reviewed release tag.
   Keep the plugin ID, marketplace name, and Git source stable. Adjust project
   adapters only when release review shows a compatibility need.
3. From the trusted project, run `codex plugin marketplace upgrade gz-skills`
   through Codex's marketplace mechanism. Use `codex plugin list --json` and
   `codex plugin marketplace list --json` to verify the effective installed
   version, enabled state, and source. If they do not match the new pin, resolve
   plugin installation before claiming the update complete. Start a new agent
   session when verifying behavior against the newly installed skill version.
4. Check that one plugin copy is discoverable and no standalone `gzs-*` copy
   has appeared. Run the project's focused policy checks and its declared
   quality gate on the final candidate. Record the old and new refs, resolved
   commits, plugin version, review, command results, and behavior changes.
5. Integrate and publish only through that project's authorized Git workflow.
   Updates in other projects are separate decisions; no update in one
   repository silently advances the others.

The Codex marketplace owns installation and refresh of this plugin; a Python,
Node, or other package manager must not mutate its cache. A project-specific
dependency adapter can retain its ecosystem scope, but the complete
`gzs-update-dependencies` report must include the plugin's reviewed status and
cannot claim the project fully current while this project-managed pin is
unverified. The installed plugin's `gzs-update-dependencies/references/inventory.md`
identifies agent workflow dependencies as an inventory category.

`codex plugin marketplace upgrade` refreshes configured Git marketplace
snapshots; a tag pin remains a pin until the project changes it. The exact CLI
commands are documented in [Codex developer commands](https://learn.chatgpt.com/docs/developer-commands#codex-plugin-marketplace).
Tracking a moving branch is outside this standard because it bypasses the
project's review point.

## Adoption procedure

1. Inventory the current portable skill discovery roots, plugin installations,
   local adapters, generated locks, Git attributes, security baselines, tests,
   documentation, and packaging exclusions. Preserve unrelated skills and
   historical evidence.
2. Add the trusted-project plugin configuration with a reviewed release tag.
   Install and verify the plugin through Codex. Confirm its skills are available
   before removing the old source.
3. Remove every redundant standalone `gzs-*` tree and its installer lock.
   Remove attributes and security-baseline entries whose only purpose was to
   preserve or scan that lock. Keep negative packaging tests that reject
   governance files from distributions.
4. Update agent guidance and tests to require plugin-only configuration and
   reject local alternatives. Preserve exact project adapters and commands.
   Do not hard-code the plugin's current skill count into project tests.
   Register the plugin ref in the project-managed dependency inventory so
   a full `gzs-update-dependencies` run cannot silently omit it.
5. Run the project's required governance audit, focused tests, quality gate,
   documentation build, and distribution boundary checks as applicable.
   Review the change before integration. Record the installed plugin version
   and final single-source discovery result.

## xplane-fdau migration mapping

| Surface | Required change |
| --- | --- |
| `AGENTS.md` | Replace the snapshot and lock authority with the plugin-only rule, keep explicit Git-sync and handoff boundaries and project adapter commands. |
| `.codex/config.toml` | Add the Git marketplace at `v0.2.0` and enable `gz-skills@gz-skills`. |
| `.agents/skills/gzs-*` | Remove the 23 tracked standalone skill files; retain ignored Superpowers discovery. |
| `gz-skills.lock.json` | Remove the obsolete standalone installer lock. |
| `.gitattributes` and `.secrets.baseline` | Remove the byte-preservation rule and entries specific to the removed lock. |
| `tests/test_project_skills.py` | Replace lock/tree hash assertions with project config and absence checks; keep adapter and Superpowers checks. |
| `tests/test_release_tool.py` | Keep negative archive tests for `.agents/` governance leakage even though the copied skills are gone. |
| T2.2 draft plan | Reconcile the full refresh workflow to inventory and verify the plugin pin and update it through Codex; the Python/uv adapter must not mutate the plugin cache. |
| Historical adoption documents | Leave unchanged as dated evidence; this specification and current `AGENTS.md` become the new authority. |

T2.1, T2.2, T3.1, B1.1, the q4xpcc handoff, product runtime, and release state do
not advance by adopting this plugin policy. No plugin update or standalone
installation runs as part of ordinary feature changes or routine hygiene.

## Acceptance evidence

The adopting project records:

- A clean policy test showing exactly one configured plugin source and no
  standalone `gzs-*` installation or lock in the repository.
- Local `codex plugin list --json` output showing the expected plugin ID,
  version, installed state, and enabled state.
- Focused tests and the declared quality, documentation, and packaging gates
  applicable to the change, with failures and remedies recorded honestly.
- Review of the exact removed files and retained project adapters.
- Final Git and backlog state, without inferring Git-sync or release authority
  from the plugin migration.

The first xplane-fdau implementation plan must name exact file edits, tests,
commands, and commit points after this specification is reviewed. It must not
bundle T2.2 dependency-toolchain implementation or q4xpcc runtime adoption.
