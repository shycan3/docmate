# Evaluate: docmate-mvp

**Evaluated at:** 2026-05-19T10:16:16+0900

## 완료 기준 검증
| 기준 | 결과 | 비고 |
|------|------|------|
| 테스트 커맨드 통과 | PASS | `compileall`, `unittest`, `node --check`, smoke check 통과 |
| 개발 서버에서 업로드/프로필/결과 흐름 확인 가능 | PASS | `python backend/run.py`로 UI와 API를 같은 포트에서 제공 |
| 샘플 공고 또는 샘플 텍스트로 API 키 없이 데모 가능 | PASS | `/api/sample`과 deterministic analyzer 구현 |
| PDF 업로드 흐름 | PARTIAL | UI와 API 업로드 경로는 있으나 실제 binary PDF 추출은 PyMuPDF 없이 안전 fallback 처리 |

## 빌드/테스트 결과
```text
python -m compileall backend scripts
PASS

python -m unittest discover -s tests -p "test_*.py"
PASS: Ran 4 tests

python -m unittest discover -s tests/backend -p "test_*.py"
PASS: Ran 10 tests

node --check frontend/src/app.js
PASS

python scripts/check_smoke.py
PASS: DocMate smoke check passed.
```

## phase별 핵심 변경 요약
- phase 0 (docs-update): `docs/spec.md`, `docs/architecture.md`, `docs/adr.md`, `docs/user-intervention.md` 생성.
- phase 1 (backend-pipeline): 표준 라이브러리 기반 API 서버, 분석 파이프라인, 샘플 데이터, 자격 판정, 체크리스트, backend tests 생성.
- phase 2 (frontend-tool): no-build UI, 문서 입력/업로드, 프로필 폼, 결과 대시보드, 경고, 체크리스트, 액션 링크 렌더링 구현.
- phase 3 (integration-smoke): README, smoke script, 전체 discover 테스트 경로 정리.

## 알려진 이슈
- 실제 PDF 텍스트 추출은 아직 PyMuPDF/pdfplumber 없이 fallback만 제공한다.
- LLM provider는 아직 sample provider이며 실제 Claude/OpenAI 연동은 없다.
- Google Calendar는 OAuth 쓰기 연동이 아니라 Google Calendar 등록 URL 생성 방식이다.
- 현재 workspace가 git 저장소가 아니라 runner의 `docs-diff.md` 자동 생성과 커밋 흐름은 동작하지 않았다.

## 후속 task 권고
- [ ] PyMuPDF 또는 pdfplumber 기반 실제 PDF 텍스트 추출 provider 추가.
- [ ] Claude/OpenAI provider adapter와 JSON schema 검증 추가.
- [ ] React + TypeScript 전환 및 컴포넌트 테스트 추가.
- [ ] Google Calendar OAuth 또는 ICS 다운로드 지원 추가.
- [ ] 실제 장학금 공고 3종으로 정확도 fixture 추가.

## 종합 판정
**PASS**: API 키와 외부 의존 없이 DocMate의 핵심 경험을 확인할 수 있는 dependency-light MVP가 완성되었고, 실제 PDF/LLM/OAuth는 다음 task로 분리하는 것이 적절하다.
