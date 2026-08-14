# -*- coding: utf-8 -*-
"""The bottom of the routine form while the folder is still unchosen, so the
reader can see the grey Create button the warning talks about."""
import os
from PIL import Image

ROOT = r"C:\Users\Tzahi\OneDrive\שולחן העבודה\LEGAL-MIND-CLAUDE-DESKTOP-GUIDE\.github-live-repo\legal-mind-claude-guides"
D = os.path.join(ROOT, "skills", "qa", "chapter-scheduled-assets")

im = Image.open(os.path.join(D, "raw-290.png")).convert("RGB")
out = os.path.join(D, "cut-grey-create.png")
im.crop((320, 774, 1200, 1020)).save(out)
print(out, Image.open(out).size)
