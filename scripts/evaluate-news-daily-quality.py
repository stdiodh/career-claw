#!/usr/bin/env python3
"""Evaluate News Daily output quality for operations review."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


KST = ZoneInfo("Asia/Seoul")
DEFAULT_REPORT_FILE = Path("reports/briefs/kr-tech-news-daily.md")
DEFAULT_SHORTLIST_FILE = Path("reports/candidates/kr-tech-news-shortlist.json")
DEFAULT_TOKEN_BUDGET_FILE = Path("reports/ops/news-daily-token-budget.json")
DEFAULT_OUTPUT_JSON = Path("reports/ops/news-daily-quality-report.json")
DEFAULT_OUTPUT_MD = Path("reports/ops/news-daily-quality-report.md")
TARGET_TOTAL_ITEMS = 4
TARGET_TECH_ITEMS = 3
TARGET_INVESTMENT_ITEMS = 1

INVESTMENT_ADVICE_PATTERNS = [
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
PRICE_MOVE_PATTERNS = [
    r"주가",
    r"급등",
    r"급락",
    r"상한가",
    r"하한가",
]
TECH_CONTEXT_PATTERNS = [
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
STRONG_ACTION_PATTERNS = [
    r"작은\s*코드\s*실험",
    r"아키텍처\s*메모",
    r"기업\s*실적",
    r"지표\s*확인",
    r"\bTIL\b",
]
OK_ACTION_PATTERNS = [
    r"공식\s*문서\s*(?:보기|확인|정리)",
    r"포트폴리오",
    r"면접\s*질문",
    r"GitHub\s*issue",
]
WEAK_ACTION_PATTERNS = [
    r"읽어본다",
    r"관심을\s*가져본다",
    r"공부해본다",
    r"살펴본다",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_FILE)
    parser.add_argument("--shortlist", type=Path, default=DEFAULT_SHORTLIST_FILE)
    parser.add_argument("--token-budget", type=Path, default=DEFAULT_TOKEN_BUDGET_FILE)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 when the recommendation is tune.",
    )
    return parser.parse_args()


def now_kst() -> str:
    return datetime.now(tz=KST).strftime("%Y-%m-%d %H:%M:%S KST")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def read_json_object(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def matches_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def section_body(markdown: str, heading: str) -> str:
    pattern = re.compile(
        rf"^##\s+{re.escape(heading)}\s*$([\s\S]*?)(?=^##\s+|\Z)",
        flags=re.MULTILINE,
    )
    match = pattern.search(markdown)
    return match.group(1).strip() if match else ""


def section_item_count(markdown: str, heading: str) -> int:
    body = section_body(markdown, heading)
    if not body:
        return 0
    return len(re.findall(r"^###\s+\d+\.\s+", body, flags=re.MULTILINE))


def bullet_field_value(markdown: str, field: str) -> str:
    match = re.search(
        rf"^\s*-\s*{re.escape(field)}\s*:\s*(.+?)\s*$",
        markdown,
        flags=re.MULTILINE,
    )
    return match.group(1).strip() if match else ""


def growth_score(markdown: str) -> int:
    raw_score = bullet_field_value(section_body(markdown, "오늘의 성장 판단"), "도움 점수")
    match = re.search(r"[1-5]", raw_score)
    return int(match.group(0)) if match else 0


def growth_action_quality(action: str) -> str:
    if not action:
        return "missing"
    if matches_any(action, WEAK_ACTION_PATTERNS):
        return "weak"
    if matches_any(action, STRONG_ACTION_PATTERNS):
        return "strong"
    if matches_any(action, OK_ACTION_PATTERNS):
        return "ok"
    return "weak"


def token_efficiency(budget: dict[str, object]) -> str:
    explicit = budget.get("token_budget_status")
    if explicit in {"ok", "watch", "too_large"}:
        return str(explicit)
    estimated = int(budget.get("estimated_prompt_tokens_rough", 0) or 0)
    shortlist_count = int(budget.get("shortlist_count", 0) or 0)
    if estimated > 4500 or shortlist_count > 12:
        return "too_large"
    if estimated > 3500 or shortlist_count > 8:
        return "watch"
    return "ok"


def price_move_only_risk(investment_body: str) -> bool:
    if not investment_body:
        return False
    has_price_move = matches_any(investment_body, PRICE_MOVE_PATTERNS)
    has_tech_context = matches_any(investment_body, TECH_CONTEXT_PATTERNS)
    return has_price_move and not has_tech_context


def quality_score(
    *,
    total_item_count: int,
    tech_item_count: int,
    investment_item_count: int,
    bridge_present: bool,
    growth_score_value: int,
    growth_action_present: bool,
    growth_action_quality_value: str,
    investment_advice_risk: bool,
    price_move_only_risk_value: bool,
) -> int:
    if investment_advice_risk or not growth_action_present:
        return 1
    if total_item_count == 0:
        return 1
    if growth_action_quality_value == "weak" or price_move_only_risk_value:
        return 2
    if tech_item_count >= 2 and investment_item_count >= 1 and not bridge_present:
        return 2

    score = 3 if tech_item_count >= 1 else 2
    if (
        2 <= tech_item_count <= 3
        and investment_item_count == 1
        and bridge_present
        and growth_action_quality_value in {"ok", "strong"}
    ):
        score = 4
    if (
        score >= 4
        and growth_score_value >= 5
        and growth_action_quality_value == "strong"
    ):
        score = 5
    return score


def recommendation(
    *,
    quality_score_value: int,
    investment_advice_risk: bool,
    growth_action_present: bool,
    token_efficiency_value: str,
    target_ratio_met: bool,
    total_item_count: int,
) -> str:
    if quality_score_value <= 1 or investment_advice_risk or not growth_action_present:
        return "tune"
    if quality_score_value == 2:
        return "review"
    if token_efficiency_value in {"watch", "too_large"}:
        return "review"
    if not target_ratio_met and total_item_count >= 3:
        return "review"
    return "accept"


def build_report(markdown: str, budget: dict[str, object]) -> dict[str, object]:
    tech_item_count = section_item_count(markdown, "새 기술 이야기")
    investment_body = section_body(markdown, "주식/투자 이야기")
    investment_item_count = section_item_count(markdown, "주식/투자 이야기")
    total_item_count = tech_item_count + investment_item_count
    bridge_present = bool(section_body(markdown, "기술과 시장 연결"))
    growth_score_value = growth_score(markdown)
    growth_action = bullet_field_value(
        section_body(markdown, "오늘의 성장 판단"),
        "오늘 할 일 1개",
    )
    growth_action_quality_value = growth_action_quality(growth_action)
    growth_action_present = growth_action_quality_value != "missing"
    investment_advice_risk = matches_any(markdown, INVESTMENT_ADVICE_PATTERNS)
    price_move_only_risk_value = price_move_only_risk(investment_body)
    target_ratio_met = (
        total_item_count == TARGET_TOTAL_ITEMS
        and tech_item_count == TARGET_TECH_ITEMS
        and investment_item_count == TARGET_INVESTMENT_ITEMS
    )
    token_efficiency_value = token_efficiency(budget)

    warnings: list[str] = []
    if not target_ratio_met and total_item_count >= 3:
        warnings.append("target ratio not met")
    if investment_advice_risk:
        warnings.append("investment advice wording risk")
    if price_move_only_risk_value:
        warnings.append("price move only investment risk")
    if growth_action_quality_value in {"missing", "weak"}:
        warnings.append("growth action is missing or weak")
    if token_efficiency_value != "ok":
        warnings.append(f"token efficiency is {token_efficiency_value}")

    quality_score_value = quality_score(
        total_item_count=total_item_count,
        tech_item_count=tech_item_count,
        investment_item_count=investment_item_count,
        bridge_present=bridge_present,
        growth_score_value=growth_score_value,
        growth_action_present=growth_action_present,
        growth_action_quality_value=growth_action_quality_value,
        investment_advice_risk=investment_advice_risk,
        price_move_only_risk_value=price_move_only_risk_value,
    )
    recommendation_value = recommendation(
        quality_score_value=quality_score_value,
        investment_advice_risk=investment_advice_risk,
        growth_action_present=growth_action_present,
        token_efficiency_value=token_efficiency_value,
        target_ratio_met=target_ratio_met,
        total_item_count=total_item_count,
    )

    return {
        "generated_at_kst": now_kst(),
        "quality_score": quality_score_value,
        "tech_item_count": tech_item_count,
        "investment_item_count": investment_item_count,
        "total_item_count": total_item_count,
        "target_ratio_met": target_ratio_met,
        "bridge_present": bridge_present,
        "growth_score": growth_score_value,
        "growth_action_present": growth_action_present,
        "growth_action_quality": growth_action_quality_value,
        "investment_advice_risk": investment_advice_risk,
        "price_move_only_risk": price_move_only_risk_value,
        "token_efficiency": token_efficiency_value,
        "warnings": warnings,
        "recommendation": recommendation_value,
    }


def markdown_report(report: dict[str, object]) -> str:
    warnings = report.get("warnings", [])
    warning_lines = "\n".join(f"- {warning}" for warning in warnings) if warnings else "- none"
    return (
        "# News Daily Quality Report\n\n"
        f"- quality_score: {report['quality_score']}\n"
        f"- recommendation: {report['recommendation']}\n"
        f"- total_item_count: {report['total_item_count']}\n"
        f"- tech_item_count: {report['tech_item_count']}\n"
        f"- investment_item_count: {report['investment_item_count']}\n"
        f"- target_ratio_met: {report['target_ratio_met']}\n"
        f"- bridge_present: {report['bridge_present']}\n"
        f"- growth_score: {report['growth_score']}\n"
        f"- growth_action_quality: {report['growth_action_quality']}\n"
        f"- investment_advice_risk: {report['investment_advice_risk']}\n"
        f"- price_move_only_risk: {report['price_move_only_risk']}\n"
        f"- token_efficiency: {report['token_efficiency']}\n\n"
        "## Warnings\n\n"
        f"{warning_lines}\n"
    )


def main() -> int:
    args = parse_args()
    markdown = read_text(args.report)
    budget = read_json_object(args.token_budget)
    report = build_report(markdown, budget)

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    args.output_md.write_text(markdown_report(report), encoding="utf-8")
    print(
        "Wrote News Daily quality report "
        f"(score={report['quality_score']}, recommendation={report['recommendation']}): "
        f"{args.output_json}"
    )
    if args.strict and report["recommendation"] == "tune":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
