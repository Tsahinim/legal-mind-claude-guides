# -*- coding: utf-8 -*-
"""cut-run-summary stops one line before the payoff. This is the part it cut off:
the thirteen items the run flagged, and what they actually were."""
import os
from PIL import Image

ROOT = r"C:\Users\Tzahi\OneDrive\שולחן העבודה\LEGAL-MIND-CLAUDE-DESKTOP-GUIDE\.github-live-repo\legal-mind-claude-guides"
D = os.path.join(ROOT, "skills", "qa", "chapter-scheduled-assets")

im = Image.open(os.path.join(D, "task-shot-04.png")).convert("RGB")
out = os.path.join(D, "cut-flagged.png")
im.crop((680, 555, 1645, 862)).save(out)
print(out, Image.open(out).size)
