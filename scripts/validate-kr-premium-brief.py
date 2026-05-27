#!/usr/bin/env python3
"""Validate KR Premium Markdown brief quality."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


DEFAULT_REPORT = "reports/briefs/kr-premium-daily.md"
MAX_WARNING_CHARS = 6500

LEGACY_SECTIONS = [
    "한국 AI 뉴스",
    "한국 백엔드/개발자 기술 뉴스",
    "한국 보안/취약점 알림",
    "국내 인턴십/해커톤/공모전/경진대회",
]
DAILY_SECTIONS = [
    "한국 AI 테크",
    "백엔드/개발자 기술",
    "오픈소스 기여 후보",
    "오늘 할 일",
]
WEEKLY_SECTIONS = [
    "이번 주 추천",
    "마감 임박",
    "포트폴리오 관점 추천",
]

NO_ITEM_PHRASES = [
    "오늘 확인된 주요 항목 없음",
    "오늘 확인된 주요 항목이 없습니다",
    "오늘 기준으로 포함할 만한 신뢰도 높은 후보를 찾지 못했습니다",
    "오늘은 긴급 체크 항목 없음",
    "오늘은 주니어가 바로 시도하기 좋은 오픈소스 후보가 없습니다.",
    "이번 주 마감 임박 항목 없음",
    "이번 주 추천 항목 없음",
]

GENERIC_PHRASES = [
    "개발 워크플로 또는 API 사용 방식 변화 확인이 필요합니다.",
    "실무 영향 여부를 원문에서 확인할 필요가 있습니다.",
    "패치 또는 영향 범위 확인이 필요합니다.",
]

LEGACY_ITEM_FIELDS = {
    "무슨 일": re.compile(r"^\s*-\s*무슨 일\s*:", re.MULTILINE),
    "왜 봐야 함": re.compile(r"^\s*-\s*왜 봐야 함\s*:", re.MULTILINE),
    "내 액션": re.compile(r"^\s*-\s*내 액션\s*:", re.MULTILINE),
    "출처": re.compile(r"^\s*-\s*.*출처.*:", re.MULTILINE),
    "시각": re.compile(r"^\s*-\s*.*(?:시각|게시|마감).*:", re.MULTILINE),
    "신뢰도": re.compile(r"^\s*-\s*.*신뢰도.*:", re.MULTILINE),
    "링크": re.compile(r"^\s*-\s*링크\s*:", re.MULTILINE),
}
LEGACY_CAREER_FIELDS = {
    "유형": re.compile(r"^\s*-\s*.*유형.*:", re.MULTILINE),
    "대상": re.compile(r"^\s*-\s*.*대상.*:", re.MULTILINE),
    "마감": re.compile(r"^\s*-\s*.*마감.*:", re.MULTILINE),
}
DAILY_REQUIRED_FIELDS = [
    re.compile(r"^\s*-\s*무슨 일\s*:", re.MULTILINE),
    re.compile(r"^\s*-\s*왜 나에게 중요한가\s*:", re.MULTILINE),
    re.compile(r"^\s*-\s*내 액션\s*:", re.MULTILINE),
    re.compile(r"^\s*-\s*.*출처.*:", re.MULTILINE),
    re.compile(r"^\s*-\s*링크\s*:", re.MULTILINE),
]
DAILY_RELEVANCE_FIELDS = [
    re.compile(r"^\s*-\s*백엔드 관점\s*:", re.MULTILINE),
    re.compile(r"^\s*-\s*Kotlin/Spring Boot 관련성\s*:", re.MULTILINE),
]
WEEKLY_REQUIRED_FIELDS = [
    "유형",
    "대상 적합성",
    "백엔드 적합성",
    "마감",
    "왜 나에게 맞는가",
    "내 액션",
    "링크",
]
DAILY_OSS_FIELDS = [
    "저장소",
    "왜 나에게 맞는가",
    "첫 30분 액션",
    "예상 난이도",
    "주의할 점",
    "링크",
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
    parser = argparse.ArgumentParser(description="Validate KR Premium Markdown brief.")
    parser.add_argument("path", nargs="?", default=DEFAULT_REPORT)
    parser.add_argument(
        "--type",
        choices=["legacy", "daily-tech", "weekly-career"],
        default="legacy",
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


def validate_common(content: str, min_links: int = 2) -> None:
    validate_timestamp(content)
    validate_secret_leaks(content)
    validate_links(content, min_links)
    validate_generic_phrases(content)
    validate_missing_source_link_phrases(content)
    validate_no_tables(content)
    if len(content) > MAX_WARNING_CHARS:
        warn(f"Markdown is long for Discord reading: {len(content)} chars")


def validate_secret_leaks(content: str) -> None:
    if SECRET_RE.search(content):
        fail("Secret, API key, or webhook-like value found in Markdown.")


def validate_links(content: str, min_links: int) -> None:
    links = LINK_RE.findall(content)
    if len(links) < min_links:
        fail(f"Expected at least {min_links} links, found {len(links)}.")
    duplicated = sorted({link for link in links if links.count(link) > 1})
    if duplicated:
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
        fail("Markdown tables are not allowed in KR Premium brief.")


def validate_item_markdown_link(item: Item) -> None:
    if not MARKDOWN_LINK_RE.search(item.body):
        fail(f"Item must include a Markdown link: {item.title}")


def validate_legacy(content: str) -> None:
    validate_common(content, min_links=2)
    sections = extract_sections(content)
    require_sections(sections, LEGACY_SECTIONS)
    for title in LEGACY_SECTIONS:
        section = find_section(sections, title)
        if section is None:
            continue
        items = extract_items(section)
        if not items:
            if section_has_no_item_phrase(section):
                continue
            fail(f"Section has no item and no empty-state phrase: {title}")
        for item in items:
            validate_legacy_item(title, item)


def validate_legacy_item(section_title: str, item: Item) -> None:
    bullet_lines = [line for line in item.body.splitlines() if line.strip().startswith("- ")]
    if len(bullet_lines) > 5:
        fail(f"Item has more than 5 bullet lines: {section_title} / {item.title}")

    fields = [name for name, pattern in LEGACY_ITEM_FIELDS.items() if pattern.search(item.body)]
    if len(fields) < 4:
        fail(
            f"Item has fewer than 4 required fields: "
            f"{section_title} / {item.title} ({', '.join(fields) or 'none'})"
        )

    if "국내 인턴십/해커톤/공모전/경진대회" in section_title:
        career_fields = [
            name for name, pattern in LEGACY_CAREER_FIELDS.items() if pattern.search(item.body)
        ]
        if len(career_fields) < 2:
            fail(f"Career event item must include at least 2 of 유형/대상/마감: {item.title}")

    validate_item_markdown_link(item)


def validate_daily_tech(content: str) -> None:
    if "Career Feed - Korea Tech Daily" not in content:
        fail("Missing daily tech title.")
    if re.search(r"^##\s+긴급 체크\s*$", content, re.MULTILINE):
        fail("Daily tech brief must not include 긴급 체크 section.")
    forbidden_structure_phrases = [
        "백엔드 개발자가 바로 확인해야 하는 보안/장애/패치",
        "오늘은 긴급 체크 항목 없음",
    ]
    found_forbidden = [phrase for phrase in forbidden_structure_phrases if phrase in content]
    if found_forbidden:
        fail(
            "Daily tech brief still contains security/emergency-check structure: "
            + ", ".join(found_forbidden)
        )

    sections = extract_sections(content)
    validate_common(content, min_links=2)
    require_sections(sections, DAILY_SECTIONS)

    if re.search(r"^##\s+.*(?:커리어|인턴|공모전|해커톤)", content, re.MULTILINE):
        fail("Daily tech brief must not include a long career event section.")

    if any(keyword in content for keyword in ["주가", "관련주", "투자의견"]):
        warn("Daily tech brief may contain stock/investment-only wording.")

    for title in ["한국 AI 테크", "백엔드/개발자 기술"]:
        section = find_section(sections, title)
        if section is None:
            continue
        items = extract_items(section)
        if not items and not section_has_no_item_phrase(section):
            fail(f"Section has no item and no empty-state phrase: {title}")
        for item in items:
            validate_daily_item(title, item)

    validate_daily_oss_section(sections)


def validate_daily_item(section_title: str, item: Item) -> None:
    missing = [
        pattern.pattern
        for pattern in DAILY_REQUIRED_FIELDS
        if not pattern.search(item.body)
    ]
    if missing:
        fail(f"Daily item is missing required field(s): {section_title} / {item.title}")
    if not any(pattern.search(item.body) for pattern in DAILY_RELEVANCE_FIELDS):
        fail(
            "Daily item must include either 백엔드 관점 or Kotlin/Spring Boot 관련성: "
            f"{section_title} / {item.title}"
        )
    validate_item_markdown_link(item)


def validate_daily_oss_section(sections: list[Section]) -> None:
    section = find_section(sections, "오픈소스 기여 후보")
    if section is None:
        fail("Daily tech brief must include 오픈소스 기여 후보 section.")

    no_item_phrase = "오늘은 주니어가 바로 시도하기 좋은 오픈소스 후보가 없습니다."
    has_issue_link = bool(
        re.search(r"\[Issue 보기\]\(https://github\.com/[^)]+/issues/\d+\)", section.body)
        or re.search(r"https://github\.com/[^\s)]+/issues/\d+", section.body)
    )
    if no_item_phrase not in section.body and not has_issue_link:
        fail("OSS section must include an Issue 보기 link or the required empty-state phrase.")

    items = extract_items(section)
    if len(items) > 1:
        fail("OSS section must include at most one candidate.")
    if not items:
        if no_item_phrase in section.body:
            return
        fail("OSS section has no candidate and no required empty-state phrase.")

    item = items[0]
    present_fields = [
        field
        for field in DAILY_OSS_FIELDS
        if re.search(rf"^\s*-\s*{re.escape(field)}\s*:", item.body, re.MULTILINE)
    ]
    if len(present_fields) < 4:
        fail(
            "OSS candidate must include at least 4 required fields: "
            f"{item.title} ({', '.join(present_fields) or 'none'})"
        )
    validate_item_markdown_link(item)


def validate_weekly_career(content: str) -> None:
    if "Career Feed - Backend Career Weekly" not in content:
        fail("Missing weekly career title.")
    sections = extract_sections(content)
    validate_common(content, min_links=2)
    require_sections(sections, WEEKLY_SECTIONS)

    top_section = find_section(sections, "이번 주 추천")
    if top_section is None:
        return
    top_items = extract_items(top_section)
    if not top_items and not section_has_no_item_phrase(top_section):
        fail("Weekly career recommendations are missing.")
    for item in top_items:
        validate_weekly_item(item)
        validate_weekly_recommended_text(item)


def validate_weekly_item(item: Item) -> None:
    missing = [
        field
        for field in WEEKLY_REQUIRED_FIELDS
        if not re.search(rf"^\s*-\s*{re.escape(field)}\s*:", item.body, re.MULTILINE)
    ]
    if missing:
        fail(f"Weekly career item is missing field(s): {item.title} ({', '.join(missing)})")
    validate_item_markdown_link(item)


def validate_weekly_recommended_text(item: Item) -> None:
    forbidden_patterns = [
        r"마감\s*(?:지남|지난|종료)",
        r"시니어|senior|경력\s*(?:3|5)년|3년 이상|5년 이상",
        r"프론트엔드\s*중심|디자인\s*중심|마케팅\s*중심",
        r"대상 적합성\s*:\s*(?:없음|불명확)",
    ]
    for pattern in forbidden_patterns:
        if re.search(pattern, item.body, flags=re.IGNORECASE):
            fail(f"Weekly career recommendation contains forbidden wording: {item.title}")


def validate(content: str, report_type: str) -> None:
    if report_type == "legacy":
        validate_legacy(content)
    elif report_type == "daily-tech":
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
        print(f"KR Premium brief validation failed: {exc}", file=sys.stderr)
        return 1

    print(f"KR Premium brief validation passed: {args.path} ({args.type})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
