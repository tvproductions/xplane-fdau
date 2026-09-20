"""Official package index evidence for the dependency refresh adapter."""

from __future__ import annotations

import importlib
import json
import unittest
from typing import Any


def _sources() -> Any:
    try:
        return importlib.import_module("tools.dependency_sources")
    except ModuleNotFoundError as error:
        raise AssertionError("dependency_sources module is missing") from error


def index_fixture() -> dict[str, object]:
    files = []
    for version, yanked, digit in (
        ("0.12.17", False, "1"),
        ("0.12.18", False, "2"),
        ("0.12.19", True, "3"),
        ("0.13.0rc1", False, "4"),
    ):
        files.append(
            {
                "filename": f"uv-{version}-py3-none-any.whl",
                "hashes": {"sha256": digit * 64},
                "requires-python": ">=3.12",
                "yanked": yanked,
            }
        )
    return {
        "meta": {"api-version": "1.4"},
        "name": "uv",
        "versions": ["0.12.17", "0.12.18", "0.12.19", "0.13.0rc1"],
        "files": files,
    }


class SourceSelectionTests(unittest.TestCase):
    def test_selects_newest_stable_release_with_non_yanked_file(self) -> None:
        sources = _sources()
        self.assertEqual("0.12.18", sources.newest_stable_release(index_fixture()))

    def test_unrelated_legacy_files_do_not_hide_valid_release(self) -> None:
        sources = _sources()
        index = index_fixture()
        files = index["files"]
        assert isinstance(files, list)
        files.insert(0, {"filename": "uv-0.1.0.egg", "hashes": {"sha256": "a" * 64}})
        self.assertEqual("0.12.18", sources.newest_stable_release(index))
        self.assertFalse(sources.release_is_yanked(index, "0.12.18", "2" * 64))
        with self.assertRaisesRegex(sources.SourceError, "invalid artifact filename"):
            sources.release_is_yanked(index, "0.12.18", "a" * 64)

    def test_bounded_html_fallback_for_large_json_index(self) -> None:
        sources = _sources()
        requested: list[str] = []
        html = (
            b"""<!DOCTYPE html><html><body>
<a href="https://files.pythonhosted.org/packages/a/coverage-7.10.7.tar.gz#sha256="""
            + b"b" * 64
            + b"""">coverage-7.10.7.tar.gz</a>
<a data-yanked="bad release" href="https://files.pythonhosted.org/packages/b/coverage-7.10.8.tar.gz#sha256="""
            + b"c" * 64
            + b"""">coverage-7.10.8.tar.gz</a>
</body></html>"""
        )

        def opener(request: Any, timeout: int, ceiling: int) -> tuple[bytes, str, str]:
            assert isinstance(request.full_url, str)
            requested.append(request.headers["Accept"])
            if len(requested) == 1:
                return b"x" * (ceiling + 1), request.full_url, "application/vnd.pypi.simple.v1+json"
            return html, request.full_url, "text/html; charset=UTF-8"

        index = sources.fetch_index("coverage", opener)
        self.assertEqual(["application/vnd.pypi.simple.v1+json", "text/html"], requested)
        self.assertEqual("7.10.7", sources.newest_stable_release(index))
        self.assertFalse(sources.release_is_yanked(index, "7.10.7", "b" * 64))

    def test_normalizes_package_name_in_index_request(self) -> None:
        sources = _sources()
        requested_urls: list[str] = []

        def opener(request: Any, timeout: int, ceiling: int) -> tuple[bytes, str, str]:
            requested_urls.append(request.full_url)
            self.assertEqual(15, timeout)
            self.assertEqual(5 * 1024 * 1024, ceiling)
            return (
                json.dumps({"meta": {"api-version": "1.4"}, "name": "my-package", "versions": [], "files": []}).encode("utf-8"),
                "https://pypi.org/simple/my-package/",
                "application/vnd.pypi.simple.v1+json",
            )

        sources.fetch_index("My_Package", opener)
        self.assertEqual(["https://pypi.org/simple/my-package/"], requested_urls)


class SourceFailureTests(unittest.TestCase):
    def test_rejects_untrusted_or_malformed_index_response(self) -> None:
        sources = _sources()
        cases = (
            (b"{", "https://pypi.org/simple/uv/", "application/vnd.pypi.simple.v1+json", "invalid Index JSON"),
            (b"[]", "https://pypi.org/simple/uv/", "application/vnd.pypi.simple.v1+json", "root"),
            (json.dumps({"name": "uv", "files": []}).encode("utf-8"), "https://pypi.org/simple/uv/", "application/vnd.pypi.simple.v1+json", "versions"),
            (json.dumps({"name": "uv", "versions": []}).encode("utf-8"), "https://pypi.org/simple/uv/", "application/vnd.pypi.simple.v1+json", "files"),
            (b"{}" * (3 * 1024 * 1024), "https://pypi.org/simple/uv/", "application/vnd.pypi.simple.v1+json", "oversized"),
            (b"{}", "https://example.org/simple/uv/", "application/vnd.pypi.simple.v1+json", "untrusted"),
            (b"{}", "https://pypi.org/simple/uv/", "application/json", "content type"),
        )
        for body, final_url, content_type, reason in cases:
            with self.subTest(reason=reason):

                def opener(request: Any, timeout: int, ceiling: int) -> tuple[bytes, str, str]:
                    return body, final_url, content_type

                with self.assertRaisesRegex(sources.SourceError, f"uv: .*{reason}"):
                    sources.fetch_index("uv", opener)

    def test_rejects_invalid_or_unavailable_release_evidence(self) -> None:
        sources = _sources()
        cases = (
            ({"name": "uv", "versions": ["."], "files": []}, "invalid Index version"),
            ({"name": "uv", "versions": ["1.0rc1"], "files": [{"filename": "uv-1.0rc1-py3-none-any.whl"}]}, "no stable"),
            ({"name": "uv", "versions": ["1.0"], "files": [{"filename": "uv-1.0-py3-none-any.whl", "yanked": True}]}, "no stable"),
            ({"name": "uv", "versions": ["1.0"], "files": [{"filename": "bad.whl"}]}, "invalid artifact filename"),
        )
        for index, reason in cases:
            with self.subTest(reason=reason):
                with self.assertRaisesRegex(sources.SourceError, f"uv: .*{reason}"):
                    sources.newest_stable_release(index)

    def test_fetches_bounded_official_release_requirements(self) -> None:
        sources = _sources()
        payload = {"info": {"name": "wily", "version": "1.25.0", "requires_dist": ["radon>=5.1,<5.2", "plotly>=4,<6"]}}

        def opener(request: Any, timeout: int, ceiling: int) -> tuple[bytes, str, str]:
            self.assertEqual(request.full_url, "https://pypi.org/pypi/wily/1.25.0/json")
            self.assertEqual((timeout, ceiling), (15, 5 * 1024 * 1024))
            return json.dumps(payload).encode(), "https://pypi.org/pypi/wily/1.25.0/json", "application/json"

        self.assertEqual(sources.fetch_release_requirements("wily", "1.25.0", opener), ["radon>=5.1,<5.2", "plotly>=4,<6"])
        payload["info"]["name"] = "other"
        with self.assertRaisesRegex(sources.SourceError, "identity mismatch"):
            sources.fetch_release_requirements("wily", "1.25.0", opener)

    def test_release_metadata_rejects_untrusted_or_missing_requirements(self) -> None:
        sources = _sources()
        body = json.dumps({"info": {"name": "wily", "version": "1.25.0"}}).encode()

        def opener(request: Any, timeout: int, ceiling: int) -> tuple[bytes, str, str]:
            return body, "https://pypi.org/pypi/wily/1.25.0/json", "application/json"

        with self.assertRaisesRegex(sources.SourceError, "requires_dist"):
            sources.fetch_release_requirements("wily", "1.25.0", opener)

    def test_locked_hash_must_match_exact_official_artifact(self) -> None:
        sources = _sources()
        self.assertFalse(sources.release_is_yanked(index_fixture(), "0.12.18", "2" * 64))
        self.assertTrue(sources.release_is_yanked(index_fixture(), "0.12.19", "3" * 64))
        with self.assertRaisesRegex(sources.SourceError, "official hash match"):
            sources.release_is_yanked(index_fixture(), "0.12.18", "9" * 64)
