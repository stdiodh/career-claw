#!/usr/bin/env python3
"""Render the manual Backend Career site radar Markdown."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COLLECTOR_PATH = ROOT / "scripts" / "collect-kr-feeds.py"


def load_collector():
    spec = importlib.util.spec_from_file_location("collector", COLLECTOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load collector module: {COLLECTOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[str(spec.name)] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    collector = load_collector()
    payload = collector.write_weekly_career_site_radar_report(collector.now_kst())
    print(
        "Rendered weekly career site radar "
        f"({payload['site_count']} site(s), {payload['link_count']} link(s)): "
        f"{collector.WEEKLY_CAREER_BRIEF_OUTPUT_PATH}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
