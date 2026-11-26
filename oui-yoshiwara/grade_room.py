"""Bring a crisp ink line image closer to image 1 (soft sepia charcoal).
usage: python3 grade_room.py in.png out.png
- lifts pure black lines to dark sepia
- tints everything to the sepia of image 1, keeps the warm lantern light
- softens hard edges very slightly
"""
import sys
import numpy as np
from PIL import Image, ImageFilter

src = Image.open(sys.argv[1]).convert('RGB')
soft = src.filter(ImageFilter.GaussianBlur(1.2))
A = np.asarray(src).astype(np.float32) / 255
S = np.asarray(soft).astype(np.float32) / 255
A = A * 0.55 + S * 0.45                      # soften crisp edges

L = (A * np.array([0.3, 0.59, 0.11])).sum(axis=2, keepdims=True)
dark = np.array([62, 48, 38]) / 255            # darkest charcoal, not pure black
paper = np.array([238, 228, 210]) / 255        # cream paper
sepia = dark + (paper - dark) * L

# warm lantern light: orange and bright -> keep original colour
r, g, b = A[..., 0], A[..., 1], A[..., 2]
warm = np.clip(((r - b) - 0.12) * 5, 0, 1)[..., None]
warm = np.asarray(Image.fromarray((warm[..., 0] * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6))).astype(np.float32)[..., None] / 255

out = sepia * 0.8 + A * 0.2
out = out * (1 - warm) + A * warm
Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)).save(sys.argv[2])
