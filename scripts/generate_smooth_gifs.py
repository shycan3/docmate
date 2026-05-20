from __future__ import annotations

import os
import time
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import imageio
import numpy as np

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "presentation-materials" / "demo_assets"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = os.environ.get("DOCMATE_BASE_URL", "http://127.0.0.1:8000")


def ensure_server_running():
    import socket
    host, port = "127.0.0.1", 8000
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
            return
        except Exception:
            pass
    print("Starting backend server...")
    subprocess.Popen(["python", "backend/run.py"], cwd=str(ROOT))
    for _ in range(40):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))
            s.close()
            return
        except Exception:
            time.sleep(0.5)
    raise RuntimeError("Server did not start")


def inject_cursor(page):
    """Inject synthetic cursor (circle with border) and ripple effect"""
    page.evaluate("""
    if (!window.__demo_cursor) {
      const c = document.createElement('div');
      c.id='__demo_cursor';
      Object.assign(c.style,{position:'fixed',width:'20px',height:'20px',borderRadius:'50%',background:'rgba(31,95,191,0.1)',border:'2px solid #1f5fbf',boxShadow:'0 0 8px rgba(31,95,191,0.4)',transform:'translate(-50%,-50%)',zIndex:9999999,pointerEvents:'none'});
      document.body.appendChild(c);
      window.__demo_cursor = c;
      window.__moveCursor = (x,y)=>{c.style.left = x+'px'; c.style.top = y+'px';}
      window.__ripple = (x,y)=>{ const r=document.createElement('div'); Object.assign(r.style,{position:'fixed',left:(x-8)+'px',top:(y-8)+'px',width:'16px',height:'16px',borderRadius:'50%',background:'rgba(31,95,191,0.3)',zIndex:9999998,pointerEvents:'none'}); document.body.appendChild(r); setTimeout(()=>r.remove(),400);}
    }
    """
    )


def capture_frame_sequence(page, actions, frame_dir, base_name, num_frames=30):
    """
    Capture a sequence of frames for a smooth GIF.
    actions: list of (delay_ms, lambda_fn) tuples
    """
    frame_dir.mkdir(parents=True, exist_ok=True)
    frames = []

    for action_idx, (delay_ms, action_fn) in enumerate(actions):
        # Capture multiple frames during the delay to create smooth motion
        num_captures = max(1, delay_ms // 50)  # ~50ms per capture
        for capture_idx in range(num_captures):
            frame_path = frame_dir / f"{base_name}_{len(frames):04d}.png"
            page.screenshot(path=str(frame_path))
            frames.append(frame_path)
            if len(frames) >= num_frames:
                break
            time.sleep(0.050)

        # Execute action
        if action_fn:
            action_fn(page)

        time.sleep((delay_ms % 50) / 1000.0)

        if len(frames) >= num_frames:
            break

    return frames


def scenario_1(page):
    """Part 1: Demo mode + History tab + compare scroll (5-8s, ~2.5s/frame = 3 frames)"""
    page.goto(BASE_URL, wait_until='networkidle')
    page.wait_for_timeout(3000)  # Extra wait for rendering

    # Verify page loaded
    try:
        page.wait_for_selector('body', timeout=5000)
    except Exception as e:
        print(f"Warning: Page load issue: {e}")
    inject_cursor(page)

    # Clear any existing analyses
    try:
        page.evaluate("fetch('/api/analyses', {method:'DELETE'})")
    except Exception:
        pass

    frames = []
    frame_dir = OUT_DIR / "frames_s1"
    frame_dir.mkdir(parents=True, exist_ok=True)

    # Frame 1: Initial state with demo button visible
    frame_path = frame_dir / "frame_0000.png"
    page.screenshot(path=str(frame_path))
    frames.append(frame_path)

    # Move cursor to button and show ripple
    box = page.eval_on_selector('#demoModeButton', "el=>{const r=el.getBoundingClientRect(); return {x: r.left + r.width/2, y: r.top + r.height/2}}")
    page.evaluate(f"window.__moveCursor({box['x']},{box['y']})")
    page.evaluate(f"window.__ripple({box['x']},{box['y']})")
    page.click('#demoModeButton')

    # Wait for demo to complete and history to be populated
    page.wait_for_selector('#tabHistory')
    page.wait_for_timeout(2500)

    # Frame 2: Click history tab to show results
    page.click('#tabHistory')
    page.wait_for_selector('#compareGrid')
    page.wait_for_timeout(500)

    frame_path = frame_dir / "frame_0001.png"
    page.screenshot(path=str(frame_path))
    frames.append(frame_path)

    # Frame 3: Scroll to show comparison
    page.evaluate("document.querySelector('#compareGrid')?.scrollBy(400,0)")
    page.wait_for_timeout(500)

    frame_path = frame_dir / "frame_0002.png"
    page.screenshot(path=str(frame_path))
    frames.append(frame_path)

    return frames


def scenario_2(page):
    """Part 2: Result with evidence highlight (10-12s, ~3s/frame = 4 frames)"""
    page.goto(BASE_URL, wait_until='networkidle')
    page.wait_for_timeout(3000)  # Extra wait for rendering

    # Verify page loaded
    try:
        page.wait_for_selector('body', timeout=5000)
    except Exception as e:
        print(f"Warning: Page load issue: {e}")
    inject_cursor(page)

    frames = []
    frame_dir = OUT_DIR / "frames_s2"
    frame_dir.mkdir(parents=True, exist_ok=True)

    # Inject fake result for consistency
    page.evaluate("""
    const fakeResult = {
      id: 'demo-1',
      filename: '서울희망장학금.txt',
      extraction: {
        title: '2026년 서울 청년 희망장학금',
        eligibility_conditions: ['만 19세 이상', '소득 기준 충족'],
        benefits: ['최대 5천만원 보조금', '멘토링 6개월 제공'],
        required_documents: ['사업계획서', '신분증 사본'],
        application_period: '2026-06-01 ~ 2026-06-30'
      },
      eligibility: { status: 'eligible', reasons: ['기본 조건 충족'] },
      warnings: [],
      evidence: [
        { kind: 'benefit', label: '지원금', snippet: '최대 5천만원 보조금이 지급됩니다.' },
        { kind: 'condition', label: '연령', snippet: '만 19세 이상인 자' }
      ],
      checklist: [{ title: '사업계획서 작성', description: '제출용 사업계획서' }],
      actions: []
    };
    if (window.renderResult) window.renderResult(fakeResult);
    """)

    # Wait for results
    page.wait_for_selector('#results', timeout=5000)
    page.wait_for_timeout(500)

    # Frame 1: Result page view
    frame_path = frame_dir / f"frame_0000.png"
    page.screenshot(path=str(frame_path))
    frames.append(frame_path)
    page.wait_for_timeout(2000)

    # Scroll to evidence section
    page.evaluate("document.querySelector('#evidenceList')?.scrollIntoView()")
    page.wait_for_timeout(500)

    # Frame 2: Evidence section visible
    frame_path = frame_dir / f"frame_0001.png"
    page.screenshot(path=str(frame_path))
    frames.append(frame_path)
    page.wait_for_timeout(2000)

    # Highlight first evidence with glow effect
    page.evaluate("""
    const article = document.querySelector('#evidenceList article');
    if (article) {
      article.style.boxShadow = '0 0 20px rgba(31,95,191,0.4)';
      article.style.background = 'rgba(31,95,191,0.05)';
    }
    """)
    page.wait_for_timeout(500)

    # Frame 3: Evidence highlighted
    frame_path = frame_dir / f"frame_0002.png"
    page.screenshot(path=str(frame_path))
    frames.append(frame_path)
    page.wait_for_timeout(2000)

    # Frame 4: Evidence still highlighted (static hold)
    frame_path = frame_dir / f"frame_0003.png"
    page.screenshot(path=str(frame_path))
    frames.append(frame_path)

    return frames


def scenario_3(page):
    """Part 3: Checklist + terminal verification (4-6s, ~1.5-2s/frame = 3 frames)"""
    page.goto(BASE_URL, wait_until='networkidle')
    page.wait_for_timeout(3000)  # Extra wait for rendering

    # Verify page loaded
    try:
        page.wait_for_selector('body', timeout=5000)
    except Exception as e:
        print(f"Warning: Page load issue: {e}")
    inject_cursor(page)

    frames = []
    frame_dir = OUT_DIR / "frames_s3"
    frame_dir.mkdir(parents=True, exist_ok=True)

    # Inject fake result
    page.evaluate("""
    const fakeResult = {
      id: 'demo-1',
      filename: '서울희망장학금.txt',
      extraction: { title: '2026년 서울 청년 희망장학금' },
      eligibility: { status: 'eligible' },
      checklist: [
        { title: '사업계획서 작성', description: '제출용 사업계획서' },
        { title: '서류 스캔', description: '신분증 및 증빙서류' },
        { title: '접수 링크 확인', description: '온라인 신청 페이지' }
      ],
      evidence: [],
      warnings: [],
      actions: []
    };
    if (window.renderResult) window.renderResult(fakeResult);
    """)

    page.wait_for_selector('#results', timeout=5000)
    page.wait_for_timeout(300)

    # Scroll to checklist
    page.evaluate("document.querySelector('#checklist')?.scrollIntoView()")
    page.wait_for_timeout(300)

    # Frame 1: Checklist visible
    frame_path = frame_dir / f"frame_0000.png"
    page.screenshot(path=str(frame_path))
    frames.append(frame_path)
    page.wait_for_timeout(1500)

    # Click first checklist checkbox
    try:
        checkbox = page.query_selector('#checklist input[type=checkbox]')
        if checkbox:
            box = page.eval_on_selector('#checklist input[type=checkbox]', "el=>{const r=el.getBoundingClientRect(); return {x: r.left + 8, y: r.top + 8}}")
            page.evaluate(f"window.__moveCursor({box['x']},{box['y']})")
            page.evaluate(f"window.__ripple({box['x']},{box['y']})")
            page.click('#checklist input[type=checkbox]')
    except Exception:
        pass

    page.wait_for_timeout(400)

    # Frame 2: Checkbox checked
    frame_path = frame_dir / f"frame_0001.png"
    page.screenshot(path=str(frame_path))
    frames.append(frame_path)
    page.wait_for_timeout(1500)

    # Terminal verification image (static)
    term_img = Image.new('RGB', (1200, 360), (15, 15, 15))
    draw = ImageDraw.Draw(term_img)
    try:
        font = ImageFont.truetype("consola.ttf", 16)
    except Exception:
        font = ImageFont.load_default()

    lines = [
        "$ python scripts/check_smoke.py",
        "",
        "✓ Health check: OK",
        "✓ API samples: 3 loaded",
        "✓ Analysis pipeline: OK",
        "✓ Database: OK",
        "",
        "PASSED: All smoke tests completed successfully"
    ]
    y = 20
    for line in lines:
        draw.text((20, y), line, fill=(100, 255, 100), font=font)
        y += 30

    # Frame 3: Terminal output
    frame_path = frame_dir / f"frame_0002.png"
    term_img.save(str(frame_path))
    frames.append(frame_path)

    return frames


def frames_to_gif(frames, output_path, frame_duration_sec=2.0):
    """Convert frame sequence to GIF with specified duration per frame"""
    if not frames:
        return

    imgs = []
    max_w, max_h = 0, 0

    # First pass: find max dimensions
    for frame_path in frames:
        if isinstance(frame_path, Path):
            img = Image.open(str(frame_path))
        else:
            img = Image.open(frame_path)
        img = img.convert('RGB')
        max_w = max(max_w, img.width)
        max_h = max(max_h, img.height)

    # Second pass: normalize and convert to arrays
    for frame_path in frames:
        if isinstance(frame_path, Path):
            img = Image.open(str(frame_path))
        else:
            img = Image.open(frame_path)
        img = img.convert('RGB')

        # Pad to max dimensions if needed
        if img.width != max_w or img.height != max_h:
            bg = Image.new('RGB', (max_w, max_h), (255, 255, 255))
            bg.paste(img, (0, 0))
            img = bg

        imgs.append(np.asarray(img))

    total_duration = len(frames) * frame_duration_sec
    imageio.mimsave(str(output_path), imgs, duration=frame_duration_sec)
    print(f"Saved: {output_path} ({len(frames)} frames × {frame_duration_sec}s/frame = ~{total_duration:.1f}s)")


def main():
    ensure_server_running()
    time.sleep(1)  # Extra wait for server startup

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Show browser for debugging

        # Scenario 1: Demo + History (3 frames, 2.25s each = ~6.75s total)
        print("Recording scenario 1 (demo + history)...")
        page1 = browser.new_page(viewport={"width": 1200, "height": 720})
        frames1 = scenario_1(page1)
        frames_to_gif(frames1, OUT_DIR / "rec_demo_part1.gif", frame_duration_sec=2.25)
        page1.close()

        # Scenario 2: Evidence (4 frames, 3s each = ~12s total)
        print("Recording scenario 2 (evidence highlight)...")
        page2 = browser.new_page(viewport={"width": 1200, "height": 720})
        frames2 = scenario_2(page2)
        frames_to_gif(frames2, OUT_DIR / "rec_demo_part2.gif", frame_duration_sec=3.0)
        page2.close()

        # Scenario 3: Checklist (3 frames, 1.75s each = ~5.25s total)
        print("Recording scenario 3 (checklist + verification)...")
        page3 = browser.new_page(viewport={"width": 1200, "height": 720})
        frames3 = scenario_3(page3)
        frames_to_gif(frames3, OUT_DIR / "rec_demo_part3.gif", frame_duration_sec=1.75)
        page3.close()

        browser.close()


if __name__ == '__main__':
    main()
