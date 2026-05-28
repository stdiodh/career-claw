#!/usr/bin/env python3
"""Focused tests for Weekly Career discovery and final filtering helpers."""

from __future__ import annotations

import importlib.util
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COLLECTOR_PATH = ROOT / "scripts" / "collect-kr-feeds.py"

spec = importlib.util.spec_from_file_location("collector", COLLECTOR_PATH)
collector = importlib.util.module_from_spec(spec)
sys.modules[str(spec.name)] = collector
assert spec.loader is not None
spec.loader.exec_module(collector)

NOW = datetime(2026, 5, 28, 14, 23, 54, tzinfo=collector.KST)
CATEGORY = {
    "id": collector.WEEKLY_CAREER_CATEGORY_ID,
    "tags": ["backend", "internship"],
}


def build_detail_html(
    *,
    title: str = "예시테크 IT/인터넷 인턴",
    company: str = "예시테크",
    role: str = "IT/인터넷",
    valid_through: str = "2026-06-07T14:59:59.999Z",
) -> str:
    valid = f'"validThrough":"{valid_through}",' if valid_through else ""
    return f"""
    <html>
      <head>
        <title>{title} | 공모전 대외활동-링커리어</title>
        <script type="application/ld+json">
          {{
            "@context": "https://schema.org",
            "@type": "JobPosting",
            "title": "{title}",
            "datePosted": "2026-05-20T00:00:00.000Z",
            {valid}
            "employmentType": ["INTERN"],
            "experienceRequirements": ["신입"],
            "hiringOrganization": {{"@type": "Organization", "name": "{company}"}},
            "description": "{title}\\n[지원자격]\\n모집직무: {role}\\n고용형태: 신입"
          }}
        </script>
      </head>
      <body>
        <dl><dt>채용형태</dt><dd>체험형 인턴</dd></dl>
        <dl><dt>모집직무</dt><dd>{role}</dd></dl>
      </body>
    </html>
    """


def parse_detail(html: str, url: str = "https://linkareer.com/activity/320853"):
    discovered = collector.WeeklyDiscoveredUrl(
        url=url,
        source="Linkareer Intern",
        listing_url="https://linkareer.com/list/intern",
    )
    candidate = collector.parse_weekly_career_detail_page(
        url,
        html,
        CATEGORY,
        discovered,
        NOW,
        [],
    )
    assert candidate is not None
    return collector.normalize_weekly_career_candidate(candidate, NOW)


def weekly_item(
    weekly_category: str,
    selection_tier: str,
    *,
    title: str = "후보",
    freshness_tier: str = "fresh_this_week",
    score: int = 100,
    url: str = "https://linkareer.com/activity/320853",
) -> dict[str, object]:
    return {
        "title": title,
        "url": url,
        "source": "Linkareer",
        "source_kind": "job_platform_detail",
        "is_detail_url": True,
        "is_generic_url": False,
        "is_news_article": False,
        "is_active": True,
        "weekly_category": weekly_category,
        "category_label": collector.WEEKLY_CATEGORY_LABELS[weekly_category],
        "selection_tier": selection_tier,
        "freshness_tier": freshness_tier,
        "verification_status": "verified_active",
        "exclude_reason": "",
        "deadline_confidence": "high",
        "score": score,
    }


def test_listing_extracts_linkareer_detail() -> None:
    html = '<a href="/activity/320853">상세</a><a href="/list/intern">목록</a>'
    assert collector.extract_links_from_listing_page(
        html,
        "https://linkareer.com/list/intern",
    ) == ["https://linkareer.com/activity/320853"]


def test_linkareer_detail_parses_fields() -> None:
    item = parse_detail(build_detail_html())
    assert item["title"] == "예시테크 IT/인터넷 인턴"
    assert item["company_or_host"] == "예시테크"
    assert item["deadline_confidence"] == "high"
    assert item["type"] == "인턴"
    assert item["selection_tier"] == "backend_adjacent"
    assert item["exclude_reason"] == ""


def test_marketing_only_role_is_excluded() -> None:
    item = parse_detail(
        build_detail_html(
            title="예시테크 마케팅 인턴",
            role="마케팅/광고/홍보",
        )
    )
    assert "non-developer-role" in item["exclude_reason"]


def test_system_development_role_is_backend_adjacent() -> None:
    item = parse_detail(build_detail_html(role="ERP/시스템개발/설계"))
    assert item["selection_tier"] == "backend_adjacent"
    assert item["exclude_reason"] == ""


def test_naver_news_candidate_is_excluded() -> None:
    candidate = collector.build_candidate(
        category=CATEGORY,
        title="백엔드 인턴 기사",
        url="https://news.naver.com/main/read.naver?oid=001&aid=1",
        source_url="https://news.naver.com/main/read.naver?oid=001&aid=1",
        source="Naver News Search",
        publisher="news.naver.com",
        published_at=None,
        summary="백엔드 인턴 모집 기사",
        query="백엔드 인턴",
        source_reliability="aggregator",
        current_time=NOW,
        penalty_keywords=[],
    )
    assert candidate is not None
    item = collector.normalize_weekly_career_candidate(candidate, NOW)
    assert "naver-news-not-career-source" in item["exclude_reason"]
    assert item["is_news_article"] is True


def test_generic_url_is_excluded() -> None:
    candidate = collector.build_candidate(
        category=CATEGORY,
        title="링커리어 인턴 목록",
        url="https://linkareer.com/list/intern",
        source_url="https://linkareer.com/list/intern",
        source="Linkareer",
        publisher="linkareer.com",
        published_at=None,
        summary="상태: 모집 중 IT/인터넷 인턴",
        query="reference_page",
        source_reliability="platform",
        current_time=NOW,
        penalty_keywords=[],
    )
    assert candidate is not None
    item = collector.normalize_weekly_career_candidate(candidate, NOW)
    assert "generic-url" in item["exclude_reason"]


def test_linkareer_cover_letter_url_is_excluded() -> None:
    candidate = collector.build_candidate(
        category=CATEGORY,
        title="합격 자기소개서 백엔드 인턴",
        url="https://linkareer.com/cover-letter/12345",
        source_url="https://linkareer.com/cover-letter/12345",
        source="Linkareer",
        publisher="Linkareer",
        published_at=None,
        summary="백엔드 인턴 자기소개서 참고자료입니다. 상태: 모집 중",
        query="reference_page",
        source_reliability="platform",
        current_time=NOW,
        penalty_keywords=[],
    )
    assert candidate is not None
    item = collector.normalize_weekly_career_candidate(candidate, NOW)
    assert item["is_detail_url"] is False
    assert "reference-material-not-career-opportunity" in item["exclude_reason"]


def test_deadline_unknown_active_detail_can_pass() -> None:
    item = parse_detail(build_detail_html(valid_through=""))
    assert item["deadline_confidence"] == "none"
    assert item["is_active"] is True
    assert item["exclude_reason"] == ""


def test_expired_deadline_is_excluded() -> None:
    item = parse_detail(build_detail_html(valid_through="2026-05-01T14:59:59.999Z"))
    assert "expired-or-past-event" in item["exclude_reason"]


def test_weekly_category_classifier() -> None:
    assert collector.classify_weekly_category_from_text("신입 백엔드 개발자") == "job"
    assert collector.classify_weekly_category_from_text("채용연계형 인턴") == "intern"
    assert collector.classify_weekly_category_from_text("AI 서비스 해커톤") == "hackathon"
    assert collector.classify_weekly_category_from_text("SW 개발 공모전") == "contest"
    assert collector.classify_weekly_category_from_text("데이터 AI 경진대회") == "competition"


def test_selected_by_category_picks_one_each() -> None:
    coverage = collector.default_weekly_career_coverage_config()
    items = [
        weekly_item("job", "backend_direct", title="채용"),
        weekly_item("intern", "backend_adjacent", title="인턴"),
        weekly_item("hackathon", "portfolio_activity", title="해커톤"),
        weekly_item("contest", "portfolio_activity", title="공모전"),
        weekly_item("competition", "portfolio_activity", title="경진대회"),
    ]
    selected = collector.select_weekly_career_by_category(items, [], coverage, NOW)
    assert set(selected) == set(collector.WEEKLY_CATEGORY_ORDER)
    assert all(selected[key] is not None for key in collector.WEEKLY_CATEGORY_ORDER)


def test_selected_by_category_in_payload_has_all_categories() -> None:
    payload = collector.build_weekly_career_payload(
        collector.WEEKLY_CAREER_CATEGORY_ID,
        NOW,
        [],
        [],
        update_cache=False,
    )
    assert set(payload["selected_by_category"]) == set(collector.WEEKLY_CATEGORY_ORDER)


def test_selection_prefers_fresh_and_stronger_tier() -> None:
    coverage = collector.default_weekly_career_coverage_config()
    cached = weekly_item(
        "job",
        "backend_direct",
        title="캐시 채용",
        freshness_tier="cached_revalidated",
        score=200,
        url="https://linkareer.com/activity/320854",
    )
    fresh_adjacent = weekly_item("job", "backend_adjacent", title="fresh 채용", score=10)
    selected = collector.select_weekly_career_by_category([fresh_adjacent], [cached], coverage, NOW)
    assert selected["job"]["title"] == "fresh 채용"

    direct = weekly_item("job", "backend_direct", title="direct", score=10)
    adjacent = weekly_item(
        "job",
        "backend_adjacent",
        title="adjacent",
        score=200,
        url="https://linkareer.com/activity/320855",
    )
    selected = collector.select_weekly_career_by_category([adjacent, direct], [], coverage, NOW)
    assert selected["job"]["title"] == "direct"


def test_portfolio_activity_is_allowed_for_activity_categories() -> None:
    coverage = collector.default_weekly_career_coverage_config()
    portfolio = weekly_item("hackathon", "portfolio_activity", title="포트폴리오 해커톤")
    selected = collector.select_weekly_career_by_category([portfolio], [], coverage, NOW)
    assert selected["hackathon"]["title"] == "포트폴리오 해커톤"


def test_cache_revalidation_uses_active_detail(monkeypatch=None) -> None:
    original_fetch = collector.fetch_weekly_career_detail_page

    def fake_fetch(url: str) -> str:
        assert url == "https://linkareer.com/activity/320853"
        return build_detail_html(title="예시테크 채용연계형 인턴")

    collector.fetch_weekly_career_detail_page = fake_fetch
    try:
        items, diagnostics = collector.revalidate_weekly_career_cache(
            [
                {
                    "url": "https://linkareer.com/activity/320853",
                    "title": "예시테크 채용연계형 인턴",
                    "weekly_category": "intern",
                    "category_label": "인턴",
                    "source": "Linkareer",
                    "source_kind": "job_platform_detail",
                    "selection_tier": "backend_adjacent",
                    "first_seen_at": "2026-05-20 00:00:00 KST",
                    "last_seen_at": "2026-05-20 00:00:00 KST",
                    "last_verified_at": "2026-05-20 00:00:00 KST",
                    "verification_status": "verified_active",
                }
            ],
            CATEGORY,
            NOW,
            [],
            {"intern"},
            collector.default_weekly_career_coverage_config(),
        )
    finally:
        collector.fetch_weekly_career_detail_page = original_fetch
    assert diagnostics["revalidated"] == 1
    assert items[0]["freshness_tier"] == "cached_revalidated"
    assert items[0]["weekly_category"] == "intern"


def test_cache_revalidation_excludes_expired_generic_and_news() -> None:
    calls = {"count": 0}
    original_fetch = collector.fetch_weekly_career_detail_page

    def fake_fetch(url: str) -> str:
        calls["count"] += 1
        return build_detail_html(valid_through="2026-05-01T14:59:59.999Z")

    collector.fetch_weekly_career_detail_page = fake_fetch
    try:
        items, diagnostics = collector.revalidate_weekly_career_cache(
            [
                {
                    "url": "https://linkareer.com/activity/320853",
                    "title": "만료 인턴",
                    "weekly_category": "intern",
                    "category_label": "인턴",
                    "source": "Linkareer",
                    "last_verified_at": "2026-05-20 00:00:00 KST",
                },
                {
                    "url": "https://linkareer.com/list/intern",
                    "title": "목록",
                    "weekly_category": "intern",
                    "source": "Linkareer",
                    "last_verified_at": "2026-05-20 00:00:00 KST",
                },
                {
                    "url": "https://news.naver.com/main/read.naver?oid=001&aid=1",
                    "title": "뉴스",
                    "weekly_category": "intern",
                    "source": "Naver News Search",
                    "last_verified_at": "2026-05-20 00:00:00 KST",
                },
            ],
            CATEGORY,
            NOW,
            [],
            {"intern"},
            collector.default_weekly_career_coverage_config(),
        )
    finally:
        collector.fetch_weekly_career_detail_page = original_fetch
    assert calls["count"] == 1
    assert diagnostics["revalidated"] == 1
    assert items == []


def test_coverage_diagnostics_include_all_categories() -> None:
    payload = collector.build_weekly_career_payload(
        collector.WEEKLY_CAREER_CATEGORY_ID,
        NOW,
        [weekly_item("job", "backend_direct", title="채용")],
        [],
        diagnostics={"coverage": {"job": {"sources": {"Linkareer": {"discovered": 1}}}}},
        update_cache=False,
    )
    coverage_diagnostics = payload["diagnostics"]["coverage"]
    assert set(coverage_diagnostics) == set(collector.WEEKLY_CATEGORY_ORDER)
    assert coverage_diagnostics["intern"]["why_empty"]
    assert "sources" in coverage_diagnostics["job"]
    assert payload["diagnostics"]["empty_categories"]


def test_company_watchlist_config_contains_required_companies() -> None:
    names = {str(company.get("name", "")) for company in collector.load_company_watchlist()}
    assert {"NAVER", "Kakao", "LINE", "Coupang", "우아한형제들", "Toss", "당근"}.issubset(names)


def test_company_watchlist_diagnostics_include_required_sources() -> None:
    diagnostics = collector.build_weekly_career_payload(
        collector.WEEKLY_CAREER_CATEGORY_ID,
        NOW,
        [],
        [],
        update_cache=False,
    )["diagnostics"]
    checked = diagnostics["company_watchlist"]["checked"]
    sources = {str(item.get("source", "")) for item in checked}
    assert {
        "NAVER Careers",
        "Kakao Careers",
        "LINE Careers",
        "Coupang Jobs",
        "Woowa Careers",
        "Toss Careers",
        "Daangn Careers",
    }.issubset(sources)


def test_prompt_safe_selected_output() -> None:
    coverage = collector.default_weekly_career_coverage_config()
    selected = collector.select_weekly_career_by_category(
        [
            weekly_item("job", "backend_direct", title="safe"),
            {
                **weekly_item("intern", "backend_adjacent", title="bad"),
                "url": "https://linkareer.com/list/intern",
                "is_generic_url": True,
            },
            {
                **weekly_item("contest", "portfolio_activity", title="excluded"),
                "exclude_reason": "generic-url",
            },
        ],
        [],
        coverage,
        NOW,
    )
    assert selected["job"]["source"] != "Naver News Search"
    assert selected["job"]["exclude_reason"] == ""
    assert selected["intern"] is None
    assert selected["contest"] is None


def main() -> int:
    for name, value in sorted(globals().items()):
        if name.startswith("test_") and callable(value):
            value()
    print("weekly career collector tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
