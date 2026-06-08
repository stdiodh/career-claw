#!/usr/bin/env python3
"""Tests for the GitHub Actions runtime gate."""

from __future__ import annotations

import importlib.util
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "should-run-now.py"


def load_runtime_gate():
    spec = importlib.util.spec_from_file_location("should_run_now", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load should-run-now.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


gate = load_runtime_gate()


def utc_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def test_default_timezone_is_asia_seoul() -> None:
    config = gate.read_config({})
    assert config.timezone_name == "Asia/Seoul"
    assert str(config.timezone) == "Asia/Seoul"


def test_hh_mm_time_parses() -> None:
    parsed = gate.parse_time("09:05")
    assert parsed.hour == 9
    assert parsed.minute == 5


def test_invalid_time_format_fails() -> None:
    for value in ["9:00", "24:00", "09:60", "abc"]:
        try:
            gate.parse_time(value)
        except ValueError as exc:
            assert "HH:MM" in str(exc) or "00:00 and 23:59" in str(exc)
        else:
            raise AssertionError(f"Expected invalid time to fail: {value}")


def test_backend_daily_runs_inside_target_window() -> None:
    decision = gate.evaluate_gate(
        "backend_daily",
        {"CAREER_FEED_BACKEND_DAILY_TIME": "09:00"},
        event_name="schedule",
        now_utc=utc_datetime("2026-06-08T00:05:00Z"),
    )
    assert decision.should_run is True
    assert decision.reason == "scheduled_window_match"
    assert decision.local_date == "2026-06-08"


def test_backend_daily_skips_outside_target_window() -> None:
    decision = gate.evaluate_gate(
        "backend_daily",
        {"CAREER_FEED_BACKEND_DAILY_TIME": "09:00"},
        event_name="schedule",
        now_utc=utc_datetime("2026-06-08T01:05:00Z"),
    )
    assert decision.should_run is False
    assert decision.reason == "outside_schedule_window"


def test_career_weekly_runs_on_configured_weekday() -> None:
    decision = gate.evaluate_gate(
        "career_weekly",
        {
            "CAREER_FEED_CAREER_WEEKLY_DAY": "MON",
            "CAREER_FEED_CAREER_WEEKLY_TIME": "09:00",
        },
        event_name="schedule",
        now_utc=utc_datetime("2026-06-08T00:05:00Z"),
    )
    assert decision.should_run is True
    assert decision.target_weekday == "MON"


def test_career_weekly_skips_when_weekday_differs() -> None:
    decision = gate.evaluate_gate(
        "career_weekly",
        {
            "CAREER_FEED_CAREER_WEEKLY_DAY": "MON",
            "CAREER_FEED_CAREER_WEEKLY_TIME": "09:00",
        },
        event_name="schedule",
        now_utc=utc_datetime("2026-06-09T00:05:00Z"),
    )
    assert decision.should_run is False
    assert decision.reason == "weekly_day_mismatch"


def test_manual_dispatch_always_runs_with_valid_config() -> None:
    decision = gate.evaluate_gate(
        "backend_daily",
        {"CAREER_FEED_BACKEND_DAILY_TIME": "09:00"},
        event_name="workflow_dispatch",
        now_utc=utc_datetime("2026-06-08T01:05:00Z"),
    )
    assert decision.should_run is True
    assert decision.reason == "manual_dispatch"


def test_invalid_timezone_returns_clear_skip_reason() -> None:
    decision = gate.evaluate_gate(
        "backend_daily",
        {"CAREER_FEED_TIMEZONE": "Mars/Base"},
        event_name="schedule",
        now_utc=utc_datetime("2026-06-08T00:05:00Z"),
    )
    assert decision.should_run is False
    assert decision.reason.startswith("invalid_config:")
    assert "unknown timezone" in decision.reason


def test_discord_delivery_enabled_defaults_to_false() -> None:
    config = gate.read_config({})
    assert config.discord_delivery_enabled is False
