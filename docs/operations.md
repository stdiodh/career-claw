# 운영 가이드

이 문서는 Career Feed를 GitHub Actions에서 실행하고 Discord Webhook으로 브리핑을 전송하기 위한 운영 기준을 정리한다.

## GitHub Secrets 설정

GitHub 저장소의 `Settings` > `Secrets and variables` > `Actions`에서 다음 Secrets를 등록한다.

| Secret | 설명 |
| --- | --- |
| `OPENAI_API_KEY` | Codex 기반 브리핑 생성과 live web search에 사용할 OpenAI API 키 |
| `DISCORD_WEBHOOK_URL` | 브리핑을 전송할 Discord Webhook URL |

주의 사항:

- Secret 값은 코드, 문서 예시, 커밋 로그에 남기지 않는다.
- 로컬 테스트가 필요하면 `.env` 같은 커밋되지 않는 파일이나 셸 환경변수를 사용한다.
- Webhook URL은 토큰과 같은 민감 정보로 취급한다.

## Workflow 실행 방식

Career Feed의 일일 브리핑 workflow는 `.github/workflows/daily-news.yml`에 정의되어 있다.

- Workflow 이름: `Daily Career Feed News`
- 예약 실행: 매일 `09:07 Asia/Seoul`
- GitHub Actions cron: `7 0 * * *`
- 수동 실행: `workflow_dispatch`

GitHub Actions의 schedule 이벤트는 기본 브랜치에 있는 workflow 파일을 기준으로 동작한다. 기본 브랜치에 workflow가 반영되지 않았거나 비활성화된 경우 예약 실행은 동작하지 않는다.

workflow는 실행 시점의 KST 시간을 계산해 `.github/codex/prompts/daily-news.md` 안의 `{{KST_NOW}}`를 치환한 임시 runtime prompt를 만든다. Codex는 live web search를 사용해 브리핑을 생성하고, 결과를 `reports/YYYY-MM-DD-daily-news.md`에 저장한 뒤 Discord Webhook으로 전송한다. 생성된 리포트는 GitHub Actions artifact로도 업로드된다.

## 수동 실행 방법

GitHub Actions 화면에서 다음 방식으로 수동 실행한다.

1. GitHub 저장소의 `Actions` 탭으로 이동한다.
2. `Daily Career Feed News` workflow를 선택한다.
3. `Run workflow`를 클릭한다.
4. 실행 대상 브랜치를 확인하고 `Run workflow`를 실행한다.
5. 실행 로그에서 runtime prompt 생성, Codex 리포트 생성, Markdown 검증, Discord 전송, artifact 업로드 단계가 성공했는지 확인한다.
6. Discord 채널에 브리핑 메시지가 도착했는지 확인한다.

수동 실행은 다음 상황에서 사용한다.

- GitHub Secrets 설정 직후 연결을 확인할 때
- 프롬프트를 수정한 뒤 결과 품질을 확인할 때
- Discord Webhook 재발급 후 전송을 확인할 때
- 예약 실행 실패 원인을 재현할 때

## 로컬 전송 테스트

이미 생성된 Markdown 리포트가 있다면 로컬에서 Discord 전송 스크립트만 확인할 수 있다.

```bash
DISCORD_WEBHOOK_URL="..." python3 scripts/send-discord.py reports/YYYY-MM-DD-daily-news.md
```

실제 Webhook URL은 터미널 히스토리나 로그에 남지 않도록 주의한다. 필요한 경우 일회성 셸 환경변수나 커밋되지 않는 `.env` 파일을 사용한다.

## 로컬 검증 방법

Secret 없이 기본 파일 구조, Python 문법, 샘플 리포트 생성을 확인하려면 다음 명령을 실행한다.

```bash
./scripts/validate.sh
```

검증 스크립트는 다음을 확인한다.

- `python3 -m py_compile scripts/send-discord.py`
- `python3 scripts/make-sample-report.py`
- `reports/sample-daily-news.md` 생성 여부
- `.github/codex/prompts/daily-news.md` 존재 여부
- `.github/workflows/daily-news.yml` 존재 여부

`DISCORD_WEBHOOK_URL`이 설정되어 있어도 `validate.sh`는 자동으로 Discord 전송을 실행하지 않는다. 실제 전송 테스트는 사용자가 아래 명령을 명시적으로 실행할 때만 수행한다.

```bash
python3 scripts/send-discord.py reports/sample-daily-news.md
```

## Artifact 확인 방법

1차 MVP에서는 매일 생성된 Markdown 리포트를 GitHub 저장소에 자동 commit/push하지 않는다. 결과 확인은 Discord 알림과 GitHub Actions artifact를 기준으로 한다.

workflow가 끝나면 실행 상세 화면의 artifact 영역에서 `career-feed-daily-news-YYYY-MM-DD` 파일을 내려받아 생성된 Markdown 리포트를 확인할 수 있다. Discord 전송이 실패하더라도 리포트 파일이 생성된 경우 artifact 업로드 단계에서 확인할 수 있다.

저장 정책은 다음과 같다.

- `reports/.gitkeep`만 저장소에 유지한다.
- `reports/*.md`, `reports/*.markdown`은 `.gitignore` 대상이다.
- `reports/YYYY-MM-DD-daily-news.md`는 Actions 실행 중 생성되고 artifact로 업로드된다.
- `reports/sample-daily-news.md`는 로컬 테스트용으로 생성될 수 있지만 기본 커밋 대상이 아니다.
- 장기 보관이 필요해지면 일일 workflow에 자동 커밋을 넣지 않고 별도의 archive workflow로 분리한다.

## 실패 시 확인할 것

실패가 발생하면 다음 순서로 확인한다.

- `OPENAI_API_KEY` Secret이 등록되어 있는지 확인한다.
- `DISCORD_WEBHOOK_URL` Secret이 등록되어 있고 값이 최신인지 확인한다.
- workflow가 기본 브랜치에 존재하는지 확인한다.
- `reports/` 디렉터리 생성 단계가 성공했는지 확인한다.
- Discord Webhook이 삭제되거나 대상 채널 권한이 변경되지 않았는지 확인한다.
- 생성된 Markdown 리포트가 비어 있지 않은지 확인한다.
- Discord 메시지 길이가 2000자를 초과하지 않았는지 확인한다.
- GitHub Actions 로그에서 Codex 실행 오류, 네트워크 오류, 인증 오류, API 제한 오류를 확인한다.

## Discord Webhook 재발급 시 주의할 것

Discord Webhook을 재발급하면 기존 URL은 더 이상 사용하지 않는 것을 전제로 운영한다.

- 새 Webhook URL을 GitHub Secret `DISCORD_WEBHOOK_URL`에 즉시 반영한다.
- 이전 Webhook URL이 코드, 문서, 이슈, PR, 로그에 노출되지 않았는지 확인한다.
- 노출 가능성이 있으면 기존 Webhook을 삭제하고 새 Webhook으로 교체한다.
- 재발급 후에는 `workflow_dispatch`로 수동 실행해 메시지 전송을 확인한다.
- Webhook 권한과 대상 채널이 의도한 브리핑 채널인지 확인한다.
