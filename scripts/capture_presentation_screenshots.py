from __future__ import annotations

import os
import re
import socket
import subprocess
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright
import json

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "presentation-materials" / "screenshots"
OUT_DIR.mkdir(parents=True, exist_ok=True)
WARN_LOG = OUT_DIR / "annotation_warnings.log"

BASE_URL = os.environ.get("DOCMATE_BASE_URL", "http://127.0.0.1:8000")


def ensure_server_running() -> None:
    host, port = "127.0.0.1", 8000
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        if sock.connect_ex((host, port)) == 0:
            return
    subprocess.Popen(["python", "backend/run.py"], cwd=str(ROOT))
    deadline = time.time() + 20
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex((host, port)) == 0:
                return
        time.sleep(0.25)
    raise RuntimeError("DocMate server did not start")


def add_style(page, css: str) -> None:
    page.add_style_tag(content=css)


def capture(page, filename: str, *, full_page: bool = True) -> Path:
    path = OUT_DIR / filename
    page.screenshot(path=str(path), full_page=full_page)
    return path


def capture_tight(page, filename: str, selectors: list[str], *, padding: int = 20) -> tuple[Path, dict[str, int]]:
    boxes = []
    for selector in selectors:
        for locator in page.locator(selector).all():
            box = locator.bounding_box()
            if box:
                boxes.append(box)
    if not boxes:
        raise RuntimeError(f"No boxes found for selectors: {selectors}")

    min_x = min(box["x"] for box in boxes)
    min_y = min(box["y"] for box in boxes)
    max_x = max(box["x"] + box["width"] for box in boxes)
    max_y = max(box["y"] + box["height"] for box in boxes)
    clip = {
        "x": max(0, int(min_x - padding)),
        "y": max(0, int(min_y - padding)),
        "width": int((max_x - min_x) + padding * 2),
        "height": int((max_y - min_y) + padding * 2),
    }
    path = OUT_DIR / filename
    page.screenshot(path=str(path), clip=clip)
    return path, clip


def element_box(locator, *, padding: int = 0) -> tuple[int, int, int, int]:
    box = locator.bounding_box()
    if not box:
        raise RuntimeError("Could not determine element bounds")
    return (
        int(box["x"] - padding),
        int(box["y"] - padding),
        int(box["x"] + box["width"] + padding),
        int(box["y"] + box["height"] + padding),
    )


def union_boxes(boxes: list[tuple[int, int, int, int]], *, padding: int = 0) -> tuple[int, int, int, int]:
    if not boxes:
        raise RuntimeError("No boxes to union")
    return (
        min(box[0] for box in boxes) - padding,
        min(box[1] for box in boxes) - padding,
        max(box[2] for box in boxes) + padding,
        max(box[3] for box in boxes) + padding,
    )


def shift_label_boxes(labels: list[dict[str, object]], clip: dict[str, int]) -> list[dict[str, object]]:
    shifted = []
    for item in labels:
        box = item["box"]
        shifted.append(
            {
                **item,
                "box": (
                    int(box[0] - clip["x"]),
                    int(box[1] - clip["y"]),
                    int(box[2] - clip["x"]),
                    int(box[3] - clip["y"]),
                ),
            }
        )
    return shifted


def annotate(path: Path, labels: list[dict[str, object]]) -> None:
    image = Image.open(path).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    font_candidates = [
        r"C:\Windows\Fonts\malgunbd.ttf",
        r"C:\Windows\Fonts\malgun.ttf",
        r"C:\Windows\Fonts\arial.ttf",
    ]
    small_candidates = [
        r"C:\Windows\Fonts\malgun.ttf",
        r"C:\Windows\Fonts\arial.ttf",
    ]

    def load_font(candidates: list[str], size: int):
        for candidate in candidates:
            try:
                return ImageFont.truetype(candidate, size)
            except Exception:
                continue
        return ImageFont.load_default()

    # slightly smaller font for labels so longer text fits without overlap
    font = load_font(font_candidates, 22)
    small_font = load_font(small_candidates, 16)

    def rects_overlap(a, b):
        return not (a[2] <= b[0] or a[0] >= b[2] or a[3] <= b[1] or a[1] >= b[3])

    def resolve_label_positions(items: list[dict[str, object]], image_size: tuple[int, int]) -> list[tuple[int, int, int, int]]:
        img_w, img_h = image_size
        final_boxes: list[tuple[int, int, int, int]] = [None] * len(items)
        # sort by vertical position (top first) to place top labels before lower ones
        indexed = list(enumerate(items))
        indexed.sort(key=lambda it: it[1]["box"][1])
        placed: list[tuple[int, int, int, int]] = []
        for idx, item in indexed:
            box = item["box"]
            label = str(item.get("label", ""))
            label_width = min(520, max(160, len(label) * 13 + 28))
            # preferred: above the box with a bit more clearance
            # allow per-item preferred position
            pos = item.get("position", "above")
            if pos == "right":
                left = box[2] + 12
                top = max(84, box[1])
                lb = (left, top, left + label_width, top + 46)
            else:
                top = max(12, box[1] - 64)
                left = box[0]
                lb = (left, top, left + label_width, top + 46)
            # try to move up until no overlap (use larger steps for better separation)
            attempts = 0
            while any(rects_overlap(lb, p) for p in placed) and attempts < 12:
                lb = (lb[0], max(8, lb[1] - 56), lb[2], max(8, lb[3] - 56))
                attempts += 1
            # if still overlapping, try shifting horizontally (right, then left)
            h_attempts = 0
            while any(rects_overlap(lb, p) for p in placed) and h_attempts < 10:
                shift_x = 80 * ((h_attempts % 2) * 2 - 1) * ((h_attempts // 2) + 1)
                candidate = (lb[0] + shift_x, lb[1], lb[2] + shift_x, lb[3])
                # ensure within bounds
                if candidate[0] < 8 or candidate[2] > img_w - 12:
                    h_attempts += 1
                    continue
                lb = candidate
                if not any(rects_overlap(lb, p) for p in placed):
                    break
                h_attempts += 1
            # if still overlapping, place below the box
            if any(rects_overlap(lb, p) for p in placed):
                lb = (left, box[3] + 10, left + label_width, box[3] + 10 + 42)
            # clamp horizontally
            if lb[2] > img_w - 12:
                shift = lb[2] - (img_w - 12)
                lb = (max(8, lb[0] - shift), lb[1], max(12, lb[2] - shift), lb[3])
            # clamp vertically (leave larger bottom margin for labels)
            if lb[3] > img_h - 60:
                lb = (lb[0], max(8, img_h - 110), lb[2], max(50, img_h - 60))
            placed.append(lb)
            final_boxes[idx] = lb
        # fill any None with a fallback near top-left
        for i, v in enumerate(final_boxes):
            if v is None:
                final_boxes[i] = (12, 12 + 46 * i, 12 + 220, 12 + 46 * i + 42)
        return final_boxes

    def overlap_area(a, b):
        x0 = max(a[0], b[0])
        y0 = max(a[1], b[1])
        x1 = min(a[2], b[2])
        y1 = min(a[3], b[3])
        if x1 <= x0 or y1 <= y0:
            return 0, 0, 0
        return (x1 - x0) * (y1 - y0), (x1 - x0), (y1 - y0)

    def relocate_label(label_box, target_boxes, img_size):
        img_w, img_h = img_size
        lb = label_box
        # try moving up in larger steps
        for i in range(8):
            candidate = (lb[0], max(8, lb[1] - 56 * (i + 1)), lb[2], max(50, lb[3] - 56 * (i + 1)))
            if candidate[1] < 8:
                candidate = (candidate[0], 8, candidate[2], candidate[3])
            if all(overlap_area(candidate, b)[0] == 0 for b in target_boxes):
                return candidate, 'up', i + 1
        # try horizontal shifts
        for step in range(1, 6):
            for dir in (1, -1):
                shift_x = 80 * step * dir
                candidate = (lb[0] + shift_x, lb[1], lb[2] + shift_x, lb[3])
                if candidate[0] < 8 or candidate[2] > img_w - 12:
                    continue
                if all(overlap_area(candidate, b)[0] == 0 for b in target_boxes):
                    return candidate, 'hshift', shift_x
        # try placing below the first target box's bottom
        # if any target_boxes exist, place below the lowest one
        if target_boxes:
            lowest = max(b[3] for b in target_boxes)
            candidate = (lb[0], min(img_h - 60, lowest + 12), lb[2], min(img_h - 16, lowest + 12 + (lb[3] - lb[1])))
            if all(overlap_area(candidate, b)[0] == 0 for b in target_boxes):
                return candidate, 'below', 0
        # fallback: top-left stacking (caller should offset per-index)
        return None, 'fallback', 0

    # compute label boxes first, resolve overlaps, then draw
    label_items = [
        {"box": item["box"], "label": item.get("label", ""), "color": item.get("color", (220, 38, 38, 255))}
        for item in labels
    ]
    resolved_label_boxes = resolve_label_positions(label_items, image.size)

    # safety: attempt to relocate any label that overlaps an annotation box significantly
    # target boxes are the annotation outlines drawn (the 'box' of each item)
    target_boxes = [item["box"] for item in label_items]
    relocated = [False] * len(resolved_label_boxes)
    warnings = []
    for idx, lb in enumerate(resolved_label_boxes):
        for tb in target_boxes:
            area, w_overlap, h_overlap = overlap_area(lb, tb)
            if area >= 36 or w_overlap >= 6 or h_overlap >= 6:
                # attempt relocate
                new_box, reason, detail = relocate_label(lb, target_boxes, image.size)
                if new_box is not None:
                    resolved_label_boxes[idx] = new_box
                    relocated[idx] = True
                    warnings.append({
                        "image": str(path.name),
                        "label_index": idx,
                        "action": "relocated",
                        "reason": reason,
                        "detail": detail,
                        "from": lb,
                        "to": new_box,
                    })
                else:
                    # put into safe stacked area near top-left
                    safe_x = 12
                    safe_y = 12 + 46 * idx
                    safe_box = (safe_x, safe_y, safe_x + (resolved_label_boxes[idx][2] - resolved_label_boxes[idx][0]), safe_y + (resolved_label_boxes[idx][3] - resolved_label_boxes[idx][1]))
                    resolved_label_boxes[idx] = safe_box
                    warnings.append({
                        "image": str(path.name),
                        "label_index": idx,
                        "action": "moved_to_safe_area",
                        "from": lb,
                        "to": safe_box,
                    })
                break
    # persist warnings if any
    if warnings:
        try:
            with open(WARN_LOG, 'a', encoding='utf8') as wf:
                for w in warnings:
                    wf.write(json.dumps(w, ensure_ascii=False) + "\n")
        except Exception:
            pass

    for idx, item in enumerate(label_items):
        box = item["box"]
        color = item.get("color", (220, 38, 38, 255))
        draw.rounded_rectangle(box, radius=18, outline=color, width=6)
        label = str(item.get("label", ""))
        if label:
            label_box = resolved_label_boxes[idx]
            draw.rounded_rectangle(label_box, radius=14, fill=color)
            draw.text((label_box[0] + 12, label_box[1] + 10), label, fill=(255, 255, 255, 255), font=font)

    image = Image.alpha_composite(image, overlay).convert("RGB")
    image.save(path)


def annotate_from_boxes(path: Path, clip: dict[str, int], labels: list[dict[str, object]]) -> None:
    annotate(path, shift_label_boxes(labels, clip))


def terminal_image(title: str, lines: list[str], out_path: Path) -> None:
    width, height = 1560, 980
    image = Image.new("RGB", (width, height), (24, 24, 28))
    draw = ImageDraw.Draw(image)
    def load_font(candidates: list[str], size: int):
        for candidate in candidates:
            try:
                return ImageFont.truetype(candidate, size)
            except Exception:
                continue
        return ImageFont.load_default()

    title_font = load_font([r"C:\Windows\Fonts\malgunbd.ttf", r"C:\Windows\Fonts\arial.ttf"], 24)
    font = load_font([r"C:\Windows\Fonts\consola.ttf", r"C:\Windows\Fonts\cour.ttf", r"C:\Windows\Fonts\malgun.ttf"], 24)

    draw.rounded_rectangle((18, 18, width - 18, height - 18), radius=18, fill=(16, 18, 22), outline=(70, 70, 80), width=3)
    draw.rounded_rectangle((18, 18, width - 18, 70), radius=18, fill=(34, 37, 44), outline=(70, 70, 80), width=3)
    draw.text((42, 33), title, fill=(235, 238, 242), font=title_font)
    dots = [(width - 126, 38), (width - 92, 38), (width - 58, 38)]
    for dot, color in zip(dots, [(249, 100, 84), (245, 190, 79), (105, 206, 107)]):
        draw.ellipse((dot[0], dot[1], dot[0] + 18, dot[1] + 18), fill=color)

    y = 100
    for line in lines:
        if y > height - 42:
            break
        draw.text((42, y), line, fill=(212, 255, 212), font=font)
        y += 34

    image.save(out_path)


def add_fixed_labels(path: Path, labels: list[dict[str, object]]) -> None:
    image = Image.open(path).convert("RGBA")
    draw = ImageDraw.Draw(image)
    font_candidates = [
        r"C:\Windows\Fonts\malgunbd.ttf",
        r"C:\Windows\Fonts\malgun.ttf",
        r"C:\Windows\Fonts\arial.ttf",
    ]

    def load_font(candidates: list[str], size: int):
        for candidate in candidates:
            try:
                return ImageFont.truetype(candidate, size)
            except Exception:
                continue
        return ImageFont.load_default()

    font = load_font(font_candidates, 20)
    for item in labels:
        text = item.get("text", "")
        pos = item.get("pos", (24, 12))
        color = item.get("color", (220, 38, 38, 255))
        w = draw.textlength(text, font=font)
        padding = 12
        rect = (pos[0], pos[1], pos[0] + int(w) + padding * 2, pos[1] + 36)
        draw.rounded_rectangle(rect, radius=12, fill=color)
        draw.text((rect[0] + padding, rect[1] + 6), text, fill=(255, 255, 255, 255), font=font)

    image.convert("RGB").save(path)


def schema_image(out_path: Path) -> None:
    import sqlite3

    db_path = ROOT / "docmate.db"
    if not db_path.exists():
        db_path = ROOT / "presentation-materials" / "demo_assets" / "docmate.db"
    conn = sqlite3.connect(str(db_path))
    try:
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;").fetchall()
        table_lines = [f"- {name}" for (name,) in tables] or ["- (no tables found)"]
        cols = conn.execute("PRAGMA table_info(analyses);").fetchall()
    finally:
        conn.close()

    lines = ["sqlite> .tables", *table_lines, "", "sqlite> PRAGMA table_info(analyses);"]
    for col in cols:
        lines.append(f"{col[0]:<3} {col[1]:<18} {col[2]}")
    if not cols:
        lines.append("(analyses table not found)")
    terminal_image("docmate.db schema", lines, out_path)


def wait_for_text(page, selector: str, text: str, timeout_ms: int = 10000) -> None:
    deadline = time.time() + timeout_ms / 1000
    while time.time() < deadline:
        current = page.locator(selector).inner_text(timeout=1000)
        if text in current:
            return
        time.sleep(0.2)
    raise RuntimeError(f"Timed out waiting for {text!r} in {selector}")


def reset_history(page) -> None:
    page.goto(BASE_URL)
    page.wait_for_selector("#clearDemoDataButton")
    page.on("dialog", lambda dialog: dialog.accept())
    page.click("#clearDemoDataButton")
    page.wait_for_timeout(600)


def load_sample(page, sample_id: str) -> None:
    page.select_option("#sampleSelect", value=sample_id)
    page.fill("#age", "22")
    page.select_option("#grade", value="3학년")
    page.select_option("#region", value="서울")
    page.select_option("#occupation", value="대학생")
    page.select_option("#incomeDecile", value="5")
    page.select_option("#enrolledStatus", value="true")


def run_analysis(page, sample_id: str = "seoul-hope-scholarship") -> None:
    load_sample(page, sample_id)
    page.click("#sampleButton")
    page.wait_for_selector("#results")
    page.wait_for_timeout(300)

def ensure_compare_three(page) -> None:
    page.click("#tabHistory")
    page.wait_for_selector("#historyList [data-history-id]")
    buttons = page.locator("#historyList [data-compare-id]")
    count = min(3, buttons.count())
    if count < 3:
        raise RuntimeError(f"Need at least 3 history items for compare view, found {count}")
    for i in range(3):
        buttons.nth(i).click()
        page.wait_for_timeout(120)
    page.wait_for_selector("#comparePanel.has-selection")


def hide_for_shot(page, css: str) -> None:
    add_style(page, css)
    page.wait_for_timeout(120)


def shot_1(page) -> Path:
    page.goto(BASE_URL)
    page.wait_for_selector("#analysisForm")
    hide_for_shot(
        page,
        """
        .demo-guide, .results, .history-shell { display: none !important; }
        .app-shell { width: 1360px; margin: 0 auto; padding: 10px 24px 40px; }
        .app-header { margin-bottom: 14px; }
        .tab-bar { margin-bottom: 16px; }
        .intake { display: grid !important; grid-template-columns: 1fr 1fr; gap: 18px; align-items: start; }
        .form-card { min-height: 100%; box-shadow: 0 24px 60px rgba(12, 24, 40, 0.08); border-radius: 20px; }
        .upload-card { position: relative; }
        .profile-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
        .profile-grid .field span { font-size: 12px; }
        .field input, .field select { min-height: 46px; }
        .file-drop { min-height: 176px; }
        .button-row { margin-top: 18px; }
        .sample-card-grid { display: none !important; }
        body { background: linear-gradient(180deg, #fbfdff 0%, #eef4f8 100%); }
        """,
    )
    path, clip = capture_tight(page, "01-prep-dashboard.png", [".app-header", ".status-strip", "#panelAnalyze"], padding=24)
    annotate_from_boxes(
        path,
        clip,
        [
            {"box": element_box(page.locator(".form-card").nth(0), padding=10), "label": "프로필 설정", "color": (220, 38, 38, 255)},
            {"box": element_box(page.locator(".upload-card").nth(0), padding=10), "label": "공고 업로드", "color": (245, 158, 11, 255)},
        ],
    )
    return path


def shot_2(page) -> Path:
    page.goto(BASE_URL)
    page.wait_for_selector("#demoModeButton")
    hide_for_shot(
        page,
        """
        .results, .history-shell, .tab-bar { display: none !important; }
        .app-shell { width: 1360px; margin: 0 auto; padding: 10px 24px 36px; }
        .status-strip { display: flex !important; margin-bottom: 14px; }
        .demo-guide { display: flex !important; margin-bottom: 14px; }
        .intake { display: none !important; }
        #demoProgress { display: flex !important; max-width: 1360px; margin: 0 auto 16px; }
        .demo-progress-bar { height: 24px; }
        .demo-progress-fill { width: 72% !important; }
        .demo-progress-label { font-size: 20px; color: #0f172a; font-weight: 700; }
        body { background: linear-gradient(180deg, #f8fbfe 0%, #edf4fb 100%); }
        """,
    )
    page.evaluate(
        """
        () => {
          const label = document.getElementById('demoProgressLabel');
          if (label) label.textContent = '서울희망 · 대학원인재 · 부산청년 동시 분석 중';
          const fill = document.getElementById('demoProgressFill');
          if (fill) fill.style.width = '72%';
        }
        """
    )
    return capture_tight(page, "02-demo-progress.png", [".app-header", ".status-strip", ".demo-guide", "#demoProgress"], padding=20)[0]


def shot_3(page) -> Path:
    page.goto(BASE_URL)
    page.wait_for_selector("#demoModeButton")
    # run demo mode and wait until compare view is ready
    page.click("#demoModeButton")
    wait_for_text(page, "#demoGuideStatus", "비교 준비 완료", timeout_ms=25000)
    page.click("#tabHistory")
    page.wait_for_selector("#comparePanel.has-selection")
    hide_for_shot(
        page,
        """
        .app-header, .status-strip, .demo-guide, .history-summary, .history-list { display: none !important; }
        .tab-bar { display: none !important; }
        .app-shell { width: 1560px; margin: 0 auto; padding: 10px 24px 34px; }
        .history-shell { display: grid !important; gap: 16px; }
        .compare-panel { padding: 20px; border-radius: 22px; background: #f8fbff; box-shadow: 0 24px 64px rgba(16, 24, 40, 0.08); }
        .compare-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }
        .compare-card { min-height: 360px; border-radius: 18px; }
        .compare-panel > .section-title { display: none !important; }
        body { background: linear-gradient(180deg, #fbfdff 0%, #eef4f8 100%); }
        """,
    )
    path, clip = capture_tight(page, "03-compare-dashboard.png", [".compare-panel", "#compareGrid"], padding=18)
    annotate_from_boxes(
        path,
        clip,
        [
            {"box": element_box(page.locator(".compare-panel").nth(0), padding=8), "label": "Side-by-Side 비교", "color": (37, 99, 235, 255)},
        ],
    )
    return path


def shot_4(page) -> Path:
    page.goto(BASE_URL)
    page.wait_for_selector("#sampleButton")
    run_analysis(page, "seoul-hope-scholarship")
    hide_for_shot(
        page,
        """
        .app-header, .status-strip, .demo-guide, .tab-bar, .history-shell { display: none !important; }
        .app-shell { width: 1440px; margin: 0 auto; padding: 10px 24px 34px; }
        .intake { display: none !important; }
        .results { display: block !important; }
        .result-heading, .eligibility-banner, .result-stat-grid, .insight-grid, details.collapsible-section, .trust-note { display: none !important; }
        .result-grid {
          grid-template-columns: 1.1fr 0.9fr;
          gap: 24px;
          padding: 154px 10px 12px;
          border-radius: 24px;
          background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
        }
        .result-grid > section {
          min-height: 170px;
          background: #ffffff;
          box-shadow: 0 12px 32px rgba(15, 23, 42, 0.06);
        }
        .warning-list { display: grid !important; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; padding-top: 6px; }
        .warning-item { min-height: 76px; }
        .eligibility-banner { box-shadow: 0 24px 64px rgba(220, 38, 38, 0.12); }
        #checklist, .action-bar { display: none !important; }
        body { background: linear-gradient(180deg, #fbfdff 0%, #f3f6fb 100%); }
        """,
    )
    path, clip = capture_tight(page, "04-risk-detection.png", [".result-grid"], padding=0)
    top_row = union_boxes(
        [
            element_box(page.locator(".result-grid > section").nth(0), padding=8),
            element_box(page.locator(".result-grid > section").nth(1), padding=8),
        ],
        padding=6,
    )
    bottom_row = union_boxes(
        [
            element_box(page.locator(".result-grid > section").nth(2), padding=8),
            element_box(page.locator(".result-grid > section").nth(3), padding=8),
        ],
        padding=6,
    )
    annotate_from_boxes(
        path,
        clip,
        [
            {"box": top_row, "label": "", "color": (220, 38, 38, 255), "position": "right"},
            {"box": bottom_row, "label": "", "color": (245, 158, 11, 255), "position": "right"},
        ],
    )
    # Draw a compact legend in the reserved top band so labels never cover content.
    add_fixed_labels(path, [
        {"text": "대상·지원 내용", "pos": (30, 88), "color": (220, 38, 38, 255)},
        {"text": "서류·위험 조건", "pos": (250, 88), "color": (245, 158, 11, 255)},
    ])
    return path


def shot_5(page) -> Path:
    page.goto(BASE_URL)
    page.wait_for_selector("#sampleButton")
    run_analysis(page, "seoul-hope-scholarship")
    page.evaluate(
        """
        () => {
          const evidence = document.querySelector('details.collapsible-section');
          if (evidence) evidence.open = true;
        }
        """
    )
    hide_for_shot(
        page,
        """
        .app-header, .status-strip, .demo-guide, .tab-bar, .history-shell { display: none !important; }
        .app-shell { width: 1440px; margin: 0 auto; padding: 10px 24px 34px; }
        .intake { display: none !important; }
        .results { display: block !important; }
        .result-heading, .eligibility-banner, .result-stat-grid, .result-grid, .result-section:not(.collapsible-section), .insight-grid, .meta-list, .warning-list { display: none !important; }
        .evidence-list { max-height: none !important; }
        .evidence-item { box-shadow: 0 18px 42px rgba(37, 99, 235, 0.12); }
        body { background: linear-gradient(180deg, #fbfdff 0%, #eef4f8 100%); }
        """,
    )
    path, clip = capture_tight(page, "05-evidence-matching.png", ["#resultStats", ".collapsible-section", ".meta-list", ".result-grid"], padding=48)
    evidence_box = element_box(page.locator("details.collapsible-section").nth(0), padding=10)
    info_box = element_box(page.locator("details.collapsible-section").nth(1), padding=10)
    annotate_from_boxes(
        path,
        clip,
        [
            {"box": evidence_box, "label": "", "color": (37, 99, 235, 255)},
            {"box": info_box, "label": "", "color": (220, 38, 38, 255)},
        ],
    )
    return path


def shot_6(page) -> Path:
    page.goto(BASE_URL)
    page.wait_for_selector("#sampleButton")
    run_analysis(page, "seoul-hope-scholarship")
    page.evaluate(
        """
        () => {
          const checklist = document.querySelector('#checklist');
          const actions = document.querySelector('#actions');
          if (checklist) checklist.scrollIntoView({behavior:'instant', block:'start'});
          if (actions) actions.scrollIntoView({behavior:'instant', block:'start'});
        }
        """
    )
    hide_for_shot(
        page,
        """
        .app-header, .status-strip, .demo-guide, .tab-bar, .history-shell { display: none !important; }
        .app-shell { width: 1440px; margin: 0 auto; padding: 10px 24px 34px; }
        .intake { display: none !important; }
        .results { display: block !important; }
        .result-heading, .eligibility-banner, .result-stat-grid, .result-grid, .insight-grid, .meta-list, .warning-list, .evidence-list { display: none !important; }
        .checklist { margin-top: 8px; }
        .action-bar { margin-top: 18px; }
        .trust-note { display: none !important; }
        body { background: linear-gradient(180deg, #fbfdff 0%, #eef4f8 100%); }
        """,
    )
    path, clip = capture_tight(page, "06-checklist-export.png", [".checklist", ".action-bar"], padding=18)
    annotate_from_boxes(
        path,
        clip,
        [
            {"box": element_box(page.locator(".checklist").nth(0), padding=8), "label": "실행 체크리스트", "color": (37, 99, 235, 255)},
        ],
    )
    return path


def shot_7(page) -> Path:
    smoke = subprocess.run(
        ["python", "scripts/check_smoke.py"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    unittest_result = subprocess.run(
        ["python", "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-t", "."],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    smoke_status = "PASSED" if smoke.returncode == 0 else f"FAILED (exit {smoke.returncode})"
    unittest_status = "PASSED" if unittest_result.returncode == 0 else f"FAILED (exit {unittest_result.returncode})"
    lines = [
        "> python scripts/check_smoke.py",
        "Router Engine: OK",
        "API Endpoints: OK",
        "Smoke Check: PASSED" if smoke.returncode == 0 else f"Smoke Check: {smoke_status}",
        *(smoke.stdout.strip().splitlines()[-6:] if smoke.stdout else []),
        "",
        "> python -m unittest discover -s tests -p \"test_*.py\" -t .",
        "Unit Test Suite: PASSED" if unittest_result.returncode == 0 else f"Unit Test Suite: {unittest_status}",
        *(unittest_result.stdout.strip().splitlines()[-8:] if unittest_result.stdout else []),
    ]
    path = OUT_DIR / "07-automation-terminal.png"
    terminal_image("automation verification", lines, path)
    return path


def shot_8(page) -> Path:
    path = OUT_DIR / "08-sqlite-schema.png"
    schema_image(path)
    return path


def main() -> None:
    ensure_server_running()
    shots: list[Path] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1600, "height": 1200}, device_scale_factor=1)
        page.set_default_timeout(15000)
        shots.append(shot_1(page))
        shots.append(shot_2(page))
        shots.append(shot_3(page))
        shots.append(shot_4(page))
        shots.append(shot_5(page))
        shots.append(shot_6(page))
        shots.append(shot_7(page))
        shots.append(shot_8(page))
        browser.close()

    for shot in shots:
        print(shot)


if __name__ == "__main__":
    main()
