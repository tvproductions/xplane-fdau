from __future__ import annotations

from dataclasses import dataclass
import importlib.util
from io import StringIO
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / ".codex/skills/backlog-status/scripts"
FIXTURE = ROOT / "tests/fixtures/backlog_status/valid"
sys.path.insert(0, str(SCRIPTS))

from backlog.model import GitState  # noqa: E402  # ty: ignore[unresolved-import]


@dataclass(frozen=True, slots=True)
class CliResult:
    code: int
    stdout: str
    stderr: str


def load_cli() -> object:
    path = SCRIPTS / "backlog_status.py"
    specification = importlib.util.spec_from_file_location("backlog_status_cli", path)
    if specification is None or specification.loader is None:
        raise RuntimeError("cannot load backlog status CLI")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


class BacklogStatusCliTests(unittest.TestCase):
    def malformed_fixture(self) -> Path:
        temporary = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, temporary)
        shutil.copytree(FIXTURE, temporary, dirs_exist_ok=True)
        backlog = temporary / "BACKLOG.md"
        backlog.write_text(backlog.read_text(encoding="utf-8").replace("0/1", "0/x", 1), encoding="utf-8")
        return temporary

    def run_cli(self, argv: list[str], *, root: Path) -> CliResult:
        module = load_cli()
        output = StringIO()
        errors = StringIO()
        with patch.object(module, "observe_git", return_value=GitState("main", False, ())):
            code = module.main(  # ty: ignore[unresolved-attribute]
                argv, root=root, stdout=output, stderr=errors
            )
        return CliResult(code, output.getvalue(), errors.getvalue())

    def test_status_writes_human_report_to_stdout(self) -> None:
        status = self.run_cli(["status"], root=FIXTURE)

        self.assertEqual(0, status.code)
        self.assertIn("Repository: xplane-fdau", status.stdout)
        self.assertEqual("", status.stderr)

    def test_status_json_writes_schema_version_one_in_source_order(self) -> None:
        status = self.run_cli(["status", "--json"], root=FIXTURE)

        self.assertEqual(0, status.code)
        self.assertEqual("", status.stderr)
        payload = json.loads(status.stdout)
        self.assertEqual(1, payload["schema_version"])
        self.assertTrue(payload["valid"])
        self.assertEqual([], payload["findings"])
        self.assertIsNone(payload["recommendation"])
        self.assertNotIn("timestamp", payload)
        self.assertEqual(["T1.1", "T1.2"], [child["id"] for child in payload["roadmap"]["local_children"]])
        self.assertEqual(["T1.1", "T1.2"], [child["id"] for child in payload["backlog"]["children"]])

    def test_current_repository_status_reports_human_and_json(self) -> None:
        human = self.run_cli(["status"], root=ROOT)

        self.assertEqual(0, human.code, human.stderr)
        self.assertIn("54 local children", human.stdout)

        machine = self.run_cli(["status", "--json"], root=ROOT)

        self.assertEqual(0, machine.code, machine.stderr)
        payload = json.loads(machine.stdout)
        self.assertTrue(payload["valid"])
        self.assertEqual([], payload["findings"])
        self.assertIsNone(payload["recommendation"])
        self.assertEqual(54, len(payload["roadmap"]["local_children"]))
        self.assertEqual(54, len(payload["backlog"]["children"]))

    def test_unknown_command_is_invalid_usage(self) -> None:
        invalid = self.run_cli(["audit"], root=FIXTURE)

        self.assertEqual(2, invalid.code)
        self.assertIn("invalid choice", invalid.stderr)

    def test_malformed_repository_writes_parse_context_to_stderr(self) -> None:
        malformed = self.run_cli(["status"], root=self.malformed_fixture())

        self.assertEqual(1, malformed.code)
        self.assertEqual("", malformed.stdout)
        self.assertRegex(malformed.stderr, r"BACKLOG.md:[0-9]+:")


if __name__ == "__main__":
    unittest.main()
