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
- 추천 점수: 92/100
- 왜 시도해볼 만한가: 문서 위치와 확인 범위가 작아 첫 기여로 검토하기 좋습니다.
- 첫 30분 액션: CONTRIBUTING 문서에서 빌드 명령을 확인하고 관련 docs 위치를 메모합니다.
- 기여 전 매너: 최근 댓글과 연결 PR/branch가 계속 없는지 확인한 뒤 범위 확인 댓글을 남깁니다.
- 확인할 파일/키워드: CONTRIBUTING.adoc, getting started docs
- 주의할 점: PR 작성 전에 재현 범위와 문서 위치를 먼저 확인합니다.
- 이슈에 남길 첫 댓글 초안: Hi team, I am interested in looking into this issue. Please let me know if this direction sounds reasonable.
- 링크: [Issue 보기]({url})"""


def oss_candidate_section_with_natural_absence_text(url: str = SAFE_URL) -> str:
    return f"""## 3. 오픈소스 기여 후보
### 후보: Improve getting started documentation
- 상태 확인: maintainer 작성 이슈이고, assignee와 linked PR/branch가 없고 claim 댓글도 확인되지 않아 안전한 추천 조건을 만족합니다.
- 난이도 밴드: P5-like
- 저장소: spring-projects/spring-boot
- 기여 유형: docs
- 추천 점수: 92/100
- 왜 시도해볼 만한가: 문서 위치와 확인 범위가 작아 첫 기여로 검토하기 좋습니다.
- 첫 30분 액션: CONTRIBUTING 문서에서 빌드 명령을 확인하고 관련 docs 위치를 메모합니다.
- 기여 전 매너: 최근 댓글과 연결 PR/branch가 계속 없는지 확인한 뒤 범위 확인 댓글을 남깁니다.
- 확인할 파일/키워드: CONTRIBUTING.adoc, getting started docs
- 주의할 점: PR 작성 전에 재현 범위와 문서 위치를 먼저 확인합니다.
- 이슈에 남길 첫 댓글 초안: Hi team, I am interested in looking into this issue. Please let me know if this direction sounds reasonable.
- 링크: [Issue 보기]({url})"""


def oss_candidate_section_with_split_maintainer_signal(url: str = SAFE_URL) -> str:
    return f"""## 3. 오픈소스 기여 후보
### 후보: Improve getting started documentation
- 상태 확인: `spring-projects/spring-boot`의 open issue이고 assignee가 없으며 linked PR/branch와 claim 댓글도 없다.
- 난이도 밴드: P5-like
- 저장소: spring-projects/spring-boot
- 기여 유형: docs
- 추천 점수: 92/100
- 왜 시도해볼 만한가: maintainer가 작성한 문서 이슈이고 확인 범위가 작아 첫 기여로 검토하기 좋습니다.
- 첫 30분 액션: CONTRIBUTING 문서에서 빌드 명령을 확인하고 관련 docs 위치를 메모합니다.
- 기여 전 매너: 최근 댓글과 연결 PR/branch가 계속 없는지 확인한 뒤 범위 확인 댓글을 남깁니다.
- 확인할 파일/키워드: CONTRIBUTING.adoc, getting started docs
- 주의할 점: PR 작성 전에 재현 범위와 문서 위치를 먼저 확인합니다.
- 이슈에 남길 첫 댓글 초안: Hi team, I am interested in looking into this issue. Please let me know if this direction sounds reasonable.
- 링크: [Issue 보기]({url})"""


def oss_candidate_section_without_maintainer_text(url: str = SAFE_URL) -> str:
    return f"""## 3. 오픈소스 기여 후보
### 후보: Improve getting started documentation
- 상태 확인: `spring-projects/spring-boot`의 열린 이슈이고, 담당자 없음, linked PR/branch 없음, claim 댓글 없음이 확인된 안전 후보다.
- 난이도 밴드: P5-like
- 저장소: spring-projects/spring-boot
- 기여 유형: docs
- 추천 점수: 92/100
- 왜 시도해볼 만한가: 문서 위치와 확인 범위가 작아 첫 기여로 검토하기 좋습니다.
- 첫 30분 액션: CONTRIBUTING 문서에서 빌드 명령을 확인하고 관련 docs 위치를 메모합니다.
- 기여 전 매너: 최근 댓글과 연결 PR/branch가 계속 없는지 확인한 뒤 범위 확인 댓글을 남깁니다.
- 확인할 파일/키워드: CONTRIBUTING.adoc, getting started docs
- 주의할 점: PR 작성 전에 재현 범위와 문서 위치를 먼저 확인합니다.
- 이슈에 남길 첫 댓글 초안: Hi team, I am interested in looking into this issue. Please let me know if this direction sounds reasonable.
- 링크: [Issue 보기]({url})"""


def candidate_payload(url: str = SAFE_URL, *, safe: bool = True) -> dict[str, object]:
    return {
        "schema_version": 3,
        "category": "kr-oss-contribution-opportunities",
        "candidate_count": 1 if safe else 0,
        "diagnostics": {"safe_items_count": 1 if safe else 0},
        "items": [
            {
                "title": "Improve getting started documentation",
                "url": url,
                "repository": "spring-projects/spring-boot",
                "difficulty_band": "p5_like",
                "contribution_type": "docs",
                "score": 92,
                "score_breakdown": {
                    "technical_fit": 28,
                    "external_contribution_signal": 20,
                    "scope_clarity": 15,
                    "validation_feasibility": 15,
                    "maintainer_signal": 10,
                    "portfolio_value": 4,
                },
                "safety_checks": {
                    "open_issue": True,
                    "no_assignee": True,
                    "no_linked_pr": True,
                    "no_linked_branch": True,
                    "no_claim_comment": True,
                    "linked_work_verified": True,
                },
                "safe_to_recommend": safe,
            }
        ]
        if safe
        else [],
    }


def fallback_oss_section() -> str:
    return """## 3. 오픈소스 기여 후보
### 오늘의 OSS 기여 준비 루틴
- 오늘은 바로 추천할 안전한 issue는 없습니다.
- 저장소: spring-projects/spring-security
- 30분 액션: CONTRIBUTING 문서에서 빌드와 테스트 명령을 확인하고 docs 위치를 메모합니다.
- 확인할 문서: CONTRIBUTING.adoc, docs
- 다음에 issue를 찾을 때 쓸 GitHub 검색식: `repo:spring-projects/spring-security is:issue is:open label:"status: ideal-for-contribution" no:assignee`
- 기여 전 매너: issue에 댓글을 남기기 전 linked PR/branch와 최근 claim 댓글을 다시 확인합니다."""


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


def test_safe_candidate_split_maintainer_signal_passes() -> None:
    base = VALID_DAILY_FIXTURE.read_text(encoding="utf-8")
    markdown = replace_oss_section(base, oss_candidate_section_with_split_maintainer_signal())
    assert_passes(run_validator(markdown, candidate_payload()))


def test_safe_candidate_without_maintainer_text_passes() -> None:
    base = VALID_DAILY_FIXTURE.read_text(encoding="utf-8")
    markdown = replace_oss_section(base, oss_candidate_section_without_maintainer_text())
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


def test_fallback_routine_passes_without_safe_candidate() -> None:
    base = VALID_DAILY_FIXTURE.read_text(encoding="utf-8")
    markdown = replace_oss_section(base, fallback_oss_section())
    assert_passes(run_validator(markdown, candidate_payload(safe=False)))


def main() -> int:
    tests = [
        test_safe_candidate_url_passes,
        test_safe_candidate_natural_absence_text_passes,
        test_safe_candidate_split_maintainer_signal_passes,
        test_safe_candidate_without_maintainer_text_passes,
        test_empty_candidate_rejects_issue_url,
        test_hallucinated_issue_url_is_rejected,
        test_fallback_routine_passes_without_safe_candidate,
    ]
    for test in tests:
        test()
    print("Daily OSS candidate-to-brief contract tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
