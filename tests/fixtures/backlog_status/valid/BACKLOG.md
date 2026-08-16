# Fixture Backlog

## Current position

- Active child: —.

## Local child inventory

| Child | Outcome | Status | Depends on | Spec | Plan | Gates | Review | Resume | Reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `T1.1` | Markdown authority contract and explicit inventory normalization | `verified` | `M0` | [design](docs/superpowers/specs/t1-design.md) | [plan](docs/superpowers/plans/t1-1.md) | 1/1 | [review](.superpowers/sdd/t1-1/review.md) | — | — |
| `T1.2` | Typed parser, status report, and versioned JSON | `specified` | `T1.1` | [design](docs/superpowers/specs/t1-design.md) | — | 0/1 | — | — | — |

## Local-child acceptance gates

### T1.1 — Markdown authority contract and explicit inventory normalization

- [x] Frozen contract is verified and
      remains explicit. — Evidence: [verification](.superpowers/sdd/t1-1/gate-1.md)

### T1.2 — Typed parser, status report, and versioned JSON

- [ ] Frozen parser remains open.

## Release-gate dashboard

| Gate | Outcome | Gate state | Prerequisites | Evidence |
| --- | --- | --- | --- | --- |
| `G1` | Canonical vertical-slice reconciliation | `waiting` | `T1.2` | — |
