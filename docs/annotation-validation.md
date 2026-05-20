**Annotation & Validation**

요약
- 자동 스크린샷 주석(레이블/박스)과 엄격한 디자이너 페르소나 검증을 지원합니다.

무엇이 변경되었나
- `scripts/capture_presentation_screenshots.py`
  - `annotate()`에 레이블-박스 충돌 감지 및 자동 재배치 로직 추가
  - 충돌이 해결되지 않으면 상단 안전 영역으로 강제 이동
  - 재배치/이동 이벤트를 `presentation-materials/screenshots/annotation_warnings.log`에 기록
- `scripts/validate_screenshots.py`
  - 작은 잡음(작은 컬러 점)을 필터링하고, 레이블-박스 겹침은 면적/너비/높이 임계값으로 판단

왜 필요한가
- 작은 UI 점(상태 아이콘)이 검증에서 false-positive를 일으켜 실제 디자인 문제 추적이 어려웠습니다.
- 레이블을 자동 재배치하면 프레젠테이션 이미지 일관성을 보장하면서 수동 개입을 줄입니다.

사용 방법
- 스크린샷 생성 및 검증(자동):
```bash
python scripts/capture_presentation_screenshots.py
python scripts/validate_screenshots.py
```

로그
- 재배치/이동 이벤트는 `presentation-materials/screenshots/annotation_warnings.log`에 JSON 라인으로 기록됩니다.

향후 개선안
- 레이블 자동 재배치를 이미지별로 더 스마트하게(폰트 길이에 따른 넓이 계산, 충돌 우선순위 개선)
- CI 단계에 검증을 추가해 실패 시 빌드 차단
