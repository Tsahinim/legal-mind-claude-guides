# -*- coding: utf-8 -*-
"""The New routine arrow opened, showing Local above Cloud. The section tells the
reader to choose Local and until now showed only the closed button."""
import os
from PIL import Image

ROOT = r"C:\Users\Tzahi\OneDrive\שולחן העבודה\LEGAL-MIND-CLAUDE-DESKTOP-GUIDE\.github-live-repo\legal-mind-claude-guides"
D = os.path.join(ROOT, "skills", "qa", "chapter-scheduled-assets")

im = Image.open(os.path.join(D, "raw-286.png")).convert("RGB")
out = os.path.join(D, "cut-local-cloud.png")
im.crop((1300, 0, 1519, 150)).save(out)
print(out, Image.open(out).size)
