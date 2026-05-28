#!/usr/bin/env python3
"""Validate Career Feed Markdown brief quality."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


DEFAULT_REPORT = "reports/briefs/kr-tech-daily.md"
MAX_WARNING_CHARS = 6500


def joined(*parts: str) -> str:
    return "".join(parts)

DAILY_SECTIONS = [
    "오늘의 Spring Boot/JVM 학습",
    "이번 주 PS 성장 루틴",
    "오픈소스 기여 후보",
    "한국 최신 개발/AI 뉴스",
    "주니어 백엔드 실무지식",
]
WEEKLY_SECTIONS = [
    "이번 주 백엔드 커리어 기회 TOP 5",
    "마감 임박",
    "포트폴리오로 남기기 좋은 대외활동",
]

NO_ITEM_PHRASES = [
    "오늘 확인된 주요 항목 없음",
    "오늘 확인된 주요 항목이 없습니다",
    "오늘 기준으로 포함할 만한 신뢰도 높은 후보를 찾지 못했습니다",
    "오늘은 긴급 체크 항목 없음",
    "오늘은 주니어가 바로 시도하기 좋은 오픈소스 후보가 없습니다.",
    "오늘은 기준을 만족하는 한국 최신 개발/AI 뉴스가 없습니다.",
    "이번 주 마감 임박 항목 없음",
    "이번 주 추천 항목 없음",
    "이번 주 기준을 만족하는 백엔드 커리어 기회가 없습니다.",
    "이번 주 마감 임박 항목은 없습니다.",
    "이번 주 포트폴리오용 대외활동 후보는 없습니다.",
]

GENERIC_PHRASES = [
    "개발 워크플로 또는 API 사용 방식 변화 확인이 필요합니다.",
    "실무 영향 여부를 원문에서 확인할 필요가 있습니다.",
    "패치 또는 영향 범위 확인이 필요합니다.",
]

DAILY_FORBIDDEN_PATTERNS = [
    r"##\s*" + joined("오늘 ", "할 일"),
    joined("오늘 ", "할 일"),
    r"\bBOJ\b",
    r"acmicpc\.net",
    r"백준",
    r"매일\s*랜덤\s*문제",
    r"정답\s*코드\s*제공",
    r"왜 나에게 중요한가",
    joined("Kotlin/Spring Boot ", "관련성"),
    r"백엔드 관점",
    r"긴급 체크",
]
DAILY_STUDY_FIELDS = [
    "핵심 개념",
    "30분 실습",
    "완료 기준",
    "확장해서 볼 것",
    "참고 링크",
]
DAILY_PS_FIELDS = [
    "이번 주 주제",
    "이번 주 목표",
    "현재 진행",
    "오늘 문제",
    "플랫폼",
    "난이도",
    "먼저 생각할 것",
    "풀이 후 점검",
    "막히면 검색",
    "링크",
]
DAILY_NEWS_FIELDS = [
    "제목",
    "출처/게시",
    "핵심",
    "실무 연결",
    "검색 키워드",
    "링크",
]
DAILY_PRACTICAL_FIELDS = [
    "큰 흐름",
    "핵심 개념",
    "30분 실습",
    "현업 체크 질문",
    "검색 키워드",
]
DAILY_NEWS_EMPTY_STATE = "오늘은 기준을 만족하는 한국 최신 개발/AI 뉴스가 없습니다."
DAILY_OSS_EMPTY_STATE = "오늘은 주니어가 바로 시도하기 좋은 오픈소스 후보가 없습니다."
DAILY_NEWS_FORBIDDEN_PATTERNS = [
    r"docs\.spring\.io",
    r"(?<!docs\.)\bspring\.io",
    r"github\.com",
    r"kotlinlang\.org",
    r"docs\.oracle\.com",
    r"programmers\.co\.kr",
    r"school\.programmers\.co\.kr",
    r"Official reference page",
    r"reference_page",
    r"Spring Boot Reference",
    r"Spring Framework Reference",
    r"공식 문서",
    r"Issue 보기",
    r"공부로 연결할 점",
]
WEEKLY_REQUIRED_FIELDS = [
    "유형",
    "마감",
    "회사/주최",
    "직무/역할",
    "지원 조건",
    "기술 키워드",
    "전형/제출물",
    "이번 주 액션",
    "출처",
    "링크",
]
WEEKLY_FORBIDDEN_FIELDS = [
    joined("대상 ", "적합성"),
    joined("백엔드 ", "적합성"),
    joined("Kotlin/Spring Boot ", "관련성"),
    joined("왜 나에게 ", "맞는가"),
    "내 액션",
]
WEEKLY_FORBIDDEN_DEADLINE_VALUES = [
    "원문 확인 필요",
    "확인 필요",
    "미정",
    "알 수 없음",
]
WEEKLY_TOP_EMPTY_STATE = "이번 주 기준을 만족하는 백엔드 커리어 기회가 없습니다."
WEEKLY_URGENT_EMPTY_STATE = "이번 주 마감 임박 항목은 없습니다."
WEEKLY_PORTFOLIO_EMPTY_STATE = "이번 주 포트폴리오용 대외활동 후보는 없습니다."
WEEKLY_PORTFOLIO_FIELDS = [
    "유형",
    "마감",
    "주최",
    "만들 수 있는 백엔드 산출물",
    "기술 키워드",
    "이번 주 액션",
    "링크",
]
WEEKLY_GENERIC_URLS = {
    "https://www.wanted.co.kr",
    "https://www.wanted.co.kr/",
    "https://dacon.io/competitions",
    "https://linkareer.com",
    "https://linkareer.com/",
    "https://www.saramin.co.kr",
    "https://www.saramin.co.kr/",
    "https://www.saramin.co.kr/zf_user",
    "https://www.saramin.co.kr/zf_user/",
    "https://www.jobkorea.co.kr",
    "https://www.jobkorea.co.kr/",
    "https://programmers.co.kr",
    "https://programmers.co.kr/",
    "https://aifactory.space",
    "https://aifactory.space/",
    "https://www.wevity.com",
    "https://www.wevity.com/",
    "https://www.all-con.co.kr",
    "https://www.all-con.co.kr/",
}
DAILY_OSS_FIELDS = [
    "상태 확인",
    "난이도 밴드",
    "저장소",
    "기여 유형",
    "왜 시도해볼 만한가",
    "첫 30분 액션",
    "기여 전 매너",
    "확인할 파일/키워드",
    "주의할 점",
    "링크",
]
DAILY_OSS_FORBIDDEN_PATTERNS = [
    r"바로\s*PR",
    r"바로\s*구현",
    r"전체\s*구조를\s*파악",
    r"담당자\s*있음",
    r"연결\s*PR\s*있음",
    r"연결\s*branch\s*있음",
    r"작업\s*중",
    r"claim\s*있음",
    r"\bapprove\b",
    r"\breject\b",
    r"리뷰\s*승인",
]
DAILY_OSS_STATUS_CHECK_TERMS = [
    r"maintainer",
    r"메인테이너",
    r"담당자\s*없음",
    r"연결\s*PR",
    r"연결\s*branch",
    r"claim\s*댓글",
    r"작업\s*claim",
]

LINK_RE = re.compile(r"https?://[^\s)>\\\]]+")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(https?://[^)]+\)")
SECTION_HEADING_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
ITEM_HEADING_RE = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)
SECRET_RE = re.compile(
    r"(OPENAI_API_KEY|DISCORD_WEBHOOK|NAVER_CLIENT_SECRET|"
    r"https://(?:discord(?:app)?\.com/api/webhooks|hooks\.slack\.com)/|"
    r"sk-[A-Za-z0-9_-]{20,})"
)


@dataclass(frozen=True)
class Section:
    heading: str
    body: str


@dataclass(frozen=True)
class Item:
    title: str
    body: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Career Feed Markdown brief.")
    parser.add_argument("path", nargs="?", default=DEFAULT_REPORT)
    parser.add_argument(
        "--type",
        choices=["daily-tech", "weekly-career"],
        default="daily-tech",
        help="Brief type to validate.",
    )
    return parser.parse_args()


def fail(message: str) -> None:
    raise RuntimeError(message)


def warn(message: str) -> None:
    print(f"Warning: {message}", file=sys.stderr)


def read_report(path: Path) -> str:
    if not path.exists():
        fail(f"Markdown file does not exist: {path}")
    if not path.is_file():
        fail(f"Markdown path is not a file: {path}")

    content = path.read_text(encoding="utf-8").strip()
    if not content:
        fail(f"Markdown file is empty: {path}")
    return content


def validate_timestamp(content: str) -> None:
    if "기준시각:" not in content:
        fail("Missing 기준시각 field.")
    if not re.search(r"기준시각:\s*.+KST", content):
        fail("기준시각 must include a KST timestamp.")


def extract_sections(content: str) -> list[Section]:
    matches = list(SECTION_HEADING_RE.finditer(content))
    sections: list[Section] = []
    for index, match in enumerate(matches):
        heading = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        sections.append(Section(heading=heading, body=content[start:end].strip()))
    return sections


def find_section(sections: list[Section], title: str) -> Section | None:
    for section in sections:
        if title in section.heading:
            return section
    return None


def require_sections(sections: list[Section], titles: list[str]) -> None:
    missing = [title for title in titles if find_section(sections, title) is None]
    if missing:
        fail(f"Missing required section(s): {', '.join(missing)}")


def extract_items(section: Section) -> list[Item]:
    matches = list(ITEM_HEADING_RE.finditer(section.body))
    items: list[Item] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(section.body)
        items.append(Item(title=match.group(1).strip(), body=section.body[start:end].strip()))
    return items


def section_has_no_item_phrase(section: Section) -> bool:
    return any(phrase in section.body for phrase in NO_ITEM_PHRASES)


def validate_common(
    content: str,
    min_links: int = 2,
    *,
    allow_duplicate_links: bool = False,
) -> None:
    validate_timestamp(content)
    validate_secret_leaks(content)
    validate_links(content, min_links, allow_duplicate_links=allow_duplicate_links)
    validate_generic_phrases(content)
    validate_missing_source_link_phrases(content)
    validate_no_tables(content)
    if len(content) > MAX_WARNING_CHARS:
        warn(f"Markdown is long for Discord reading: {len(content)} chars")


def validate_secret_leaks(content: str) -> None:
    if SECRET_RE.search(content):
        fail("Secret, API key, or webhook-like value found in Markdown.")


def validate_links(
    content: str,
    min_links: int,
    *,
    allow_duplicate_links: bool = False,
) -> None:
    links = LINK_RE.findall(content)
    if len(links) < min_links:
        fail(f"Expected at least {min_links} links, found {len(links)}.")
    duplicated = sorted({link for link in links if links.count(link) > 1})
    if duplicated and not allow_duplicate_links:
        fail(f"Duplicate links found: {', '.join(duplicated[:3])}")


def validate_generic_phrases(content: str) -> None:
    found = [phrase for phrase in GENERIC_PHRASES if phrase in content]
    if found:
        fail(f"Generic placeholder phrase found: {', '.join(found)}")


def validate_missing_source_link_phrases(content: str) -> None:
    if "링크 없음" in content or re.search(r"링크\s*:\s*없음", content):
        fail("Found item with missing link text.")
    if "출처 없음" in content or re.search(r"출처(?:/시각)?\s*:\s*없음", content):
        warn("Found item with missing source text.")


def validate_no_tables(content: str) -> None:
    if any(line.strip().startswith("|") for line in content.splitlines()):
        fail("Markdown tables are not allowed in Career Feed briefs.")


def validate_item_markdown_link(item: Item) -> None:
    if not MARKDOWN_LINK_RE.search(item.body):
        fail(f"Item must include a Markdown link: {item.title}")


def missing_bullet_fields(text: str, fields: list[str]) -> list[str]:
    return [
        field
        for field in fields
        if not re.search(rf"^\s*-\s*{re.escape(field)}\s*:", text, re.MULTILINE)
    ]


def require_markdown_link_in_text(text: str, context: str) -> None:
    if not MARKDOWN_LINK_RE.search(text):
        fail(f"Section must include a Markdown link: {context}")


def bullet_field_value(text: str, field: str) -> str:
    match = re.search(
        rf"^\s*-\s*{re.escape(field)}\s*:\s*(.+?)\s*$",
        text,
        flags=re.MULTILINE,
    )
    return match.group(1).strip() if match else ""


def markdown_link_urls(text: str) -> list[str]:
    return re.findall(r"\[[^\]]+\]\((https?://[^)]+)\)", text)


def normalize_validation_url(url: str) -> str:
    return url.strip().rstrip("/")


def is_generic_weekly_url(url: str) -> bool:
    normalized = normalize_validation_url(url)
    generic = {normalize_validation_url(item) for item in WEEKLY_GENERIC_URLS}
    return normalized in generic


def validate_weekly_deadline_value(value: str, context: str) -> None:
    if any(forbidden in value for forbidden in WEEKLY_FORBIDDEN_DEADLINE_VALUES):
        fail(f"Weekly career deadline is not actionable: {context}")
    if value in {"상시채용", "채용 시 마감"}:
        return
    if re.fullmatch(r"20\d{2}-\d{2}-\d{2}(?: \d{2}:\d{2})? KST \(D-\d+\)", value):
        return
    fail(f"Weekly career deadline has invalid format: {context} ({value})")


def validate_weekly_item_links(text: str, context: str) -> None:
    urls = markdown_link_urls(text)
    if not urls:
        fail(f"Item must include a Markdown link: {context}")
    generic_urls = [url for url in urls if is_generic_weekly_url(url)]
    if generic_urls:
        fail(f"Weekly career item uses generic URL: {context} ({generic_urls[0]})")


def validate_daily_tech(content: str) -> None:
    if (
        "Career Feed - Backend Daily" not in content
        and "Career Feed - Korea Tech Daily" not in content
    ):
        fail("Missing daily tech title.")
    validate_daily_forbidden_text(content)
    sections = extract_sections(content)
    validate_common(content, min_links=2)
    require_sections(sections, DAILY_SECTIONS)

    if re.search(r"^##\s+.*(?:커리어|인턴|공모전|해커톤)", content, re.MULTILINE):
        fail("Daily tech brief must not include a long career event section.")

    if any(keyword in content for keyword in ["주가", "관련주", "투자의견"]):
        warn("Daily tech brief may contain stock/investment-only wording.")

    validate_daily_study_section(sections)
    validate_daily_ps_section(sections)
    validate_daily_oss_section(sections)
    validate_daily_news_section(sections)
    validate_daily_practical_section(sections)


def validate_daily_forbidden_text(content: str) -> None:
    found = [
        pattern
        for pattern in DAILY_FORBIDDEN_PATTERNS
        if re.search(pattern, content, flags=re.IGNORECASE)
    ]
    if found:
        fail(f"Daily tech brief contains forbidden wording: {', '.join(found)}")


def validate_daily_study_section(sections: list[Section]) -> None:
    section = find_section(sections, "오늘의 Spring Boot/JVM 학습")
    if section is None:
        fail("Daily tech brief must include 오늘의 Spring Boot/JVM 학습 section.")

    items = extract_items(section)
    if len(items) != 1:
        fail("Spring Boot/JVM study section must include exactly one topic.")
    item = items[0]
    missing = missing_bullet_fields(item.body, DAILY_STUDY_FIELDS)
    if missing:
        fail(f"Spring Boot/JVM study topic is missing field(s): {', '.join(missing)}")
    if re.search(r"^\s*-\s*검색 키워드\s*:", item.body, re.MULTILINE):
        fail("Spring Boot/JVM study section must use 완료 기준, not 검색 키워드.")
    validate_item_markdown_link(item)


def validate_daily_ps_section(sections: list[Section]) -> None:
    section = find_section(sections, "이번 주 PS 성장 루틴")
    if section is None:
        fail("Daily tech brief must include 이번 주 PS 성장 루틴 section.")

    missing = missing_bullet_fields(section.body, DAILY_PS_FIELDS)
    if missing:
        fail(f"PS routine section is missing field(s): {', '.join(missing)}")
    if re.search(r"^\s*-\s*오늘 목표\s*:", section.body, re.MULTILINE):
        fail("PS routine section must use 풀이 후 점검, not 오늘 목표.")
    if "Programmers" not in section.body and "school.programmers.co.kr" not in section.body:
        fail("PS routine section must reference Programmers.")
    require_markdown_link_in_text(section.body, "이번 주 PS 성장 루틴")


def validate_daily_oss_section(sections: list[Section]) -> None:
    section = find_section(sections, "오픈소스 기여 후보")
    if section is None:
        fail("Daily tech brief must include 오픈소스 기여 후보 section.")

    found_forbidden = [
        pattern
        for pattern in DAILY_OSS_FORBIDDEN_PATTERNS
        if re.search(pattern, section.body, flags=re.IGNORECASE)
    ]
    if found_forbidden:
        fail(f"OSS section contains forbidden phrase(s): {', '.join(found_forbidden)}")

    has_issue_link = bool(
        re.search(r"\[Issue 보기\]\(https://github\.com/[^)]+/issues/\d+\)", section.body)
        or re.search(r"https://github\.com/[^\s)]+/issues/\d+", section.body)
    )
    if DAILY_OSS_EMPTY_STATE not in section.body and not has_issue_link:
        fail("OSS section must include an Issue 보기 link or the required empty-state phrase.")

    items = extract_items(section)
    if len(items) > 1:
        fail("OSS section must include at most one candidate.")
    if not items:
        if DAILY_OSS_EMPTY_STATE in section.body:
            return
        fail("OSS section has no candidate and no required empty-state phrase.")

    item = items[0]
    if not re.search(r"P[45]-like", item.body):
        fail("OSS candidate must include P5-like or P4-like difficulty band.")
    if re.search(r"too_hard|unclear", item.body, flags=re.IGNORECASE):
        fail("OSS candidate must not recommend too_hard or unclear issues.")
    missing = missing_bullet_fields(item.body, DAILY_OSS_FIELDS)
    if missing:
        fail(f"OSS candidate is missing field(s): {item.title} ({', '.join(missing)})")
    status_check = bullet_field_value(item.body, "상태 확인")
    matched_status_terms = [
        pattern
        for pattern in DAILY_OSS_STATUS_CHECK_TERMS
        if re.search(pattern, status_check, flags=re.IGNORECASE)
    ]
    if len(matched_status_terms) < 2:
        fail("OSS 상태 확인 must include at least two verification signals.")
    first_action = bullet_field_value(item.body, "첫 30분 액션")
    if re.match(r"`?(PR\s*생성|코드\s*수정|구현)", first_action, flags=re.IGNORECASE):
        fail("OSS 첫 30분 액션 must not start with PR creation or code editing.")
    validate_item_markdown_link(item)


def validate_daily_news_section(sections: list[Section]) -> None:
    section = find_section(sections, "한국 최신 개발/AI 뉴스")
    if section is None:
        fail("Daily tech brief must include 한국 최신 개발/AI 뉴스 section.")

    found_forbidden = [
        pattern
        for pattern in DAILY_NEWS_FORBIDDEN_PATTERNS
        if re.search(pattern, section.body, flags=re.IGNORECASE)
    ]
    if found_forbidden:
        fail(f"Daily news section contains forbidden source or field: {', '.join(found_forbidden)}")

    items = extract_items(section)
    if len(items) > 1:
        fail("Daily development/AI news section must include at most one item.")
    if not items and DAILY_NEWS_EMPTY_STATE in section.body:
        return

    body = items[0].body if items else section.body
    missing = missing_bullet_fields(body, DAILY_NEWS_FIELDS)
    if missing:
        fail(f"Daily development/AI news is missing field(s): {', '.join(missing)}")
    require_markdown_link_in_text(body, "한국 최신 개발/AI 뉴스")


def validate_daily_practical_section(sections: list[Section]) -> None:
    section = find_section(sections, "주니어 백엔드 실무지식")
    if section is None:
        fail("Daily tech brief must include 주니어 백엔드 실무지식 section.")

    items = extract_items(section)
    if len(items) != 1:
        fail("Backend practical knowledge section must include exactly one topic.")
    item = items[0]
    if not item.title.startswith("주제:"):
        fail("Backend practical knowledge topic must use a 주제 heading.")
    missing = missing_bullet_fields(item.body, DAILY_PRACTICAL_FIELDS)
    if missing:
        fail(f"Backend practical knowledge topic is missing field(s): {', '.join(missing)}")
    if len(section.body) > 1200:
        warn("Backend practical knowledge section may be too long for daily reading.")


def validate_weekly_career(content: str) -> None:
    if "Career Feed - Backend Career Weekly" not in content:
        fail("Missing weekly career title.")
    validate_weekly_forbidden_text(content)
    sections = extract_sections(content)
    validate_common(content, min_links=0, allow_duplicate_links=True)
    require_sections(sections, WEEKLY_SECTIONS)

    top_section = find_section(sections, "이번 주 백엔드 커리어 기회 TOP 5")
    if top_section is None:
        return
    top_items = extract_items(top_section)
    if not top_items and WEEKLY_TOP_EMPTY_STATE not in top_section.body:
        fail("Weekly career recommendations are missing.")
    if len(top_items) > 5:
        fail("Weekly career TOP 5 must include at most five items.")
    for item in top_items:
        validate_weekly_item(item)
        validate_weekly_recommended_text(item)

    validate_weekly_urgent_section(sections)
    validate_weekly_portfolio_section(sections)


def validate_weekly_forbidden_text(content: str) -> None:
    excluded_section = joined("제외한 ", "후보")
    if re.search(rf"^##\s+.*{re.escape(excluded_section)}", content, flags=re.MULTILINE):
        fail("Weekly career brief must not include an excluded-candidate section.")
    found_fields = [
        field
        for field in WEEKLY_FORBIDDEN_FIELDS
        if re.search(rf"^\s*-\s*{re.escape(field)}\s*:", content, flags=re.MULTILINE)
    ]
    if found_fields:
        fail(f"Weekly career brief contains forbidden field(s): {', '.join(found_fields)}")


def validate_weekly_item(item: Item) -> None:
    missing = missing_bullet_fields(item.body, WEEKLY_REQUIRED_FIELDS)
    if missing:
        fail(f"Weekly career item is missing field(s): {item.title} ({', '.join(missing)})")
    deadline = bullet_field_value(item.body, "마감")
    validate_weekly_deadline_value(deadline, item.title)
    validate_weekly_item_links(item.body, item.title)


def validate_weekly_recommended_text(item: Item) -> None:
    forbidden_patterns = [
        r"마감\s*(?:지남|지난|종료)",
        r"시니어|senior|경력\s*(?:3|5)년|3년 이상|5년 이상",
        r"프론트엔드\s*중심|디자인\s*중심|마케팅\s*중심",
        r"원문 확인 필요|확인 필요|미정|알 수 없음",
    ]
    for pattern in forbidden_patterns:
        if re.search(pattern, item.body, flags=re.IGNORECASE):
            fail(f"Weekly career recommendation contains forbidden wording: {item.title}")


def validate_weekly_urgent_section(sections: list[Section]) -> None:
    section = find_section(sections, "마감 임박")
    if section is None:
        fail("Weekly career brief must include 마감 임박 section.")
    if WEEKLY_URGENT_EMPTY_STATE in section.body:
        return
    lines = [line.strip() for line in section.body.splitlines() if line.strip().startswith("- ")]
    if not lines:
        fail("마감 임박 section must include candidates or the required empty-state phrase.")
    for line in lines:
        match = re.search(r"\[D-(\d+)\]", line)
        if not match:
            fail("마감 임박 item must include D-n notation.")
        if int(match.group(1)) > 7:
            fail("마감 임박 section must only include items within D-7.")
        validate_weekly_item_links(line, "마감 임박")


def validate_weekly_portfolio_section(sections: list[Section]) -> None:
    section = find_section(sections, "포트폴리오로 남기기 좋은 대외활동")
    if section is None:
        fail("Weekly career brief must include 포트폴리오로 남기기 좋은 대외활동 section.")
    items = extract_items(section)
    if not items:
        if WEEKLY_PORTFOLIO_EMPTY_STATE in section.body:
            return
        fail("Portfolio section must include candidates or the required empty-state phrase.")
    for item in items:
        missing = missing_bullet_fields(item.body, WEEKLY_PORTFOLIO_FIELDS)
        if missing:
            fail(f"Portfolio activity is missing field(s): {item.title} ({', '.join(missing)})")
        validate_weekly_item_links(item.body, item.title)


def validate(content: str, report_type: str) -> None:
    if report_type == "daily-tech":
        validate_daily_tech(content)
    elif report_type == "weekly-career":
        validate_weekly_career(content)
    else:
        fail(f"Unsupported report type: {report_type}")


def main() -> int:
    args = parse_args()
    try:
        content = read_report(Path(args.path))
        validate(content, args.type)
    except (OSError, UnicodeDecodeError, RuntimeError) as exc:
        print(f"Career Feed brief validation failed: {exc}", file=sys.stderr)
        return 1

    print(f"Career Feed brief validation passed: {args.path} ({args.type})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
