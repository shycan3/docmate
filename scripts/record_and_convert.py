from __future__ import annotations

import os
import time
import shutil
import subprocess
from pathlib import Path
from typing import Tuple

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "presentation-materials" / "demo_assets"
VID_DIR = OUT_DIR / "videos"
OUT_DIR.mkdir(parents=True, exist_ok=True)
VID_DIR.mkdir(parents=True, exist_ok=True)

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
    page.evaluate("""
    if (!window.__demo_cursor) {
      const c = document.createElement('div');
      c.id='__demo_cursor';
      Object.assign(c.style,{position:'fixed',width:'18px',height:'18px',borderRadius:'50%',background:'#fff',border:'3px solid rgba(31,95,191,0.9)',boxShadow:'0 4px 12px rgba(0,0,0,0.25)',transform:'translate(-50%,-50%)',zIndex:9999999,pointerEvents:'none'});
      document.body.appendChild(c);
      window.__demo_cursor = c;
      window.__moveCursor = (x,y)=>{c.style.left = x+'px'; c.style.top = y+'px';}
      window.__ripple = (x,y)=>{ const r=document.createElement('div'); Object.assign(r.style,{position:'fixed',left:(x-6)+'px',top:(y-6)+'px',width:'12px',height:'12px',borderRadius:'50%',background:'rgba(31,95,191,0.18)',zIndex:9999998}); document.body.appendChild(r); setTimeout(()=>r.remove(),500);}    }
    """
    )


def move_cursor_to_element(page, selector: str):
    # compute center
    box = page.eval_on_selector(selector, "el=>{const r=el.getBoundingClientRect(); return {x: r.left + r.width/2, y: r.top + r.height/2}}")
    page.evaluate(f"window.__moveCursor({box['x']},{box['y']})")
    return box["x"], box["y"]


def click_with_cursor(page, selector: str, delay_ms: int = 120):
    x, y = move_cursor_to_element(page, selector)
    page.evaluate(f"window.__ripple({x},{y})")
    page.mouse.click(x, y)
    page.wait_for_timeout(delay_ms)


def record_scenario(playwright, scenario: int) -> Tuple[Path, Path]:
    # returns (video_path, gif_path)
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 1200, "height": 720}, record_video_dir=str(VID_DIR), record_video_size={"width": 1200, "height": 720})
    page = context.new_page()
    page.goto(BASE_URL)
    page.wait_for_load_state('domcontentloaded')
    inject_cursor(page)
    page.wait_for_load_state('networkidle')

    if scenario == 1:
        # demo mode -> history -> compare scroll
        try:
            page.evaluate("fetch('/api/analyses', {method:'DELETE'})")
        except Exception:
            pass
        # move cursor to demo button and click
        click_with_cursor(page, '#demoModeButton')
        page.wait_for_timeout(3000)
        click_with_cursor(page, '#tabHistory')
        page.wait_for_timeout(600)
        page.evaluate("document.querySelector('#compareGrid').scrollBy(400,0)")
        page.wait_for_timeout(800)

    elif scenario == 2:
        # evidence highlight — inject fake result for deterministic rendering
        page.evaluate("window.renderResult && window.renderResult(window.buildFakeResult())")
        page.wait_for_selector('#results')
        page.wait_for_timeout(600)
        page.evaluate("document.querySelector('#evidenceList article')?.scrollIntoView()")
        page.wait_for_timeout(400)

    elif scenario == 3:
        # checklist + terminal verification — use fake result for consistency
        page.evaluate("window.renderResult && window.renderResult(window.buildFakeResult())")
        page.wait_for_selector('#results')
        page.evaluate("document.querySelector('#checklist')?.scrollIntoView()")
        page.wait_for_timeout(400)
        try:
            click_with_cursor(page, '#checklist input[type=checkbox]')
        except Exception:
            pass
        page.wait_for_timeout(600)

    # close context to finalize video
    context.close()
    browser.close()

    # Playwright writes video file with a generated name in VID_DIR
    vids = sorted(VID_DIR.glob("*.webm")) + sorted(VID_DIR.glob("*.mp4"))
    if not vids:
        raise RuntimeError("No video generated")
    video_path = vids[-1]
    # target gif path
    gif_path = OUT_DIR / (f"rec_demo_part{scenario}.gif")
    return video_path, gif_path


def convert_video_to_gif(video_path: Path, gif_path: Path, fps: int = 12):
    ffmpeg = shutil.which('ffmpeg')
    if ffmpeg:
        palette = gif_path.with_suffix('.png')
        # generate palette
        cmd1 = [ffmpeg, '-y', '-i', str(video_path), '-vf', f'fps={fps},scale=1200:-1:flags=lanczos,palettegen', str(palette)]
        subprocess.check_call(cmd1)
        cmd2 = [ffmpeg, '-y', '-i', str(video_path), '-i', str(palette), '-lavfi', f'fps={fps},scale=1200:-1:flags=lanczos[x];[x][1:v]paletteuse', str(gif_path)]
        subprocess.check_call(cmd2)
        try:
            palette.unlink()
        except Exception:
            pass
    else:
        # fallback: use imageio to extract frames and write gif
        import imageio
        reader = imageio.get_reader(str(video_path))
        frames = []
        for im in reader:
            frames.append(im)
        imageio.mimsave(str(gif_path), frames, fps=fps)


def main():
    ensure_server_running()
    with sync_playwright() as p:
        # scenario fps: smoother 1->24 (slow), 2->20 (slower), 3->24 (fast)
        mapping = {1:24, 2:20, 3:24}
        for s in (1,2,3):
            print(f"Recording scenario {s}...")
            video_path, gif_path = record_scenario(p, s)
            print(f"Recorded: {video_path}")
            print(f"Converting to GIF (fps={mapping[s]})...")
            convert_video_to_gif(video_path, gif_path, fps=mapping[s])
            print(f"Saved GIF: {gif_path}")


if __name__ == '__main__':
    main()
