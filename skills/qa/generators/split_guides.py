# -*- coding: utf-8 -*-
"""Takes the single working page and emits the published series: a hub and three
guides, laid out like the Skills series - top button back to the hub, a chapter
rail that marks where the reader is, and prev/next at the bottom."""
import os, re, shutil, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = r"C:\Users\Tzahi\OneDrive\שולחן העבודה\LEGAL-MIND-CLAUDE-DESKTOP-GUIDE\.github-live-repo\legal-mind-claude-guides"
SRC = os.path.join(ROOT, "claude-code", "sequel-preview", "index.html")
OUT = os.path.join(ROOT, "claude-code", "sequel")
NL = chr(10)

SERIES = "מדריך ההמשך על <bdi dir=\"ltr\">Claude Code</bdi> לעורכי דין"
SERIES_PLAIN = "מדריך ההמשך על Claude Code לעורכי דין"

GUIDES = [
    dict(dir="guide-1", num=1, ids=["start", "firstopen", "panic"],
         title="להרגיש בבית בסביבה",
         sub="לפני שנוגעים בתרגיל אחד: מה לוקחים מהמדריך למתחילים, מה קורה ברגע שפותחים תיקייה, ולמה כמעט כל מה שנראה כמו תקלה הוא לא.",
         learn="איך נראה המסך מיד אחרי שפותחים תיקייה ומה עושים בו לפי הסדר, ולמה חלונות קופצים, חלוניות שיחה זרות ושיחות שנעלמו הם התנהגות רגילה ולא תקלה.",
         end="סביבת עבודה שאתם מרגישים בה בבית, ופרק שאפשר לחזור אליו בכל פעם שמשהו נראה מוזר.",
         time="כ-20 דקות קריאה", need="למי שסיים את המדריך למתחילים. אין צורך בידע טכני"),
    dict(dir="guide-2", num=2, ids=["download", "ex1", "ex2", "ex3", "ex4", "ex5", "why"],
         title="חמישה תרגילים על תיק אמיתי",
         sub="תיקיית תרגול אחת, וחמישה תרגילים שכל אחד מהם מראה משהו שלא ראיתם קודם. הכול מוכן, אתם מעתיקים ולוחצים.",
         learn="לתייק ארבעים מסמכים סרוקים, לאתר מועדים בתשעת אלפים שורות פרוטוקול, לחזור לאחור ולבטל, לבקש ממנו לבדוק את עצמו, ולבנות כלי חישוב שעובד.",
         end="חמישה תוצרים בתיקייה שלכם, וידיעה מה הכלי הזה באמת יודע לעשות.",
         time="כשעה וחצי, בקצב שלכם", need="דורש את מדריך 1"),
    dict(dir="guide-3", num=3, ids=["open", "local", "form", "run", "result", "truth"],
         title="לתת לקלוד קוד לעבוד גם כשאתם לא מול המחשב",
         sub="מגדירים משימה אחת, פעם אחת, והיא עוברת על תיקיית התיק גם כשאתם לא ליד המחשב ומשאירה לכם קובץ מוכן.",
         learn="איפה נמצא המסך הנכון ולמה יש שניים שנראים דומים, איך ממלאים את הטופס, ומה חייבים לדעת לפני שסומכים על משימה שרצה בלעדיכם.",
         end="משימה פעילה על תיק, ותוצר שמופק בלי שנגעתם.",
         time="כ-30 דקות", need="דורש את מדריך 1"),
]

H = open(SRC, encoding='utf-8').read()

head = H[:H.index('<body>')]
scripts = H[H.index('<script>'):]
sections = {m.group(1): m.group(0) for m in
            re.finditer(r'<section class="guide-section" id="([a-z0-9]+)">.*?</section>', H, re.S)}

os.makedirs(OUT, exist_ok=True)

def page(g, idx):
    body = [sections[i] for i in g["ids"] if i in sections]
    missing = [i for i in g["ids"] if i not in sections]
    assert not missing, "sections missing: %s" % missing

    # chapter rail, built from this guide's own sections
    rows = []
    for n, sid in enumerate([i for i in g["ids"] if i in sections], 1):
        h2 = re.search(r'<h2>(.*?)</h2>', sections[sid], re.S).group(1).strip()
        rows.append('<li><a href="#%s"><span>%02d</span>%s</a></li>' % (sid, n, h2))
    rail = NL.join(rows)

    # sections renumbered inside this guide
    joined = NL + NL.join(body) + NL
    c = [0]
    def renum(m):
        c[0] += 1
        return '<span class="section-number">%02d</span>' % c[0]
    joined = re.sub(r'<span class="section-number">\d+</span>', renum, joined)
    joined = joined.replace('src="../assets/', 'src="../../assets/')
    joined = joined.replace('href="../assets/', 'href="../../assets/')
    # one level deeper than the working page, so cross-series links move too
    joined = joined.replace('href="../../skills/', 'href="../../../skills/')

    prev_next = []
    if idx > 0:
        p = GUIDES[idx - 1]
        prev_next.append('<a class="button" href="../%s/index.html">המדריך הקודם: %s</a>' % (p["dir"], p["title"]))
    prev_next.append('<a class="button" href="../index.html">מרכז המדריכים</a>')
    if idx < len(GUIDES) - 1:
        n = GUIDES[idx + 1]
        prev_next.append('<a class="button primary" href="../%s/index.html">המדריך הבא: %s</a>' % (n["dir"], n["title"]))

    hd = head.replace('href="../assets/site.css', 'href="../../assets/site.css')
    hd = re.sub(r'<title>.*?</title>',
                '<title>%s · מדריך %d: %s | Legal Mind</title>' % (SERIES_PLAIN, g["num"], g["title"]), hd, flags=re.S)
    hd = re.sub(r'<meta name="description" content="[^"]*">',
                '<meta name="description" content="%s">' % g["sub"], hd)

    out = [hd, '<body>', '',
           '<a class="skip" href="#main">דילוג לתוכן</a>',
           '<nav class="backbar"><a href="../index.html">חזרה למרכז המדריכים של ההמשך</a></nav>', '',
           '<div class="skills-brand"><img class="skills-logo" src="../../assets/legal-mind-logo-tight.png" '
           'alt="לוגו Legal Mind - נורה מעל שם המותג" decoding="async"></div>', '',
           '<header class="hero"><div>',
           '<p class="eyebrow">%s · מדריך %d מתוך %d · קושי בינוני</p>' % (SERIES_PLAIN, g["num"], len(GUIDES)),
           '<h1>%s</h1>' % g["title"],
           '<p class="hero-copy">%s</p>' % g["sub"],
           '</div><dl class="facts">',
           '<div><dt>מה נלמד</dt><dd>%s</dd></div>' % g["learn"],
           '<div><dt>בסיום</dt><dd>%s</dd></div>' % g["end"],
           '<div><dt>זמן</dt><dd>%s</dd></div>' % g["time"],
           '<div><dt>דרישות</dt><dd>%s</dd></div>' % g["need"],
           '</dl></header>', '',
           '<nav class="mobile-toc"><details><summary>תוכן המדריך</summary><ol>', rail, '</ol></details></nav>', '',
           '<div class="layout">', '<main class="surface" id="main">',
           joined,
           '<div class="bottom-nav">' + "".join(prev_next) + '</div>',
           '</main>', '',
           '<aside class="desktop-toc"><h2>תוכן המדריך</h2><ol>', rail, '</ol></aside>',
           '</div>', '',
           '<footer><bdi dir="ltr">Legal Mind</bdi> | %s | מדריך %d: %s</footer>' % (SERIES_PLAIN, g["num"], g["title"]),
           '', scripts]
    d = os.path.join(OUT, g["dir"])
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "index.html")
    open(p, "w", encoding="utf-8").write(NL.join(out))
    return p, len(body)

for i, g in enumerate(GUIDES):
    p, n = page(g, i)
    print("wrote", p, "%d sections" % n, os.path.getsize(p), "bytes")

cards = []
for g in GUIDES:
    cards.append(
        '<article class="guide-card"><div><span class="guide-number">%d</span></div>'
        '<h2>%s</h2><dl>'
        '<div><dt>מה נלמד</dt><dd>%s</dd></div>'
        '<div><dt>בסיום המדריך</dt><dd>%s</dd></div>'
        '<div><dt>זמן משוער</dt><dd>%s</dd></div>'
        '<div><dt>רמה ודרישות</dt><dd>%s</dd></div>'
        '</dl><a class="button primary" href="%s/index.html">למדריך %d</a></article>'
        % (g["num"], g["title"], g["learn"], g["end"], g["time"], g["need"], g["dir"], g["num"]))

hub = """<!DOCTYPE html>
<html dir="rtl" lang="he"><head><meta charset="utf-8">
<meta content="width=device-width,initial-scale=1" name="viewport">
<meta name="description" content="מדריך ההמשך על Claude Code לעורכי דין - שלושה מדריכים של Legal Mind, למי שסיים את המדריך למתחילים">
<title>%s | Legal Mind</title>
<link href="../assets/site.css?v=20260815" rel="stylesheet">
<style>@media(min-width:900px){.guide-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.learning-path ol{grid-template-columns:repeat(3,1fr)}}</style>
</head><body class="center">
<nav class="backbar"><a href="../../index.html">חזרה למרכז המדריכים הראשי</a></nav>
<header class="center-head">
<div class="center-brand"><img alt="לוגו Legal Mind - נורה מעל שם המותג" class="skills-logo" decoding="async" src="../assets/legal-mind-logo-tight.png"></div>
<div class="center-hero">
<p class="center-kicker">מרכז המדריכים של LEGAL MIND</p>
<h1>%s</h1>
<p class="center-subtitle">שלושה מדריכים למי שכבר סיים את המדריך למתחילים. מתחילים בלהרגיש בבית בסביבה, ממשיכים לחמישה תרגילים על תיק אמיתי, ומסיימים במשימה שרצה גם כשאתם לא מול המחשב.</p>
<p class="platform-note"><strong>סביבת ההדגמה:</strong> רוב התרגילים מבוצעים ב-<bdi dir="ltr">VS Code</bdi>, הסביבה ש-<bdi dir="ltr">LEGAL MIND</bdi> בחרה ללמד, ומדריך 3 עובר לאפליקציית <bdi dir="ltr">Claude</bdi>. מדריך 1 מסביר למה בחרנו דווקא בסביבה הזאת.</p>
</div></header><main class="center-main">

<section class="learning-path"><h2>מסלול הלימוד</h2>
<p>כל מדריך עומד בפני עצמו, והסדר הוא מה שהופך אותו לקל.</p>
<ol><li><span>1</span>להרגיש בבית</li><li><span>2</span>לתרגל על תיק</li><li><span>3</span>להריץ בלי לשבת מול המחשב</li></ol>
<p class="path-note"><strong>לא בטוחים מאיפה להתחיל?</strong> התחילו במדריך 1. הוא לא מבקש מכם לבצע שום תרגיל, והוא זה שהופך את כל השאר לפשוט. מי שידלג עליו יתקע בתרגיל הראשון על משהו שאינו קשור לתרגיל.</p></section>

<section><div class="guide-grid">
%s
</div></section>

<section class="source-note"><p><strong>הערת עדכניות:</strong> עובדות הממשק נבדקו מול הממשק החי באוגוסט 2026, וכל תרגיל בסדרה הורץ בפועל ותוצאותיו נבדקו אחת לאחת. ממשקים משתנים, ולכן כל פעולה מתוארת גם בנתיב כתוב ולא נשענת על הצילום בלבד. אם מסך אצלכם נראה אחרת מהצילום, פעלו לפי הנתיב הכתוב.</p></section>

</main><footer class="center-footer">Legal Mind | %s | שלושה מדריכים | עודכן באוגוסט 2026</footer></body></html>
""" % (SERIES_PLAIN, SERIES, NL + NL.join(cards) + NL, SERIES_PLAIN)

p = os.path.join(OUT, "index.html")
open(p, "w", encoding="utf-8").write(hub)
print("wrote", p, os.path.getsize(p), "bytes")
