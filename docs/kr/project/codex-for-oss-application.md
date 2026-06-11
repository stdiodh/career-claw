# Codex for OSS Application

> Language: [한국어](./codex-for-oss-application.md) | [English](../../en/project/codex-for-oss-application.md)

이 문서는 maintainer가 Career Feed를 OpenAI Codex for Open Source 프로그램에 신청할 때 사용할 수 있는 정직한 근거와 짧은 문구를 정리합니다.

## 1. Project summary

Career Feed는 Early Public OSS 단계의 fork 기반 GitHub Actions 자동화 프로젝트입니다.

OpenAI API와 Discord Webhook을 사용해 백엔드 학습, 개발/AI 뉴스, OSS 후보 검토, 커리어 신호를 Markdown artifact로 생성하고 검증합니다.

Discord 전송은 선택 사항이며, 기본 흐름은 dry-run artifact 검토입니다.

## 2. Why it matters to the backend ecosystem

이 프로젝트는 프로덕션 백엔드 의존성, 프레임워크, 데이터베이스, hosted SaaS가 아닙니다.

가치는 백엔드 생태계의 온보딩 계층에 있습니다.

백엔드 학습자, 주니어 개발자, Discord 스터디 그룹, 멘토가 반복 가능한 학습 주제, 뉴스 요약, OSS 기여 준비 자료를 만들고 검토하는 데 도움을 줍니다.

## 3. Current evidence in v0.2.0

v0.2.0에서 확인할 수 있는 근거는 다음과 같습니다.

- `ko-KR` 기본 지원 locale
- `en-US` experimental foundation
- Daily Backend Brief, Dev News Daily, Backend Career Site Radar, PS progress workflow
- locale-aware artifact path
- locale-specific Discord webhook Secret 이름
- Discord delivery disabled-by-default 흐름
- dry-run artifact review
- generated brief validation before delivery
- validation script와 fixture
- source policy, issue template, release checklist

## 4. Honest limitations

Career Feed는 아직 초기 공개 OSS입니다.

넓은 adoption, download, star, active user, organization 사용 지표는 주장하지 않습니다.

사용 지표는 아직 claimed 상태가 아닙니다.

`en-US`는 mature global support가 아니라 experimental foundation입니다.

출력 품질은 source 품질, prompt, validation, maintainer review에 의존합니다.

생성 결과는 career decision, hiring decision, OSS maintainer 판단을 대체하지 않습니다.

## 5. How API credits would be used

API credits는 maintainer가 검토할 수 있는 초안과 요약을 만드는 데 사용합니다.

- Daily Backend Brief 초안 생성
- 개발/AI 뉴스 후보 요약
- Spring Boot, JVM, Kotlin, backend study topic 우선순위화
- OSS candidate note 정리
- validation report와 release checklist 검토
- 문서 일관성 점검
- locale/provider expansion 검토

## 6. Automation boundaries and safety

Codex/OpenAI output은 unchecked public action이 아니라 reviewable draft material입니다.

외부 repository에 자동 comment를 작성하지 않습니다.

외부 repository에 자동 PR을 만들지 않습니다.

외부 issue를 자동 assign하지 않습니다.

외부 label을 자동 변경하지 않습니다.

Discord 전송은 dry-run, validation, delivery enabled 설정, delivery lock 정책을 통해 제한합니다.

Secrets, webhook URLs, API keys, private identifiers는 문서나 issue에 포함하지 않고 GitHub Secrets 또는 환경변수로만 다룹니다.

## 7. Copy-ready short application text

아래 문구는 500자 미만입니다.

```text
Career Feed는 v0.2.0 기준 Early Public OSS인 fork 기반 GitHub Actions 자동화입니다. 프로덕션 백엔드 의존성, 프레임워크, 데이터베이스, SaaS가 아니라 백엔드 학습자, 주니어 개발자, Discord 스터디, 멘토의 온보딩과 OSS 기여 준비를 돕는 검토 가능한 브리핑 도구입니다. 사용 지표는 아직 주장하지 않습니다.
```

## 8. Copy-ready API credit usage text

아래 문구는 500자 미만입니다.

```text
API credits는 Daily Backend Brief, 개발/AI 뉴스 요약, OSS 후보 정리, 검증 리포트, 문서 리뷰처럼 maintainer가 확인할 수 있는 초안 생성에만 사용합니다. 외부 저장소에 자동 comment, PR, assign, label 변경을 하지 않고, Discord 전송 전 dry-run artifact와 validation을 검토합니다.
```
