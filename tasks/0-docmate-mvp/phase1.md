# Phase 1: backend-pipeline

## 사전 준비

먼저 아래 문서들을 반드시 읽고 프로젝트의 전체 아키텍처와 설계 의도를 완전히 이해하라:

- `docs/spec.md`
- `docs/architecture.md`
- `docs/adr.md`
- `docs/user-intervention.md`
- `tasks/0-docmate-mvp/docs-diff.md`
- `tasks/0-docmate-mvp/artifacts/02-clarify.md`

그리고 이전 phase의 작업물을 반드시 확인하라:

- `docs/spec.md`
- `docs/architecture.md`
- `docs/adr.md`
- `docs/user-intervention.md`

이전 phase에서 만들어진 문서를 꼼꼼히 읽고, 설계 의도를 이해한 뒤 작업하라.

## 작업 내용

DocMate MVP 백엔드 분석 파이프라인을 만든다. 외부 패키지 설치가 없어도 테스트와 데모가 가능해야 한다.

생성/수정할 주요 파일:

- `backend/app/__init__.py`
- `backend/app/models.py`
- `backend/app/sample_data.py`
- `backend/app/parser.py`
- `backend/app/analyzer.py`
- `backend/app/eligibility.py`
- `backend/app/checklist.py`
- `backend/app/server.py`
- `backend/run.py`
- `tests/backend/test_analysis.py`
- `tests/backend/test_server.py`

필수 인터페이스:

- `models.Profile`: age, grade, region, occupation, income_decile, enrolled 필드를 가진 데이터 구조.
- `parser.extract_text_from_upload(filename: str, content: bytes) -> str`: PDF는 최소한 안전하게 처리하고, 텍스트 파일 또는 디코딩 가능한 입력은 문자열을 반환한다. PDF 파싱 라이브러리가 없으면 명확한 fallback 메시지와 sample provider 흐름을 유지한다.
- `analyzer.analyze_document(text: str, profile: Profile) -> AnalysisResult`: 구조화 정보, 자격 결과, 경고, 체크리스트, action links를 반환한다.
- `eligibility.evaluate_profile(extraction, profile)`: 신청 가능, 추가 확인 필요, 신청 불가 중 하나를 보수적으로 판정한다.
- `checklist.build_checklist(extraction)`: 서류/절차를 행동 단위 체크리스트로 변환한다.
- `server.py`: stdlib `http.server` 기반으로 `GET /health`, `GET /api/sample`, `POST /api/analyze`를 제공한다. 동시에 `frontend/` 정적 파일을 서빙할 수 있게 설계한다.

도메인 규칙:

- 나이, 지역, 재학 여부처럼 단순한 필수 조건은 rule-based로 판정한다.
- 프로필 정보가 비어 있거나 조건 해석이 불확실하면 `"needs_review"`로 판정한다.
- 중복 지원 불가, 수정 불가, 자동 탈락, 서류 미비, 국적 제한 키워드는 경고로 추출한다.
- API 키가 없어도 샘플 공고 분석 결과가 일관되게 나온다.

## Acceptance Criteria

```bash
python -m compileall backend
python -m unittest discover -s tests/backend -p "test_*.py"
```

## AC 검증 방법

위 AC 커맨드를 실행하라. 모두 통과하면 `tasks/0-docmate-mvp/index.json`의 phase 1 status를 `"completed"`로 변경하라.
수정 3회 이상 시도해도 실패하면 status를 `"error"`로 변경하고, 에러 내용을 index.json의 해당 phase에 `"error_message"` 필드로 기록하라.

## 주의사항

- FastAPI가 설치되어 있지 않아도 동작해야 한다. FastAPI 전환은 문서의 확장 지점으로만 남긴다.
- 테스트는 `pytest`가 없어도 실행되도록 `unittest`를 사용한다.
- 사용자 파일 업로드를 처리할 때 임의 파일을 디스크에 저장하지 마라.
