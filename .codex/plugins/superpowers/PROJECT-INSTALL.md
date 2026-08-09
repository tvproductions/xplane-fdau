# Superpowers Project Install

Source: https://github.com/obra/superpowers
Version: 6.2.0
Commit: 3dcbd5c4b48e02263fbf4a3c01e3fe4f81d584d9

This project vendors a fresh Superpowers installation for Codex in two places:

- `.codex/skills/`: project-local skills loaded by Codex for this repository.
- `.codex/plugins/superpowers/`: a self-contained copy of the Codex plugin
  metadata, assets, hooks, license, README, and skills.

Project-specific operational skills are maintained for `xplane-fdau` beneath
`.codex/skills/`. They preserve this project's standard-library-only runtime,
`unittest`, and unreleased non-publishing contracts. Instructions in `AGENTS.md`
take precedence.
