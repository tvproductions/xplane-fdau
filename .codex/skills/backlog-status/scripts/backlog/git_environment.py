"""Keep explicit-root Git operations independent of their caller's hook state."""

from __future__ import annotations

import os

_LOCAL_ENVIRONMENT = frozenset(
    {
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        "GIT_COMMON_DIR",
        "GIT_CONFIG",
        "GIT_CONFIG_COUNT",
        "GIT_CONFIG_PARAMETERS",
        "GIT_DIR",
        "GIT_GRAFT_FILE",
        "GIT_IMPLICIT_WORK_TREE",
        "GIT_INDEX_FILE",
        "GIT_NO_REPLACE_OBJECTS",
        "GIT_OBJECT_DIRECTORY",
        "GIT_PREFIX",
        "GIT_REPLACE_REF_BASE",
        "GIT_SHALLOW_FILE",
        "GIT_WORK_TREE",
    }
)


def git_environment() -> dict[str, str]:
    """Preserve process settings while clearing Git's repository-local routing.

    These names come from ``git rev-parse --local-env-vars``. Hook inheritance
    otherwise defeats an explicit ``git -C`` target, including test fixtures.
    """
    return {key: value for key, value in os.environ.items() if key not in _LOCAL_ENVIRONMENT and not key.startswith(("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_"))}
