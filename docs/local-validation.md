# 로컬 검증 가이드

이 문서는 Career Feed의 로컬 검증 명령과 fixture 확인 방법을 정리합니다.

## 빠른 검증

일반적인 문서 또는 설정 변경 후에는 아래 명령을 우선 실행합니다.

```bash
python3 scripts/check-workflow-schedules.py
./scripts/validate.sh
git diff --check
```

## 전체 검증 명령

README 기준 로컬 검증 전체 목록입니다.

```bash
python3 scripts/check-workflow-schedules.py
python3 scripts/collect-kr-feeds.py --mode daily-backend --dry-run
python3 scripts/collect-kr-feeds.py --mode daily-news --dry-run
python3 scripts/build-daily-news-shortlist.py
python3 scripts/estimate-prompt-budget.py
python3 scripts/collect-kr-feeds.py --mode weekly-career --dry-run
python3 scripts/render-weekly-career-site-radar.py
python3 scripts/update-oss-progress.py --status
python3 scripts/validate-career-feed-brief.py reports/briefs/kr-backend-career-weekly.md --type weekly-career
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-daily-valid.md --type daily-tech --candidates-dir tests/fixtures/candidates-empty
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-news-daily-valid.md --type daily-news
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-news-daily-valid-sparse.md --type daily-news
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-news-daily-valid-empty.md --type daily-news
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-news-daily-valid-tech-investment.md --type daily-news
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-news-daily-valid-tech-only.md --type daily-news
python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-backend-career-weekly-valid.md --type weekly-career
./scripts/validate.sh
git diff --check
```

## Fixture 검증

`scripts/validate-career-feed-brief.py`는 브리핑 타입별 Markdown 품질을 검사합니다.

| 타입 | 대표 fixture | 명령 |
| --- | --- | --- |
| Daily Backend | `tests/fixtures/kr-tech-daily-valid.md` | `python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-daily-valid.md --type daily-tech --candidates-dir tests/fixtures/candidates-empty` |
| News Daily | `tests/fixtures/kr-tech-news-daily-valid.md` | `python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-news-daily-valid.md --type daily-news` |
| News Daily sparse | `tests/fixtures/kr-tech-news-daily-valid-sparse.md` | `python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-news-daily-valid-sparse.md --type daily-news` |
| News Daily empty | `tests/fixtures/kr-tech-news-daily-valid-empty.md` | `python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-tech-news-daily-valid-empty.md --type daily-news` |
| Site Radar | `tests/fixtures/kr-backend-career-weekly-valid.md` | `python3 scripts/validate-career-feed-brief.py tests/fixtures/kr-backend-career-weekly-valid.md --type weekly-career` |

Negative fixture는 `./scripts/validate.sh` 안에서 실패해야 하는 케이스로 확인합니다.

## `validate.sh`가 확인하는 것

`./scripts/validate.sh`는 아래 범위를 한 번에 검사합니다.

- Python syntax
- 활성 workflow 파일 수와 schedule
- prompt와 script 경로
- required config, docs, tests
- collector dry-run
- run summary, token budget, quality report smoke check
- validator fixture
- OSS reliability gate test
- weekly career site radar test
- 제거된 과거 경로 참조
- whitespace

## 생성 산출물 주의

검증 명령은 `reports/` 아래 JSON과 Markdown을 생성합니다. 이 산출물은 기본적으로 `.gitignore` 대상이며 커밋하지 않습니다.

## app 또는 infra를 건드렸을 때

`app/`을 수정했다면 아래 명령을 추가로 실행합니다.

```bash
cd app
./gradlew test
./gradlew clean build
```

`infra/`나 compose 관련 파일을 수정했다면 Docker가 가능한 환경에서 아래 명령을 실행합니다.

```bash
docker compose -f infra/compose.yaml config
```
