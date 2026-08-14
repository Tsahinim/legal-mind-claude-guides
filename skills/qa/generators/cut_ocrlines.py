# -*- coding: utf-8 -*-
"""The two lines the exercise text quotes in Hebrew, cut out of the real run so
nothing but the message text is in frame - no interface, nothing to mis-attribute."""
import os
from PIL import Image

ROOT = r"C:\Users\Tzahi\OneDrive\שולחן העבודה\LEGAL-MIND-CLAUDE-DESKTOP-GUIDE\.github-live-repo\legal-mind-claude-guides"
D = os.path.join(ROOT, "skills", "qa", "chapter-scheduled-assets")

im = Image.open(os.path.join(D, "task-shot-03.png")).convert("RGB")
out = os.path.join(D, "cut-ocr-lines.png")
im.crop((645, 598, 1585, 830)).save(out)
print(out, Image.open(out).size)
