#!/usr/bin/env python3
"""Resolve locale-aware Career Feed runtime paths."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


DEFAULT_ENABLED_LOCALES = "ko-KR"
DEFAULT_LOCALE = "ko-KR"
SUPPORTED_LOCALES = {"ko-KR", "en-US"}
SUPPORTED_FEEDS = {"backend-daily", "news-daily", "backend-career-weekly"}


@dataclass(frozen=True)
class LocaleRuntime:
    locale: str
    locale_env: str
    feed: str
    config_file: Path
    audience_file: Path
    prompt_file: Path
    candidate_dir: Path
    brief_dir: Path
    ops_dir: Path
    report_file: Path
    codex_summary_file: Path
    validation_report: Path
    run_summary_json: Path
    run_summary_md: Path
    legacy_report_file: str
    legacy_codex_summary_file: str
    legacy_validation_report: str


def env_value(env: Mapping[str, str], name: str, default: str) -> str:
    value = env.get(name, "")
    return value.strip() or default


def parse_locale_list(raw: str) -> list[str]:
    seen: set[str] = set()
    locales: list[str] = []
    for item in raw.split(","):
        locale = item.strip()
        if not locale:
            continue
        if locale not in SUPPORTED_LOCALES:
            raise ValueError(f"unsupported locale: {locale}")
        if locale not in seen:
            locales.append(locale)
            seen.add(locale)
    if not locales:
        locales = [DEFAULT_LOCALE]
    return locales


def enabled_locales(env: Mapping[str, str]) -> list[str]:
    return parse_locale_list(
        env_value(env, "CAREER_FEED_ENABLED_LOCALES", DEFAULT_ENABLED_LOCALES)
    )


def locale_env_name(locale: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", locale).upper()


def prompt_filename(feed: str) -> str:
    if feed == "backend-daily":
        return "backend-daily.md"
    if feed == "news-daily":
        return "news-daily.md"
    raise ValueError(f"unsupported prompt feed: {feed}")


def legacy_report(feed: str, locale: str) -> str:
    if locale != "ko-KR":
        return ""
    return {
        "backend-daily": "reports/briefs/kr-tech-daily.md",
        "news-daily": "reports/briefs/kr-tech-news-daily.md",
        "backend-career-weekly": "reports/briefs/kr-backend-career-weekly.md",
    }.get(feed, "")


def legacy_codex_summary(feed: str, locale: str) -> str:
    if locale != "ko-KR":
        return ""
    return {
        "backend-daily": "reports/briefs/kr-tech-daily-codex-summary.md",
        "news-daily": "reports/briefs/kr-tech-news-daily-codex-summary.md",
    }.get(feed, "")


def legacy_validation_report(feed: str, locale: str) -> str:
    if locale != "ko-KR":
        return ""
    return {
        "backend-daily": "reports/ops/backend-daily-validation-report.md",
        "news-daily": "reports/ops/news-daily-validation-report.md",
    }.get(feed, "")


def report_name(feed: str) -> str:
    return {
        "backend-daily": "backend-daily.md",
        "news-daily": "news-daily.md",
        "backend-career-weekly": "backend-career-weekly.md",
    }[feed]


def runtime_for(locale: str, feed: str) -> LocaleRuntime:
    if locale not in SUPPORTED_LOCALES:
        raise ValueError(f"unsupported locale: {locale}")
    if feed not in SUPPORTED_FEEDS:
        raise ValueError(f"unsupported feed: {feed}")

    locale_dir = Path("configs/locales") / locale
    prompt_file = (
        locale_dir / "prompts" / prompt_filename(feed)
        if feed != "backend-career-weekly"
        else Path("")
    )
    candidate_dir = Path("reports/candidates") / locale
    brief_dir = Path("reports/briefs") / locale
    ops_dir = Path("reports/ops") / locale
    report_file = brief_dir / report_name(feed)

    return LocaleRuntime(
        locale=locale,
        locale_env=locale_env_name(locale),
        feed=feed,
        config_file=locale_dir / "sources.json",
        audience_file=locale_dir / "audience-profile.json",
        prompt_file=prompt_file,
        candidate_dir=candidate_dir,
        brief_dir=brief_dir,
        ops_dir=ops_dir,
        report_file=report_file,
        codex_summary_file=brief_dir / f"{feed}-codex-summary.md",
        validation_report=ops_dir / f"{feed}-validation-report.md",
        run_summary_json=ops_dir / f"{feed}-run-summary.json",
        run_summary_md=ops_dir / f"{feed}-run-summary.md",
        legacy_report_file=legacy_report(feed, locale),
        legacy_codex_summary_file=legacy_codex_summary(feed, locale),
        legacy_validation_report=legacy_validation_report(feed, locale),
    )


def write_github_output(values: Mapping[str, object], output_path: str) -> None:
    if not output_path:
        printable = {key: str(value) for key, value in values.items()}
        print(json.dumps(printable, ensure_ascii=False, indent=2))
        return
    with Path(output_path).open("a", encoding="utf-8") as output:
        for key, value in values.items():
            output.write(f"{key}={value}\n")


def command_matrix(args: argparse.Namespace) -> int:
    locales = enabled_locales(os.environ)
    write_github_output(
        {
            "locales_json": json.dumps(locales),
            "default_locale": env_value(
                os.environ,
                "CAREER_FEED_DEFAULT_LOCALE",
                DEFAULT_LOCALE,
            ),
        },
        args.github_output,
    )
    return 0


def command_paths(args: argparse.Namespace) -> int:
    runtime = runtime_for(args.locale, args.feed)
    values = {
        "locale": runtime.locale,
        "locale_env": runtime.locale_env,
        "feed": runtime.feed,
        "config_file": runtime.config_file,
        "audience_file": runtime.audience_file,
        "prompt_file": runtime.prompt_file,
        "candidate_dir": runtime.candidate_dir,
        "brief_dir": runtime.brief_dir,
        "ops_dir": runtime.ops_dir,
        "report_file": runtime.report_file,
        "codex_summary_file": runtime.codex_summary_file,
        "validation_report": runtime.validation_report,
        "run_summary_json": runtime.run_summary_json,
        "run_summary_md": runtime.run_summary_md,
        "legacy_report_file": runtime.legacy_report_file,
        "legacy_codex_summary_file": runtime.legacy_codex_summary_file,
        "legacy_validation_report": runtime.legacy_validation_report,
    }
    write_github_output(values, args.github_output)
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    matrix = subparsers.add_parser("matrix")
    matrix.add_argument("--github-output", default=os.environ.get("GITHUB_OUTPUT", ""))

    paths = subparsers.add_parser("paths")
    paths.add_argument("--locale", required=True)
    paths.add_argument("--feed", required=True, choices=sorted(SUPPORTED_FEEDS))
    paths.add_argument("--github-output", default=os.environ.get("GITHUB_OUTPUT", ""))

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.command == "matrix":
            return command_matrix(args)
        if args.command == "paths":
            return command_paths(args)
    except ValueError as exc:
        print(f"locale config error: {exc}", file=sys.stderr)
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
