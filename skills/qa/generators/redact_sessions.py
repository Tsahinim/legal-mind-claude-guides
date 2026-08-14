# -*- coding: utf-8 -*-
"""vs-19 shows the session list, and one row carries the name of an unrelated
personal project. Blur that row's title before the shot goes into a guide."""
import os
from PIL import Image, ImageFilter

ROOT = r"C:\Users\Tzahi\OneDrive\שולחן העבודה\LEGAL-MIND-CLAUDE-DESKTOP-GUIDE\.github-live-repo\legal-mind-claude-guides"
D = os.path.join(ROOT, "skills", "qa", "chapter-vscode-assets")

im = Image.open(os.path.join(D, "vs-19.png")).convert("RGB")
box = (0, 294, 350, 332)
im.paste(im.crop(box).filter(ImageFilter.GaussianBlur(9)), box)
out = os.path.join(D, "cut-sessions.png")
im.save(out)
print(out, im.size)
