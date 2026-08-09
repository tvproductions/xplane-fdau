from pathlib import Path
import unittest


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "fdr"


class FDRFixtureTests(unittest.TestCase):
    def test_minimal_fixtures_and_provenance_are_committed(self) -> None:
        for name in (
            "version3-minimal.fdr",
            "version4-minimal.fdr",
            "inherited-recorder-minimal.fdr",
        ):
            with self.subTest(name=name):
                self.assertTrue((FIXTURE_ROOT / name).is_file())
        provenance = (FIXTURE_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("Laminar Research", provenance)
        self.assertIn("independently minimized", provenance)


if __name__ == "__main__":
    unittest.main()
