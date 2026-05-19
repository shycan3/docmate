from __future__ import annotations

from .models import DocumentExtraction, EligibilityResult, Profile


def evaluate_profile(extraction: DocumentExtraction, profile: Profile) -> EligibilityResult:
    hints = extraction.condition_hints or {}
    reasons: list[str] = []
    missing: list[str] = []

    age_min = hints.get("age_min")
    age_max = hints.get("age_max")
    if age_min is not None or age_max is not None:
        if profile.age is None:
            missing.append("age")
        else:
            if age_min is not None and profile.age < age_min:
                reasons.append(f"최소 연령 {age_min}세 이상 조건을 충족하지 않습니다.")
            if age_max is not None and profile.age > age_max:
                reasons.append(f"최대 연령 {age_max}세 이하 조건을 충족하지 않습니다.")

    regions = hints.get("regions") or []
    if regions:
        if not profile.region:
            missing.append("region")
        elif not any(region in profile.region for region in regions):
            reasons.append(f"거주 지역 조건({', '.join(regions)})을 충족하지 않습니다.")

    income_max_decile = hints.get("income_max_decile")
    if income_max_decile is not None:
        if profile.income_decile is None:
            missing.append("income_decile")
        elif profile.income_decile > income_max_decile:
            reasons.append(
                f"소득분위 {income_max_decile}분위 이하 조건을 충족하지 않습니다."
            )

    if hints.get("requires_enrolled"):
        if profile.enrolled is None:
            missing.append("enrolled")
        elif not profile.enrolled:
            reasons.append("재학 상태 조건을 충족하지 않습니다.")

    occupation_keywords = hints.get("occupation_keywords") or []
    if occupation_keywords:
        if not profile.occupation:
            missing.append("occupation")
        else:
            occupation = profile.occupation.lower()
            if not any(keyword.lower() in occupation for keyword in occupation_keywords):
                reasons.append(
                    f"직업 조건({', '.join(occupation_keywords)})을 충족하지 않습니다."
                )

    if hints.get("requires_manual_review"):
        return EligibilityResult(
            status="needs_review",
            reasons=reasons
            or ["기본계획 문서라 사업별 세부요건과 최신 신청 공고 확인이 필요합니다."],
            missing_information=sorted(set(missing)),
        )

    if reasons:
        return EligibilityResult(status="ineligible", reasons=reasons, missing_information=[])

    if missing:
        missing = sorted(set(missing))
        return EligibilityResult(
            status="needs_review",
            reasons=["프로필 정보가 부족하거나 조건 해석에 추가 확인이 필요합니다."],
            missing_information=missing,
        )

    if not any(
        key in hints for key in ("age_min", "age_max", "regions", "income_max_decile")
    ) and not hints.get("requires_enrolled"):
        return EligibilityResult(
            status="needs_review",
            reasons=["공고 조건을 충분히 구조화하지 못해 수동 확인이 필요합니다."],
            missing_information=[],
        )

    return EligibilityResult(
        status="eligible",
        reasons=["기본 자격 조건을 rule-based 기준으로 충족합니다."],
        missing_information=[],
    )
