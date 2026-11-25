"""S2b: walking past the lattice and looking in (layered parallax).

usage: python3 render_lattice_walk.py <room_image> <out.mp4> [preview t1,t2,...]

- back layer : the room image (no lattice), moves slowly
- front layer: dark lattice bars (charcoal silhouettes), move about 3x faster
"""
import sys, subprocess
import numpy as np
from PIL import Image, ImageFilter

SRC, OUT = sys.argv[1], sys.argv[2]
PREVIEW = len(sys.argv) > 3 and sys.argv[3] == 'preview'

W, H, FPS, DUR = 1920, 1080, 30, 8.0
BG_SCALE = 1.16        # room image is enlarged so it can slide
PARALLAX = 3.0         # bars move this many times faster than the room
BAR_PERIOD = 240       # px between bars (output px)
BAR_WIDTH = 92
BEAM_TOP = 70          # horizontal beam at the top
SILL_Y = 930           # sill at the bottom
FG_BLUR = 4            # foreground slightly out of focus
BAR_RGB = np.array([30, 22, 16], np.float32)

room = Image.open(SRC).convert('RGB')
rw, rh = room.size
s = max(W * BG_SCALE / rw, H * BG_SCALE / rh)
room = room.resize((int(rw * s), int(rh * s)), Image.LANCZOS)
R = np.asarray(room).astype(np.float32)
RH, RW = R.shape[:2]
bg_travel = RW - W
fg_travel = bg_travel * PARALLAX
y_off = (RH - H) // 2

rng = np.random.default_rng(7)
# lattice strip, wide enough for the whole travel; drawn once
LW = int(W + fg_travel + BAR_PERIOD * 2)
yy = np.arange(H, dtype=np.float32)[:, None]
xx = np.arange(LW, dtype=np.float32)[None, :]
# rough charcoal edges: per-row wobble of each bar edge
wob = np.cumsum(rng.normal(0, 0.6, (H, 1)), axis=0)
wob = (wob - wob.mean()) * 0.25
pos = np.mod(xx + wob, BAR_PERIOD)
bar = ((pos > (BAR_PERIOD - BAR_WIDTH) / 2) & (pos < (BAR_PERIOD + BAR_WIDTH) / 2)).astype(np.float32)
bar = np.maximum(bar, (yy < BEAM_TOP).astype(np.float32))
bar = np.maximum(bar, (yy > SILL_Y).astype(np.float32))
grain = rng.normal(0, 1, (H, LW)).astype(np.float32)
mask_img = Image.fromarray((bar * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(FG_BLUR))
MASK = np.asarray(mask_img).astype(np.float32) / 255.0
# charcoal texture inside the bars
TEX = BAR_RGB[None, None, :] * (1 + 0.25 * grain[..., None])

gy, gx = np.mgrid[0:H, 0:W].astype(np.float32)
r = np.sqrt(((gx - W / 2) / (W / 2)) ** 2 + ((gy - H / 2) / (H / 2)) ** 2)
VIG = (1 - 0.4 * np.clip(r - 0.5, 0, 1) ** 1.4)[..., None].astype(np.float32)

def ease(u):
    # constant walking speed, with soft start and stop
    a = 0.12
    if u < a: return 0.5 * u * u / a / (1 - a)
    if u > 1 - a: return 1 - 0.5 * (1 - u) ** 2 / a / (1 - a)
    return (u - a / 2) / (1 - a)

def frame(t):
    k = ease(t / DUR)
    bx = int(round(k * bg_travel))
    fx = int(round(k * fg_travel))
    bg = R[y_off:y_off + H, bx:bx + W]
    m = MASK[:, fx:fx + W, None]
    tex = TEX[:, fx:fx + W]
    # light from the room wraps slightly around the bar edges
    glow = np.asarray(Image.fromarray(bg.astype(np.uint8)).filter(ImageFilter.GaussianBlur(40))).astype(np.float32)
    edge = np.clip(m * (1 - m) * 4, 0, 1)
    img = bg * (1 - m) + tex * m + glow * edge * np.array([0.22, 0.15, 0.08], np.float32)
    img = img * VIG + np.random.default_rng(int(t * FPS)).normal(0, 4, (H, W, 1))
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))

if PREVIEW:
    for t in [float(x) for x in sys.argv[4].split(',')]:
        frame(t).save(f'{OUT}_{t:04.1f}.jpg', quality=88)
    sys.exit(0)

p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                      '-c:v', 'libx264', '-preset', 'slow', '-crf', '24', '-tune', 'grain', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', OUT],
                     stdin=subprocess.PIPE)
for i in range(int(DUR * FPS)):
    p.stdin.write(frame(i / FPS).tobytes())
p.stdin.close(); p.wait()
print('done')
