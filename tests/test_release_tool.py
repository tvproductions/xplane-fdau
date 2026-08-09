"""Tests for release artifact validation."""

from __future__ import annotations

import io
from pathlib import Path
import stat
import tarfile
import tempfile
import unittest
import warnings
import zipfile
from unittest.mock import patch

from tools import release


class ReleaseToolTests(unittest.TestCase):
    def _package_files(self) -> dict[str, bytes]:
        files: dict[str, bytes] = {}
        for source in Path("xplane_fdr").rglob("*"):
            if source.is_file() and (source.suffix == ".py" or source.name == "py.typed" or source.suffix == ".json"):
                files[source.as_posix()] = source.read_bytes()
        return files

    def _make_dist(
        self,
        directory: Path,
        *,
        wheel_metadata: bytes | None = None,
        wheel_tag: bytes | None = None,
        wheel_updates: dict[str, bytes] | None = None,
        wheel_duplicates: tuple[str, bytes] | None = None,
        wheel_link: str | None = None,
        tar_updates: dict[str, bytes] | None = None,
        tar_link: tuple[str, str] | None = None,
    ) -> None:
        metadata = wheel_metadata or b"Metadata-Version: 2.4\nName: xplane-fdr\nVersion: 0.1.0\nRequires-Python: >=3.12\n"
        wheel_files = self._package_files()
        wheel_files.update(
            {
                "xplane_fdr-0.1.0.dist-info/METADATA": metadata,
                "xplane_fdr-0.1.0.dist-info/WHEEL": wheel_tag or b"Wheel-Version: 1.0\nGenerator: test\nRoot-Is-Purelib: true\nTag: py3-none-any\n",
                "xplane_fdr-0.1.0.dist-info/RECORD": b"",
                "xplane_fdr-0.1.0.dist-info/licenses/LICENSE": Path("LICENSE").read_bytes(),
            }
        )
        if wheel_updates:
            wheel_files.update(wheel_updates)
        wheel = directory / "xplane_fdr-0.1.0-py3-none-any.whl"
        with zipfile.ZipFile(wheel, "w") as archive:
            for name in ("xplane_fdr/", "xplane_fdr/schemas/", "xplane_fdr-0.1.0.dist-info/", "xplane_fdr-0.1.0.dist-info/licenses/"):
                archive.writestr(name, b"")
            for name, payload in wheel_files.items():
                if name == wheel_link:
                    link = zipfile.ZipInfo(name)
                    link.external_attr = (stat.S_IFLNK | 0o777) << 16
                    archive.writestr(link, b"target")
                else:
                    archive.writestr(name, payload)
            if wheel_duplicates:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", UserWarning)
                    archive.writestr(*wheel_duplicates)

        tar_files = {f"xplane_fdr-0.1.0/{name}": payload for name, payload in self._package_files().items()}
        tar_files.update(
            {
                "xplane_fdr-0.1.0/LICENSE": Path("LICENSE").read_bytes(),
                "xplane_fdr-0.1.0/PKG-INFO": metadata,
                "xplane_fdr-0.1.0/pyproject.toml": Path("pyproject.toml").read_bytes(),
            }
        )
        if tar_updates:
            tar_files.update(tar_updates)
        sdist = directory / "xplane_fdr-0.1.0.tar.gz"
        with tarfile.open(sdist, "w:gz") as archive:
            root = tarfile.TarInfo("xplane_fdr-0.1.0")
            root.type = tarfile.DIRTYPE
            archive.addfile(root)
            for name in ("xplane_fdr-0.1.0/xplane_fdr", "xplane_fdr-0.1.0/xplane_fdr/schemas"):
                directory_member = tarfile.TarInfo(name)
                directory_member.type = tarfile.DIRTYPE
                archive.addfile(directory_member)
            for name, payload in tar_files.items():
                member = tarfile.TarInfo(name)
                member.size = len(payload)
                archive.addfile(member, io.BytesIO(payload))
            if tar_link:
                name, target = tar_link
                member = tarfile.TarInfo(name)
                member.type = tarfile.SYMTYPE
                member.linkname = target
                archive.addfile(member)

    def test_check_dist_accepts_complete_realistic_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            self._make_dist(directory)

            artifacts = release.check_dist(directory)

        self.assertEqual("xplane_fdr-0.1.0-py3-none-any.whl", artifacts.wheel.name)
        self.assertEqual("xplane_fdr-0.1.0.tar.gz", artifacts.sdist.name)

    def test_check_dist_rejects_hostile_metadata_and_internal_wheel_tag(self) -> None:
        cases = {
            "x-name": b"Metadata-Version: 2.4\nX-Name: xplane-fdr\nVersion: 0.1.0\nRequires-Python: >=3.12\n",
            "dev-version": b"Metadata-Version: 2.4\nName: xplane-fdr\nVersion: 0.1.0.dev1\nRequires-Python: >=3.12\n",
            "broadened-python": b"Metadata-Version: 2.4\nName: xplane-fdr\nVersion: 0.1.0\nRequires-Python: >=3.11\n",
            "lowercase-requires-dist": b"Metadata-Version: 2.4\nName: xplane-fdr\nVersion: 0.1.0\nRequires-Python: >=3.12\nrequires-dist: hostile\n",
        }
        for name, metadata in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as raw:
                self._make_dist(Path(raw), wheel_metadata=metadata)
                with self.assertRaises(release.ReleaseError):
                    release.check_dist(Path(raw))
        with tempfile.TemporaryDirectory() as raw:
            self._make_dist(Path(raw), wheel_tag=b"Wheel-Version: 1.0\nTag: cp312-cp312-win_amd64\n")
            with self.assertRaisesRegex(release.ReleaseError, "WHEEL"):
                release.check_dist(Path(raw))

    def test_release_version_is_pinned_and_metadata_defects_are_rejected(self) -> None:
        with patch.object(release, "_project_version", return_value="0.1.0.dev1"), patch.object(release, "_version_from_source", return_value="0.1.0.dev1"):
            with self.assertRaisesRegex(release.ReleaseError, "0.1.0"):
                release.validate_tag("v0.1.0.dev1")
        malformed = {
            "space-before-colon": b"Metadata-Version: 2.4\nName: xplane-fdr\nVersion: 0.1.0\nRequires-Python: >=3.12\nRequires-Dist : hostile\n",
            "non-header": b"Metadata-Version: 2.4\nName: xplane-fdr\nVersion: 0.1.0\nRequires-Python: >=3.12\nthis is not a header\n",
        }
        for name, metadata in malformed.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as raw:
                self._make_dist(Path(raw), wheel_metadata=metadata)
                with self.assertRaisesRegex(release.ReleaseError, "metadata"):
                    release.check_dist(Path(raw))

    def test_check_dist_requires_canonical_sdist_pyproject_and_exactly_one_wheel_license(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            self._make_dist(
                Path(raw),
                tar_updates={"xplane_fdr-0.1.0/pyproject.toml": b"[project]\nname = 'xplane-fdr'\nversion = '9.9.9'\ndependencies = ['hostile']\n"},
            )
            with self.assertRaisesRegex(release.ReleaseError, "pyproject"):
                release.check_dist(Path(raw))
        with tempfile.TemporaryDirectory() as raw:
            self._make_dist(Path(raw), wheel_updates={"xplane_fdr-0.1.0.dist-info/licenses/third/LICENSE": b"duplicate"})
            with self.assertRaisesRegex(release.ReleaseError, "exactly one LICENSE"):
                release.check_dist(Path(raw))

    def test_check_dist_accepts_semantically_identical_sdist_pyproject(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            self._make_dist(Path(raw), tar_updates={"xplane_fdr-0.1.0/pyproject.toml": Path("pyproject.toml").read_bytes() + b"\n"})
            release.check_dist(Path(raw))

    def test_check_dist_requires_exact_package_contents_schema_and_license_locations(self) -> None:
        expected_schema = "xplane_fdr/schemas/fdr-record-config-v1.schema.json"
        cases = {
            "corrupt-wheel-schema": {expected_schema: b"{}\n"},
            "unexpected-native": {"xplane_fdr/hostile.pyd": b"native"},
            "unexpected-module": {"xplane_fdr/hostile.py": b""},
            "relocated-license": {
                "xplane_fdr-0.1.0.dist-info/licenses/LICENSE": b"",
                "xplane_fdr-0.1.0.dist-info/LICENSE": Path("LICENSE").read_bytes(),
            },
        }
        for name, updates in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as raw:
                self._make_dist(Path(raw), wheel_updates=updates)
                with self.assertRaises(release.ReleaseError):
                    release.check_dist(Path(raw))
        with tempfile.TemporaryDirectory() as raw:
            self._make_dist(Path(raw), tar_updates={f"xplane_fdr-0.1.0/{expected_schema}": b"{}\n"})
            with self.assertRaises(release.ReleaseError):
                release.check_dist(Path(raw))

    def test_check_dist_rejects_unsafe_archive_paths_duplicates_and_links(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            self._make_dist(Path(raw), wheel_updates={"xplane_fdr/..\\evil.py": b""})
            with self.assertRaisesRegex(release.ReleaseError, "path"):
                release.check_dist(Path(raw))
        with tempfile.TemporaryDirectory() as raw:
            self._make_dist(Path(raw), wheel_duplicates=("xplane_fdr/__init__.py", b"duplicate"))
            with self.assertRaisesRegex(release.ReleaseError, "duplicate"):
                release.check_dist(Path(raw))
        with tempfile.TemporaryDirectory() as raw:
            self._make_dist(Path(raw), tar_link=("xplane_fdr-0.1.0/xplane_fdr/link.py", "../../evil.py"))
            with self.assertRaisesRegex(release.ReleaseError, "link"):
                release.check_dist(Path(raw))
        with tempfile.TemporaryDirectory() as raw:
            self._make_dist(Path(raw), wheel_link="xplane_fdr-0.1.0.dist-info/RECORD")
            with self.assertRaisesRegex(release.ReleaseError, "link"):
                release.check_dist(Path(raw))

    def test_validate_tag_requires_exact_project_version(self) -> None:
        self.assertEqual("0.1.0", release.validate_tag("v0.1.0"))
        with self.assertRaisesRegex(release.ReleaseError, "v0.1.0"):
            release.validate_tag("v0.1.1")


if __name__ == "__main__":
    unittest.main()
