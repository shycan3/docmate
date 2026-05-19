const state = {
  checklistDone: new Set(),
  currentAnalysisId: null,
  samples: [],
};

const DRAFT_STORAGE_KEY = "docmate.profileDraft";

const statusText = {
  eligible: {
    label: "신청 가능",
    className: "eligible",
    body: "입력한 프로필 기준으로 기본 조건을 충족합니다.",
  },
  needs_review: {
    label: "추가 확인 필요",
    className: "needs-review",
    body: "자동 판정만으로 확정하기 어려운 항목이 있습니다.",
  },
  ineligible: {
    label: "신청 불가",
    className: "ineligible",
    body: "필수 조건 중 충족하지 못한 항목이 있습니다.",
  },
};

const elements = {
  tabAnalyze: document.querySelector("#tabAnalyze"),
  tabHistory: document.querySelector("#tabHistory"),
  panelAnalyze: document.querySelector("#panelAnalyze"),
  panelHistory: document.querySelector("#panelHistory"),
  historyCount: document.querySelector("#historyCount"),
  historyMetricCount: document.querySelector("#historyMetricCount"),
  sampleMetricCount: document.querySelector("#sampleMetricCount"),
  historyList: document.querySelector("#historyList"),
  historySummary: document.querySelector("#historySummary"),
  refreshHistoryButton: document.querySelector("#refreshHistoryButton"),
  form: document.querySelector("#analysisForm"),
  fileInput: document.querySelector("#documentFile"),
  fileLabel: document.querySelector("#fileLabel"),
  fileMeta: document.querySelector("#fileMeta"),
  sampleSelect: document.querySelector("#sampleSelect"),
  sampleCards: document.querySelector("#sampleCards"),
  analyzeButton: document.querySelector("#analyzeButton"),
  sampleButton: document.querySelector("#sampleButton"),
  resetButton: document.querySelector("#resetButton"),
  errorBox: document.querySelector("#errorBox"),
  results: document.querySelector("#results"),
  saveResultButton: document.querySelector("#saveResultButton"),
  resultTitle: document.querySelector("#resultTitle"),
  resultStats: document.querySelector("#resultStats"),
  profileStatus: document.querySelector("#profileStatus"),
  documentStatus: document.querySelector("#documentStatus"),
  eligibilityBanner: document.querySelector("#eligibilityBanner"),
  metaList: document.querySelector("#metaList"),
  conditionList: document.querySelector("#conditionList"),
  benefitList: document.querySelector("#benefitList"),
  documentList: document.querySelector("#documentList"),
  warningCount: document.querySelector("#warningCount"),
  warningList: document.querySelector("#warningList"),
  checklistProgress: document.querySelector("#checklistProgress"),
  checklist: document.querySelector("#checklist"),
  actions: document.querySelector("#actions"),
};

restoreDraft();
loadSampleOptions();
updateHistoryCount();
updateIntakeStatus();

elements.tabAnalyze.addEventListener("click", () => switchTab("analyze"));
elements.tabHistory.addEventListener("click", () => {
  switchTab("history");
  loadHistoryList();
});

elements.refreshHistoryButton.addEventListener("click", loadHistoryList);

elements.saveResultButton.addEventListener("click", () => {
  if (!state.currentAnalysisId) {
    return;
  }
  switchTab("history");
  loadHistoryList();
});

elements.fileInput.addEventListener("change", () => {
  const file = elements.fileInput.files[0];
  if (!file) {
    elements.fileLabel.textContent = "PDF 파일 선택";
    elements.fileMeta.textContent = "선택된 파일 없음";
    return;
  }

  elements.fileLabel.textContent = file.name;
  elements.fileMeta.textContent = `${formatBytes(file.size)} · ${file.type || "파일"}`;
  updateIntakeStatus();
});

document.querySelectorAll("#analysisForm input, #analysisForm select").forEach((field) => {
  field.addEventListener("input", () => {
    saveDraft();
    updateIntakeStatus();
  });
  field.addEventListener("change", () => {
    saveDraft();
    updateIntakeStatus();
  });
});

elements.sampleSelect.addEventListener("change", () => {
  syncSelectedSampleCard();
  updateIntakeStatus();
});

elements.sampleButton.addEventListener("click", async () => {
  setBusy(true, "샘플 분석 중");
  clearError();

  try {
    await applySelectedSampleProfile();
    const result = await analyze({ useSample: true });
    renderResult(result);
    updateHistoryCount();
  } catch (error) {
    renderError(error.message);
  } finally {
    setBusy(false);
  }
});

elements.resetButton.addEventListener("click", () => {
  elements.form.reset();
  elements.fileInput.value = "";
  elements.fileLabel.textContent = "PDF 파일 선택";
  elements.fileMeta.textContent = "선택된 파일 없음";
  clearError();
  state.checklistDone.clear();
  state.currentAnalysisId = null;
  elements.results.classList.add("hidden");
  saveDraft();
  updateIntakeStatus();
  syncSelectedSampleCard();
});

elements.form.addEventListener("submit", async (event) => {
  event.preventDefault();
  setBusy(true);
  clearError();

  try {
    const result = await analyze();
    renderResult(result);
    updateHistoryCount();
  } catch (error) {
    renderError(error.message);
  } finally {
    setBusy(false);
  }
});

async function loadSampleOptions() {
  try {
    const selectedSampleId = elements.sampleSelect.value;
    const response = await fetch("/api/samples");
    const payload = await readApiResponse(response);
    const samples = payload.samples || [];
    if (!samples.length) {
      return;
    }

    state.samples = samples;
    elements.sampleMetricCount.textContent = String(samples.length);
    elements.sampleSelect.innerHTML = samples
      .map(
        (sample) => `
          <option value="${escapeAttribute(sample.id)}">${escapeHtml(sample.label)}</option>
        `
      )
      .join("");
    if (samples.some((sample) => sample.id === selectedSampleId)) {
      elements.sampleSelect.value = selectedSampleId;
    }
    renderSampleCards(samples);
  } catch {
    // Keep the static fallback options from the HTML.
  }
}

function renderSampleCards(samples) {
  elements.sampleCards.innerHTML = samples
    .map(
      (sample) => `
        <button class="sample-card" type="button" data-sample-id="${escapeAttribute(sample.id)}">
          <span>${escapeHtml(sample.label)}</span>
          <small>${escapeHtml(sample.description || sample.filename)}</small>
        </button>
      `
    )
    .join("");

  elements.sampleCards.querySelectorAll("[data-sample-id]").forEach((button) => {
    button.addEventListener("click", () => {
      elements.sampleSelect.value = button.dataset.sampleId;
      syncSelectedSampleCard();
      updateIntakeStatus();
    });
  });
  syncSelectedSampleCard();
}

function syncSelectedSampleCard() {
  elements.sampleCards.querySelectorAll("[data-sample-id]").forEach((button) => {
    button.classList.toggle("active", button.dataset.sampleId === elements.sampleSelect.value);
  });
}

async function applySelectedSampleProfile() {
  const sampleId = elements.sampleSelect.value;
  const response = await fetch(`/api/sample?sample_id=${encodeURIComponent(sampleId)}`);
  const payload = await readApiResponse(response);
  if (payload.profile) {
    writeProfile(payload.profile);
    saveDraft();
  }
}

async function analyze(options = {}) {
  const { useSample = false } = options;
  const file = elements.fileInput.files[0];
  if (!file && !useSample) {
    throw new Error("분석할 PDF 또는 텍스트 파일을 선택하세요.");
  }

  const formData = new FormData();
  if (!useSample) {
    formData.append("file", file);
  } else {
    formData.append("use_sample", "true");
    formData.append("sample_id", elements.sampleSelect.value);
  }
  formData.append("profile", JSON.stringify(readProfile()));

  const response = await fetch("/api/analyze", {
    method: "POST",
    body: formData,
  });
  return readApiResponse(response);
}

async function readApiResponse(response) {
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.detail || "요청을 처리하지 못했습니다.");
  }
  return payload;
}

function readProfile() {
  const enrolledStatus = valueOf("#enrolledStatus");
  return {
    age: valueAsNumber("#age"),
    grade: valueOf("#grade"),
    region: valueOf("#region"),
    occupation: valueOf("#occupation"),
    income_decile: valueAsNumber("#incomeDecile"),
    enrolled: enrolledStatus === "" ? null : enrolledStatus === "true",
  };
}

function writeProfile(profile = {}) {
  setInputValue("#age", profile.age);
  setInputValue("#grade", profile.grade);
  setInputValue("#region", profile.region);
  setInputValue("#occupation", profile.occupation);
  setInputValue("#incomeDecile", profile.income_decile);
  setInputValue("#enrolledStatus", profile.enrolled === null || profile.enrolled === undefined ? "" : String(profile.enrolled));
}

function saveDraft() {
  const draft = { ...readProfile(), sample_id: elements.sampleSelect.value };
  try {
    localStorage.setItem(DRAFT_STORAGE_KEY, JSON.stringify(draft));
  } catch {
    // Ignore storage failures in private mode or restricted environments.
  }
}

function restoreDraft() {
  let draft = null;
  try {
    draft = JSON.parse(localStorage.getItem(DRAFT_STORAGE_KEY) || "null");
  } catch {
    draft = null;
  }

  if (!draft || typeof draft !== "object") {
    return;
  }

  writeProfile(draft);
  if (draft.sample_id) {
    elements.sampleSelect.value = draft.sample_id;
  }
}

function setInputValue(selector, value) {
  const field = document.querySelector(selector);
  if (!field) {
    return;
  }
  field.value = value == null ? "" : String(value);
}

function valueOf(selector) {
  return document.querySelector(selector).value.trim();
}

function valueAsNumber(selector) {
  const value = document.querySelector(selector).value;
  return value === "" ? null : Number(value);
}

function switchTab(tabName) {
  const isHistory = tabName === "history";
  elements.tabAnalyze.classList.toggle("active", !isHistory);
  elements.tabAnalyze.setAttribute("aria-selected", String(!isHistory));
  elements.panelAnalyze.classList.toggle("active", !isHistory);

  elements.tabHistory.classList.toggle("active", isHistory);
  elements.tabHistory.setAttribute("aria-selected", String(isHistory));
  elements.panelHistory.classList.toggle("active", isHistory);
}

function renderResult(result) {
  state.checklistDone.clear();
  state.currentAnalysisId = result.id || null;
  elements.results.classList.remove("hidden");
  clearError();

  if (result.profile) {
    writeProfile(result.profile);
    saveDraft();
  }

  const extraction = result.extraction || {};
  elements.resultTitle.textContent = extraction.title || "분석 결과";
  renderSaveState();
  renderResultStats(result);
  renderEligibility(result.eligibility || {});
  renderMeta(extraction);
  renderList(elements.conditionList, extraction.eligibility_conditions);
  renderList(elements.benefitList, extraction.benefits);
  renderList(elements.documentList, extraction.required_documents);
  renderWarnings(result.warnings || []);
  renderChecklist(result.checklist || []);
  renderActions(result.actions || []);
  elements.results.scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderResultStats(result) {
  const extraction = result.extraction || {};
  const warnings = result.warnings || [];
  const checklist = result.checklist || [];
  const actions = result.actions || [];
  const applyAction = actions.find((action) => action.kind === "apply");
  const deadline = extraction.application_period || "확인 필요";

  elements.resultStats.innerHTML = [
    ["신청 상태", statusLabel(result.eligibility?.status), statusClass(result.eligibility?.status)],
    ["마감/기간", deadline, ""],
    ["위험 조건", `${warnings.length}개`, warnings.length ? "warning" : "eligible"],
    ["할 일", `${checklist.length}개`, ""],
    ["신청 링크", applyAction ? "있음" : "없음", applyAction ? "eligible" : "needs-review"],
  ]
    .map(
      ([label, value, tone]) => `
        <div class="result-stat ${escapeAttribute(tone)}">
          <span>${escapeHtml(label)}</span>
          <strong>${escapeHtml(value)}</strong>
        </div>
      `
    )
    .join("");
}

function renderSaveState() {
  if (state.currentAnalysisId) {
    elements.saveResultButton.textContent = "저장됨 · 히스토리 보기";
    elements.saveResultButton.classList.add("saved");
    elements.saveResultButton.disabled = false;
    return;
  }
  elements.saveResultButton.textContent = "저장 실패";
  elements.saveResultButton.classList.remove("saved");
  elements.saveResultButton.disabled = true;
}

function renderEligibility(eligibility) {
  const meta = statusText[eligibility.status] || statusText.needs_review;
  const reasons = eligibility.reasons || [];
  const missing = eligibility.missing_information || [];
  const notes = [
    ...reasons,
    ...missing.map((item) => `${item} 정보가 필요합니다.`),
  ];

  elements.eligibilityBanner.className = `eligibility-banner ${meta.className}`;
  elements.eligibilityBanner.innerHTML = `
    <div>
      <span class="result-label">${escapeHtml(meta.label)}</span>
      <p>${escapeHtml(meta.body)}</p>
    </div>
    ${renderInlineNotes(notes)}
  `;
}

function renderMeta(extraction) {
  const rows = [
    ["신청 기간", extraction.application_period],
    ["신청 방법", extraction.application_method],
    ["신청 URL", extraction.application_url],
  ];

  elements.metaList.innerHTML = rows
    .map(([label, value]) => renderMetaRow(label, value))
    .join("");
}

function renderMetaRow(label, value) {
  const content = formatValue(value);
  return `
    <div class="meta-row">
      <dt>${escapeHtml(label)}</dt>
      <dd>${content}</dd>
    </div>
  `;
}

function renderList(container, value) {
  const items = Array.isArray(value) ? value.filter(Boolean) : [];
  if (!items.length) {
    container.innerHTML = `<li class="muted">추출된 항목이 없습니다.</li>`;
    return;
  }

  container.innerHTML = items.map((item) => `<li>${escapeHtml(item)}</li>`).join("");
}

function renderWarnings(warnings) {
  elements.warningCount.textContent = `${warnings.length}개`;
  if (!warnings.length) {
    elements.warningList.innerHTML = `<p class="muted">탐지된 위험 조건이 없습니다.</p>`;
    return;
  }

  elements.warningList.innerHTML = warnings
    .map(
      (warning) => `
        <article class="warning-item ${escapeAttribute(warning.severity)}">
          <strong>${escapeHtml(warning.title)}</strong>
          <span>${escapeHtml(warning.evidence)}</span>
        </article>
      `
    )
    .join("");
}

function renderChecklist(items) {
  updateChecklistProgress(items.length);
  if (!items.length) {
    elements.checklist.innerHTML = `<p class="muted">생성된 체크리스트가 없습니다.</p>`;
    return;
  }

  elements.checklist.innerHTML = items
    .map((item, index) => {
      const action = item.action_url
        ? `<a href="${escapeAttribute(item.action_url)}" target="_blank" rel="noreferrer">열기</a>`
        : "";
      return `
        <label class="check-item">
          <input type="checkbox" data-check-index="${index}" />
          <span>
            <strong>${escapeHtml(item.title)}</strong>
            <small>${escapeHtml(item.description)}</small>
          </span>
          ${action}
        </label>
      `;
    })
    .join("");

  elements.checklist.querySelectorAll("input[type='checkbox']").forEach((checkbox) => {
    checkbox.addEventListener("change", () => {
      const index = Number(checkbox.dataset.checkIndex);
      if (checkbox.checked) {
        state.checklistDone.add(index);
      } else {
        state.checklistDone.delete(index);
      }
      updateChecklistProgress(items.length);
    });
  });
}

function updateChecklistProgress(total) {
  elements.checklistProgress.textContent = `${state.checklistDone.size}/${total}`;
}

function renderActions(actions) {
  if (!actions.length) {
    elements.actions.innerHTML = "";
    return;
  }

  elements.actions.innerHTML = actions
    .map(
      (action) => `
        <a class="action-button ${escapeAttribute(action.kind)}" href="${escapeAttribute(action.url)}" target="_blank" rel="noreferrer">
          ${escapeHtml(action.label)}
        </a>
      `
    )
    .join("");
}

async function updateHistoryCount() {
  try {
    const response = await fetch("/api/analyses");
    const payload = await readApiResponse(response);
    const count = String((payload.analyses || []).length);
    elements.historyCount.textContent = count;
    elements.historyMetricCount.textContent = count;
  } catch {
    elements.historyCount.textContent = "0";
    elements.historyMetricCount.textContent = "0";
  }
}

async function loadHistoryList() {
  elements.historyList.innerHTML = `<p class="empty-state">히스토리를 불러오는 중입니다.</p>`;
  elements.refreshHistoryButton.disabled = true;

  try {
    const response = await fetch("/api/analyses");
    const payload = await readApiResponse(response);
    const analyses = payload.analyses || [];
    elements.historyCount.textContent = String(analyses.length);
    elements.historyMetricCount.textContent = String(analyses.length);
    elements.historySummary.textContent = analyses.length
      ? `최근 ${analyses.length}개 분석이 저장되어 있습니다. 항목을 선택하면 결과 화면으로 돌아갑니다.`
      : "저장된 결과를 불러오면 입력값과 분석 결과가 함께 복원됩니다.";
    renderHistoryList(analyses);
  } catch (error) {
    elements.historyList.innerHTML = `<p class="empty-state error-text">${escapeHtml(error.message)}</p>`;
  } finally {
    elements.refreshHistoryButton.disabled = false;
  }
}

function renderHistoryList(analyses) {
  if (!analyses.length) {
    elements.historyList.innerHTML = `<p class="empty-state">저장된 분석이 없습니다. 샘플이나 파일을 분석하면 여기에 쌓입니다.</p>`;
    return;
  }

  elements.historyList.innerHTML = analyses.map(renderHistoryItem).join("");

  elements.historyList.querySelectorAll("[data-history-id]").forEach((item) => {
    item.addEventListener("click", (event) => {
      if (event.target.closest("[data-delete-id]")) {
        return;
      }
      loadAnalysis(item.dataset.historyId);
    });
  });

  elements.historyList.querySelectorAll("[data-delete-id]").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.stopPropagation();
      deleteAnalysis(button.dataset.deleteId);
    });
  });
}

function renderHistoryItem(analysis) {
  const extraction = analysis.extraction || {};
  const eligibility = analysis.eligibility || {};
  const title = extraction.title || analysis.filename || "저장된 분석";
  const status = eligibility.status || "needs_review";
  const warningCount = Array.isArray(analysis.warnings) ? analysis.warnings.length : 0;
  const checklistCount = Array.isArray(analysis.checklist) ? analysis.checklist.length : 0;

  const period = extraction.application_period || "기간 확인 필요";
  return `
    <article class="history-item" data-history-id="${escapeAttribute(analysis.id)}" role="button" tabindex="0">
      <div class="history-main">
        <div>
          <strong class="history-title">${escapeHtml(title)}</strong>
          <span class="history-file">${escapeHtml(analysis.filename || "파일명 없음")}</span>
        </div>
        <span class="history-status ${statusClass(status)}">${escapeHtml(statusLabel(status))}</span>
      </div>
      <div class="history-meta">
        <span>${escapeHtml(formatDate(analysis.created_at))}</span>
        <span>${escapeHtml(period)}</span>
        <span>경고 ${warningCount}개</span>
        <span>체크리스트 ${checklistCount}개</span>
      </div>
      <button class="history-delete" type="button" data-delete-id="${escapeAttribute(analysis.id)}">삭제</button>
    </article>
  `;
}

function updateIntakeStatus() {
  const profile = readProfile();
  const filledProfileFields = Object.values(profile).filter((value) => value !== null && value !== "").length;
  elements.profileStatus.textContent = filledProfileFields >= 4 ? "준비됨" : `${filledProfileFields}/6`;
  elements.profileStatus.classList.toggle("ready", filledProfileFields >= 4);

  const hasFile = Boolean(elements.fileInput.files[0]);
  elements.documentStatus.textContent = hasFile ? "파일 선택됨" : "샘플 가능";
  elements.documentStatus.classList.toggle("ready", hasFile);
}

async function loadAnalysis(analysisId) {
  try {
    const response = await fetch(`/api/analyses/${encodeURIComponent(analysisId)}`);
    const analysis = await readApiResponse(response);
    switchTab("analyze");
    renderResult(analysis);
  } catch (error) {
    elements.historyList.innerHTML = `<p class="empty-state error-text">${escapeHtml(error.message)}</p>`;
  }
}

async function deleteAnalysis(analysisId) {
  if (!confirm("이 분석 결과를 삭제할까요?")) {
    return;
  }

  const response = await fetch(`/api/analyses/${encodeURIComponent(analysisId)}`, {
    method: "DELETE",
  });
  if (!response.ok && response.status !== 204) {
    const payload = await response.json().catch(() => ({}));
    elements.historyList.innerHTML = `<p class="empty-state error-text">${escapeHtml(payload.detail || "삭제하지 못했습니다.")}</p>`;
    return;
  }

  if (state.currentAnalysisId === analysisId) {
    state.currentAnalysisId = null;
    renderSaveState();
  }
  loadHistoryList();
}

function statusClass(status) {
  return statusText[status]?.className || "needs-review";
}

function statusLabel(status) {
  return statusText[status]?.label || "추가 확인 필요";
}

function formatDate(isoString) {
  if (!isoString) {
    return "날짜 없음";
  }
  const date = new Date(isoString);
  if (Number.isNaN(date.getTime())) {
    return isoString;
  }
  return date.toLocaleString("ko-KR", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function renderInlineNotes(notes) {
  if (!notes.length) {
    return "";
  }
  return `
    <ul>
      ${notes.map((note) => `<li>${escapeHtml(note)}</li>`).join("")}
    </ul>
  `;
}

function formatValue(value) {
  const text = listText(value);
  if (!text) {
    return `<span class="muted">없음</span>`;
  }
  if (String(text).startsWith("http")) {
    return `<a href="${escapeAttribute(text)}" target="_blank" rel="noreferrer">${escapeHtml(text)}</a>`;
  }
  if (String(text).includes(";")) {
    const items = String(text)
      .split(";")
      .map((item) => item.trim())
      .filter(Boolean);
    return `<ul class="compact-list">${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
  }
  return escapeHtml(text);
}

function listText(value) {
  if (Array.isArray(value)) {
    return value.length ? value.join(", ") : "";
  }
  return value || "";
}

function renderError(message) {
  elements.errorBox.textContent = message;
  elements.errorBox.classList.remove("hidden");
}

function clearError() {
  elements.errorBox.textContent = "";
  elements.errorBox.classList.add("hidden");
}

function setBusy(isBusy, label = "분석 중") {
  elements.analyzeButton.disabled = isBusy;
  elements.sampleButton.disabled = isBusy;
  elements.resetButton.disabled = isBusy;
  elements.sampleSelect.disabled = isBusy;
  elements.analyzeButton.textContent = isBusy ? label : "분석하기";
  elements.sampleButton.textContent = isBusy ? "준비 중" : "샘플 불러오기";
}

function formatBytes(size) {
  if (!Number.isFinite(size) || size <= 0) {
    return "0 KB";
  }
  if (size < 1024 * 1024) {
    return `${Math.ceil(size / 1024)} KB`;
  }
  return `${(size / 1024 / 1024).toFixed(1)} MB`;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function escapeAttribute(value) {
  return escapeHtml(value).replaceAll("`", "&#096;");
}
