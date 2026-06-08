#!/usr/bin/env python3
"""Contract tests for OSS candidate JSON to daily brief validation."""

from __future__ import annotations

import importlib.util
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
EXCLUDED_URL = "https://github.com/spring-projects/spring-boot/issues/33333"
STALE_URL = "https://github.com/spring-projects/spring-boot/issues/44444"


def load_validator_module():
    spec = importlib.util.spec_from_file_location("career_feed_validator", VALIDATOR)
    if spec is None or spec.loader is None:
        raise AssertionError("Could not load validator module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


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


def candidate_payload(
    url: str = SAFE_URL,
    *,
    safe: bool = True,
    created_at: str = "2026-05-15 09:00:00 KST",
    updated_at: str = "2026-05-30 09:00:00 KST",
    is_recent: bool = True,
    recency_reason: str = "created_within_recent_window",
    safety_recency: bool = True,
) -> dict[str, object]:
    return {
        "schema_version": 3,
        "category": "kr-oss-contribution-opportunities",
        "oss_recent_days": 30,
        "recency_window_start": "2026-05-02T00:00:00Z",
        "recency_window_end": "2026-06-01T00:00:00Z",
        "stale_issue_filtered_count": 0,
        "invalid_created_at_filtered_count": 0,
        "safe_candidate_count": 1 if safe else 0,
        "candidate_count": 1 if safe else 0,
        "diagnostics": {
            "oss_recent_days": 30,
            "recency_window_start": "2026-05-02T00:00:00Z",
            "recency_window_end": "2026-06-01T00:00:00Z",
            "stale_issue_filtered_count": 0,
            "missing_created_at_filtered_count": 0,
            "invalid_created_at_filtered_count": 0,
            "safe_candidate_count": 1 if safe else 0,
            "safe_items_count": 1 if safe else 0,
            "source_error_type_counts": {},
            "excluded_candidates_preview": [
                {
                    "repository": "spring-projects/spring-boot",
                    "issue_number": 33333,
                    "title": "Excluded assigned docs issue",
                    "url": EXCLUDED_URL,
                    "labels": ["type: documentation"],
                    "reason": "assigned",
                    "reason_detail": "Issue has an assignee, so it is not safe for first contribution recommendation.",
                }
            ],
        },
        "items": [
            {
                "title": "Improve getting started documentation",
                "url": url,
                "repository": "spring-projects/spring-boot",
                "repository_priority": "A",
                "repository_initial_fit_score": 82,
                "repository_ecosystem_tags": ["spring", "backend"],
                "repository_junior_notes": "문서와 테스트 재현 우선",
                "repository_local_check_hints": ["./gradlew test"],
                "repository_docs_or_test_hints": ["spring-boot docs"],
                "issue_number": 12345,
                "labels": ["status: ideal-for-contribution"],
                "author_association": "MEMBER",
                "created_at": created_at,
                "updated_at": updated_at,
                "last_activity_at": updated_at,
                "is_recent": is_recent,
                "recency_reason": recency_reason,
                "oss_recent_days": 30,
                "recency_window_start": "2026-05-02T00:00:00Z",
                "recency_window_end": "2026-06-01T00:00:00Z",
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
                    "is_open": True,
                    "has_no_assignee": True,
                    "has_no_linked_work": True,
                    "linked_work_check_complete": True,
                    "has_no_claim_comment": True,
                    "has_beginner_or_maintainer_signal": True,
                    "matches_preferred_type": True,
                    "has_no_avoid_label": True,
                    "has_no_avoid_keyword": True,
                    "created_within_recent_window": safety_recency,
                },
                "junior_fit_evidence": ["preferred contribution type: docs"],
                "maintainer_signal": "maintainer-authored",
                "risk": "low",
                "first_30_minute_action": "CONTRIBUTING 문서에서 빌드 명령을 확인합니다.",
                "suggested_first_comment": "Hi team, I am interested in looking into this issue.",
                "search_source": "profile_query:docs q=repo:spring-projects/spring-boot is:issue is:open no:assignee documentation",
                "safe_to_recommend": safe,
            }
        ]
        if safe
        else [],
        "safe_oss_candidates": []
        if not safe
        else [
            {
                "title": "Improve getting started documentation",
                "url": url,
                "repository": "spring-projects/spring-boot",
                "safe_to_recommend": True,
                "is_recent": is_recent,
                "recency_reason": recency_reason,
            }
        ],
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
        "OSS_FALLBACK_CONTAINS_ISSUE_URL",
    )


def test_hallucinated_issue_url_is_rejected() -> None:
    base = VALID_DAILY_FIXTURE.read_text(encoding="utf-8")
    markdown = replace_oss_section(base, oss_candidate_section(OTHER_URL))
    assert_fails(
        run_validator(markdown, candidate_payload()),
        "OSS_ISSUE_URL_NOT_IN_SAFE_CANDIDATES",
    )


def test_excluded_issue_url_is_rejected() -> None:
    base = VALID_DAILY_FIXTURE.read_text(encoding="utf-8")
    markdown = replace_oss_section(base, oss_candidate_section(EXCLUDED_URL))
    assert_fails(
        run_validator(markdown, candidate_payload()),
        "OSS_ISSUE_URL_NOT_SAFE_TO_RECOMMEND",
    )


def test_stale_2023_issue_url_is_rejected() -> None:
    base = VALID_DAILY_FIXTURE.read_text(encoding="utf-8")
    markdown = replace_oss_section(base, oss_candidate_section(STALE_URL))
    assert_fails(
        run_validator(
            markdown,
            candidate_payload(
                STALE_URL,
                created_at="2023-04-10T00:00:00Z",
                updated_at="2026-05-30T00:00:00Z",
            ),
        ),
        "OSS_ISSUE_URL_NOT_RECENT",
    )


def test_candidate_created_31_days_ago_is_rejected() -> None:
    base = VALID_DAILY_FIXTURE.read_text(encoding="utf-8")
    markdown = replace_oss_section(base, oss_candidate_section())
    assert_fails(
        run_validator(
            markdown,
            candidate_payload(created_at="2026-05-01T23:59:59Z"),
        ),
        "OSS_ISSUE_URL_NOT_RECENT",
    )


def test_candidate_invalid_created_at_is_rejected() -> None:
    base = VALID_DAILY_FIXTURE.read_text(encoding="utf-8")
    markdown = replace_oss_section(base, oss_candidate_section())
    assert_fails(
        run_validator(markdown, candidate_payload(created_at="not-a-date")),
        "OSS_ISSUE_URL_INVALID_CREATED_AT",
    )


def test_candidate_is_recent_false_is_rejected() -> None:
    base = VALID_DAILY_FIXTURE.read_text(encoding="utf-8")
    markdown = replace_oss_section(base, oss_candidate_section())
    assert_fails(
        run_validator(
            markdown,
            candidate_payload(
                is_recent=False,
                recency_reason="created_at_older_than_recent_window",
                safety_recency=True,
            ),
        ),
        "OSS_ISSUE_URL_NOT_RECENT",
    )


def test_fallback_routine_passes_without_safe_candidate() -> None:
    base = VALID_DAILY_FIXTURE.read_text(encoding="utf-8")
    markdown = replace_oss_section(base, fallback_oss_section())
    assert_passes(run_validator(markdown, candidate_payload(safe=False)))


def test_fallback_routine_rejects_invented_issue_url() -> None:
    base = VALID_DAILY_FIXTURE.read_text(encoding="utf-8")
    section = fallback_oss_section() + f"\n- 링크: [Issue 보기]({OTHER_URL})"
    markdown = replace_oss_section(base, section)
    assert_fails(
        run_validator(markdown, candidate_payload(safe=False)),
        "OSS_FALLBACK_CONTAINS_ISSUE_URL",
    )


def test_github_issue_url_extraction_and_normalization() -> None:
    validator = load_validator_module()
    markdown = """
- markdown: [Issue](https://github.com/Spring-Projects/Spring-Boot/issues/12345?utm=test#note)
- plain: http://github.com/spring-projects/spring-boot/issues/12345
- angle: <https://github.com/spring-projects/spring-boot/issues/12345/>
"""
    urls = validator.extract_github_issue_urls(markdown)
    normalized = [validator.normalize_github_issue_url(url) for url in urls]
    assert normalized == [
        SAFE_URL,
        SAFE_URL,
        SAFE_URL,
    ]


def test_first_action_rejects_overscoped_pr_wording() -> None:
    base = VALID_DAILY_FIXTURE.read_text(encoding="utf-8")
    section = oss_candidate_section().replace(
        "CONTRIBUTING 문서에서 빌드 명령을 확인하고 관련 docs 위치를 메모합니다.",
        "바로 PR을 만들고 전체 구현을 진행합니다.",
    )
    markdown = replace_oss_section(base, section)
    assert_fails(
        run_validator(markdown, candidate_payload()),
        "forbidden phrase",
    )


def test_safe_candidate_missing_score_is_rejected() -> None:
    base = VALID_DAILY_FIXTURE.read_text(encoding="utf-8")
    section = oss_candidate_section().replace("- 추천 점수: 92/100\n", "")
    markdown = replace_oss_section(base, section)
    assert_fails(
        run_validator(markdown, candidate_payload()),
        "추천 점수",
    )


def test_safe_candidate_payload_missing_required_field_is_rejected() -> None:
    base = VALID_DAILY_FIXTURE.read_text(encoding="utf-8")
    payload = candidate_payload()
    del payload["items"][0]["search_source"]  # type: ignore[index]
    markdown = replace_oss_section(base, oss_candidate_section())
    assert_fails(
        run_validator(markdown, payload),
        "missing field",
    )


def main() -> int:
    tests = [
        test_safe_candidate_url_passes,
        test_safe_candidate_natural_absence_text_passes,
        test_safe_candidate_split_maintainer_signal_passes,
        test_safe_candidate_without_maintainer_text_passes,
        test_empty_candidate_rejects_issue_url,
        test_hallucinated_issue_url_is_rejected,
        test_excluded_issue_url_is_rejected,
        test_stale_2023_issue_url_is_rejected,
        test_candidate_created_31_days_ago_is_rejected,
        test_candidate_invalid_created_at_is_rejected,
        test_candidate_is_recent_false_is_rejected,
        test_fallback_routine_passes_without_safe_candidate,
        test_fallback_routine_rejects_invented_issue_url,
        test_github_issue_url_extraction_and_normalization,
        test_first_action_rejects_overscoped_pr_wording,
        test_safe_candidate_missing_score_is_rejected,
        test_safe_candidate_payload_missing_required_field_is_rejected,
    ]
    for test in tests:
        test()
    print("Daily OSS candidate-to-brief contract tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
