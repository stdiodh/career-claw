from __future__ import annotations

import copy
from datetime import datetime, timedelta, timezone
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from scripts import collect_spring_updates as collector


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = ROOT / "tests/fixtures/spring-updates.json"


class SpringUpdateCollectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.settings = collector.load_config()
        cls.schedule = collector.load_delivery_schedule()
        cls.fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        cls.now = collector.fixture_now(cls.fixture, None)

    def run_fixture(
        self,
        fixture: dict[str, object] | None = None,
        as_of: str | None = None,
    ) -> dict[str, str] | None:
        selected_fixture = copy.deepcopy(self.fixture if fixture is None else fixture)
        return collector.collect_updates(
            self.settings,
            collector.fixture_fetcher(selected_fixture),
            collector.fixture_now(selected_fixture, None),
            as_of,
            self.schedule,
        )

    def response_releases(
        self, fixture: dict[str, object], source_index: int
    ) -> list[dict[str, object]]:
        url = self.settings.sources[source_index].api_url
        response = fixture["responses"][url]
        return json.loads(response["body"])

    def replace_releases(
        self,
        fixture: dict[str, object],
        source_index: int,
        releases: list[dict[str, object]],
    ) -> None:
        url = self.settings.sources[source_index].api_url
        fixture["responses"][url]["body"] = json.dumps(releases, separators=(",", ":"))

    def set_page(
        self,
        fixture: dict[str, object],
        source_index: int,
        page: int,
        releases: list[dict[str, object]],
        *,
        final_url: str | None = None,
    ) -> str:
        url = collector.release_page_url(self.settings.sources[source_index], page)
        fixture["responses"][url] = {
            "status": 200,
            "final_url": final_url or url,
            "body": json.dumps(releases, separators=(",", ":")),
        }
        return url

    def test_config_is_the_exact_two_endpoint_contract(self) -> None:
        self.assertEqual(self.settings.freshness_days, 14)
        self.assertEqual(self.settings.selection_limit, 1)
        self.assertEqual(
            tuple(source.api_url for source in self.settings.sources),
            tuple(item["api_url"] for item in collector.EXPECTED_SOURCES),
        )
        self.assertTrue(
            all(url.endswith("/releases?per_page=100&page=1") for url in (
                source.api_url for source in self.settings.sources
            ))
        )

    def test_fixture_uses_published_at_and_ignores_a_recent_edit(self) -> None:
        selected = self.run_fixture()

        self.assertEqual(
            selected,
            {
                "title": "v3.5.4",
                "date": "2026-08-05",
                "link": "https://github.com/spring-projects/spring-boot/releases/tag/v3.5.4",
                "source": "Spring Boot",
            },
        )
        ai_releases = self.response_releases(self.fixture, 1)
        edited_old_release = ai_releases[0]
        self.assertEqual(edited_old_release["tag_name"], "v2.0.0")
        self.assertEqual(edited_old_release["updated_at"], "2026-08-14T10:00:00Z")
        self.assertEqual(edited_old_release["published_at"], "2026-06-12T15:14:59Z")
        self.assertNotEqual(selected["title"], "v2.0.0")
        self.assertEqual(set(selected), {"title", "date", "link", "source"})

    def test_as_of_date_excludes_later_boot_release_and_selects_ai(self) -> None:
        selected = self.run_fixture(as_of="2026-08-04")

        self.assertEqual(
            selected,
            {
                "title": "v1.0.1",
                "date": "2026-08-04",
                "link": "https://github.com/spring-projects/spring-ai/releases/tag/v1.0.1",
                "source": "Spring AI",
            },
        )

        window = collector.parse_as_of(
            "2026-08-04", self.now, 14, self.schedule
        )
        self.assertEqual(window.cutoff, datetime(2026, 8, 4, 0, 0, tzinfo=timezone.utc))
        self.assertTrue(
            collector.entry_is_in_window(
                collector.ReleaseEntry(
                    "boundary",
                    "https://example.test/boundary",
                    "Spring AI",
                    window.cutoff,
                    window.cutoff,
                    True,
                ),
                window,
            )
        )

    def test_custom_timezone_controls_cutoff_and_output_date(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        ai_releases = self.response_releases(fixture, 1)
        ai_releases[1]["created_at"] = "2026-08-03T18:00:00Z"
        ai_releases[1]["published_at"] = "2026-08-03T18:55:00Z"
        ai_releases[1]["updated_at"] = "2026-08-03T18:56:00Z"
        self.replace_releases(fixture, 1, ai_releases)
        schedule = collector.sync_schedule.DeliverySchedule(
            enabled=True,
            timezone="Pacific/Kiritimati",
            hour=9,
            minute=0,
        )

        selected = collector.collect_updates(
            self.settings,
            collector.fixture_fetcher(fixture),
            self.now,
            "2026-08-04",
            schedule,
        )

        assert selected is not None
        self.assertEqual(selected["source"], "Spring AI")
        self.assertEqual(selected["date"], "2026-08-04")
        window = collector.parse_as_of("2026-08-04", self.now, 14, schedule)
        self.assertEqual(window.cutoff, datetime(2026, 8, 3, 19, 0, tzinfo=timezone.utc))

    def test_as_of_fails_closed_when_a_newer_release_changed_after_cutoff(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        ai_releases = self.response_releases(fixture, 1)
        ai_releases[1]["updated_at"] = "2026-08-10T00:00:00Z"
        ai_releases.append(
            {
                "draft": False,
                "prerelease": False,
                "tag_name": "v0.9.9",
                "html_url": (
                    "https://github.com/spring-projects/spring-ai/releases/tag/v0.9.9"
                ),
                "created_at": "2026-08-01T22:00:00Z",
                "published_at": "2026-08-01T23:00:00Z",
                "updated_at": "2026-08-01T23:01:00Z",
            }
        )
        self.replace_releases(fixture, 1, ai_releases)

        with self.assertRaisesRegex(collector.CollectionError, "history changed"):
            self.run_fixture(fixture, as_of="2026-08-04")

    def test_both_sources_outside_fourteen_days_return_null(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        for source_index in (0, 1):
            releases = self.response_releases(fixture, source_index)
            for release in releases:
                release["created_at"] = "2026-07-09T09:00:00Z"
                release["published_at"] = "2026-07-10T09:00:00Z"
                release["updated_at"] = "2026-07-10T09:01:00Z"
            self.replace_releases(fixture, source_index, releases)

        self.assertIsNone(self.run_fixture(fixture))

    def test_latest_published_release_wins_with_deterministic_tie_breaking(self) -> None:
        timestamp = self.now - timedelta(days=1)
        boot = collector.ReleaseEntry(
            "boot",
            "https://example.test/boot",
            "Spring Boot",
            timestamp,
            timestamp,
            True,
        )
        ai = collector.ReleaseEntry(
            "ai", "https://example.test/ai", "Spring AI", timestamp, timestamp, True
        )
        older = collector.ReleaseEntry(
            "older",
            "https://example.test/older",
            "Spring Boot",
            timestamp - timedelta(seconds=1),
            timestamp - timedelta(seconds=1),
            True,
        )
        prerelease = collector.ReleaseEntry(
            "preview",
            "https://example.test/preview",
            "Spring AI",
            self.now,
            self.now,
            False,
        )
        window = collector.parse_as_of(None, self.now, 14)

        ordered = collector.sorted_fresh_entries(
            [prerelease, older, boot, ai], window
        )

        self.assertEqual([entry.tag_name for entry in ordered], ["ai", "boot", "older"])

    def test_freshness_is_inclusive_at_exactly_fourteen_days(self) -> None:
        boundary = collector.ReleaseEntry(
            "boundary",
            "https://example.test/boundary",
            "Spring Boot",
            self.now - timedelta(days=14),
            self.now - timedelta(days=14),
            True,
        )
        stale = collector.ReleaseEntry(
            "stale",
            "https://example.test/stale",
            "Spring Boot",
            self.now - timedelta(days=14, seconds=1),
            self.now - timedelta(days=14, seconds=1),
            True,
        )
        window = collector.parse_as_of(None, self.now, 14)

        selected = collector.sorted_fresh_entries([stale, boundary], window)

        self.assertEqual([entry.tag_name for entry in selected], ["boundary"])

    def test_draft_and_prerelease_entries_are_never_selected(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        boot_releases = self.response_releases(fixture, 0)
        boot_releases[0]["draft"] = True
        self.replace_releases(fixture, 0, boot_releases)
        ai_releases = self.response_releases(fixture, 1)
        ai_releases[1]["prerelease"] = True
        self.replace_releases(fixture, 1, ai_releases)

        self.assertIsNone(self.run_fixture(fixture))

    def test_config_rejects_non_exact_scheme_host_path_and_query(self) -> None:
        invalid_urls = (
            "http://api.github.com/repos/spring-projects/spring-boot/releases?per_page=100&page=1",
            "https://evil.example/repos/spring-projects/spring-boot/releases?per_page=100&page=1",
            "https://api.github.com/repos/spring-projects/spring-boot/releases/latest",
            "https://api.github.com/repos/spring-projects/spring-boot/releases?per_page=100",
            "https://api.github.com/repos/spring-projects/spring-boot/releases?per_page=100&page=2",
        )
        for invalid_url in invalid_urls:
            with self.subTest(url=invalid_url), tempfile.TemporaryDirectory() as directory:
                payload = json.loads(collector.DEFAULT_CONFIG.read_text(encoding="utf-8"))
                payload["sources"][0]["api_url"] = invalid_url
                path = Path(directory) / "spring-updates.json"
                path.write_text(json.dumps(payload), encoding="utf-8")

                with self.assertRaisesRegex(
                    collector.ConfigurationError, "exactly match"
                ):
                    collector.load_config(path)

    def test_release_url_must_match_both_source_and_tag(self) -> None:
        wrong_source = copy.deepcopy(self.fixture)
        releases = self.response_releases(wrong_source, 0)
        releases[0]["html_url"] = (
            "https://github.com/spring-projects/spring-ai/releases/tag/v3.5.4"
        )
        self.replace_releases(wrong_source, 0, releases)
        with self.assertRaisesRegex(collector.CollectionError, "allowlisted path"):
            self.run_fixture(wrong_source)

        wrong_tag = copy.deepcopy(self.fixture)
        releases = self.response_releases(wrong_tag, 0)
        releases[0]["html_url"] = (
            "https://github.com/spring-projects/spring-boot/releases/tag/v3.5.3"
        )
        self.replace_releases(wrong_tag, 0, releases)
        with self.assertRaisesRegex(collector.CollectionError, "match tag_name"):
            self.run_fixture(wrong_tag)

    def test_timestamps_are_timezone_aware_and_not_future(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        releases = self.response_releases(fixture, 0)
        releases[0]["published_at"] = "2026-08-05T09:30:00"
        self.replace_releases(fixture, 0, releases)
        with self.assertRaisesRegex(collector.CollectionError, "include a timezone"):
            self.run_fixture(fixture)

        non_chronological = copy.deepcopy(self.fixture)
        releases = self.response_releases(non_chronological, 0)
        releases[0]["created_at"] = "2026-08-06T09:30:00Z"
        self.replace_releases(non_chronological, 0, releases)
        selected = self.run_fixture(non_chronological)
        assert selected is not None
        self.assertEqual(selected["title"], "v3.5.4")

        future = copy.deepcopy(self.fixture)
        releases = self.response_releases(future, 0)
        releases[0]["updated_at"] = "2026-08-16T09:30:00Z"
        self.replace_releases(future, 0, releases)
        with self.assertRaisesRegex(collector.CollectionError, "must not be in the future"):
            self.run_fixture(future)

    def test_malformed_non_utf8_and_oversized_responses_fail_closed(self) -> None:
        source = self.settings.sources[0]
        with self.assertRaisesRegex(collector.CollectionError, "malformed JSON"):
            collector.parse_release_list(b"[", source, self.now)
        with self.assertRaisesRegex(collector.CollectionError, "not UTF-8"):
            collector.parse_release_list(b"\xff", source, self.now)
        with self.assertRaisesRegex(collector.CollectionError, "too large"):
            collector.parse_release_list(
                b"x" * (collector.MAX_RESPONSE_BYTES + 1), source, self.now
            )

    def test_any_fetch_failure_http_error_or_redirect_discards_all_sources(self) -> None:
        first_url = self.settings.sources[0].api_url
        original_fetch = collector.fixture_fetcher(copy.deepcopy(self.fixture))

        def failing_fetch(url: str) -> collector.FetchResponse:
            if url == first_url:
                return original_fetch(url)
            raise OSError("network unavailable")

        with self.assertRaisesRegex(collector.CollectionError, "request failed"):
            collector.collect_updates(self.settings, failing_fetch, self.now)

        http_fixture = copy.deepcopy(self.fixture)
        http_fixture["responses"][first_url]["status"] = 500
        with self.assertRaisesRegex(collector.CollectionError, "HTTP 500"):
            self.run_fixture(http_fixture)

        redirected_fixture = copy.deepcopy(self.fixture)
        redirected_fixture["responses"][first_url]["final_url"] = (
            "https://api.github.com/repos/spring-projects/spring-boot/releases"
        )
        with self.assertRaisesRegex(collector.CollectionError, "redirected"):
            self.run_fixture(redirected_fixture)

    def test_later_published_stable_release_on_page_two_is_selected(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        first_page: list[dict[str, object]] = []
        for index in range(collector.PAGE_SIZE):
            tag = f"v8.0.{index}"
            first_page.append(
                {
                    "draft": False,
                    "prerelease": False,
                    "tag_name": tag,
                    "html_url": (
                        "https://github.com/spring-projects/spring-boot/releases/tag/"
                        f"{tag}"
                    ),
                    "created_at": "2026-08-04T00:00:00Z",
                    "published_at": "2026-08-05T00:00:00Z",
                    "updated_at": "2026-08-05T00:00:00Z",
                }
            )
        self.replace_releases(fixture, 0, first_page)
        late_tag = "v7.9.0-late"
        second_page = [
            {
                "draft": False,
                "prerelease": False,
                "tag_name": late_tag,
                "html_url": (
                    "https://github.com/spring-projects/spring-boot/releases/tag/"
                    f"{late_tag}"
                ),
                "created_at": "2026-07-30T00:00:00Z",
                "published_at": "2026-08-10T00:00:00Z",
                "updated_at": "2026-08-10T00:00:00Z",
            }
        ]
        page_two_url = self.set_page(fixture, 0, 2, second_page)
        requested: list[str] = []
        fixture_fetch = collector.fixture_fetcher(fixture)

        def fetch(url: str) -> collector.FetchResponse:
            requested.append(url)
            return fixture_fetch(url)

        selected = collector.collect_updates(
            self.settings, fetch, self.now, schedule=self.schedule
        )

        assert selected is not None
        self.assertEqual(selected["title"], late_tag)
        self.assertEqual(selected["date"], "2026-08-10")
        self.assertEqual(
            requested[:2],
            [self.settings.sources[0].api_url, page_two_url],
        )

    def test_ten_full_pages_fail_closed(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        for page in range(1, collector.MAX_PAGES + 1):
            releases: list[dict[str, object]] = []
            for index in range(collector.PAGE_SIZE):
                tag = f"v{page}.{index}.0"
                releases.append(
                    {
                        "draft": False,
                        "prerelease": False,
                        "tag_name": tag,
                        "html_url": (
                            "https://github.com/spring-projects/spring-boot/"
                            f"releases/tag/{tag}"
                        ),
                        "created_at": "2026-07-01T00:00:00Z",
                        "published_at": "2026-07-02T00:00:00Z",
                        "updated_at": "2026-07-02T00:00:00Z",
                    }
                )
            self.set_page(fixture, 0, page, releases)

        with self.assertRaisesRegex(collector.CollectionError, "exceeded 10 full pages"):
            self.run_fixture(fixture)

    def test_fixture_rejects_urls_outside_derived_pagination_allowlist(self) -> None:
        invalid_urls = (
            "https://api.github.com/repos/spring-projects/spring-boot/releases?per_page=100&page=11",
            "https://api.github.com/repos/spring-projects/spring-boot/releases?page=2&per_page=100",
            "https://api.github.com/repos/spring-projects/spring-framework/releases?per_page=100&page=2",
        )
        for invalid_url in invalid_urls:
            with self.subTest(url=invalid_url):
                fixture = copy.deepcopy(self.fixture)
                fixture["responses"][invalid_url] = {
                    "status": 200,
                    "final_url": invalid_url,
                    "body": "[]",
                }
                with self.assertRaisesRegex(
                    collector.ConfigurationError, "pagination allowlist"
                ):
                    collector.fixture_fetcher(fixture)

    def test_fixture_stdout_only_keeps_cli_contract_and_accepts_as_of(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "spring-updates.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/collect_spring_updates.py"),
                    "--fixture",
                    str(FIXTURE_PATH),
                    "--as-of",
                    "2026-08-04",
                    "--stdout-only",
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(output.exists())
        selected = json.loads(result.stdout)
        self.assertEqual(selected["source"], "Spring AI")
        self.assertEqual(selected["date"], "2026-08-04")
        self.assertEqual(result.stderr, "")

    def test_invalid_schedule_config_fails_closed_before_collection(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            schedule = root / "delivery-schedule.json"
            schedule.write_text("{}", encoding="utf-8")
            output = root / "spring-updates.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/collect_spring_updates.py"),
                    "--fixture",
                    str(FIXTURE_PATH),
                    "--schedule-config",
                    str(schedule),
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertFalse(output.exists())
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("Delivery schedule is invalid", result.stderr)

    def test_live_dry_run_uses_both_exact_urls_without_external_writes(self) -> None:
        current = datetime.now(timezone.utc).replace(microsecond=0)

        def release(source: collector.Source) -> bytes:
            created = (current - timedelta(minutes=2)).isoformat()
            published = (current - timedelta(minutes=1)).isoformat()
            updated = (current - timedelta(seconds=30)).isoformat()
            tag = "v1.0.0"
            return json.dumps(
                [
                    {
                        "draft": False,
                        "prerelease": False,
                        "tag_name": tag,
                        "html_url": f"https://github.com{source.release_path_prefix}{tag}",
                        "created_at": created,
                        "published_at": published,
                        "updated_at": updated,
                    }
                ]
            ).encode()

        responses = {
            source.api_url: collector.FetchResponse(200, source.api_url, release(source))
            for source in self.settings.sources
        }
        requested: list[str] = []

        def fetch(url: str) -> collector.FetchResponse:
            requested.append(url)
            return responses[url]

        stdout = io.StringIO()
        stderr = io.StringIO()
        argv = ["collect_spring_updates.py", "--live-dry-run", "--stdout-only"]
        with (
            mock.patch.object(collector, "fetch_live", side_effect=fetch),
            mock.patch("sys.argv", argv),
            mock.patch("sys.stdout", stdout),
            mock.patch("sys.stderr", stderr),
        ):
            result = collector.main()

        self.assertEqual(result, 0, stderr.getvalue())
        self.assertEqual(requested, [source.api_url for source in self.settings.sources])
        self.assertEqual(set(json.loads(stdout.getvalue())), {"title", "date", "link", "source"})
        self.assertEqual(stderr.getvalue(), "")

    def test_live_request_is_exact_unauthenticated_get_with_a_size_bound(self) -> None:
        source = self.settings.sources[0]
        captured: dict[str, object] = {}

        class Response:
            status = 200

            def __enter__(self) -> Response:
                return self

            def __exit__(self, *args: object) -> None:
                return None

            def read(self, limit: int) -> bytes:
                captured["limit"] = limit
                return b"[]"

            def geturl(self) -> str:
                return source.api_url

        def urlopen(request: object, timeout: int) -> Response:
            captured["request"] = request
            captured["timeout"] = timeout
            return Response()

        with mock.patch.object(collector.urllib.request, "urlopen", side_effect=urlopen):
            response = collector.fetch_live(source.api_url)

        request = captured["request"]
        headers = {key.lower(): value for key, value in request.header_items()}
        self.assertEqual(request.full_url, source.api_url)
        self.assertEqual(request.get_method(), "GET")
        self.assertNotIn("authorization", headers)
        self.assertEqual(headers["accept"], "application/vnd.github+json")
        self.assertEqual(captured["limit"], collector.MAX_RESPONSE_BYTES + 1)
        self.assertEqual(response.final_url, source.api_url)

    def test_invalid_or_future_as_of_date_is_rejected(self) -> None:
        for value in ("2026/08/04", "2026-8-4", "2026-08-16"):
            with self.subTest(value=value), self.assertRaises(collector.ConfigurationError):
                collector.parse_as_of(value, self.now, 14)


if __name__ == "__main__":
    unittest.main()
