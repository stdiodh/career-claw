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


def test_deadline_unknown_active_detail_can_pass() -> None:
    item = parse_detail(build_detail_html(valid_through=""))
    assert item["deadline_confidence"] == "none"
    assert item["is_active"] is True
    assert item["exclude_reason"] == ""


def test_expired_deadline_is_excluded() -> None:
    item = parse_detail(build_detail_html(valid_through="2026-05-01T14:59:59.999Z"))
    assert "expired-or-past-event" in item["exclude_reason"]


def main() -> int:
    for name, value in sorted(globals().items()):
        if name.startswith("test_") and callable(value):
            value()
    print("weekly career collector tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
