from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .models import Profile


@dataclass(frozen=True, slots=True)
class SampleAnnouncement:
    id: str
    label: str
    description: str
    filename: str
    text: str
    profile_factory: Callable[[], Profile]

    def profile(self) -> Profile:
        return self.profile_factory()

    def to_metadata(self) -> dict[str, object]:
        return {
            "id": self.id,
            "label": self.label,
            "description": self.description,
            "filename": self.filename,
            "profile": self.profile().to_dict(),
        }


SAMPLE_1_ID = "seoul-hope-scholarship"
SAMPLE_1_FILENAME = "sample-1-seoul-hope-scholarship.txt"
SAMPLE_1_DOCUMENT_TEXT = """2026 서울 청년 희망장학금 공고
신청 기간: 2026-05-01 ~ 2026-05-31
지원 대상: 만 19세 이상 24세 이하, 서울 거주, 국내 대학 재학생, 소득 6분위 이하
지원 내용: 학업장려금 150만원 1회 지급, 진로 멘토링 제공
제출 서류: 주민등록초본, 재학증명서, 소득분위 확인서
신청 방법: 공식 홈페이지 온라인 신청
신청 URL: https://scholar.example/apply
유의 사항: 중복 지원 불가. 제출 서류 미비 시 자동 탈락. 신청 후 내용 수정 불가. 대한민국 국적자만 신청 가능.
"""


def get_sample_1_profile() -> Profile:
    return Profile(
        age=22,
        grade="3학년",
        region="서울",
        occupation="대학생",
        income_decile=5,
        enrolled=True,
    )


SAMPLE_2_ID = "graduate-talent-scholarship"
SAMPLE_2_FILENAME = "sample-2-graduate-talent-scholarship.txt"
SAMPLE_2_DOCUMENT_TEXT = """2026 국립대학교 대학원 우수 인재 장학금
신청 기간: 2026-06-01 ~ 2026-06-15
지원 대상: 만 24세 이상 34세 이하, 서울 거주, 석사 또는 박사과정 재학생
지원 내용: 연구장려금 월 300만원 12개월 지급, 국제 학술대회 참가비 1회 지원
제출 서류: 학사 학위증명서, 대학원 재학증명서, 성적증명서, 연구계획서, 추천서 2부
신청 방법: 대학원 장학 포털에서 온라인 신청 후 원본 서류 우편 제출
신청 URL: https://graduate.example/apply
유의 사항: 허위 서류 제출 시 자동 탈락. 제출 후 내용 수정 불가. 타 연구장학금 중복 수혜 불가.
"""


def get_sample_2_profile() -> Profile:
    return Profile(
        age=26,
        grade="석사과정",
        region="서울",
        occupation="대학원생",
        income_decile=7,
        enrolled=True,
    )


SAMPLE_3_ID = "busan-youth-living-fund"
SAMPLE_3_FILENAME = "sample-3-busan-youth-living-fund.txt"
SAMPLE_3_DOCUMENT_TEXT = """2026 부산 저소득 청년 생활지원금 공고
신청 기간: 2026-06-01 ~ 2026-06-30
지원 대상: 만 18세 이상 35세 이하, 부산 거주, 구직자 또는 미취업 청년, 소득 2분위 이하
지원 내용: 생활지원금 월 50만원 12개월 지급, 의료비 긴급 지원 1회 100만원
제출 서류: 주민등록초본, 건강보험료 납부확인서, 소득 증명서, 구직활동 확인서
신청 방법: 부산 청년정책 포털 온라인 신청
신청 URL: https://youth-busan.example/fund
유의 사항: 다른 정부 생활지원금 중복 지원 불가. 제출 서류 미비 시 탈락 처리. 지원금 사용 목적 외 사용 시 환수.
"""


def get_sample_3_profile() -> Profile:
    return Profile(
        age=28,
        grade="졸업",
        region="부산",
        occupation="구직자",
        income_decile=1,
        enrolled=False,
    )


SAMPLES = (
    SampleAnnouncement(
        id=SAMPLE_1_ID,
        label="서울 청년 희망장학금",
        description="나이, 지역, 재학, 소득 조건이 모두 있는 기본 장학금 사례",
        filename=SAMPLE_1_FILENAME,
        text=SAMPLE_1_DOCUMENT_TEXT,
        profile_factory=get_sample_1_profile,
    ),
    SampleAnnouncement(
        id=SAMPLE_2_ID,
        label="대학원 우수 인재 장학금",
        description="대학원 재학과 원본 서류 제출이 포함된 고학력 지원 사례",
        filename=SAMPLE_2_FILENAME,
        text=SAMPLE_2_DOCUMENT_TEXT,
        profile_factory=get_sample_2_profile,
    ),
    SampleAnnouncement(
        id=SAMPLE_3_ID,
        label="부산 저소득 청년 생활지원금",
        description="구직자, 지역, 소득 조건이 엄격한 청년정책 사례",
        filename=SAMPLE_3_FILENAME,
        text=SAMPLE_3_DOCUMENT_TEXT,
        profile_factory=get_sample_3_profile,
    ),
)


SAMPLE_FILENAME = SAMPLE_1_FILENAME
SAMPLE_DOCUMENT_TEXT = SAMPLE_1_DOCUMENT_TEXT


def get_sample(sample_id: str | None = None) -> SampleAnnouncement:
    target_id = (sample_id or SAMPLE_1_ID).strip()
    for sample in SAMPLES:
        if sample.id == target_id:
            return sample
    raise KeyError(target_id)


def list_samples() -> list[dict[str, object]]:
    return [sample.to_metadata() for sample in SAMPLES]


def get_sample_profile(sample_id: str | None = None) -> Profile:
    return get_sample(sample_id).profile()
