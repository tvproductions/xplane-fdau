# Fixture Roadmap

## Milestones

| Milestone | Outcome |
| --- | --- |
| `M0` | Frozen migration baseline |

## T1 — Repository governance tooling epic

| Child | Outcome | Depends on |
| --- | --- | --- |
| `T1.1` | Markdown authority contract and explicit inventory normalization | `M0` |
| `T1.2` | Typed parser, status report, and versioned JSON | `T1.1` |

## Release gates

| Gate | Outcome | Depends on |
| --- | --- | --- |
| `G1` | Canonical vertical-slice reconciliation | `T1.2` |

## External consumer and downstream boundaries

| Boundary | Outcome | Owner | xplane-fdau handoff condition |
| --- | --- | --- | --- |
| `I1.1` | Fixture contract adoption | Fixture consumer | Adoption begins after `T1.2`. |
