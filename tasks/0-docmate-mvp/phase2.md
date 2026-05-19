# Phase 2: frontend-tool

## 사전 준비

먼저 아래 문서들을 반드시 읽고 프로젝트의 전체 아키텍처와 설계 의도를 완전히 이해하라:

- `docs/spec.md`
- `docs/architecture.md`
- `docs/adr.md`
- `tasks/0-docmate-mvp/docs-diff.md`
- `tasks/0-docmate-mvp/artifacts/02-clarify.md`

그리고 이전 phase의 작업물을 반드시 확인하라:

- `backend/app/server.py`
- `backend/app/models.py`
- `backend/app/sample_data.py`
- `tests/backend/test_analysis.py`
- `tests/backend/test_server.py`

이전 phase에서 만들어진 코드를 꼼꼼히 읽고, 설계 의도를 이해한 뒤 작업하라.

## 작업 내용

DocMate MVP 프론트엔드 도구 화면을 만든다. 첫 화면은 랜딩 페이지가 아니라 실제 분석 작업 화면이어야 한다.

생성/수정할 주요 파일:

- `frontend/index.html`
- `frontend/src/app.js`
- `frontend/src/styles.css`
- `frontend/src/icons.js` 또는 필요한 경우 간단한 아이콘 helper
- `frontend/README.md`

필수 UI:

- 문서 업로드 영역과 샘플 공고 사용 버튼.
- 프로필 입력 영역: 나이, 학년, 거주지, 직업, 소득분위, 재학 여부.
- 분석 실행 버튼과 loading/error/empty/result 상태.
- 자격 결과 배너: 신청 가능, 추가 확인 필요, 신청 불가.
- 핵심 정보 카드: 신청 기간, 지원 대상 조건, 혜택, 제출 서류, 신청 방법, 신청 URL.
- 경고 카드: 수정 불가, 중복 지원 불가, 자동 탈락, 서류 미비 등.
- 체크리스트: 실행 가능한 할 일, 관련 action URL, 완료 체크 상태.
- 즉시 실행 영역: 신청 페이지 이동, 캘린더 등록 링크.

디자인 규칙:

- 업무형 SaaS 도구처럼 차분하고 스캔하기 쉬운 화면을 만든다.
- 카드 안에 카드를 중첩하지 않는다.
- 첫 화면은 실제 기능 화면이어야 하며 마케팅 hero를 만들지 않는다.
- 모바일과 데스크톱에서 텍스트가 버튼이나 패널 밖으로 넘치지 않게 한다.
- 의미 없는 장식용 gradient/orb/bokeh를 넣지 않는다.

API 연결:

- `GET /api/sample`로 샘플 데이터를 불러온다.
- `POST /api/analyze`로 파일과 프로필을 보내고 결과를 렌더링한다.
- backend가 없을 때도 샘플 결과를 보여주는 fallback을 둔다.

## Acceptance Criteria

```bash
node --check frontend/src/app.js
python -m compileall backend
python -m unittest discover -s tests/backend -p "test_*.py"
```

## AC 검증 방법

위 AC 커맨드를 실행하라. 모두 통과하면 `tasks/0-docmate-mvp/index.json`의 phase 2 status를 `"completed"`로 변경하라.
수정 3회 이상 시도해도 실패하면 status를 `"error"`로 변경하고, 에러 내용을 index.json의 해당 phase에 `"error_message"` 필드로 기록하라.

## 주의사항

- npm install이 필요 없는 no-build 프론트엔드로 완성한다. React/TypeScript 전환은 문서화된 다음 단계로 남긴다.
- 외부 CDN에 의존하지 마라. 로컬 파일만으로 UI가 렌더링되어야 한다.
- 업로드된 파일 내용이나 프로필을 localStorage에 저장하지 마라.
