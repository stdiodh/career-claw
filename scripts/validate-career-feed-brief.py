#!/usr/bin/env python3
"""Validate Career Feed Markdown brief quality."""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import urllib.parse
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


DEFAULT_REPORT = "reports/briefs/kr-tech-daily.md"
MAX_WARNING_CHARS = 6500
DAILY_CS_TERM_SECTION_MAX_CHARS = 1500
OSS_CANDIDATE_FILENAME = "kr-oss-contribution-opportunities.json"


def joined(*parts: str) -> str:
    return "".join(parts)

DAILY_SECTIONS = [
    "오늘의 Spring Boot/JVM 학습",
    "이번 주 PS 성장 루틴",
    "오픈소스 기여 후보",
    "주니어 백엔드 실무지식",
    "오늘의 CS Core & 백엔드 용어",
]
NEWS_DAILY_DEFAULT_MIN = 3
NEWS_DAILY_SECTIONS_MAX = 5
NEWS_DAILY_SPARSE_MAX = NEWS_DAILY_DEFAULT_MIN - 1
WEEKLY_SECTIONS = [
    "공식 채용 사이트",
    "채용·인턴 플랫폼",
    "해커톤·공모전·경진대회 플랫폼",
    "30분 확인 루틴",
]
WEEKLY_SITE_SECTION_MIN_COUNTS = {
    "공식 채용 사이트": 7,
    "채용·인턴 플랫폼": 6,
    "해커톤·공모전·경진대회 플랫폼": 5,
}
WEEKLY_JOB_REQUIRED_SITE_NAMES = [
    "NAVER",
    "Kakao",
    "LINE",
    "Coupang",
    "우아한형제들",
    "Toss",
    "당근",
]
WEEKLY_INTERN_REQUIRED_SITE_NAMES = [
    "Linkareer",
    "Work24",
    "ZeroBase",
    "Saramin",
    "JobKorea",
    "Wanted",
    "Jumpit",
]
WEEKLY_COMPETITION_REQUIRED_SITE_NAMES = [
    "DACON",
    "AI Factory",
    "Programmers",
    "Wevity",
    "All-Con",
]
WEEKLY_CATEGORY_EMPTY_STATES = {
    "채용": "이번 주 기준을 만족하는 채용 후보가 없습니다.",
    "인턴": "이번 주 기준을 만족하는 인턴 후보가 없습니다.",
    "해커톤": "이번 주 기준을 만족하는 해커톤 후보가 없습니다.",
    "공모전": "이번 주 기준을 만족하는 공모전 후보가 없습니다.",
    "경진대회": "이번 주 기준을 만족하는 경진대회 후보가 없습니다.",
}

NO_ITEM_PHRASES = [
    "오늘 확인된 주요 항목 없음",
    "오늘 확인된 주요 항목이 없습니다",
    "오늘 기준으로 포함할 만한 신뢰도 높은 후보를 찾지 못했습니다",
    "오늘은 긴급 체크 항목 없음",
    "오늘은 바로 추천할 안전한 issue는 없습니다.",
    "오늘은 기준을 만족하는 한국 최신 개발/AI 뉴스가 없습니다.",
    "오늘은 기준을 만족하는 한국 개발/AI 뉴스가 없습니다.",
    "이번 주 마감 임박 항목 없음",
    "이번 주 추천 항목 없음",
    "이번 주 기준을 만족하는 백엔드 커리어 기회가 없습니다.",
    "이번 주 기준을 만족하는 채용 후보가 없습니다.",
    "이번 주 기준을 만족하는 인턴 후보가 없습니다.",
    "이번 주 기준을 만족하는 해커톤 후보가 없습니다.",
    "이번 주 기준을 만족하는 공모전 후보가 없습니다.",
    "이번 주 기준을 만족하는 경진대회 후보가 없습니다.",
    "이번 주 마감 임박 항목은 없습니다.",
    "이번 주 포트폴리오용 대외활동 후보는 없습니다.",
    "다음 주로 넘겨 추적할 후보는 없습니다.",
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
    "왜 지금 볼 만한가",
    "핵심 개념",
    "30분 실습",
    "완료 기준",
    "확장해서 볼 것",
    "레퍼런스",
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
NEWS_DAILY_FIELDS = [
    "분류",
    "출처/게시",
    "핵심",
    "백엔드 주니어 관점",
    "더 볼 키워드",
    "링크",
]
NEWS_DAILY_TECH_FIELDS_REQUIRED = [
    "분류",
    "출처/게시",
    "핵심",
    "더 볼 키워드",
    "링크",
]
NEWS_DAILY_INVESTMENT_FIELDS = [
    "분류",
    "출처/게시",
    "핵심",
    "투자 관찰 포인트",
    "기술과 연결",
    "리스크",
    "확인할 지표",
    "링크",
]
NEWS_DAILY_GROWTH_FIELDS = [
    "도움 점수",
    "왜 도움 되는가",
    "오늘 할 일 1개",
]
DAILY_PRACTICAL_FIELDS = [
    "실무 상황",
    "핵심 개념",
    "실패하면 생기는 문제",
    "30분 실습",
    "현업 체크 질문",
    "레퍼런스",
    "검색 키워드",
]
DAILY_CS_CORE_FIELDS = [
    "트랙",
    "왜 백엔드에 중요한가",
    "핵심 개념",
    "10~20분 확인",
    "완료 기준",
    "면접 연결 질문",
    "레퍼런스",
]
DAILY_BACKEND_TERM_FIELDS = [
    "한 줄 정의",
    "실무 상황",
    "오해하면 생기는 문제",
    "Spring/API 연결",
    "확인 질문",
    "레퍼런스",
]
DAILY_NEWS_EMPTY_STATE = "오늘은 기준을 만족하는 한국 최신 개발/AI 뉴스가 없습니다."
NEWS_DAILY_EMPTY_STATES = [
    "오늘은 기준을 만족하는 한국 개발/AI 뉴스가 없습니다.",
    "오늘은 기준을 만족하는 한국 최신 개발/AI 뉴스가 없습니다.",
]
DAILY_OSS_EMPTY_STATE = "오늘은 바로 추천할 안전한 issue는 없습니다."
DAILY_OSS_PREP_FIELDS = [
    "저장소",
    "30분 액션",
    "확인할 문서",
    "다음에 issue를 찾을 때 쓸 GitHub 검색식",
    "기여 전 매너",
]
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
NEWS_DAILY_INVESTMENT_ADVICE_PATTERNS = [
    r"매수",
    r"매도",
    r"목표가",
    r"투자\s*의견",
    r"투자의견",
    r"매수하세요",
    r"매도하세요",
    r"지금\s*사야",
    r"지금\s*팔아야",
    r"매수\s*(?:추천|의견)",
    r"매도\s*(?:추천|의견)",
    r"추천주",
    r"관련주",
    r"테마주",
    r"급등주",
    r"수익\s*보장",
    r"무조건",
    r"목표가까지\s*간다",
]
NEWS_DAILY_MARKET_PRICE_PATTERNS = [
    r"주가",
    r"급등",
    r"급락",
    r"상한가",
    r"하한가",
]
NEWS_DAILY_PRICE_CONTEXT_PATTERNS = [
    r"실적",
    r"영업이익",
    r"매출",
    r"\bCAPEX\b",
    r"데이터\s*센터",
    r"데이터센터",
    r"\bGPU\b",
    r"\bHBM\b",
    r"클라우드",
    r"AI\s*제품",
    r"기업용\s*AI",
    r"\bAPI\b",
    r"수요",
    r"공시",
    r"컨퍼런스콜",
]
NEWS_DAILY_TECH_CONTEXT_PATTERNS = [
    r"\bAPI\b",
    r"\bSDK\b",
    r"클라우드",
    r"데이터\s*센터",
    r"데이터센터",
    r"인프라",
    r"\bGPU\b",
    r"\bHBM\b",
    r"반도체",
    r"서버",
    r"개발자",
    r"플랫폼",
    r"백엔드",
    r"보안",
    r"오픈소스",
    r"AI\s*서비스",
    r"기업용\s*AI",
    r"실적",
    r"\bCAPEX\b",
    r"가이던스",
    r"수요",
    r"매출",
    r"공시",
    r"컨퍼런스콜",
]
NEWS_DAILY_OBJECTIVE_METRIC_PATTERNS = [
    r"매출",
    r"영업이익",
    r"\bCAPEX\b",
    r"가이던스",
    r"데이터\s*센터\s*투자",
    r"데이터센터\s*투자",
    r"\bGPU\b\s*수요",
    r"\bHBM\b\s*매출\s*비중",
    r"클라우드\s*영업이익률",
    r"\bAPI\b\s*사용량",
    r"기업용\s*AI\s*매출",
    r"고객\s*수",
    r"서버\s*출하량",
]
NEWS_DAILY_GROWTH_ACTION_PATTERNS = [
    r"공식\s*문서\s*(?:보기|확인|정리)",
    r"작은\s*코드\s*실험",
    r"아키텍처\s*메모",
    r"기업\s*실적",
    r"지표\s*확인",
    r"포트폴리오",
    r"면접\s*질문",
    r"GitHub\s*issue",
    r"\bTIL\b",
]
NEWS_DAILY_VAGUE_ACTION_PATTERNS = [
    r"관련\s*내용을\s*읽어본다",
    r"관심을\s*가져본다",
    r"공부해본다",
    r"살펴본다",
]
NEWS_DAILY_OFFICIAL_TECH_BLOG_DOMAINS = {
    "d2.naver.com",
    "tech.kakao.com",
    "techblog.woowahan.com",
    "toss.tech",
    "engineering.linecorp.com",
    "developers.naver.com",
}
WEEKLY_REQUIRED_FIELDS = [
    "확인 유형",
    "바로가기",
    "검색 키워드",
    "제외 키워드",
    "확인 기준",
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
WEEKLY_FORBIDDEN_TEXT_PATTERNS = [
    r"후보\s*:",
    r"이번 주 기준을 만족하는",
    r"마감\s*:",
    r"회사/주최\s*:",
    r"직무/역할\s*:",
    r"지원/참가 조건\s*:",
    r"확인 상태\s*:",
    r"Naver News Search",
    r"출처\s*:\s*NAVER\b",
    r"출처\s*:\s*Naver\b",
    r"출처\s*:\s*Naver News Search\b",
    r"원문 확인 필요",
    r"확인 필요",
    r"미정",
    r"알 수 없음",
    r"뉴스브리핑",
    r"수상",
    r"2등 수상",
    r"개최했다",
    r"개최 완료",
    r"성료",
    r"결과 발표",
]
WEEKLY_TOP_EMPTY_STATE = "이번 주 기준을 만족하는 백엔드 커리어 기회가 없습니다."
WEEKLY_URGENT_EMPTY_STATE = "이번 주 마감 임박 항목은 없습니다."
WEEKLY_TRACKING_EMPTY_STATE = "다음 주로 넘겨 추적할 후보는 없습니다."
WEEKLY_PORTFOLIO_FIELDS = [
    "유형",
    "만들 수 있는 백엔드 산출물",
    "기술/산출물 키워드",
    "이번 주 액션",
    "링크",
]
WEEKLY_GENERIC_URLS = {
    "https://www.wanted.co.kr",
    "https://www.wanted.co.kr/",
    "https://dacon.io/competitions",
    "https://linkareer.com",
    "https://linkareer.com/",
    "https://linkareer.com/list/intern",
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
WEEKLY_BLOCKED_DOMAINS = {
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
    "newswire.co.kr",
    "prnewswire.com",
    "prtimes.jp",
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
DAILY_OSS_STATUS_REQUIRED_GROUPS = {
    "assignee absence": [
        r"담당자\s*없음",
        r"assignee\s*(?:없음|none|0)",
        r"(?:담당자|assignee|배정).{0,30}없(?:음|다|고|는|습니다)?",
        r"배정\s*없음",
        r"미배정",
    ],
    "linked work absence": [
        r"(?:연결|linked).*(?:PR|branch|브랜치).*(?:없음|none|0)",
        r"(?:연결|linked).{0,40}(?:PR|branch|브랜치).{0,40}없(?:음|다|고|는|습니다)?",
    ],
    "claim absence": [
        r"(?:claim|작업\s*의사|working|맡겠).*(?:없음|none|0)",
        r"댓글.*(?:claim|작업\s*의사).*(?:없음|none|0)",
        r"(?:claim|작업\s*의사|working|맡겠).{0,40}없(?:음|다|고|는|습니다)?",
        r"댓글.{0,40}(?:claim|작업\s*의사).{0,40}없(?:음|다|고|는|습니다)?",
        r"(?:claim|작업\s*의사|working|맡겠).{0,40}(?:확인|발견)되지",
    ],
}
OSS_CONTRIBUTION_TYPE_ALIASES = {
    "docs": ["docs", "문서"],
    "test": ["test", "테스트"],
    "bug-repro": ["bug-repro", "bug repro", "재현"],
    "sample": ["sample", "샘플", "예제"],
}
SPRING_ALLOWED_URL_PREFIXES = [
    "spring.io",
    "docs.spring.io",
    "github.com/spring-projects/",
    "grpc.io",
    "openjdk.org",
    "inside.java",
    "blogs.oracle.com",
    "opentelemetry.io",
    "micrometer.io",
    "kotlinlang.org",
    "docs.gradle.org",
    "testcontainers.com",
    "docs.docker.com",
    "kubernetes.io",
]
PRACTICAL_ALLOWED_URL_PREFIXES = [
    "datatracker.ietf.org",
    "developer.mozilla.org",
    "cheatsheetseries.owasp.org",
    "owasp.org",
    "docs.spring.io",
    "docs.oracle.com",
    "postgresql.org",
    "dev.mysql.com",
    "redis.io",
    "kafka.apache.org",
    "docs.docker.com",
    "kubernetes.io",
    "opentelemetry.io",
    "micrometer.io",
    "testcontainers.com",
    "toss.tech",
    "techblog.woowahan.com",
    "tech.kakao.com",
    "d2.naver.com",
    "engineering.linecorp.com",
]
DAILY_LEARNING_BLOCKED_DOMAINS = [
    "n.news.naver.com",
    "news.naver.com",
    "m.search.naver.com",
    "search.naver.com",
    "m.blog.naver.com",
    "blog.naver.com",
    "etnews.com",
    "zdnet.co.kr",
    "ddaily.co.kr",
    "bloter.net",
    "aitimes.com",
    "itworld.co.kr",
    "ciokorea.com",
    "hankyung.com",
    "chosun.com",
    "joongang.co.kr",
    "donga.com",
    "yna.co.kr",
    "newsis.com",
]

LINK_RE = re.compile(r"https?://[^\s)>\\\]]+")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(https?://[^)]+\)")
SITE_LINK_RE = re.compile(r"\[사이트 보기\]\((https?://[^)]+)\)")
GITHUB_ISSUE_URL_RE = re.compile(
    r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/issues/\d+"
)
SECTION_HEADING_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
ITEM_HEADING_RE = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)
WEEKLY_CATEGORY_HEADING_RE = re.compile(r"^###\s+\d+\.\s+(.+?)\s*$", re.MULTILINE)
WEEKLY_CANDIDATE_HEADING_RE = re.compile(r"^####\s+후보\s*:\s*(.+?)\s*$", re.MULTILINE)
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
        choices=["daily-tech", "daily-news", "weekly-career"],
        default="daily-tech",
        help="Brief type to validate.",
    )
    parser.add_argument(
        "--candidates-dir",
        default="reports/candidates",
        help="Directory containing candidate JSON files for cross-checks.",
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


def read_oss_candidate_payload(candidates_dir: Path) -> dict[str, object]:
    path = candidates_dir / OSS_CANDIDATE_FILENAME
    if not path.exists():
        fail(f"Daily tech validation requires OSS candidate JSON: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"OSS candidate JSON is invalid: {path} ({exc})")
    if not isinstance(payload, dict):
        fail(f"OSS candidate JSON must be an object: {path}")
    return payload


def safe_oss_candidates_by_url(payload: dict[str, object]) -> dict[str, dict[str, object]]:
    raw_items = payload.get("items", [])
    if not isinstance(raw_items, list):
        fail("OSS candidate JSON items must be a list.")

    candidates: dict[str, dict[str, object]] = {}
    for raw_item in raw_items:
        if not isinstance(raw_item, dict):
            continue
        if raw_item.get("safe_to_recommend") is not True:
            continue
        url = str(raw_item.get("url") or raw_item.get("source_url") or "").strip()
        if not GITHUB_ISSUE_URL_RE.fullmatch(url):
            fail("safe_to_recommend OSS candidate must include a GitHub issue URL.")
        candidates[normalize_github_issue_url(url)] = raw_item
    return candidates


def candidate_text_value(candidate: dict[str, object], *keys: str) -> str:
    for key in keys:
        value = candidate.get(key)
        if value is not None:
            text = str(value).strip()
            if text:
                return text
    return ""


def text_contains_expected_or_alias(text: str, expected: str, aliases: dict[str, list[str]]) -> bool:
    lowered_text = text.lower()
    lowered_expected = expected.lower()
    values = aliases.get(lowered_expected, [expected])
    return any(value.lower() in lowered_text for value in values)


def normalize_token_value(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def bullet_field_value(text: str, field: str) -> str:
    match = re.search(
        rf"^\s*-\s*{re.escape(field)}\s*:\s*(.+?)\s*$",
        text,
        flags=re.MULTILINE,
    )
    return match.group(1).strip() if match else ""


def markdown_link_urls(text: str) -> list[str]:
    return re.findall(r"\[[^\]]+\]\((https?://[^)]+)\)", text)


def github_issue_urls(text: str) -> list[str]:
    return GITHUB_ISSUE_URL_RE.findall(text)


def normalize_github_issue_url(url: str) -> str:
    parsed = urllib.parse.urlsplit(url.strip().rstrip("/"))
    return f"https://{parsed.netloc.lower()}{parsed.path.rstrip('/')}"


def normalize_validation_url(url: str) -> str:
    return url.strip().rstrip("/")


def validation_domain(url: str) -> str:
    domain = urllib.parse.urlsplit(url).netloc.lower()
    return domain[4:] if domain.startswith("www.") else domain


def validation_url_key(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    domain = validation_domain(url)
    path = parsed.path.lstrip("/")
    return f"{domain}/{path}" if path else domain


def normalize_validation_title(title: str) -> str:
    cleaned = re.sub(r"\[[^\]]+\]|\([^)]*\)", " ", title)
    cleaned = re.sub(
        r"\s*[-–—|:]\s*(전자신문|ZDNet Korea|지디넷코리아|블로터|"
        r"AI타임스|디지털데일리|ITWorld|CIO Korea)\s*$",
        " ",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"[^\w가-힣]+", " ", cleaned, flags=re.UNICODE)
    return re.sub(r"\s+", " ", cleaned.strip()).lower()


def news_daily_has_sparse_phrase(content: str, item_count: int) -> bool:
    count_pattern = re.escape(str(item_count))
    patterns = [
        rf"기준을\s*만족하는\s*뉴스가\s*{count_pattern}\s*개",
        rf"기준\s*만족\s*뉴스\s*수\s*[:：]?\s*{count_pattern}\s*개",
        r"기준을\s*만족하는\s*뉴스가\s*3\s*개\s*미만",
        r"후보가\s*3\s*개\s*미만",
        r"기준을\s*만족하는\s*후보가\s*3\s*개\s*미만",
    ]
    return any(re.search(pattern, content) for pattern in patterns)


def news_daily_has_empty_phrase(content: str) -> bool:
    if any(phrase in content for phrase in NEWS_DAILY_EMPTY_STATES):
        return True
    return bool(re.search(r"기준을\s*만족하는.*(?:한국\s*)?(?:개발/AI|개발\s*/\s*AI).*뉴스.*없", content))


def keyword_count(value: str) -> int:
    comma_parts = [
        part.strip()
        for part in re.split(r"[,;/|·]+", value)
        if part.strip()
    ]
    if len(comma_parts) >= 2:
        return len(set(comma_parts))
    tokens = re.findall(r"[A-Za-z0-9가-힣+#.]+", value)
    return len(set(tokens))


def matches_any_pattern(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def news_daily_has_tech_context(text: str) -> bool:
    return matches_any_pattern(text, NEWS_DAILY_TECH_CONTEXT_PATTERNS)


def is_official_tech_blog_domain(domain: str) -> bool:
    return any(
        domain == official or domain.endswith(f".{official}")
        for official in NEWS_DAILY_OFFICIAL_TECH_BLOG_DOMAINS
    )


def is_allowed_url_prefix(url: str, allowed_prefixes: list[str]) -> bool:
    key = validation_url_key(url).lower()
    domain = validation_domain(url)
    for prefix in allowed_prefixes:
        normalized = prefix.lower().strip().rstrip("/")
        if "/" in normalized:
            if key == normalized or key.startswith(f"{normalized}/"):
                return True
            continue
        if domain == normalized or domain.endswith(f".{normalized}"):
            return True
    return False


def blocked_learning_domain(url: str) -> str:
    domain = validation_domain(url)
    for blocked in DAILY_LEARNING_BLOCKED_DOMAINS:
        if domain == blocked or domain.endswith(f".{blocked}"):
            return blocked
    return ""


def validate_learning_reference_domains(
    text: str,
    allowed_prefixes: list[str],
    context: str,
) -> None:
    urls = markdown_link_urls(text)
    if not urls:
        fail(f"Section must include a Markdown link: {context}")

    blocked = [(url, blocked_learning_domain(url)) for url in urls]
    blocked = [(url, domain) for url, domain in blocked if domain]
    if blocked:
        fail(f"{context} uses blocked portal/news domain: {blocked[0][0]}")

    invalid = [
        url
        for url in urls
        if not is_allowed_url_prefix(url, allowed_prefixes)
    ]
    if invalid:
        fail(f"{context} uses unsupported reference domain: {invalid[0]}")


def is_generic_weekly_url(url: str) -> bool:
    normalized = normalize_validation_url(url)
    generic = {normalize_validation_url(item) for item in WEEKLY_GENERIC_URLS}
    return normalized in generic


def is_blocked_weekly_domain(url: str) -> bool:
    domain = validation_domain(url)
    return any(domain == blocked or domain.endswith(f".{blocked}") for blocked in WEEKLY_BLOCKED_DOMAINS)


def is_allowed_weekly_detail_url(url: str) -> bool:
    parsed = urllib.parse.urlsplit(url)
    domain = validation_domain(url)
    path = parsed.path.rstrip("/") or "/"
    query = parsed.query.lower()
    if domain == "linkareer.com" and re.fullmatch(r"/activity/\d+", path):
        return True
    if domain == "dacon.io" and path.startswith("/competitions/official/"):
        return True
    if domain == "aifactory.space" and path.startswith("/competition/detail/"):
        return True
    if domain == "wanted.co.kr" and path.startswith("/wd/"):
        return True
    if domain == "jumpit.co.kr" and path.startswith("/position/"):
        return True
    if domain == "saramin.co.kr" and path.startswith("/zf_user/jobs/"):
        return True
    if domain == "jobkorea.co.kr" and path.startswith("/Recruit/GI_Read"):
        return True
    if domain in {"programmers.co.kr", "school.programmers.co.kr"} and (
        path.startswith("/competitions/") or path.startswith("/pages/")
    ):
        return True
    if domain == "wevity.com" and "c=find" in query:
        return True
    if domain == "all-con.co.kr" and path.startswith("/view/contest/"):
        return True
    if domain == "recruit.navercorp.com" and "/rcrt/view.do" in path:
        return True
    if domain == "careers.kakao.com" and (path.startswith("/jobs/") or "jobid=" in query):
        return True
    if domain == "careers.linecorp.com" and re.fullmatch(r"/(?:ko|en)/jobs/\d+", path):
        return True
    if domain == "coupang.jobs" and re.fullmatch(r"/(?:en/|ko/)?jobs/\d+", path):
        return True
    if domain == "career.woowahan.com" and path.startswith("/jobs/"):
        return True
    if domain == "toss.im" and (path.startswith("/career/job-detail") or "job_id=" in query):
        return True
    if domain in {"about.daangn.com", "team.daangn.com"} and re.search(r"/jobs/\d+", path):
        return True
    return False


def validate_weekly_deadline_value(value: str, context: str) -> None:
    if any(forbidden in value for forbidden in WEEKLY_FORBIDDEN_DEADLINE_VALUES):
        fail(f"Weekly career deadline is not actionable: {context}")
    if value in {"상시채용", "채용 시 마감"}:
        return
    if re.fullmatch(r"20\d{2}-\d{2}-\d{2}(?: \d{2}:\d{2})? KST(?: \(D-\d+\))?", value):
        return
    fail(f"Weekly career deadline has invalid format: {context} ({value})")


def validate_weekly_item_links(text: str, context: str) -> None:
    urls = markdown_link_urls(text)
    if not urls:
        fail(f"Item must include a Markdown link: {context}")
    generic_urls = [url for url in urls if is_generic_weekly_url(url)]
    if generic_urls:
        fail(f"Weekly career item uses generic URL: {context} ({generic_urls[0]})")
    blocked_urls = [url for url in urls if is_blocked_weekly_domain(url)]
    if blocked_urls:
        fail(f"Weekly career item uses news URL: {context} ({blocked_urls[0]})")
    invalid_urls = [url for url in urls if not is_allowed_weekly_detail_url(url)]
    if invalid_urls:
        fail(f"Weekly career item uses unsupported detail URL: {context} ({invalid_urls[0]})")


def validate_weekly_naver_host_policy(text: str, context: str) -> None:
    for field in ("회사/주최", "주최"):
        value = bullet_field_value(text, field)
        if value != "NAVER":
            continue
        urls = markdown_link_urls(text)
        if not urls or not any(
            validation_domain(url) == "recruit.navercorp.com" for url in urls
        ):
            fail(f"Weekly career item uses NAVER as host without official NAVER career URL: {context}")


def validate_daily_tech(content: str, candidates_dir: Path) -> None:
    if (
        "Career Feed - Backend Daily" not in content
        and "Career Feed - Korea Tech Daily" not in content
    ):
        fail("Missing daily tech title.")
    validate_daily_forbidden_text(content)
    sections = extract_sections(content)
    validate_common(content, min_links=2, allow_duplicate_links=True)
    require_sections(sections, DAILY_SECTIONS)
    validate_daily_section_duplicate_links(sections)
    if find_section(sections, "한국 최신 개발/AI 뉴스") is not None:
        fail("Daily backend brief must not include 한국 최신 개발/AI 뉴스 section.")

    if re.search(r"^##\s+.*(?:커리어|인턴|공모전|해커톤)", content, re.MULTILINE):
        fail("Daily tech brief must not include a long career event section.")

    if any(keyword in content for keyword in ["주가", "관련주", "투자의견"]):
        warn("Daily tech brief may contain price-move-only wording.")

    validate_daily_study_section(sections)
    validate_daily_ps_section(sections)
    validate_daily_oss_section(sections, candidates_dir)
    validate_daily_practical_section(sections)
    validate_daily_cs_term_section(sections)


def validate_daily_section_duplicate_links(sections: list[Section]) -> None:
    for section in sections:
        urls = markdown_link_urls(section.body)
        duplicated = sorted({url for url in urls if urls.count(url) > 1})
        if duplicated:
            fail(
                "Daily backend section repeats the same reference link: "
                f"{section.heading} ({duplicated[0]})"
            )


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
    validate_learning_reference_domains(
        item.body,
        SPRING_ALLOWED_URL_PREFIXES,
        "오늘의 Spring Boot/JVM 학습",
    )


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


def validate_daily_oss_section(sections: list[Section], candidates_dir: Path) -> None:
    section = find_section(sections, "오픈소스 기여 후보")
    if section is None:
        fail("Daily tech brief must include 오픈소스 기여 후보 section.")
    safe_candidates = safe_oss_candidates_by_url(read_oss_candidate_payload(candidates_dir))

    found_forbidden = [
        pattern
        for pattern in DAILY_OSS_FORBIDDEN_PATTERNS
        if re.search(pattern, section.body, flags=re.IGNORECASE)
    ]
    if found_forbidden:
        fail(f"OSS section contains forbidden phrase(s): {', '.join(found_forbidden)}")

    issue_urls = sorted({normalize_github_issue_url(url) for url in github_issue_urls(section.body)})
    has_issue_link = bool(issue_urls)
    if len(issue_urls) > 1:
        fail("OSS section must include at most one GitHub issue URL.")
    if has_issue_link and DAILY_OSS_EMPTY_STATE in section.body:
        fail("OSS section must not mix an issue URL with the empty-state prep routine.")
    if not safe_candidates and has_issue_link:
        fail("OSS candidate JSON has no safe candidate, but Markdown includes an issue URL.")
    if safe_candidates and not has_issue_link:
        fail("OSS candidate JSON has safe candidate(s), but Markdown does not include an issue URL.")
    if DAILY_OSS_EMPTY_STATE not in section.body and not has_issue_link:
        fail("OSS section must include an Issue 보기 link or the required prep-routine phrase.")

    items = extract_items(section)
    if len(items) > 1:
        fail("OSS section must include at most one candidate.")
    if not items:
        if DAILY_OSS_EMPTY_STATE in section.body:
            return
        fail("OSS section has no candidate and no required empty-state phrase.")

    item = items[0]
    if DAILY_OSS_EMPTY_STATE in item.body and not has_issue_link:
        if item.title != "오늘의 OSS 기여 준비 루틴":
            fail("OSS prep routine must use the required heading.")
        missing = missing_bullet_fields(item.body, DAILY_OSS_PREP_FIELDS)
        if missing:
            fail(f"OSS prep routine is missing field(s): {', '.join(missing)}")
        return
    if not issue_urls:
        fail("OSS candidate must include a GitHub issue URL.")
    issue_url = issue_urls[0]
    candidate = safe_candidates.get(issue_url)
    if candidate is None:
        fail("OSS issue URL is not present in safe_to_recommend candidate JSON items.")

    if not re.search(r"P[45]-like", item.body):
        fail("OSS candidate must include P5-like or P4-like difficulty band.")
    if re.search(r"too_hard|unclear", item.body, flags=re.IGNORECASE):
        fail("OSS candidate must not recommend too_hard or unclear issues.")
    missing = missing_bullet_fields(item.body, DAILY_OSS_FIELDS)
    if missing:
        fail(f"OSS candidate is missing field(s): {item.title} ({', '.join(missing)})")
    status_check = bullet_field_value(item.body, "상태 확인")
    missing_status_groups = [
        name
        for name, patterns in DAILY_OSS_STATUS_REQUIRED_GROUPS.items()
        if not any(re.search(pattern, status_check, flags=re.IGNORECASE) for pattern in patterns)
    ]
    if missing_status_groups:
        fail(f"OSS 상태 확인 is missing candidate safety signal(s): {', '.join(missing_status_groups)}")
    first_action = bullet_field_value(item.body, "첫 30분 액션")
    if re.match(r"`?(PR\s*생성|코드\s*수정|구현)", first_action, flags=re.IGNORECASE):
        fail("OSS 첫 30분 액션 must not start with PR creation or code editing.")
    validate_item_markdown_link(item)
    validate_oss_candidate_alignment(item, candidate, issue_url)


def validate_oss_candidate_alignment(
    item: Item,
    candidate: dict[str, object],
    issue_url: str,
) -> None:
    link_value = bullet_field_value(item.body, "링크")
    link_issue_urls = [
        normalize_github_issue_url(url)
        for url in github_issue_urls(link_value)
    ]
    if link_issue_urls != [issue_url]:
        fail("OSS candidate 링크 field must contain exactly the safe candidate issue URL.")

    repository = candidate_text_value(candidate, "repository", "repo")
    repository_value = bullet_field_value(item.body, "저장소")
    if repository and repository not in repository_value:
        fail("OSS candidate 저장소 field must match the safe candidate JSON repository.")

    difficulty_band = candidate_text_value(candidate, "difficulty_band")
    difficulty_value = bullet_field_value(item.body, "난이도 밴드")
    if difficulty_band and normalize_token_value(difficulty_band) not in normalize_token_value(difficulty_value):
        fail("OSS candidate 난이도 밴드 field must match the safe candidate JSON.")

    contribution_type = candidate_text_value(candidate, "contribution_type")
    contribution_value = bullet_field_value(item.body, "기여 유형")
    if contribution_type and not text_contains_expected_or_alias(
        contribution_value,
        contribution_type,
        OSS_CONTRIBUTION_TYPE_ALIASES,
    ):
        fail("OSS candidate 기여 유형 field must match the safe candidate JSON.")

    if not bullet_field_value(item.body, "첫 30분 액션"):
        fail("OSS candidate 첫 30분 액션 field must not be empty.")
    if not bullet_field_value(item.body, "기여 전 매너"):
        fail("OSS candidate 기여 전 매너 field must not be empty.")


def validate_news_item_identity(
    item: Item,
    seen_titles: list[str],
    seen_urls: set[str],
    domain_counts: Counter[str],
) -> None:
    title = re.sub(r"^\d+\.\s+", "", item.title).strip()
    title_key = normalize_validation_title(title)
    if title_key in seen_titles or any(
        difflib.SequenceMatcher(None, title_key, seen).ratio() >= 0.9
        for seen in seen_titles
    ):
        fail(f"Duplicate daily news title found: {title}")
    seen_titles.append(title_key)

    core = bullet_field_value(item.body, "핵심")
    core_key = normalize_validation_title(core)
    if core_key == title_key or difflib.SequenceMatcher(None, core_key, title_key).ratio() >= 0.82:
        fail(f"Daily news 핵심 must not just repeat the title: {title}")

    link_value = bullet_field_value(item.body, "링크")
    if not MARKDOWN_LINK_RE.search(link_value):
        fail(f"Daily news item must include a Markdown link in 링크 field: {title}")

    urls = markdown_link_urls(link_value)
    if not urls:
        fail(f"Daily news item must include a URL: {title}")
    for url in urls:
        url_key = normalize_validation_url(url)
        if url_key in seen_urls:
            fail(f"Duplicate daily news URL found: {url}")
        seen_urls.add(url_key)
        domain_counts[validation_domain(url)] += 1


def validate_daily_news_tech_item(item: Item) -> None:
    title = re.sub(r"^\d+\.\s+", "", item.title).strip()
    missing = missing_bullet_fields(item.body, NEWS_DAILY_TECH_FIELDS_REQUIRED)
    viewpoint = bullet_field_value(item.body, "백엔드 주니어 관점")
    learning_action = bullet_field_value(item.body, "내가 뭘 배워야 하는가")
    if not viewpoint and not learning_action:
        missing.append("백엔드 주니어 관점 또는 내가 뭘 배워야 하는가")
    if missing:
        fail(f"Daily tech news item is missing field(s): {title} ({', '.join(missing)})")

    empty_fields = [
        field
        for field in NEWS_DAILY_TECH_FIELDS_REQUIRED
        if not bullet_field_value(item.body, field)
    ]
    if empty_fields:
        fail(f"Daily tech news item has empty field(s): {title} ({', '.join(empty_fields)})")
    if viewpoint and not viewpoint.strip():
        fail(f"Daily tech news 백엔드 주니어 관점 is empty: {title}")
    if learning_action and not is_specific_growth_action(learning_action):
        fail(f"Daily tech news learning action is not concrete enough: {title}")

    keywords = bullet_field_value(item.body, "더 볼 키워드")
    if keyword_count(keywords) < 2:
        fail(f"Daily tech news 더 볼 키워드 must include at least two keywords: {title}")


def validate_daily_news_investment_item(item: Item) -> None:
    title = re.sub(r"^\d+\.\s+", "", item.title).strip()
    missing = missing_bullet_fields(item.body, NEWS_DAILY_INVESTMENT_FIELDS)
    if missing:
        fail(f"Daily investment news item is missing field(s): {title} ({', '.join(missing)})")

    empty_fields = [
        field
        for field in NEWS_DAILY_INVESTMENT_FIELDS
        if not bullet_field_value(item.body, field)
    ]
    if empty_fields:
        fail(f"Daily investment news item has empty field(s): {title} ({', '.join(empty_fields)})")

    if matches_any_pattern(item.body, NEWS_DAILY_INVESTMENT_ADVICE_PATTERNS):
        fail(f"Daily investment news item contains investment advice wording: {title}")

    technology_link = bullet_field_value(item.body, "기술과 연결")
    metrics = bullet_field_value(item.body, "확인할 지표")
    if not news_daily_has_tech_context("\n".join([technology_link, metrics])):
        fail(f"Daily investment news item must connect to technology demand or metrics: {title}")
    if is_vague_technology_link(technology_link):
        fail(f"Daily investment news item has vague technology connection: {title}")
    if not matches_any_pattern(metrics, NEWS_DAILY_OBJECTIVE_METRIC_PATTERNS):
        fail(f"Daily investment news item must include at least one objective metric: {title}")

    short_term_text = "\n".join(
        [
            title,
            bullet_field_value(item.body, "핵심"),
            bullet_field_value(item.body, "투자 관찰 포인트"),
        ]
    )
    if matches_any_pattern(short_term_text, NEWS_DAILY_MARKET_PRICE_PATTERNS):
        if not matches_any_pattern(short_term_text, NEWS_DAILY_PRICE_CONTEXT_PATTERNS):
            fail(f"Daily investment news item describes price movement without business driver: {title}")
        if not news_daily_has_tech_context("\n".join([item.body, technology_link, metrics])):
            fail(f"Daily investment news item describes market movement without technology context: {title}")


def is_specific_growth_action(text: str) -> bool:
    if not text.strip():
        return False
    if re.fullmatch(r"(?:기사|뉴스|원문)?\s*(?:읽기|보기|확인)\s*", text.strip()):
        return False
    if matches_any_pattern(text, NEWS_DAILY_VAGUE_ACTION_PATTERNS):
        return False
    return matches_any_pattern(text, NEWS_DAILY_GROWTH_ACTION_PATTERNS)


def is_vague_technology_link(text: str) -> bool:
    stripped = re.sub(r"\s+", " ", text.strip())
    if not stripped:
        return True
    vague = [
        r"AI와\s*관련(?:이\s*)?있(?:다|습니다)?\.?",
        r"기술과\s*(?:관련|연결)(?:이\s*)?있(?:다|습니다)?\.?",
        r"AI\s*기술과\s*(?:관련|연결)(?:이\s*)?있(?:다|습니다)?\.?",
    ]
    return matches_any_pattern(stripped, vague) and len(stripped) < 35


def validate_daily_news_growth_section(section: Section | None) -> None:
    if section is None:
        fail("Daily news brief must include 오늘의 성장 판단 section.")
    missing = missing_bullet_fields(section.body, NEWS_DAILY_GROWTH_FIELDS)
    if missing:
        fail(f"Daily news growth section is missing field(s): {', '.join(missing)}")

    score = bullet_field_value(section.body, "도움 점수")
    if not re.fullmatch(r"[1-5]", score):
        fail("Daily news growth score must be an integer from 1 to 5.")
    reason = bullet_field_value(section.body, "왜 도움 되는가")
    action = bullet_field_value(section.body, "오늘 할 일 1개")
    if not reason:
        fail("Daily news growth reason must not be empty.")
    if not is_specific_growth_action(action):
        fail("Daily news growth action must be a concrete allowed action.")


def validate_daily_news(content: str) -> None:
    if not re.search(r"^#\s+Career Feed - Tech & Investment Daily\s*$", content, re.MULTILINE):
        fail("Missing Tech & Investment Daily title.")
    if "오늘의 흐름:" not in content:
        fail("Daily news brief must include 오늘의 흐름 field.")
    if matches_any_pattern(content, NEWS_DAILY_INVESTMENT_ADVICE_PATTERNS):
        fail("Daily news brief contains investment advice wording.")

    sections = extract_sections(content)
    tech_section = find_section(sections, "새 기술 이야기")
    investment_section = find_section(sections, "주식/투자 이야기")
    bridge_section = find_section(sections, "기술과 시장 연결")
    growth_section = find_section(sections, "오늘의 성장 판단")
    tech_items = extract_items(tech_section) if tech_section else []
    investment_items = extract_items(investment_section) if investment_section else []
    news_count = len(tech_items) + len(investment_items)

    validate_common(content, min_links=news_count)
    validate_daily_news_growth_section(growth_section)
    if len(investment_items) > 2:
        fail("Daily news brief must not include more than 2 investment items.")
    if news_count > NEWS_DAILY_SECTIONS_MAX:
        fail(f"Daily news brief must not include more than {NEWS_DAILY_SECTIONS_MAX} news items.")
    if NEWS_DAILY_DEFAULT_MIN <= news_count <= NEWS_DAILY_SECTIONS_MAX:
        pass
    elif 1 <= news_count <= NEWS_DAILY_SPARSE_MAX:
        if not news_daily_has_sparse_phrase(content, news_count):
            fail("Sparse daily news brief must state that fewer than 3 items met the criteria.")
    elif news_count == 0:
        if not news_daily_has_empty_phrase(content):
            fail("Empty daily news brief must include the required no-qualified-news phrase.")
        return
    else:
        fail("Daily news brief has an invalid number of news items.")

    if tech_items and investment_items:
        if bridge_section is None or not bridge_section.body.strip():
            fail("Daily news brief with both tracks must include 기술과 시장 연결 section.")
        if not news_daily_has_tech_context(bridge_section.body):
            fail("Daily news bridge section must connect technology and market demand.")

    seen_titles: list[str] = []
    seen_urls: set[str] = set()
    domain_counts: Counter[str] = Counter()
    for item in tech_items:
        validate_news_item_identity(item, seen_titles, seen_urls, domain_counts)
        validate_daily_news_tech_item(item)
    for item in investment_items:
        validate_news_item_identity(item, seen_titles, seen_urls, domain_counts)
        validate_daily_news_investment_item(item)

    repeated_domains = [
        (domain, count)
        for domain, count in domain_counts.items()
        if domain and count >= 3
    ]
    for domain, count in repeated_domains:
        if is_official_tech_blog_domain(domain):
            warn(f"Daily news uses the same official tech blog domain {count} times: {domain}")
            continue
        fail(f"Daily news repeats the same domain {count} times: {domain}")


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
    require_markdown_link_in_text(item.body, "주니어 백엔드 실무지식")
    validate_learning_reference_domains(
        item.body,
        PRACTICAL_ALLOWED_URL_PREFIXES,
        "주니어 백엔드 실무지식",
    )
    if len(section.body) > 1200:
        warn("Backend practical knowledge section may be too long for daily reading.")


def validate_daily_cs_term_section(sections: list[Section]) -> None:
    section = find_section(sections, "오늘의 CS Core & 백엔드 용어")
    if section is None:
        fail("Daily tech brief must include 오늘의 CS Core & 백엔드 용어 section.")

    items = extract_items(section)
    cs_item = next((item for item in items if item.title.startswith("CS Core:")), None)
    term_item = next((item for item in items if item.title.startswith("백엔드 용어:")), None)
    if cs_item is None:
        fail("CS/term section must include a CS Core topic heading.")
    if term_item is None:
        fail("CS/term section must include a backend term heading.")

    missing = missing_bullet_fields(cs_item.body, DAILY_CS_CORE_FIELDS)
    if missing:
        fail(f"CS Core topic is missing field(s): {', '.join(missing)}")
    missing = missing_bullet_fields(term_item.body, DAILY_BACKEND_TERM_FIELDS)
    if missing:
        fail(f"Backend term is missing field(s): {', '.join(missing)}")

    for item, context in (
        (cs_item, "오늘의 CS Core"),
        (term_item, "오늘의 백엔드 용어"),
    ):
        require_markdown_link_in_text(item.body, context)

    if not bullet_field_value(cs_item.body, "10~20분 확인"):
        fail("CS Core topic must include a concrete 10~20 minute check action.")
    if not bullet_field_value(cs_item.body, "완료 기준"):
        fail("CS Core topic must include done criteria.")
    if not bullet_field_value(term_item.body, "오해하면 생기는 문제"):
        fail("Backend term must include the risk of misunderstanding.")
    if not bullet_field_value(term_item.body, "Spring/API 연결"):
        fail("Backend term must include a Spring/API connection.")
    if len(section.body) > DAILY_CS_TERM_SECTION_MAX_CHARS:
        fail(
            "CS Core & backend term section is too long for daily reading: "
            f"{len(section.body)} chars"
        )


def validate_weekly_career(content: str) -> None:
    if "Career Feed - Backend Career Site Radar" not in content:
        fail("Missing weekly career site radar title.")
    validate_weekly_forbidden_text(content)
    sections = extract_sections(content)
    validate_common(content, min_links=19)
    validate_no_raw_weekly_urls(content)
    validate_no_duplicate_weekly_site_headings(content)
    require_sections(sections, WEEKLY_SECTIONS)

    for label, min_count in WEEKLY_SITE_SECTION_MIN_COUNTS.items():
        section = find_section(sections, label)
        if section is None:
            fail(f"Weekly career site radar must include {label} section.")
        validate_weekly_site_radar_section(section, min_count)

    validate_weekly_site_presence(sections)
    routine_section = find_section(sections, "30분 확인 루틴")
    if routine_section is None or "북마크" not in routine_section.body:
        fail("Weekly career site radar must include the 30-minute bookmark routine.")


def validate_no_raw_weekly_urls(content: str) -> None:
    without_markdown_links = MARKDOWN_LINK_RE.sub("", content)
    raw_urls = LINK_RE.findall(without_markdown_links)
    if raw_urls:
        fail(f"Weekly career site radar uses raw URL text: {raw_urls[0]}")


def validate_no_duplicate_weekly_site_headings(content: str) -> None:
    headings = [
        heading.strip()
        for heading in re.findall(r"^###\s+(.+?)\s*$", content, flags=re.MULTILINE)
    ]
    duplicated = sorted({heading for heading in headings if headings.count(heading) > 1})
    if duplicated:
        fail(f"Duplicate weekly career site heading found: {duplicated[0]}")


def validate_weekly_site_radar_section(section: Section, min_count: int) -> None:
    sites = extract_items(section)
    if len(sites) < min_count:
        fail(
            f"Weekly career section needs at least {min_count} site entries: "
            f"{section.heading}"
        )
    for site in sites:
        missing = missing_bullet_fields(site.body, WEEKLY_REQUIRED_FIELDS)
        if missing:
            fail(
                f"Weekly career site entry is missing field(s): "
                f"{', '.join(missing)} ({site.title})"
            )
        link_line = bullet_field_value(site.body, "바로가기")
        links = re.findall(r"\[([^\]]+)\]\((https?://[^)]+)\)", link_line)
        if not links:
            fail(f"Weekly career site entry must include Markdown links: {site.title}")
        for label, url in links:
            if label.strip() == "사이트 보기":
                fail(f"Weekly career site link label is too generic: {site.title}")
            validate_weekly_site_url(url, site.title)


def validate_weekly_site_url(url: str, context: str) -> None:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        fail(f"Weekly career site radar uses invalid URL: {context} ({url})")
    if is_blocked_weekly_domain(url):
        fail(f"Weekly career site radar uses news URL: {context} ({url})")
    lowered = f"{parsed.netloc}{parsed.path}".lower()
    if re.search(r"(?:^|[./_-])(news|press|pr)(?:[./_-]|$)", lowered):
        fail(f"Weekly career site radar uses news or press URL: {context} ({url})")


def count_weekly_named_sites(sections: list[Section], section_label: str, names: list[str]) -> int:
    section = find_section(sections, section_label)
    if section is None:
        return 0
    return sum(1 for name in names if name in section.body)


def validate_weekly_site_presence(sections: list[Section]) -> None:
    job_count = count_weekly_named_sites(
        sections,
        "공식 채용 사이트",
        WEEKLY_JOB_REQUIRED_SITE_NAMES,
    )
    if job_count < len(WEEKLY_JOB_REQUIRED_SITE_NAMES):
        fail("Weekly career official site section is missing required company sites.")

    intern_count = count_weekly_named_sites(
        sections,
        "채용·인턴 플랫폼",
        WEEKLY_INTERN_REQUIRED_SITE_NAMES,
    )
    if intern_count < len(WEEKLY_INTERN_REQUIRED_SITE_NAMES):
        fail("Weekly career platform section is missing required job/intern sites.")

    competition_count = count_weekly_named_sites(
        sections,
        "해커톤·공모전·경진대회 플랫폼",
        WEEKLY_COMPETITION_REQUIRED_SITE_NAMES,
    )
    if competition_count < len(WEEKLY_COMPETITION_REQUIRED_SITE_NAMES):
        fail("Weekly career activity section is missing required competition sites.")


def extract_weekly_category_blocks(section: Section) -> dict[str, str]:
    matches = list(WEEKLY_CATEGORY_HEADING_RE.finditer(section.body))
    blocks: dict[str, str] = {}
    for index, match in enumerate(matches):
        label = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(section.body)
        blocks[label] = section.body[start:end].strip()
    return blocks


def validate_weekly_category_section(section: Section) -> None:
    blocks = extract_weekly_category_blocks(section)
    missing = [label for label in WEEKLY_CATEGORY_LABELS if label not in blocks]
    if missing:
        fail(f"Weekly career type section is missing category subsection(s): {', '.join(missing)}")
    for label in WEEKLY_CATEGORY_LABELS:
        body = blocks[label]
        empty_state = WEEKLY_CATEGORY_EMPTY_STATES[label]
        candidate_matches = list(WEEKLY_CANDIDATE_HEADING_RE.finditer(body))
        if not candidate_matches:
            if empty_state not in body:
                fail(f"Weekly career {label} subsection has no candidate and no empty-state.")
            continue
        if empty_state in body:
            fail(f"Weekly career {label} subsection has both candidate and empty-state.")
        if len(candidate_matches) > 1:
            fail(f"Weekly career {label} subsection must include at most one candidate.")
        match = candidate_matches[0]
        item = Item(title=match.group(1).strip(), body=body[match.end() :].strip())
        validate_weekly_item(item)
        validate_weekly_recommended_text(item)


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
    found_text = [
        pattern
        for pattern in WEEKLY_FORBIDDEN_TEXT_PATTERNS
        if re.search(pattern, content, flags=re.IGNORECASE)
    ]
    current_year = datetime.now().year
    past_years = [
        str(year)
        for year in range(2022, current_year)
        if re.search(rf"\b{year}\b", content)
    ]
    if found_text or past_years:
        values = found_text + past_years
        fail(f"Weekly career brief contains forbidden wording: {', '.join(values)}")


def validate_weekly_item(item: Item) -> None:
    missing = missing_bullet_fields(item.body, WEEKLY_REQUIRED_FIELDS)
    if missing:
        fail(f"Weekly career item is missing field(s): {item.title} ({', '.join(missing)})")
    deadline = bullet_field_value(item.body, "마감")
    if deadline:
        validate_weekly_deadline_value(deadline, item.title)
    validate_weekly_item_links(item.body, item.title)
    validate_weekly_naver_host_policy(item.body, item.title)


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


def validate_weekly_tracking_section(sections: list[Section]) -> None:
    section = find_section(sections, "다음 주에도 추적할 후보")
    if section is None:
        fail("Weekly career brief must include 다음 주에도 추적할 후보 section.")
    if WEEKLY_TRACKING_EMPTY_STATE in section.body:
        return
    lines = [line.strip() for line in section.body.splitlines() if line.strip().startswith("- ")]
    if not lines:
        fail("다음 주에도 추적할 후보 section must include cache candidates or the required empty-state phrase.")
    for line in lines:
        if "지난 후보" not in line and "다시 확인" not in line:
            fail("Tracking section must only include revalidated cache candidates.")
        validate_weekly_item_links(line, "다음 주에도 추적할 후보")


def validate(content: str, report_type: str, candidates_dir: Path) -> None:
    if report_type == "daily-tech":
        validate_daily_tech(content, candidates_dir)
    elif report_type == "daily-news":
        validate_daily_news(content)
    elif report_type == "weekly-career":
        validate_weekly_career(content)
    else:
        fail(f"Unsupported report type: {report_type}")


def main() -> int:
    args = parse_args()
    try:
        content = read_report(Path(args.path))
        validate(content, args.type, Path(args.candidates_dir))
    except (OSError, UnicodeDecodeError, RuntimeError) as exc:
        print(f"Career Feed brief validation failed: {exc}", file=sys.stderr)
        return 1

    print(f"Career Feed brief validation passed: {args.path} ({args.type})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
