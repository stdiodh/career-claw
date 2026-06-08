# career-feed

![Career Feed social preview](./docs/assets/career-feed-social-preview.png)

## 한 줄 소개

Career Feed는 Java/Kotlin 백엔드 학습자와 주니어 개발자가 오늘 볼 학습 주제, 커리어 정보, OSS 후보를 GitHub Actions와 Discord로 받아볼 수 있게 돕는 공개 자동 브리핑 workflow입니다.

## 프로젝트가 해결하려는 문제

백엔드 학습과 커리어 준비에는 자료가 부족하지 않습니다.

문제는 자료가 흩어져 있고, 매일 무엇을 우선순위에 둘지 판단하기 어렵다는 점입니다.

다음 질문을 반복해서 마주하는 사람을 위해 만들어졌습니다.

- Java, Spring Boot, JVM, Kotlin 학습 다음 단계를 고르기 어렵습니다.
- Programmers 문제 풀이 루틴을 꾸준히 관리하기 어렵습니다.
- 첫 OSS 기여 후보를 찾고 안전성을 확인하기 어렵습니다.
- 한국 개발/AI 뉴스 중 백엔드 커리어 관점에서 중요한 내용을 고르기 어렵습니다.
- 채용, 인턴, 대외활동, 해커톤 정보를 매주 직접 확인하기 어렵습니다.
- Discord 스터디나 멘토링 그룹에 꾸준히 공유할 브리핑을 만들 시간이 부족합니다.

커리어 판단을 자동화하지 않습니다.

대신 검토 가능한 공개 출처와 안전한 기본값을 바탕으로, 매일 확인할 수 있는 작은 성장 피드를 만드는 것을 목표로 합니다.

## What it generates

| Output | Description |
| --- | --- |
| Daily Backend Brief | Spring Boot/JVM 학습, Programmers PS 루틴, Spring/JVM/Kotlin OSS 후보, 주니어 백엔드 실무 지식, 용어 정리를 포함한 일일 브리핑 |
| Korea Dev/AI News Daily | 한국 개발/AI 뉴스 후보를 수집하고 품질 평가를 거쳐 Discord에 보낼 수 있는 일일 뉴스 피드 |
| Backend Career Site Radar | 채용, 인턴, 대외활동, 해커톤, 공모전 관련 공개 출처를 주기적으로 확인하는 주간 커리어 레이더 |
| PS Progress Update | Programmers 풀이 완료 여부를 progress 파일에 기록하는 수동 업데이트 |
| Validation Reports | 브리핑 품질, safe OSS 후보, fallback, 전송 정책을 확인하기 위한 검증 출력 |

## How it works

정적 설정, GitHub Actions, OpenAI API, validator, Discord Webhook을 조합합니다.

```text
Static config and progress data
  ↓
GitHub Actions schedule or workflow_dispatch
  ↓
Collectors and renderers
  ↓
OpenAI API assisted draft generation
  ↓
Validation and dry-run artifacts
  ↓
Discord Webhook delivery when enabled
```

주요 workflow는 다음과 같습니다.

| Workflow | File | Main output |
| --- | --- | --- |
| Daily Backend Brief | `.github/workflows/kr-tech-daily.yml` | Backend daily study brief |
| Korea Dev/AI News Daily | `.github/workflows/kr-tech-news-daily.yml` | Korea development and AI news feed |
| Backend Career Site Radar | `.github/workflows/kr-backend-career-weekly.yml` | Backend career site radar brief |
| Mark PS Solved | `.github/workflows/mark-ps-solved.yml` | `data/ps-progress.json` update |

Workflow 파일의 실제 cron, inputs, dispatch option이 README 설명보다 우선합니다.

## Quick Start

fork해서 GitHub Actions와 Discord에서 운영하려면 다음 순서로 시작합니다.

1. 이 repository를 fork합니다.
2. GitHub Actions Secrets에 API key와 Discord webhook을 등록합니다.
3. GitHub Actions Variables에 timezone, 실행 시간, OSS 후보 freshness, delivery flag를 등록합니다.
4. `Daily Korea Tech Brief` workflow를 `dry_run=true`로 실행합니다.
5. generated artifacts와 validation reports를 확인합니다.
6. 결과가 맞으면 `CAREER_FEED_DISCORD_DELIVERY_ENABLED=true`로 Discord 전송을 켭니다.

전체 walkthrough는 [Fork Setup Guide](./docs/getting-started/fork-setup.md)를 따라가세요.

로컬에서 문서와 정책 검증을 실행하려면 다음 명령을 사용합니다.

```bash
./scripts/validate.sh
```

## Configuration

민감한 값과 실행 설정값을 분리합니다.

- API key와 Discord webhook URL은 GitHub Actions Secrets에 둡니다.
- timezone, 목표 실행 시간, OSS 후보 freshness, Discord delivery flag는 GitHub Actions Variables에 둡니다.
- GitHub Actions cron은 Variables로 직접 바뀌지 않으므로 runtime gate가 scheduled run 안에서 실행 여부를 판단합니다.
- 첫 실행은 `dry_run=true`로 시작하고, artifact와 validation report를 확인한 뒤 Discord delivery를 켭니다.

전체 설정값은 [Runtime Configuration](./docs/getting-started/runtime-configuration.md)을 참고해 주세요.

## Safety / Limitations

안전한 기본 동작을 우선합니다.

- Discord delivery는 기본적으로 꺼져 있습니다.
- `dry_run=true`이면 Discord로 전송하지 않습니다.
- 생성된 브리프는 Discord 전송 전에 validator를 통과해야 합니다.
- OSS 후보는 기본적으로 `created_at` 기준 최근 30일 이내 issue만 추천합니다.
- safe 후보가 없으면 오래된 issue를 억지로 추천하지 않고 fallback routine을 출력합니다.
- 외부 GitHub 저장소에 자동 댓글, PR, assign, label 변경을 하지 않습니다.

상시 실행 서버, 데이터베이스, 웹 대시보드, Discord Gateway Bot, Slash Command, 채용 매칭 서비스가 아닙니다.

브리핑은 학습과 탐색의 시작점이며, 사용자가 최종 확인해야 합니다.

## Repository structure

| Path | Purpose |
| --- | --- |
| `.github/workflows/` | GitHub Actions workflow |
| `configs/` | 브리핑과 수집 정책에 사용하는 정적 설정 |
| `data/` | PS progress와 작은 상태 파일 |
| `docs/` | 사용자, 운영자, 기여자 문서 |
| `scripts/` | 수집, 렌더링, 검증, 전송 스크립트 |
| `tests/` | 정책과 스크립트 검증 테스트 |

Generated reports are written under `reports/` during workflow runs and are not meant to be committed by default.

## Documentation

Start with these documents:

| Document | Purpose |
| --- | --- |
| [Docs Index](./docs/README.md) | 전체 문서 지도와 읽는 순서 |
| [Fork Setup Guide](./docs/getting-started/fork-setup.md) | fork 후 첫 dry-run과 Discord delivery 설정 |
| [Runtime Configuration](./docs/getting-started/runtime-configuration.md) | Secrets, Variables, runtime gate 설정 |
| [Usage Guide](./docs/getting-started/usage.md) | workflow 실행, artifact 확인, dry-run 사용법 |
| [OSS Candidate Policy](./docs/policies/oss-candidate-policy.md) | 최근 OSS 후보와 fallback 정책 |
| [Contributing](./CONTRIBUTING.md) | issue/PR 기여 방법 |
| [Roadmap](./docs/project/roadmap.md) | 현재 범위와 향후 방향 |

## Contributing

Contributions are welcome in small, reviewable changes.

Good starting points:

- documentation improvements
- source suggestions
- sample output improvements
- validation fixture improvements
- Java/Kotlin backend learning topic suggestions
- recent OSS candidate suggestions

Read [CONTRIBUTING.md](./CONTRIBUTING.md) and the [Contribution Guide Index](./docs/contributing/README.md) before opening a PR.

커뮤니티 기대 사항은 [Code of Conduct](./CODE_OF_CONDUCT.md)를 따릅니다.

## License

MIT License로 배포됩니다.

자세한 내용은 [LICENSE](./LICENSE)를 확인해 주세요.
