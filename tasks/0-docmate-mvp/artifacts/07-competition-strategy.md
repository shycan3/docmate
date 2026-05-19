# Competition Strategy & 2-Day Build Plan

**Document Version:** 1.0  
**Created:** 2026-05-19T15:00:00+0900  
**Deadline:** 2026-05-21T23:59:59+0900  
**Time Remaining:** 48 hours

---

## Executive Summary

DocMate는 현재 **dependency-light MVP** 상태입니다. 경진대회(5월 27일 신청 마감)에 경쟁력을 갖추려면, 심사위원들이 "실제 제품이다"라고 느낄 수 있는 3가지 핵심 기능을 48시간 내에 추가해야 합니다.

**핵심 목표:**
1. PDF 텍스트 추출 실제 동작 (fallback → 기능)
2. 분석 결과 저장/히스토리 (stateless → stateful)
3. Business Model 문서화 (기술만 강조 → 비즈니스 가치 제시)

---

## Why These 3?

### 심사 기준과의 매핑

**경진대회 평가 항목:**
- 시스템 설계 및 개발 (40%)
- 기술 창의성 (20%)
- Business Model 제안 (20%)
- 경영데이터 분석 (20%)

**현재 상태:**
| 항목 | 현재 | 문제점 | 개선 후 |
|------|------|--------|--------|
| 시스템 설계 | ⭐⭐⭐⭐ | PDF 추출이 fallback만 | ⭐⭐⭐⭐⭐ |
| 기술 창의성 | ⭐⭐⭐ | 표준 라이브러리만 | ⭐⭐⭐⭐ |
| Business Model | ⭐ | 전혀 없음 | ⭐⭐⭐⭐ |
| 경영데이터 분석 | ⭐ | 샘플만 존재 | ⭐⭐ (최소한) |

**선택하지 않은 것들 (48시간 불가능):**
- ❌ React 마이그레이션 (8시간+, 테스트 필요)
- ❌ Claude API 연동 (3시간, 비용/키 관리 복잡)
- ❌ Google OAuth (2시간, 설정 복잡)
- ❌ 고급 대시보드 (4시간+)

---

## 2-Day Implementation Plan

### Day 1 (2026-05-20): Backend Enhancement (4-5 hours)

**목표:** 실제 PDF 추출 + 데이터 저장 기능 구현

#### 1.1 PyMuPDF 통합 (1.5 hours)

**파일:** `backend/app/parser.py`

**현재 상태:**
```python
def extract_text_from_upload(filename: str, file_bytes: bytes) -> str:
    # Fallback: return first 200 chars as placeholder
    return "PDF 또는 텍스트 파일 업로드..."
```

**변경 내용:**
- PyMuPDF 추가: `pip install PyMuPDF`
- `.pdf` 확장자 → PyMuPDF로 추출
- 추출 실패 시 → 기존 fallback
- 테스트: 샘플 PDF로 검증

**결과:**
- PDF 파일을 실제로 읽을 수 있음
- 심사 데모에서 "제품 같은 느낌" 제공
- 발표때 "실제 기능" 강조 가능

#### 1.2 SQLite 저장소 추가 (2 hours)

**파일들:**
- `backend/app/storage.py` (신규)
- `backend/app/models.py` (확장)
- `backend/app/server.py` (수정)

**기능:**
1. **저장**: 분석 결과를 로컬 DB에 저장
2. **로드**: 과거 분석 결과 조회
3. **목록**: 저장된 분석 결과 목록 API

**새로운 엔드포인트:**
```
POST   /api/analyze         (기존 - 이제 자동으로 저장됨)
GET    /api/analyses        (저장된 분석 목록)
GET    /api/analyses/{id}   (특정 분석 결과 조회)
DELETE /api/analyses/{id}   (분석 결과 삭제)
```

**데이터베이스 스키마:**
```sql
CREATE TABLE analyses (
  id TEXT PRIMARY KEY,
  created_at TEXT,
  filename TEXT,
  document_text TEXT,
  profile JSON,
  extraction JSON,
  eligibility JSON,
  warnings JSON,
  checklist JSON,
  actions JSON
);
```

**결과:**
- 사용자가 분석 결과를 저장할 수 있음
- 다시 오면 과거 분석 결과를 볼 수 있음
- "상태를 가진 제품" → 심사위들에게 강한 인상

#### 1.3 테스트 및 검증 (1 hour)

- 모든 기존 테스트 통과 확인
- 새로운 엔드포인트 테스트 추가
- PDF 샘플로 실제 추출 테스트
- SQLite 저장/로드 테스트

---

### Day 2 (2026-05-21): Frontend + Documentation (4-5 hours)

**목표:** UI 개선 + 경진대회 발표 자료 준비

#### 2.1 히스토리/비교 UI 추가 (1.5 hours)

**파일:** `frontend/index.html`, `frontend/src/app.js`, `frontend/src/styles.css`

**추가 기능:**
1. **저장 버튼**: 분석 후 결과를 저장할 수 있음
2. **히스토리 탭**: 과거 분석 목록 표시
3. **비교 기능**: 두 공고를 나란히 비교 (선택사항)

**사용자 흐름:**
```
파일 업로드 → 분석 → 결과 화면에서 "저장" 버튼 → 
로컬 히스토리에 추가 → "히스토리" 탭에서 조회 가능 → 
과거 분석 다시 열기
```

**결과:**
- "발표 데모가 더 professional해 보임"
- 실제로 사용자가 여러 공고를 비교할 수 있음

#### 2.2 발표용 샘플 데이터 3개 준비 (1 hour)

**현재:** 샘플 1개 (2026 서울 청년 희망장학금)

**추가할 샘플:**
1. **대학원 장학금** (높은 학위 요구)
2. **지역 인재 정책** (지역 제한)
3. **저소득층 대상 기금** (소득 조건 엄격)

**사유:**
- 발표때 "다양한 공고를 처리할 수 있음" 보여주기
- 심사위들이 "아, 실제로 쓸 수 있겠네" 느낌
- 시스템이 다양한 조건을 잘 처리함을 증명

**구현:**
- `backend/app/sample_data.py` 확장
- 각 샘플마다 다른 프로필과 결과 매핑
- 발표 데모에서 3개를 차례대로 돌려보기

#### 2.3 Business Model 문서 작성 (1.5 hours)

**파일:** `docs/business-model.md` (신규)

**내용:**
1. **문제 정의**
   - 한국 청년 200만 명이 연평균 5~10개 공고 확인
   - 조건 이해에 평균 30분 소요
   - 자격 탈락률 40% (확인 부족)

2. **솔루션**
   - DocMate: 5초 만에 자격 판정
   - 체크리스트: 신청서 작성까지 자동 가이드
   - 결과 저장: 여러 공고 비교 가능

3. **시장**
   - TAM: 청년층 200만 명 × 월 평균 비용 5,000원 = 100억 시장
   - SAM: 1년 내 온라인 신청자 50만 명
   - SOM: 연 1억 원 (첫 2년)

4. **수익 모델**
   - 개인: 프리미엄 (3,000원/월) - 이력서 도우미, 자동 신청, AI 컨설팅
   - B2B: 대학/지자체 공고 관리 시스템 (월 500만원)
   - 제휴: 금융사 추천 커미션

5. **경쟁 우위**
   - 도메인 특화 (일반 사람 검색과 다름)
   - 자동화 (수동 심사 불가능)
   - 한국 청년정책 전문성

#### 2.4 README 업데이트 (1 hour)

**파일:** `README.md`

**추가 섹션:**
1. **새로운 기능 설명**
   - PDF 추출 (PyMuPDF)
   - 분석 결과 저장/로드 (SQLite)
   - 히스토리 관리

2. **로드맵**
   - Phase 1 (완료): MVP (dependency-light)
   - Phase 2 (준비): 저장소 + PDF 추출 (경진대회 버전)
   - Phase 3 (계획): React + LLM + OAuth

3. **설치 및 실행**
   ```bash
   pip install -r requirements.txt
   python backend/run.py
   # 브라우저: http://127.0.0.1:8000
   ```

4. **API 문서 확장**
   - 새로운 `/api/analyses` 엔드포인트 추가
   - 저장/로드 흐름 설명

**결과:**
- 심사위들이 "버전 관리가 명확하구나" 느낌
- 향후 발전 방향이 명확함

---

## Implementation Order

**Day 1 (5월 20일)**

| 시간 | 작업 | 파일 | 검증 |
|------|------|------|------|
| 1시간 | PyMuPDF 설치 + parser.py 수정 | parser.py | `python -c "import fitz"` |
| 0.5시간 | SQLite 스키마 및 storage.py 작성 | storage.py (신규) | 테이블 생성 확인 |
| 1시간 | 서버 엔드포인트 추가 | server.py | `/api/analyses` 동작 확인 |
| 0.5시간 | 테스트 작성 | tests/backend/test_storage.py | `unittest` 통과 |
| 1시간 | 통합 테스트 | tests/ | 모든 테스트 통과 |

**Day 2 (5월 21일)**

| 시간 | 작업 | 파일 | 검증 |
|------|------|------|------|
| 0.5시간 | 저장 버튼 UI 추가 | frontend/index.html | 버튼 표시 |
| 0.5시간 | 히스토리 탭 UI | frontend/index.html | 탭 전환 동작 |
| 0.5시간 | API 호출 로직 | frontend/src/app.js | 저장/로드 동작 |
| 1시간 | 샘플 데이터 3개 작성 | sample_data.py | 3개 모두 동작 |
| 1시간 | Business Model 문서 | docs/business-model.md | 완성도 체크 |
| 1시간 | README 업데이트 | README.md | 문서 완성 |

---

## Success Criteria

**Day 1 끝 (5월 20일 자정):**
- [ ] PDF 추출 실제 동작 (샘플 PDF로 테스트)
- [ ] 분석 결과 저장/로드 기능 (SQLite)
- [ ] 새로운 엔드포인트 테스트 통과
- [ ] 기존 모든 테스트 통과

**Day 2 끝 (5월 21일 자정):**
- [ ] 히스토리 UI 완성
- [ ] 샘플 데이터 3개 모두 동작
- [ ] Business Model 문서 완성
- [ ] README 완전히 업데이트
- [ ] 발표 데모 시연 가능

**최종 검증:**
```bash
python -m compileall backend scripts
python -m unittest discover -s tests -p "test_*.py"
node --check frontend/src/app.js
python scripts/check_smoke.py
```

모두 통과해야 함.

---

## Risk & Mitigation

| 리스크 | 확률 | 영향 | 대응 |
|--------|------|------|------|
| PyMuPDF 설치 오류 | 중간 | 높음 | 미리 테스트, pdfplumber 대안 준비 |
| SQLite 동시성 이슈 | 낮음 | 중간 | 로컬 테스트만 → 문제 없음 |
| UI 추가 후 기존 기능 깨짐 | 낮음 | 높음 | 모든 변경 후 `unittest` 실행 |
| 시간 초과 | 중간 | 높음 | 히스토리 UI를 "간단 버전"으로 축소 가능 |

**시간이 모자르면:**
1. 히스토리 UI → 저장 기능만 (로드는 API로 확인)
2. 샘플 3개 → 샘플 1개 유지 (설득력은 조금 낮아지지만 시간 절약)
3. Business Model → 핵심 3줄로 축약 (TAM/SAM/SOM)

---

## Notes for Future Codex Work

- 이 문서를 먼저 읽고, 아래 각 구현 문서를 참고하면서 코딩하기
- 변경사항이 생기면 이 문서를 먼저 업데이트한 후 코딩 시작
- Day 1 끝나면 `tasks/0-docmate-mvp/artifacts/08-backend-changes.md` 작성
- Day 2 끝나면 `tasks/0-docmate-mvp/artifacts/09-frontend-changes.md` 작성
- 최종 완성 후 `tasks/0-docmate-mvp/artifacts/10-final-summary.md` 작성

---

## Document References

- `docs/spec.md` - 기본 스펙
- `docs/architecture.md` - 현재 아키텍처
- `tasks/0-docmate-mvp/phase3.md` - MVP 완료 기준
- `tasks/0-docmate-mvp/artifacts/06-frontend-refresh.md` - 최근 UI 개선 사항

---

**Status:** Ready for Implementation  
**Next Step:** Day 1 - PyMuPDF 통합 시작
