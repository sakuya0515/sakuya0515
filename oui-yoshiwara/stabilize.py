"""Undo camera drift in a generated 'locked camera' video: align every frame to the first one.
usage: python3 stabilize.py in.mp4 out.mp4
Moving people are rejected as outliers; the wall, floor and lanterns hold the frame.
"""
import sys
import cv2
import numpy as np

cap = cv2.VideoCapture(sys.argv[1])
fps = cap.get(cv2.CAP_PROP_FPS)
ok, f0 = cap.read()
h, w = f0.shape[:2]
g0 = cv2.cvtColor(f0, cv2.COLOR_BGR2GRAY)
orb = cv2.ORB_create(4000)
k0, d0 = orb.detectAndCompute(g0, None)
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
out = cv2.VideoWriter(sys.argv[2], cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
out.write(f0)
i = 0
last = np.eye(2, 3, dtype=np.float64)
while True:
    ok, f = cap.read()
    if not ok:
        break
    i += 1
    g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
    k, d = orb.detectAndCompute(g, None)
    M = None
    if d is not None:
        m = sorted(bf.match(d, d0), key=lambda x: x.distance)[:1500]
        if len(m) > 30:
            src = np.float32([k[x.queryIdx].pt for x in m])
            dst = np.float32([k0[x.trainIdx].pt for x in m])
            M, inl = cv2.estimateAffinePartial2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=2.0)
    if M is None:
        M = last
    last = M
    if i % 24 == 0:
        s = np.sqrt(M[0, 0] ** 2 + M[1, 0] ** 2)
        print(f't={i / fps:4.1f}s  scale_fix={s:.4f}  shift=({M[0, 2]:.1f},{M[1, 2]:.1f})', flush=True)
    out.write(cv2.warpAffine(f, M, (w, h), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT))
out.release()
