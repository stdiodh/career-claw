# 운영 가이드

이 문서는 Career Feed를 GitHub Actions에서 실행하고 Discord Webhook으로 브리핑을 전송하기 위한 운영 기준을 정리한다.

## 기본 운영

KR Premium v2는 아래 두 알림만 기본 자동 운영으로 둔다.

| Workflow | 주기 | 목표 시각 | 내용 |
| --- | ---: | ---: | --- |
| `Daily Korea Tech Brief` | 월~금 | 09:10 KST | 한국 AI 테크, 백엔드/개발자 기술, 오픈소스 기여 후보 |
| `Weekly Backend Career Brief` | 월요일 | 09:30 KST | 백엔드 인턴, 신입/주니어, 해커톤, 공모전, 경진대회 |

기존 `Manual Legacy Korea Premium Brief`와 `Manual Free RSS Career Feed`는 수동 백업으로만 유지한다.

## GitHub Secrets 설정

GitHub 저장소의 `Settings` > `Secrets and variables` > `Actions`에서 다음 Secrets를 등록한다.

### 기본 운영 Secrets

| Secret | 설명 |
| --- | --- |
| `OPENAI_API_KEY` | Codex 편집에 사용하는 OpenAI API Key |
| `NAVER_CLIENT_ID` | Naver News Search API 후보 수집용 |
| `NAVER_CLIENT_SECRET` | Naver News Search API 후보 수집용 |
| `DISCORD_WEBHOOK_KR_TECH_DAILY` | Daily Korea Tech Brief를 전송할 Discord Webhook URL |
| `DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY` | Weekly Backend Career Brief를 전송할 Discord Webhook URL |

Daily workflow 필수 검사는 `OPENAI_API_KEY`, `DISCORD_WEBHOOK_KR_TECH_DAILY`를 대상으로 한다. Weekly workflow 필수 검사는 `OPENAI_API_KEY`, `DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY`를 대상으로 한다. Naver Secrets가 없으면 RSS/공식 URL 후보만 수집하므로 품질이 낮아질 수 있다.

### Legacy/manual로만 남길 수 있는 Secrets

| Secret | 필요한 경우 |
| --- | --- |
| `DISCORD_WEBHOOK_KR_PREMIUM_BRIEF` | 기존 4섹션 통합 KR Premium manual legacy 전송 |
| `DISCORD_WEBHOOK_DAILY_OVERVIEW` | 수동 무료 RSS Daily Overview 전송 |
| `DISCORD_WEBHOOK_AI_NEWS` | 수동 무료 RSS AI News 전송 |
| `DISCORD_WEBHOOK_BACKEND_NEWS` | 수동 무료 RSS Backend News 전송 |
| `DISCORD_WEBHOOK_SECURITY_ALERTS` | 수동 무료 RSS Security Alerts 전송 |
| `DISCORD_WEBHOOK_BACKEND_TECH` | legacy Backend Tech 전송 |
| `DISCORD_WEBHOOK_JOB_FEED` | legacy Job Feed 전송 |

Secret 값은 코드, 문서 예시, 커밋 로그에 남기지 않는다.

## Workflow 실행 방식

### Daily Korea Tech Brief

- 파일: `.github/workflows/kr-tech-daily.yml`
- 예약 실행 요청: 평일 `09:10 Asia/Seoul`
- GitHub Actions cron: `10 0 * * 1-5`
- 수동 실행: `workflow_dispatch`
- 후보 수집: `python3 scripts/collect-kr-feeds.py --mode daily-tech`
- report: `reports/briefs/kr-tech-daily.md`
- summary: `reports/briefs/kr-tech-daily-codex-summary.md`
- 검증: `--type daily-tech`

실행 순서는 다음과 같다.

1. 한국 AI 테크/백엔드 기술/오픈소스 기여 후보 수집
2. runtime prompt 생성
3. Codex Action으로 실제 report 파일 작성
4. Markdown 품질 검증
5. `DISCORD_WEBHOOK_KR_TECH_DAILY`로 Discord 전송
6. 후보, report, summary artifact 업로드

### Weekly Backend Career Brief

- 파일: `.github/workflows/kr-backend-career-weekly.yml`
- 예약 실행 요청: 월요일 `09:30 Asia/Seoul`
- GitHub Actions cron: `30 0 * * 1`
- 수동 실행: `workflow_dispatch`
- 후보 수집: `python3 scripts/collect-kr-feeds.py --mode weekly-career`
- report: `reports/briefs/kr-backend-career-weekly.md`
- summary: `reports/briefs/kr-backend-career-weekly-codex-summary.md`
- 검증: `--type weekly-career`

실행 순서는 다음과 같다.

1. 백엔드 커리어 후보 수집
2. runtime prompt 생성
3. Codex Action으로 실제 report 파일 작성
4. Markdown 품질 검증
5. `DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY`로 Discord 전송
6. 후보, report, summary artifact 업로드

### Manual Legacy Korea Premium Brief

`.github/workflows/kr-premium-brief.yml`은 기존 4섹션 통합 브리핑을 수동 백업으로 보존한다.

- 자동 schedule 없음
- `workflow_dispatch` 전용
- `--search` 미사용
- 실제 report: `reports/briefs/kr-premium-daily.md`
- Codex Action `output-file`: `reports/briefs/kr-premium-action-summary.md`

### Manual Free RSS Career Feed

`.github/workflows/daily-feed.yml`은 무료 RSS 백업 workflow다.

- 자동 schedule 없음
- OpenAI API 사용 없음
- legacy/manual free RSS Webhook Secret이 있을 때만 Discord 전송 가능

## 후보 수집 출력

| 모드 | 출력 파일 |
| --- | --- |
| `--mode daily-tech` | `reports/candidates/kr-ai-tech-news.json` |
| `--mode daily-tech` | `reports/candidates/kr-backend-tech-news.json` |
| `--mode daily-tech` | `reports/candidates/kr-oss-contribution-opportunities.json` |
| `--mode weekly-career` | `reports/candidates/kr-backend-career-events.json` |
| legacy/all | `reports/candidates/kr-security-alerts.json` |

`kr-security-alerts`는 삭제하지 않고 legacy/manual 용도로 남긴다. 기본 daily 알림에서는 보안 알림을 제외하고, GitHub issue 기반 오픈소스 기여 후보를 최대 1개 포함한다. 오픈소스 후보 수집은 issue 조회와 추천만 수행하며 자동 댓글, PR 생성, assign은 하지 않는다.

GitHub Actions에서는 workflow의 `github.token`을 `GITHUB_TOKEN`으로 주입해 GitHub Issues API를 조회한다. 로컬에서는 `GITHUB_TOKEN` 또는 `GH_TOKEN`이 없어도 공개 API로 가능한 범위에서 동작하지만 rate limit에 걸릴 수 있다.

## 로컬 검증

Secret 없이 기본 파일 구조, Python 문법, validation fixture, dry-run을 확인한다.

```bash
./scripts/validate.sh
python3 scripts/collect-kr-feeds.py --dry-run
python3 scripts/collect-kr-feeds.py --mode daily-tech --dry-run
python3 scripts/collect-kr-feeds.py --mode weekly-career --dry-run
git diff --check
```

실제 후보 수집은 Naver API Secret을 셸 환경변수나 GitHub Actions Secrets로 주입한 뒤 실행한다.

```bash
python3 scripts/collect-kr-feeds.py --mode daily-tech
python3 scripts/collect-kr-feeds.py --mode weekly-career
```

## 시간 정책

GitHub Actions schedule은 UTC 기준이며, 실행 시각은 정확 보장이 아니라 목표 시각이다. GitHub 인프라 상태에 따라 지연되거나 누락될 수 있다.

- `10 0 * * 1-5`: 평일 09:10 KST 실행 요청
- `30 0 * * 1`: 월요일 09:30 KST 실행 요청

정확한 실행 시각이 필요하면 GitHub Actions schedule만으로는 부족하며, 외부 scheduler가 `repository_dispatch` 또는 `workflow_dispatch`를 호출하는 구조를 별도로 검토한다.

## 실제 아침 알림 확인 절차

1. GitHub Actions에서 `Daily Korea Tech Brief` 또는 `Weekly Backend Career Brief` 실행 이력을 확인한다.
2. 실행 로그에서 후보 수집, Codex 편집, Markdown 검증, Discord 전송 단계가 모두 성공했는지 확인한다.
3. artifact에 후보 JSON과 실제 report 파일이 포함됐는지 확인한다.
4. Discord 채널에 브리핑이 도착했는지 확인한다.
5. 내용이 주가/홍보/시니어 채용 중심으로 흐르지 않았는지 확인한다.

## 수동 실행 전 체크리스트

1. 변경 사항이 `main` 브랜치에 push되어 있는지 확인한다.
2. GitHub Actions에 `OPENAI_API_KEY`, `DISCORD_WEBHOOK_KR_TECH_DAILY`, `DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY`가 등록되어 있는지 확인한다.
3. 후보 품질을 위해 `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET`이 등록되어 있는지 확인한다.
4. 로컬에서 `./scripts/validate.sh`가 통과했는지 확인한다.
5. OpenAI 비용이 발생할 수 있음을 확인한다.
6. 같은 workflow를 반복해서 `workflow_dispatch`하지 않는다.

## GitHub Actions 수동 실행 방법

1. GitHub 저장소의 `Actions` 탭으로 이동한다.
2. 왼쪽 workflow 목록에서 `Daily Korea Tech Brief` 또는 `Weekly Backend Career Brief`를 선택한다.
3. `Run workflow`를 선택한다.
4. branch를 `main`으로 선택한다.
5. 실행을 시작하고 완료 상태가 성공인지 확인한다.

비용 방지를 위해 최초 테스트는 daily 1회, weekly 1회만 실행한다.

## 실패 시 확인할 것

1. Secret 누락: `OPENAI_API_KEY`, `DISCORD_WEBHOOK_KR_TECH_DAILY`, `DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY` 등록 여부를 확인한다.
2. Naver API 실패: `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET`과 API 사용 한도를 확인한다.
3. OpenAI quota/billing: 결제 한도, 월 예산, quota 오류를 확인한다.
4. Codex Action 실패: runtime prompt 생성과 `codex-args`를 확인한다.
5. report 파일 미생성: Codex가 실제 report path에 Markdown을 작성했는지 확인한다.
6. Markdown 검증 실패: `scripts/validate-kr-premium-brief.py` 실패 메시지를 확인한다.
7. Discord Webhook 실패: Webhook 삭제, 채널 권한, Secret 이름을 확인한다.
8. artifact 업로드 실패: report/candidate 파일 경로를 확인한다.
9. GitHub schedule 지연: schedule 이벤트 지연 또는 누락 가능성을 고려한다.

## Discord 메시지 포맷

Discord에서 브리핑 본문을 먼저 읽을 수 있도록 링크와 embed preview를 제한한다.

- `scripts/send-discord.py`는 Discord webhook payload에 `SUPPRESS_EMBEDS` flag를 설정한다.
- KR Premium v2 항목 링크 텍스트는 `[원문 보기](URL)` 형식을 기본으로 한다.
- 한 항목에서 같은 URL을 중복해서 쓰지 않는다.
- Markdown 표는 사용하지 않는다.

## 사용자가 GitHub에서 직접 할 일

1. 새 Daily/Weekly workflow가 `main`에 반영된 뒤 Actions 탭에서 schedule과 manual 실행 가능 여부를 확인한다.
2. `OPENAI_API_KEY`, `DISCORD_WEBHOOK_KR_TECH_DAILY`, `DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY`, `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET`이 등록되어 있는지 확인한다.
3. 새 구조가 Discord에 정상 도착하면 legacy Webhook Secrets 삭제 여부를 판단한다.
