# -*- coding: utf-8 -*-
"""The right-click menu, cut to the part the reader needs: Open Preview at the top."""
import os
from PIL import Image

ROOT = r"C:\Users\Tzahi\OneDrive\שולחן העבודה\LEGAL-MIND-CLAUDE-DESKTOP-GUIDE\.github-live-repo\legal-mind-claude-guides"
D = os.path.join(ROOT, "skills", "qa", "md-preview-assets")

im = Image.open(os.path.join(D, "md-menu.png")).convert("RGB")
out = os.path.join(D, "cut-md-menu.png")
im.crop((155, 225, 552, 560)).save(out)
print(out, Image.open(out).size)
