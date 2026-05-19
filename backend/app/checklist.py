from __future__ import annotations

from .models import ChecklistItem, DocumentExtraction

_DOCUMENT_LINKS = {
    "주민등록": "https://www.gov.kr/portal/main",
    "재학증명서": "https://www.gov.kr/portal/main",
    "소득": "https://www.gov.kr/portal/main",
}


def build_checklist(extraction: DocumentExtraction) -> list[ChecklistItem]:
    items: list[ChecklistItem] = []

    for document in extraction.required_documents:
        action_url = _resolve_document_link(document) or extraction.application_url
        items.append(
            ChecklistItem(
                title=f"{document} 준비",
                description=f"발급 또는 업로드 가능한 상태로 준비합니다: {document}",
                action_url=action_url,
            )
        )

    if extraction.application_method:
        items.append(
            ChecklistItem(
                title="신청 방법 확인",
                description=extraction.application_method,
                action_url=extraction.application_url,
            )
        )

    if extraction.application_period:
        items.append(
            ChecklistItem(
                title="마감일 확인",
                description=f"신청 기간을 다시 확인하고 마감 전에 제출합니다: {extraction.application_period}",
                action_url=extraction.application_url,
            )
        )

    return items


def _resolve_document_link(document: str) -> str:
    for keyword, url in _DOCUMENT_LINKS.items():
        if keyword in document:
            return url
    return ""
