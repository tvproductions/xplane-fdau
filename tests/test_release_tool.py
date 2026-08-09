"""Tests for release artifact validation."""

from __future__ import annotations

import base64
import csv
import hashlib
import io
from pathlib import Path
import stat
import tarfile
import tempfile
import unittest
import warnings
import zipfile
from collections.abc import Callable
from contextlib import redirect_stderr

from tools import release


class ReleaseToolTests(unittest.TestCase):
    def _package_files(self) -> dict[str, bytes]:
        files: dict[str, bytes] = {}
        for source in Path("xplane_fdau").rglob("*"):
            if source.is_file() and (source.suffix == ".py" or source.name == "py.typed" or source.suffix == ".json"):
                files[source.as_posix()] = source.read_bytes()
        return files

    def _wheel_record(self, files: dict[str, bytes], record_name: str) -> bytes:
        output = io.StringIO(newline="")
        writer = csv.writer(output, lineterminator="\n")
        for name, payload in sorted(files.items()):
            if name == record_name:
                continue
            digest = base64.urlsafe_b64encode(hashlib.sha256(payload).digest()).rstrip(b"=").decode("ascii")
            writer.writerow((name, f"sha256={digest}", str(len(payload))))
        writer.writerow((record_name, "", ""))
        return output.getvalue().encode("utf-8")

    def _replace_record_field(self, payload: bytes, row: int, column: int, value: str) -> bytes:
        rows = list(csv.reader(io.StringIO(payload.decode("utf-8"), newline=""), strict=True))
        rows[row][column] = value
        output = io.StringIO(newline="")
        writer = csv.writer(output, lineterminator="\n")
        writer.writerows(rows)
        return output.getvalue().encode("utf-8")

    def _make_dist(
        self,
        directory: Path,
        *,
        wheel_metadata: bytes | None = None,
        wheel_tag: bytes | None = None,
        wheel_updates: dict[str, bytes] | None = None,
        wheel_remove: set[str] | None = None,
        wheel_record: bytes | Callable[[bytes], bytes] | None = None,
        wheel_duplicates: tuple[str, bytes] | None = None,
        wheel_link: str | None = None,
        tar_updates: dict[str, bytes] | None = None,
        tar_remove: set[str] | None = None,
        tar_link: tuple[str, str] | None = None,
    ) -> None:
        metadata = wheel_metadata or b"Metadata-Version: 2.4\nName: xplane-fdau\nVersion: 0.1.0\nRequires-Python: >=3.12\n"
        record_name = "xplane_fdau-0.1.0.dist-info/RECORD"
        wheel_files = self._package_files()
        wheel_files.update(
            {
                "xplane_fdau-0.1.0.dist-info/METADATA": metadata,
                "xplane_fdau-0.1.0.dist-info/WHEEL": wheel_tag or b"Wheel-Version: 1.0\nGenerator: test\nRoot-Is-Purelib: true\nTag: py3-none-any\n",
                "xplane_fdau-0.1.0.dist-info/entry_points.txt": b"[console_scripts]\nxplane-fdau = xplane_fdau.cli:main\n\n",
                "xplane_fdau-0.1.0.dist-info/licenses/LICENSE": Path("LICENSE").read_bytes(),
            }
        )
        if wheel_updates:
            wheel_files.update(wheel_updates)
        for name in wheel_remove or ():
            wheel_files.pop(name, None)
        if record_name not in (wheel_remove or set()):
            generated_record = self._wheel_record(wheel_files, record_name)
            if isinstance(wheel_record, bytes):
                wheel_files[record_name] = wheel_record
            elif wheel_record is not None:
                wheel_files[record_name] = wheel_record(generated_record)
            else:
                wheel_files[record_name] = generated_record
        wheel = directory / "xplane_fdau-0.1.0-py3-none-any.whl"
        with zipfile.ZipFile(wheel, "w") as archive:
            for name in (
                "xplane_fdau/",
                "xplane_fdau/formats/",
                "xplane_fdau/formats/xplane_fdr/",
                "xplane_fdau/formats/xplane_fdr/schemas/",
                "xplane_fdau/sinks/",
                "xplane_fdau-0.1.0.dist-info/",
                "xplane_fdau-0.1.0.dist-info/licenses/",
            ):
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

        tar_files = {f"xplane_fdau-0.1.0/{name}": payload for name, payload in self._package_files().items()}
        tar_files.update(
            {
                "xplane_fdau-0.1.0/LICENSE": Path("LICENSE").read_bytes(),
                "xplane_fdau-0.1.0/PKG-INFO": metadata,
                "xplane_fdau-0.1.0/pyproject.toml": Path("pyproject.toml").read_bytes(),
                "xplane_fdau-0.1.0/pyproject.toml.orig": Path("pyproject.toml").read_bytes(),
                "xplane_fdau-0.1.0/README.md": Path("README.md").read_bytes(),
            }
        )
        if tar_updates:
            tar_files.update(tar_updates)
        for name in tar_remove or ():
            tar_files.pop(name, None)
        sdist = directory / "xplane_fdau-0.1.0.tar.gz"
        with tarfile.open(sdist, "w:gz") as archive:
            root = tarfile.TarInfo("xplane_fdau-0.1.0")
            root.type = tarfile.DIRTYPE
            archive.addfile(root)
            for name in (
                "xplane_fdau-0.1.0/xplane_fdau",
                "xplane_fdau-0.1.0/xplane_fdau/formats",
                "xplane_fdau-0.1.0/xplane_fdau/formats/xplane_fdr",
                "xplane_fdau-0.1.0/xplane_fdau/formats/xplane_fdr/schemas",
                "xplane_fdau-0.1.0/xplane_fdau/sinks",
            ):
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

        self.assertEqual("xplane_fdau-0.1.0-py3-none-any.whl", artifacts.wheel.name)
        self.assertEqual("xplane_fdau-0.1.0.tar.gz", artifacts.sdist.name)

    def test_check_dist_rejects_invalid_wheel_record_manifests(self) -> None:
        digest = base64.urlsafe_b64encode(hashlib.sha256(b"").digest()).rstrip(b"=").decode("ascii")
        cases: dict[str, bytes | Callable[[bytes], bytes]] = {
            "empty": b"",
            "malformed-encoding": b"\xff",
            "malformed-csv": b'"unterminated,sha256=AAAA,1\n',
            "wrong-column-count": b"only,two\n",
            "missing-row": lambda payload: b"\n".join(payload.splitlines()[1:]) + b"\n",
            "extra-row": lambda payload: payload + f"extra.py,sha256={digest},0\n".encode(),
            "duplicate-row": lambda payload: payload + payload.splitlines(keepends=True)[0],
            "traversal-row": lambda payload: payload + f"../evil.py,sha256={digest},0\n".encode(),
            "wrong-digest": lambda payload: self._replace_record_field(payload, 0, 1, f"sha256={'A' * 43}"),
            "padded-digest": lambda payload: self._replace_record_field(payload, 0, 1, f"sha256={'A' * 43}="),
            "invalid-algorithm": lambda payload: self._replace_record_field(payload, 0, 1, f"md5={'A' * 43}"),
            "wrong-size": lambda payload: self._replace_record_field(payload, 0, 2, "999999"),
            "non-decimal-size": lambda payload: self._replace_record_field(payload, 0, 2, "1.0"),
            "record-row-digest": lambda payload: self._replace_record_field(payload, -1, 1, f"sha256={digest}"),
            "record-row-size": lambda payload: self._replace_record_field(payload, -1, 2, "0"),
        }

        for name, record in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as raw:
                self._make_dist(Path(raw), wheel_record=record)
                with self.assertRaisesRegex(release.ReleaseError, "RECORD"):
                    release.check_dist(Path(raw))

    def test_check_dist_rejects_hostile_metadata_and_internal_wheel_tag(self) -> None:
        cases = {
            "x-name": b"Metadata-Version: 2.4\nX-Name: xplane-fdau\nVersion: 0.1.0\nRequires-Python: >=3.12\n",
            "dev-version": b"Metadata-Version: 2.4\nName: xplane-fdau\nVersion: 0.1.0.dev1\nRequires-Python: >=3.12\n",
            "broadened-python": b"Metadata-Version: 2.4\nName: xplane-fdau\nVersion: 0.1.0\nRequires-Python: >=3.11\n",
            "lowercase-requires-dist": b"Metadata-Version: 2.4\nName: xplane-fdau\nVersion: 0.1.0\nRequires-Python: >=3.12\nrequires-dist: hostile\n",
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

    def test_check_dist_requires_exact_internal_wheel_metadata(self) -> None:
        cases = {
            "missing-wheel-version": b"Root-Is-Purelib: true\nTag: py3-none-any\n",
            "wrong-wheel-version": b"Wheel-Version: 2.0\nRoot-Is-Purelib: true\nTag: py3-none-any\n",
            "duplicate-wheel-version": b"Wheel-Version: 1.0\nWheel-Version: 1.0\nRoot-Is-Purelib: true\nTag: py3-none-any\n",
            "missing-purelib": b"Wheel-Version: 1.0\nTag: py3-none-any\n",
            "wrong-purelib": b"Wheel-Version: 1.0\nRoot-Is-Purelib: false\nTag: py3-none-any\n",
            "duplicate-purelib": b"Wheel-Version: 1.0\nRoot-Is-Purelib: true\nRoot-Is-Purelib: true\nTag: py3-none-any\n",
            "missing-tag": b"Wheel-Version: 1.0\nRoot-Is-Purelib: true\n",
            "duplicate-tag": b"Wheel-Version: 1.0\nRoot-Is-Purelib: true\nTag: py3-none-any\nTag: py3-none-any\n",
            "parser-defect": b"Wheel-Version: 1.0\nRoot-Is-Purelib: true\nTag: py3-none-any\nthis is not a header\n",
        }
        for name, wheel_metadata in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as raw:
                self._make_dist(Path(raw), wheel_tag=wheel_metadata)
                with self.assertRaisesRegex(release.ReleaseError, "WHEEL"):
                    release.check_dist(Path(raw))

    def test_release_version_is_pinned_and_metadata_defects_are_rejected(self) -> None:
        malformed = {
            "space-before-colon": b"Metadata-Version: 2.4\nName: xplane-fdau\nVersion: 0.1.0\nRequires-Python: >=3.12\nRequires-Dist : hostile\n",
            "non-header": b"Metadata-Version: 2.4\nName: xplane-fdau\nVersion: 0.1.0\nRequires-Python: >=3.12\nthis is not a header\n",
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
                tar_updates={"xplane_fdau-0.1.0/pyproject.toml": b"[project]\nname = 'xplane-fdau'\nversion = '9.9.9'\ndependencies = ['hostile']\n"},
            )
            with self.assertRaisesRegex(release.ReleaseError, "pyproject"):
                release.check_dist(Path(raw))
        with tempfile.TemporaryDirectory() as raw:
            self._make_dist(Path(raw), wheel_updates={"xplane_fdau-0.1.0.dist-info/licenses/third/LICENSE": b"duplicate"})
            with self.assertRaisesRegex(release.ReleaseError, "exactly one LICENSE"):
                release.check_dist(Path(raw))

    def test_check_dist_accepts_semantically_identical_sdist_pyproject(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            self._make_dist(Path(raw), tar_updates={"xplane_fdau-0.1.0/pyproject.toml": Path("pyproject.toml").read_bytes() + b"\n"})
            release.check_dist(Path(raw))

    def test_check_dist_requires_exact_package_contents_schema_and_license_locations(self) -> None:
        expected_schema = "xplane_fdau/formats/xplane_fdr/schemas/fdr-record-config-v1.schema.json"
        cases = {
            "corrupt-wheel-schema": {expected_schema: b"{}\n"},
            "unexpected-native": {"xplane_fdau/hostile.pyd": b"native"},
            "unexpected-module": {"xplane_fdau/hostile.py": b""},
            "relocated-license": {
                "xplane_fdau-0.1.0.dist-info/licenses/LICENSE": b"",
                "xplane_fdau-0.1.0.dist-info/LICENSE": Path("LICENSE").read_bytes(),
            },
        }
        for name, updates in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as raw:
                self._make_dist(Path(raw), wheel_updates=updates)
                with self.assertRaises(release.ReleaseError):
                    release.check_dist(Path(raw))
        with tempfile.TemporaryDirectory() as raw:
            self._make_dist(Path(raw), tar_updates={f"xplane_fdau-0.1.0/{expected_schema}": b"{}\n"})
            with self.assertRaises(release.ReleaseError):
                release.check_dist(Path(raw))

    def test_check_dist_rejects_unexpected_wheel_dist_info_members_and_every_extra_license(self) -> None:
        cases = {
            "python": {"xplane_fdau-0.1.0.dist-info/evil.py": b"hostile"},
            "native": {"xplane_fdau-0.1.0.dist-info/evil.so": b"hostile"},
            "license-extension": {"xplane_fdau-0.1.0.dist-info/licenses/LICENSE.txt": b"duplicate"},
        }
        for name, updates in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as raw:
                self._make_dist(Path(raw), wheel_updates=updates)
                with self.assertRaisesRegex(release.ReleaseError, "members"):
                    release.check_dist(Path(raw))

    def test_check_dist_rejects_unexpected_sdist_root_members_and_every_extra_license(self) -> None:
        cases = {
            "setup": {"xplane_fdau-0.1.0/setup.py": b"raise SystemExit\n"},
            "native": {"xplane_fdau-0.1.0/evil.so": b"hostile"},
            "license-extension": {"xplane_fdau-0.1.0/LICENSE.txt": b"duplicate"},
        }
        for name, updates in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as raw:
                self._make_dist(Path(raw), tar_updates=updates)
                with self.assertRaisesRegex(release.ReleaseError, "members"):
                    release.check_dist(Path(raw))

    def test_check_dist_requires_exact_sdist_original_project_and_readme_bytes(self) -> None:
        root = "xplane_fdau-0.1.0"
        cases = {
            "missing-project-original": ({f"{root}/pyproject.toml.orig"}, None),
            "corrupt-project-original": (None, {f"{root}/pyproject.toml.orig": b"[project]\nname='hostile'\n"}),
            "corrupt-readme": (None, {f"{root}/README.md": b"hostile\n"}),
        }
        for name, (remove, updates) in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as raw:
                self._make_dist(Path(raw), tar_remove=remove, tar_updates=updates)
                with self.assertRaises(release.ReleaseError):
                    release.check_dist(Path(raw))

    def test_check_dist_rejects_unsafe_archive_paths_duplicates_and_links(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            self._make_dist(Path(raw), wheel_updates={"xplane_fdau/..\\evil.py": b""})
            with self.assertRaisesRegex(release.ReleaseError, "path"):
                release.check_dist(Path(raw))
        with tempfile.TemporaryDirectory() as raw:
            self._make_dist(Path(raw), wheel_duplicates=("xplane_fdau/__init__.py", b"duplicate"))
            with self.assertRaisesRegex(release.ReleaseError, "duplicate"):
                release.check_dist(Path(raw))
        with tempfile.TemporaryDirectory() as raw:
            self._make_dist(Path(raw), tar_link=("xplane_fdau-0.1.0/xplane_fdau/link.py", "../../evil.py"))
            with self.assertRaisesRegex(release.ReleaseError, "link"):
                release.check_dist(Path(raw))
        with tempfile.TemporaryDirectory() as raw:
            self._make_dist(Path(raw), wheel_link="xplane_fdau-0.1.0.dist-info/RECORD")
            with self.assertRaisesRegex(release.ReleaseError, "link"):
                release.check_dist(Path(raw))

    def test_check_dist_rejects_metadata_duplicates_with_mixed_case(self) -> None:
        metadata = b"Metadata-Version: 2.4\nName: xplane-fdau\nname: xplane-fdau\nVersion: 0.1.0\nRequires-Python: >=3.12\n"
        with tempfile.TemporaryDirectory() as raw:
            self._make_dist(Path(raw), wheel_metadata=metadata)
            with self.assertRaisesRegex(release.ReleaseError, "Name"):
                release.check_dist(Path(raw))

    def test_check_dist_rejects_near_match_dist_info_root(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            self._make_dist(Path(raw), wheel_updates={"xplane_fdau-0.1.0.dist-info-evil/METADATA": b"hostile"})
            with self.assertRaisesRegex(release.ReleaseError, "outside"):
                release.check_dist(Path(raw))

    def test_command_offers_only_distribution_validation(self) -> None:
        errors = io.StringIO()
        with redirect_stderr(errors), self.assertRaises(SystemExit) as raised:
            release.main(["check-tag", "v0.1.0"])

        self.assertEqual(2, raised.exception.code)
        self.assertIn("invalid choice", errors.getvalue())


if __name__ == "__main__":
    unittest.main()
