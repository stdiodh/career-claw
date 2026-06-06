<p align="center">
  <img src="docs/assets/career-feed-social-preview.png" alt="career-feed — Open-source backend career growth feed for Korean backend learners" width="100%" />
</p>

# career-feed

> Open-source backend career growth feed for Korean backend learners.

백엔드 지망생과 주니어 개발자가 “오늘 무엇을 공부하고, 어떤 기회를 확인하고, 어떤 OSS 후보를 살펴봐야 하는지”를 덜 막막하게 만들기 위한 공개 자동 브리핑 workflow입니다.

`career-feed`는 GitHub Actions, OpenAI API, Discord Webhook을 사용해 백엔드 학습 주제, PS 루틴, OSS 기여 후보, 한국 개발·AI 뉴스, 커리어 사이트 레이더를 생성·검증·전송합니다.

이 프로젝트는 아직 초기 단계입니다. 큰 사용 지표를 주장하지 않습니다. 대신 백엔드 지망생의 정보 과부하와 시작점 부재 문제를 공개 저장소에서 성실하게 다루고, 재사용 가능한 학습·커리어 브리핑 workflow로 발전시키는 것을 목표로 합니다.

<p align="center">
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-blue.svg" /></a>
  <img alt="GitHub Actions" src="https://img.shields.io/badge/GitHub_Actions-automation-2563EB" />
  <img alt="OpenAI API" src="https://img.shields.io/badge/OpenAI_API-briefing-10B981" />
  <img alt="Discord Webhook" src="https://img.shields.io/badge/Discord-Webhook-5865F2" />
</p>

<p align="center">
  <a href="#why-career-feed">Why</a> ·
  <a href="#what-it-generates">Outputs</a> ·
  <a href="#quick-start">Quick Start</a> ·
  <a href="#how-it-works">How It Works</a> ·
  <a href="#backend-ecosystem-importance">Ecosystem Importance</a> ·
  <a href="#contributing">Contributing</a>
</p>

---

## Why career-feed?

백엔드 지망생은 정보가 부족해서가 아니라, 정보가 너무 흩어져 있어서 어디서 시작해야 할지 모르는 경우가 많습니다.

반복되는 고민은 대체로 비슷합니다.

- Java와 Spring Boot를 공부하고 있지만 다음 학습 순서를 정하기 어렵습니다.
- 채용 공고를 읽어도 요구 역량을 학습 계획으로 바꾸기 어렵습니다.
- OSS에 기여하고 싶지만 초보자에게 적합한 저장소와 이슈를 찾기 어렵습니다.
- 기술 뉴스와 실무 지식을 매일 직접 선별하기 어렵습니다.
- Discord 스터디나 멘토링 그룹에서 꾸준한 성장 루틴을 운영하기 어렵습니다.

`career-feed`는 이 막막함을 줄이기 위해 학습 주제, 커리어 정보, OSS 기여 후보, 실무 지식, 한국 개발·AI 뉴스를 반복 가능한 브리핑 형태로 정리합니다.

## What it generates

| Output | Description |
| --- | --- |
| Daily Backend Brief | Spring Boot/JVM 학습, PS 루틴, Spring/JVM/Kotlin OSS 기여 후보, 실무 지식, CS/백엔드 용어를 묶은 일일 브리핑 |
| Korea Dev/AI News Daily | 한국 개발·AI 뉴스와 기술 수요를 관찰하고 validator를 거쳐 전송하는 일일 뉴스 피드 |
| Backend Career Site Radar | 공식 채용 사이트, 채용·인턴 플랫폼, 대외활동·해커톤·공모전 플랫폼을 점검하는 커리어 레이더 |
| Mark PS Solved | `data/ps-progress.json`에 Programmers 풀이 진행도를 기록하는 수동 workflow |

## What this is not

운영 범위를 의도적으로 작게 유지합니다.

`career-feed`는 다음을 하지 않습니다.

- 상시 실행 서버 운영
- 데이터베이스 운영
- 웹 대시보드 제공
- Discord Gateway Bot 또는 Slash Command 제공
- 외부 저장소에 자동 댓글 작성
- 외부 저장소에 자동 PR 생성
- 외부 저장소 issue 자동 assign 또는 label 변경
- 채용 결과나 개인 역량에 대한 단정적 평가

## Quick Start

1. 저장소를 fork 또는 clone합니다.
2. 필요한 GitHub Actions secrets를 등록합니다.
3. Daily workflow는 먼저 `dry_run=true`, `force_send=false`로 실행합니다.
4. 생성된 artifacts와 validation reports를 확인합니다.
5. 검증이 성공한 뒤에만 Discord 전송을 실행합니다.

```bash
git clone https://github.com/stdiodh/career-feed.git
cd career-feed

# 문서/스케줄 검증
python3 scripts/check-workflow-schedules.py

# 저장소 검증 스크립트가 실행 가능하다면
./scripts/validate.sh
```

## Required secrets

| Secret | Required | Purpose |
| --- | --- | --- |
| `OPENAI_API_KEY` | Yes | Daily Backend Brief, Korea Dev/AI News Daily 생성 |
| `DISCORD_WEBHOOK_KR_TECH_DAILY` | Yes | Daily Backend Brief 전송 |
| `DISCORD_WEBHOOK_KR_TECH_NEWS_DAILY` | Yes | Korea Dev/AI News Daily 전송 |
| `DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY` | Yes | Backend Career Site Radar 전송 |
| `NAVER_CLIENT_ID` | Optional | Korea Dev/AI News Daily 후보 품질 개선 |
| `NAVER_CLIENT_SECRET` | Optional | Korea Dev/AI News Daily 후보 품질 개선 |
| `DISCORD_WEBHOOK_CAREER_FEED_OPS` | Optional | workflow 실패 알림 |

Secret 값, API key, token, webhook URL은 코드, 문서 예시, 커밋 로그, 이슈, PR에 저장하지 않습니다.

## How it works

```text
Static configs
  ↓
GitHub Actions schedule or manual dispatch
  ↓
Collectors and renderers
  ↓
OpenAI API assisted briefing draft
  ↓
Validation and dry-run artifacts
  ↓
Maintainer review
  ↓
Discord Webhook delivery
```

## Workflows

| Workflow | File | Trigger | Output |
| --- | --- | --- | --- |
| Daily Backend Brief | `.github/workflows/kr-tech-daily.yml` | Weekday schedule, manual | `reports/briefs/kr-tech-daily.md` |
| Korea Dev/AI News Daily | `.github/workflows/kr-tech-news-daily.yml` | Weekday schedule, manual | `reports/briefs/kr-tech-news-daily.md` |
| Backend Career Site Radar | `.github/workflows/kr-backend-career-weekly.yml` | Manual | `reports/briefs/kr-backend-career-weekly.md` |
| Mark PS Solved | `.github/workflows/mark-ps-solved.yml` | Manual | `data/ps-progress.json` |

README와 workflow schedule이 다르면 실제 workflow 파일을 우선합니다.

## Backend ecosystem importance

`career-feed`는 백엔드 런타임, 프레임워크, 라이브러리처럼 production dependency가 되는 프로젝트는 아닙니다.

대신 백엔드 생태계에 진입하려는 지망생과 주니어 개발자의 onboarding friction을 줄이는 공개 성장 인프라를 목표로 합니다.

이 프로젝트의 중요성은 “얼마나 많은 애플리케이션이 이 패키지에 의존하는가”보다 “백엔드 생태계에 새로 들어오는 사람들이 더 꾸준하고 안전하게 학습·기여 루틴을 만들 수 있는가”에 있습니다.

자세한 내용은 `docs/ecosystem-importance.md`를 참고해 주세요.

## API usage policy

OpenAI API는 다음 용도로 사용합니다.

- daily/weekly 브리핑 초안 생성
- 학습 주제와 커리어 정보의 우선순위화
- OSS 후보의 beginner-friendly 여부 정리 보조
- 이슈로 접수된 고민의 분류와 답변 초안 생성
- maintainer가 검토할 수 있는 validation summary 생성

OpenAI API를 다음 용도로 사용하지 않습니다.

- 외부 저장소에 자동 댓글 작성
- 외부 저장소에 자동 PR 생성
- 외부 저장소 issue 자동 assign 또는 label 변경
- 무검토 배포
- 사용자의 민감 정보 저장 또는 분석
- 채용 결과나 개인 역량에 대한 단정적 평가

## Documentation

| Document | Purpose |
| --- | --- |
| `docs/ecosystem-importance.md` | 백엔드 생태계에서 Career Feed가 갖는 의미와 한계 |
| `docs/open-source-readiness-review.md` | 현재 OSS 적합성 판단, 강점, 약점, 보완 계획 |
| `docs/oss-program-application.md` | Codex Open Source Support Program 신청용 정리 문구 |
| `docs/community-guide.md` | 개인, 스터디, 멘토링에서 재사용하는 방법 |
| `docs/maintainer-guide.md` | dry-run, 검증, secret 안전, issue 제안 검토 체크리스트 |

## Maintainer

- `@stdiodh`: primary maintainer
  - GitHub Actions workflow 관리
  - OpenAI API 기반 브리핑 생성과 검증 흐름 관리
  - 백엔드 학습 주제와 커리어 소스 관리
  - Discord Webhook 전송 운영
  - 문서화와 로드맵 관리
  - issue template 기반 제안 검토

## Contributing

기여 방식은 `CONTRIBUTING.md`를 확인해 주세요.

기여할 수 있는 방법은 다음과 같습니다.

- 백엔드 학습 주제 제안
- 커리어 정보 출처 제안
- OSS 기여 후보 제안
- 깨진 링크 또는 수집 실패 제보
- 백엔드 커리어 고민 공유
- 문서 개선

## Roadmap

- 공개 샘플 브리핑 추가
- 백엔드 지망생 고민·질문 issue template 개선
- good first issue 기반 OSS 기여 후보 큐레이션 개선
- Spring/JVM 학습 로드맵 개선
- Discord 커뮤니티 운영 가이드 문서화
- 브리핑 결과 검증 로직 개선
- API 사용량과 prompt budget 리포트 개선
- 중복 전송 방지와 실패 알림 개선

## License

This project is licensed under the MIT License.
