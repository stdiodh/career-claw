# Daily Growth Ops

Daily Backend Brief는 Discord 전송 결과만 보는 흐름이 아니라, artifact에 남는 후보 JSON과 운영 요약으로 학습 진행과 OSS 후보 생성 상태를 확인하는 흐름입니다. 이 문서는 서버, DB, 웹 대시보드, Discord Bot 없이 GitHub Actions artifact와 정적 파일만으로 확인하는 방법을 정리합니다.

## dry_run으로 후보 확인

Actions에서 `Daily Korea Tech Brief` workflow를 수동 실행할 때 `dry_run=true`, `force_send=false`로 실행합니다.

- 후보 수집, Codex 생성, validator, artifact 업로드까지 실행합니다.
- Discord 전송과 delivery lock 저장은 하지 않습니다.
- PS progress commit도 하지 않습니다.

로컬에서는 아래 명령으로 후보 JSON 생성만 확인합니다.

```bash
python3 scripts/collect-kr-feeds.py --mode daily-backend --dry-run
```

## Artifact에서 볼 파일

workflow run의 artifact `career-feed-kr-tech-daily-<run_id>`를 내려받아 아래 파일을 봅니다.

- `reports/candidates/kr-oss-contribution-opportunities.json`
- `reports/ops/backend-daily-run-summary.json`
- `reports/ops/backend-daily-run-summary.md`
- `reports/briefs/kr-tech-daily.md`

`backend-daily-run-summary.md`의 OSS 영역은 사람이 빠르게 보는 요약입니다.

- `OSS 후보 상태`: safe 후보 수, 필터링된 후보 수, fallback 여부
- `선택 후보`: Discord에 나갈 수 있는 safe 후보의 repository와 issue 번호
- `주의`: linked work 검증 degraded 여부와 source error 수

## 후보가 없을 때 해석

Discord에 issue가 나오지 않는 날은 실패가 아닐 수 있습니다. `kr-oss-contribution-opportunities.json`의 `items`가 비어 있으면 safe 후보가 없다는 뜻이고, 브리핑은 OSS 기여 준비 루틴으로 fallback해야 합니다.

확인 순서:

1. `diagnostics.safe_items_count`가 0인지 확인합니다.
2. `diagnostics.gate_exclusion_counts`에서 많이 걸린 이유를 봅니다.
3. `source_errors`와 `diagnostics.source_error_type_counts`를 확인합니다.
4. `github_rate_limit`, `github_repository_access_failed`, `github_graphql_*`가 있으면 GitHub API나 linked work 검증이 불완전했을 수 있습니다.
5. `linked-work-check-unknown`이 많으면 linked PR/branch 검증이 완료되지 않아 추천하지 않은 것입니다.

## Discord에 issue가 없는 날의 의미

OSS 섹션에 특정 issue가 없고 준비 루틴만 나오면, 그날은 “추천 가능한 safe issue가 없음”으로 봅니다. 이는 임의 issue를 만들어내는 것보다 안전한 상태입니다. 준비 루틴은 CONTRIBUTING 문서, 빌드/테스트 명령, issue 댓글 매너를 확인하는 데 사용합니다.

## OSS progress 기록 방향

`data/oss-progress.json`과 `scripts/update-oss-progress.py`는 로컬 상태 기록용 초안입니다.

```bash
python3 scripts/update-oss-progress.py --status
python3 scripts/update-oss-progress.py --mark-reviewed https://github.com/owner/repo/issues/123 --note "문서 이슈로 검토"
python3 scripts/update-oss-progress.py --mark-skipped https://github.com/owner/repo/issues/123 --note "linked PR 확인"
python3 scripts/update-oss-progress.py --mark-attempted https://github.com/owner/repo/issues/123 --note "로컬 테스트 확인"
```

이 스크립트는 GitHub issue에 댓글을 달거나 label, assignee를 바꾸지 않습니다. 이후 필요하면 reviewed/skipped/attempted 기록을 Daily summary에 읽어 넣을 수 있지만, 현재는 정적 파일에만 기록합니다.

## News Daily 성장 품질 점검

News Daily의 후보 수, 투자 섹션, sparse/empty 정책은 [Korea Dev/AI News Daily](./daily-news-ops.md)를 따릅니다.

성장 판단은 매일 도움 점수와 오늘 할 일 1개를 남깁니다. 오늘 할 일은 읽기만 하는 행동이 아니라 20~30분 안에 실행 가능한 공식 문서 확인, 작은 코드 실험, 아키텍처 메모, 지표 확인, TIL 작성이어야 합니다.

운영 점검 파일:

- token budget: `reports/ops/news-daily-token-budget.json`
- quality report: `reports/ops/news-daily-quality-report.json`
- run summary: `reports/ops/news-daily-run-summary.json`
