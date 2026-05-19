# Phase 0: docs-update

## 사전 준비

먼저 아래 문서들을 반드시 읽고 프로젝트의 전체 아키텍처와 설계 의도를 완전히 이해하라:

- `DocMate_기획서.docx`
- `tasks/0-docmate-mvp/artifacts/01-initial-plan.md`
- `tasks/0-docmate-mvp/artifacts/02-clarify.md`
- `tasks/0-docmate-mvp/artifacts/03-context.md`

그리고 이전 phase의 작업물을 반드시 확인하라:

- 없음. 이 phase가 첫 phase다.

## 작업 내용

DocMate MVP의 프로젝트 문서를 새로 만든다.

생성할 파일:

- `docs/spec.md`
- `docs/architecture.md`
- `docs/adr.md`
- `docs/user-intervention.md`

문서에 반드시 포함할 내용:

- DocMate의 목표: 정책·장학금 공고 문서를 사용자가 바로 행동할 수 있는 체크리스트와 자격 판단으로 변환한다.
- MVP 범위: 1~5페이지 텍스트 기반 PDF, 대학생·청년 대상 정책/장학금 공고, 구조화 정보 추출, 프로필 기반 3단계 자격 판정, 경고 탐지, 체크리스트, 신청/캘린더 링크.
- 제외 범위: 로그인, 결제, DB 저장, 실제 Google OAuth 쓰기, 서류 자동 발급, 이미지 중심 PDF, 법률 문서, 복잡한 중첩 조건 자동 판정.
- 구현 방침: API 키 없이도 데모 가능한 deterministic sample provider를 둔다. 실제 LLM provider는 이후 확장 지점으로 문서화한다.
- 로컬 실행 방침: 외부 패키지 설치가 막힌 환경에서도 동작하도록 dependency-light MVP를 우선 완성하고, FastAPI/React 전환 지점은 아키텍처 문서에 남긴다.

## Acceptance Criteria

```bash
python -c "from pathlib import Path; required=['docs/spec.md','docs/architecture.md','docs/adr.md','docs/user-intervention.md']; [assertion for assertion in []]; missing=[p for p in required if not Path(p).exists()]; assert not missing, missing"
```

## AC 검증 방법

위 AC 커맨드를 실행하라. 모두 통과하면 `tasks/0-docmate-mvp/index.json`의 phase 0 status를 `"completed"`로 변경하라.
수정 3회 이상 시도해도 실패하면 status를 `"error"`로 변경하고, 에러 내용을 index.json의 해당 phase에 `"error_message"` 필드로 기록하라.

## 주의사항

- `tasks/0-docmate-mvp/docs-diff.md`는 만들지 마라. runner가 phase 0 완료 후 자동 생성한다.
- 문서에는 사용자가 직접 해야 하는 API 키/OAuth 설정이 있다면 `docs/user-intervention.md`에만 분리해서 적어라.
- 구현 코드를 만들지 마라. 이 phase는 문서 업데이트만 수행한다.
