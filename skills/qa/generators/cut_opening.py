# -*- coding: utf-8 -*-
"""Crops for the opening chapter. A full 1919px window scaled to 650 leaves no
room for a marker badge anywhere near a corner, so anything that needs marking
gets cut out of the window first."""
import os
from PIL import Image

ROOT = r"C:\Users\Tzahi\OneDrive\שולחן העבודה\LEGAL-MIND-CLAUDE-DESKTOP-GUIDE\.github-live-repo\legal-mind-claude-guides"
D = os.path.join(ROOT, "skills", "qa", "chapter-opening-assets")

def cut(src, box, name):
    im = Image.open(os.path.join(D, src)).convert("RGB")
    out = os.path.join(D, name)
    im.crop(box).save(out)
    print(name, Image.open(out).size)

# the Claude panel on its own, so New session can carry a marker
cut("open-newsession.png", (55, 40, 430, 320), "cut-newsession.png")
