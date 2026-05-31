#!/usr/bin/env python3
"""Contract tests for OSS candidate JSON to daily brief validation."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALID_DAILY_FIXTURE = ROOT / "tests" / "fixtures" / "kr-tech-daily-valid.md"
VALIDATOR = ROOT / "scripts" / "validate-career-feed-brief.py"
SAFE_URL = "https://github.com/spring-projects/spring-boot/issues/12345"
OTHER_URL = "https://github.com/spring-projects/spring-boot/issues/67890"


def replace_oss_section(content: str, section: str) -> str:
    updated, count = re.subn(
        r"## 3\. 오픈소스 기여 후보.*?(?=\n## 4\.)",
        section.rstrip() + "\n\n",
        content,
        count=1,
        flags=re.DOTALL,
    )
    if count != 1:
        raise AssertionError("Could not replace OSS section")
    return updated


def oss_candidate_section(url: str = SAFE_URL) -> str:
    return f"""## 3. 오픈소스 기여 후보
### 후보: Improve getting started documentation
- 상태 확인: maintainer triage 완료, 담당자 없음, 연결 PR/branch 없음, claim 댓글 없음
- 난이도 밴드: P5-like
- 저장소: spring-projects/spring-boot
- 기여 유형: docs
- 왜 시도해볼 만한가: 문서 위치와 확인 범위가 작아 첫 기여로 검토하기 좋습니다.
- 첫 30분 액션: CONTRIBUTING 문서에서 빌드 명령을 확인하고 관련 docs 위치를 메모합니다.
- 기여 전 매너: 최근 댓글과 연결 PR/branch가 계속 없는지 확인한 뒤 범위 확인 댓글을 남깁니다.
- 확인할 파일/키워드: CONTRIBUTING.adoc, getting started docs
- 주의할 점: PR 작성 전에 재현 범위와 문서 위치를 먼저 확인합니다.
- 링크: [Issue 보기]({url})"""


def oss_candidate_section_with_natural_absence_text(url: str = SAFE_URL) -> str:
    return f"""## 3. 오픈소스 기여 후보
### 후보: Improve getting started documentation
- 상태 확인: maintainer 작성 이슈이고, assignee와 linked PR/branch가 없고 claim 댓글도 없다.
- 난이도 밴드: P5-like
- 저장소: spring-projects/spring-boot
- 기여 유형: docs
- 왜 시도해볼 만한가: 문서 위치와 확인 범위가 작아 첫 기여로 검토하기 좋습니다.
- 첫 30분 액션: CONTRIBUTING 문서에서 빌드 명령을 확인하고 관련 docs 위치를 메모합니다.
- 기여 전 매너: 최근 댓글과 연결 PR/branch가 계속 없는지 확인한 뒤 범위 확인 댓글을 남깁니다.
- 확인할 파일/키워드: CONTRIBUTING.adoc, getting started docs
- 주의할 점: PR 작성 전에 재현 범위와 문서 위치를 먼저 확인합니다.
- 링크: [Issue 보기]({url})"""


def candidate_payload(url: str = SAFE_URL, *, safe: bool = True) -> dict[str, object]:
    return {
        "schema_version": 2,
        "category": "kr-oss-contribution-opportunities",
        "candidate_count": 1 if safe else 0,
        "items": [
            {
                "title": "Improve getting started documentation",
                "url": url,
                "repository": "spring-projects/spring-boot",
                "difficulty_band": "p5_like",
                "contribution_type": "docs",
                "safe_to_recommend": safe,
            }
        ]
        if safe
        else [],
    }


def run_validator(markdown: str, payload: dict[str, object]) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        report_path = tmp_path / "daily.md"
        candidates_dir = tmp_path / "candidates"
        candidates_dir.mkdir()
        report_path.write_text(markdown, encoding="utf-8")
        (candidates_dir / "kr-oss-contribution-opportunities.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return subprocess.run(
            [
                sys.executable,
                str(VALIDATOR),
                str(report_path),
                "--type",
                "daily-tech",
                "--candidates-dir",
                str(candidates_dir),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )


def assert_passes(result: subprocess.CompletedProcess[str]) -> None:
    if result.returncode != 0:
        raise AssertionError(result.stderr)


def assert_fails(result: subprocess.CompletedProcess[str], expected: str) -> None:
    output = result.stdout + result.stderr
    if result.returncode == 0:
        raise AssertionError("Expected validator to fail")
    if expected not in output:
        raise AssertionError(f"Expected failure containing {expected!r}, got: {output}")


def test_safe_candidate_url_passes() -> None:
    base = VALID_DAILY_FIXTURE.read_text(encoding="utf-8")
    markdown = replace_oss_section(base, oss_candidate_section())
    assert_passes(run_validator(markdown, candidate_payload()))


def test_safe_candidate_natural_absence_text_passes() -> None:
    base = VALID_DAILY_FIXTURE.read_text(encoding="utf-8")
    markdown = replace_oss_section(base, oss_candidate_section_with_natural_absence_text())
    assert_passes(run_validator(markdown, candidate_payload()))


def test_empty_candidate_rejects_issue_url() -> None:
    base = VALID_DAILY_FIXTURE.read_text(encoding="utf-8")
    markdown = replace_oss_section(base, oss_candidate_section())
    assert_fails(
        run_validator(markdown, candidate_payload(safe=False)),
        "OSS candidate JSON has no safe candidate",
    )


def test_hallucinated_issue_url_is_rejected() -> None:
    base = VALID_DAILY_FIXTURE.read_text(encoding="utf-8")
    markdown = replace_oss_section(base, oss_candidate_section(OTHER_URL))
    assert_fails(
        run_validator(markdown, candidate_payload()),
        "OSS issue URL is not present",
    )


def main() -> int:
    tests = [
        test_safe_candidate_url_passes,
        test_safe_candidate_natural_absence_text_passes,
        test_empty_candidate_rejects_issue_url,
        test_hallucinated_issue_url_is_rejected,
    ]
    for test in tests:
        test()
    print("Daily OSS candidate-to-brief contract tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
