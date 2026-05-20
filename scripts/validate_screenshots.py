from PIL import Image
import numpy as np
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parents[1] / "presentation-materials" / "screenshots"

# Designer persona rules:
# - Label pills (red/orange) must not overlap page header (top 60px)
# - Label pills must not overlap annotation boxes (large colored outlines)
# - Label pills must not overlap each other
# - Annotation boxes must be within image bounds


def detect_color_blobs(img_arr):
    # img_arr: HxWx3 uint8
    h, w, _ = img_arr.shape
    hsv = np.zeros_like(img_arr, dtype=np.float32)
    # convert to normalized RGB then to approximate hue
    rgb = img_arr.astype(np.float32) / 255.0
    r = rgb[:, :, 0]
    g = rgb[:, :, 1]
    b = rgb[:, :, 2]
    # simple red/orange mask heuristics
    red_mask = (r > 0.7) & (g < 0.5)
    orange_mask = (r > 0.75) & (g > 0.35) & (g < 0.85) & (b < 0.5)
    mask = red_mask | orange_mask
    return mask


def find_bboxes(mask):
    h, w = mask.shape
    visited = np.zeros_like(mask, dtype=bool)
    bboxes = []
    for y in range(h):
        for x in range(w):
            if mask[y, x] and not visited[y, x]:
                # flood fill
                stack = [(y, x)]
                visited[y, x] = True
                minx, miny, maxx, maxy = x, y, x, y
                while stack:
                    cy, cx = stack.pop()
                    if cx < minx: minx = cx
                    if cy < miny: miny = cy
                    if cx > maxx: maxx = cx
                    if cy > maxy: maxy = cy
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            ny, nx = cy + dy, cx + dx
                            if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not visited[ny, nx]:
                                visited[ny, nx] = True
                                stack.append((ny, nx))
                bboxes.append((minx, miny, maxx + 1, maxy + 1))
    return bboxes


def intersects(a, b):
    return not (a[2] <= b[0] or a[0] >= b[2] or a[3] <= b[1] or a[1] >= b[3])


def overlap_area(a, b):
    # a and b are (x0,y0,x1,y1)
    x0 = max(a[0], b[0])
    y0 = max(a[1], b[1])
    x1 = min(a[2], b[2])
    y1 = min(a[3], b[3])
    if x1 <= x0 or y1 <= y0:
        return 0
    return (x1 - x0) * (y1 - y0), (x1 - x0), (y1 - y0)


def classify_bboxes(bboxes, img_size):
    labels = []
    boxes = []
    h, w = img_size
    for bb in bboxes:
        x0, y0, x1, y1 = bb
        area = (x1 - x0) * (y1 - y0)
        # ignore tiny noise
        if area < 800:
            continue
        # classify: label pills are medium-sized; annotation boxes are large
        if area < 30000 and (x1 - x0) < 800:
            labels.append(bb)
        else:
            boxes.append(bb)
    return labels, boxes


def validate_image(path: Path):
    img = Image.open(path).convert('RGB')
    arr = np.array(img)
    mask = detect_color_blobs(arr)
    bboxes = find_bboxes(mask)
    labels, boxes = classify_bboxes(bboxes, arr.shape[:2])
    issues = []
    # check labels not in header (top 80px)
    for L in labels:
        if L[1] < 80:
            issues.append(f"label_too_high: {L}")
    # check label-label overlap
    for i in range(len(labels)):
        for j in range(i+1, len(labels)):
            if intersects(labels[i], labels[j]):
                issues.append(f"label_overlap: {labels[i]} vs {labels[j]}")
    # check label-box overlap with size-aware rule
    for L in labels:
        for B in boxes:
            if intersects(L, B):
                area, w_overlap, h_overlap = overlap_area(L, B)
                # if overlap is visually significant, report regardless of label size
                if area >= 36 or w_overlap >= 6 or h_overlap >= 6:
                    issues.append(f"label_overlaps_box: {L} vs {B} (overlap area={area}, w={w_overlap}, h={h_overlap})")
    # check boxes inside image bounds
    h, w = arr.shape[:2]
    for B in boxes:
        x0, y0, x1, y1 = B
        if x0 < 0 or y0 < 0 or x1 > w or y1 > h:
            issues.append(f"box_out_of_bounds: {B}")
    passed = len(issues) == 0
    return passed, issues, {'labels': labels, 'boxes': boxes}


def main():
    results = {}
    for p in sorted(OUT_DIR.glob('*.png')):
        passed, issues, meta = validate_image(p)
        results[p.name] = {'passed': passed, 'issues': issues, 'meta': meta}
        print(p.name, 'PASS' if passed else 'FAIL')
        if issues:
            for it in issues:
                print('  -', it)
    # summary
    fail_count = sum(1 for v in results.values() if not v['passed'])
    print('\nSummary: {} images failed'.format(fail_count))
    return 0

if __name__ == '__main__':
    main()
