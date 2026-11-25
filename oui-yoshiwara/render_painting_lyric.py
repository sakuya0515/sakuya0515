import sys, math, subprocess, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC = sys.argv[1]
OUT = sys.argv[2]
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

# Camera keyframes: (t, cx, cy, view width) in source px
KEYS = [
    (0.0, 258, 372, 360),
    (8.0, 252, 366, 390),
    (14.0, 228, 330, 400),
    (20.5, 140, 290, 430),
    (27.0, 300, 210, 480),
    (33.5, 560, 330, 430),
    (41.0, 420, 270, 620),
    (47.0, 350, 247, 878),
    (DUR, 350, 247, 878),
]

def cam(t):
    for (t0, x0, y0, w0), (t1, x1, y1, w1) in zip(KEYS, KEYS[1:]):
        if t0 <= t <= t1:
            k = smooth(t0, t1, t)
            return x0 + (x1 - x0) * k, y0 + (y1 - y0) * k, w0 + (w1 - w0) * k
    return KEYS[-1][1:]

def light(t):
    lan = smooth(5.5, 10.0, t)            # lanterns appear out of darkness
    lat = 0.55 * smooth(19.0, 27.0, t)    # lattice interior light
    glob = smooth(41.5, 47.0, t)          # whole painting as it is
    dark = 0.02
    m = np.zeros((bh, bw), np.float32)
    for mk, seed in lantern_masks:
        m = np.maximum(m, mk * lan * flicker(t, seed))
    m = np.maximum(m, floor_mask * lan * flicker(t, 4.1) * 0.9)
    m = np.maximum(m, lattice_mask * lat)
    m = np.maximum(m, glob)
    img = B * (dark + (1 - dark) * m[..., None])
    bloom_amt = 0.55 * lan * (1 - 0.6 * glob) * flicker(t, 9.0)
    img = img + BLOOM * bloom_amt
    return np.clip(img, 0, 1)

# ---------- text ----------
TEXT_COL = (243, 230, 204)
def vtext_layer(lines, size, x_right, y_top, alpha, bold=False, gap=1.6, glow=True, color=TEXT_COL):
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    font = ImageFont.truetype(FONT_BOLD if bold else FONT_PATH, size, index=JPB if bold else JPI)
    d = ImageDraw.Draw(layer)
    for i, line in enumerate(lines):
        x = x_right - i * size * gap
        d.text((x, y_top), line, font=font, fill=color + (255,), direction='ttb', features=['vert'], anchor='mt')
    if glow:
        g = layer.filter(ImageFilter.GaussianBlur(size * 0.35))
        ga = np.asarray(g).astype(np.float32)
        ga[..., :3] = np.array([255, 190, 110], np.float32)
        ga[..., 3] *= 0.8
        g = Image.fromarray(ga.astype(np.uint8))
        layer = Image.alpha_composite(g, layer)
    a = np.asarray(layer).astype(np.float32)
    a[..., 3] *= alpha
    return Image.fromarray(a.astype(np.uint8))

def htext_layer(text, size, cx, cy, alpha, color=TEXT_COL, glow=True, bold=False, glow_rgb=(255, 170, 80), glow_r=0.3):
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    font = ImageFont.truetype(FONT_BOLD if bold else FONT_PATH, size, index=JPB if bold else JPI)
    d = ImageDraw.Draw(layer)
    d.text((cx, cy), text, font=font, fill=color + (255,), anchor='mm')
    if glow:
        g = layer.filter(ImageFilter.GaussianBlur(size * glow_r))
        ga = np.asarray(g).astype(np.float32)
        ga[..., :3] = np.array(glow_rgb, np.float32)
        ga[..., 3] = np.clip(ga[..., 3] * (3.0 if glow_rgb == (0, 0, 0) else 1.0), 0, 255)
        g = Image.fromarray(ga.astype(np.uint8))
        layer = Image.alpha_composite(g, layer)
    a = np.asarray(layer).astype(np.float32)
    a[..., 3] *= alpha
    return Image.fromarray(a.astype(np.uint8))

def env(t, a, b, fin=1.2, fout=1.2):
    if t < a or t > b: return 0.0
    return min(smooth(a, a + fin, t), 1 - smooth(b - fout, b, t))

# vertical lyric cues: (start, end, lines, size, x_right, y_top)
CUES = [
    (0.8, 7.2, ['この時代の浮世絵は', '夜を描いても', '昼のように明るい'], 54, 1180, 230),
    (8.0, 13.6, ['だけど', '応為の夜は'], 66, 1700, 200),
    (14.2, 19.8, ['ちゃんと　夜'], 84, 1680, 220),
    (20.6, 26.6, ['ちゃんと　暗い'], 84, 300, 200),
    (27.6, 34.6, ['そして', '提灯のあかり'], 66, 360, 190),
]
SIG = [(35.6, '応'), (36.6, '為'), (37.6, '栄')]

cache = {}
def cue_layer(i, alpha, drift):
    s, e, lines, size, xr, yt = CUES[i]
    key = (i, round(alpha, 2), int(drift))
    if key not in cache:
        cache.clear()
        cache[key] = vtext_layer(lines, size, xr, yt - drift, alpha)
    return cache[key]

def frame(t):
    img = light(t)
    cx, cy, vw = cam(t)
    vh = vw * H / W
    x0, y0 = (cx - vw / 2) * UP, (cy - vh / 2) * UP
    pil = Image.fromarray((img * 255).astype(np.uint8))
    sx = vw * UP / W
    out = pil.transform((W, H), Image.AFFINE, (sx, 0, x0, 0, sx, y0), resample=Image.BICUBIC, fillcolor=(0, 0, 0))
    # film grain + vignette
    arr = np.asarray(out).astype(np.float32)
    rng = np.random.default_rng(int(t * FPS))
    arr += rng.normal(0, 5.0, (H, W, 1)).astype(np.float32)
    arr *= VIG
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert('RGBA')
    for i, (s, e, *_r) in enumerate(CUES):
        a = env(t, s, e)
        if a > 0:
            drift = (t - s) * 6
            out = Image.alpha_composite(out, vtext_layer(CUES[i][2], CUES[i][3], CUES[i][4], CUES[i][5] - drift, a))
    # 応 為 栄
    for k, (ts, ch) in enumerate(SIG):
        a = env(t, ts, 41.5, 0.9, 1.5)
        if a > 0:
            out = Image.alpha_composite(out, htext_layer(ch, 150, W / 2 + (k - 1) * 230, H / 2 - 40, a, color=(255, 214, 150), bold=True))
    a = env(t, 38.6, 41.5, 0.9, 1.5)
    if a > 0:
        out = Image.alpha_composite(out, htext_layer('提灯に　隠された　名前', 40, W / 2, H / 2 + 120, a))
    a = env(t, 47.5, DUR - 0.2, 1.5, 2.5)
    if a > 0:
        out = Image.alpha_composite(out, htext_layer('葛飾応為「吉原格子先之図」', 44, W / 2, H - 70, a, glow_rgb=(0, 0, 0), glow_r=0.6))
    # fade out at the very end
    fo = 1 - smooth(DUR - 2.0, DUR, t)
    if fo < 1:
        arr = np.asarray(out.convert('RGB')).astype(np.float32) * fo
        return Image.fromarray(arr.astype(np.uint8))
    return out.convert('RGB')

gy, gx = np.mgrid[0:H, 0:W].astype(np.float32)
r = np.sqrt(((gx - W / 2) / (W / 2)) ** 2 + ((gy - H / 2) / (H / 2)) ** 2)
VIG = (1 - 0.35 * np.clip(r - 0.55, 0, 1) ** 1.5)[..., None].astype(np.float32)

if PREVIEW:
    times = [float(x) for x in sys.argv[4].split(',')]
    for t in times:
        frame(t).save(f'{OUT}_{t:05.1f}.jpg', quality=88)
    sys.exit(0)

proc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                         '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)
n = int(DUR * FPS)
for i in range(n):
    proc.stdin.write(frame(i / FPS).tobytes())
    if i % 150 == 0:
        print(i, '/', n, flush=True)
proc.stdin.close()
proc.wait()
print('done')
