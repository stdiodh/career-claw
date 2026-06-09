# Career Feed

![Career Feed social preview](./docs/assets/career-feed-social-preview.png)

## 30-Second Overview

Career Feed는 Java/Kotlin 백엔드 학습자와 주니어 개발자를 위한 공개 커리어 브리핑 자동화입니다.
GitHub Actions가 정해진 시간 또는 수동 실행으로 학습 주제, 뉴스, OSS 후보, 커리어 사이트 레이더를 생성합니다.
생성 결과는 Markdown artifact와 validation report로 먼저 확인하고, 사용자가 켠 경우에만 Discord Webhook으로 전송합니다.
상시 서버, 데이터베이스, Discord Bot, Slash Command 없이 fork 기반으로 운영하는 프로젝트입니다.

## What You Get

| Output | What it includes | Example |
| --- | --- | --- |
| Daily Backend Brief | Spring Boot/JVM 학습, Programmers PS 루틴, Spring/JVM/Kotlin OSS 후보, 주니어 백엔드 실무 지식 | [sample](./docs/examples/daily-backend-brief.example.md) |
| Korea Dev/AI News Daily | 한국 개발/AI 뉴스 후보, 품질 기준, 백엔드 커리어 관점의 읽을거리 | [sample](./docs/examples/korea-dev-ai-news-daily.example.md) |
| Backend Career Site Radar | 채용, 인턴, 대외활동, 해커톤, 공모전 관련 공개 출처 확인 루틴 | [sample](./docs/examples/career-site-radar.example.md) |

전체 예시는 [Sample Output](./docs/getting-started/sample-output.md), 실행 화면은 [Demo Guide](./docs/demo.md)에서 확인할 수 있습니다.

## Quick Start Path

| 목적 | 문서 |
| --- | --- |
| 결과물을 먼저 보고 싶음 | [Sample Output](./docs/getting-started/sample-output.md) |
| 내 Discord에서 실행하고 싶음 | [Fork Setup Guide](./docs/getting-started/fork-setup.md) |
| 설정값을 바꾸고 싶음 | [Runtime Configuration](./docs/getting-started/runtime-configuration.md) |
| 운영 방법이 궁금함 | [Usage Guide](./docs/getting-started/usage.md) |
| 기여하고 싶음 | [Contributing](./CONTRIBUTING.md) |

첫 실행은 [Fork Setup Guide](./docs/getting-started/fork-setup.md)를 따라 `dry_run=true`로 시작하세요.

## Project Status

- Status: Early Public OSS
- Stable release: No stable release yet
- GitHub Releases: none published as of the 2026-06-09 documentation audit
- Release tags: none found in local or `origin` tag list during the same audit
- `v0.1.0` 문서는 현재 release draft이며, 실제 release tag보다 우선하지 않습니다.

Workflow 파일의 실제 cron, inputs, dispatch option이 README 설명보다 우선합니다.

## How It Works

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

| Workflow | File | Main output |
| --- | --- | --- |
| Daily Backend Brief | `.github/workflows/kr-tech-daily.yml` | `reports/briefs/kr-tech-daily.md` |
| Korea Dev/AI News Daily | `.github/workflows/kr-tech-news-daily.yml` | `reports/briefs/kr-tech-news-daily.md` |
| Backend Career Site Radar | `.github/workflows/kr-backend-career-weekly.yml` | `reports/briefs/kr-backend-career-weekly.md` |
| Mark PS Solved | `.github/workflows/mark-ps-solved.yml` | `data/ps-progress.json` update |

## Safety / Limitations

- API key와 Discord webhook URL은 GitHub Actions Secrets 또는 로컬 환경변수에만 둡니다.
- Discord delivery는 기본적으로 꺼져 있으며, `dry_run=true`이면 Discord로 전송하지 않습니다.
- 생성된 브리프는 Discord 전송 전에 validator를 통과해야 합니다.
- OSS 후보는 기본적으로 `created_at` 기준 최근 30일 이내 issue만 추천합니다.
- safe 후보가 없으면 오래된 issue를 억지로 추천하지 않고 fallback routine을 출력합니다.
- 외부 GitHub 저장소에 자동 댓글, PR, assign, label 변경을 하지 않습니다.
- Career Feed는 채용 매칭 서비스나 최종 커리어 조언이 아니며, 사용자가 artifact와 링크를 최종 확인해야 합니다.

상세 설정값은 [Runtime Configuration](./docs/getting-started/runtime-configuration.md), 운영 흐름은
[Usage Guide](./docs/getting-started/usage.md)를 참고하세요.

## Repository Structure

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

문서 전체 경로는 [Docs Index](./docs/README.md)를 사용합니다.

로컬에서 문서와 정책 검증을 실행하려면 다음 명령을 사용합니다.

```bash
./scripts/validate.sh
```

## Contributing

작고 검토 가능한 변경을 권장합니다.

좋은 시작점:

- documentation improvements
- source suggestions
- sample output improvements
- validation fixture improvements
- Java/Kotlin backend learning topic suggestions
- recent OSS candidate suggestions

PR을 열기 전에 [CONTRIBUTING.md](./CONTRIBUTING.md)와
[Contribution Guide Index](./docs/contributing/README.md)를 읽어 주세요.

커뮤니티 기대 사항은 [Code of Conduct](./CODE_OF_CONDUCT.md)를 따릅니다.

## License

MIT License로 배포됩니다.

자세한 내용은 [LICENSE](./LICENSE)를 확인해 주세요.
