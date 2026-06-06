# Backend Growth Curriculum

이 문서는 Daily Backend Brief에 추가된 CS Core와 백엔드 용어 슬롯의 운영 기준을 정리합니다.

## 목적

Daily Backend Brief는 기존 Spring Boot/JVM 학습, Programmers PS, OSS 기여 후보, 주니어 실무지식 구조를 유지하면서 매일 짧은 CS
Core와 백엔드 용어 학습을 함께 보냅니다.

이 슬롯은 면접 암기장을 만들기 위한 기능이 아닙니다. 매일 10~20분 안에 확인할 수 있는 행동, 완료 기준, Spring/API/DB/운영 연결을 남기는 것이 목적입니다.

## 입력 파일

- `configs/backend-core-cs-curriculum.json`
- `configs/backend-terms-glossary.json`

수집 결과는 아래 후보 파일로 생성됩니다.

- `reports/candidates/cs-core-daily-topic.json`
- `reports/candidates/backend-term-daily.json`

두 config 모두 수동 관리하는 정적 JSON입니다. 외부 사이트 크롤링, 제출 결과 수집, 데이터베이스 저장은 사용하지 않습니다.

## 선택 정책

- `selection_policy.type`은 `date_rotation`입니다.
- 기준 시간대는 `Asia/Seoul`입니다.
- workflow 실행일과 `start_date` 차이를 이용해 topic 또는 term을 deterministic하게 1개 선택합니다.
- `dry_run`에서도 같은 schema의 후보 JSON을 생성합니다.

## CS Core 트랙

CS Core는 아래 5개 트랙을 포함해야 합니다.

- `computer-architecture`
- `operating-system`
- `network`
- `database`
- `jvm-runtime`

각 topic은 백엔드 개발과의 연결, 핵심 개념, 10~20분 확인 행동, 완료 기준, 면접 연결 질문, 레퍼런스를 포함합니다.

## 백엔드 용어

백엔드 용어는 최소 30개를 유지합니다.

각 term은 한 줄 정의뿐 아니라 실무 상황, 흔한 오해, 오해하면 생기는 문제, Spring 또는 API 설계 연결, 확인 질문, 레퍼런스를 포함합니다.

## 커리어 피드 범위

이 변경은 Daily Backend Brief의 학습 슬롯을 확장하는 작업입니다. 채용, 인턴, 공모전, 대외활동 자동 파싱을 확대하지 않습니다.

커리어 정보는 기존처럼 Backend Career Site Radar를 통해 사용자가 공식 사이트와 플랫폼을 직접 확인하는 방식을 유지합니다.
