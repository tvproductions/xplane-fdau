# C1.2 independent implementation review

- **Child:** `C1.2`
- **Gate:** —
- **Kind:** review
- **Result:** accepted
- **Date:** 2026-10-04
- **Subject:** Identity, hashing, references, authority, and provenance.

One fresh-context independent reviewer inspected `8bd7bc288eb0fd4f4ae14be204dfdcc04ce91174..dfd5856b1354aaedf9eb6b49b29269bea698413e` using the Superpowers requesting-code-review workflow and canonical `gzs-change-review` v0.5.0. The review covered the source specification, approved C1.2 plan, ledger rulings, four acceptance gates, all changed runtime code, public and installed surfaces, and adversarial programmatic inputs. Its 35 focused tests and backlog audit passed.

The reviewer reported no Critical or Minor findings and five Important findings:

1. Parameter conversion descended before bounded validation, allowing `RecursionError` for cyclic or very deep dictionaries.
2. Nested mappings were copied inside tuples but rejected inside lists.
3. Generated algorithm-reference equality treated Boolean, integer, and real parameter values as equal.
4. Field-by-field semantic validation masked later shape or canonical-domain errors.
5. Revision/counter signed-64-bit overflow had a semantic exception class, contrary to the specification; the plan also encoded that conflict.

The executor reproduced these with 14 behavior assertion failures and corrected them in `c0cc603`. Bounded recursive copying retains the first excessive-depth container for the canonical encoder to diagnose in lexical key order. Both array forms copy nested mappings. Algorithm-reference equality compares canonical parameter bytes. Explicit model-wide field checks run shape, canonical domain, then semantic validation. Signed-64-bit overflow is `CanonicalJSONError`; in-domain range violations remain `ContractValidationError`. The conflicting plan text was corrected. The final focused integration run passed 41 tests with Ruff and ty. No second review was dispatched, following the approved native execution workflow; acceptance is the executor's disposition of the independent findings after regression verification.

Closeout also identified and corrected secret-scanner false positives on literal public digest vectors, a runtime assertion in provenance deduplication, and missing public model docstrings. The security and docstring checks passed after those corrections. Complete hygiene and external installed-wheel evidence are recorded in `completion.md`.

The review deliberately set aside later model factories, public model hash dispatch, loaders, schemas, loaded-document integration, semantic validation of private hash-helper input trees, Python dictionary-key hashability, and pending full-gate/artifact results. Executor rulings are retained in `progress.md`; the approved boundary and already-validated private-helper input contract stand. Python `hash()` support is not added. Final artifact and gate results are supplied by the executor.
