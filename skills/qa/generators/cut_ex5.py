# -*- coding: utf-8 -*-
"""Crops for exercise 5. The yellow note and the date row sit too close for both
to carry a badge in one frame, so they become two figures."""
import os
from PIL import Image

ROOT = r"C:\Users\Tzahi\OneDrive\שולחן העבודה\LEGAL-MIND-CLAUDE-DESKTOP-GUIDE\.github-live-repo\legal-mind-claude-guides"
D = os.path.join(ROOT, "skills", "qa", "ex5-assets")

def cut(src, box, name):
    im = Image.open(os.path.join(D, src)).convert("RGB")
    p = os.path.join(D, name)
    im.crop(box).save(p)
    print(name, Image.open(p).size)

cut("ex5-datefields.png", (0, 255, 1254, 420), "ex5-note.png")
cut("ex5-datefields.png", (0, 120, 1254, 225), "ex5-fields.png")
