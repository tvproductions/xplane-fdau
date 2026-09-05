# Dependency and tool inventory

Use this checklist for discovery, not as a requirement to add or update a
technology the repository does not already use.

## Project manifests and lockfiles

- Python: `pyproject.toml`, `uv.lock`, requirements or constraints files, build
  backend pins, dependency groups, and tool configuration with version floors.
- JavaScript/TypeScript: `package.json`, npm/pnpm/yarn/bun lockfiles, package
  manager declarations, and workspace manifests.
- Other ecosystems: Cargo, Go modules, .NET/NuGet, Ruby/Bundler, JVM build
  files, PHP/Composer, and language-specific tool manifests evidenced in the
  tree.

## Runtime and package-manager pins

- Runtime-version files and manifest constraints.
- Package-manager version or required-version fields.
- Dev-container, toolchain, environment-manager, and CI setup versions.

## Repository automation

- Pre-commit hook revisions and hook-managed tool versions.
- GitHub Actions or other CI actions pinned to release tags or commit SHAs.
- Container base images and explicitly versioned build images.
- Documentation-generation, packaging, release, and code-generation tools.

## Vendored or separately installed tools

- Checked-in binaries, downloaded archives, Git submodules, or Git-based tool
  installs.
- Project bootstrap scripts that install named global tools.
- Agent workflow dependencies such as a separately pinned skill or helper
  repository.

Treat machine-global tools as project-managed only when the repository records
their required version or its bootstrap process owns their installation.
