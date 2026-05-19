# Clarify Summary: docmate-mvp

## 1. 구현가능성
- MVP는 구현 가능하다. PDF 텍스트 추출, 구조화 분석, 자격 판정, 체크리스트 생성, 경고 탐지는 독립 모듈로 나눌 수 있다.
- 실제 LLM API 키와 Google Calendar OAuth는 사용자 환경 의존성이므로, 첫 구현에서는 deterministic sample provider와 캘린더 등록 링크 또는 ICS 생성으로 대체한다.
- 복잡한 중첩 조건, 표/이미지 중심 PDF, 법률 문서는 MVP 범위 밖으로 둔다.

## 2. 기술스택
| 항목 | 선택 |
|------|------|
| 프론트엔드 | React + TypeScript + Vite |
| 백엔드 | FastAPI + Python 3.11 |
| 문서 파싱 | PyMuPDF 우선, 미설치/실패 시 텍스트 샘플 fallback |
| AI 분석 | provider 인터페이스 + sample provider, 추후 Claude/OpenAI provider 확장 |
| 자격 판정 | rule-based 비교 + 불확실 조건 보수 처리 |
| 데이터 저장 | MVP에서는 DB 없음, 요청/응답 JSON 중심 |
| 테스트 | pytest, frontend smoke는 build/test script |

## 3. 사용흐름
1. 사용자는 PDF를 업로드하거나 샘플 공고를 선택한다.
2. 사용자는 나이, 학년, 거주지, 직업, 소득분위, 재학 여부 같은 프로필을 입력한다.
3. 시스템은 문서 텍스트를 추출하고 구조화 결과, 자격 상태, 경고, 체크리스트, 행동 링크를 생성한다.
4. 사용자는 결과 카드를 확인하고 신청 페이지 또는 서류 발급/캘린더 등록 액션으로 이동한다.

## 4. 화면 설계
- 단일 작업형 화면을 첫 화면으로 둔다.
- 좌측 또는 상단에는 PDF 업로드/샘플 선택과 프로필 입력 폼을 배치한다.
- 결과 영역에는 자격 상태 배너, 핵심 정보 카드, 경고 카드, 제출 서류/체크리스트, 신청/캘린더 액션을 표시한다.
- 모바일에서는 입력 영역과 결과 영역을 세로 흐름으로 배치한다.

## 5. API 설계
| METHOD | PATH | 입력 | 출력 |
|--------|------|------|------|
| GET | `/health` | 없음 | `{ "status": "ok" }` |
| GET | `/api/sample` | 없음 | 샘플 분석 요청/결과에 쓸 문서 텍스트와 프로필 |
| POST | `/api/analyze` | multipart PDF 또는 raw text, profile JSON | 구조화 정보, 자격 결과, 경고, 체크리스트, 액션 링크 |

오류 응답은 `{ "detail": "..." }` 형태를 따른다. MVP 인증은 없다.

## 6. 데이터 설계
- `Profile`: age, grade, region, occupation, incomeDecile, enrolled
- `DocumentExtraction`: title, applicationPeriod, eligibilityConditions, benefits, requiredDocuments, applicationMethod, applicationUrl
- `EligibilityResult`: status, reasons, missingInformation
- `WarningItem`: severity, title, evidence
- `ChecklistItem`: title, description, actionUrl, done
- `AnalysisResult`: extraction, eligibility, warnings, checklist, actions

DB와 migration은 두지 않는다. 브라우저 상태와 API 응답으로 MVP를 완성한다.

## 7. 코드 아키텍처
- `backend/app/main.py`: FastAPI app과 route 등록
- `backend/app/models.py`: Pydantic request/response schema
- `backend/app/parser.py`: PDF/text 추출
- `backend/app/analyzer.py`: provider 인터페이스와 sample analysis
- `backend/app/eligibility.py`: profile 조건 비교
- `backend/app/checklist.py`: 행동 체크리스트와 링크 생성
- `frontend/src/App.tsx`: 화면 composition
- `frontend/src/api.ts`: backend API client
- `frontend/src/components/`: upload, profile, result components
- `tests/`: backend service/API 테스트

## 8. 기술 결정사항 (ADR 요약)
- LLM provider를 분리한다: API 키가 없는 환경에서도 데모와 테스트가 가능해야 한다.
- DB를 제외한다: MVP 검증 목표는 분석 경험이며, 저장/히스토리는 프리미엄 또는 고도화 단계다.
- 복합 조건은 보수적으로 처리한다: 잘못된 신청 가능 판정보다 추가 확인 필요가 사용자 신뢰에 유리하다.
- 첫 화면을 실제 도구로 만든다: DocMate의 차별점은 설명이 아니라 행동 연결이다.

## 9. 구현 계획 논의점
- Phase 0에서 `docs/spec.md`, `docs/architecture.md`, `docs/adr.md`를 만든다.
- Phase 1에서 백엔드 schema, parser, analyzer, eligibility, checklist, tests를 만든다.
- Phase 2에서 프론트엔드 작업형 UI와 API 연결을 만든다.
- Phase 3에서 샘플 데이터, 통합 실행 스크립트, 빌드/테스트 검증을 정리한다.
- 위험 영역은 PDF 파서 의존성, 실제 LLM API, 캘린더 OAuth다. 모두 fallback 가능한 형태로 설계한다.
