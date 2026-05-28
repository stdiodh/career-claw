#!/usr/bin/env python3
"""Focused checks for Weekly Career site radar output."""

from __future__ import annotations

import importlib.util
import sys
import urllib.parse
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COLLECTOR_PATH = ROOT / "scripts" / "collect-kr-feeds.py"

spec = importlib.util.spec_from_file_location("collector", COLLECTOR_PATH)
collector = importlib.util.module_from_spec(spec)
sys.modules[str(spec.name)] = collector
assert spec.loader is not None
spec.loader.exec_module(collector)

NOW = datetime(2026, 5, 28, 9, 7, 0, tzinfo=collector.KST)
REQUIRED_SECTION_IDS = {"job", "intern", "hackathon", "contest", "competition"}
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
    return collector.load_weekly_career_site_radar_config()


def sections_by_id() -> dict[str, dict[str, object]]:
    return {
        str(section["id"]): section
        for section in radar_config()["sections"]
        if isinstance(section, dict)
    }


def site_names(section_id: str) -> set[str]:
    section = sections_by_id()[section_id]
    return {
        str(site.get("name", ""))
        for site in section.get("sites", [])
        if isinstance(site, dict)
    }


def site_urls() -> list[str]:
    urls: list[str] = []
    for section in sections_by_id().values():
        sites = section.get("sites", [])
        assert isinstance(sites, list)
        for site in sites:
            assert isinstance(site, dict)
            urls.append(str(site.get("url", "")))
    return urls


def test_site_radar_has_required_sections() -> None:
    sections = sections_by_id()
    assert set(sections) == REQUIRED_SECTION_IDS
    for section_id, section in sections.items():
        sites = section.get("sites", [])
        assert isinstance(sites, list), section_id
        assert len(sites) >= 3, section_id


def test_each_site_has_required_fields() -> None:
    for section_id, section in sections_by_id().items():
        sites = section.get("sites", [])
        assert isinstance(sites, list)
        for site in sites:
            assert isinstance(site, dict)
            for field in (
                "name",
                "url",
                "how_to_check",
                "keywords",
                "exclude_keywords",
                "backend_portfolio_angle",
            ):
                assert site.get(field), (section_id, field)


def test_job_section_includes_official_company_sites() -> None:
    names = site_names("job")
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


def test_intern_section_includes_required_sources() -> None:
    names = site_names("intern")
    required = {
        "Linkareer 인턴",
        "Work24 청년일경험",
        "Saramin 신입·인턴",
        "JobKorea 신입·인턴",
    }
    assert required.issubset(names)


def test_competition_section_includes_required_sources() -> None:
    names = site_names("competition")
    required = {"DACON", "AI Factory", "Programmers"}
    assert required.issubset(names)


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
    assert {section["id"] for section in payload["sections"]} == REQUIRED_SECTION_IDS


def test_compat_payload_is_disabled() -> None:
    payload = collector.build_disabled_weekly_career_compat_payload(
        "kr-backend-career-events",
        NOW,
    )
    assert payload["items"] == []
    assert payload["selected_by_category"] == {}
    assert payload["diagnostics"]["status"] == "disabled"


def main() -> int:
    for name, value in sorted(globals().items()):
        if name.startswith("test_") and callable(value):
            value()
    print("weekly career site radar tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
