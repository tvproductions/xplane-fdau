"""Tests for release artifact validation."""

from __future__ import annotations

import io
from pathlib import Path
import tarfile
import tempfile
import unittest
import zipfile

from tools import release


class ReleaseToolTests(unittest.TestCase):
    def _make_dist(
        self,
        directory: Path,
        *,
        extra_member: str | None = None,
        build_marker: bool = False,
        sdist_requires_dist: bool = False,
        sdist_extra_license: bool = False,
    ) -> None:
        wheel = directory / "xplane_fdr-0.1.0-py3-none-any.whl"
        with zipfile.ZipFile(wheel, "w") as archive:
            archive.writestr(
                "xplane_fdr-0.1.0.dist-info/METADATA",
                "Metadata-Version: 2.4\nName: xplane-fdr\nVersion: 0.1.0\nRequires-Python: >=3.12\n",
            )
            archive.writestr("xplane_fdr-0.1.0.dist-info/licenses/LICENSE", "MIT\n")
            for source in Path("xplane_fdr").rglob("*.py"):
                archive.writestr(source.as_posix(), source.read_text(encoding="utf-8"))
            archive.writestr(
                "xplane_fdr/schemas/fdr-record-config-v1.schema.json",
                Path("xplane_fdr/schemas/fdr-record-config-v1.schema.json").read_text(encoding="utf-8"),
            )
            if extra_member is not None:
                archive.writestr(extra_member, "forbidden\n")

        sdist = directory / "xplane_fdr-0.1.0.tar.gz"
        with tarfile.open(sdist, "w:gz") as archive:
            archive.addfile(tarfile.TarInfo("xplane_fdr-0.1.0"))
            metadata = b"Metadata-Version: 2.4\nName: xplane-fdr\nVersion: 0.1.0\nRequires-Python: >=3.12\n"
            if sdist_requires_dist:
                metadata += b"Requires-Dist: forbidden\n"
            members = [
                ("xplane_fdr-0.1.0/LICENSE", b"MIT\n"),
                ("xplane_fdr-0.1.0/PKG-INFO", metadata),
            ]
            members.extend((f"xplane_fdr-0.1.0/{source.as_posix()}", source.read_bytes()) for source in Path("xplane_fdr").rglob("*.py"))
            members.append(
                (
                    "xplane_fdr-0.1.0/xplane_fdr/schemas/fdr-record-config-v1.schema.json",
                    Path("xplane_fdr/schemas/fdr-record-config-v1.schema.json").read_bytes(),
                )
            )
            if sdist_extra_license:
                members.append(("xplane_fdr-0.1.0/docs/LICENSE", b"duplicate\n"))
            for name, payload in members:
                member = tarfile.TarInfo(name)
                member.size = len(payload)
                archive.addfile(member, io.BytesIO(payload))
        if build_marker:
            (directory / ".gitignore").write_text("*\n", encoding="utf-8")

    def test_check_dist_accepts_required_universal_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            self._make_dist(directory)

            artifacts = release.check_dist(directory)

        self.assertEqual("xplane_fdr-0.1.0-py3-none-any.whl", artifacts.wheel.name)
        self.assertEqual("xplane_fdr-0.1.0.tar.gz", artifacts.sdist.name)
        self.assertEqual(64, len(artifacts.wheel_sha256))

    def test_check_dist_rejects_forbidden_archive_member(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            self._make_dist(directory, extra_member="xplane_fdr-0.1.0/.codex/skills/release/SKILL.md")

            with self.assertRaisesRegex(release.ReleaseError, "forbidden"):
                release.check_dist(directory)

    def test_check_dist_ignores_uv_build_marker_but_no_other_extra_file(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            self._make_dist(directory, build_marker=True)

            release.check_dist(directory)

    def test_check_dist_rejects_sdist_runtime_requirement(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            self._make_dist(directory, sdist_requires_dist=True)

            with self.assertRaisesRegex(release.ReleaseError, "Requires-Dist"):
                release.check_dist(directory)

    def test_check_dist_rejects_unexpected_dist_directory(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            self._make_dist(directory)
            (directory / "unexpected").mkdir()

            with self.assertRaisesRegex(release.ReleaseError, "exactly"):
                release.check_dist(directory)

    def test_check_dist_rejects_second_sdist_license(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            self._make_dist(directory, sdist_extra_license=True)

            with self.assertRaisesRegex(release.ReleaseError, "exactly one LICENSE"):
                release.check_dist(directory)

    def test_validate_tag_requires_exact_project_version(self) -> None:
        self.assertEqual("0.1.0", release.validate_tag("v0.1.0"))
        with self.assertRaisesRegex(release.ReleaseError, "v0.1.0"):
            release.validate_tag("v0.1.1")


if __name__ == "__main__":
    unittest.main()
