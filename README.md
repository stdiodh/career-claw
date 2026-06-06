# Career Feed

Career Feed는 백엔드 지망생과 주니어 개발자가 “무엇부터 공부하고, 어떤 채용·인턴·대외활동 정보를 보고, 어떤 OSS 기회와 실무 지식을 따라가야 하는지”를 덜 막막하게 만들기 위한 오픈소스 성장 피드입니다.

GitHub Actions, OpenAI API, Discord Webhook을 사용해 백엔드 학습 주제, PS 루틴, OSS 기여 후보, 한국 개발·AI 뉴스, 커리어 사이트 레이더를 자동 생성·검증·전송합니다.

이 프로젝트는 아직 초기 단계입니다. 다만 백엔드 지망생이 겪는 정보 과부하, 시작점 부재, 커리어 정보 단절 문제를 공개 저장소에서 성실하게 다루고, 재사용 가능한 학습·커리어 브리핑 workflow로 발전시키는 것을 목표로 합니다.

## 한 줄 요약

> 백엔드 지망생이 매일 “무엇을 보고, 무엇을 공부하고, 어떤 기회를 확인해야 하는지”를 덜 고민하도록 돕는 공개 자동 브리핑 workflow입니다.

## 왜 만들었나요?

백엔드 지망생은 정보가 부족해서가 아니라, 정보가 너무 흩어져 있어서 어디서 시작해야 할지 모르는 경우가 많습니다.

예를 들어 다음과 같은 고민이 반복됩니다.

- Java와 Spring Boot를 공부하고 있지만 다음 학습 순서를 정하기 어렵습니다.
- 채용 공고를 읽어도 어떤 역량을 먼저 채워야 하는지 판단하기 어렵습니다.
- OSS에 기여하고 싶지만 어떤 저장소와 이슈가 초보자에게 적합한지 찾기 어렵습니다.
- 기술 뉴스와 실무 지식을 따라가고 싶지만 매일 직접 선별하기 어렵습니다.
- Discord 스터디나 멘토링 그룹에서 꾸준한 성장 루틴을 운영하기 어렵습니다.

Career Feed는 이 막막함을 줄이기 위해 학습 주제, 커리어 정보, OSS 기여 후보, 실무 지식, 한국 개발·AI 뉴스를 반복 가능한 브리핑 형태로 정리합니다.

이 저장소는 백엔드 지망생의 고충을 이슈와 제안으로 수집하고, 반복 가능한 브리핑·가이드·설정으로 다시 공개 지식화하는 것을 지향합니다.

## Who this helps

- 백엔드 개발자가 되고 싶지만 학습 순서를 잡기 어려운 사람
- Spring Boot/JVM 기반 백엔드 로드맵을 꾸준히 따라가고 싶은 사람
- 채용, 인턴, 대외활동, OSS 기여 후보를 한 곳에서 보고 싶은 사람
- Discord 커뮤니티나 스터디에서 매일 또는 매주 성장 피드를 운영하고 싶은 사람
- 정보 과부하 때문에 무엇부터 해야 할지 막막한 주니어 개발자
- 백엔드 멘토링에서 반복되는 질문을 더 구조적으로 정리하고 싶은 멘토

## What it generates

| 산출물 | 설명 |
| --- | --- |
| Daily Backend Brief | Spring Boot/JVM 학습, Programmers PS 루틴, Spring/JVM/Kotlin OSS 기여 후보, 주니어 백엔드 실무 지식, CS Core/백엔드 용어를 묶은 일일 브리핑 |
| Korea Dev/AI News Daily | 한국 개발·AI 뉴스와 기술 수요를 관찰하고, sparse/empty 정책과 validator를 거쳐 전송하는 일일 뉴스 피드 |
| Backend Career Site Radar | 공식 채용 사이트, 채용·인턴 플랫폼, 대외활동·해커톤·공모전 플랫폼을 수동으로 점검하는 백엔드 커리어 레이더 |
| Mark PS Solved | `data/ps-progress.json`에 Programmers 풀이 진행도를 기록하는 수동 workflow |

## 운영 범위

현재 운영 범위는 의도적으로 작게 유지합니다.

포함하는 것:

- 정적 설정 파일 기반 후보 수집
- GitHub Actions 기반 daily/manual workflow
- OpenAI API 기반 브리핑 초안 생성과 요약 보조
- validator 기반 전송 전 검증
- Discord Webhook 전송
- GitHub Actions artifact 기반 결과 확인
- issue template 기반 커리어 질문·출처·OSS 후보 제안 수집

포함하지 않는 것:

- 상시 실행 서버
- 데이터베이스
- 웹 대시보드
- Discord Gateway Bot
- Slash Command
- 외부 저장소에 대한 자동 댓글, 자동 PR, 자동 assign, 자동 label 변경
- 채용 사이트 또는 PS 사이트에 대한 무단 크롤링
- 사용자의 개인정보나 비공개 커리어 정보 저장

## 운영 Workflow 요약

| 경로 | Workflow | 주요 산출물 | 실행 방식 |
| --- | --- | --- | --- |
| Daily Backend Brief | `.github/workflows/kr-tech-daily.yml` | `reports/briefs/kr-tech-daily.md` | 평일 자동, 수동 실행 |
| Korea Dev/AI News Daily | `.github/workflows/kr-tech-news-daily.yml` | `reports/briefs/kr-tech-news-daily.md` | 평일 자동, 수동 실행 |
| Backend Career Site Radar | `.github/workflows/kr-backend-career-weekly.yml` | `reports/briefs/kr-backend-career-weekly.md` | 수동 실행 |
| Mark PS Solved | `.github/workflows/mark-ps-solved.yml` | `data/ps-progress.json` | 수동 실행 |

## 자동 실행 시간

| 경로 | 실행 시간 |
| --- | --- |
| Daily Backend Brief | 평일 08:05 KST 시작, 09:00 KST 전송, 09:25 KST catch-up |
| Korea Dev/AI News Daily | 평일 08:15 KST 시작, 09:05 KST 전송, 09:30 KST catch-up |
| Backend Career Site Radar | 자동 실행 없음 |
| Mark PS Solved | 자동 실행 없음 |

실제 schedule은 workflow 파일을 기준으로 확인합니다. README와 workflow가 다르면 workflow 파일을 우선합니다.

## 빠른 시작

1. 저장소를 fork 또는 clone합니다.
2. 필요한 GitHub Actions secrets를 등록합니다.
3. Daily workflow는 먼저 `dry_run=true`, `force_send=false`로 실행합니다.
4. 생성된 artifacts와 validation reports를 확인합니다.
5. 검증이 성공한 뒤에만 Discord 전송을 실행합니다.

## 필요한 Secrets

| Secret | 필수 여부 | 용도 |
| --- | --- | --- |
| `OPENAI_API_KEY` | 필수 | Daily Backend Brief, Korea Dev/AI News Daily 생성 |
| `DISCORD_WEBHOOK_KR_TECH_DAILY` | 필수 | Daily Backend Brief 전송 |
| `DISCORD_WEBHOOK_KR_TECH_NEWS_DAILY` | 필수 | Korea Dev/AI News Daily 전송 |
| `DISCORD_WEBHOOK_BACKEND_CAREER_WEEKLY` | 필수 | Backend Career Site Radar 전송 |
| `NAVER_CLIENT_ID` | 선택 | Korea Dev/AI News Daily 후보 품질 개선 |
| `NAVER_CLIENT_SECRET` | 선택 | Korea Dev/AI News Daily 후보 품질 개선 |
| `DISCORD_WEBHOOK_CAREER_FEED_OPS` | 선택 | workflow 실패 알림. 없으면 실패 알림만 skip |

Secret 값, API key, token, webhook URL은 코드, 문서 예시, 커밋 로그, 이슈, PR에 저장하지 않습니다.

## 로컬 검증

자주 쓰는 검증 명령입니다.

    python3 scripts/check-workflow-schedules.py
    python3 scripts/collect-kr-feeds.py --mode daily-backend --dry-run
    python3 scripts/collect-kr-feeds.py --mode daily-news --dry-run
    python3 scripts/build-daily-news-shortlist.py
    python3 scripts/estimate-prompt-budget.py
    python3 scripts/collect-kr-feeds.py --mode weekly-career --dry-run
    python3 scripts/render-weekly-career-site-radar.py
    ./scripts/validate.sh
    git diff --check

OpenAI API 호출이나 Discord 전송이 포함될 수 있는 명령은 dry-run 여부를 먼저 확인합니다.

## 디렉터리 구조

    repository-root/
    ├─ .github/          # GitHub Actions workflows, issue templates
    ├─ app/              # 현재 운영 경로 밖의 앱 관련 코드
    ├─ configs/          # 수집 소스, 커리큘럼, OSS, site radar 설정
    ├─ data/             # PS/OSS/Spring topic 진행도 JSON
    ├─ docs/             # 운영 정책과 상세 가이드
    ├─ infra/            # 현재 운영 경로 밖의 infra 관련 파일
    ├─ reports/          # 생성 브리핑, 후보 JSON, 운영 요약 artifact
    ├─ scripts/          # 수집, 렌더링, 검증, Discord 전송 스크립트
    ├─ tests/            # validator와 collector fixture/test
    ├─ LEGACY.md         # 레거시 파일 제거 기준
    └─ README.md

`reports/` 아래 생성 산출물은 기본적으로 커밋하지 않습니다.

## 상세 문서

| 문서 | 내용 |
| --- | --- |
| `docs/ecosystem-importance.md` | 백엔드 생태계에서 Career Feed가 갖는 의미와 한계 |
| `docs/oss-program-application.md` | Codex Open Source Support Program 신청용 정리 문구 |
| `docs/open-source-readiness-review.md` | 현재 OSS 적합성 판단, 강점, 약점, 보완 계획 |
| `docs/community-guide.md` | 개인, 스터디, 멘토링에서 Career Feed를 재사용하는 방법 |
| `docs/maintainer-guide.md` | dry-run, 검증, secret 안전, issue 제안 검토 체크리스트 |
| `docs/github-labels.md` | issue/PR 분류에 사용할 권장 label |

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

Career Feed에는 아래 방식으로 기여할 수 있습니다.

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
- 신청·유지관리 문서의 영어 요약 추가

## API usage policy

Career Feed는 OpenAI API를 사용해 브리핑 초안, 요약, 후보 정리, 검증 보조 산출물을 생성합니다.

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

생성 결과는 workflow validator와 maintainer 검토 흐름을 거쳐 사용합니다.

## 운영 정책 요약

- Backend Daily와 News Daily는 `dry_run`, `force_send`, delivery lock, catch-up schedule로 누락과 중복 전송 위험을 줄입니다.
- News Daily는 기준을 만족하는 뉴스가 적을 때도 sparse/empty 정책에 맞으면 정상 성공으로 봅니다.
- Programmers PS 루틴은 정적 config와 progress 파일만 사용하며 사이트 크롤링이나 제출 결과 자동 수집을 하지 않습니다.
- OSS 후보는 GitHub issue 기반으로 추천만 하며 댓글, PR 생성, assign, label 변경은 자동 수행하지 않습니다.
- OpenJDK/JBS는 Spring OSS 난이도 모델 참고로만 사용하고 직접 수집하지 않습니다.
- `app/`와 `infra/`는 현재 README 운영 경로에는 포함하지 않지만 HIGH 위험 영역이므로 레거시 정리에서 삭제하지 않습니다.
- 레거시 파일 제거 기준은 `LEGACY.md`를 따릅니다.

## License

This project is licensed under the MIT License.
