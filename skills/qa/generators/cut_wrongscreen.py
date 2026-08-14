# -*- coding: utf-8 -*-
"""The Scheduled tasks page - the screen the warning says is the wrong one."""
import os
from PIL import Image

ROOT = r"C:\Users\Tzahi\OneDrive\שולחן העבודה\LEGAL-MIND-CLAUDE-DESKTOP-GUIDE\.github-live-repo\legal-mind-claude-guides"
D = os.path.join(ROOT, "skills", "qa", "chapter-scheduled-assets")

im = Image.open(os.path.join(D, "raw-277.png")).convert("RGB")
out = os.path.join(D, "cut-wrong-screen.png")
im.crop((20, 30, 1080, 555)).save(out)
print(out, Image.open(out).size)
