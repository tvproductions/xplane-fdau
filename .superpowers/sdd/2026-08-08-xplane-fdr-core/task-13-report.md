# Task 13 report: publish the supported API and documentation

## Result

Published the MkDocs user guide, stable API reference, changelog, backlog, and
repository documentation skill. The existing `xplane_fdr.__all__` already
contained the complete deliberate stable surface required by the task, so no
production API change was needed; `tests/test_public_api.py` now protects it.

The published guidance is explicit that native X-Plane textual FDR v3/v4 is a
different scope from ARINC recorder/QAR formats and FOQA/FDM programs. It makes
no regulatory, threshold, parameter-count, or real-world codec claim.

## RED / GREEN evidence

### Public API and documentation contracts

RED command:

```powershell
uv run python -m unittest tests.test_public_api tests.test_documentation -v
```

RED output: the existing public export test passed, while all three
documentation tests errored because `mkdocs.yml` and `docs/index.md` did not
exist. The command finished `Ran 4 tests` with `FAILED (errors=3)`. This proved
the missing documentation behavior; the public surface was already complete.

The new project-skill requirement also had a separate RED:

```powershell
uv run python -m unittest tests.test_project_skills.ProjectSkillTests.test_project_skills_are_scoped_to_xplane_fdr -v
```

It failed with `FileNotFoundError` for `.codex/skills/documentation/SKILL.md`.

An additional documentation-example RED required executable recording inputs:

```powershell
uv run python -m unittest tests.test_documentation.DocumentationTests.test_recording_examples_construct_semantic_inputs -v
```

It first failed because the guide had no `FDRRecordingDefinition` or
`FDRSample`, then again correctly failed until the `FDRSample` example supplied
its required empty value tuples. The final guide constructs all semantic inputs
before calling `session.record(sample)` or `session.record_from((sample,))`.

The independent review found that the documented hosted schema URL would have
returned 404. A review-follow-up RED confirmed the missing artifact:

```powershell
uv run python -m unittest tests.test_documentation.DocumentationTests.test_documented_schema_url_has_a_published_schema_artifact -v
```

It failed with `AssertionError: False is not true` for the absent
`docs/schemas/fdr-record-config-v1.schema.json`. The schema is now published as
an exact copy of the packaged contract. The same focused test is green, and
`uv run mkdocs build --strict` completed with exit status 0 afterward.

GREEN command and exact summary:

```powershell
uv run python -m unittest tests.test_public_api tests.test_documentation -v
```

`Ran 5 tests in 0.001s` and `OK`.

The repository-skill contract was also green:

```powershell
uv run python -m unittest tests.test_project_skills -v
```

`Ran 2 tests in 0.008s` and `OK`.

## Documentation-skill evaluation

The new `documentation` skill is a small repository reference skill. It names
the actual pages, the `xplane_fdr.__all__` public contract, the API-reference
directive, format/capture accuracy boundaries, and all three local validation
commands.

### Baseline (without the new skill)

A fresh subagent was asked for the exact repository documentation workflow.
It found the broad page list and the main format boundaries, but its own
uncertainty identified the gap: it could not provide a configured link-check
workflow and noted that `quality.py docs` only runs Interrogate. It also did not
identify the concrete MkDocstrings API-reference directive. This was the
baseline failure: an incomplete, not directly executable documentation
workflow.

### Forward test (with the new skill)

A second fresh subagent read `.codex/skills/documentation/SKILL.md` before
answering the same request. It named `README.md`, `docs/index.md`,
`docs/usage/fdr-toolkit.md`, `docs/reference/fdr.md`, and `mkdocs.yml`; required
the deliberate `xplane_fdr.__all__` surface and `::: xplane_fdr`; preserved all
format/capture/GeoJSON boundaries; and gave this exact validation sequence:

```powershell
uv run python -m unittest tests.test_public_api tests.test_documentation -v
uv run mkdocs build --strict
uv run python tools/quality.py docs
```

It correctly explained that the strict MkDocs build renders the API reference
and validates navigation plus configured link warnings, while the quality gate
only runs Interrogate. This closes the baseline gap without adding an unrelated
tool or deployment action.

## Documentation build and verification

```powershell
uv run mkdocs build --strict
```

Exit status 0; the site built successfully. The installed Material theme emitted
its upstream MkDocs 2.0 migration notice, but MkDocs reported no project
warning/error and completed the strict build.

```powershell
uv run python tools/quality.py docs
```

Exit status 0. Interrogate passed with `43.5%` coverage against its `40.0%`
minimum.

```powershell
uv run python -m unittest discover -v
```

Exit status 0: `Ran 158 tests in 0.308s`, `OK`.

`git diff --check` also completed with exit status 0.

## Files changed

- `README.md`, `CHANGELOG.md`, and `BACKLOG.md`
- `mkdocs.yml`, `docs/index.md`, `docs/usage/fdr-toolkit.md`, and
  `docs/reference/fdr.md`, and `docs/schemas/fdr-record-config-v1.schema.json`
- `tests/test_public_api.py`, `tests/test_documentation.py`, and
  `tests/test_project_skills.py`
- `.codex/skills/documentation/SKILL.md`
- `HANDOFF.md`

## Self-review

- Confirmed that only canonical v4 is documented as output and that v3
  normalization is explicit and lossy.
- Confirmed no capture adapter, connection, cadence scheduler, plugin
  lifecycle, live-record command, network client, or simulator dependency is
  represented as bundled.
- Confirmed storage precedence, partial recovery, explicit overwrite, strict
  JSON configuration/schema, 2D GeoJSON/MSL handling, and XPPython3 released
  wheel guidance are all covered.
- Confirmed the forward-tested documentation skill contains no stale project
  names and uses only the repository's actual commands.
- An independent review found and the follow-up RED/GREEN contract corrected
  the hosted-schema publication gap; no Critical or remaining Important review
  finding remains.
