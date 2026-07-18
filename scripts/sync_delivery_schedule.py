#!/usr/bin/env python3
"""Synchronize GitHub Actions schedules from one local-time configuration."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

try:
    from . import check_oss_delivery_gate as delivery_gate
except ImportError:
    import check_oss_delivery_gate as delivery_gate


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = Path("configs/delivery-schedule.json")
GATE_PATH = Path("configs/oss-delivery-gate.json")
EXPECTED_CONFIG_KEYS = {"schema_version", "enabled", "timezone", "local_time"}
TIME_RE = re.compile(r"(?:[01]\d|2[0-3]):[0-5]\d")
TIMEZONE_RE = re.compile(r"[A-Za-z0-9._+-]+(?:/[A-Za-z0-9._+-]+)*")
SCHEDULE_BLOCK_RE = re.compile(
    r"^  schedule:\n.*?(?=^  [A-Za-z_][A-Za-z0-9_-]*:)",
    re.MULTILINE | re.DOTALL,
)
WORKFLOW_RECURRENCES = {
    Path(".github/workflows/backend-daily.yml"): "* * *",
    Path(".github/workflows/oss-weekly.yml"): "* * 1",
}
OSS_WORKFLOW_PATH = Path(".github/workflows/oss-weekly.yml")


class ScheduleError(RuntimeError):
    """Raised when the schedule configuration or generated workflow is invalid."""


@dataclass(frozen=True)
class DeliverySchedule:
    enabled: bool
    timezone: str
    hour: int
    minute: int


def _require_object(value: Any, path: Path) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ScheduleError(f"Schedule config must be a JSON object: {path}")
    return value


def load_schedule(path: Path = ROOT / CONFIG_PATH) -> DeliverySchedule:
    try:
        payload = _require_object(json.loads(path.read_text(encoding="utf-8")), path)
    except json.JSONDecodeError as exc:
        raise ScheduleError(f"Schedule config is not valid JSON: {path}: {exc}") from exc

    keys = set(payload)
    missing = sorted(EXPECTED_CONFIG_KEYS - keys)
    unknown = sorted(keys - EXPECTED_CONFIG_KEYS)
    if missing:
        raise ScheduleError(f"Schedule config is missing key(s): {', '.join(missing)}")
    if unknown:
        raise ScheduleError(f"Schedule config has unknown key(s): {', '.join(unknown)}")

    schema_version = payload["schema_version"]
    if type(schema_version) is not int or schema_version != 1:
        raise ScheduleError("Schedule config schema_version must be 1")

    enabled = payload["enabled"]
    if type(enabled) is not bool:
        raise ScheduleError("Schedule enabled must be a boolean")

    local_time = payload["local_time"]
    if not isinstance(local_time, str) or TIME_RE.fullmatch(local_time) is None:
        raise ScheduleError("Schedule local_time must use zero-padded 24-hour HH:MM")
    hour_text, minute_text = local_time.split(":", 1)

    timezone = payload["timezone"]
    if not isinstance(timezone, str) or TIMEZONE_RE.fullmatch(timezone) is None:
        raise ScheduleError("Schedule timezone must be an IANA timezone name")
    try:
        ZoneInfo(timezone)
    except (ValueError, ZoneInfoNotFoundError) as exc:
        raise ScheduleError(f"Unknown IANA timezone: {timezone}") from exc

    return DeliverySchedule(
        enabled=enabled,
        timezone=timezone,
        hour=int(hour_text),
        minute=int(minute_text),
    )


def render_schedule_block(
    schedule: DeliverySchedule, recurrence: str
) -> str:
    return (
        "  schedule:\n"
        "    # Generated from configs/delivery-schedule.json; run "
        "python3 scripts/sync_delivery_schedule.py.\n"
        f'    - cron: "{schedule.minute} {schedule.hour} {recurrence}"\n'
        f'      timezone: "{schedule.timezone}"\n'
    )


def render_workflow(
    content: str,
    schedule: DeliverySchedule,
    recurrence: str,
    path: Path,
) -> str:
    if not schedule.enabled:
        rendered, count = SCHEDULE_BLOCK_RE.subn("", content)
        if count not in {0, 1}:
            raise ScheduleError(f"Expected at most one on.schedule block: {path}")
        return rendered

    replacement = render_schedule_block(schedule, recurrence)
    rendered, count = SCHEDULE_BLOCK_RE.subn(lambda _: replacement, content)
    if count == 0:
        rendered, count = re.subn(
            r"^on:\n",
            "on:\n" + replacement,
            content,
            count=1,
            flags=re.MULTILINE,
        )
    if count != 1:
        raise ScheduleError(f"Expected one on block: {path}")
    return rendered


def calculate_shadow_contract(
    root: Path,
    content_overrides: dict[Path, str] | None = None,
) -> str:
    overrides = content_overrides or {}
    digest = hashlib.sha256()
    for source_path in delivery_gate.SHADOW_CONTRACT_PATHS:
        relative_path = source_path.relative_to(delivery_gate.ROOT)
        digest.update(relative_path.as_posix().encode("utf-8"))
        digest.update(b"\0")
        if relative_path in overrides:
            digest.update(overrides[relative_path].encode("utf-8"))
        else:
            digest.update((root / relative_path).read_bytes())
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


def load_gate(path: Path) -> dict[str, Any]:
    try:
        return _require_object(json.loads(path.read_text(encoding="utf-8")), path)
    except json.JSONDecodeError as exc:
        raise ScheduleError(f"OSS delivery gate is not valid JSON: {path}: {exc}") from exc


def gate_has_no_evidence(gate: dict[str, Any]) -> bool:
    return (
        gate.get("status") == "LOCKED"
        and gate.get("runs") == []
        and gate.get("candidate_reviews") == []
        and gate.get("approved_at") is None
    )


def render_gate(gate: dict[str, Any], shadow_contract: str) -> str:
    updated = dict(gate)
    updated["shadow_contract_sha256"] = shadow_contract
    return json.dumps(updated, ensure_ascii=False, indent=2) + "\n"


def synchronize(root: Path = ROOT, *, check: bool = False) -> list[Path]:
    schedule = load_schedule(root / CONFIG_PATH)
    original_workflows: dict[Path, str] = {}
    rendered_workflows: dict[Path, str] = {}

    for relative_path, recurrence in WORKFLOW_RECURRENCES.items():
        path = root / relative_path
        content = path.read_text(encoding="utf-8")
        original_workflows[relative_path] = content
        rendered_workflows[relative_path] = render_workflow(
            content, schedule, recurrence, path
        )

    shadow_contract = calculate_shadow_contract(
        root,
        {OSS_WORKFLOW_PATH: rendered_workflows[OSS_WORKFLOW_PATH]},
    )
    gate_path = root / GATE_PATH
    gate = load_gate(gate_path)
    gate_contract_changed = gate.get("shadow_contract_sha256") != shadow_contract
    oss_workflow_changed = (
        original_workflows[OSS_WORKFLOW_PATH]
        != rendered_workflows[OSS_WORKFLOW_PATH]
    )
    if (gate_contract_changed or oss_workflow_changed) and not gate_has_no_evidence(gate):
        raise ScheduleError(
            "Refusing to change the OSS Shadow contract because delivery evidence "
            "or approval exists; preserve the evidence and start an explicit migration"
        )

    updates = {
        relative_path: rendered
        for relative_path, rendered in rendered_workflows.items()
        if rendered != original_workflows[relative_path]
    }
    if gate_contract_changed:
        updates[GATE_PATH] = render_gate(gate, shadow_contract)
    changed = list(updates)

    if check and changed:
        paths = ", ".join(str(path) for path in changed)
        raise ScheduleError(
            "Delivery schedule is out of sync for "
            f"{paths}; run python3 scripts/sync_delivery_schedule.py"
        )
    if not check:
        for relative_path, rendered in updates.items():
            (root / relative_path).write_text(rendered, encoding="utf-8")
    return changed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail instead of writing when workflow schedules are out of sync.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        changed = synchronize(check=args.check)
    except (OSError, ScheduleError) as exc:
        print(f"Failed to synchronize delivery schedule: {exc}", file=sys.stderr)
        return 1

    if args.check:
        print("Delivery schedule is synchronized.")
    elif changed:
        print("Updated delivery schedule: " + ", ".join(str(path) for path in changed))
    else:
        print("Delivery schedule already synchronized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
