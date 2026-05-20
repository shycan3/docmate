from __future__ import annotations

from dataclasses import dataclass
from math import cos, pi, sin
from pathlib import Path
from typing import Callable, Iterable

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "presentation-materials" / "visuals"
WIDTH, HEIGHT = 1600, 900


COLORS = {
    "bg": "#F7F9FC",
    "ink": "#172033",
    "muted": "#5B667A",
    "soft": "#E7ECF3",
    "card": "#FFFFFF",
    "blue": "#2563EB",
    "blue_soft": "#EAF1FF",
    "green": "#079669",
    "green_soft": "#E7F7F1",
    "amber": "#B7791F",
    "amber_soft": "#FFF4DE",
    "red": "#D64545",
    "red_soft": "#FFE9E9",
    "purple": "#6D5DD3",
    "purple_soft": "#EFEDFF",
    "teal": "#0E7490",
    "teal_soft": "#E4F6FA",
}


@dataclass(frozen=True)
class FontSet:
    title: ImageFont.FreeTypeFont
    h1: ImageFont.FreeTypeFont
    h2: ImageFont.FreeTypeFont
    body: ImageFont.FreeTypeFont
    small: ImageFont.FreeTypeFont
    tiny: ImageFont.FreeTypeFont
    label: ImageFont.FreeTypeFont


def _font_path(bold: bool = False) -> str | None:
    candidates = [
        Path("C:/Windows/Fonts/malgunbd.ttf" if bold else "C:/Windows/Fonts/malgun.ttf"),
        Path("C:/Windows/Fonts/NanumGothicBold.ttf" if bold else "C:/Windows/Fonts/NanumGothic.ttf"),
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return None


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = _font_path(bold)
    if path:
        return ImageFont.truetype(path, size=size)
    return ImageFont.load_default(size=size)


FONTS = FontSet(
    title=_font(64, True),
    h1=_font(48, True),
    h2=_font(32, True),
    body=_font(25),
    small=_font(21),
    tiny=_font(17),
    label=_font(22, True),
)


def text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> tuple[int, int]:
    if not text:
        return 0, 0
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.ImageFont,
    max_width: int,
) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        if not paragraph:
            lines.append("")
            continue

        current = ""
        tokens = paragraph.split(" ")
        for token in tokens:
            candidate = token if not current else f"{current} {token}"
            if text_size(draw, candidate, font)[0] <= max_width:
                current = candidate
                continue

            if current:
                lines.append(current)
            current = ""

            if text_size(draw, token, font)[0] <= max_width:
                current = token
                continue

            piece = ""
            for ch in token:
                candidate_piece = f"{piece}{ch}"
                if text_size(draw, candidate_piece, font)[0] <= max_width:
                    piece = candidate_piece
                else:
                    if piece:
                        lines.append(piece)
                    piece = ch
            current = piece

        if current:
            lines.append(current)
    return lines


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    text: str,
    xy: tuple[int, int],
    font: ImageFont.ImageFont,
    fill: str,
    max_width: int,
    line_gap: int = 9,
) -> int:
    x, y = xy
    for line in wrap_text(draw, text, font, max_width):
        draw.text((x, y), line, font=font, fill=fill)
        y += text_size(draw, line or " ", font)[1] + line_gap
    return y


def rounded_box(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    fill: str = COLORS["card"],
    outline: str = COLORS["soft"],
    width: int = 2,
    radius: int = 22,
) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def pill(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fill: str,
    color: str,
    font: ImageFont.ImageFont = FONTS.tiny,
    pad_x: int = 15,
    pad_y: int = 8,
) -> tuple[int, int, int, int]:
    x, y = xy
    tw, th = text_size(draw, text, font)
    box = (x, y, x + tw + pad_x * 2, y + th + pad_y * 2)
    draw.rounded_rectangle(box, radius=(box[3] - box[1]) // 2, fill=fill)
    draw.text((x + pad_x, y + pad_y - 1), text, font=font, fill=color)
    return box


def arrow(
    draw: ImageDraw.ImageDraw,
    start: tuple[int, int],
    end: tuple[int, int],
    color: str = COLORS["blue"],
    width: int = 5,
) -> None:
    x1, y1 = start
    x2, y2 = end
    draw.line((x1, y1, x2, y2), fill=color, width=width)
    angle = 0 if x2 >= x1 else pi
    size = 16
    points = [
        (x2, y2),
        (x2 - size * cos(angle - pi / 7), y2 - size * sin(angle - pi / 7)),
        (x2 - size * cos(angle + pi / 7), y2 - size * sin(angle + pi / 7)),
    ]
    draw.polygon(points, fill=color)


def base(title: str, subtitle: str, tag: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (WIDTH, HEIGHT), COLORS["bg"])
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, WIDTH, 12), fill=COLORS["blue"])
    pill(draw, (90, 48), tag, COLORS["blue_soft"], COLORS["blue"], FONTS.tiny)
    draw.text((90, 90), title, font=FONTS.title, fill=COLORS["ink"])
    draw_wrapped(draw, subtitle, (92, 166), FONTS.body, COLORS["muted"], 1160, line_gap=7)
    return img, draw


def card_title(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    eyebrow: str,
    title: str,
    body: str,
    accent: str,
    soft: str,
) -> None:
    x1, y1, x2, _ = box
    rounded_box(draw, box)
    pill(draw, (x1 + 28, y1 + 26), eyebrow, soft, accent, FONTS.tiny)
    draw_wrapped(draw, title, (x1 + 28, y1 + 78), FONTS.h2, COLORS["ink"], x2 - x1 - 56, line_gap=8)
    draw_wrapped(draw, body, (x1 + 28, y1 + 142), FONTS.small, COLORS["muted"], x2 - x1 - 56, line_gap=8)


def draw_doc_icon(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], color: str) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle((x1, y1, x2, y2), radius=18, fill="#FFFFFF", outline=color, width=5)
    fold = 38
    draw.polygon([(x2 - fold, y1), (x2, y1 + fold), (x2 - fold, y1 + fold)], fill="#DCE8FF", outline=color)
    for i in range(4):
        y = y1 + 64 + i * 34
        draw.rounded_rectangle((x1 + 34, y, x2 - 34, y + 10), radius=5, fill="#CBD5E1")


def draw_checklist_icon(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], color: str) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle((x1, y1, x2, y2), radius=20, fill="#FFFFFF", outline=color, width=5)
    for i in range(3):
        cy = y1 + 54 + i * 48
        draw.ellipse((x1 + 28, cy - 10, x1 + 48, cy + 10), outline=color, width=4)
        draw.line((x1 + 32, cy, x1 + 38, cy + 7, x1 + 50, cy - 11), fill=color, width=4)
        draw.rounded_rectangle((x1 + 70, cy - 7, x2 - 28, cy + 7), radius=7, fill="#D9E2EC")


def draw_slide_01() -> None:
    img, draw = base(
        "DocMate 한 장 소개",
        "긴 장학금·청년정책 공고를 신청 가능성, 위험 조건, 원문 근거, 체크리스트로 바꾸는 로컬 분석 콘솔입니다.",
        "서비스 포지셔닝",
    )
    stages = [
        ("공고 문서", "PDF/TXT 또는 샘플 공고", COLORS["blue"], COLORS["blue_soft"]),
        ("조건 구조화", "기간, 대상, 서류, 제한 조건 추출", COLORS["teal"], COLORS["teal_soft"]),
        ("프로필 판정", "나이·거주지·직업·소득구간 비교", COLORS["green"], COLORS["green_soft"]),
        ("신청 준비", "근거 확인 후 할 일 목록으로 전환", COLORS["amber"], COLORS["amber_soft"]),
    ]
    top = 300
    box_w, box_h, gap = 305, 255, 42
    for idx, (title, body, accent, soft) in enumerate(stages):
        x = 90 + idx * (box_w + gap)
        rounded_box(draw, (x, top, x + box_w, top + box_h), fill="#FFFFFF", outline=soft, width=4)
        if idx == 0:
            draw_doc_icon(draw, (x + 92, top + 32, x + 212, top + 158), accent)
        elif idx == 3:
            draw_checklist_icon(draw, (x + 92, top + 32, x + 212, top + 158), accent)
        else:
            draw.ellipse((x + 98, top + 38, x + 206, top + 146), fill=soft, outline=accent, width=5)
            draw.text((x + 132, top + 68), str(idx + 1), font=FONTS.h1, fill=accent)
        draw.text((x + 32, top + 174), title, font=FONTS.h2, fill=COLORS["ink"])
        draw_wrapped(draw, body, (x + 32, top + 220), FONTS.small, COLORS["muted"], box_w - 64, 7)
        if idx < len(stages) - 1:
            arrow(draw, (x + box_w + 12, top + box_h // 2), (x + box_w + gap - 14, top + box_h // 2), COLORS["muted"], 4)

    rounded_box(draw, (165, 635, 1435, 770), fill="#FFFFFF", outline="#DDE6F2", width=2)
    draw.text((205, 665), "발표 핵심 문장", font=FONTS.label, fill=COLORS["blue"])
    draw_wrapped(
        draw,
        "DocMate는 공고를 대신 읽어주는 데서 끝나지 않고, 사용자가 바로 신청 준비를 시작할 수 있는 화면으로 변환합니다.",
        (205, 710),
        FONTS.h2,
        COLORS["ink"],
        1160,
        8,
    )
    img.save(OUT_DIR / "01-service-positioning.png", quality=95)


def draw_slide_02() -> None:
    img, draw = base(
        "분석 파이프라인",
        "현재 데모는 생성형 AI 없이, 문서 추출 → 규칙 기반 구조화 → 프로필 비교 → 근거와 체크리스트 생성 순서로 동작합니다.",
        "기술 흐름도",
    )
    steps = [
        ("1", "입력", "PDF / TXT / 샘플 공고"),
        ("2", "텍스트 추출", "파일에서 분석 가능한 문장 확보"),
        ("3", "항목 구조화", "기간, 대상, 제한 조건, 서류 분리"),
        ("4", "프로필 비교", "사용자 조건과 공고 조건 매칭"),
        ("5", "보수적 판정", "가능 / 추가 확인 / 불가로 분류"),
        ("6", "실행 화면", "원문 근거, 위험 조건, 체크리스트 표시"),
    ]
    y = 314
    box_w, box_h, gap = 220, 230, 24
    accents = [COLORS["blue"], COLORS["teal"], COLORS["purple"], COLORS["green"], COLORS["amber"], COLORS["red"]]
    softs = [COLORS["blue_soft"], COLORS["teal_soft"], COLORS["purple_soft"], COLORS["green_soft"], COLORS["amber_soft"], COLORS["red_soft"]]
    for idx, ((num, title, body), accent, soft) in enumerate(zip(steps, accents, softs)):
        x = 90 + idx * (box_w + gap)
        rounded_box(draw, (x, y, x + box_w, y + box_h), fill="#FFFFFF", outline=soft, width=4)
        draw.ellipse((x + 26, y + 26, x + 82, y + 82), fill=soft, outline=accent, width=3)
        nw, nh = text_size(draw, num, FONTS.label)
        draw.text((x + 54 - nw / 2, y + 54 - nh / 2 - 2), num, font=FONTS.label, fill=accent)
        draw.text((x + 28, y + 104), title, font=FONTS.h2, fill=COLORS["ink"])
        draw_wrapped(draw, body, (x + 28, y + 152), FONTS.small, COLORS["muted"], box_w - 56, 7)
        if idx < len(steps) - 1:
            arrow(draw, (x + box_w + 4, y + 114), (x + box_w + gap - 8, y + 114), COLORS["muted"], 3)

    rounded_box(draw, (185, 625, 1415, 760), fill="#FFFFFF", outline="#DDE6F2", width=2)
    draw.text((225, 655), "운영 원칙", font=FONTS.label, fill=COLORS["blue"])
    badges = [
        ("외부 AI API 호출 없음", COLORS["green_soft"], COLORS["green"]),
        ("같은 입력은 같은 결과", COLORS["blue_soft"], COLORS["blue"]),
        ("근거 문장 함께 표시", COLORS["amber_soft"], COLORS["amber"]),
        ("애매하면 추가 확인", COLORS["red_soft"], COLORS["red"]),
    ]
    x = 225
    for label, fill, color in badges:
        box = pill(draw, (x, 710), label, fill, color, FONTS.small, 18, 10)
        x = box[2] + 18
    img.save(OUT_DIR / "02-analysis-pipeline.png", quality=95)


def draw_slide_03() -> None:
    img, draw = base(
        "생성형 AI PDF 분석과의 차별점",
        "DocMate의 경쟁력은 범용 답변 생성이 아니라, 반복되는 신청 준비 업무를 일정한 제품 흐름으로 고정한 데 있습니다.",
        "차별화 논리",
    )
    left = (95, 285, 720, 720)
    right = (880, 285, 1505, 720)
    rounded_box(draw, left, fill="#FFFFFF", outline="#E3E7EF", width=2)
    rounded_box(draw, right, fill="#FFFFFF", outline="#CFE6DA", width=4)
    pill(draw, (130, 320), "범용 생성형 AI", COLORS["soft"], COLORS["muted"], FONTS.tiny)
    pill(draw, (915, 320), "DocMate", COLORS["green_soft"], COLORS["green"], FONTS.tiny)
    draw.text((130, 372), "문서를 읽고 답변 생성", font=FONTS.h2, fill=COLORS["ink"])
    draw.text((915, 372), "신청 준비 화면 생성", font=FONTS.h2, fill=COLORS["ink"])

    left_items = [
        "질문을 잘 써야 결과가 좋아짐",
        "답변 형식이 프롬프트마다 달라짐",
        "근거 확인과 할 일 정리는 사용자가 다시 수행",
        "문서와 개인 조건이 외부 서비스로 전송될 수 있음",
    ]
    right_items = [
        "선택형 프로필과 고정된 분석 흐름",
        "신청 상태, 위험 조건, 서류, 근거가 같은 형식",
        "분석 결과가 체크리스트와 히스토리로 이어짐",
        "현재 데모는 로컬 실행, 외부 AI API 미사용",
    ]
    for i, item in enumerate(left_items):
        y = 455 + i * 62
        draw.text((132, y), "•", font=FONTS.body, fill=COLORS["muted"])
        draw_wrapped(draw, item, (158, y), FONTS.small, COLORS["muted"], 505, 5)
    for i, item in enumerate(right_items):
        y = 455 + i * 62
        draw.text((917, y), "•", font=FONTS.body, fill=COLORS["green"])
        draw_wrapped(draw, item, (943, y), FONTS.small, COLORS["muted"], 505, 5)

    draw.rounded_rectangle((742, 430, 858, 560), radius=20, fill=COLORS["blue_soft"], outline="#C7D8FF")
    draw.text((771, 465), "VS", font=FONTS.h1, fill=COLORS["blue"])
    rounded_box(draw, (370, 755, 1230, 828), fill="#FFFFFF", outline="#DDE6F2", width=2)
    draw.text((415, 777), "한 줄 답변", font=FONTS.label, fill=COLORS["blue"])
    draw.text((565, 777), "생성형 AI는 문서를 읽어주고, DocMate는 신청 준비 과정을 표준화합니다.", font=FONTS.small, fill=COLORS["ink"])
    img.save(OUT_DIR / "03-generative-ai-differentiation.png", quality=95)


def draw_slide_04() -> None:
    img, draw = base(
        "신뢰를 만드는 판정 루프",
        "분석 결과를 곧바로 확정 답변처럼 보이지 않게 하고, 원문 근거와 추가 확인 상태를 통해 사용자가 판단할 여지를 남깁니다.",
        "신뢰성 설계",
    )
    center = (680, 525)
    radius = 215
    nodes = [
        ("조건 추출", COLORS["blue"], COLORS["blue_soft"]),
        ("프로필 비교", COLORS["teal"], COLORS["teal_soft"]),
        ("보수적 판정", COLORS["amber"], COLORS["amber_soft"]),
        ("원문 근거", COLORS["green"], COLORS["green_soft"]),
        ("사용자 확인", COLORS["purple"], COLORS["purple_soft"]),
    ]
    positions: list[tuple[int, int]] = []
    for i, _ in enumerate(nodes):
        angle = -pi / 2 + i * 2 * pi / len(nodes)
        positions.append((int(center[0] + cos(angle) * radius), int(center[1] + sin(angle) * radius)))

    for i, pos in enumerate(positions):
        next_pos = positions[(i + 1) % len(positions)]
        arrow(draw, pos, next_pos, "#AAB4C3", 4)

    for (label, accent, soft), (x, y) in zip(nodes, positions):
        draw.ellipse((x - 78, y - 78, x + 78, y + 78), fill=soft, outline=accent, width=4)
        lines = wrap_text(draw, label, FONTS.label, 120)
        ty = y - len(lines) * 15
        for line in lines:
            tw, th = text_size(draw, line, FONTS.label)
            draw.text((x - tw / 2, ty), line, font=FONTS.label, fill=accent)
            ty += th + 4

    draw.ellipse((center[0] - 115, center[1] - 115, center[0] + 115, center[1] + 115), fill="#FFFFFF", outline=COLORS["soft"], width=3)
    draw.text((center[0] - 64, center[1] - 45), "DocMate", font=FONTS.h2, fill=COLORS["ink"])
    draw_wrapped(draw, "판정은 결론보다 근거를 먼저 보여준다", (center[0] - 88, center[1] + 8), FONTS.tiny, COLORS["muted"], 185, 4)

    statuses = [
        ("신청 가능", "핵심 조건이 충족될 때", COLORS["green"], COLORS["green_soft"]),
        ("추가 확인 필요", "문서가 애매하거나 근거가 부족할 때", COLORS["amber"], COLORS["amber_soft"]),
        ("신청 불가", "명확한 제한 조건과 충돌할 때", COLORS["red"], COLORS["red_soft"]),
    ]
    y = 325
    for title, body, accent, soft in statuses:
        rounded_box(draw, (1060, y, 1485, y + 115), fill="#FFFFFF", outline=soft, width=4, radius=18)
        pill(draw, (1085, y + 25), title, soft, accent, FONTS.small)
        draw_wrapped(draw, body, (1085, y + 72), FONTS.tiny, COLORS["muted"], 350, 4)
        y += 140
    img.save(OUT_DIR / "04-trust-loop.png", quality=95)


def draw_slide_05() -> None:
    img, draw = base(
        "발표 데모와 출시 준비도",
        "현재 버전은 경진대회 발표용 로컬 데모로는 완성도가 높지만, 실제 공개 서비스로 가려면 운영·데이터·보안 영역이 추가되어야 합니다.",
        "로드맵",
    )
    lanes = [
        ("지금", "발표용 로컬 데모", "90~95%", "핵심 화면, 샘플 공고, 분석 결과, 근거, 체크리스트, 히스토리", COLORS["green"], COLORS["green_soft"]),
        ("다음", "공개 베타", "55~60%", "실공고 fixture 확장, 오류 리포트, OCR 보강, 사용자 테스트", COLORS["blue"], COLORS["blue_soft"]),
        ("이후", "실제 출시", "40~50%", "계정, 개인정보, 배포, 모니터링, 약관, 삭제 요청 처리", COLORS["amber"], COLORS["amber_soft"]),
    ]
    x_start, x_end, y = 150, 1450, 430
    draw.line((x_start, y, x_end, y), fill="#CAD3DF", width=8)
    xs = [220, 800, 1380]
    for idx, ((time, title, pct, body, accent, soft), x) in enumerate(zip(lanes, xs)):
        draw.ellipse((x - 28, y - 28, x + 28, y + 28), fill=accent)
        box = (x - 210, 500, x + 210, 735)
        rounded_box(draw, box, fill="#FFFFFF", outline=soft, width=4)
        pill(draw, (box[0] + 28, box[1] + 28), time, soft, accent, FONTS.tiny)
        draw.text((box[0] + 28, box[1] + 78), title, font=FONTS.h2, fill=COLORS["ink"])
        draw.text((box[0] + 28, box[1] + 125), pct, font=FONTS.h1, fill=accent)
        draw_wrapped(draw, body, (box[0] + 28, box[1] + 183), FONTS.tiny, COLORS["muted"], 360, 5)
        if idx < len(xs) - 1:
            arrow(draw, (x + 70, y), (xs[idx + 1] - 70, y), COLORS["muted"], 4)

    rounded_box(draw, (155, 270, 1445, 348), fill="#FFFFFF", outline="#DDE6F2", width=2)
    draw.text((198, 292), "발표에서는", font=FONTS.label, fill=COLORS["blue"])
    draw.text((340, 292), "“서비스 구동 완성도”와 “출시 전 남은 검증 과제”를 분리해서 말하면 설득력이 높습니다.", font=FONTS.small, fill=COLORS["ink"])
    img.save(OUT_DIR / "05-roadmap-readiness.png", quality=95)


def draw_slide_06() -> None:
    img, draw = base(
        "로컬 처리와 개인정보 메시지",
        "현재 발표 데모는 사용자의 조건과 분석 결과를 로컬 환경에서 처리합니다. 이 점은 생성형 AI 업로드 방식과 구분되는 중요한 발표 포인트입니다.",
        "운영·보안 포인트",
    )
    boxes = [
        ((105, 360, 380, 555), "사용자 브라우저", "프로필 선택\n공고 업로드/샘플 선택", COLORS["blue"], COLORS["blue_soft"]),
        ((510, 360, 785, 555), "로컬 Python 서버", "문서 텍스트 추출\n규칙 기반 분석 실행", COLORS["teal"], COLORS["teal_soft"]),
        ((915, 360, 1190, 555), "분석 엔진", "조건 매칭\n위험 조건 분리", COLORS["green"], COLORS["green_soft"]),
        ((1320, 360, 1535, 555), "로컬 SQLite", "분석 히스토리\n비교 결과 저장", COLORS["amber"], COLORS["amber_soft"]),
    ]
    for idx, (box, title, body, accent, soft) in enumerate(boxes):
        rounded_box(draw, box, fill="#FFFFFF", outline=soft, width=4)
        pill(draw, (box[0] + 24, box[1] + 28), title, soft, accent, FONTS.tiny)
        draw_wrapped(draw, body, (box[0] + 24, box[1] + 90), FONTS.small, COLORS["ink"], box[2] - box[0] - 48, 8)
        if idx < len(boxes) - 1:
            arrow(draw, (box[2] + 22, 458), (boxes[idx + 1][0][0] - 25, 458), COLORS["muted"], 4)

    rounded_box(draw, (215, 635, 1385, 775), fill="#FFFFFF", outline="#DDE6F2", width=2)
    draw.text((255, 665), "발표용 표현", font=FONTS.label, fill=COLORS["blue"])
    draw_wrapped(
        draw,
        "현재 데모는 외부 AI API를 호출하지 않고, 원본 파일을 서버에 영구 저장하지 않는 방향으로 설계했습니다. 실제 출시 단계에서는 암호화, 계정 격리, 삭제 요청 처리, 개인정보 처리방침을 추가해야 합니다.",
        (255, 710),
        FONTS.small,
        COLORS["ink"],
        1060,
        7,
    )
    img.save(OUT_DIR / "06-privacy-local-processing.png", quality=95)


def draw_slide_07() -> None:
    img, draw = base(
        "발표 한 장 요약 보드",
        "발표 말미나 질의응답 시작 전에 띄워 두기 좋은 요약 이미지입니다. 문제, 해결, 차별점, 한계를 한 화면에 정리합니다.",
        "마무리 보드",
    )
    cards = [
        ((90, 285, 470, 520), "문제", "장학금·청년정책 공고는 길고 조건이 흩어져 있어 신청 가능성 판단과 서류 준비가 늦어집니다.", COLORS["red"], COLORS["red_soft"]),
        ((510, 285, 890, 520), "해결", "공고를 구조화해 신청 상태, 위험 조건, 원문 근거, 체크리스트로 즉시 보여줍니다.", COLORS["green"], COLORS["green_soft"]),
        ((930, 285, 1310, 520), "차별점", "범용 요약이 아니라 신청 준비 워크플로우입니다. 결과 형식이 일정하고 히스토리 비교가 가능합니다.", COLORS["blue"], COLORS["blue_soft"]),
        ((90, 560, 470, 795), "현재 강점", "로컬 데모 완성도, 발표 재현성, 선택형 프로필 UX, 근거 중심 판정 화면", COLORS["teal"], COLORS["teal_soft"]),
        ((510, 560, 890, 795), "남은 과제", "OCR, 실공고 검증, 개인정보·계정·배포 운영, 복잡한 예외 조항 처리", COLORS["amber"], COLORS["amber_soft"]),
        ((930, 560, 1310, 795), "확장 방향", "규칙 기반 구조화 위에 LLM을 보조적으로 연결해 모호한 문맥만 검증 대상으로 보완합니다.", COLORS["purple"], COLORS["purple_soft"]),
    ]
    for box, title, body, accent, soft in cards:
        rounded_box(draw, box, fill="#FFFFFF", outline=soft, width=4, radius=18)
        pill(draw, (box[0] + 28, box[1] + 28), title, soft, accent, FONTS.small)
        draw_wrapped(draw, body, (box[0] + 28, box[1] + 88), FONTS.small, COLORS["ink"], box[2] - box[0] - 56, 8)

    draw.rounded_rectangle((1370, 338, 1495, 742), radius=28, fill=COLORS["blue"])
    draw_wrapped(draw, "공고 읽기에서 신청 준비로", (1395, 390), FONTS.h2, "#FFFFFF", 82, 14)
    img.save(OUT_DIR / "07-summary-board.png", quality=95)


def draw_slide_08() -> None:
    img, draw = base(
        "심사위원 질문 대응 맵",
        "예상 질문을 제품 가치, 기술, 신뢰성, 출시 가능성으로 나누어 답변의 중심 문장을 미리 고정합니다.",
        "Q&A 보조자료",
    )
    center = (800, 520)
    topics = [
        ((145, 300, 540, 455), "가치", "왜 필요한가?", "공고 해석 시간을 신청 준비 행동으로 줄입니다.", COLORS["green"], COLORS["green_soft"]),
        ((1060, 300, 1455, 455), "기술", "어떻게 분석하나?", "텍스트 추출 후 규칙 기반 구조화와 프로필 비교를 수행합니다.", COLORS["blue"], COLORS["blue_soft"]),
        ((145, 610, 540, 765), "신뢰성", "틀리면 어떻게 하나?", "근거를 함께 보여주고 애매한 조건은 추가 확인으로 남깁니다.", COLORS["amber"], COLORS["amber_soft"]),
        ((1060, 610, 1455, 765), "출시", "실제로 서비스 가능한가?", "발표 데모는 완성, 출시는 OCR·보안·운영 검증이 다음 단계입니다.", COLORS["purple"], COLORS["purple_soft"]),
    ]

    for box, *_ in topics:
        bx = (box[0] + box[2]) // 2
        by = (box[1] + box[3]) // 2
        dx = bx - center[0]
        dy = by - center[1]
        length = max((dx * dx + dy * dy) ** 0.5, 1)
        sx = int(center[0] + dx / length * 150)
        sy = int(center[1] + dy / length * 150)
        ex = box[2] if bx < center[0] else box[0]
        ey = by
        draw.line((sx, sy, ex, ey), fill="#B8C2D1", width=4)

    for box, title, q, answer, accent, soft in topics:
        rounded_box(draw, box, fill="#FFFFFF", outline=soft, width=4, radius=18)
        pill(draw, (box[0] + 24, box[1] + 24), title, soft, accent, FONTS.tiny)
        draw.text((box[0] + 24, box[1] + 70), q, font=FONTS.label, fill=COLORS["ink"])
        draw_wrapped(draw, answer, (box[0] + 24, box[1] + 108), FONTS.tiny, COLORS["muted"], box[2] - box[0] - 48, 5)

    draw.ellipse((center[0] - 145, center[1] - 145, center[0] + 145, center[1] + 145), fill="#FFFFFF", outline=COLORS["soft"], width=3)
    draw.text((center[0] - 91, center[1] - 42), "DocMate", font=FONTS.h1, fill=COLORS["ink"])
    draw_wrapped(draw, "질문을 네 갈래로 분류해 흔들리지 않게 답한다", (center[0] - 110, center[1] + 25), FONTS.tiny, COLORS["muted"], 220, 4)
    img.save(OUT_DIR / "08-judge-qna-map.png", quality=95)


SLIDES: Iterable[Callable[[], None]] = [
    draw_slide_01,
    draw_slide_02,
    draw_slide_03,
    draw_slide_04,
    draw_slide_05,
    draw_slide_06,
    draw_slide_07,
    draw_slide_08,
]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for slide in SLIDES:
        slide()
    print(f"Generated {len(list(SLIDES))} visuals in {OUT_DIR}")


if __name__ == "__main__":
    main()
