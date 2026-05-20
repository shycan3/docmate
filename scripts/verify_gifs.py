from PIL import Image
import numpy as np
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / 'presentation-materials' / 'demo_assets'
files = ['rec_demo_part1.gif','rec_demo_part2.gif','rec_demo_part3.gif']

def gradient_sharpness(arr):
    # approximate sharpness using gradient magnitude variance
    arrf = arr.astype(float)
    gy, gx = np.gradient(arrf)
    mag2 = gx * gx + gy * gy
    return float(mag2.var())

for fname in files:
    path = OUT / fname
    if not path.exists():
        print(f'MISSING: {fname}')
        continue
    im = Image.open(path)
    frames = []
    try:
        i = 0
        while True:
            im.seek(i)
            frame = im.convert('L')
            arr = np.array(frame)
            frames.append(arr)
            i += 1
    except EOFError:
        pass
    if not frames:
        print(f'EMPTY: {fname}')
        continue
    sharpness_vals = [gradient_sharpness(f) for f in frames]
    mean_sharp = float(np.mean(sharpness_vals))
    print(f'{fname}: frames={len(frames)}, size={frames[0].shape[::-1]}, mean_sharpness={mean_sharp:.2f}, min={min(sharpness_vals):.2f}, max={max(sharpness_vals):.2f}')
