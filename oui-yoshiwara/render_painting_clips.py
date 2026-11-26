"""P1-P3: clips from the real painting, no text.
usage: python3 render_painting_clips.py <painting> <outdir> [preview]
"""
import sys, math, subprocess, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC = sys.argv[1]
OUTDIR = sys.argv[2]
PREVIEW = len(sys.argv) > 3 and sys.argv[3] == 'preview'

W, H, FPS = 1920, 1080, 30
DUR = 53.0
UP = 2  # work resolution multiplier over 700px source

FONT_PATH = '/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc'
FONT_BOLD = '/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc'

def jp_index(path):
    for i in range(10):
        try:
            f = ImageFont.truetype(path, 20, index=i)
        except Exception:
            break
        if 'JP' in ' '.join(f.getname()):
            return i
    return 0
JPI = jp_index(FONT_PATH)
JPB = jp_index(FONT_BOLD)

src = Image.open(SRC).convert('RGB')
sw, sh = src.size
base = src.resize((sw * UP, sh * UP), Image.LANCZOS)
B = np.asarray(base).astype(np.float32) / 255.0
bh, bw = B.shape[:2]
yy, xx = np.mgrid[0:bh, 0:bw].astype(np.float32)

def gauss(cx, cy, r):
    cx, cy, r = cx * UP, cy * UP, r * UP
    return np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r * r)))

def soft_rect(x0, y0, x1, y1, feather):
    x0, y0, x1, y1, f = [v * UP for v in (x0, y0, x1, y1, feather)]
    ax = np.clip(np.minimum(xx - x0, x1 - xx) / f, 0, 1)
    ay = np.clip(np.minimum(yy - y0, y1 - yy) / f, 0, 1)
    return (ax * ay).astype(np.float32)

# Lantern light sources (source-pixel coords, 700x494)
LANTERNS = [
    # (cx, cy, core r, spill r, seed)
    (226, 323, 16, 46, 1.3),   # lantern hanging from the dark figure, centre-left
    (255, 390, 18, 55, 2.7),   # kamuro's lantern
    (578, 312, 26, 80, 4.1),   # lantern on the right
]
FLOOR = [(255, 430, 70), (585, 420, 90)]  # light pools on the ground

lantern_masks = []
for cx, cy, rc, rs, seed in LANTERNS:
    lantern_masks.append((np.maximum(gauss(cx, cy, rc), 0.75 * gauss(cx, cy, rs)), seed))
floor_mask = np.maximum.reduce([gauss(x, y, r) for x, y, r in FLOOR]) * 0.85
lattice_mask = np.maximum(soft_rect(0, 0, 440, 250, 30), soft_rect(505, 20, 700, 300, 30))

# warm bloom source: bright parts of lanterns only
lum = B.mean(axis=2)
bloom_src = np.zeros_like(B)
for m, _ in lantern_masks:
    bloom_src += B * (m[..., None] > 0.5) * (lum[..., None] > 0.55)
bloom_img = Image.fromarray((np.clip(bloom_src, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(18 * UP))
BLOOM = np.asarray(bloom_img).astype(np.float32) / 255.0 * np.array([1.0, 0.72, 0.38], np.float32)

def smooth(a, b, t):
    if t <= a: return 0.0
    if t >= b: return 1.0
    x = (t - a) / (b - a)
    return x * x * (3 - 2 * x)

def flicker(t, seed):
    return 0.88 + 0.07 * math.sin(t * 2.3 + seed) + 0.04 * math.sin(t * 5.1 + seed * 2.1) + 0.02 * math.sin(t * 11.7 + seed * 3.3)


# ---------- clips (no text) ----------
def lit(t, lan=(1, 1, 1), floor=1.0, lat=0.0, glob=0.0, dark=0.02):
    m = np.zeros((bh, bw), np.float32)
    for (mk, seed), a in zip(lantern_masks, lan):
        m = np.maximum(m, mk * a * flicker(t, seed))
    m = np.maximum(m, floor_mask * floor * flicker(t, 4.1) * 0.9)
    m = np.maximum(m, lattice_mask * lat)
    m = np.maximum(m, glob)
    img = B * (dark + (1 - dark) * m[..., None])
    img = img + BLOOM * 0.55 * max(lan) * (1 - 0.6 * glob) * flicker(t, 9.0)
    return np.clip(img, 0, 1)

def lerp(a, b, k): return a + (b - a) * k

CLIPS = {
    # P1: the lattice and the dark figures, slow move right to left, interior light grows
    'P1_lattice': (8.0,
        lambda t: (lerp(330, 220, smooth(0, 8, t)), 205, 430),
        lambda t: lit(t, lat=lerp(0.55, 1.0, smooth(0, 7, t)), glob=0.32)),
    # P2: kamuro lantern held at lower centre (same place as the candle flame in S5), slow push-in
    'P2_lantern': (8.0,
        lambda t: (255, lerp(365, 370, smooth(0, 8, t)), lerp(300, 240, smooth(0, 8, t))),
        lambda t: lit(t, glob=0.18, lat=0.25)),
    # P3: darkness; lanterns light one by one (kamuro lantern first, at centre), lattice, then the whole picture
    'P3_reveal': (14.0,
        lambda t: (lerp(255, 350, smooth(0.5, 12.5, t)), lerp(375, 247, smooth(0.5, 12.5, t)), lerp(420, 878, smooth(0.5, 12.5, t))),
        lambda t: lit(t, lan=(smooth(2.2, 3.4, t), smooth(0.6, 1.8, t), smooth(3.8, 5.0, t)),
                      floor=smooth(0.6, 5.0, t), lat=0.8 * smooth(5.5, 8.5, t), glob=smooth(8.0, 12.0, t))),
}

def render_frame(camf, lightf, t):
    img = lightf(t)
    cx, cy, vw = camf(t)
    vh = vw * H / W
    x0, y0 = (cx - vw / 2) * UP, (cy - vh / 2) * UP
    pil = Image.fromarray((img * 255).astype(np.uint8))
    sx = vw * UP / W
    out = pil.transform((W, H), Image.AFFINE, (sx, 0, x0, 0, sx, y0), resample=Image.BICUBIC, fillcolor=(0, 0, 0))
    arr = np.asarray(out).astype(np.float32)
    arr += np.random.default_rng(int(t * FPS)).normal(0, 5.0, (H, W, 1)).astype(np.float32)
    arr *= VIG
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

gy, gx = np.mgrid[0:H, 0:W].astype(np.float32)
r = np.sqrt(((gx - W / 2) / (W / 2)) ** 2 + ((gy - H / 2) / (H / 2)) ** 2)
VIG = (1 - 0.35 * np.clip(r - 0.55, 0, 1) ** 1.5)[..., None].astype(np.float32)

os.makedirs(OUTDIR, exist_ok=True)
for name, (dur, camf, lightf) in CLIPS.items():
    if PREVIEW:
        for t in (0.5, dur / 2, dur - 0.1):
            render_frame(camf, lightf, t).save(f'{OUTDIR}/{name}_{t:04.1f}.jpg', quality=85)
        continue
    out = f'{OUTDIR}/{name}.mp4'
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'slow', '-crf', '24', '-tune', 'grain', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        p.stdin.write(render_frame(camf, lightf, i / FPS).tobytes())
    p.stdin.close(); p.wait()
    print('done', name, flush=True)
