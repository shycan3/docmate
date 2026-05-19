# Phase 3: integration-smoke

## 사전 준비

먼저 아래 문서들을 반드시 읽고 프로젝트의 전체 아키텍처와 설계 의도를 완전히 이해하라:

- `docs/spec.md`
- `docs/architecture.md`
- `docs/adr.md`
- `docs/user-intervention.md`
- `tasks/0-docmate-mvp/docs-diff.md`
- `tasks/0-docmate-mvp/artifacts/02-clarify.md`

그리고 이전 phase의 작업물을 반드시 확인하라:

- `backend/run.py`
- `backend/app/server.py`
- `frontend/index.html`
- `frontend/src/app.js`
- `frontend/src/styles.css`
- `tests/backend/test_analysis.py`
- `tests/backend/test_server.py`

이전 phase에서 만들어진 코드를 꼼꼼히 읽고, 설계 의도를 이해한 뒤 작업하라.

## 작업 내용

백엔드와 프론트엔드가 한 번에 실행되고, 샘플 분석 flow가 통합 검증되도록 마무리한다.

생성/수정할 주요 파일:

- `README.md`
- `scripts/check_smoke.py`
- `tests/test_project_shape.py`
- 필요하면 `package.json` 또는 `Makefile` 대신 Windows/Unix 모두 이해 가능한 README 명령어.

필수 작업:

- `python backend/run.py`로 API와 프론트엔드 정적 파일이 같은 포트에서 실행되게 한다.
- README에 실행 방법, API 사용 예, MVP 범위, 향후 FastAPI/React/LLM provider 전환 계획을 적는다.
- `scripts/check_smoke.py`는 서버를 임시 포트에서 띄우고 `/health`, `/api/sample`, `/api/analyze`, `/` 응답을 검증한다.
- 모든 테스트가 외부 네트워크와 API 키 없이 통과해야 한다.
- 분석 결과에 DocMate 핵심 기능 5개가 모두 드러나는지 확인한다.

## Acceptance Criteria

```bash
python -m compileall backend scripts
python -m unittest discover -s tests -p "test_*.py"
node --check frontend/src/app.js
python scripts/check_smoke.py
```

## AC 검증 방법

위 AC 커맨드를 실행하라. 모두 통과하면 `tasks/0-docmate-mvp/index.json`의 phase 3 status를 `"completed"`로 변경하라.
수정 3회 이상 시도해도 실패하면 status를 `"error"`로 변경하고, 에러 내용을 index.json의 해당 phase에 `"error_message"` 필드로 기록하라.

## 주의사항

- smoke test가 끝난 뒤 서버 프로세스를 반드시 종료하라.
- README에서 현재 구현이 dependency-light MVP임을 솔직하게 밝히고, 기획서의 React/FastAPI/Claude 구조로 확장하는 경로를 적어라.
- `DocMate_기획서.docx` 원본 파일은 수정하지 마라.
