#!/usr/bin/env python3
"""Build a compact News Daily shortlist for Codex input."""

from __future__ import annotations

import argparse
import difflib
import json
import re
import urllib.parse
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


KST = ZoneInfo("Asia/Seoul")
DEFAULT_INPUT_FILES = [
    Path("reports/candidates/kr-dev-ai-news.json"),
    Path("reports/candidates/kr-ai-tech-news.json"),
]
DEFAULT_AUDIENCE_PROFILE = Path("configs/audience-profile.json")
DEFAULT_OUTPUT_FILE = Path("reports/candidates/kr-tech-news-shortlist.json")
DEFAULT_MAX_ITEMS = 12
TEXT_LIMIT = 180

INVESTMENT_OPINION_PATTERNS = [
    r"목표가",
    r"매수",
    r"매도",
    r"투자\s*의견",
    r"투자의견",
    r"추천주",
]
RELATED_STOCK_PATTERNS = [
    r"관련주",
    r"테마주",
    r"수혜주",
    r"급등주",
]
PRICE_ONLY_PATTERNS = [
    r"주가",
    r"급등",
    r"급락",
    r"상한가",
    r"하한가",
]
MARKET_CONTEXT_KEYWORDS = [
    "ai infrastructure",
    "infrastructure investment",
    "데이터센터",
    "data center",
    "gpu",
    "hbm",
    "반도체",
    "서버",
    "클라우드",
    "cloud",
    "capex",
    "투자",
    "인프라",
]
DEVELOPER_CONTEXT_KEYWORDS = [
    "developer",
    "개발자",
    "api",
    "sdk",
    "플랫폼",
    "platform",
    "backend",
    "백엔드",
    "인프라",
    "클라우드",
    "cloud",
    "데이터센터",
    "서버",
    "ai 서비스",
    "채용",
    "역량",
]
ALLOWED_CATEGORIES = {
    "AI",
    "Backend",
    "Cloud",
    "Security",
    "Data",
    "Developer Productivity",
    "Open Source",
    "Business/Market Context",
}
RELIABILITY_WEIGHT = {
    "official": 20,
    "major_media": 12,
    "platform": 10,
    "aggregator": 5,
    "unknown": 0,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-file",
        action="append",
        type=Path,
        default=[],
        help="Candidate JSON file. Defaults to the two News Daily candidate files.",
    )
    parser.add_argument(
        "--audience-profile",
        type=Path,
        default=DEFAULT_AUDIENCE_PROFILE,
        help="Audience profile config path.",
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        default=DEFAULT_OUTPUT_FILE,
        help="Shortlist JSON output path.",
    )
    parser.add_argument(
        "--max-items",
        type=int,
        default=DEFAULT_MAX_ITEMS,
        help="Maximum shortlist item count.",
    )
    return parser.parse_args()


def now_kst() -> str:
    return datetime.now(tz=KST).strftime("%Y-%m-%d %H:%M:%S KST")


def read_json_object(path: Path) -> dict[str, object]:
    if not path.exists():
        return {
            "items": [],
            "candidate_count": 0,
            "warnings": [{"file": str(path), "warning": "candidate file missing"}],
        }
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Candidate JSON must be an object: {path}")
    return payload


def compact_text(value: object, limit: int = TEXT_LIMIT) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)].rstrip() + "..."


def text_value(item: dict[str, object], *keys: str) -> str:
    for key in keys:
        value = item.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return ""


def normalized_url(url: str) -> str:
    if not url:
        return ""
    parsed = urllib.parse.urlsplit(url.strip())
    query_items = [
        (key, value)
        for key, value in urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
        if not key.lower().startswith("utm_")
        and key.lower() not in {"fbclid", "gclid", "igshid"}
    ]
    query = urllib.parse.urlencode(query_items, doseq=True)
    return urllib.parse.urlunsplit(
        (
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path.rstrip("/") or parsed.path,
            query,
            "",
        )
    )


def normalized_title(title: str) -> str:
    cleaned = re.sub(
        r"\s*[-–—|:]\s*(전자신문|ZDNet Korea|지디넷코리아|블로터|AI타임스|"
        r"디지털데일리|ITWorld|CIO Korea)\s*$",
        " ",
        title,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"[^\w가-힣]+", " ", cleaned, flags=re.UNICODE)
    return re.sub(r"\s+", " ", cleaned.strip()).lower()


def matches_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def contains_any(text: str, keywords: list[str]) -> bool:
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in keywords)


def has_market_context(text: str) -> bool:
    return contains_any(text, MARKET_CONTEXT_KEYWORDS)


def has_developer_context(text: str) -> bool:
    return contains_any(text, DEVELOPER_CONTEXT_KEYWORDS)


def infer_market_context(text: str) -> str:
    if not (has_market_context(text) and has_developer_context(text)):
        return ""
    if contains_any(text, ["데이터센터", "data center", "gpu", "hbm", "반도체", "서버"]):
        return "AI 인프라와 서버 수요 변화가 클라우드 운영, API 비용, 백엔드 역량 수요와 연결되는지 볼 후보입니다."
    if contains_any(text, ["api", "sdk", "플랫폼", "developer", "개발자"]):
        return "기업 투자와 플랫폼 변화가 API, SDK, 개발자 생태계에 미치는 영향을 볼 후보입니다."
    return "시장 변화가 개발자 인프라, 클라우드 운영, 역량 수요와 연결되는지 볼 후보입니다."


def risk_flags_for(item: dict[str, object], market_context: str) -> list[str]:
    exclude_reason = text_value(item, "exclude_reason")
    text = " ".join(
        [
            text_value(item, "title"),
            text_value(item, "summary", "description"),
            text_value(item, "query"),
            exclude_reason,
        ]
    )
    flags: list[str] = []
    if matches_any(text, INVESTMENT_OPINION_PATTERNS):
        flags.append("investment_opinion")
    if matches_any(text, RELATED_STOCK_PATTERNS):
        flags.append("related_stock")
    price_only = matches_any(text, PRICE_ONLY_PATTERNS) and not market_context
    if price_only or ("stock-or-investment-only" in exclude_reason and not market_context):
        flags.append("stock_only")
    if "promotional" in text.lower() or "홍보" in text:
        flags.append("promotional")
    if text_value(item, "developer_relevance").lower() == "low" and not market_context:
        flags.append("weak_developer_relevance")
    return list(dict.fromkeys(flags))


def should_exclude(flags: list[str]) -> bool:
    return any(
        flag in {"stock_only", "investment_opinion", "related_stock"}
        for flag in flags
    )


def int_score(value: object) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def category_hint_for(item: dict[str, object], market_context: str) -> str:
    category = text_value(item, "category_hint")
    if market_context:
        return "Business/Market Context"
    if category in ALLOWED_CATEGORIES:
        return category
    text = " ".join([text_value(item, "title"), text_value(item, "summary")]).lower()
    if contains_any(text, ["security", "보안", "cve", "취약점"]):
        return "Security"
    if contains_any(text, ["cloud", "클라우드", "kubernetes", "aws", "ncloud"]):
        return "Cloud"
    if contains_any(text, ["data", "데이터", "postgresql", "redis", "kafka"]):
        return "Data"
    if contains_any(text, ["open source", "오픈소스"]):
        return "Open Source"
    if contains_any(text, ["productivity", "생산성", "ci", "코딩 에이전트"]):
        return "Developer Productivity"
    if contains_any(text, ["ai", "llm", "모델", "에이전트"]):
        return "AI"
    return "Backend"


def shortlist_item(item: dict[str, object]) -> dict[str, object] | None:
    title = text_value(item, "title")
    url = text_value(item, "url", "source_url")
    if not title or not url:
        return None

    source_reliability = text_value(item, "source_reliability") or "unknown"
    text = " ".join(
        [
            title,
            text_value(item, "summary", "description"),
            text_value(item, "query"),
            text_value(item, "developer_relevance"),
        ]
    )
    market_context = compact_text(infer_market_context(text))
    risk_flags = risk_flags_for(item, market_context)
    if should_exclude(risk_flags):
        return None

    return {
        "title": compact_text(title, 160),
        "url": url,
        "source": text_value(item, "source", "source_name"),
        "publisher": text_value(item, "publisher"),
        "published_at_kst": text_value(item, "published_at_kst", "published_at"),
        "category_hint": category_hint_for(item, market_context),
        "summary": compact_text(text_value(item, "summary", "description")),
        "developer_relevance": compact_text(text_value(item, "developer_relevance")),
        "market_context": market_context,
        "score": int_score(item.get("score"))
        + RELIABILITY_WEIGHT.get(source_reliability, 0),
        "source_reliability": source_reliability,
        "risk_flags": risk_flags,
        "_canonical_url": text_value(item, "canonical_url") or normalized_url(url),
        "_normalized_title": text_value(item, "normalized_title") or normalized_title(title),
    }


def is_duplicate(candidate: dict[str, object], selected: list[dict[str, object]]) -> bool:
    candidate_url = str(candidate.get("_canonical_url", ""))
    candidate_title = str(candidate.get("_normalized_title", ""))
    for item in selected:
        if candidate_url and candidate_url == str(item.get("_canonical_url", "")):
            return True
        selected_title = str(item.get("_normalized_title", ""))
        if candidate_title and selected_title:
            if candidate_title == selected_title:
                return True
            if difflib.SequenceMatcher(None, candidate_title, selected_title).ratio() >= 0.9:
                return True
    return False


def public_item(item: dict[str, object]) -> dict[str, object]:
    return {
        key: value
        for key, value in item.items()
        if not key.startswith("_")
    }


def build_shortlist(
    input_files: list[Path],
    audience_profile_path: Path,
    max_items: int,
) -> dict[str, object]:
    if audience_profile_path.exists():
        audience_profile = read_json_object(audience_profile_path)
    else:
        audience_profile = {}

    raw_items: list[dict[str, object]] = []
    source_errors: list[object] = []
    warnings: list[object] = []
    raw_candidate_count_total = 0
    for path in input_files:
        payload = read_json_object(path)
        items = payload.get("items", [])
        if isinstance(items, list):
            raw_items.extend(item for item in items if isinstance(item, dict))
        raw_candidate_count_total += int_score(payload.get("candidate_count")) or (
            len(items) if isinstance(items, list) else 0
        )
        if isinstance(payload.get("source_errors"), list):
            source_errors.extend(payload["source_errors"])  # type: ignore[index]
        if isinstance(payload.get("warnings"), list):
            warnings.extend(payload["warnings"])  # type: ignore[index]

    candidates = [
        item
        for item in (shortlist_item(raw_item) for raw_item in raw_items)
        if item is not None
    ]
    candidates.sort(
        key=lambda item: (
            int_score(item.get("score")),
            str(item.get("published_at_kst", "")),
        ),
        reverse=True,
    )

    selected: list[dict[str, object]] = []
    for candidate in candidates:
        if is_duplicate(candidate, selected):
            continue
        selected.append(candidate)
        if len(selected) >= max(0, max_items):
            break

    market_policy = {}
    if isinstance(audience_profile.get("preferences"), dict):
        market_policy = audience_profile["preferences"].get("market_context", {})  # type: ignore[index]
        if not isinstance(market_policy, dict):
            market_policy = {}

    return {
        "schema_version": 1,
        "mode": "daily-news-shortlist",
        "generated_at_kst": now_kst(),
        "input_files": [str(path) for path in input_files],
        "audience_profile": str(audience_profile_path),
        "raw_candidate_count_total": raw_candidate_count_total,
        "shortlist_count": len(selected),
        "max_items": max_items,
        "market_context_policy": market_policy,
        "source_errors": source_errors,
        "warnings": warnings,
        "items": [public_item(item) for item in selected],
    }


def main() -> int:
    args = parse_args()
    input_files = args.input_file or DEFAULT_INPUT_FILES
    payload = build_shortlist(input_files, args.audience_profile, args.max_items)
    args.output_file.parent.mkdir(parents=True, exist_ok=True)
    args.output_file.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {payload['shortlist_count']} shortlist item(s): {args.output_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
