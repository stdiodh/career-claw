# Legacy Cleanup Policy

이 문서는 Career Feed 저장소에서 레거시 파일을 제거할 때 사용하는 기준입니다.

## 기준 소스

- `README.md`를 현재 운영 경로의 첫 기준으로 삼습니다.
- 워크플로, 스크립트, 설정, 테스트, 문서의 실제 참조를 함께 확인합니다.
- 오래되어 보인다는 이유만으로 삭제하지 않습니다.

## 분류 상태

| 상태 | 의미 | 처리 |
| --- | --- | --- |
| KEEP | 현재 운영 경로에서 사용 중이거나 유지 이유가 명확함 | 유지 |
| MIGRATE | 이동, 병합, 대체 후 제거해야 함 | 별도 변경으로 처리 |
| REMOVE | 미사용이 입증됐고 제거 위험이 낮음 | 삭제 가능 |
| ARCHIVE | 삭제 전 이력 보존이나 별도 기록이 필요함 | 별도 변경으로 처리 |
| UNKNOWN | 사용 여부가 불명확함 | 삭제 금지 |

## 삭제 가능 조건

파일은 아래 조건을 모두 만족할 때만 `REMOVE`로 분류할 수 있습니다.

1. `README.md`가 현재 운영 경로로 정의하지 않습니다.
2. 활성 workflow, script, config, test, Docker/infra 파일, 문서가 참조하지 않습니다.
3. 생성 산출물 계약, fixture, 호환 파일, 배포 파일, 보안/secret 관련 파일, 외부 연동 파일이 아닙니다.
4. 직접 경로명과 파일명, stem, 디렉터리명, 명령명, 환경변수명, JSON key, workflow job name 등 간접 참조를 확인했습니다.
5. 삭제 후 관련 검증이 통과합니다.

## 보호 항목

아래 항목은 명확한 근거 없이 삭제하지 않습니다.

- DB migration 파일
- 테스트 fixture
- CI/CD workflow
- Docker, compose, nginx, infra, deploy, cloud, webhook, scheduler 파일
- 보안, 인증, secret 관련 파일
- `.env.example`
- LICENSE, NOTICE, THIRD_PARTY, copyright 파일
- incident, deployment, recovery에 필요한 운영 문서
- `app/` 또는 `infra/` 전체
- `reports/` 경로 자체와 workflow가 기대하는 `.gitkeep`

## 검증 원칙

- 삭제 후보마다 `rg`, `git grep`, `git log -- <path>`로 참조와 이력을 확인합니다.
- Python script는 import, argparse, 파일 read/write, workflow 호출, validator/test 참조를 확인합니다.
- GitHub Actions workflow는 모든 `run:` 명령, script 경로, config/report 경로, prompt, secret을 추적합니다.
- 검증 기본 명령은 `./scripts/validate.sh`입니다.
- 검증을 실행할 수 없으면 명령, 실패 이유, 예상 여부, cleanup 안전성을 문서화합니다.

