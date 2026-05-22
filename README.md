# Career Feed

## 소개

Career Feed는 AI와 백엔드 개발자에게 필요한 최신 기술 뉴스를 매일 Discord로 전달하는 자동 브리핑 프로젝트입니다.

GitHub Actions가 정해진 시간에 실행되고, Codex live web search로 최신 정보를 확인한 뒤, Markdown 브리핑을 생성해 Discord Webhook으로 전송합니다. 별도 상시 서버나 Discord Bot을 운영하지 않는 가벼운 자동화 구조를 지향합니다.

## 문제 정의

개발자가 매일 확인해야 하는 AI 모델, 백엔드 프레임워크, 클라우드, 보안, 오픈소스 릴리스 정보는 여러 출처에 흩어져 있습니다.

공식 블로그, 릴리스 노트, 보안 공지, GitHub Release를 매일 직접 확인하는 것은 시간이 들고, 중요한 변경 사항을 놓치기 쉽습니다. Career Feed는 매일 아침 확인할 가치가 있는 소식만 짧게 모아 Discord 채널로 전달해 정보 확인 비용을 줄이는 것을 목표로 합니다.

## 핵심 기능

현재 구현된 1차 MVP 범위는 다음과 같습니다.

- 매일 `09:07 Asia/Seoul` 자동 실행
- AI/백엔드 중심 뉴스 3~5개 선별
- Codex live web search 기반 최신 정보 확인
- Markdown 브리핑 생성
- Discord Webhook 전송
- GitHub Actions `workflow_dispatch` 수동 실행 지원
- 생성된 리포트의 GitHub Actions artifact 업로드
- 로컬 검증용 샘플 리포트 생성 및 스크립트 점검

초기 범위에 포함하지 않는 항목은 다음과 같습니다.

- 상시 실행 서버
- Discord Gateway Bot
- Slash Command
- 데이터베이스 저장
- 로그인/회원 기능
- 웹 대시보드

## 아키텍처

Career Feed는 GitHub Actions 실행 환경 안에서 브리핑 생성과 전송을 끝냅니다.

```text
GitHub Actions schedule / workflow_dispatch
        |
        v
Codex live web search
        |
        v
reports/YYYY-MM-DD-daily-news.md
        |
        v
Discord Webhook
        |
        v
Discord channel
```

역할은 다음과 같습니다.

- GitHub Actions: 예약 실행, 수동 실행, artifact 업로드를 담당합니다.
- Codex: 최신 웹 검색으로 후보 뉴스를 확인하고 최종 브리핑을 생성합니다.
- `reports/`: 실행 중 생성되는 Markdown 리포트 경로입니다.
- `scripts/send-discord.py`: Markdown 리포트를 Discord Webhook으로 전송합니다.
- Discord Webhook: 생성된 브리핑을 지정된 채널에 게시합니다.

## 필요한 Secrets

GitHub 저장소의 `Settings` > `Secrets and variables` > `Actions`에 다음 Secrets를 등록해야 합니다.

| Secret | 설명 |
| --- | --- |
| `OPENAI_API_KEY` | Codex 실행과 live web search에 사용할 OpenAI API 키 |
| `DISCORD_WEBHOOK_URL` | 브리핑을 전송할 Discord Webhook URL |

Secret 값은 코드, 문서 예시, 커밋 로그에 저장하지 않습니다.

## 실행 방법

### GitHub Actions Schedule

workflow는 매일 `09:07 Asia/Seoul`에 실행됩니다. GitHub Actions cron은 UTC 기준이므로 workflow에는 `00:07 UTC`로 설정되어 있습니다.

```yaml
on:
  schedule:
    - cron: "7 0 * * *"
```

schedule은 기본 브랜치에 있는 workflow 파일을 기준으로 동작합니다.

### Workflow Dispatch

수동 테스트는 GitHub Actions 화면에서 실행합니다.

1. GitHub 저장소의 `Actions` 탭으로 이동합니다.
2. `Daily Career Feed News` workflow를 선택합니다.
3. `Run workflow`를 클릭합니다.
4. 실행 로그에서 Codex 리포트 생성, Markdown 검증, Discord 전송, artifact 업로드 단계를 확인합니다.

### 로컬 검증

Secret 없이 기본 파일 구조와 Python 스크립트 문법을 확인할 수 있습니다.

```bash
./scripts/validate.sh
```

검증 스크립트는 다음을 수행합니다.

- `scripts/send-discord.py` 문법 검사
- `reports/sample-daily-news.md` 샘플 리포트 생성
- prompt 파일과 workflow 파일 존재 여부 확인

실제 Discord 전송은 자동으로 실행하지 않습니다. 샘플 리포트를 전송하려면 `DISCORD_WEBHOOK_URL`을 설정한 뒤 명시적으로 실행합니다.

```bash
python3 scripts/send-discord.py reports/sample-daily-news.md
```

## 디렉터리 구조

```text
career-feed/
├─ .github/
│  ├─ codex/
│  │  └─ prompts/
│  │     └─ daily-news.md
│  └─ workflows/
│     └─ daily-news.yml
├─ docs/
│  ├─ architecture.md
│  └─ operations.md
├─ reports/
│  └─ .gitkeep
├─ scripts/
│  ├─ make-sample-report.py
│  ├─ send-discord.py
│  └─ validate.sh
├─ .gitignore
├─ AGENTS.md
└─ README.md
```

## 운영 정책

- daily report는 GitHub Actions artifact로 보관합니다.
- daily report Markdown은 repository에 자동 커밋하거나 push하지 않습니다.
- `reports/.gitkeep`만 유지하고, `reports/*.md`, `reports/*.markdown`은 `.gitignore` 대상으로 둡니다.
- Discord 알림을 1차 운영 결과로 봅니다.
- Secrets는 코드에 저장하지 않고 GitHub Secrets 또는 로컬 환경변수로만 주입합니다.
- 장기 보관이 필요해지면 일일 workflow에 자동 커밋을 추가하지 않고 별도의 archive workflow로 분리합니다.

## Roadmap

아래 항목은 아직 구현되지 않은 확장 계획입니다.

- 채용공고 알림
- 기술 블로그 추천
- GitHub Release 알림
- CVE/보안 알림
- 관심 키워드 설정
- Discord 채널 분리
