from PIL import Image, ImageDraw, ImageFont
import os

root = os.path.join(os.getcwd(), "presentation-materials")
img_dir = os.path.join(root, "images")
out_dir = os.path.join(root, "demo_assets")
os.makedirs(out_dir, exist_ok=True)

# Source images (input -> result -> checklist)
src_files = [
    "02-structured-profile-and-sample-choice.png",
    "03-result-summary-decision.png",
    "05-checklist-and-next-actions.png",
]

captions = [
    "(입력) 간단 프로필로 자가진단 시작",
    "(결과) 우선순위 정책 및 근거 스니펫",
    "(체크리스트) 제출서류·다음 액션 안내",
]

annotated_paths = []
for i, fname in enumerate(src_files, start=1):
    src = os.path.join(img_dir, fname)
    if not os.path.exists(src):
        print('Missing source image:', src)
        continue
    im = Image.open(src).convert("RGBA")
    # resize to width 1200 if larger
    max_w = 1200
    w, h = im.size
    if w > max_w:
        new_h = int(h * (max_w / w))
        im = im.resize((max_w, new_h), Image.LANCZOS)
        w, h = im.size
    # draw semi-transparent band at bottom
    overlay = Image.new('RGBA', im.size, (255,255,255,0))
    draw = ImageDraw.Draw(overlay)
    band_h = int(h * 0.16)
    band_y = h - band_h
    draw.rectangle([(0, band_y), (w, h)], fill=(0, 0, 0, 190))
    # caption text
    try:
        font = ImageFont.truetype("arial.ttf", size=int(band_h * 0.30))
    except Exception:
        font = ImageFont.load_default()
    text = captions[i-1]
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font); text_w = right - left; text_h = bottom - top
    padding = int(band_h * 0.18)
    text_x = padding
    text_y = band_y + (band_h - text_h) // 2
    draw.text((text_x, text_y), text, font=font, fill=(255,255,255,255))
    # composite
    out = Image.alpha_composite(im, overlay)
    # convert to RGB
    out_rgb = out.convert('RGB')
    out_path = os.path.join(out_dir, f"annotated_{i:02d}.png")
    out_rgb.save(out_path, quality=95)
    annotated_paths.append(out_path)
    print('Saved', out_path)

# create looping GIF
frames = []
for p in annotated_paths:
    im = Image.open(p).convert('P')
    frames.append(im)

if frames:
    gif_path = os.path.join(out_dir, 'demo_loop.gif')
    frames[0].save(gif_path, save_all=True, append_images=frames[1:], duration=1500, loop=0, optimize=True)
    print('Saved GIF', gif_path)
else:
    print('No frames to create GIF')
