"""Adversarial tests for the complete runtime import boundary."""

from __future__ import annotations

from pathlib import Path
import unittest

from tools.runtime_imports import runtime_import_violations


ROOT = Path(__file__).resolve().parents[1]


class RuntimeImportBoundaryTests(unittest.TestCase):
    """Keep every shipped module package-local, synchronous, and host-neutral."""

    def test_every_runtime_module_uses_only_approved_static_imports(self) -> None:
        """Adding any unapproved edge anywhere in the wheel must fail."""
        violations: list[str] = []
        for path in sorted((ROOT / "xplane_fdau").rglob("*.py")):
            violations.extend(
                runtime_import_violations(
                    path.read_text(encoding="utf-8"),
                    filename=str(path.relative_to(ROOT)),
                )
            )

        self.assertEqual([], violations)

    def test_guard_accepts_stdlib_package_local_and_relative_imports(self) -> None:
        """The guard must not reject the supported runtime dependency directions."""
        source = """
from __future__ import annotations
from importlib import resources
from pathlib import Path
import xplane_fdau.formats.xplane_fdr
from . import models
from ..formats import xplane_fdr
"""

        self.assertEqual((), runtime_import_violations(source))

    def test_guard_rejects_providers_network_clients_and_third_party_imports(self) -> None:
        """Every forbidden static root must be diagnosed independently."""
        for module in (
            "xplane_fdr",
            "xpwebapi",
            "XPPython3",
            "xp",
            "XPLM",
            "q4xpcc",
            "socket",
            "http.client",
            "urllib.request",
            "requests",
        ):
            with self.subTest(module=module):
                violations = runtime_import_violations(f"import {module}\n")
                self.assertEqual(1, len(violations))
                self.assertIn(module.split(".", 1)[0], violations[0])

    def test_guard_rejects_direct_aliased_and_indirect_dynamic_imports(self) -> None:
        """Renaming or copying a loader must not bypass the runtime boundary."""
        cases = {
            "builtin": '__import__("requests")',
            "builtins attribute": 'import builtins\nbuiltins.__import__("requests")',
            "module alias": 'import importlib as loader\nloader.import_module("requests")',
            "symbol alias": 'from importlib import import_module as load\nload("requests")',
            "assigned alias": 'import importlib\nload = importlib.import_module\nload("requests")',
            "getattr alias": 'import importlib as loader\ngetattr(loader, "import_module")("requests")',
            "module spec": "from importlib.util import module_from_spec as build\nbuild(spec)",
            "run module": 'import runpy\nrunpy.run_module("payload")',
            "resolve name": 'import pkgutil\npkgutil.resolve_name("payload:entry")',
        }

        for name, source in cases.items():
            with self.subTest(name=name):
                violations = runtime_import_violations(source)
                self.assertTrue(violations)
                self.assertIn("dynamic import", violations[0])


if __name__ == "__main__":
    unittest.main()
