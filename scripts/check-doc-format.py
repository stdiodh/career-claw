#!/usr/bin/env python3
"""Validate documentation files that must keep real line breaks."""

from __future__ import annotations

import re
import subprocess
import sys
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

LINE_COUNT_MINIMUMS = {
    "CHANGELOG.md": 40,
    "README.md": 100,
    "docs/README.md": 60,
    "docs/project/ecosystem-importance.md": 50,
    "docs/getting-started/fork-setup.md": 120,
    "docs/getting-started/usage.md": 80,
    "docs/getting-started/runtime-configuration.md": 120,
    "docs/demo.md": 80,
    "docs/getting-started/sample-output.md": 30,
    "docs/project/release-checklist.md": 100,
    "docs/release-notes/v0.1.0.md": 40,
    "docs/project/roadmap.md": 40,
    "docs/project/contributor-tasks.md": 80,
    "CONTRIBUTING.md": 80,
    "CODE_OF_CONDUCT.md": 60,
    "SUPPORT.md": 40,
    "docs/contributing/README.md": 40,
    "docs/contributing/good-suggestion-criteria.md": 70,
    "docs/contributing/source-suggestion-guide.md": 70,
    "docs/contributing/oss-candidate-guide.md": 70,
    "docs/contributing/backend-career-question-guide.md": 50,
    "docs/contributing/review-policy.md": 60,
    "SECURITY.md": 30,
    "LICENSE": 20,
    "scripts/check-doc-format.py": 100,
    "scripts/validate.sh": 300,
}

MARKDOWN_FILES = [
    "CHANGELOG.md",
    "README.md",
    "docs/README.md",
    "docs/project/ecosystem-importance.md",
    "docs/getting-started/fork-setup.md",
    "docs/getting-started/usage.md",
    "docs/getting-started/runtime-configuration.md",
    "docs/demo.md",
    "docs/getting-started/sample-output.md",
    "docs/project/release-checklist.md",
    "docs/release-notes/v0.1.0.md",
    "docs/project/roadmap.md",
    "docs/project/contributor-tasks.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "SUPPORT.md",
    "docs/contributing/README.md",
    "docs/contributing/good-suggestion-criteria.md",
    "docs/contributing/source-suggestion-guide.md",
    "docs/contributing/oss-candidate-guide.md",
    "docs/contributing/backend-career-question-guide.md",
    "docs/contributing/review-policy.md",
    "SECURITY.md",
]

README_HEADINGS = [
    "# Career Feed",
    "## 30-Second Overview",
    "## What You Get",
    "## Quick Start Path",
    "## Project Status",
    "## How It Works",
    "## Safety / Limitations",
    "## Repository Structure",
    "## Documentation",
    "## Contributing",
    "## License",
]

DOCS_INDEX_HEADINGS = [
    "# Documentation",
    "## New Here?",
    "## Documentation Map",
    "### Getting Started",
    "### Usage / Operations",
    "### Examples / Demo",
    "### Contributing",
    "### Security / Maintainer",
    "### Release",
    "## Repository Level Documents",
]

ECOSYSTEM_HEADINGS = [
    "# Ecosystem Importance",
    "## Summary",
    "## Problem",
    "## Position in the backend ecosystem",
    "## Why this matters",
    "## Who benefits",
    "## What Career Feed does not claim",
    "## Honest limitations",
    "## How API credits help",
    "## Safety and maintainer review",
    "## Suggested wording for applications",
]

CHANGELOG_HEADINGS = [
    "# Changelog",
    "## [Unreleased]",
    "## [0.1.0] - TBD",
]

FORK_SETUP_HEADINGS = [
    "# Fork Setup Guide",
    "## Before You Start",
    "## Step 1. Fork Repository",
    "## Step 2. Enable GitHub Actions",
    "## Step 3. Add GitHub Actions Secrets",
    "## Step 4. Add GitHub Actions Variables",
    "## Step 5. Run Workflow with Dry Run",
    "## Step 6. Review Generated Artifacts",
    "## Step 7. Enable Discord Delivery",
    "## Success Checklist",
    "## Troubleshooting",
    "## Related Documents",
]

USAGE_HEADINGS = [
    "# Usage Guide",
    "## Overview",
    "## First-time fork setup",
    "## Who should use this",
    "## Before you start",
    "## Repository setup",
    "## Configuration references",
    "## Running local validation",
    "## Running a workflow manually",
    "## Recommended first run: dry-run",
    "## Reading validation artifacts",
    "## Sending to Discord",
    "## Marking PS progress",
    "## Common operating modes",
    "## What to check after a run",
    "## Troubleshooting",
    "## Safety checklist",
    "## Related documents",
]

RUNTIME_CONFIGURATION_HEADINGS = [
    "# Runtime Configuration",
    "## Secrets와 Variables",
    "## 필수 Secrets",
    "## 지원 Variables",
    "## 시간 형식",
    "## Timezone 예시",
    "## 요일 형식",
    "## Runtime Gate 방식",
    "## GitHub Actions Output",
    "## Discord 전송 우선순위",
    "## Dry-run 관계",
    "## 로컬 확인",
    "## 자주 발생하는 설정 실수",
    "## 이번 Phase 한계",
]

DEMO_HEADINGS = [
    "# 데모 가이드",
    "## Demo Flow",
    "## What to Show",
    "## What Not to Show",
    "## Screenshot Rules",
    "## Optional GIF",
    "## Related Documents",
]

SAMPLE_OUTPUT_HEADINGS = [
    "# Sample Output",
    "## Available Examples",
    "## What to Check",
    "## Adding a Sample",
    "## Related Documents",
]

RELEASE_CHECKLIST_HEADINGS = [
    "# Release Checklist",
    "## v0.1.0 release goal",
    "## v0.1.0 scope",
    "## v0.1.0 acceptance criteria",
    "## Pre-release checks",
    "## Verification commands",
    "## Release note draft",
]

RELEASE_NOTES_V010_HEADINGS = [
    "# v0.1.0 Release Notes",
    "## Summary",
    "## Highlights",
    "## Safety",
    "## Setup",
    "## Known limitations",
    "## Maintainer notes",
]

ROADMAP_HEADINGS = [
    "# Roadmap",
    "## v0.1.x",
    "## v0.2.x",
    "## Later",
    "## Out of scope",
    "## How to suggest roadmap changes",
]

CONTRIBUTOR_TASKS_HEADINGS = [
    "# Contributor Task Ideas",
    "## Good first issues",
    "## Help wanted",
    "## Not accepted contributions",
    "## Before opening a PR",
]

CODE_OF_CONDUCT_HEADINGS = [
    "# Code of Conduct",
    "## Our standard",
    "## Expected behavior",
    "## Unacceptable behavior",
    "## Project-specific expectations",
    "## Respect for beginners",
    "## Respect for maintainers",
    "## Source and suggestion etiquette",
    "## Automation safety",
    "## Reporting concerns",
    "## Enforcement approach",
    "## Scope",
    "## Maintainer notes",
]

CONTRIBUTING_INDEX_HEADINGS = [
    "# Contribution Guide Index",
    "## Start here",
    "## Contribution paths",
    "## Suggestion quality",
    "## Regional and language expansion",
    "## Maintainer review",
    "## Related documents",
]

SUPPORT_HEADINGS = [
    "# Support",
    "## Where to ask",
    "## Before opening an issue",
    "## Do not include secrets",
    "## What support can cover",
    "## What support cannot guarantee",
]

GOOD_SUGGESTION_HEADINGS = [
    "# Good Suggestion Criteria",
    "## Summary",
    "## What a good suggestion includes",
    "## What makes a suggestion hard to review",
    "## Good examples",
    "## Weak examples",
    "## Region and language metadata",
    "## Evidence and source quality",
    "## Maintainer checklist",
]

SOURCE_SUGGESTION_HEADINGS = [
    "# Source Suggestion Guide",
    "## What counts as a source",
    "## Recommended source types",
    "## Source quality checklist",
    "## Region-specific source suggestions",
    "## Examples of strong source suggestions",
    "## Examples of weak source suggestions",
    "## Sources that may be rejected",
    "## Privacy and scraping boundaries",
    "## Maintainer review flow",
]

OSS_CANDIDATE_HEADINGS = [
    "# OSS Candidate Suggestion Guide",
    "## Purpose",
    "## What makes an OSS candidate useful",
    "## Beginner-friendly signals",
    "## Backend relevance",
    "## Safety boundaries",
    "## Good examples",
    "## Weak examples",
    "## What Career Feed will not do",
    "## Maintainer checklist",
]

BACKEND_CAREER_QUESTION_HEADINGS = [
    "# Backend Career Question Guide",
    "## Purpose",
    "## What to include",
    "## Good question examples",
    "## Weak question examples",
    "## Personal information safety",
    "## How questions improve Career Feed",
    "## Maintainer review",
]

REVIEW_POLICY_HEADINGS = [
    "# Maintainer Review Policy",
    "## Review principles",
    "## What maintainers look for",
    "## Why suggestions may be declined",
    "## Automation review boundaries",
    "## Regional expansion review",
    "## Documentation review",
    "## Security review",
    "## Decision outcomes",
]

REQUIRED_README_LINKS = [
    "docs/README.md",
    "docs/getting-started/fork-setup.md",
    "docs/getting-started/sample-output.md",
    "docs/getting-started/usage.md",
    "docs/getting-started/runtime-configuration.md",
    "docs/demo.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "docs/contributing/README.md",
    "LICENSE",
]

REQUIRED_DOCS_INDEX_LINKS = [
    "CHANGELOG.md",
    "./getting-started/sample-output.md",
    "./demo.md",
    "./operations/daily-backend-brief.md",
    "./operations/daily-news-ops.md",
    "./operations/career-site-radar.md",
    "./operations/backend-growth-curriculum.md",
    "./operations/local-validation.md",
    "./policies/github-labels.md",
    "./project/contributor-tasks.md",
    "./project/release-checklist.md",
    "./release-notes/v0.1.0.md",
    "SECURITY.md",
    "SUPPORT.md",
]

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


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def line_count(text: str) -> int:
    return text.count("\n") + (0 if text.endswith("\n") or not text else 1)


def check_line_counts() -> None:
    for path, minimum in LINE_COUNT_MINIMUMS.items():
        text = read_text(path)
        count = line_count(text)
        if count < minimum:
            fail(f"{path} must have at least {minimum} physical lines, found {count}.")


def check_required_headings(path: str, headings: list[str]) -> None:
    text = read_text(path)
    missing = [heading for heading in headings if heading not in text.splitlines()]
    if missing:
        fail(f"{path} misses required heading(s): {', '.join(missing)}")


def check_readme_links() -> None:
    text = read_text("README.md")
    missing = [link for link in REQUIRED_README_LINKS if link not in text]
    if missing:
        fail(f"README.md misses required contribution link(s): {', '.join(missing)}")


def check_docs_index_links() -> None:
    text = read_text("docs/README.md")
    missing = [link for link in REQUIRED_DOCS_INDEX_LINKS if link not in text]
    if missing:
        fail(f"docs/README.md misses required documentation link(s): {', '.join(missing)}")


def check_literal_newline_strings(paths: list[str]) -> None:
    for path in paths:
        text = read_text(path)
        if "\\n" in text:
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
            re.search(r"\s-\s+\S", line)
            and not line.lstrip().startswith("-")
            and not line.lstrip().startswith("#")
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
    docs = list(LINE_COUNT_MINIMUMS)
    all_targets = docs + ISSUE_TEMPLATE_FILES

    check_line_counts()
    check_required_headings("CHANGELOG.md", CHANGELOG_HEADINGS)
    check_required_headings("README.md", README_HEADINGS)
    check_required_headings("docs/README.md", DOCS_INDEX_HEADINGS)
    check_required_headings("docs/project/ecosystem-importance.md", ECOSYSTEM_HEADINGS)
    check_required_headings("docs/getting-started/fork-setup.md", FORK_SETUP_HEADINGS)
    check_required_headings("docs/getting-started/usage.md", USAGE_HEADINGS)
    check_required_headings("docs/getting-started/runtime-configuration.md", RUNTIME_CONFIGURATION_HEADINGS)
    check_required_headings("docs/demo.md", DEMO_HEADINGS)
    check_required_headings("docs/getting-started/sample-output.md", SAMPLE_OUTPUT_HEADINGS)
    check_required_headings("docs/project/release-checklist.md", RELEASE_CHECKLIST_HEADINGS)
    check_required_headings("docs/release-notes/v0.1.0.md", RELEASE_NOTES_V010_HEADINGS)
    check_required_headings("docs/project/roadmap.md", ROADMAP_HEADINGS)
    check_required_headings("docs/project/contributor-tasks.md", CONTRIBUTOR_TASKS_HEADINGS)
    check_required_headings("CODE_OF_CONDUCT.md", CODE_OF_CONDUCT_HEADINGS)
    check_required_headings("SUPPORT.md", SUPPORT_HEADINGS)
    check_required_headings("docs/contributing/README.md", CONTRIBUTING_INDEX_HEADINGS)
    check_required_headings("docs/contributing/good-suggestion-criteria.md", GOOD_SUGGESTION_HEADINGS)
    check_required_headings("docs/contributing/source-suggestion-guide.md", SOURCE_SUGGESTION_HEADINGS)
    check_required_headings("docs/contributing/oss-candidate-guide.md", OSS_CANDIDATE_HEADINGS)
    check_required_headings(
        "docs/contributing/backend-career-question-guide.md",
        BACKEND_CAREER_QUESTION_HEADINGS,
    )
    check_required_headings("docs/contributing/review-policy.md", REVIEW_POLICY_HEADINGS)
    check_readme_links()
    check_docs_index_links()
    check_literal_newline_strings(MARKDOWN_FILES)
    for path in MARKDOWN_FILES:
        check_compressed_markdown(path)
    check_mit_license()
    check_hidden_unicode(all_targets)
    check_config_yml()
    check_issue_template_yaml()
    print("Document format checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
