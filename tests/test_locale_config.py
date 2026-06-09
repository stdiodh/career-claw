#!/usr/bin/env python3
"""Contract tests for locale-aware runtime path resolution."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "locale_config.py"


def load_locale_config():
    spec = importlib.util.spec_from_file_location("locale_config", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load locale_config.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


locale_config = load_locale_config()


def assert_equal(actual: object, expected: object) -> None:
    if actual != expected:
        raise AssertionError(f"Expected {expected!r}, got {actual!r}")


def test_default_enabled_locale_is_ko_kr() -> None:
    assert_equal(locale_config.enabled_locales({}), ["ko-KR"])


def test_enabled_locale_list_is_deduplicated() -> None:
    env = {"CAREER_FEED_ENABLED_LOCALES": "ko-KR,en-US,ko-KR"}
    assert_equal(locale_config.enabled_locales(env), ["ko-KR", "en-US"])


def test_unsupported_locale_fails() -> None:
    try:
        locale_config.parse_locale_list("ko-KR,ja-JP")
    except ValueError as exc:
        if "unsupported locale: ja-JP" not in str(exc):
            raise AssertionError(f"Unexpected error: {exc}") from exc
        return
    raise AssertionError("Unsupported locale should fail")


def test_ko_kr_backend_daily_paths_include_legacy_mirrors() -> None:
    runtime = locale_config.runtime_for("ko-KR", "backend-daily")
    assert_equal(runtime.config_file, Path("configs/locales/ko-KR/sources.json"))
    assert_equal(runtime.report_file, Path("reports/briefs/ko-KR/backend-daily.md"))
    assert_equal(runtime.candidate_dir, Path("reports/candidates/ko-KR"))
    assert_equal(runtime.ops_dir, Path("reports/ops/ko-KR"))
    assert_equal(runtime.legacy_report_file, "reports/briefs/kr-tech-daily.md")
    assert_equal(
        runtime.legacy_validation_report,
        "reports/ops/backend-daily-validation-report.md",
    )


def test_en_us_news_daily_paths_do_not_include_legacy_mirrors() -> None:
    runtime = locale_config.runtime_for("en-US", "news-daily")
    assert_equal(runtime.config_file, Path("configs/locales/en-US/sources.json"))
    assert_equal(runtime.report_file, Path("reports/briefs/en-US/news-daily.md"))
    assert_equal(runtime.candidate_dir, Path("reports/candidates/en-US"))
    assert_equal(runtime.ops_dir, Path("reports/ops/en-US"))
    assert_equal(runtime.legacy_report_file, "")
    assert_equal(runtime.legacy_validation_report, "")


def main() -> int:
    test_default_enabled_locale_is_ko_kr()
    test_enabled_locale_list_is_deduplicated()
    test_unsupported_locale_fails()
    test_ko_kr_backend_daily_paths_include_legacy_mirrors()
    test_en_us_news_daily_paths_do_not_include_legacy_mirrors()
    print("Locale config tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
