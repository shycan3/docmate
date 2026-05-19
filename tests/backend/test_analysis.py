from __future__ import annotations

import unittest

from backend.app.analyzer import analyze_document
from backend.app.models import Profile
from backend.app.parser import PDF_FALLBACK_MESSAGE, extract_text_from_upload
from backend.app.sample_data import SAMPLE_DOCUMENT_TEXT, get_sample_profile


class ParserTests(unittest.TestCase):
    def test_extract_text_from_plain_upload(self) -> None:
        text = extract_text_from_upload("notice.txt", "신청 기간: 2026-05-01".encode("utf-8"))
        self.assertIn("신청 기간", text)

    def test_extract_text_from_binary_pdf_falls_back_safely(self) -> None:
        content = b"%PDF-1.4\x00\x01\x02binary"
        text = extract_text_from_upload("notice.pdf", content)
        self.assertEqual(text, PDF_FALLBACK_MESSAGE)


class AnalysisTests(unittest.TestCase):
    def test_sample_analysis_is_eligible_and_structured(self) -> None:
        result = analyze_document(SAMPLE_DOCUMENT_TEXT, get_sample_profile())

        self.assertEqual(result.eligibility.status, "eligible")
        self.assertEqual(result.extraction.title, "2026 서울 청년 희망장학금 공고")
        self.assertIn("주민등록초본", result.extraction.required_documents)
        self.assertGreaterEqual(len(result.warnings), 4)
        self.assertTrue(any(action.kind == "apply" for action in result.actions))
        self.assertTrue(any(action.kind == "calendar" for action in result.actions))

    def test_rule_based_ineligibility_for_age_and_region(self) -> None:
        profile = Profile(
            age=27,
            grade="졸업",
            region="부산",
            occupation="대학생",
            income_decile=5,
            enrolled=True,
        )
        result = analyze_document(SAMPLE_DOCUMENT_TEXT, profile)

        self.assertEqual(result.eligibility.status, "ineligible")
        joined_reasons = " ".join(result.eligibility.reasons)
        self.assertIn("연령", joined_reasons)
        self.assertIn("거주 지역", joined_reasons)

    def test_missing_profile_information_returns_needs_review(self) -> None:
        profile = Profile(age=22, region=None, occupation="대학생", enrolled=None)
        result = analyze_document(SAMPLE_DOCUMENT_TEXT, profile)

        self.assertEqual(result.eligibility.status, "needs_review")
        self.assertIn("region", result.eligibility.missing_information)
        self.assertIn("enrolled", result.eligibility.missing_information)

    def test_national_scholarship_plan_is_structured(self) -> None:
        plan_text = """2025년맞춤형 국가장학금 지원 기본계획(안)
< 2025년 맞춤형 국가장학금 지원 주요 내용 >
국가장학금Ⅰ유형 저소득·중산층 부담 경감 학자금 지원구간 9구간 이하 대학생
다자녀장학금 다자녀 가구 형제 자매가 셋 이상인 대학생 등록금 지원
대학생 근로장학금 교내·교외 근로장학금 지원
주거안정장학금 원거리 대학 진학 기초·차상위 대학생 월 최대20만원, 연간 최대240만원
Ⅳ. 향후 일정
□’25학년도1학기국가장학금2차신청접수:’25.2.~3.
□’25학년도2학기국가장학금1차신청접수:’25.5~6월
"""
        result = analyze_document(plan_text, get_sample_profile())

        self.assertEqual(result.eligibility.status, "needs_review")
        self.assertEqual(result.extraction.application_url, "https://www.kosaf.go.kr")
        self.assertIn("2025년 맞춤형", result.extraction.title)
        self.assertIn("2025년 2~3월", result.extraction.application_period)
        self.assertIn(
            "학자금 지원구간 9구간 이하 대학생",
            result.extraction.eligibility_conditions,
        )
        self.assertTrue(any("주거안정장학금" in item for item in result.extraction.benefits))
        self.assertTrue(result.checklist)


if __name__ == "__main__":
    unittest.main()
