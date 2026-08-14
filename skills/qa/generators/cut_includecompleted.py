# -*- coding: utf-8 -*-
"""The Include completed switch, turned on. A finished routine vanishes from the
list until this is flipped, and it goes back to off on every visit."""
import os
from PIL import Image

ROOT = r"C:\Users\Tzahi\OneDrive\שולחן העבודה\LEGAL-MIND-CLAUDE-DESKTOP-GUIDE\.github-live-repo\legal-mind-claude-guides"
D = os.path.join(ROOT, "skills", "qa", "chapter-scheduled-assets")

im = Image.open(os.path.join(D, "raw-280.png")).convert("RGB")
out = os.path.join(D, "cut-include-completed.png")
im.crop((700, 185, 1500, 290)).save(out)
print(out, Image.open(out).size)
