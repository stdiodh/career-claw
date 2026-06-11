#!/usr/bin/env python3
"""Decide whether a scheduled Career Feed workflow should continue."""

from __future__ import annotations

import argparse
import os
import re
from dataclasses import dataclass
from datetime import datetime, time, timedelta, timezone
from typing import Mapping
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


DEFAULT_TIMEZONE = "Asia/Seoul"
DEFAULT_BACKEND_DAILY_TIME = "09:00"
DEFAULT_NEWS_DAILY_TIME = "09:05"
DEFAULT_CAREER_WEEKLY_DAY = "MON"
DEFAULT_CAREER_WEEKLY_TIME = "09:00"
DEFAULT_OSS_RECENT_DAYS = 30
DEFAULT_SCHEDULE_ENABLED = False
DEFAULT_DISCORD_DELIVERY_ENABLED = False
TOLERANCE_MINUTES = 30
DAILY_WEEKDAYS = {0, 1, 2, 3, 4}
WEEKDAYS = {
    "MON": 0,
    "TUE": 1,
    "WED": 2,
    "THU": 3,
    "FRI": 4,
    "SAT": 5,
    "SUN": 6,
}
WORKFLOWS = {"backend_daily", "news_daily", "career_weekly"}


@dataclass(frozen=True)
class RuntimeConfig:
    schedule_enabled: bool
    timezone_name: str
    timezone: ZoneInfo
    backend_daily_time: time
    news_daily_time: time
    career_weekly_day: str
    career_weekly_time: time
    oss_recent_days: int
    discord_delivery_enabled: bool


@dataclass(frozen=True)
class GateDecision:
    should_run: bool
    reason: str
    schedule_enabled: bool
    timezone_name: str
    target_time: str
    local_now: str
    local_date: str
    discord_delivery_enabled: bool
    oss_recent_days: int
    target_weekday: str = ""


def parse_time(value: str, *, name: str = "time") -> time:
    raw = value.strip()
    if not re.fullmatch(r"\d{2}:\d{2}", raw):
        raise ValueError(f"{name} must use HH:MM format: {value!r}")
    hour_text, minute_text = raw.split(":", maxsplit=1)
    hour = int(hour_text)
    minute = int(minute_text)
    if hour > 23 or minute > 59:
        raise ValueError(f"{name} must be between 00:00 and 23:59: {value!r}")
    return time(hour=hour, minute=minute)


def format_time(value: time) -> str:
    return f"{value.hour:02d}:{value.minute:02d}"


def parse_weekday(value: str, *, name: str = "weekday") -> str:
    normalized = value.strip().upper()
    if normalized not in WEEKDAYS:
        allowed = ", ".join(WEEKDAYS)
        raise ValueError(f"{name} must be one of {allowed}: {value!r}")
    return normalized


def resolve_timezone(value: str) -> ZoneInfo:
    timezone_name = value.strip()
    if not timezone_name:
        timezone_name = DEFAULT_TIMEZONE
    try:
        return ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(f"unknown timezone: {timezone_name}") from exc


def parse_bool(value: str, *, name: str) -> bool:
    normalized = value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise ValueError(f"{name} must be true or false: {value!r}")


def parse_positive_int(value: str, *, name: str) -> int:
    raw = value.strip()
    try:
        parsed = int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be a positive integer: {value!r}") from exc
    if parsed < 1:
        raise ValueError(f"{name} must be a positive integer: {value!r}")
    return parsed


def env_value(env: Mapping[str, str], name: str, default: str) -> str:
    value = env.get(name, "")
    if not value.strip():
        return default
    return value


def read_config(env: Mapping[str, str]) -> RuntimeConfig:
    timezone_name = env_value(env, "CAREER_FEED_TIMEZONE", DEFAULT_TIMEZONE).strip()
    resolved_timezone = resolve_timezone(timezone_name)
    return RuntimeConfig(
        schedule_enabled=parse_bool(
            env_value(
                env,
                "CAREER_FEED_SCHEDULE_ENABLED",
                str(DEFAULT_SCHEDULE_ENABLED).lower(),
            ),
            name="CAREER_FEED_SCHEDULE_ENABLED",
        ),
        timezone_name=timezone_name,
        timezone=resolved_timezone,
        backend_daily_time=parse_time(
            env_value(env, "CAREER_FEED_BACKEND_DAILY_TIME", DEFAULT_BACKEND_DAILY_TIME),
            name="CAREER_FEED_BACKEND_DAILY_TIME",
        ),
        news_daily_time=parse_time(
            env_value(env, "CAREER_FEED_NEWS_DAILY_TIME", DEFAULT_NEWS_DAILY_TIME),
            name="CAREER_FEED_NEWS_DAILY_TIME",
        ),
        career_weekly_day=parse_weekday(
            env_value(env, "CAREER_FEED_CAREER_WEEKLY_DAY", DEFAULT_CAREER_WEEKLY_DAY),
            name="CAREER_FEED_CAREER_WEEKLY_DAY",
        ),
        career_weekly_time=parse_time(
            env_value(env, "CAREER_FEED_CAREER_WEEKLY_TIME", DEFAULT_CAREER_WEEKLY_TIME),
            name="CAREER_FEED_CAREER_WEEKLY_TIME",
        ),
        oss_recent_days=parse_positive_int(
            env_value(
                env,
                "CAREER_FEED_OSS_RECENT_DAYS",
                str(DEFAULT_OSS_RECENT_DAYS),
            ),
            name="CAREER_FEED_OSS_RECENT_DAYS",
        ),
        discord_delivery_enabled=parse_bool(
            env_value(
                env,
                "CAREER_FEED_DISCORD_DELIVERY_ENABLED",
                str(DEFAULT_DISCORD_DELIVERY_ENABLED).lower(),
            ),
            name="CAREER_FEED_DISCORD_DELIVERY_ENABLED",
        ),
    )


def target_for_workflow(workflow: str, config: RuntimeConfig) -> tuple[time, str]:
    if workflow == "backend_daily":
        return config.backend_daily_time, ""
    if workflow == "news_daily":
        return config.news_daily_time, ""
    if workflow == "career_weekly":
        return config.career_weekly_time, config.career_weekly_day
    raise ValueError(f"unsupported workflow: {workflow}")


def raw_target_for_workflow(workflow: str, env: Mapping[str, str]) -> tuple[str, str]:
    if workflow == "backend_daily":
        return env_value(env, "CAREER_FEED_BACKEND_DAILY_TIME", DEFAULT_BACKEND_DAILY_TIME), ""
    if workflow == "news_daily":
        return env_value(env, "CAREER_FEED_NEWS_DAILY_TIME", DEFAULT_NEWS_DAILY_TIME), ""
    if workflow == "career_weekly":
        return (
            env_value(env, "CAREER_FEED_CAREER_WEEKLY_TIME", DEFAULT_CAREER_WEEKLY_TIME),
            env_value(env, "CAREER_FEED_CAREER_WEEKLY_DAY", DEFAULT_CAREER_WEEKLY_DAY),
        )
    raise ValueError(f"unsupported workflow: {workflow}")


def format_local_now(value: datetime) -> str:
    return value.strftime("%Y-%m-%d %H:%M:%S %Z")


def target_candidates(local_now: datetime, target: time) -> list[datetime]:
    today_target = datetime.combine(local_now.date(), target, tzinfo=local_now.tzinfo)
    return [today_target, today_target - timedelta(days=1)]


def find_window_target(
    local_now: datetime,
    target: time,
    tolerance: timedelta,
) -> tuple[datetime | None, timedelta | None]:
    for candidate in target_candidates(local_now, target):
        delta = local_now - candidate
        if timedelta(0) <= delta < tolerance:
            return candidate, delta
    return None, None


def make_decision(
    workflow: str,
    config: RuntimeConfig,
    *,
    event_name: str,
    now_utc: datetime,
    tolerance_minutes: int = TOLERANCE_MINUTES,
) -> GateDecision:
    if workflow not in WORKFLOWS:
        raise ValueError(f"unsupported workflow: {workflow}")
    if now_utc.tzinfo is None:
        now_utc = now_utc.replace(tzinfo=timezone.utc)
    now_utc = now_utc.astimezone(timezone.utc)
    local_now = now_utc.astimezone(config.timezone)
    target_time, target_weekday = target_for_workflow(workflow, config)
    target_time_text = format_time(target_time)
    local_now_text = format_local_now(local_now)

    if event_name == "workflow_dispatch":
        return GateDecision(
            should_run=True,
            reason="manual_dispatch",
            schedule_enabled=config.schedule_enabled,
            timezone_name=config.timezone_name,
            target_time=target_time_text,
            local_now=local_now_text,
            local_date=local_now.date().isoformat(),
            discord_delivery_enabled=config.discord_delivery_enabled,
            oss_recent_days=config.oss_recent_days,
            target_weekday=target_weekday,
        )

    if not config.schedule_enabled:
        return GateDecision(
            should_run=False,
            reason="schedule_disabled",
            schedule_enabled=config.schedule_enabled,
            timezone_name=config.timezone_name,
            target_time=target_time_text,
            local_now=local_now_text,
            local_date=local_now.date().isoformat(),
            discord_delivery_enabled=config.discord_delivery_enabled,
            oss_recent_days=config.oss_recent_days,
            target_weekday=target_weekday,
        )

    window_target, _delta = find_window_target(
        local_now,
        target_time,
        timedelta(minutes=tolerance_minutes),
    )
    if window_target is None:
        return GateDecision(
            should_run=False,
            reason="outside_schedule_window",
            schedule_enabled=config.schedule_enabled,
            timezone_name=config.timezone_name,
            target_time=target_time_text,
            local_now=local_now_text,
            local_date=local_now.date().isoformat(),
            discord_delivery_enabled=config.discord_delivery_enabled,
            oss_recent_days=config.oss_recent_days,
            target_weekday=target_weekday,
        )

    target_date = window_target.date().isoformat()
    target_weekday_index = window_target.weekday()
    if workflow in {"backend_daily", "news_daily"} and target_weekday_index not in DAILY_WEEKDAYS:
        return GateDecision(
            should_run=False,
            reason="daily_weekend",
            schedule_enabled=config.schedule_enabled,
            timezone_name=config.timezone_name,
            target_time=target_time_text,
            local_now=local_now_text,
            local_date=target_date,
            discord_delivery_enabled=config.discord_delivery_enabled,
            oss_recent_days=config.oss_recent_days,
            target_weekday=target_weekday,
        )

    if workflow == "career_weekly" and target_weekday_index != WEEKDAYS[target_weekday]:
        return GateDecision(
            should_run=False,
            reason="weekly_day_mismatch",
            schedule_enabled=config.schedule_enabled,
            timezone_name=config.timezone_name,
            target_time=target_time_text,
            local_now=local_now_text,
            local_date=target_date,
            discord_delivery_enabled=config.discord_delivery_enabled,
            oss_recent_days=config.oss_recent_days,
            target_weekday=target_weekday,
        )

    return GateDecision(
        should_run=True,
        reason="scheduled_window_match",
        schedule_enabled=config.schedule_enabled,
        timezone_name=config.timezone_name,
        target_time=target_time_text,
        local_now=local_now_text,
        local_date=target_date,
        discord_delivery_enabled=config.discord_delivery_enabled,
        oss_recent_days=config.oss_recent_days,
        target_weekday=target_weekday,
    )


def parse_schedule_enabled(env: Mapping[str, str]) -> bool:
    return parse_bool(
        env_value(
            env,
            "CAREER_FEED_SCHEDULE_ENABLED",
            str(DEFAULT_SCHEDULE_ENABLED).lower(),
        ),
        name="CAREER_FEED_SCHEDULE_ENABLED",
    )


def schedule_disabled_decision(
    workflow: str,
    env: Mapping[str, str],
    now_utc: datetime,
) -> GateDecision:
    if now_utc.tzinfo is None:
        now_utc = now_utc.replace(tzinfo=timezone.utc)
    now_utc = now_utc.astimezone(timezone.utc)
    target_time, target_weekday = raw_target_for_workflow(workflow, env)
    timezone_name = env_value(env, "CAREER_FEED_TIMEZONE", DEFAULT_TIMEZONE)
    try:
        local_now = now_utc.astimezone(resolve_timezone(timezone_name))
    except ValueError:
        local_now = now_utc
    return GateDecision(
        should_run=False,
        reason="schedule_disabled",
        schedule_enabled=False,
        timezone_name=timezone_name,
        target_time=target_time,
        local_now=format_local_now(local_now),
        local_date=local_now.date().isoformat(),
        discord_delivery_enabled=DEFAULT_DISCORD_DELIVERY_ENABLED,
        oss_recent_days=DEFAULT_OSS_RECENT_DAYS,
        target_weekday=target_weekday,
    )


def invalid_config_decision(
    workflow: str,
    env: Mapping[str, str],
    message: str,
    now_utc: datetime,
) -> GateDecision:
    if now_utc.tzinfo is None:
        now_utc = now_utc.replace(tzinfo=timezone.utc)
    now_utc = now_utc.astimezone(timezone.utc)
    target_time, target_weekday = raw_target_for_workflow(workflow, env)
    return GateDecision(
        should_run=False,
        reason=f"invalid_config:{message}",
        schedule_enabled=DEFAULT_SCHEDULE_ENABLED,
        timezone_name=env_value(env, "CAREER_FEED_TIMEZONE", DEFAULT_TIMEZONE),
        target_time=target_time,
        local_now=now_utc.strftime("%Y-%m-%d %H:%M:%S UTC"),
        local_date=now_utc.date().isoformat(),
        discord_delivery_enabled=DEFAULT_DISCORD_DELIVERY_ENABLED,
        oss_recent_days=DEFAULT_OSS_RECENT_DAYS,
        target_weekday=target_weekday,
    )


def evaluate_gate(
    workflow: str,
    env: Mapping[str, str],
    *,
    event_name: str = "",
    now_utc: datetime | None = None,
) -> GateDecision:
    if now_utc is None:
        now_utc = datetime.now(tz=timezone.utc)
    try:
        schedule_enabled = parse_schedule_enabled(env)
        if event_name != "workflow_dispatch" and not schedule_enabled:
            return schedule_disabled_decision(workflow, env, now_utc)
        config = read_config(env)
        return make_decision(
            workflow,
            config,
            event_name=event_name,
            now_utc=now_utc,
        )
    except ValueError as exc:
        return invalid_config_decision(workflow, env, str(exc), now_utc)


def write_github_output(decision: GateDecision, output_path: str) -> None:
    if not output_path:
        return
    lines = {
        "should_run": str(decision.should_run).lower(),
        "reason": decision.reason,
        "schedule_enabled": str(decision.schedule_enabled).lower(),
        "timezone": decision.timezone_name,
        "target_time": decision.target_time,
        "local_now": decision.local_now,
        "local_date": decision.local_date,
        "discord_delivery_enabled": str(decision.discord_delivery_enabled).lower(),
        "oss_recent_days": str(decision.oss_recent_days),
        "target_weekday": decision.target_weekday,
    }
    with open(output_path, "a", encoding="utf-8") as output_file:
        for key, value in lines.items():
            output_file.write(f"{key}={value}\n")


def print_decision(decision: GateDecision) -> None:
    print(f"should_run={str(decision.should_run).lower()}")
    print(f"reason={decision.reason}")
    print(f"schedule_enabled={str(decision.schedule_enabled).lower()}")
    print(f"timezone={decision.timezone_name}")
    print(f"target_time={decision.target_time}")
    if decision.target_weekday:
        print(f"target_weekday={decision.target_weekday}")
    print(f"local_now={decision.local_now}")
    print(f"local_date={decision.local_date}")
    print(f"discord_delivery_enabled={str(decision.discord_delivery_enabled).lower()}")
    print(f"oss_recent_days={decision.oss_recent_days}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check whether a Career Feed workflow should run now.")
    parser.add_argument("--workflow", required=True, choices=sorted(WORKFLOWS))
    parser.add_argument(
        "--now-utc",
        help="UTC timestamp for tests, for example 2026-06-08T00:05:00Z.",
    )
    return parser.parse_args()


def parse_now_utc(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized = value.strip().replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def main() -> int:
    args = parse_args()
    decision = evaluate_gate(
        args.workflow,
        os.environ,
        event_name=os.environ.get("GITHUB_EVENT_NAME", ""),
        now_utc=parse_now_utc(args.now_utc),
    )
    print_decision(decision)
    write_github_output(decision, os.environ.get("GITHUB_OUTPUT", ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
