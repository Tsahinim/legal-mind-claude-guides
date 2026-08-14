# -*- coding: utf-8 -*-
"""The icon ribbon on the left edge, cut out of vs-02 at native size. The reader
is told to click the Claude asterisk there, and until now had no picture of it."""
import os
from PIL import Image

ROOT = r"C:\Users\Tzahi\OneDrive\שולחן העבודה\LEGAL-MIND-CLAUDE-DESKTOP-GUIDE\.github-live-repo\legal-mind-claude-guides"
D = os.path.join(ROOT, "skills", "qa", "chapter-vscode-assets")

im = Image.open(os.path.join(D, "vs-02.png")).convert("RGB")
out = os.path.join(D, "cut-activitybar.png")
im.crop((0, 0, 56, 517)).save(out)
print(out, Image.open(out).size)
