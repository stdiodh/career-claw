#!/usr/bin/env python3
"""Build a compact Tech & Investment Daily shortlist for Codex input."""

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
DEFAULT_TECH_MAX_ITEMS = 8
DEFAULT_INVESTMENT_MAX_ITEMS = 4
DEFAULT_MAX_ITEMS = DEFAULT_TECH_MAX_ITEMS + DEFAULT_INVESTMENT_MAX_ITEMS
TEXT_LIMIT = 160

TECH_CATEGORIES = {
    "AI",
    "Backend",
    "Cloud",
    "Security",
    "Data",
    "Developer Productivity",
    "Open Source",
}
INVESTMENT_CATEGORIES = {
    "Investment",
    "Earnings",
    "Semiconductor",
    "Cloud CAPEX",
    "AI Infra",
    "Platform Business",
}
RELIABILITY_WEIGHT = {
    "official": 20,
    "major_media": 12,
    "platform": 10,
    "aggregator": 5,
    "unknown": 0,
}

HARD_EXCLUDE_PATTERNS = {
    "related_stock_list": [
        r"관련주",
        r"테마주",
        r"수혜주",
        r"종목\s*리스트",
        r"추천\s*종목",
    ],
    "pump_style": [
        r"급등주",
        r"상한가",
        r"따상",
        r"폭등\s*예상",
    ],
    "buy_sell_command": [
        r"지금\s*(?:사야|사지|매수|팔아야|팔지|매도)",
        r"(?:매수|매도)\s*(?:추천|의견|전략)",
        r"사라",
        r"팔아라",
    ],
    "guaranteed_return": [
        r"수익\s*보장",
        r"확정\s*수익",
        r"무조건\s*(?:상승|오른다|수익)",
    ],
    "promotional": [
        r"종목\s*홍보",
        r"무료\s*리딩",
        r"카톡방",
    ],
}
SOFT_RISK_PATTERNS = {
    "stock_price": [r"주가", r"시가총액"],
    "price_move": [r"급등", r"급락", r"상승", r"하락"],
    "target_price": [r"목표가"],
    "analyst_opinion": [r"투자\s*의견", r"투자의견", r"증권사\s*리포트"],
    "earnings_surprise": [r"실적\s*서프라이즈", r"어닝\s*서프라이즈"],
    "capex": [r"\bCAPEX\b", r"설비\s*투자", r"투자\s*확대"],
    "orders": [r"수주", r"공급\s*계약"],
    "guidance": [r"가이던스", r"전망치", r"컨퍼런스콜"],
}
TECH_CONTEXT_KEYWORDS = [
    "ai infrastructure",
    "ai 인프라",
    "gpu",
    "hbm",
    "반도체",
    "데이터센터",
    "data center",
    "서버",
    "클라우드",
    "cloud",
    "api",
    "sdk",
    "플랫폼",
    "platform",
    "developer",
    "개발자",
    "backend",
    "백엔드",
    "기업용 ai",
    "ai 서비스",
    "llm",
]
INVESTMENT_SIGNAL_KEYWORDS = [
    "실적",
    "매출",
    "영업이익",
    "capex",
    "설비 투자",
    "투자",
    "수요",
    "가이던스",
    "컨퍼런스콜",
    "공시",
    "수주",
    "공급 계약",
    "증권사",
    "주가",
    "목표가",
    "투자의견",
    "비용 구조",
    "사업 전략",
    "기업 전략",
]


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
        help="Maximum flat shortlist item count kept for compatibility.",
    )
    parser.add_argument(
        "--tech-max-items",
        type=int,
        default=DEFAULT_TECH_MAX_ITEMS,
        help="Maximum tech track item count.",
    )
    parser.add_argument(
        "--investment-max-items",
        type=int,
        default=DEFAULT_INVESTMENT_MAX_ITEMS,
        help="Maximum investment track item count.",
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


def int_score(value: object) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def hard_flags_for(text: str) -> list[str]:
    flags: list[str] = []
    for flag, patterns in HARD_EXCLUDE_PATTERNS.items():
        if matches_any(text, patterns):
            flags.append(flag)
    return flags


def soft_risk_flags_for(text: str) -> list[str]:
    flags: list[str] = []
    for flag, patterns in SOFT_RISK_PATTERNS.items():
        if matches_any(text, patterns):
            flags.append(flag)
    return flags


def has_technology_driver(text: str) -> bool:
    return contains_any(text, TECH_CONTEXT_KEYWORDS)


def has_investment_signal(text: str) -> bool:
    return contains_any(text, INVESTMENT_SIGNAL_KEYWORDS) or bool(soft_risk_flags_for(text))


def should_drop_stock_only(item: dict[str, object], text: str) -> bool:
    exclude_reason = text_value(item, "exclude_reason")
    stock_labeled = "price-move-without-tech-driver" in exclude_reason
    price_text = matches_any(text, SOFT_RISK_PATTERNS["stock_price"] + SOFT_RISK_PATTERNS["price_move"])
    return (stock_labeled or price_text) and not has_technology_driver(text)


def infer_track(item: dict[str, object], text: str) -> str:
    query = text_value(item, "query")
    category_hint = text_value(item, "category_hint")
    if category_hint in INVESTMENT_CATEGORIES:
        return "investment"
    if contains_any(query, ["capex", "실적", "투자", "수요", "hbm", "데이터센터"]):
        if has_technology_driver(text):
            return "investment"
    if has_investment_signal(text) and has_technology_driver(text):
        return "investment"
    return "tech"


def investment_relevance_for(text: str) -> str:
    if contains_any(text, ["실적", "매출", "영업이익", "가이던스", "컨퍼런스콜"]):
        return "실적과 가이던스가 AI/cloud 인프라 수요의 지속성을 보여주는지 볼 후보입니다."
    if contains_any(text, ["capex", "설비 투자", "데이터센터", "gpu", "hbm", "반도체"]):
        return "AI 인프라 투자와 서버 수요가 기업 비용 구조와 공급망에 미치는 영향을 볼 후보입니다."
    if contains_any(text, ["api", "sdk", "플랫폼", "기업용 ai", "매출"]):
        return "개발자 플랫폼과 기업용 AI 매출이 API 생태계 변화로 이어지는지 볼 후보입니다."
    return "기술 수요와 기업 전략의 연결을 관찰할 후보입니다."


def technology_link_for(text: str) -> str:
    if contains_any(text, ["gpu", "hbm", "반도체", "데이터센터", "서버"]):
        return "GPU/HBM, 데이터센터, 서버 수요는 AI API 비용과 클라우드 아키텍처 선택에 연결됩니다."
    if contains_any(text, ["capex", "클라우드", "cloud"]):
        return "클라우드 CAPEX는 백엔드 운영 비용, 배포 구조, 인프라 역량 수요와 연결됩니다."
    if contains_any(text, ["api", "sdk", "플랫폼", "developer", "개발자"]):
        return "API/SDK 플랫폼 사업 변화는 개발자 생태계와 서비스 연동 방식에 연결됩니다."
    return "기업의 기술 투자 흐름이 백엔드 개발자가 봐야 할 인프라와 운영 지표에 연결됩니다."


def tech_category_hint_for(item: dict[str, object], text: str) -> str:
    category = text_value(item, "category_hint")
    if category in TECH_CATEGORIES:
        return category
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


def investment_category_hint_for(text: str) -> str:
    if contains_any(text, ["실적", "매출", "영업이익", "가이던스", "컨퍼런스콜"]):
        return "Earnings"
    if contains_any(text, ["hbm", "gpu", "반도체"]):
        return "Semiconductor"
    if contains_any(text, ["capex", "데이터센터", "data center", "클라우드 투자"]):
        return "Cloud CAPEX"
    if contains_any(text, ["ai 인프라", "서버 수요", "ai 서버"]):
        return "AI Infra"
    if contains_any(text, ["api", "sdk", "플랫폼", "기업용 ai"]):
        return "Platform Business"
    return "Investment"


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
            text_value(item, "exclude_reason"),
        ]
    )
    hard_flags = hard_flags_for(text)
    if hard_flags or should_drop_stock_only(item, text):
        return None

    track = infer_track(item, text)
    risk_flags = soft_risk_flags_for(text)
    category_hint = (
        investment_category_hint_for(text)
        if track == "investment"
        else tech_category_hint_for(item, text)
    )

    return {
        "track": track,
        "title": compact_text(title, 160),
        "url": url,
        "source": text_value(item, "source", "source_name"),
        "publisher": text_value(item, "publisher"),
        "published_at_kst": text_value(item, "published_at_kst", "published_at"),
        "category_hint": category_hint,
        "summary": compact_text(text_value(item, "summary", "description"), 160),
        "developer_relevance": compact_text(text_value(item, "developer_relevance"), 120),
        "investment_relevance": compact_text(investment_relevance_for(text), 120)
        if track == "investment"
        else "",
        "technology_link": compact_text(technology_link_for(text), 120),
        "risk_flags": risk_flags,
        "score": int_score(item.get("score"))
        + RELIABILITY_WEIGHT.get(source_reliability, 0),
        "source_reliability": source_reliability,
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
    return {key: value for key, value in item.items() if not key.startswith("_")}


def select_track_items(
    candidates: list[dict[str, object]],
    track: str,
    max_items: int,
    selected: list[dict[str, object]],
) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    for candidate in candidates:
        if candidate.get("track") != track:
            continue
        if is_duplicate(candidate, selected + items):
            continue
        items.append(candidate)
        if len(items) >= max(0, max_items):
            break
    return items


def build_shortlist(
    input_files: list[Path],
    audience_profile_path: Path,
    max_items: int,
    tech_max_items: int,
    investment_max_items: int,
) -> dict[str, object]:
    audience_profile = read_json_object(audience_profile_path) if audience_profile_path.exists() else {}

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

    tech_items = select_track_items(candidates, "tech", tech_max_items, [])
    investment_items = select_track_items(
        candidates,
        "investment",
        investment_max_items,
        tech_items,
    )
    flat_items = sorted(
        tech_items + investment_items,
        key=lambda item: (
            int_score(item.get("score")),
            str(item.get("published_at_kst", "")),
        ),
        reverse=True,
    )[: max(0, max_items)]

    preferences = audience_profile.get("preferences", {})
    if not isinstance(preferences, dict):
        preferences = {}
    content_tracks = preferences.get("content_tracks", {})
    if not isinstance(content_tracks, dict):
        content_tracks = {}
    previous_market_policy = preferences.get("market_context", {})
    if not isinstance(previous_market_policy, dict):
        previous_market_policy = {}

    return {
        "schema_version": 2,
        "mode": "daily-tech-investment-shortlist",
        "generated_at_kst": now_kst(),
        "input_files": [str(path) for path in input_files],
        "audience_profile": str(audience_profile_path),
        "raw_candidate_count_total": raw_candidate_count_total,
        "shortlist_count": len(flat_items),
        "tech_shortlist_count": len(tech_items),
        "investment_shortlist_count": len(investment_items),
        "max_items": max_items,
        "content_tracks_policy": content_tracks,
        "daily_ratio_policy": content_tracks.get("daily_ratio_policy", {}),
        "previous_market_policy": previous_market_policy,
        "source_errors": source_errors,
        "warnings": warnings,
        "tracks": {
            "tech": {
                "max_items": tech_max_items,
                "items": [public_item(item) for item in tech_items],
            },
            "investment": {
                "max_items": investment_max_items,
                "items": [public_item(item) for item in investment_items],
            },
        },
        "items": [public_item(item) for item in flat_items],
    }


def main() -> int:
    args = parse_args()
    input_files = args.input_file or DEFAULT_INPUT_FILES
    payload = build_shortlist(
        input_files,
        args.audience_profile,
        args.max_items,
        args.tech_max_items,
        args.investment_max_items,
    )
    args.output_file.parent.mkdir(parents=True, exist_ok=True)
    args.output_file.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        "Wrote News Daily shortlist "
        f"({payload['tech_shortlist_count']} tech, "
        f"{payload['investment_shortlist_count']} investment): {args.output_file}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
