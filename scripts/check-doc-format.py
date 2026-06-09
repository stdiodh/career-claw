#!/usr/bin/env python3
"""Validate documentation files that must keep real line breaks."""

from __future__ import annotations

import re
import subprocess
import sys
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

ROOT_MARKDOWN_FILES = [
    "README.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
    "SUPPORT.md",
    "CHANGELOG.md",
]

LINE_COUNT_MINIMUMS = {
    "README.md": 80,
    "docs/README.md": 8,
    "docs/kr/README.md": 60,
    "docs/en/README.md": 60,
    "docs/kr/getting-started/fork-setup.md": 120,
    "docs/en/getting-started/fork-setup.md": 120,
    "scripts/check-doc-format.py": 100,
    "scripts/validate.sh": 300,
}

EXPECTED_HEADINGS = {
    "README.md": [
        "# Career Feed",
        "## 30-Second Overview",
        "## What You Get",
        "## Project Status",
        "## How It Works",
        "## Documentation",
    ],
    "docs/README.md": ["# Documentation", "## Notes"],
    "CONTRIBUTING.md": ["# Contributing"],
    "CODE_OF_CONDUCT.md": ["# Code of Conduct"],
    "SECURITY.md": ["# Security Policy"],
    "SUPPORT.md": ["# Support"],
    "docs/kr/README.md": [
        "# Documentation",
        "## New Here?",
        "## Documentation Map",
        "### Getting Started",
        "### Usage / Operations",
        "### Examples / Demo",
        "### Contributing",
        "### Security / Maintainer",
        "### Release",
    ],
    "docs/en/README.md": [
        "# Documentation",
        "## New Here?",
        "## Documentation Map",
        "### Getting Started",
        "### Usage / Operations",
        "### Examples / Demo",
        "### Contributing",
        "### Security / Maintainer",
        "### Release",
    ],
    "docs/kr/getting-started/fork-setup.md": [
        "# Fork Setup Guide",
        "## Before You Start",
        "## Step 1. Fork Repository",
        "## Step 5. Run Workflow with Dry Run",
        "## Step 6. Review Generated Artifacts",
        "## Step 7. Enable Discord Delivery",
        "## Success Checklist",
        "## Troubleshooting",
    ],
    "docs/en/getting-started/fork-setup.md": [
        "# Fork Setup Guide",
        "## Before You Start",
        "## Step 1. Fork Repository",
        "## Step 5. Run Workflow with Dry Run",
        "## Step 6. Review Generated Artifacts",
        "## Step 7. Enable Discord Delivery",
        "## Success Checklist",
        "## Troubleshooting",
    ],
}

REQUIRED_SNIPPETS = {
    "README.md": [
        "docs/kr/README.md",
        "docs/en/README.md",
        "sequenceDiagram",
        "alt dry_run=true or delivery disabled",
    ],
    "docs/README.md": [
        "./kr/README.md",
        "./en/README.md",
    ],
    "CONTRIBUTING.md": [
        "./docs/kr/CONTRIBUTING.md",
        "./docs/en/CONTRIBUTING.md",
    ],
    "CODE_OF_CONDUCT.md": [
        "./docs/kr/CODE_OF_CONDUCT.md",
        "./docs/en/CODE_OF_CONDUCT.md",
    ],
    "SECURITY.md": [
        "./docs/kr/SECURITY.md",
        "./docs/en/SECURITY.md",
    ],
    "SUPPORT.md": [
        "./docs/kr/SUPPORT.md",
        "./docs/en/SUPPORT.md",
    ],
}

ISSUE_TEMPLATE_FILES = [
    ".github/ISSUE_TEMPLATE/backend-career-question.yml",
    ".github/ISSUE_TEMPLATE/bug-report.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/ISSUE_TEMPLATE/docs-improvement.yml",
    ".github/ISSUE_TEMPLATE/feature-request.yml",
    ".github/ISSUE_TEMPLATE/oss-candidate-suggestion.yml",
    ".github/ISSUE_TEMPLATE/source-suggestion.yml",
]

EXPECTED_CONFIG_YML = """blank_issues_enabled: true
contact_links:
  - name: Career Feed README
    url: https://github.com/stdiodh/career-feed#readme
    about: 프로젝트 목적과 운영 방식을 먼저 확인해 주세요.
"""

BIDI_CONTROL_NAMES = {
    "LEFT-TO-RIGHT MARK",
    "RIGHT-TO-LEFT MARK",
    "LEFT-TO-RIGHT EMBEDDING",
    "RIGHT-TO-LEFT EMBEDDING",
    "POP DIRECTIONAL FORMATTING",
    "LEFT-TO-RIGHT OVERRIDE",
    "RIGHT-TO-LEFT OVERRIDE",
    "LEFT-TO-RIGHT ISOLATE",
    "RIGHT-TO-LEFT ISOLATE",
    "FIRST STRONG ISOLATE",
    "POP DIRECTIONAL ISOLATE",
}


def fail(message: str) -> None:
    raise SystemExit(message)


def read_text(path: str | Path) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def markdown_files() -> list[str]:
    files = [str(path.relative_to(ROOT)) for path in (ROOT / "docs").rglob("*.md")]
    files.extend(ROOT_MARKDOWN_FILES)
    return sorted(set(files))


def line_count(text: str) -> int:
    return text.count("\n") + (0 if text.endswith("\n") or not text else 1)


def check_line_counts() -> None:
    for path, minimum in LINE_COUNT_MINIMUMS.items():
        count = line_count(read_text(path))
        if count < minimum:
            fail(f"{path} must have at least {minimum} physical lines, found {count}.")


def check_required_headings() -> None:
    for path, headings in EXPECTED_HEADINGS.items():
        lines = read_text(path).splitlines()
        missing = [heading for heading in headings if heading not in lines]
        if missing:
            fail(f"{path} misses required heading(s): {', '.join(missing)}")


def check_required_snippets() -> None:
    for path, snippets in REQUIRED_SNIPPETS.items():
        text = read_text(path)
        missing = [snippet for snippet in snippets if snippet not in text]
        if missing:
            fail(f"{path} misses required snippet(s): {', '.join(missing)}")


def check_language_tree_pairs() -> None:
    kr = {
        path.relative_to(ROOT / "docs/kr")
        for path in (ROOT / "docs/kr").rglob("*.md")
    }
    en = {
        path.relative_to(ROOT / "docs/en")
        for path in (ROOT / "docs/en").rglob("*.md")
    }
    if kr != en:
        missing_en = sorted(str(path) for path in kr - en)
        missing_kr = sorted(str(path) for path in en - kr)
        fail(
            "docs/kr and docs/en must contain the same Markdown files. "
            f"missing en={missing_en}; missing kr={missing_kr}"
        )


def check_language_switches() -> None:
    for base in ("docs/kr", "docs/en"):
        for path in (ROOT / base).rglob("*.md"):
            first_lines = path.read_text(encoding="utf-8").splitlines()[:6]
            if not any(line.startswith("> Language:") for line in first_lines):
                fail(f"{path.relative_to(ROOT)} is missing a language switch near the top.")


def check_literal_newline_strings(paths: list[str]) -> None:
    for path in paths:
        if "\\n" in read_text(path):
            fail(f'{path} contains literal "\\n" text; use physical line breaks.')


def iter_non_fenced_lines(text: str):
    in_fence = False
    for number, line in enumerate(text.splitlines(), start=1):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield number, line


def check_compressed_markdown(path: str) -> None:
    text = read_text(path)
    for number, line in iter_non_fenced_lines(text):
        if re.search(r"\s#{1,6}\s+\S", line) and not line.lstrip().startswith("#"):
            fail(f"{path}:{number} appears to contain a heading glued to prior text.")
        if re.search(r"^#{1,6}\s+.+\s#{1,6}\s+\S", line):
            fail(f"{path}:{number} appears to contain multiple headings on one line.")
        if re.search(r"\|\s+\|", line):
            fail(f"{path}:{number} appears to contain multiple Markdown table rows on one line.")
        if (
            re.search(r"[.!?。！？]\s+-\s+\S", line)
            and not line.lstrip().startswith("-")
            and not line.lstrip().startswith("#")
            and not re.match(r"\s*(?:\d+[.)]|[-*+])\s+", line)
        ):
            fail(f"{path}:{number} appears to contain a list item glued to prior text.")


def check_mit_license() -> None:
    text = read_text("LICENSE")
    required_snippets = [
        "MIT License\n\nCopyright (c) 2026 stdiodh",
        'Permission is hereby granted, free of charge, to any person obtaining a copy\nof this software',
        "The above copyright notice and this permission notice shall be included in all\ncopies or substantial portions of the Software.",
        'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\nIMPLIED',
    ]
    missing = [snippet for snippet in required_snippets if snippet not in text]
    if missing:
        fail("LICENSE does not match the expected MIT License paragraph formatting.")


def check_hidden_unicode(paths: list[str]) -> None:
    for path in paths:
        text = read_text(path)
        for index, char in enumerate(text):
            if char in "\n\r\t":
                continue
            category = unicodedata.category(char)
            name = unicodedata.name(char, "")
            if category == "Cf" or name in BIDI_CONTROL_NAMES:
                fail(f"{path} contains hidden Unicode character U+{ord(char):04X} at offset {index}.")


def check_config_yml() -> None:
    text = read_text(".github/ISSUE_TEMPLATE/config.yml")
    if text != EXPECTED_CONFIG_YML:
        fail(".github/ISSUE_TEMPLATE/config.yml does not match the expected YAML content.")


def check_issue_template_yaml() -> None:
    paths = [str(ROOT / path) for path in ISSUE_TEMPLATE_FILES]
    ruby = (
        'require "yaml"; '
        'ARGV.each do |path| '
        'data = YAML.load_file(path); '
        'if data.key?("body") && !data["body"].is_a?(Array); '
        'raise "body is not a list: #{path}"; '
        "end; "
        'puts "YAML OK: #{path}"; '
        "end"
    )
    result = subprocess.run(
        ["ruby", "-e", ruby, *paths],
        check=False,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if result.returncode != 0:
        fail(result.stdout.strip() or "Issue template YAML parse failed.")
    print(result.stdout, end="")


def main() -> int:
    docs = markdown_files()
    all_targets = docs + ISSUE_TEMPLATE_FILES

    check_line_counts()
    check_required_headings()
    check_required_snippets()
    check_language_tree_pairs()
    check_language_switches()
    check_literal_newline_strings(docs)
    for path in docs:
        check_compressed_markdown(path)
    check_mit_license()
    check_hidden_unicode(all_targets)
    check_config_yml()
    check_issue_template_yaml()
    print("Document format checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
