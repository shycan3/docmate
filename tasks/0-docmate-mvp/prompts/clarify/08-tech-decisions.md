# Clarify 8: 기술적 결정사항 점검

**Asked at:** 2026-05-19T09:50:24+0900

## Agent question

LLM 호출부는 실제 provider와 deterministic sample provider를 분리하고, 복합 조건은 `추가 확인 필요`로 보수 처리하는 결정을 ADR에 남겨도 될까요?

## User answer (원문)

하네스 시작: docmate_기획서를 읽고 프로젝트를 진행해줘

## Source used

`DocMate_기획서.docx`의 "현실적 구현 접근" 문단에서 복잡한 조건은 추가 확인 필요로 처리한다고 명시되어 있어 그대로 채택했다.
