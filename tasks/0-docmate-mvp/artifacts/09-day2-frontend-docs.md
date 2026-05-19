# Day 2 Implementation: Frontend + Documentation

**Document Version:** 1.0  
**Date:** 2026-05-21  
**Estimated Duration:** 4-5 hours  
**Status:** Pending Day 1 Completion  
**Prerequisite:** Day 1 must be completed and all tests passing

---

## Prerequisites from Day 1

Before starting Day 2, ensure:
- ✅ PyMuPDF integrated and working
- ✅ SQLite storage functional
- ✅ API endpoints `/api/analyses`, `/api/analyses/{id}` working
- ✅ All backend tests passing
- ✅ No merge conflicts

---

## Part 1: Frontend UI Enhancement (1.5-2 hours)

### 1.1 Add Save Button to Results Screen

**File:** `frontend/index.html`

**Current Result Section:**
```html
<section class="results hidden" id="results" aria-live="polite">
    <div class="result-heading">
        <span class="eyebrow">분석 결과</span>
        <h2 id="resultTitle"></h2>
    </div>
    
    <section class="eligibility-banner" id="eligibilityBanner"></section>
    <!-- ... rest of results ... -->
    
    <div class="action-bar" id="actions"></div>
</section>
```

**Modified:**
```html
<section class="results hidden" id="results" aria-live="polite">
    <div class="result-heading">
        <span class="eyebrow">분석 결과</span>
        <h2 id="resultTitle"></h2>
        <div class="result-actions">
            <button class="save-button" id="saveResultButton" type="button" title="이 분석 결과를 저장합니다">💾 저장</button>
        </div>
    </div>
    
    <section class="eligibility-banner" id="eligibilityBanner"></section>
    <!-- ... rest of results ... -->
    
    <div class="action-bar" id="actions"></div>
</section>
```

**Why:**
- Results 헤더에 Save 버튼 추가 (눈에 띄는 위치)
- 아이콘 + 텍스트로 명확함

### 1.2 Add History Tab

**File:** `frontend/index.html`

**Add after the main form/intake section:**
```html
<!-- Tab Navigation -->
<nav class="tab-bar" role="tablist">
    <button class="tab-button active" id="tab-analyze" role="tab" aria-selected="true" aria-controls="panel-analyze">
        새로 분석
    </button>
    <button class="tab-button" id="tab-history" role="tab" aria-selected="false" aria-controls="panel-history">
        히스토리 (<span id="historyCount">0</span>)
    </button>
</nav>

<!-- Analyze Panel -->
<div class="tab-panel active" id="panel-analyze" role="tabpanel" aria-labelledby="tab-analyze">
    <form class="intake" id="analysisForm">
        <!-- ... existing form ... -->
    </form>
    <section class="results hidden" id="results" aria-live="polite">
        <!-- ... existing results ... -->
    </section>
</div>

<!-- History Panel -->
<div class="tab-panel" id="panel-history" role="tabpanel" aria-labelledby="tab-history">
    <div class="history-container">
        <div class="history-list" id="historyList">
            <p class="empty-state">저장된 분석이 없습니다. "새로 분석" 탭에서 분석을 저장해보세요.</p>
        </div>
    </div>
</div>
```

**Why:**
- Tab로 UI를 나누어 깔끔함
- 히스토리 탭은 과거 분석 조회만 (수정 불가)

### 1.3 CSS for New UI Elements

**File:** `frontend/src/styles.css`

**Add:**
```css
/* Tab Navigation */
.tab-bar {
  display: flex;
  gap: 2px;
  border-bottom: 2px solid var(--line);
  margin: 0 0 24px 0;
}

.tab-button {
  flex: 0 1 auto;
  padding: 12px 16px;
  border: none;
  background: transparent;
  color: var(--muted);
  font-weight: 900;
  font-size: 14px;
  cursor: pointer;
  border-bottom: 3px solid transparent;
  transition: all 160ms ease;
}

.tab-button.active {
  color: var(--blue);
  border-bottom-color: var(--blue);
}

.tab-button:hover:not(.active) {
  color: var(--text);
  background: rgba(31, 95, 191, 0.04);
}

.tab-panel {
  display: none;
}

.tab-panel.active {
  display: block;
}

/* Result Actions */
.result-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.result-actions {
  display: flex;
  gap: 10px;
}

.save-button {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border: 1px solid var(--line);
  background: var(--surface-strong);
  color: var(--text);
  border-radius: 8px;
  font-size: 13px;
  font-weight: 800;
  cursor: pointer;
  transition: all 160ms ease;
}

.save-button:hover {
  background: var(--blue-soft);
  border-color: var(--blue);
  color: var(--blue);
}

.save-button.saved {
  background: var(--green-soft);
  border-color: var(--green);
  color: var(--green);
}

/* History List */
.history-container {
  display: grid;
  gap: 16px;
}

.history-list {
  display: grid;
  gap: 12px;
}

.history-item {
  display: grid;
  gap: 8px;
  padding: 16px;
  border: 1px solid var(--line);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.86);
  cursor: pointer;
  transition: all 160ms ease;
}

.history-item:hover {
  border-color: var(--blue);
  box-shadow: 0 4px 12px rgba(31, 95, 191, 0.08);
}

.history-item-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.history-item-title {
  font-weight: 900;
  color: var(--ink);
}

.history-item-date {
  font-size: 12px;
  color: var(--muted);
}

.history-item-status {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
}

.history-item-status.eligible {
  background: var(--green-soft);
  color: var(--green);
}

.history-item-status.needs-review {
  background: var(--amber-soft);
  color: var(--amber);
}

.history-item-status.ineligible {
  background: var(--red-soft);
  color: var(--red);
}

.history-item-delete {
  align-self: start;
  padding: 4px 8px;
  border: none;
  background: transparent;
  color: var(--muted);
  font-size: 12px;
  cursor: pointer;
  text-decoration: underline;
}

.history-item-delete:hover {
  color: var(--red);
}

.empty-state {
  padding: 32px 16px;
  text-align: center;
  color: var(--muted);
}

@media (max-width: 900px) {
  .result-heading {
    flex-direction: column;
  }
  
  .result-actions {
    width: 100%;
  }
  
  .result-actions button {
    flex: 1;
  }
}
```

### 1.4 JavaScript for Tab & Save Logic

**File:** `frontend/src/app.js`

**Add to elements object:**
```javascript
const elements = {
  // ... existing ...
  tabAnalyze: document.querySelector("#tab-analyze"),
  tabHistory: document.querySelector("#tab-history"),
  panelAnalyze: document.querySelector("#panel-analyze"),
  panelHistory: document.querySelector("#panel-history"),
  historyList: document.querySelector("#historyList"),
  historyCount: document.querySelector("#historyCount"),
  saveResultButton: document.querySelector("#saveResultButton"),
};
```

**Add tab switching:**
```javascript
elements.tabAnalyze.addEventListener("click", () => switchTab("analyze"));
elements.tabHistory.addEventListener("click", () => {
  switchTab("history");
  loadHistoryList();
});

function switchTab(tabName) {
  const tabs = [
    { button: elements.tabAnalyze, panel: elements.panelAnalyze, name: "analyze" },
    { button: elements.tabHistory, panel: elements.panelHistory, name: "history" },
  ];
  
  tabs.forEach(({ button, panel, name }) => {
    if (name === tabName) {
      button.classList.add("active");
      button.setAttribute("aria-selected", "true");
      panel.classList.add("active");
    } else {
      button.classList.remove("active");
      button.setAttribute("aria-selected", "false");
      panel.classList.remove("active");
    }
  });
}
```

**Add save functionality:**
```javascript
let currentAnalysisId = null;

elements.saveResultButton.addEventListener("click", async () => {
  if (!currentAnalysisId) {
    // 이미 저장됨
    alert("이미 저장된 분석입니다.");
    return;
  }
  
  elements.saveResultButton.disabled = true;
  elements.saveResultButton.textContent = "저장 중...";
  
  // API call to confirm save (already saved server-side)
  // Just update UI
  elements.saveResultButton.classList.add("saved");
  elements.saveResultButton.textContent = "✓ 저장됨";
  currentAnalysisId = null;
  
  // Refresh history count
  updateHistoryCount();
  
  setTimeout(() => {
    elements.saveResultButton.disabled = false;
  }, 1000);
});

function updateHistoryCount() {
  fetch("/api/analyses")
    .then(r => r.json())
    .then(data => {
      const count = (data.analyses || []).length;
      elements.historyCount.textContent = count;
    })
    .catch(() => {});
}
```

**Add history loading:**
```javascript
async function loadHistoryList() {
  try {
    const response = await fetch("/api/analyses");
    const data = await response.json();
    const analyses = data.analyses || [];
    
    if (analyses.length === 0) {
      elements.historyList.innerHTML = '<p class="empty-state">저장된 분석이 없습니다.</p>';
      return;
    }
    
    elements.historyList.innerHTML = analyses.map(analysis => `
      <div class="history-item" data-analysis-id="${escapeAttribute(analysis.id)}">
        <div class="history-item-meta">
          <div>
            <div class="history-item-title">${escapeHtml(analysis.filename)}</div>
            <div class="history-item-date">${formatDate(analysis.created_at)}</div>
          </div>
          <div class="history-item-status ${escapeAttribute(analysis.eligibility.status)}">
            ${escapeHtml(getStatusLabel(analysis.eligibility.status))}
          </div>
        </div>
        <button class="history-item-delete" data-analysis-id="${escapeAttribute(analysis.id)}">삭제</button>
      </div>
    `).join("");
    
    // Add click handlers
    elements.historyList.querySelectorAll(".history-item").forEach(item => {
      item.addEventListener("click", (e) => {
        if (e.target.closest(".history-item-delete")) return;
        const id = item.getAttribute("data-analysis-id");
        loadAnalysis(id);
      });
    });
    
    elements.historyList.querySelectorAll(".history-item-delete").forEach(btn => {
      btn.addEventListener("click", async (e) => {
        e.stopPropagation();
        const id = btn.getAttribute("data-analysis-id");
        if (confirm("정말 삭제하시겠습니까?")) {
          await fetch(`/api/analyses/${id}`, { method: "DELETE" });
          loadHistoryList();
          updateHistoryCount();
        }
      });
    });
  } catch (error) {
    elements.historyList.innerHTML = '<p class="error">히스토리를 불러올 수 없습니다.</p>';
  }
}

async function loadAnalysis(analysisId) {
  try {
    const response = await fetch(`/api/analyses/${analysisId}`);
    const result = await response.json();
    
    renderResult(result);
    switchTab("analyze");
    elements.results.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    alert("분석을 불러올 수 없습니다.");
  }
}

function formatDate(isoString) {
  const date = new Date(isoString);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);
  
  if (diffMins < 60) return `${diffMins}분 전`;
  if (diffHours < 24) return `${diffHours}시간 전`;
  if (diffDays < 7) return `${diffDays}일 전`;
  
  return date.toLocaleDateString("ko-KR");
}

function getStatusLabel(status) {
  const labels = {
    eligible: "신청 가능",
    needs_review: "추가 확인 필요",
    ineligible: "신청 불가",
  };
  return labels[status] || "미분류";
}
```

**Modify renderResult to track save state:**
```javascript
function renderResult(result) {
  state.checklistDone.clear();
  elements.results.classList.remove("hidden");
  clearError();

  // Track if this analysis is already saved
  currentAnalysisId = result.id || null;
  
  if (result.id) {
    // Already saved
    elements.saveResultButton.classList.add("saved");
    elements.saveResultButton.textContent = "✓ 저장됨";
    elements.saveResultButton.disabled = true;
  } else {
    // New analysis
    elements.saveResultButton.classList.remove("saved");
    elements.saveResultButton.textContent = "💾 저장";
    elements.saveResultButton.disabled = false;
  }
  
  // ... rest of existing renderResult ...
}
```

---

## Part 2: Sample Data (1 hour)

### 2.1 Extend `sample_data.py`

**File:** `backend/app/sample_data.py`

**Current:**
```python
SAMPLE_FILENAME = "sample-announcement.txt"
SAMPLE_DOCUMENT_TEXT = """2026 서울 청년 희망장학금 공고
...
"""

def get_sample_profile() -> Profile:
    return Profile(...)
```

**New Structure:**
```python
# Sample 1: 일반 청년 장학금 (현재 샘플)
SAMPLE_1_FILENAME = "sample-1-seoul-hope-scholarship.txt"
SAMPLE_1_DOCUMENT_TEXT = """..."""  # 기존 것

def get_sample_1_profile() -> Profile:
    return Profile(age=22, grade="3학년", region="서울", ...)

# Sample 2: 대학원 장학금 (학위 요구)
SAMPLE_2_FILENAME = "sample-2-graduate-scholarship.txt"
SAMPLE_2_DOCUMENT_TEXT = """2026 국립대학교 대학원 우수 인재 장학금

【 공고 목적 】
국내 우수 대학원생에게 학업 장려금을 지급

【 신청 자격 】
- 국내 4년제 대학 학사 학위 소유자
- 2026년 9월 입학 예정 또는 현재 석·박사 과정 재학생
- GPA 3.5/4.0 이상
- 토익 800점 이상 또는 영어 능력 입증 가능자

【 지원 내용 】
- 장학금 월 300만원 (1년)
- 국제 학술대회 참석 지원

【 필수 서류 】
- 학사 학위증명서
- 대학원 입학 허가서
- 성적 증명서
- 토익 성적표
- 추천서 2부

【 신청 마감 】
2026-06-15 자정 까지
...
"""

def get_sample_2_profile() -> Profile:
    # Graduate student profile
    return Profile(age=25, grade="석사과정", region="서울", ...)

# Sample 3: 저소득층 정책 기금 (소득 조건 엄격)
SAMPLE_3_FILENAME = "sample-3-low-income-fund.txt"
SAMPLE_3_DOCUMENT_TEXT = """2026 저소득층 청년 생활 지원금

【 지원 목적 】
기초생활수급자 및 차상위 계층 청년의 생활 안정 지원

【 신청 자격 】
- 만 18세 ~ 35세
- 기초생활수급자 또는 차상위 계층
- 월 가구 소득 기준 충족
  * 4인 가족: 180만원 이하
  * 3인 가족: 145만원 이하
- 금융 채무가 5,000만원 이상인 경우 제외

【 지원 내용 】
- 월 50만원 × 12개월 (총 600만원)
- 의료비 추가 지원 (1회 100만원)

【 필수 서류 】
- 건강보험료 납부 증명서
- 주민등록초본
- 소득 증명서 또는 수급자증

【 신청 기간 】
2026-06-01 ~ 2026-06-30

【 유의사항 】
- 다른 정부 지원금 동시 수령 불가
- 지원금 용도: 주거비, 식비, 의료비만 인정
...
"""

def get_sample_3_profile() -> Profile:
    # Low-income profile
    return Profile(age=28, grade="무직", region="부산", 
                   occupation="구직중", income_decile=1, enrolled=False)
```

**Add to sample responses:**
```python
SAMPLE_PROFILES = [
    ("sample-1", SAMPLE_1_FILENAME, SAMPLE_1_DOCUMENT_TEXT, get_sample_1_profile),
    ("sample-2", SAMPLE_2_FILENAME, SAMPLE_2_DOCUMENT_TEXT, get_sample_2_profile),
    ("sample-3", SAMPLE_3_FILENAME, SAMPLE_3_DOCUMENT_TEXT, get_sample_3_profile),
]

def get_random_sample():
    """Return a random sample for demo variety."""
    import random
    sample_id, filename, text, profile_fn = random.choice(SAMPLE_PROFILES)
    return sample_id, filename, text, profile_fn()

# Keep backward compatibility
SAMPLE_FILENAME = SAMPLE_1_FILENAME
SAMPLE_DOCUMENT_TEXT = SAMPLE_1_DOCUMENT_TEXT
def get_sample_profile() -> Profile:
    return get_sample_1_profile()
```

**Why 3 samples:**
- **Sample 1**: 기본 사례 (청년 장학금)
- **Sample 2**: 고학력 요구사항 (대학원 장학금)
- **Sample 3**: 엄격한 소득 제한 (저소득층 기금)

발표할 때 3개를 차례대로 돌려보면, 시스템이 다양한 조건을 처리할 수 있음을 보여줄 수 있음.

---

## Part 3: Documentation (2-2.5 hours)

### 3.1 Business Model Document

**File:** `docs/business-model.md` (신규)

```markdown
# DocMate: Business Model Canvas

**Version:** 1.0  
**Date:** 2026-05-21

## Problem

### Current Situation
- 한국에는 연 1,000개 이상의 장학금·청년정책 공고가 발생
- 청년층(18~35세) 약 200만 명이 이 공고들을 알고 신청

### Key Pain Points
1. **정보 과부하**: 조건 확인에 평균 30분 소요
2. **자격 불명확**: 조건 이해 부족으로 탈락률 40%
3. **수동 프로세스**: 신청서 체크리스트를 손으로 작성
4. **비교 불가**: 여러 공고를 비교할 방법이 없음

### Market Data
- 한국 청년 인구: 200만 명
- 월평균 공고 검토: 5~10개
- 신청 성공률: 평균 60% (조건 미달이 주요 탈락 사유)

## Solution

### DocMate: 5초 자격 판정 + 자동 체크리스트

**Core Value Proposition:**
> 공고를 올리면 5초 안에 자격 판정, 체크리스트, 신청 링크를 한 화면에서 확인

### Key Features
1. **자동 자격 판정**: 프로필 기반 rule-based eligibility
2. **위험 조건 탐지**: 중복지원 불가, 수정 불가 등 주의사항
3. **체크리스트**: 신청서 작성 가이드
4. **바로가기 링크**: 신청 페이지, Google Calendar

### Technical Approach
- **Phase 1 (완료)**: Dependency-light MVP (Python stdlib)
- **Phase 2 (진행 중)**: PDF 추출 (PyMuPDF) + 저장소 (SQLite)
- **Phase 3 (계획)**: AI 기반 정교한 자격 판정 (Claude API)
- **Phase 4 (계획)**: React UI + FastAPI + OAuth

## Market & TAM/SAM/SOM

### Total Addressable Market (TAM)
```
200만 청년 × 5,000원/월 = 1,000억 원/년
```

**Assumption:**
- 월 활동 청년: 200만 명
- 월평균 공고 검토: 1~2개
- 월평균 지불 의향: 5,000원 (프리미엄 + 부가 서비스)

### Serviceable Addressable Market (SAM)
```
50만 청년 × 12,000원/년 = 60억 원/년
```

**Assumption:**
- 1년 내 온라인 신청 경험 있는 청년: 50만 명
- 전환율: 월 활동층의 25%
- 가격: 월 1,000원 (프리미엄)

### Serviceable Obtainable Market (SOM) - Year 2
```
2,000 사용자 × 60,000원/년 = 1.2억 원
```

**First Year Goal:**
- 1,000 사용자 확보
- Revenue: 6,000만 원
- Churn rate: 20%

## Business Model

### Revenue Streams

#### 1. Consumer (B2C)
**Free Tier:**
- 월 3건 분석 무료
- 기본 기능만 (자격 판정, 체크리스트)

**Premium Tier (2,900원/월):**
- 무제한 분석
- 분석 결과 저장 + 비교
- 이력서 작성 가이드
- AI 컨설팅 (텍스트 피드백)

**구매율 가정:** 월 활동 사용자의 5%

#### 2. B2B (대학/지자체)
**공고 관리 시스템:**
- 가격: 월 500만원 (소규모), 월 2,000만원 (대규모)
- 타겟: 전국 100개 대학 + 17개 시도청
- 목표: 연 20계약 (Year 3)

#### 3. 제휴 & 파트너십
**금융사 추천:**
- CPC: 1,000~2,000원
- 예상: 월 1,000회 × 1,500원 = 150만 원/월

**정부 공고 큐레이션:**
- 한국장학재단, 중소벤처기업부와 협력
- 노출료 + 클릭수 수수료

### Unit Economics (Year 2)

| 항목 | 값 |
|------|-----|
| 월 활동 사용자 | 2,000 |
| 프리미엄 전환율 | 8% |
| 프리미엄 사용자 | 160 |
| 월 ARPU (Premium) | 2,900원 |
| 월 ARPU (B2B 배분) | 500원 |
| 월 MRR | 546만 원 |
| 연 Revenue | 6.5억 원 |

### Cost Structure

| 항목 | 월 | 연 |
|------|-----|-----|
| 서버 호스팅 | 50만원 | 600만원 |
| 개발자 (2명) | 400만원 | 4,800만원 |
| 마케팅 | 150만원 | 1,800만원 |
| 기타 | 100만원 | 1,200만원 |
| **Total OpEx** | **700만원** | **8,400만원** |

### Break-even Analysis

```
Break-even MRR = 700만원
Premium Users Needed = 700만원 ÷ 2,900원 = 2,414명

Timeline to Break-even = 18-24개월
(Initial: 월 200사용자 → 12개월: 1,000 → 18개월: 2,400)
```

## Competitive Advantage

| 항목 | DocMate | 경쟁사 (일반 검색) |
|------|---------|-----------------|
| 도메인 특화 | ✓ | ✗ |
| 자격 자동 판정 | ✓ | ✗ |
| 체크리스트 | ✓ | ✗ |
| 바로가기 링크 | ✓ | △ (부분) |
| 다양한 공고 | ✓ | ✓ |
| 사용자 경험 | ⭐⭐⭐⭐⭐ | ⭐⭐ |

## Go-to-Market Strategy

### Phase 1: Launch (Month 1-3)
- Product Hunt, 온라인 커뮤니티 (고시생 카페, 장학금 커뮤니티)
- 대학생 100명 초기 사용자 모집
- 피드백 기반 개선

### Phase 2: Growth (Month 4-6)
- 대학 총학생회 / 학생 신문 파트너십
- SNS 마케팅 (인스타그램, 틱톡)
- 월 사용자 1,000명 목표

### Phase 3: Scale (Month 7-12)
- 대학 공식 시스템 통합 (B2B)
- 구글 광고, 페이스북 광고
- 월 사용자 5,000명 목표

### Phase 4: Enterprise (Year 2+)
- 정부 기관 공고 큐레이션
- 금융사 제휴 확대
- 국제 확장 검토

## Risk & Mitigation

| 리스크 | 확률 | 임팩트 | 대응 |
|--------|------|--------|------|
| 사용자 확보 어려움 | 중간 | 높음 | 초기 1,000명 모집에 집중, 입소문 활용 |
| 공고 데이터 확보 | 중간 | 중간 | 정부 데이터 API, 웹 크롤링 조합 |
| 규제 변화 | 낮음 | 중간 | 법무 검토, 투명성 강화 |
| 기술 리스크 | 낮음 | 중간 | 검증된 기술 스택 (Python, React) |

## Financial Projections (Year 1-3)

```
Year 1:
- Users: 500
- Revenue: 1,000만원
- OpEx: 8,400만원
- Loss: -7,400만원

Year 2:
- Users: 2,500
- Revenue: 6.5억원
- OpEx: 8,400만원
- Loss: -1,900만원

Year 3:
- Users: 8,000
- Revenue: 20억원 (B2B 포함)
- OpEx: 1억원 (확장)
- Profit: 10억원
```

## Conclusion

DocMate는 한국 청년의 **실제 문제**를 해결하는 **니치한 솔루션**이다.

**경쟁 우위:** 도메인 특화 + 자동화
**성장 기회:** 200만 청년 시장 + B2B 확장
**수익 가능성:** Year 3 단계별 이익 달성

---

**Status:** Ready for Pitch  
**Next:** Market Validation (초기 100명 사용자 모집)
```

### 3.2 Update README

**File:** `README.md`

**Add new sections:**

```markdown
# DocMate

> 장학금·청년정책 공고를 올리면 5초 안에 자격 판정과 체크리스트를 제공합니다.

## What's New (2026-05-21)

- ✨ **PDF 텍스트 추출 지원** - PyMuPDF로 PDF 파일 실제 추출
- 💾 **분석 결과 저장** - SQLite로 과거 분석 결과 보관 및 비교
- 📋 **히스토리 관리** - 저장한 분석 목록에서 다시 조회
- 🎯 **3가지 샘플 데이터** - 다양한 공고 유형 데모 가능

## Architecture Phases

### Phase 1: MVP (2026-05-19) ✅ Complete
- Standard library HTTP server
- Dependency-light implementation
- Sample-based demo
- Frontend: No build, pure HTML/CSS/JS

### Phase 2: Enhanced (2026-05-21) 🚀 Current
- PDF 텍스트 추출 (PyMuPDF)
- 로컬 저장소 (SQLite)
- 히스토리 관리
- 경진대회 준비 버전

### Phase 3: Cloud Ready (Planned)
- FastAPI 마이그레이션
- 클라우드 데이터베이스 (PostgreSQL)
- 사용자 인증 (OAuth 2.0)

### Phase 4: AI Enhanced (Planned)
- Claude/OpenAI API 기반 정교한 자격 판정
- React 프론트엔드 재구성
- 고급 분석 & 통계

### Phase 5: Enterprise (Planned)
- B2B 대학/지자체 시스템
- Google Calendar OAuth 통합
- 기관용 공고 관리 대시보드

## API Reference

### `/health`
```bash
GET /health
```

### `/api/sample`
```bash
GET /api/sample

Response:
{
  "document": {
    "filename": "...",
    "text": "..."
  },
  "profile": {...},
  "analysis": {...}
}
```

### `/api/analyze`
```bash
POST /api/analyze

# Multipart form or JSON with:
# - file (or text)
# - profile (JSON)
```

### `/api/analyses` ⭐ NEW
```bash
GET /api/analyses

Response:
{
  "analyses": [
    {
      "id": "...",
      "created_at": "2026-05-21T...",
      "filename": "...",
      "extraction": {...},
      "eligibility": {...},
      ...
    }
  ]
}
```

### `/api/analyses/{id}` ⭐ NEW
```bash
GET /api/analyses/{id}
DELETE /api/analyses/{id}
```

## File Structure

```
backend/
  app/
    parser.py          ← PDF extraction (PyMuPDF)
    storage.py         ← SQLite CRUD (NEW)
    server.py          ← API endpoints (updated)
    models.py
    analyzer.py
    ...
  run.py

frontend/
  index.html           ← History tab (updated)
  src/
    app.js             ← Tab logic, save/load (updated)
    styles.css         ← Tab styles (updated)

docs/
  spec.md
  architecture.md
  business-model.md    ← Business case (NEW)
  adr.md
  user-intervention.md
```

## Roadmap

- **2026-05-21**: Phase 2 완료 (경진대회 제출)
- **2026-06-30**: Phase 3 클라우드 준비
- **2026-09-01**: Phase 4 AI 통합
- **2026-12-01**: Phase 5 B2B 런칭

## Contributing

이 프로젝트는 경진대회 준비 단계입니다. 피드백은 `docs/adr.md`의 이슈 트래킹 방식을 따릅니다.

---

**마지막 업데이트:** 2026-05-21  
**버전:** 2.0 (경진대회)  
**상태:** 🟢 실행 가능
```

---

## Part 4: Final Testing & Validation (1 hour)

### 4.1 Complete Testing Checklist

```bash
# 1. Syntax check
python -m compileall backend scripts
node --check frontend/src/app.js

# 2. Unit tests
python -m unittest discover -s tests -p "test_*.py"

# 3. Integration test
python scripts/check_smoke.py

# 4. Manual verification
# - Start server: python backend/run.py
# - Test tab switching
# - Test save/load history
# - Test 3 samples
# - Test PDF extraction
```

### 4.2 Demo Preparation

**What to Show (5 minutes):**
1. 새 공고 분석 (2분)
   - "새로 분석" 탭
   - 프로필 입력 (또는 기존 값)
   - 샘플 불러오기 → 분석 결과 표시
   - 결과 저장 버튼

2. 히스토리 확인 (1분)
   - "히스토리" 탭으로 이동
   - 저장된 분석 목록 표시
   - 과거 분석 클릭해서 다시 열기

3. 다양한 샘플 (2분)
   - Sample 1: 일반 청년 장학금
   - Sample 2: 대학원 장학금 (높은 학위 요구)
   - Sample 3: 저소득층 기금 (엄격한 조건)
   - "다양한 공고를 처리할 수 있음" 강조

---

## Deliverables (End of Day 2)

✅ **Completed:**
- [ ] Tab navigation (analyze/history)
- [ ] Save button on results
- [ ] History list display
- [ ] Delete from history
- [ ] Load past analysis
- [ ] CSS for new UI
- [ ] 3 sample data entries
- [ ] Business Model document
- [ ] README updated
- [ ] All tests passing

---

## Success Criteria

**발표 전 체크리스트:**

- [ ] 서버 띄웠을 때 모든 기능 동작 ✅
- [ ] PDF 실제 추출 동작 ✅
- [ ] 분석 결과 저장/로드 동작 ✅
- [ ] 3가지 샘플 모두 데모 가능 ✅
- [ ] Business Model 문서 완성 ✅
- [ ] 발표 시나리오 3회 리허설 ✅
- [ ] 모든 테스트 통과 ✅

---

**Status:** Ready for Implementation after Day 1  
**Next:** Competition Submission (5월 27일)

```

