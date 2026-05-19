# 발표자료 제작 과정 기록

날짜: 2026-05-19  
대상 프로젝트: DocMate  
로컬 데모 URL: `http://127.0.0.1:8000`

## 1. 폴더 생성

- `presentation-materials/` 폴더를 생성했다.
- 하위 폴더는 `images/`, `docs/`, `source-template/`로 나누었다.

## 2. HWP 템플릿 보관과 구조 확인

- 사용자가 제공한 `C:/Users/DO/Downloads/2. 경진대회 발표개요서.hwp`를 `source-template/`에 복사했다.
- HWP 미리보기 텍스트를 추출해 `source-template/template-preview.txt`로 저장했다.
- 템플릿 항목은 팀명, 작품명, 작품주제, 보고서 개요로 확인했다.

## 3. 발표용 화면 캡처

브라우저에서 실제 로컬 서비스를 실행하며 다음 화면을 캡처했다.

- 첫 화면과 분석 작업 공간
- 선택형 프로필 입력과 샘플 공고 선택
- 분석 결과 요약
- 원문 근거 펼침 화면
- 체크리스트와 다음 행동
- 히스토리 공고 비교

## 4. 이미지 정리

- 스크롤 중 고정 탭이 화면 상단 일부를 가리는 캡처는 발표 삽입용으로 상단을 살짝 잘라 냈다.
- 이미지 원본 내용은 바꾸지 않았고, 슬라이드 배치 시 가독성을 높이기 위한 컷 정리만 수행했다.

## 5. 발표 문서 작성

다음 문서를 작성했다.

- `README.md`: 폴더 사용법
- `docs/image-usage-guide.md`: 이미지별 역할과 발표 포인트
- `docs/presentation-overview.md`: 발표개요서 원고
- `docs/slide-outline.md`: 슬라이드 구성안
- `docs/speaker-notes.md`: 발표 대본 초안
- `docs/judge-qna.md`: 예상 심사 질문과 답변 방향

## 6. 발표개요서 문서화

- HWP 원본 템플릿은 그대로 보존했다.
- 작성본은 Markdown 원고와 Word 문서(`presentation-overview.docx`)로 생성했다.
- 로컬 환경에서 HWP 바이너리를 직접 편집할 수 있는 안정적인 도구는 확인되지 않아, 제출 전 필요하면 이 원고를 HWP 양식에 붙여 넣는 방식이 가장 안전하다.

## 7. 검증 계획

- 생성된 이미지가 실제 브라우저 캡처인지 확인했다.
- 문서 목록과 링크가 깨지지 않는지 확인했다.
- DOCX는 `python-docx`로 구조 생성 후 문서 객체 기준 `문단 9개`, `표 2개`, `섹션 1개`를 확인했다.
- DOCX 렌더링 검증은 `render_docx.py`로 시도했으나, 현재 Windows 환경에서 LibreOffice/`soffice` 실행 파일을 찾을 수 없어 PNG 렌더 QA는 완료하지 못했다.
- 최종 변경 사항은 Git에 커밋하고 GitHub 원격 저장소에 푸시한다.
