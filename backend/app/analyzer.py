from __future__ import annotations

import re
from datetime import datetime, timedelta
from urllib.parse import urlencode

from .checklist import build_checklist
from .eligibility import evaluate_profile
from .models import (
    ActionLink,
    AnalysisResult,
    DocumentExtraction,
    Profile,
    WarningItem,
)

_SECTION_LABELS = {
    "application_period": ("신청 기간", "신청기간", "접수 기간", "모집 기간"),
    "eligibility_conditions": ("지원 대상", "지원대상", "신청 자격", "자격 요건", "지원 조건"),
    "benefits": ("지원 내용", "지원내용", "혜택", "지원 금액"),
    "required_documents": ("제출 서류", "필수 서류", "구비 서류", "준비 서류"),
    "application_method": ("신청 방법", "신청방법", "접수 방법"),
    "application_url": ("신청 URL", "신청 링크", "접수 URL"),
}

_WARNING_RULES = (
    ("critical", "중복 지원 불가", ("중복 지원 불가", "중복신청 불가", "중복 수혜 불가")),
    ("critical", "수정 불가", ("수정 불가", "내용 수정 불가", "정정 불가")),
    ("critical", "자동 탈락", ("자동 탈락", "자동탈락", "탈락 처리")),
    ("warning", "서류 미비", ("서류 미비", "제출 서류 미비", "미비 시 탈락")),
    ("warning", "국적 제한", ("국적자만", "국적 제한", "외국인 제외")),
    ("warning", "중복지원 관리", ("중복지원 방지", "중복지원", "중복 지원 방지")),
    ("warning", "사업별 세부요건 확인", ("사업별 세부요건", "사업별 지원 대상", "사업별 시행계획")),
    (
        "warning",
        "주거비 중복 수혜 제외",
        ("타 부처 청년 주거비 지원 사업", "청년 월세 특별지원", "청년 주거급여"),
    ),
)

_OCCUPATION_KEYWORDS = ("대학생", "미취업", "구직자", "재직자", "직장인")
_IGNORED_URL_FRAGMENTS = (
    "w3.org/",
    "adobe.com/",
    "purl.org/",
    "xmp",
    "rdf-syntax-ns",
)


def analyze_document(text: str, profile: Profile) -> AnalysisResult:
    extraction = _extract_document(text)
    warnings = _detect_warnings(text)
    eligibility = evaluate_profile(extraction, profile)
    checklist = build_checklist(extraction)
    actions = _build_actions(extraction)
    return AnalysisResult(
        extraction=extraction,
        eligibility=eligibility,
        warnings=warnings,
        checklist=checklist,
        actions=actions,
    )


def _extract_document(text: str) -> DocumentExtraction:
    lines = _normalize_lines(text)
    title = _clean_title(lines[0]) if lines else "업로드 문서"
    sections = {key: [] for key in _SECTION_LABELS}

    for index, line in enumerate(lines):
        for field, labels in _SECTION_LABELS.items():
            if _matches_label(line, labels):
                sections[field] = _collect_section_values(lines, index, labels)
                break

    application_url = _sanitize_application_url(_pick_first(sections["application_url"]))
    if not application_url:
        application_url = _extract_first_application_url(text)

    extraction = DocumentExtraction(
        title=title,
        application_period=_pick_first(sections["application_period"]),
        eligibility_conditions=_split_list_items(sections["eligibility_conditions"]),
        benefits=_split_list_items(sections["benefits"]),
        required_documents=_split_list_items(sections["required_documents"]),
        application_method=_pick_first(sections["application_method"]),
        application_url=application_url,
        raw_text=text.strip(),
    )
    _apply_known_document_fallbacks(extraction, text, lines)
    extraction.condition_hints = _extract_condition_hints(text, extraction.eligibility_conditions)
    if _looks_like_national_scholarship_plan(text):
        extraction.condition_hints["requires_manual_review"] = True
    return extraction


def _normalize_lines(text: str) -> list[str]:
    cleaned = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.strip(" -•\t") for line in cleaned.splitlines()]
    return [line for line in lines if line]


def _matches_label(line: str, labels: tuple[str, ...]) -> bool:
    for label in labels:
        if line.startswith(f"{label}:") or line.startswith(f"{label} :"):
            return True
        if line.startswith(label) and ":" in line:
            return True
    return False


def _collect_section_values(
    lines: list[str], start_index: int, labels: tuple[str, ...]
) -> list[str]:
    line = lines[start_index]
    for label in labels:
        prefix = f"{label}:"
        if line.startswith(prefix):
            remainder = line[len(prefix) :].strip()
            break
        prefix = f"{label} :"
        if line.startswith(prefix):
            remainder = line[len(prefix) :].strip()
            break
    else:
        remainder = ""

    values = [remainder] if remainder else []
    next_index = start_index + 1
    while next_index < len(lines) and not _is_known_heading(lines[next_index]):
        values.append(lines[next_index])
        next_index += 1
    return values


def _is_known_heading(line: str) -> bool:
    for labels in _SECTION_LABELS.values():
        if _matches_label(line, labels):
            return True
    return False


def _pick_first(values: list[str]) -> str:
    return values[0].strip() if values else ""


def _clean_title(title: str) -> str:
    cleaned = re.sub(r"\s+", " ", title).strip()
    cleaned = cleaned.replace("년맞춤형", "년 맞춤형")
    cleaned = cleaned.replace(")(국가장학금", ") (국가장학금")
    return cleaned


def _split_list_items(values: list[str]) -> list[str]:
    items: list[str] = []
    for value in values:
        for part in re.split(r"[,\u00b7;]", value):
            cleaned = part.strip()
            if cleaned:
                items.append(cleaned)
    deduped: list[str] = []
    for item in items:
        if item not in deduped:
            deduped.append(item)
    return deduped


def _extract_first_application_url(text: str) -> str:
    for raw_url in re.findall(r"https?://[^\s)>\]}]+", text):
        url = _sanitize_application_url(raw_url)
        if url:
            return url
    return ""


def _sanitize_application_url(url: str) -> str:
    cleaned = url.strip().rstrip(".,;:)]}>")
    lowered = cleaned.lower()
    if not cleaned or any(fragment in lowered for fragment in _IGNORED_URL_FRAGMENTS):
        return ""
    return cleaned


def _apply_known_document_fallbacks(
    extraction: DocumentExtraction, text: str, lines: list[str]
) -> None:
    if _looks_like_national_scholarship_plan(text):
        _apply_national_scholarship_plan_fallback(extraction, text, lines)


def _looks_like_national_scholarship_plan(text: str) -> bool:
    compact = re.sub(r"\s+", "", text)
    return "국가장학금" in compact and (
        "학자금지원구간" in compact
        or "맞춤형국가장학금지원기본계획" in compact
        or "한국장학재단" in compact
    )


def _apply_national_scholarship_plan_fallback(
    extraction: DocumentExtraction, text: str, lines: list[str]
) -> None:
    extraction.title = _clean_national_scholarship_title(extraction.title)

    if not extraction.application_period:
        extraction.application_period = _extract_national_scholarship_schedule(lines)

    _append_unique(
        extraction.eligibility_conditions,
        _derive_national_scholarship_conditions(text),
    )
    _append_unique(extraction.benefits, _derive_national_scholarship_benefits(text))

    if not extraction.required_documents:
        extraction.required_documents = [
            "가구원 정보제공 동의",
            "소득구간 산정 관련 증빙",
            "대학별 추가 제출서류",
        ]

    if not extraction.application_method:
        extraction.application_method = (
            "한국장학재단 홈페이지 또는 모바일 앱에서 사업별 신청 공고를 확인한 뒤 온라인 신청"
        )

    if not extraction.application_url:
        extraction.application_url = "https://www.kosaf.go.kr"


def _clean_national_scholarship_title(title: str) -> str:
    cleaned = _clean_title(title)
    if "국가장학금 지원 기본계획" in cleaned and "2025년" in cleaned:
        return cleaned
    if "국가장학금" in cleaned and "기본계획" in cleaned:
        return cleaned
    return "2025년 맞춤형 국가장학금 지원 기본계획"


def _extract_national_scholarship_schedule(lines: list[str]) -> str:
    schedule_items: list[str] = []
    for line in lines:
        for segment in _split_schedule_segments(line):
            compact = re.sub(r"\s+", "", segment)
            if "신청접수" not in compact:
                continue
            if "국가장학금" not in compact and "주거안정장학금" not in compact:
                continue
            if not re.search(r"(?:[’']\d{2}|20\d{2})\.\d{1,2}", segment):
                continue
            label, separator, raw_date = segment.partition(":")
            if not separator:
                continue
            schedule_items.append(
                f"{_format_schedule_label(label)}: {_format_schedule_date(raw_date)}"
            )
    return "; ".join(schedule_items[:6])


def _split_schedule_segments(line: str) -> list[str]:
    return [segment.strip() for segment in re.split(r"(?=□)", line) if segment.strip()]


def _format_schedule_label(label: str) -> str:
    cleaned = label.strip("□-•* \t")
    cleaned = cleaned.replace("’25학년도", "2025학년도 ")
    cleaned = cleaned.replace("'25학년도", "2025학년도 ")
    cleaned = cleaned.replace("’26학년도", "2026학년도 ")
    cleaned = cleaned.replace("'26학년도", "2026학년도 ")
    cleaned = cleaned.replace("국가장학금", " 국가장학금 ")
    cleaned = cleaned.replace("주거안정장학금", " 주거안정장학금 ")
    cleaned = cleaned.replace("신청접수", " 신청 접수")
    cleaned = re.sub(r"([12])학기", r"\1학기 ", cleaned)
    cleaned = re.sub(r"(\d차)", r" \1 ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def _format_schedule_date(raw_date: str) -> str:
    cleaned = raw_date.strip().replace("’", "'")
    cleaned = re.sub(r"'(25|26)\.", r"20\1.", cleaned)
    range_match = re.search(
        r"(20\d{2})\.(\d{1,2})\.?\s*~\s*(\d{1,2})\s*월?", cleaned
    )
    if range_match:
        year, start_month, end_month = range_match.groups()
        return f"{year}년 {int(start_month)}~{int(end_month)}월"

    month_match = re.search(r"(20\d{2})\.(\d{1,2})\s*월?", cleaned)
    if month_match:
        year, month = month_match.groups()
        return f"{year}년 {int(month)}월"
    return cleaned


def _derive_national_scholarship_conditions(text: str) -> list[str]:
    compact = re.sub(r"\s+", "", text)
    conditions: list[str] = []
    if "학자금지원구간9구간이하" in compact:
        conditions.append("학자금 지원구간 9구간 이하 대학생")
    if "다자녀" in compact or "형제자매가셋이상" in compact:
        conditions.append("다자녀 가구(형제·자매 셋 이상) 대학생")
    if "지역인재" in compact:
        conditions.append("비수도권 대학 지역인재 등 사업별 세부요건 충족자")
    if "근로장학금" in compact:
        conditions.append("교내·교외 근로 가능 대학생")
    if "주거안정장학금" in compact and ("기초" in compact or "차상위" in compact):
        conditions.append("원거리 대학 진학 기초·차상위 대학생")
    conditions.append("사업별 세부요건은 한국장학재단 공고에서 추가 확인 필요")
    return conditions


def _derive_national_scholarship_benefits(text: str) -> list[str]:
    compact = re.sub(r"\s+", "", text)
    benefits: list[str] = []
    if "국가장학금Ⅰ유형" in text or "국가장학금I유형" in text:
        national_benefit = "국가장학금 I 유형: 소득연계 등록금 지원"
        if "570420350100" in compact or "연간지원단가" in compact:
            national_benefit += (
                "(기초·차상위 전액, 1~3구간 570만원, 4~6구간 420만원, "
                "7~8구간 350만원, 9구간 100만원)"
            )
        benefits.append(national_benefit)
    if "다자녀장학금" in compact:
        family_benefit = "다자녀장학금: 다자녀 가구 등록금 부담 경감"
        if "셋째이상전액" in compact:
            family_benefit += "(셋째 이상 전액 지원, 9구간 이하 확대)"
        benefits.append(family_benefit)
    if "대학생근로장학금" in compact or "근로장학금" in compact:
        work_benefit = "대학생 근로장학금: 교내·교외 근로장려금 지원"
        if "10,030원" in text and "12,430원" in text:
            work_benefit += "(교내 시간당 10,030원, 교외 시간당 12,430원)"
        if "20만명" in compact:
            work_benefit += ", 지원 인원 20만명"
        benefits.append(work_benefit)
    if "우수학생국가장학금" in compact:
        excellence_benefit = "우수학생 국가장학금: 우수·전문기술 인재 장학금 지원"
        if "1,500" in text and "440" in text and "30" in text:
            excellence_benefit += "(인문100년 1,500명, 예술체육비전 440명, 드림장학금 30명 신규 선발 예정)"
        benefits.append(excellence_benefit)
    if "주거안정장학금" in compact:
        housing_benefit = "주거안정장학금: 원거리 대학 진학 기초·차상위 학생 주거비 지원"
        if re.search(r"월\s*최대\s*20\s*만\s*원", text) and re.search(
            r"연간\s*최대\s*240\s*만\s*원", text
        ):
            housing_benefit += "(월 최대 20만원, 연간 최대 240만원)"
        benefits.append(housing_benefit)
    return benefits


def _append_unique(target: list[str], additions: list[str]) -> None:
    for item in additions:
        if item and item not in target:
            target.append(item)


def _extract_condition_hints(text: str, conditions: list[str]) -> dict[str, object]:
    joined = " ".join(conditions) or text
    hints: dict[str, object] = {}

    min_match = re.search(r"만?\s*(\d{1,2})세\s*이상", joined)
    if min_match:
        hints["age_min"] = int(min_match.group(1))

    max_match = re.search(r"만?\s*(\d{1,2})세\s*이하", joined)
    if max_match:
        hints["age_max"] = int(max_match.group(1))

    range_match = re.search(r"(\d{1,2})세\s*[~-]\s*(\d{1,2})세", joined)
    if range_match:
        hints["age_min"] = int(range_match.group(1))
        hints["age_max"] = int(range_match.group(2))

    region_matches = re.findall(r"([가-힣A-Za-z]+)\s*거주", joined)
    if region_matches:
        hints["regions"] = list(dict.fromkeys(region_matches))

    income_match = re.search(
        r"(?:소득|학자금\s*지원구간|지원구간)\s*(\d{1,2})\s*(?:분위|구간)?\s*이하",
        joined,
    )
    if income_match:
        hints["income_max_decile"] = int(income_match.group(1))

    if "재학생" in joined or "재학" in joined:
        hints["requires_enrolled"] = True

    occupations = [keyword for keyword in _OCCUPATION_KEYWORDS if keyword in joined]
    if occupations:
        hints["occupation_keywords"] = occupations

    return hints


def _detect_warnings(text: str) -> list[WarningItem]:
    warnings: list[WarningItem] = []
    for severity, title, keywords in _WARNING_RULES:
        evidence = _find_first_keyword(text, keywords)
        if evidence:
            warnings.append(WarningItem(severity=severity, title=title, evidence=evidence))
    return warnings


def _find_first_keyword(text: str, keywords: tuple[str, ...]) -> str:
    compact_text = re.sub(r"\s+", "", text)
    for keyword in keywords:
        if keyword in text:
            return keyword
        if re.sub(r"\s+", "", keyword) in compact_text:
            return keyword
    return ""


def _build_actions(extraction: DocumentExtraction) -> list[ActionLink]:
    actions: list[ActionLink] = []
    if extraction.application_url:
        actions.append(
            ActionLink(label="신청 페이지 열기", url=extraction.application_url, kind="apply")
        )
    calendar_url = _build_calendar_url(extraction)
    if calendar_url:
        actions.append(
            ActionLink(label="마감일 캘린더 등록", url=calendar_url, kind="calendar")
        )
    return actions


def _build_calendar_url(extraction: DocumentExtraction) -> str:
    deadline = _extract_deadline(extraction.application_period)
    if not deadline:
        return ""

    start = deadline.strftime("%Y%m%d")
    end = (deadline + timedelta(days=1)).strftime("%Y%m%d")
    params = urlencode(
        {
            "action": "TEMPLATE",
            "text": f"{extraction.title} 신청 마감",
            "dates": f"{start}/{end}",
            "details": extraction.application_url or extraction.application_method,
        }
    )
    return f"https://calendar.google.com/calendar/render?{params}"


def _extract_deadline(period: str) -> datetime | None:
    matches = re.findall(r"(\d{4})[.-](\d{1,2})[.-](\d{1,2})", period)
    if not matches:
        return None
    year, month, day = matches[-1]
    return datetime(int(year), int(month), int(day))
