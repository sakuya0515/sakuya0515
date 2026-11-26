"""Paint out a small spot (e.g. a leftover hair ornament) by cloning nearby strokes over it.
usage: python3 remove_spot.py in.png out.png x y r dx dy [x y r dx dy ...]
(dx, dy) = where to take the replacement strokes from, relative to the spot.
"""
import sys
import cv2
import numpy as np

img = cv2.imread(sys.argv[1]).astype(np.float32)
out = img.copy()
v = list(map(int, sys.argv[3:]))
h, w = img.shape[:2]
for x, y, r, dx, dy in zip(v[0::5], v[1::5], v[2::5], v[3::5], v[4::5]):
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    shifted = cv2.warpAffine(img, M, (w, h), borderMode=cv2.BORDER_REFLECT)  # pixel (x,y) <- (x-dx, y-dy)
    mask = np.zeros((h, w), np.float32)
    cv2.circle(mask, (x, y), r, 1.0, -1)
    mask = cv2.GaussianBlur(mask, (0, 0), r * 0.35)[..., None]
    out = out * (1 - mask) + shifted * mask
cv2.imwrite(sys.argv[2], np.clip(out, 0, 255).astype(np.uint8))
