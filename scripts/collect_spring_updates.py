#!/usr/bin/env python3
"""Select one fresh official Spring Boot or Spring AI release."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Any, Callable
import urllib.error
import urllib.request
from urllib.parse import unquote, urlsplit, urlunsplit
from zoneinfo import ZoneInfo

try:
    from . import sync_delivery_schedule as sync_schedule
except ImportError:
    import sync_delivery_schedule as sync_schedule


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "configs/spring-updates.json"
DEFAULT_OUTPUT = ROOT / "reports/spring-updates.json"
DEFAULT_SCHEDULE = ROOT / sync_schedule.CONFIG_PATH
MAX_RESPONSE_BYTES = 2 * 1024 * 1024
PAGE_SIZE = 100
MAX_PAGES = 10
EXPECTED_SOURCES = (
    {
        "id": "spring-boot",
        "name": "Spring Boot",
        "api_url": (
            "https://api.github.com/repos/spring-projects/"
            "spring-boot/releases?per_page=100&page=1"
        ),
        "release_path_prefix": "/spring-projects/spring-boot/releases/tag/",
    },
    {
        "id": "spring-ai",
        "name": "Spring AI",
        "api_url": (
            "https://api.github.com/repos/spring-projects/"
            "spring-ai/releases?per_page=100&page=1"
        ),
        "release_path_prefix": "/spring-projects/spring-ai/releases/tag/",
    },
)


class ConfigurationError(RuntimeError):
    """Raised when the local source contract is invalid."""


class CollectionError(RuntimeError):
    """Raised when release data cannot be fetched or trusted."""


@dataclass(frozen=True)
class Source:
    id: str
    name: str
    api_url: str
    release_path_prefix: str


@dataclass(frozen=True)
class Settings:
    freshness_days: int
    selection_limit: int
    sources: tuple[Source, ...]


@dataclass(frozen=True)
class FetchResponse:
    status: int
    final_url: str
    body: bytes


@dataclass(frozen=True)
class ReleaseEntry:
    tag_name: str
    link: str
    source: str
    published_at: datetime
    updated_at: datetime
    stable: bool


@dataclass(frozen=True)
class SelectionWindow:
    start: datetime
    cutoff: datetime


Fetcher = Callable[[str], FetchResponse]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--fixture",
        type=Path,
        help="Replay deterministic GitHub release API responses.",
    )
    mode.add_argument(
        "--live-dry-run",
        action="store_true",
        help="Read the two exact official GitHub release API endpoints.",
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--schedule-config", type=Path, default=DEFAULT_SCHEDULE)
    parser.add_argument("--now", help="Fixed timezone-aware timestamp for fixture mode.")
    parser.add_argument(
        "--as-of",
        help="Select releases visible at this local delivery date (YYYY-MM-DD).",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--stdout-only",
        action="store_true",
        help="Print the selected item without writing a report file.",
    )
    return parser.parse_args()


def read_object(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ConfigurationError(f"{label} does not exist: {path}") from exc
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ConfigurationError(f"{label} is not valid UTF-8 JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ConfigurationError(f"{label} root must be an object")
    return payload


def validate_api_url(url: object) -> str:
    if not isinstance(url, str):
        raise ConfigurationError("api_url must be a string")
    parsed = urlsplit(url)
    if (
        parsed.scheme != "https"
        or parsed.netloc != "api.github.com"
        or parsed.query != "per_page=100&page=1"
        or parsed.fragment
        or url not in {item["api_url"] for item in EXPECTED_SOURCES}
    ):
        raise ConfigurationError(f"API URL is not allowlisted: {url}")
    return url


def release_page_url(source: Source, page: int) -> str:
    if type(page) is not int or not 1 <= page <= MAX_PAGES:
        raise CollectionError("release API page is outside the bounded allowlist")
    if source.api_url not in {item["api_url"] for item in EXPECTED_SOURCES}:
        raise CollectionError("release API base URL is outside the allowlist")
    parsed = urlsplit(source.api_url)
    return urlunsplit(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            f"per_page={PAGE_SIZE}&page={page}",
            "",
        )
    )


def load_config(path: Path = DEFAULT_CONFIG) -> Settings:
    payload = read_object(path, "Spring update config")
    if set(payload) != {"schema_version", "freshness_days", "selection_limit", "sources"}:
        raise ConfigurationError("Spring update config has unexpected fields")
    if payload.get("schema_version") != 2:
        raise ConfigurationError("Spring update config schema_version must equal 2")
    if payload.get("freshness_days") != 14:
        raise ConfigurationError("freshness_days must equal 14")
    if payload.get("selection_limit") != 1:
        raise ConfigurationError("selection_limit must equal 1")
    if payload.get("sources") != list(EXPECTED_SOURCES):
        raise ConfigurationError(
            "sources must exactly match the two official GitHub release endpoints"
        )

    sources: list[Source] = []
    for item in payload["sources"]:
        validate_api_url(item["api_url"])
        sources.append(Source(**item))
    return Settings(14, 1, tuple(sources))


def parse_timestamp(value: object, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise CollectionError(f"{field} must be a non-empty timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise CollectionError(f"{field} must be a valid ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise CollectionError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc)


def load_delivery_schedule(
    path: Path = DEFAULT_SCHEDULE,
) -> sync_schedule.DeliverySchedule:
    try:
        return sync_schedule.load_schedule(path)
    except (OSError, UnicodeError, sync_schedule.ScheduleError) as exc:
        raise ConfigurationError(f"Delivery schedule is invalid: {exc}") from exc


def parse_as_of(
    value: str | None,
    now: datetime,
    freshness_days: int,
    schedule: sync_schedule.DeliverySchedule | None = None,
) -> SelectionWindow:
    if value is None:
        return SelectionWindow(now - timedelta(days=freshness_days), now)
    delivery_schedule = schedule or load_delivery_schedule()
    try:
        as_of = date.fromisoformat(value)
    except ValueError as exc:
        raise ConfigurationError("--as-of must use YYYY-MM-DD") from exc
    if as_of.isoformat() != value:
        raise ConfigurationError("--as-of must use YYYY-MM-DD")
    delivery_zone = ZoneInfo(delivery_schedule.timezone)
    if as_of > now.astimezone(delivery_zone).date():
        raise ConfigurationError("--as-of cannot be after the collection date")
    local_cutoff = datetime(
        as_of.year,
        as_of.month,
        as_of.day,
        delivery_schedule.hour,
        delivery_schedule.minute,
        tzinfo=delivery_zone,
    )
    cutoff = local_cutoff.astimezone(timezone.utc)
    return SelectionWindow(cutoff - timedelta(days=freshness_days), cutoff)


def validate_release_url(url: object, tag_name: str, source: Source) -> str:
    if not isinstance(url, str):
        raise CollectionError(f"{source.id}: html_url must be a string")
    parsed = urlsplit(url)
    if (
        parsed.scheme != "https"
        or parsed.netloc != "github.com"
        or parsed.query
        or parsed.fragment
        or not parsed.path.startswith(source.release_path_prefix)
        or url != f"https://github.com{parsed.path}"
    ):
        raise CollectionError(f"{source.id}: html_url is outside the allowlisted path")
    encoded_tag = parsed.path.removeprefix(source.release_path_prefix)
    if not encoded_tag or unquote(encoded_tag) != tag_name:
        raise CollectionError(f"{source.id}: html_url does not match tag_name")
    return url


def parse_release(item: object, source: Source, now: datetime, index: int) -> ReleaseEntry:
    prefix = f"{source.id}.release[{index}]"
    if not isinstance(item, dict):
        raise CollectionError(f"{prefix} must be an object")
    required = {
        "draft",
        "prerelease",
        "tag_name",
        "html_url",
        "created_at",
        "published_at",
        "updated_at",
    }
    missing = sorted(required - item.keys())
    if missing:
        raise CollectionError(f"{prefix} is missing: {', '.join(missing)}")
    if type(item["draft"]) is not bool or type(item["prerelease"]) is not bool:
        raise CollectionError(f"{prefix}: draft and prerelease must be booleans")

    tag_name = item["tag_name"]
    if (
        not isinstance(tag_name, str)
        or not tag_name
        or tag_name != tag_name.strip()
        or "/" in tag_name
    ):
        raise CollectionError(f"{prefix}: tag_name is invalid")
    link = validate_release_url(item["html_url"], tag_name, source)
    created_at = parse_timestamp(item["created_at"], f"{prefix}.created_at")
    published_at = parse_timestamp(item["published_at"], f"{prefix}.published_at")
    updated_at = parse_timestamp(item["updated_at"], f"{prefix}.updated_at")
    if any(timestamp > now for timestamp in (created_at, published_at, updated_at)):
        raise CollectionError(f"{prefix}: release timestamps must not be in the future")
    return ReleaseEntry(
        tag_name,
        link,
        source.name,
        published_at,
        updated_at,
        stable=item["draft"] is False and item["prerelease"] is False,
    )


def parse_release_list(body: bytes, source: Source, now: datetime) -> list[ReleaseEntry]:
    if not isinstance(body, bytes):
        raise CollectionError(f"{source.id}: release response body must be bytes")
    if len(body) > MAX_RESPONSE_BYTES:
        raise CollectionError(f"{source.id}: release response is too large")
    try:
        text = body.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise CollectionError(f"{source.id}: release response is not UTF-8") from exc
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise CollectionError(f"{source.id}: release response is malformed JSON") from exc
    if not isinstance(payload, list):
        raise CollectionError(f"{source.id}: release response root must be an array")
    if len(payload) > PAGE_SIZE:
        raise CollectionError(f"{source.id}: release response exceeds per_page=100")
    return [
        parse_release(item, source, now, index)
        for index, item in enumerate(payload, start=1)
    ]


def entry_is_in_window(entry: ReleaseEntry, window: SelectionWindow) -> bool:
    return (
        entry.stable
        and window.start <= entry.published_at <= window.cutoff
        and entry.updated_at <= window.cutoff
    )


def sorted_fresh_entries(
    entries: list[ReleaseEntry], window: SelectionWindow
) -> list[ReleaseEntry]:
    return sorted(
        (entry for entry in entries if entry_is_in_window(entry, window)),
        key=lambda entry: (
            -entry.published_at.timestamp(),
            entry.source,
            entry.tag_name,
            entry.link,
        ),
    )


def collect_updates(
    settings: Settings,
    fetch: Fetcher,
    now: datetime,
    as_of: str | None = None,
    schedule: sync_schedule.DeliverySchedule | None = None,
) -> dict[str, str] | None:
    if now.tzinfo is None or now.utcoffset() is None:
        raise CollectionError("collection time must include a timezone")
    now = now.astimezone(timezone.utc)
    delivery_schedule = schedule or load_delivery_schedule()
    window = parse_as_of(as_of, now, settings.freshness_days, delivery_schedule)
    entries: list[ReleaseEntry] = []
    for source in settings.sources:
        for page in range(1, MAX_PAGES + 1):
            page_url = release_page_url(source, page)
            try:
                response = fetch(page_url)
            except CollectionError:
                raise
            except Exception as exc:
                raise CollectionError(f"{source.id}: release API request failed") from exc
            if not isinstance(response, FetchResponse):
                raise CollectionError(
                    f"{source.id}: release API response contract is invalid"
                )
            if type(response.status) is not int or response.status != 200:
                raise CollectionError(
                    f"{source.id}: release API request returned HTTP {response.status}"
                )
            if response.final_url != page_url:
                raise CollectionError(
                    f"{source.id}: release API request redirected outside the exact URL"
                )
            page_entries = parse_release_list(response.body, source, now)
            entries.extend(page_entries)
            if len(page_entries) < PAGE_SIZE:
                break
            if page == MAX_PAGES:
                raise CollectionError(
                    f"{source.id}: release pagination exceeded {MAX_PAGES} full pages"
                )

    if as_of is not None and any(
        window.start <= entry.published_at <= window.cutoff
        and entry.updated_at > window.cutoff
        for entry in entries
    ):
        raise CollectionError(
            "release history changed after the requested delivery cutoff"
        )

    candidates = sorted_fresh_entries(entries, window)[: settings.selection_limit]
    if not candidates:
        return None
    selected = candidates[0]
    return {
        "title": selected.tag_name,
        "date": selected.published_at.astimezone(
            ZoneInfo(delivery_schedule.timezone)
        ).date().isoformat(),
        "link": selected.link,
        "source": selected.source,
    }


def fetch_live(url: str) -> FetchResponse:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "career-feed-spring-updates",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            body = response.read(MAX_RESPONSE_BYTES + 1)
            status = response.status
            final_url = response.geturl()
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
        raise CollectionError(f"release API request failed for {url}") from exc
    if len(body) > MAX_RESPONSE_BYTES:
        raise CollectionError(f"release API response is too large for {url}")
    return FetchResponse(status, final_url, body)


def fixture_fetcher(fixture: dict[str, Any]) -> Fetcher:
    responses = fixture.get("responses")
    if not isinstance(responses, dict):
        raise ConfigurationError("fixture.responses must be an object")
    sources = tuple(Source(**item) for item in EXPECTED_SOURCES)
    base_urls = {source.api_url for source in sources}
    allowed_urls = {
        release_page_url(source, page)
        for source in sources
        for page in range(1, MAX_PAGES + 1)
    }
    response_urls = set(responses)
    if not base_urls.issubset(response_urls):
        raise ConfigurationError("fixture.responses must include both base API URLs")
    if not response_urls.issubset(allowed_urls):
        raise ConfigurationError(
            "fixture.responses contains a URL outside the pagination allowlist"
        )

    def fetch(url: str) -> FetchResponse:
        response = responses.get(url)
        if not isinstance(response, dict) or set(response) != {"status", "final_url", "body"}:
            raise CollectionError(f"fixture response is missing or invalid: {url}")
        status = response["status"]
        final_url = response["final_url"]
        body = response["body"]
        if type(status) is not int or not isinstance(final_url, str) or not isinstance(body, str):
            raise CollectionError(f"fixture response has invalid fields: {url}")
        return FetchResponse(status, final_url, body.encode("utf-8"))

    return fetch


def fixture_now(fixture: dict[str, Any], override: str | None) -> datetime:
    return parse_timestamp(override or fixture.get("now"), "fixture.now")


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", text=True
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as temporary:
            temporary.write(content)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def main() -> int:
    args = parse_args()
    try:
        settings = load_config(args.config)
        schedule = load_delivery_schedule(args.schedule_config)
        if args.live_dry_run:
            if args.now is not None:
                raise ConfigurationError("--now is only allowed in fixture mode")
            now = datetime.now(timezone.utc)
            fetch = fetch_live
        else:
            fixture = read_object(args.fixture, "Spring update fixture")
            now = fixture_now(fixture, args.now)
            fetch = fixture_fetcher(fixture)
        selected = collect_updates(settings, fetch, now, args.as_of, schedule)
        output = json.dumps(selected, ensure_ascii=False, sort_keys=True) + "\n"
        if args.stdout_only:
            print(output, end="")
        else:
            write_atomic(args.output, output)
    except (CollectionError, ConfigurationError, OSError) as exc:
        print(f"Spring update collector failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
