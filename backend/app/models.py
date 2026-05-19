from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def _parse_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    text = str(value).strip()
    digits = "".join(char for char in text if char.isdigit())
    if not digits:
        return None
    return int(digits)


def _parse_bool(value: Any) -> bool | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "on", "재학", "enrolled"}:
        return True
    if text in {"0", "false", "no", "n", "off", "비재학", "not-enrolled"}:
        return False
    return None


@dataclass(slots=True)
class Profile:
    age: int | None = None
    grade: str | None = None
    region: str | None = None
    occupation: str | None = None
    income_decile: int | None = None
    enrolled: bool | None = None

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> "Profile":
        payload = payload or {}
        return cls(
            age=_parse_int(payload.get("age")),
            grade=_clean_optional_text(payload.get("grade")),
            region=_clean_optional_text(payload.get("region")),
            occupation=_clean_optional_text(payload.get("occupation")),
            income_decile=_parse_int(payload.get("income_decile")),
            enrolled=_parse_bool(payload.get("enrolled")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "age": self.age,
            "grade": self.grade,
            "region": self.region,
            "occupation": self.occupation,
            "income_decile": self.income_decile,
            "enrolled": self.enrolled,
        }


def _clean_optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


@dataclass(slots=True)
class DocumentExtraction:
    title: str = ""
    application_period: str = ""
    eligibility_conditions: list[str] = field(default_factory=list)
    benefits: list[str] = field(default_factory=list)
    required_documents: list[str] = field(default_factory=list)
    application_method: str = ""
    application_url: str = ""
    raw_text: str = field(default="", repr=False)
    condition_hints: dict[str, Any] = field(default_factory=dict, repr=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "application_period": self.application_period,
            "eligibility_conditions": list(self.eligibility_conditions),
            "benefits": list(self.benefits),
            "required_documents": list(self.required_documents),
            "application_method": self.application_method,
            "application_url": self.application_url,
        }


@dataclass(slots=True)
class EligibilityResult:
    status: str
    reasons: list[str] = field(default_factory=list)
    missing_information: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "reasons": list(self.reasons),
            "missing_information": list(self.missing_information),
        }


@dataclass(slots=True)
class WarningItem:
    severity: str
    title: str
    evidence: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "severity": self.severity,
            "title": self.title,
            "evidence": self.evidence,
        }


@dataclass(slots=True)
class ChecklistItem:
    title: str
    description: str
    action_url: str = ""
    done: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "description": self.description,
            "action_url": self.action_url,
            "done": self.done,
        }


@dataclass(slots=True)
class ActionLink:
    label: str
    url: str
    kind: str = "external"

    def to_dict(self) -> dict[str, Any]:
        return {"label": self.label, "url": self.url, "kind": self.kind}


@dataclass(slots=True)
class AnalysisResult:
    extraction: DocumentExtraction
    eligibility: EligibilityResult
    warnings: list[WarningItem] = field(default_factory=list)
    checklist: list[ChecklistItem] = field(default_factory=list)
    actions: list[ActionLink] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "extraction": self.extraction.to_dict(),
            "eligibility": self.eligibility.to_dict(),
            "warnings": [item.to_dict() for item in self.warnings],
            "checklist": [item.to_dict() for item in self.checklist],
            "actions": [item.to_dict() for item in self.actions],
        }
