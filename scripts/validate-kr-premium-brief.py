#!/usr/bin/env python3
"""Validate KR_PREMIUM_MODE Markdown brief quality."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


DEFAULT_REPORT = "reports/briefs/kr-premium-daily.md"
MIN_LINK_COUNT = 4
MIN_ITEM_FIELD_COUNT = 4
MAX_ITEM_BULLET_LINES = 5

SECTION_TITLES = [
    "한국 AI 뉴스",
    "한국 백엔드/개발자 기술 뉴스",
    "한국 보안/취약점 알림",
    "국내 인턴십/해커톤/공모전/경진대회",
]

NO_ITEM_PHRASES = [
    "오늘 확인된 주요 항목 없음",
    "오늘 확인된 주요 항목이 없습니다",
    "오늘 기준으로 포함할 만한 신뢰도 높은 후보를 찾지 못했습니다",
]

GENERIC_PHRASES = [
    "개발 워크플로 또는 API 사용 방식 변화 확인이 필요합니다.",
    "실무 영향 여부를 원문에서 확인할 필요가 있습니다.",
    "패치 또는 영향 범위 확인이 필요합니다.",
]

ITEM_FIELDS = {
    "무슨 일": re.compile(r"^\s*-\s*무슨 일\s*:", re.MULTILINE),
    "왜 봐야 함": re.compile(r"^\s*-\s*왜 봐야 함\s*:", re.MULTILINE),
    "내 액션": re.compile(r"^\s*-\s*내 액션\s*:", re.MULTILINE),
    "출처": re.compile(r"^\s*-\s*.*출처.*:", re.MULTILINE),
    "시각": re.compile(r"^\s*-\s*.*(?:시각|게시|마감).*:", re.MULTILINE),
    "신뢰도": re.compile(r"^\s*-\s*.*신뢰도.*:", re.MULTILINE),
    "링크": re.compile(r"^\s*-\s*링크\s*:", re.MULTILINE),
}

CAREER_FIELDS = {
    "유형": re.compile(r"^\s*-\s*.*유형.*:", re.MULTILINE),
    "대상": re.compile(r"^\s*-\s*.*대상.*:", re.MULTILINE),
    "마감": re.compile(r"^\s*-\s*.*마감.*:", re.MULTILINE),
}

LINK_RE = re.compile(r"https?://[^\s)>\\\]]+")
SECTION_HEADING_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
ITEM_HEADING_RE = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)


@dataclass(frozen=True)
class Section:
    title: str
    body: str


@dataclass(frozen=True)
class Item:
    title: str
    body: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate KR premium Markdown brief.")
    parser.add_argument("path", nargs="?", default=DEFAULT_REPORT)
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


def extract_sections(content: str) -> dict[str, Section]:
    matches = list(SECTION_HEADING_RE.finditer(content))
    sections: dict[str, Section] = {}
    for index, match in enumerate(matches):
        heading = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        for title in SECTION_TITLES:
            if title in heading:
                sections[title] = Section(title=title, body=content[start:end].strip())
    return sections


def validate_required_sections(sections: dict[str, Section]) -> None:
    missing = [title for title in SECTION_TITLES if title not in sections]
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


def validate_section_items(sections: dict[str, Section]) -> None:
    for title, section in sections.items():
        items = extract_items(section)
        if not items:
            if section_has_no_item_phrase(section):
                continue
            fail(f"Section has no item and no empty-state phrase: {title}")

        for item in items:
            validate_item_fields(title, item)


def present_item_fields(item: Item) -> list[str]:
    return [name for name, pattern in ITEM_FIELDS.items() if pattern.search(item.body)]


def validate_item_fields(section_title: str, item: Item) -> None:
    bullet_lines = [
        line for line in item.body.splitlines() if line.strip().startswith("- ")
    ]
    if len(bullet_lines) > MAX_ITEM_BULLET_LINES:
        fail(
            f"Item has more than {MAX_ITEM_BULLET_LINES} bullet lines: "
            f"{section_title} / {item.title} ({len(bullet_lines)})"
        )

    fields = present_item_fields(item)
    if len(fields) < MIN_ITEM_FIELD_COUNT:
        fail(
            f"Item has fewer than {MIN_ITEM_FIELD_COUNT} required fields: "
            f"{section_title} / {item.title} ({', '.join(fields) or 'none'})"
        )

    if "국내 인턴십/해커톤/공모전/경진대회" in section_title:
        career_fields = [
            name for name, pattern in CAREER_FIELDS.items() if pattern.search(item.body)
        ]
        if len(career_fields) < 2:
            fail(
                "Career event item must include at least 2 of 유형/대상/마감: "
                f"{item.title} ({', '.join(career_fields) or 'none'})"
            )

    validate_item_link_line(item)


def validate_item_link_line(item: Item) -> None:
    link_lines = [
        line.strip()
        for line in item.body.splitlines()
        if line.strip().startswith("- 링크:")
    ]
    if not link_lines:
        return
    for line in link_lines:
        if not re.search(r"\[[^\]]+\]\(https?://[^)]+\)", line):
            fail(f"Link line must use Markdown link text: {item.title}")


def validate_links(content: str) -> None:
    links = LINK_RE.findall(content)
    if len(links) < MIN_LINK_COUNT:
        fail(f"Expected at least {MIN_LINK_COUNT} links, found {len(links)}.")
    duplicated = sorted({link for link in links if links.count(link) > 1})
    if duplicated:
        fail(f"Duplicate links found: {', '.join(duplicated[:3])}")


def validate_generic_phrases(content: str) -> None:
    total = 0
    repeated = []
    for phrase in GENERIC_PHRASES:
        count = content.count(phrase)
        total += count
        if count >= 2:
            repeated.append(f"{phrase} ({count})")

    if repeated:
        fail(f"Generic phrase repeated 2 or more times: {', '.join(repeated)}")
    if total >= 2:
        fail(f"Generic placeholder phrases appear too often: {total} occurrence(s).")


def validate_missing_source_link_phrases(content: str) -> None:
    if "링크 없음" in content or re.search(r"링크\s*:\s*없음", content):
        fail("Found item with missing link text.")
    if "출처 없음" in content or re.search(r"출처(?:/시각)?\s*:\s*없음", content):
        warn("Found item with missing source text.")


def validate_no_tables(content: str) -> None:
    if any(line.strip().startswith("|") for line in content.splitlines()):
        fail("Markdown tables are not allowed in KR premium brief.")


def validate(content: str) -> None:
    validate_timestamp(content)
    sections = extract_sections(content)
    validate_required_sections(sections)
    validate_section_items(sections)
    validate_links(content)
    validate_generic_phrases(content)
    validate_missing_source_link_phrases(content)
    validate_no_tables(content)


def main() -> int:
    args = parse_args()
    try:
        content = read_report(Path(args.path))
        validate(content)
    except (OSError, UnicodeDecodeError, RuntimeError) as exc:
        print(f"KR premium brief validation failed: {exc}", file=sys.stderr)
        return 1

    print(f"KR premium brief validation passed: {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
