"""Lay vertical lattice shadows over the lit side of a face (S3).
usage: python3 lattice_shadow.py in.png out.png [shift_px]
Shadows fall only where the picture is lit (bright areas), stronger toward the light side (right).
"""
import sys
import numpy as np
from PIL import Image, ImageFilter

src = Image.open(sys.argv[1]).convert('RGB')
shift = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
A = np.asarray(src).astype(np.float32) / 255
h, w = A.shape[:2]
x = np.arange(w, dtype=np.float32)[None, :]
period, bar = w * 0.085, w * 0.032               # bar spacing and width, relative to image width
pos = np.mod(x + shift, period)
band = ((pos > (period - bar) / 2) & (pos < (period + bar) / 2)).astype(np.float32)
band = np.repeat(band, h, axis=0)
band = np.asarray(Image.fromarray((band * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(w * 0.006))).astype(np.float32) / 255
L = A.mean(axis=2)
lit = np.clip((L - 0.35) / 0.35, 0, 1)            # only where light actually falls
side = np.clip((x - w * 0.35) / (w * 0.35), 0, 1)  # light comes from the right
side = side * np.clip((w * 0.84 - x) / (w * 0.03), 0, 1)  # not on the lattice itself
shadow = band * lit * side * 0.45
out = A * (1 - shadow[..., None] * np.array([1.0, 1.05, 1.15]))  # shadows a little cooler than the warm light
Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)).save(sys.argv[2])
