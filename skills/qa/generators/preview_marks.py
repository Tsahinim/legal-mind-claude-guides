# -*- coding: utf-8 -*-
"""Draws the marker boxes on a source screenshot exactly where the page will put
them, so the eye check (stage ב of the marker standard) can happen before deploy."""
import os, re, sys
from PIL import Image, ImageDraw
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = r"C:\Users\Tzahi\OneDrive\שולחן העבודה\LEGAL-MIND-CLAUDE-DESKTOP-GUIDE\.github-live-repo\legal-mind-claude-guides"
A = os.path.join(ROOT, "skills", "qa", "chapter-scheduled-assets")
B = os.path.join(ROOT, "skills", "qa", "chapter-vscode-assets")
C = os.path.join(ROOT, "skills", "qa", "chapter-opening-assets")
D = os.path.join(ROOT, "skills", "qa", "ex4-assets")
E = os.path.join(ROOT, "skills", "qa", "ex5-assets")
F = os.path.join(ROOT, "skills", "qa", "ex2-assets")
G = os.path.join(ROOT, "skills", "qa", "md-preview-assets")
OUT = os.path.dirname(os.path.abspath(__file__))

def _path(n):
    for folder in (A, B, C, D, E, F, G):
        for name in ("raw-%s.png" % n, "%s.png" % n):
            p = os.path.join(folder, name)
            if os.path.exists(p):
                return p
    raise FileNotFoundError(n)

def pct(style, key):
    m = re.search(key + r':([\d.]+)%', style)
    return float(m.group(1)) if m else 0.0

def draw(name, targets):
    im = Image.open(_path(name)).convert("RGB")
    W, H = im.size
    d = ImageDraw.Draw(im)
    # the page scales the figure down to fit; the badge classes are chosen on
    # those rendered dimensions, so mirror them here or the preview lies
    CAP_W, CAP_H = 650, 520
    box_w = min(W, CAP_W)
    if H * box_w / W > CAP_H:
        box_w = CAP_H * W / H
    box_h = H * box_w / W
    # the badge is a fixed 26px on the rendered figure, so on a figure that was
    # scaled down it covers proportionally more. draw it at that true size or the
    # preview flatters every marker on a wide screenshot.
    scale = box_w / W
    B = 26.0 / scale
    R = B / 2
    for style, badge_cls, num in targets:
        if not badge_cls:
            lft, wid = pct(style, 'left'), pct(style, 'width')
            if box_h < 140:
                badge_cls = 'badge-inside-left' if wid * box_w / 100 >= 34 else 'badge-outside-left'
            elif wid <= 16:
                badge_cls = 'badge-right' if lft < 8 else 'badge-outside-left'
            elif lft < 4:
                badge_cls = 'badge-inside-left'
        x = pct(style, 'left') / 100 * W
        y = pct(style, 'top') / 100 * H
        w = pct(style, 'width') / 100 * W
        h = pct(style, 'height') / 100 * H
        d.rectangle([x, y, x + w, y + h], outline=(220, 40, 60), width=3)
        # badge centre, mirroring the css transforms in site.css
        if badge_cls == 'badge-inside-left':
            bx, by = x + 7 / scale + R, y + h / 2
        elif badge_cls == 'badge-outside-left':
            bx, by = x - B * 1.15 + R, y + h / 2
        elif badge_cls == 'badge-right':
            bx, by = x + w + B * 0.45 - R, y - B * 0.45 + R
        elif badge_cls == 'badge-above':
            bx, by = x + w / 2, y - B * 1.18 + R
        elif badge_cls == 'badge-below':
            bx, by = x + w / 2, y + h + B * 0.18 + R
        else:
            bx, by = x - B * 0.45 + R, y - B * 0.45 + R
        d.ellipse([bx - R, by - R, bx + R, by + R], fill=(220, 40, 60), outline=(255, 255, 255), width=2)
        d.text((bx - 3, by - 6), str(num), fill=(255, 255, 255))
        if bx - R < -1 or bx + R > W + 1 or by - R < -1 or by + R > H + 1:
            print('   !! badge %s leaves the image' % num)
    p = os.path.join(OUT, "preview-%s.png" % name)
    im.save(p)
    print(p, im.size)

if __name__ == "__main__":
    draw("cut-md-menu", [("left:3%;top:3.6%;width:51.1%;height:9%", "badge-right", 1),
                         ("left:3%;top:31.3%;width:51.1%;height:9%", "badge-right", 2)])
    draw("ex2-04", [("left:2.7%;top:14.1%;width:29.6%;height:34.7%", "badge-above", 1),
                    ("left:5.8%;top:52.8%;width:92.1%;height:8%", "badge-outside-left", 2)])
    draw("ex5-result", [("left:69.6%;top:50.1%;width:28%;height:11.1%", "badge-outside-left", 1),
                        ("left:75.2%;top:88.7%;width:23.3%;height:7.8%", "badge-outside-left", 2)])
    draw("ex5-daycount", [("left:59%;top:22.3%;width:6%;height:14.2%", "badge-outside-left", 1)])
    draw("cut-newsession", [("left:4.3%;top:20.7%;width:42.4%;height:11.4%", "badge-right", 1)])
    draw("open-explorer-icon", [("left:1.8%;top:12.5%;width:9.1%;height:11.4%", "badge-below", 1)])
    draw("cut-install-popup", [("left:93.1%;top:3.8%;width:5.4%;height:22.9%", "badge-below", 1),
                               ("left:53.8%;top:61%;width:11%;height:32.4%", "badge-outside-left", 2)])
    draw("cut-include-completed", [("left:52.8%;top:14.3%;width:5.5%;height:28.6%", "badge-below", 1)])
    draw("cut-flagged", [("left:80.6%;top:1.3%;width:17%;height:11.1%", "badge-outside-left", 1),
                         ("left:38.9%;top:48.2%;width:60.6%;height:9.4%", "badge-outside-left", 2)])
    draw("cut-wrong-screen", [("left:40.1%;top:83.4%;width:20%;height:6.1%", "badge-below", 1)])
    draw("cut-ocr-lines", [("left:0.5%;top:34.5%;width:98.8%;height:12.1%", "badge-above", 1),
                           ("left:0.5%;top:66.8%;width:33.5%;height:11.6%", "badge-below", 2)])
    draw("cut-local-cloud", [("left:22.8%;top:37.3%;width:68.5%;height:20%", "", 1)])
    draw("cut-grey-create", [("left:1.6%;top:17.9%;width:15.5%;height:12.2%", "", 1),
                             ("left:88.6%;top:4.1%;width:10.2%;height:10.6%", "", 2),
                             ("left:90.6%;top:84.1%;width:9%;height:14.2%", "badge-above", 3)])
    draw("cut-activitybar", [("left:14.3%;top:49.5%;width:71.4%;height:6.4%", "badge-below", 1)])
    draw("cut-sessions", [("left:0.6%;top:44.2%;width:86.7%;height:12.4%", "", 1),
                          ("left:0.6%;top:70.8%;width:86.7%;height:26.5%", "", 2)])
    draw("vs-02", [("left:14%;top:32.7%;width:85%;height:26.3%", "", 1),
                   ("left:14%;top:60.2%;width:85%;height:31.3%", "badge-below", 2)])
    draw("vs-19", [("left:0.6%;top:44.2%;width:86.7%;height:12.4%", "", 1),
                   ("left:0.6%;top:70.8%;width:86.7%;height:26.5%", "", 2)])
    draw("vs-01", [("left:2.8%;top:78.2%;width:94%;height:7.7%", "badge-right", 1)])

