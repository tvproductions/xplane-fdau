# Skills-first development stack

These instructions are mandatory adoption requirements. Agents MUST execute the
prescribed workflow and checks, preserve project authorities, and record evidence
before claiming completion. Agents MUST NOT replace requirements with convenient
defaults, skip failed checks, invent acceptance evidence, or treat configuration
as proof of installation. An unmet requirement remains explicitly incomplete.
Record an evidenced, owned exception where policy permits one; do not grant
yourself an exemption. Use the starter's commands and native host procedure.

This adopted template currently supports Python projects only, in both lite and
full/heavy lanes. Other languages, likely including Go, are future work requiring
their own reviewed and released baseline; upstream skill portability is not
evidence of template support for another language.

Use direct `gh` commands for GitHub operations and direct `git` commands for
repository operations. Do not wrap routine CLI calls in Python. Use Python when
substantive processing is actually needed, through the prescribed uv-managed
environment. Run that Python with `uv run --locked python`, honoring the project's
exact interpreter pin and required uv version.

Install and enable this stack at repository/project scope. Do not install or
register its plugins or marketplace globally or at user scope. Use project-owned
native configuration and explicit project-scope installation where supported;
do not run unscoped install commands that change user defaults. Native clients
may store downloaded files in a shared user cache; cache location does not grant
user-wide activation. If the host cannot preserve repository scope, report the
limitation instead of falling back to a global/user installation.
Existing global/user installations MAY remain. The project MUST own the selected
versions, activation and command behavior through repository configuration.
Project overrides MUST suppress duplicate inherited sources locally; do not
uninstall global copies or rewrite user settings to make the project work.
For brownfield repair, preview and apply the reviewed starter's
`skills-first-starter localize --project <root> --host <codex|claude|opencode>
--starter-ref <FULL_STARTER_SHA>` with `uv run --locked`; add `--apply` after
review. The command repairs project activation without changing adoption records
or global installations. Use `configure --host` for full adoption, not scope repair.
Keep plugin installation, version updates and enablement separate. Record and
preserve project enablement and user defaults during updates. In Codex CLI
0.166.0, `plugin add` unconditionally enables the plugin user-wide, even from
a project with a local marketplace. Do not use it as a project install, update
or reinstall command. Verify actual installed revisions and unchanged activation
scope after native resolution; report unsupported updates as pending.
On OpenCode 2.2.0, agents MUST use the reviewed starter's
`skills-first-starter run-opencode --project <root> -- <native arguments>` through
its locked uv environment. The scoped launcher reconciles configuration and uses
a private server; plain native startup can let an inherited duplicate ID beat
the project pin. Global copies remain installed. Do not bypass the launcher and
claim local precedence without fresh native evidence on the actual host version.

Maximal Astral alignment is required for Python projects under this baseline.
Read `docs/engineering/astral-alignment.md` in the reviewed starter checkout.
Complete `docs/engineering/astral-acceptance.md` there, using its worked migrations.
Adopt every applicable Astral recommendation; record evidenced departures with
an owner and revisit condition. Verify effective uv/Ruff/ty configuration,
interpreter/tool provenance, selected exact environments, published dependency
metadata and source-independent builds (`uv build --no-sources`). Locked runs
alone do not prove exact contents or executable origin. Verify clean installed
behavior and keep configuration/Python acceptance/native discovery results separate.
Use `src/<package>/`, a declared build backend (uv_build for pure Python),
installed-package imports, application entry points and py.typed for typed
libraries. Centralize Python metadata and uv/Ruff/ty configuration in
pyproject.toml; use standard dependency-groups, a committed uv.lock and exact
.python-version, ignored .venv, and locked uv execution shared by hooks and CI.
Use Cargo-style uv workspaces for compatible interconnected packages: one root
lock/environment, explicit member dependencies and editable workspace sources.
Record project-root versus non-project coordinator semantics; select members or
all packages explicitly, and independently verify built members' dependencies.
Verify artifacts outside
the checkout. Adopters must refactor nonconforming layout/configuration during
full baseline adoption. Preserve behavior, data and authorities while migrating;
configuration preservation is not a permanent exemption. Record constrained
exceptions with evidence, an owner and revisit condition. Configuration-only
requests report remaining refactoring instead of silently performing it.

Read project AGENTS.md and linked authorities first. This project records sources
in `.skills-first/bundle.lock.json`. The starter owns only the narrow
`update-gz-template` skill; it supplies stack configuration, provenance and project
policy. Use that project skill, or `docs/updating.md` in the reviewed starter,
for canonical template-update review and migration. Generic maintenance remains
with gz-skills; this is not a second dependency updater.
Its guidance highlights the emphasis when using gz-skills: dependency freshness,
current Python practices, portability and obedience to adopted project policy.
For project operations, use project-owned skills. For feature work, use the
installed SP `using-superpowers` workflow; for engineering skill selection, use
gz-skills `gzs-router`. Verify actual discovery before claiming either is available.
Superpowers supplies feature design and implementation; gz-skills supplies
portable engineering disciplines. Superpowers Backplane remains pinned for
future adoption but is disabled by default because readiness is incomplete.
Use existing project backlog and handoff practices in the meantime.

Release planning applies to this adopting project's own versions as well as
the starter. A bare scaffold may retain `0.0.0` only as an unpublished placeholder.
As soon as any original implementation, tests, documentation or configuration
is added, set the initial project version to **0.1.0**. Do not release
project-owned work as `0.0.0`. Align package metadata, runtime version output
and release records before accepting adoption. Correct an unpublished `0.0.0`
project that already contains original work to `0.1.0`.
The first substantive release is the first versioned commitment to the project's
public contract. Declare that contract and release it as `0.1.0`; it may evolve
under the required 0.x rules without claiming 1.0 stability.
Preserve existing published versions and tags; never reset or rewrite release
history. Use MAJOR.MINOR.PATCH for the project's public contract: after 1.0,
incompatible changes require major, compatible additions or public deprecations
minor, and compatible fixes patch. During 0.x, additions and changes requiring
reconciliation increment minor; compatible fixes increment patch. Define the
public API/CLI/data/configuration surface and document compatibility impact.
Every major release, including 1.0.0, always requires a newly
written PRD for that major. Keep and reference it in project-owned release
authorities. Minor releases bundle related changes through the existing backlog;
SP-BP is intended to assist once ready and explicitly adopted. Patch releases
remain compatible fixes and clarifications. Preserve compatibility rules and
independent app/template/plugin versions. Read the reviewed starter's
`docs/baseline-policy.md` and `docs/versioning.md`; this rule does not authorize
publication or enable deferred Backplane.

Project AGENTS.md, domain authorities and verification commands remain binding.
Keep project-owned operational skills, supporting domain code, and records
separate. Confirm actual discovery before invoking upstream entry skills;
configuration does not prove loading. Preserve independently versioned upstream
sources and avoid duplicate plugin/copied-skill discovery.

Backplane owns requirements tracking, labeling, backlog/release monitoring,
handoffs and lite/heavy mode definitions. Read its mode authority at
https://github.com/tvproductions/superpowers-backplane/blob/main/docs/superpowers-backplane/modes.md;
do not define a replacement lifecycle in this template or its helper. The
starter remains the shared engineering and release policy alignment source;
see `docs/versioning.md#ecosystem-policy-authority-and-consistency` there.
Explicitly select lite or heavy through the pinned gz-skills setup workflow;
missing/null selection means adoption is incomplete. Both lanes require the
same applicable Python baseline, SemVer/major-release PRDs and adoption/release
analysis. Heavy retains SP + Backplane + gz-skills as its intended design;
report deferred Backplane readiness separately and keep it disabled until ready
and explicitly activated. The helper never selects a profile or certifies
conformance. Follow `docs/adoption-0.5.md` in the reviewed starter for greenfield
adoption and brownfield first-adoption/upgrade paths. No gzkit lifecycle is
introduced. For structural backporting, updates and verification, use the reviewed starter at
https://github.com/tvproductions/gz-skills-first-starter. Existing project instructions
and app architecture are preserved until specific changes are authorized.

For projects adopting the starter's Python baseline, use the latest stable
release allowed by `docs/baseline-policy.md` at the recorded starter revision;
compare newer published policy during maintenance. It defines allowed ranges
and exception reasons separately from this checkout's tested execution pins.
Require the latest stable baseline tools across tool families. Review new stable
families and verify compatibility; an old range or exact pin is not a freshness
exemption. Required stale/unknown freshness blocks adoption and release acceptance.
The adopter owns that decision even when gz-skills performs the review. Retained
older tools need an explicit evidenced exception, owner and dated revisit and
remain conditional/noncurrent. Check official releases at setup/adoption, before
each release and scoped maintenance; pin the verified selections afterward. Python's
family follows the user-directed N-1 rule: one stable minor behind, currently
3.14.x for ordinary projects. XPPython3-bound code retains its supported 3.12.x
host exception. This runtime policy does not exempt old tool families. Verify the latest
stable host-compatible patch from official sources at setup/adoption
and scoped maintenance, then pin that exact patch for local execution and CI.
An already-installed version or a `3.14` selector does not prove freshness.
The starter's current exact patch is a reproducibility baseline, not a permanent
adopter requirement. XPPython3 controls its embedded interpreter; inspect and test
that runtime separately, recording host limitations and revisit conditions.
Keep tools pinned/locked after verification; changing families requires separate
review. Record any compatibility exception with evidence and a revisit condition,
including the documented XPPython3 host exception. Preserve project dependencies
and authorities, report adoption gaps, and follow the reviewed starter's Python
engineering policy at `docs/engineering/python.md` in the reviewed starter
checkout. Keep Ruff check/format, ty and unittest (never pytest) as routine checks
through uv and pre-commit; execute applicable deeper analysis at adoption and
release acceptance, plus on demand, outside routine hooks and routine CI.
Retain evidence and reviewed findings; required FAIL/UNKNOWN/stale results block
strict acceptance. Accepted exceptions are conditional, never 100% conformance.
Report missing
tool installation or enforcement as a gap. Adopters choose starter updates,
independent upstream updates or both, and own update timing and verification.
The starter permits scheduled scans and reviewed update PRs covering standard
and X-Plane/XPPython3 baselines separately; see
`docs/baseline-policy.md#scheduled-dependency-scanning` in the reviewed starter
checkout. No adopter scanning service or schedule is imposed. Automatic merge,
release publication and native plugin installation require separate authority.

The reviewed Python policy's on-demand tools form the adopter minimum standard,
independent of the starter helper's needs. Include project-pinned `cohesion` for
class cohesion analysis; verify its standalone CLI on the selected runtime and
representative invented classes. Record scopes, scores and reviewed findings;
record not-applicable scopes with reasons and report missing installation or
compatibility evidence as gaps. Preserve project-specific thresholds and keep
cohesion outside routine hooks and routine CI. Complexipy is under qualification
review: known keyword-conditional under-counting means a clean score alone cannot
pass cognitive acceptance. Read the current qualification evidence before relying
on that analyzer. The selected replacement direction is gzkit's CPython AST
scoring approach, preferably through one shared package; qualification and
distribution must be verified before claiming it is installed or authoritative.
See the reviewed starter's
`docs/engineering/python.md` for the full selected tool set and interpretation.

Keep code current with its selected Python family, not just its interpreter pin.
gz-skills owns runtime discovery; require its workflows to honor this project's
adopted version-range and engineering policy, report missing/conflicting evidence
and validate host-bound behavior separately. This template supplies policy, not
an upstream discovery procedure.
At adoption, runtime-family changes, feature design, code review and scoped
maintenance, assess relevant idioms, stdlib advances and deprecations using
versioned official documentation. Record benefits, risks and adopt/defer decisions;
apply useful changes within authorized scope. Use SP and gz-skills workflows with
the reviewed starter's `docs/engineering/python.md` and version opportunity guide.
XPPython3-bound code must stay within 3.12/host capabilities. The pinned gz-skills
Pythonic-pattern skills cover pattern simplification and `gzs-cross-platform-python`
covers OS seams. Read `docs/gz-skills-python.md` in the reviewed starter for the
verified mapping; those workflows do not establish a complete version audit.
Report missing workflow coverage rather than inventing a starter skill or claiming
that a current runtime proves current code.

At setup/adoption, before each release, scoped upgrades and quarterly on-demand
maintenance, check this starter template, Superpowers,
Superpowers Backplane and gz-skills independently for upstream updates. Compare
the recorded starter/component SHAs with official published releases; where no
release exists, distinguish a reviewed published commit from a stable release.
Review template changelogs for baseline-policy changes as well as dependency
versions; a new template release does not automatically change project policy.
Record the checked date, selected/latest versions or SHAs, compatibility evidence
and adopt/defer decisions. Review configuration changes before using native
update operations, preserve project additions and overrides, keep rollback pins,
and verify actual loaded sources in a fresh session. Track SP-BP freshness while
it is deferred; keep it disabled until readiness and explicit adoption are
established. Use the reviewed starter's `docs/adoption.md` maintenance procedure.

Generic maintenance belongs in gz-skills: use its discovered
`gzs-update-dependencies` for authorized dependency/tool updates and
`gzs-dependency-risk-audit` for risk assessments. The starter supplies baseline
policy and stack-specific binding guidance. Do not create a duplicate local
maintenance skill or generic freshness reporter. The pinned gz-skills v0.8.3
supplies freshness-only review and template/plugin inventory. Review mode leaves
pins and environments unchanged; preserve project policy and profile choices.
End a freshness review with a concrete recommended upgrade batch and an explicit
offer to apply it. Strongly recommend supported updates that satisfy project
policy; state targets, benefits, compatibility risks and required checks. Do not
stop at an inventory or adopt/defer table. If updates are already authorized,
perform and verify them without asking again. State evidenced deferrals; if
everything is current, say so instead of inventing an upgrade.

Track the adopted starter's own version and exact SHA in its bundle lock,
independently of app and upstream plugin versions. Compare reviewed template
releases and their changelog using the starter's `docs/versioning.md` policy.
A version label is not publication or readiness proof. Reconcile older
unversioned records without inventing historical provenance or overwriting
project changes.
