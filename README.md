# career-feed

## 한 줄 소개

Career Feed는 백엔드 지망생과 주니어 개발자가 오늘 공부할 주제, 확인할 커리어 정보, 살펴볼 OSS 후보를 덜 막막하게 고르도록 돕는 공개 자동 브리핑 workflow입니다.

## 프로젝트가 해결하려는 문제

백엔드 학습과 커리어 준비에는 자료가 부족하지 않습니다.

문제는 자료가 너무 흩어져 있고, 매일 무엇을 우선순위에 둘지 판단하기 어렵다는 점입니다.

특히 백엔드 지망생과 주니어 개발자는 다음과 같은 질문을 반복해서 마주합니다.

- Java와 Spring Boot를 공부한 뒤 무엇을 이어서 봐야 할지 모르겠습니다.
- Programmers 문제 풀이를 꾸준히 하고 싶지만 주차별 루틴을 관리하기 어렵습니다.
- OSS에 기여하고 싶지만 beginner-friendly 후보를 찾기 어렵습니다.
- 한국 개발·AI 뉴스가 많아도 백엔드 커리어 관점에서 무엇이 중요한지 고르기 어렵습니다.
- 채용, 인턴, 대외활동, 해커톤 정보를 매주 직접 확인하기 어렵습니다.
- Discord 스터디나 멘토링 그룹에 꾸준히 공유할 브리핑을 만들 시간이 부족합니다.

Career Feed는 이 문제를 GitHub Actions, OpenAI API, Discord Webhook 기반의 반복 가능한 자동화로 줄이려는 초기 단계의 공개 OSS입니다.

## Why career-feed?

Career Feed의 핵심 목표는 거창한 커리어 판단을 자동화하는 것이 아닙니다.

목표는 백엔드 학습자와 주니어 개발자가 매일 확인할 수 있는 작고 검토 가능한 성장 피드를 만드는 것입니다.

이 저장소는 다음 관점을 따릅니다.

- 학습 주제는 Spring Boot, JVM, Kotlin, CS, 실무 백엔드 지식 중심으로 정리합니다.
- PS 루틴은 정적 config와 progress 파일로 관리하며, 제출 결과를 자동 수집하지 않습니다.
- OSS 후보는 beginner-friendly 가능성을 정리하지만 외부 저장소에 자동 행동을 하지 않습니다.
- 한국 개발·AI 뉴스는 sparse하거나 empty한 날이 있어도 정책에 맞으면 정상 결과로 봅니다.
- Discord 전송 전 dry-run, validation report, delivery lock, catch-up 정책을 통해 중복과 오전송 위험을 줄입니다.

이 프로젝트는 초기 단계입니다.

stars, forks, downloads, adoption, active users, organization usage 같은 사용 지표를 과장하지 않습니다.

## Who this helps

Career Feed는 다음 사람과 그룹을 돕기 위해 설계되었습니다.

- Java와 Spring Boot를 중심으로 백엔드 개발을 준비하는 학습자
- 취업 준비와 프로젝트 경험을 동시에 정리해야 하는 주니어 개발자
- 매일 짧은 백엔드 학습 루틴을 유지하려는 개인 학습자
- Discord 기반 스터디나 멘토링 그룹을 운영하는 maintainer
- OSS 기여를 시작하고 싶지만 후보 탐색이 어려운 개발자
- 한국 개발·AI 뉴스와 커리어 정보를 정기적으로 정리하려는 커뮤니티 운영자

Career Feed는 사람을 평가하거나 채용 가능성을 예측하지 않습니다.

브리핑은 학습과 탐색의 시작점입니다.

## What it generates

Career Feed가 생성하거나 관리하는 주요 결과물은 다음과 같습니다.

| Output | Description |
| --- | --- |
| Daily Backend Brief | Spring Boot/JVM 학습, Programmers PS 루틴, Spring/JVM/Kotlin OSS 후보, 주니어 백엔드 실무 지식, 용어 정리를 포함한 일일 브리핑 |
| Korea Dev/AI News Daily | 한국 개발·AI 뉴스 후보를 수집하고 품질 평가를 거쳐 Discord에 보낼 수 있는 일일 뉴스 피드 |
| Backend Career Site Radar | 채용, 인턴, 대외활동, 해커톤, 공모전 관련 공개 출처를 주기적으로 확인하는 주간 커리어 레이더 |
| PS Progress Update | Programmers 풀이 완료 여부를 progress 파일에 기록하는 수동 업데이트 |
| Validation Reports | 브리핑 품질, 스케줄, prompt budget, 전송 정책을 확인하기 위한 검증 출력 |

## What this is not

Career Feed는 운영 범위를 의도적으로 작게 유지합니다.

현재 다음은 운영 범위에 포함하지 않습니다.

- 상시 실행 서버
- 데이터베이스
- 웹 대시보드
- Discord Gateway Bot
- Slash Command
- 사용자 계정 시스템
- 채용 매칭 서비스
- 개인 역량 평가 서비스
- 외부 저장소 자동 댓글
- 외부 저장소 자동 PR
- 외부 저장소 자동 assign
- 외부 저장소 자동 label 변경

특히 OSS 후보 추천은 사람이 검토할 수 있는 정보를 정리하는 데 그칩니다.

Career Feed는 외부 저장소에 자동 댓글, 자동 PR, 자동 assign, 자동 label 변경을 하지 않습니다.

## How it works

Career Feed는 정적 설정, GitHub Actions, OpenAI API, validator, Discord Webhook을 조합합니다.

일반적인 흐름은 다음과 같습니다.

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
Maintainer review when needed
  ↓
Discord Webhook delivery
```

OpenAI API는 브리핑 초안 생성과 정보 정리에 사용됩니다.

최종 운영 정책은 workflow, validation script, maintainer review를 함께 따릅니다.

## Workflow summary

| Workflow | File | Trigger | Main output |
| --- | --- | --- | --- |
| Daily Backend Brief | `.github/workflows/kr-tech-daily.yml` | Scheduled and manual | Backend daily study brief |
| Korea Dev/AI News Daily | `.github/workflows/kr-tech-news-daily.yml` | Scheduled and manual | Korea development and AI news feed |
| Backend Career Site Radar | `.github/workflows/kr-backend-career-weekly.yml` | Manual or weekly operation | Backend career site radar brief |
| Mark PS Solved | `.github/workflows/mark-ps-solved.yml` | Manual | `data/ps-progress.json` update |

Workflow 파일의 실제 cron, inputs, dispatch option이 README 설명보다 우선합니다.

README는 운영 의도와 전체 흐름을 설명하는 문서입니다.

## Schedule / trigger policy

Daily workflow는 기본적으로 예약 실행과 수동 실행을 모두 고려합니다.

운영 정책은 다음 원칙을 따릅니다.

- 기본 실행은 dry-run과 validation 결과를 우선 확인합니다.
- `force_send`는 검증된 상황에서만 사용합니다.
- delivery lock으로 중복 전송 위험을 줄입니다.
- catch-up schedule은 지연이나 누락이 생겼을 때의 보정 용도입니다.
- News Daily는 기준을 만족하는 뉴스가 3개 미만이어도 sparse 또는 empty 정책에 맞으면 성공으로 처리할 수 있습니다.
- 실패 알림 webhook은 선택 secret이며, 없다고 workflow가 실패해서는 안 됩니다.

구체적인 실행 시간은 `.github/workflows/*.yml` 파일과 `scripts/check-workflow-schedules.py` 검증 결과를 기준으로 확인합니다.

## Quick Start

로컬에서 저장소를 확인하려면 다음 순서로 시작합니다.

```bash
git clone https://github.com/stdiodh/career-feed.git
cd career-feed
./scripts/validate.sh
```

GitHub Actions로 실제 브리핑을 운영하려면 필요한 secrets를 먼저 등록합니다.

처음에는 Discord 전송을 바로 켜기보다 dry-run artifacts와 validation reports를 확인하는 것을 권장합니다.

## 사용법과 데모

Career Feed는 GitHub Actions 실행, validation artifacts 확인, Discord Webhook 전송으로 운영합니다.

실행 방법과 결과 형태를 빠르게 확인하려면 [사용 가이드](docs/usage.md)와 [데모 가이드](docs/demo.md)를 참고해 주세요.

데모는 redacted 또는 mock data를 사용합니다.

실제 webhook URL, token, private Discord channel name, personal identifier를 screenshot에 포함하지 않습니다.

## Required secrets

다음 값은 GitHub Secrets 또는 로컬 환경변수로만 다룹니다.

문서, commit, issue, PR, log에 실제 값을 넣지 않습니다.

| Secret | Required | Purpose |
| --- | --- | --- |
| `OPENAI_API_KEY` | Yes | OpenAI API를 사용한 브리핑 초안 생성과 정보 정리 |
| `DISCORD_WEBHOOK_KR_TECH_DAILY` | Yes | Daily Backend Brief Discord 전송 |
| `DISCORD_WEBHOOK_KR_TECH_NEWS_DAILY` | Yes | Korea Dev/AI News Daily Discord 전송 |
| `DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY` | Yes | Backend Career Site Radar Discord 전송 |
| `NAVER_CLIENT_ID` | Optional | 한국 뉴스 후보 수집 또는 품질 개선에 사용하는 Naver API credential |
| `NAVER_CLIENT_SECRET` | Optional | 한국 뉴스 후보 수집 또는 품질 개선에 사용하는 Naver API credential |
| `DISCORD_WEBHOOK_CAREER_FEED_OPS` | Optional | workflow 실패 알림용 Discord Webhook |

`DISCORD_WEBHOOK_CAREER_FEED_OPS`는 선택 값입니다.

이 값이 없을 때도 실패 알림 전송만 생략하고 workflow 자체가 실패하지 않아야 합니다.

## Local validation

문서나 workflow 정책을 수정한 뒤에는 가능한 범위에서 다음 명령을 실행합니다.

```bash
./scripts/validate.sh
```

문서 포맷과 YAML만 확인하는 경우에는 다음 명령도 유용합니다.

```bash
wc -l README.md docs/ecosystem-importance.md docs/oss-program-application.md CONTRIBUTING.md SECURITY.md LICENSE
ruby -e 'require "yaml"; ARGV.each { |p| YAML.load_file(p); puts "YAML OK: #{p}" }' .github/ISSUE_TEMPLATE/*.yml
git diff --check
```

검증 명령은 가능한 한 좁게 시작하고, 변경 범위가 넓어질 때 더 넓은 검증으로 확장합니다.

## Directory structure

주요 디렉터리와 파일은 다음과 같습니다.

| Path | Purpose |
| --- | --- |
| `.github/workflows/` | GitHub Actions workflow 정의 |
| `.github/ISSUE_TEMPLATE/` | 백엔드 커리어 질문, 출처 제안, OSS 후보 제안 issue form |
| `configs/` | 브리핑과 수집 정책에 사용하는 정적 설정 |
| `data/` | PS 진행도와 OSS 후보 진행도 같은 작은 상태 파일 |
| `docs/` | 운영 문서, 정책 문서, 신청서 참고 문서 |
| `reports/` | 실행 중 생성되는 브리핑과 검증 산출물 |
| `scripts/` | 수집, 렌더링, 검증, Discord 전송 스크립트 |
| `tests/` | 저장소 검증을 위한 테스트 |

`reports/` 산출물은 기본적으로 커밋 대상이 아닙니다.

## Documentation

README에서 링크하는 문서는 실제 저장소에 존재하는 문서만 사용합니다.

| Document | Purpose |
| --- | --- |
| [docs/ecosystem-importance.md](docs/ecosystem-importance.md) | 백엔드 생태계에서 Career Feed가 갖는 의미와 한계 |
| [docs/oss-program-application.md](docs/oss-program-application.md) | Codex Open Source Support Program 신청용 답변 초안 |
| [docs/usage.md](docs/usage.md) | GitHub Actions, dry-run, artifacts, Discord 전송 사용 가이드 |
| [docs/demo.md](docs/demo.md) | redacted demo screenshot 준비와 노출 가이드 |
| [docs/assets/demo/README.md](docs/assets/demo/README.md) | demo screenshot/GIF asset의 추가, 교체, 삭제, redaction, 크기 확인 절차 |
| [docs/daily-backend-brief.md](docs/daily-backend-brief.md) | Daily Backend Brief 운영 방식 |
| [docs/daily-news-ops.md](docs/daily-news-ops.md) | Korea Dev/AI News Daily 운영 방식 |
| [docs/career-site-radar.md](docs/career-site-radar.md) | Backend Career Site Radar 운영 방식 |
| [docs/maintainer-guide.md](docs/maintainer-guide.md) | maintainer 검토와 운영 체크리스트 |
| [docs/local-validation.md](docs/local-validation.md) | 로컬 검증 명령과 확인 방법 |
| [docs/oss-candidate-policy.md](docs/oss-candidate-policy.md) | OSS 후보 추천 정책 |
| [docs/community-guide.md](docs/community-guide.md) | 스터디와 커뮤니티에서 재사용하는 방법 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 기여 방식과 PR/issue 작성 기준 |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | 커뮤니티 행동 기준 |
| [docs/contributing/README.md](docs/contributing/README.md) | 기여 세부 문서 index |
| [docs/contributing/good-suggestion-criteria.md](docs/contributing/good-suggestion-criteria.md) | 좋은 제안의 기준과 예시 |
| [docs/contributing/source-suggestion-guide.md](docs/contributing/source-suggestion-guide.md) | 정보 출처 제안 가이드 |
| [docs/contributing/oss-candidate-guide.md](docs/contributing/oss-candidate-guide.md) | OSS 후보 제안 가이드 |
| [docs/contributing/backend-career-question-guide.md](docs/contributing/backend-career-question-guide.md) | 백엔드 커리어 질문 작성 가이드 |
| [docs/contributing/review-policy.md](docs/contributing/review-policy.md) | maintainer review 기준 |

## Backend ecosystem importance

Career Feed는 백엔드 런타임, 프레임워크, 라이브러리처럼 production dependency가 되는 프로젝트가 아닙니다.

대신 백엔드 생태계에 들어오는 학습자와 주니어 개발자의 onboarding friction을 줄이는 공개 성장 인프라를 지향합니다.

이 프로젝트의 중요성은 많은 애플리케이션이 의존하는 패키지인지보다 새로 들어오는 사람들이 꾸준하고 안전하게 학습·기여 루틴을 만들 수 있는지에 있습니다.

자세한 설명은 [docs/ecosystem-importance.md](docs/ecosystem-importance.md)를 참고해 주세요.

## API usage policy

OpenAI API는 maintainer가 검토 가능한 자료를 만들기 위해 사용합니다.

허용하는 사용 범위는 다음과 같습니다.

- 브리핑 초안 생성
- 검증 리포트 요약
- 학습 주제 우선순위화
- OSS 후보 정리
- 뉴스 후보 요약
- issue로 접수된 질문의 분류와 답변 초안 작성

사용하지 않는 범위는 다음과 같습니다.

- 외부 저장소 자동 댓글
- 외부 저장소 자동 PR
- 외부 저장소 자동 assign
- 외부 저장소 자동 label 변경
- 무검토 배포
- 민감 정보 저장
- 채용 가능성이나 개인 역량에 대한 단정적 판단

모든 자동화 결과는 공개 저장소 maintainer가 검토 가능한 형태로 남기는 것을 우선합니다.

## Security and privacy notes

Secret, API key, token, webhook URL, 개인 이메일, OpenAI organization ID 같은 비공개 정보는 문서에 포함하지 않습니다.

공개 issue, PR, commit, log에도 포함하지 않습니다.

민감 정보가 노출된 경우에는 공개 issue에 값을 붙여 넣지 말고 maintainer에게 비공개로 먼저 제보해야 합니다.

이 프로젝트는 현재 GitHub Actions, OpenAI API, Discord Webhook 기반 자동 브리핑 workflow만 운영 범위로 둡니다.

상시 실행 서버, 데이터베이스, 웹 대시보드, Discord Gateway Bot, Slash Command는 현재 운영 범위 밖입니다.

외부 저장소에 자동 댓글, 자동 PR, 자동 assign, 자동 label 변경을 하지 않는다는 정책은 보안과 maintainer 존중을 위한 기본 원칙입니다.

## Contributing

Career Feed welcomes documentation improvements, source suggestions, backend learning topics, and beginner-friendly OSS candidate suggestions.

기여하고 싶다면 먼저 [Contributing](CONTRIBUTING.md)을 확인해 주세요.

커뮤니티 기대 사항은 [Code of Conduct](CODE_OF_CONDUCT.md)를 따릅니다.

제안의 품질 기준과 세부 가이드는 [Contribution guide index](docs/contributing/README.md)에서 확인할 수 있습니다.

환영하는 기여는 다음과 같습니다.

- 백엔드 학습 주제 제안
- Spring/JVM 로드맵 보완
- Programmers PS 루틴 개선 제안
- 채용, 인턴, 대외활동, 해커톤 출처 제안
- OSS 기여 후보 제안
- 깨진 링크와 오래된 문서 제보
- 브리핑 문구와 문서 개선

세부 기준은 다음 문서를 참고해 주세요.

- [Good suggestion criteria](docs/contributing/good-suggestion-criteria.md)
- [Source suggestion guide](docs/contributing/source-suggestion-guide.md)
- [OSS candidate suggestion guide](docs/contributing/oss-candidate-guide.md)
- [Backend career question guide](docs/contributing/backend-career-question-guide.md)
- [Maintainer review policy](docs/contributing/review-policy.md)

Regional and language expansion suggestions are welcome when they include clear metadata such as region, locale, language, timezone, source reliability, and review caveats.

새 지역 제안은 바로 workflow에 반영되는 것이 아니라 maintainer review를 거칩니다.

큰 기능이나 운영 정책 변경은 PR 전에 issue로 먼저 논의해 주세요.

한 PR에는 하나의 주제를 담는 것을 권장합니다.

## Maintainer

Primary maintainer는 `stdiodh`입니다.

Maintainer 역할은 다음과 같습니다.

- GitHub Actions workflow 관리
- OpenAI API 기반 브리핑 초안 생성 정책 관리
- Discord Webhook 전송 정책 관리
- dry-run, validation, delivery lock 확인
- 백엔드 학습 주제와 커리어 출처 검토
- OSS 후보 추천 정책 검토
- issue template과 문서 유지관리

Maintainer도 외부 저장소에 자동 댓글, 자동 PR, 자동 assign, 자동 label 변경을 수행하지 않습니다.

## Roadmap

현재 로드맵은 작은 개선을 꾸준히 쌓는 방향입니다.

- Daily Backend Brief 품질 검증 강화
- Korea Dev/AI News Daily sparse/empty 정책 문서화 개선
- Backend Career Site Radar 출처 목록 정리
- Spring/JVM 학습 주제 우선순위 개선
- OSS 후보 beginner-friendly 기준 개선
- issue template 기반 제안 흐름 개선
- prompt budget 리포트 개선
- Discord 전송 실패 알림 개선
- 공개 예시 브리핑 보강

아직 구현되지 않은 기능은 문서에서 Roadmap 또는 TODO로만 표현합니다.

## License

Career Feed는 MIT License로 배포됩니다.

자세한 내용은 [LICENSE](LICENSE)를 확인해 주세요.
