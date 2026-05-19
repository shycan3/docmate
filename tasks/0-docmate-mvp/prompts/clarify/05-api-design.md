# Clarify 5: API 설계

**Asked at:** 2026-05-19T09:50:24+0900

## Agent question

API는 `GET /health`, `GET /api/sample`, `POST /api/analyze` 중심으로 최소화하고 인증은 MVP에서 제외해도 될까요?

## User answer (원문)

하네스 시작: docmate_기획서를 읽고 프로젝트를 진행해줘

## Source used

`DocMate_기획서.docx`의 MVP 범위에 로그인/구독이 핵심 기능으로 포함되어 있지 않아 인증 없는 분석 API로 결정했다.
