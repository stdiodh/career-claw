#!/usr/bin/env python3
"""Focused checks for Weekly Career site radar output."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import urllib.parse
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COLLECTOR_PATH = ROOT / "scripts" / "collect-kr-feeds.py"
CONFIG_PATH = ROOT / "configs" / "weekly-career-site-radar.json"
REPORT_PATH = ROOT / "reports" / "briefs" / "kr-backend-career-weekly.md"

spec = importlib.util.spec_from_file_location("collector", COLLECTOR_PATH)
collector = importlib.util.module_from_spec(spec)
sys.modules[str(spec.name)] = collector
assert spec.loader is not None
spec.loader.exec_module(collector)

NOW = datetime(2026, 5, 28, 9, 7, 0, tzinfo=collector.KST)
REQUIRED_SECTION_IDS = {
    "official-careers",
    "job-intern-platforms",
    "activities-competitions",
}
NEWS_DOMAINS = {
    "news.naver.com",
    "n.news.naver.com",
    "etnews.com",
    "zdnet.co.kr",
    "bloter.net",
    "aitimes.com",
    "itworld.co.kr",
    "ciokorea.com",
    "ddaily.co.kr",
    "hankyung.com",
    "chosun.com",
    "joongang.co.kr",
    "donga.com",
    "yna.co.kr",
    "newsis.com",
}


def radar_config() -> dict[str, object]:
    assert CONFIG_PATH.exists()
    return collector.load_weekly_career_site_radar_config(CONFIG_PATH)


def sections_by_id() -> dict[str, dict[str, object]]:
    return {
        str(section["id"]): section
        for section in radar_config()["sections"]
        if isinstance(section, dict)
    }


def all_sites() -> list[dict[str, object]]:
    sites: list[dict[str, object]] = []
    for section in sections_by_id().values():
        section_sites = section.get("sites", [])
        assert isinstance(section_sites, list)
        sites.extend(site for site in section_sites if isinstance(site, dict))
    return sites


def site_names(section_id: str) -> set[str]:
    section = sections_by_id()[section_id]
    return {
        str(site.get("name", ""))
        for site in section.get("sites", [])
        if isinstance(site, dict)
    }


def site_urls() -> list[str]:
    urls: list[str] = []
    for site in all_sites():
        links = site.get("links", [])
        assert isinstance(links, list)
        for link in links:
            assert isinstance(link, dict)
            urls.append(str(link.get("url", "")))
    return urls


def test_site_radar_has_required_sections() -> None:
    sections = sections_by_id()
    assert set(sections) == REQUIRED_SECTION_IDS
    assert len(sections["official-careers"]["sites"]) >= 7
    assert len(sections["job-intern-platforms"]["sites"]) >= 6
    assert len(sections["activities-competitions"]["sites"]) >= 5


def test_site_ids_and_urls_are_unique() -> None:
    site_ids = [str(site.get("id", "")) for site in all_sites()]
    urls = site_urls()
    assert len(site_ids) == len(set(site_ids))
    assert len(urls) == len(set(urls))


def test_each_site_has_required_fields() -> None:
    for site in all_sites():
        for field in (
            "id",
            "name",
            "applies_to",
            "links",
            "search_keywords",
            "exclude_keywords",
            "check_rule",
        ):
            assert site.get(field), (site.get("name"), field)


def test_official_section_includes_required_company_sites() -> None:
    names = site_names("official-careers")
    required = {
        "NAVER Careers",
        "Kakao Careers",
        "LINE Careers",
        "Coupang Jobs",
        "우아한형제들 인재영입",
        "Toss Careers",
        "당근 팀 채용",
    }
    assert required.issubset(names)


def test_platform_section_includes_required_sources() -> None:
    names = site_names("job-intern-platforms")
    required = {
        "Linkareer",
        "Work24 청년일경험",
        "ZeroBase Zero Intern",
        "Saramin",
        "JobKorea",
        "Wanted",
        "Jumpit",
    }
    assert required.issubset(names)


def test_activity_section_includes_required_sources() -> None:
    names = site_names("activities-competitions")
    required = {"DACON", "AI Factory", "Programmers", "Wevity", "All-Con"}
    assert required.issubset(names)


def test_linkareer_keeps_activity_links_without_duplicate_site() -> None:
    linkareer = [site for site in all_sites() if site.get("id") == "linkareer"]
    assert len(linkareer) == 1
    links = linkareer[0].get("links", [])
    assert isinstance(links, list)
    labels = {str(link.get("label", "")) for link in links if isinstance(link, dict)}
    assert {"인턴 목록", "신입 목록", "대외활동 목록", "공모전 목록"}.issubset(labels)


def test_site_radar_has_no_news_urls() -> None:
    for url in site_urls():
        parsed = urllib.parse.urlsplit(url)
        domain = parsed.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        assert domain not in NEWS_DOMAINS, url
        assert "news" not in parsed.path.lower(), url


def test_site_radar_payload_uses_static_sections() -> None:
    payload = collector.build_weekly_career_site_radar_payload(NOW)
    assert payload["category"] == "weekly-career-site-radar"
    assert payload["generated_at"] == "2026-05-28 09:07:00 KST"
    assert payload["site_count"] == 19
    assert payload["duplicate_urls_removed"] == 0
    assert {section["id"] for section in payload["sections"]} == REQUIRED_SECTION_IDS


def test_compat_payload_is_disabled() -> None:
    payload = collector.build_disabled_weekly_career_compat_payload(
        "kr-backend-career-events",
        NOW,
    )
    assert payload["items"] == []
    assert payload["diagnostics"]["status"] == "disabled"
    assert "selected_by_category" not in payload


def test_render_script_generates_valid_markdown() -> None:
    subprocess.run(
        [sys.executable, "scripts/render-weekly-career-site-radar.py"],
        cwd=ROOT,
        check=True,
    )
    assert REPORT_PATH.exists()
    subprocess.run(
        [
            sys.executable,
            "scripts/validate-career-feed-brief.py",
            str(REPORT_PATH.relative_to(ROOT)),
            "--type",
            "weekly-career",
        ],
        cwd=ROOT,
        check=True,
    )


def main() -> int:
    for name, value in sorted(globals().items()):
        if name.startswith("test_") and callable(value):
            value()
    print("weekly career site radar tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
