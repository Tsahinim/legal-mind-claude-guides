# -*- coding: utf-8 -*-
import base64, os, sys, io, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = r"C:\Users\Tzahi\OneDrive\שולחן העבודה\LEGAL-MIND-CLAUDE-DESKTOP-GUIDE\.github-live-repo\legal-mind-claude-guides"
A = os.path.join(ROOT, "skills", "qa", "chapter-scheduled-assets")
B = os.path.join(ROOT, "skills", "qa", "chapter-vscode-assets")
C = os.path.join(ROOT, "skills", "qa", "chapter-opening-assets")
D = os.path.join(ROOT, "skills", "qa", "ex4-assets")
E = os.path.join(ROOT, "skills", "qa", "ex5-assets")
F = os.path.join(ROOT, "skills", "qa", "ex2-assets")

def _path(n):
    for folder in (A, B, C, D, E, F):
        for name in ("raw-%s.png" % n, "%s.png" % n):
            p = os.path.join(folder, name)
            if os.path.exists(p):
                return p
    raise FileNotFoundError("asset not found: " + n)

def img(n):
    p = _path(n)
    b = base64.b64encode(open(p, "rb").read()).decode()
    return "data:image/png;base64," + b

import struct
def natural(n):
    p = _path(n)
    with open(p, "rb") as f:
        f.read(16); w, h = struct.unpack(">II", f.read(8))
    return w, h

def shot(n, caption, targets=None, legend=None):
    """targets: list of (style, badge_class, number). legend: list of strings."""
    w, h = natural(n)
    CAP_W, CAP_H = 650, 520
    box_w = min(w, CAP_W)
    if h * box_w / w > CAP_H:
        box_w = CAP_H * w / h
    cls = 'shot'
    # a very narrow strip must not squeeze the caption and legend into its own
    # width - the text keeps a readable column and the image is centred in it
    MIN_FIG = 300
    fig_style = ' style="max-width:%dpx;margin-inline:auto"' % max(round(box_w), MIN_FIG)
    frame_style = (' style="max-width:%dpx;margin-inline:auto"' % round(box_w)
                   if box_w < MIN_FIG else '')
    marks = ""
    for style, badge_cls, num in (targets or []):
        # on a narrow box the corner badge lands on the label inside it,
        # so push it out to the side where the frame is empty
        if not badge_cls:
            mw = re.search(r'width:([\d.]+)%', style)
            ml = re.search(r'left:([\d.]+)%', style)
            lft = float(ml.group(1)) if ml else 0.0
            wid = float(mw.group(1)) if mw else 100.0
            right = lft + wid
            # a badge is a fixed 26px. it must never leave the image, and never
            # sit on the words inside a box that is too narrow to hold it.
            box_h = h * box_w / w
            if box_h < 140:
                # a short strip has no room above the box for a corner badge
                badge_cls = 'badge-inside-left' if wid * box_w / 100 >= 34 else 'badge-outside-left'
            elif wid <= 16:
                badge_cls = 'badge-right' if lft < 8 else 'badge-outside-left'
            elif lft < 4:
                badge_cls = 'badge-inside-left'
        c = 'shot-target' + ((' ' + badge_cls) if badge_cls else '')
        marks += '<div class="%s" style="%s"><span class="shot-target-badge">%s</span></div>' % (c, style, num)
    out = ['<figure class="%s"%s>' % (cls, fig_style),
           '  <div class="shot-frame"%s><img src="%s" alt="%s" width="%d" height="%d" loading="lazy" decoding="async">%s</div>' % (frame_style, img(n), caption, w, h, marks),
           '  <figcaption>',
           '    <p class="shot-caption">%s</p>' % caption]
    if legend:
        items = "".join('<li><strong>%d</strong> %s</li>' % (i, t) for i, t in enumerate(legend, 1))
        out.append('    <ol class="shot-legend-num">%s</ol>' % items)
    out += ['  </figcaption>', '</figure>']
    return chr(10).join(out)

def placeholder(txt):
    return ('<aside class="content-box warning">\n<h3>צילום חסר</h3>\n<p>%s</p>\n</aside>' % txt)

INSTR = """קרא את CLAUDE.md שבתיקייה ופעל לפי נהלי המשרד שכתובים בו.

עבור על חמשת מסמכי התיק. שניים מהם סרוקים ואין בהם טקסט להעתקה, אז פשוט הסתכל על העמודים שלהם כמו על תמונה וקרא מה כתוב בהם. אל תחפש במחשב תוכנות פענוח ואל תתקין כלום, אתה יודע לקרוא תמונה בעצמך.

אתר בכל המסמכים כל מועד מחייב: מועדי תשלום, מועד מסירה, מועדים לרישום או להגשה, וכל תאריך שנקבע בו שמשהו צריך לקרות.

הפק קובץ חדש בתיקייה, בשם לפי נהלי המשרד, ובו:
טבלה של המועדים שטרם חלפו, לפי סדר כרונולוגי, ובה התאריך, מה נדרש, מי הצד שחייב בו, והמסמך שממנו נלקח.
טבלה נפרדת של מועדים שכבר חלפו ואין במסמכים אסמכתה שהם בוצעו.
וחלק בשם "טעון בדיקה" בסוף.

אל תקבע מה הדין ואל תכתוב מי צודק. עובדות, מקורות ופערים בלבד.
אל תשנה, תמחק או תשנה שם לאף מסמך קיים בתיקייה."""

HTML = """<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex">
<meta name="description" content="מדריך ההמשך על Claude Code לעורכי דין, למי שסיים את המדריך למתחילים. איך פותחים לו את כל מסמכי התיק בבת אחת, כולל סרוקים, ואיך נותנים לו לעבוד גם כשאתם לא מול המחשב. שלב אחרי שלב, עם כל החומר מוכן.">
<title>מדריך ההמשך על Claude Code לעורכי דין | Legal Mind</title>
<link rel="stylesheet" href="../assets/site.css?v=20260807">
<style>
  .download-row { display:flex; align-items:center; gap:.9rem; flex-wrap:wrap; margin:1.25rem 0; }
  .download-meta { opacity:.75; font-size:.95em; }

  /* a screenshot shrunk to a phone column is unreadable, so every one of them
     opens full size on a tap. scoped to this page - the published guides keep
     their own behaviour. */
  .shot-hint { margin:6px 0 0; color:var(--muted); font-size:.82rem; }
  .zoomer { position:fixed; inset:0; z-index:9999; display:none; direction:ltr;
            background:rgba(7,20,33,.94); overflow:auto; padding:54px 10px 24px;
            overscroll-behavior:contain; }
  .zoomer.is-open { display:block; }
  .zoomer-stage { margin-inline:auto; position:relative; }
  .zoomer-stage img { display:block; width:100%; height:auto; border-radius:8px; }
  .zoomer-close { position:fixed; top:10px; inset-inline-end:12px; z-index:1;
                  border:0; border-radius:999px; padding:9px 17px; cursor:pointer;
                  background:#fff; color:var(--navy); font:inherit; font-weight:800; }
  .zoomer-cap { max-width:760px; margin:14px auto 0; color:#eef3f3; direction:rtl;
                font-size:.95rem; line-height:1.7; text-align:center; }
  .zoomer-pan { display:none; margin:6px 0 0; color:#b8ccd8; font-size:.85rem; }
  .zoomer-cap.is-wide .zoomer-pan { display:block; }
</style>
</head>
<body>

<a class="skip" href="#main">דילוג לתוכן</a>
<nav class="backbar"><a href="../index.html">חזרה למרכז המדריכים</a></nav>

<div class="skills-brand">
  <img class="skills-logo" src="../assets/legal-mind-logo-tight.png"
       alt="לוגו Legal Mind - נורה מעל שם המותג" decoding="async">
</div>

<header class="hero">
  <div>
    <p class="eyebrow">ההמשך למדריך למתחילים · קושי בינוני · טיוטה לבדיקה</p>
    <h1>מדריך ההמשך על <bdi dir="ltr">Claude Code</bdi> לעורכי דין</h1>
    <p class="hero-copy">במדריך למתחילים למדתם לפתוח תיקייה, לבקש משימה, ולקבל תוצר. יפה מאוד. עכשיו נשב יחד ונעשה את הדברים שבגללם באתם: לפתוח לו את כל מסמכי התיק בבת אחת במקום מסמך אחד כל פעם, לבקש ממנו לבדוק את עצמו ולתקן, ולתת לו לעבוד גם כשאתם לא מול המחשב. אנחנו הולכים לאט, שלב אחרי שלב, ואת כל החומר אנחנו מביאים לכם מוכן. אתם רק מעתיקים ולוחצים.</p>
  </div>
  <dl class="facts">
    <div><dt>למי זה מתאים</dt><dd>למי שסיים את המדריך למתחילים. אין צורך בשום ידע טכני</dd></div>
    <div><dt>מה מביאים</dt><dd>תיקיית תרגול אחת, שמורידים בלחיצה בתחילת הדרך</dd></div>
    <div><dt>איפה עובדים</dt><dd>חלק ב-<bdi dir="ltr">VS Code</bdi> שאתם כבר מכירים, וחלק באפליקציה</dd></div>
    <div><dt>זמן</dt><dd>כשעה, בקצב שלכם</dd></div>
  </dl>
</header>

__MOBILE_TOC__

<div class="layout">
<main class="surface" id="main">

<aside class="content-box warning">
<p><strong>מסמך עבודה.</strong> זו טיוטה פנימית לבדיקה, ולא מדריך שפורסם. הסימונים האדומים על הצילומים והמקרא הממוספר טרם בוצעו, ושני צילומים עדיין חסרים ומסומנים בגוף הטקסט.</p>
</aside>

<section class="guide-section" id="start">
<span class="section-number">01</span>
<h2>לפני שמתחילים, כמה מילים ביניכם לביני</h2>

<p>אם סיימתם את המדריך למתחילים, יש לכם כבר את כל מה שצריך. לא נחזור על שום דבר משם, רק נוודא ביחד שהכל במקום.</p>

<p><strong>אתם יודעים לפתוח תיקייה</strong> ולראות ש-<bdi dir="ltr">Claude</bdi> עובד בתוכה ולא באוויר. <strong>אתם יודעים לבקש משימה</strong> בשפה רגילה, כמו שהייתם מסבירים למתמחה. <strong>ואתם יודעים לבדוק את מה שחזר</strong> ולא לקחת אותו כתורה מסיני. שלושת הדברים האלה הם כל מה שנדרש כאן.</p>

<p>מה שכן שונה כאן הוא כמה חומר אנחנו נותנים לו בבת אחת. במדריך למתחילים עבדנו על מסמך אחד או שניים, כדי שתראו איך זה עובד. <strong>כאן נפתח לו את כל תיקיית התיק ביחד:</strong> חמישה מסמכים, שניים מהם סרוקים שאי אפשר לחפש בהם, ועוד מאות עמודי פרוטוקולים.</p>

<p><strong>וזה לא רק יותר עבודה, זו עבודה אחרת.</strong> תאריך שרשום בהסכם אחרת מאשר בדרישת התשלום, או התחייבות שנקבעה בישיבה ואין לה אסמכתה שבוצעה - <strong>אי אפשר לראות את זה במסמך אחד.</strong> זה נמצא רק במרווח שבין שני מסמכים, וכדי לראות אותו צריך להחזיק את שניהם בראש באותו רגע. בדיוק שם הוא מתחיל להיות שווה את הזמן שלכם.</p>

<aside class="content-box info">
<h3>ואיך נעבוד</h3>
<p><strong>לאט, ובלי הפתעות.</strong> כל תרגיל מתחיל בהסבר קצר על מה אנחנו הולכים לעשות ולמה, ואז אנחנו עושים אותו יחד, צעד אחרי צעד, עם צילום מסך של מה שאתם אמורים לראות. <strong>את כל החומר אנחנו מביאים מוכן</strong> - את התיק, את המסמכים, ואת הבקשה המדויקת. אתם מעתיקים בלחיצה ומדביקים. לא צריך לכתוב כלום מהראש.</p>
</aside>

<h3>ומילה אחת על שני המקומות שבהם נעבוד</h3>

<p>עד עכשיו עבדתם ב-<bdi dir="ltr">VS Code</bdi>. <strong>ואולי כדאי שנספר לכם למה דווקא שם התחלנו,</strong> כי זו הייתה בחירה ולא מקרה.</p>

<p><bdi dir="ltr">Claude Code</bdi> יושב בשני מקומות. אחד מהם הוא <bdi dir="ltr">VS Code</bdi>, שהיא הסביבה שכל העולם עובד בה היום, וגם המקום שבו רואים הכל: את התיקייה, את הקבצים, את מה שהשתנה ומתי. <strong>והשני הוא האפליקציה של <bdi dir="ltr">Claude</bdi> שכבר מותקנת אצלכם במחשב, וששם זה הרבה יותר פשוט.</strong></p>

<p><strong>בחרנו ללמד אתכם קודם את הקשה.</strong> לא כדי להתיש אתכם, אלא כי מי שראה את המכונה מבפנים מבין מה קורה לו מתחת לידיים, ומהמקום הזה לרדת לקל הוא עניין של דקה. הפוך זה לא עובד.</p>

<p>ובמדריך הזה תעשו בדיוק את זה: <strong>חלק מהתרגילים נעשה ב-<bdi dir="ltr">VS Code</bdi> שאתם כבר מכירים, וחלק נעשה באפליקציה.</strong> ותראו בעצמכם כמה זה קל שם.</p>

<aside class="content-box recommendation">
<h3>וכל המעבר לאפליקציה הוא לחיצה אחת</h3>
<p>פותחים את אפליקציית <bdi dir="ltr">Claude</bdi> כרגיל, ולמעלה, ליד <bdi dir="ltr">Home</bdi>, לוחצים על <bdi dir="ltr">Code</bdi>. זהו. <strong>אותה אפליקציה, אותו חשבון, אותו <bdi dir="ltr">Claude Code</bdi> שלמדתם</strong> - רק בלי סייר הקבצים ובלי כל מה שמסביב.</p>
<p>אין מה להוריד, אין מה להתקין, ואי אפשר לשבור שום דבר. <strong>ובכל פרק נגיד לכם במפורש איפה אנחנו עובדים</strong>, כדי שלא תצטרכו לנחש.</p>
</aside>

<h3>ודבר אחרון לפני שיוצאים לדרך</h3>

<p>המדריך הזה לא בא ללמד אתכם טכנולוגיה. <strong>הוא בא לחסוך לכם שעות.</strong> כל תרגיל כאן הוא משהו שאתם עושים היום ביד, ושאחריו תדעו לעשות אחרת. אם משהו לא ברור, זו אשמת המדריך ולא שלכם, ואפשר תמיד לחזור צעד אחורה.</p>
</section>

<section class="guide-section" id="download">
<span class="section-number">02</span>
<h2>מורידים את התיק שנעבוד עליו</h2>

<p>כל התרגילים במדריך רצים על אותו תיק אחד, ואנחנו מביאים לכם אותו מוכן. <strong>מורידים פעם אחת בהתחלה, וזהו.</strong></p>

<p class="download-row"><a class="button primary" href="../assets/Legal-Mind-case-folder-practice.zip" download>הורדת תיקיית התרגול</a> <span class="download-meta">קובץ אחד, כ-4.7 מגה</span></p>

<h3>מה יש בפנים</h3>

<p>תיק מכר דירה שנמצא באמצע ביצוע, בדיוק כמו תיק אמיתי במשרד:</p>

<ul class="bullets">
<li><strong>חמישה מסמכי תיק</strong> - הסכם מכר, נסח רישום, התכתבות בין באי הכוח, פרוטוקול ישיבה ודרישת תשלום. <strong>שניים מהם סרוקים</strong>, כלומר תמונה בלבד, בדיוק כמו מה שמגיע אליכם מהצד השני.</li>
<li><strong>תיקיית פרוטוקולים</strong> - ארבעה ימי דיונים, מאות עמודים.</li>
<li><strong>תיקיית גרסאות</strong> - שלושה נוסחים של אותו הסכם, לפני ואחרי הערות.</li>
<li><strong>ארבעים מסמכים סרוקים לתיוק</strong>, בשמות כמו <bdi dir="ltr">scan_0030</bdi> ו-<bdi dir="ltr">doc4_final_v2</bdi>. אתם מכירים את זה.</li>
<li><strong>וקובץ נהלים בשם <bdi dir="ltr">CLAUDE.md</bdi></strong> - עליו נדבר מיד.</li>
</ul>

<aside class="content-box info">
<h3>ומהו הקובץ הזה, <bdi dir="ltr">CLAUDE.md</bdi></h3>
<p><strong>זה קובץ טקסט פשוט שיושב בתוך התיקייה, וקלוד קורא אותו לבד בכל פעם שהוא עובד בה.</strong> אתם לא צריכים להזכיר לו.</p>
<p><strong>ובתוכו כתובים נהלי המשרד:</strong> איך כותבים תאריכים, איך קוראים לקבצים, מה אסור לגעת בו, ומה חייב להופיע בכל תוצר. <strong>במקום לחזור על הכללים האלה בכל בקשה, כותבים אותם פעם אחת והם חלים על הכול.</strong></p>
<p>הכנו אותו עבורכם והוא כבר בתיקייה. <strong>אל תמחקו אותו, ואל תשנו אותו במהלך התרגילים</strong> - חלק מהתוצאות מסתמכות עליו.</p>
<p><strong>ומי שרוצה להבין לעומק מה עוד אפשר לעשות עם קבצים כאלה,</strong> ההרחבה נמצאת ב<a href="../../skills/index.html">מדריך המקיף ל-<bdi dir="ltr">Skills</bdi> לעורכי דין</a> של <bdi dir="ltr">Legal Mind</bdi>. <strong>לא צריך אותו כדי לבצע את התרגילים כאן.</strong></p>
</aside>

<aside class="content-box info">
<p><strong>הכל מומצא, ובכוונה.</strong> בשולי כל מסמך כתוב שהוא מסמך תרגול בדוי. השמות, מספרי הזהות והתאריכים אינם של אף אדם, נכס או עסקה קיימים. <strong>תרגלו בלי לחשוב פעמיים.</strong></p>
</aside>

<h3>לחלץ, לא רק לפתוח</h3>

<p>אחרי ההורדה תמצאו בתיקיית <bdi dir="ltr">Downloads</bdi> קובץ מכווץ. <strong>לחיצה כפולה עליו תראה לכם את התוכן, אבל זה עדיין לא מספיק</strong> - הקבצים עדיין דחוסים בפנים, ו-<bdi dir="ltr">Claude</bdi> לא יוכל לכתוב לשם.</p>

<ol class="steps">
<li>לחצו על הקובץ בלחיצה ימנית.</li>
<li>בחרו <bdi dir="ltr">Extract All</bdi>, ובחלון שנפתח לחצו <bdi dir="ltr">Extract</bdi>.</li>
<li>נוצרת לכם תיקייה רגילה בשם <bdi>תיק-הברוש-14-לתרגול</bdi>. <strong>זו התיקייה שנעבוד איתה לאורך כל המדריך.</strong></li>
</ol>

<aside class="content-box recommendation">
<p><strong>ואיך יודעים שהצלחתם:</strong> נכנסים לתיקייה שנוצרה, ורואים בתוכה חמישה קבצי <bdi dir="ltr">PDF</bdi>, שלוש תיקיות, וקובץ בשם <bdi dir="ltr">CLAUDE.md</bdi>. אם אתם רואים את זה, אתם מוכנים.</p>
</aside>
</section>

<section class="guide-section" id="firstopen">
<span class="section-number">03</span>
<h2>אחרי שבחרתם תיקייה שקלוד יעבוד עליה</h2>

<p><strong>זה המסלול שתעשו בתחילת כל תרגיל, וכדאי לעבור עליו פעם אחת ברוגע.</strong> אחרי פעמיים הוא ייקח לכם חצי דקה.</p>

<aside class="content-box recommendation">
<h3>ולמה אנחנו מפרטים אותו עד הסוף</h3>
<p><strong>זה לא שאנחנו לא סומכים עליכם.</strong> אנחנו פשוט לא רוצים שתיבהלו ממה שכמעט כל מי שהתחיל עם <bdi dir="ltr">Claude Code</bdi> עבר: <strong>פותחים תיקייה, וקלוד נעלם.</strong> במקומו יש מסך לבן באמצע, חלונית שיחה בצד שאינה שלו, וחלונות שקופצים.</p>
<p><strong>שום דבר לא נשבר. ככה זה נראה אצל כולם בפעם הראשונה,</strong> ובעוד שתי דקות זה ייראה אחרת.</p>
</aside>

<h3>וכך זה נראה בפועל, רגע אחרי שבחרתם תיקייה</h3>

__FIG_CHAOS__

<p><strong>שלושה דברים על המסך, ורק אחד מהם קשור אליכם.</strong> נעבור עליהם אחד אחד, ובסוף יישארו שניים: התיקייה בצד, וקלוד באמצע.</p>

<aside class="content-box info">
<h3>ולפני הכל, דבר אחד שכדאי לדעת</h3>
<p><bdi dir="ltr">Claude Code</bdi> <strong>תמיד עובד בתוך תיקייה.</strong> אי אפשר לפתוח איתו שיחה בלי לבחור אחת. <strong>וזה לא חיסרון, זה מה שמאפשר לו לעבוד על הקבצים שלכם.</strong></p>
<p>והתיקייה לא חייבת להכיל כלום. <strong>אפשר פשוט ליצור תיקייה חדשה וריקה, לתת לה שם, ולבחור אותה.</strong> מכאן הכל עובד אותו דבר.</p>
</aside>

<h3>שלב 1 · אישור התיקייה</h3>

<p>מיד אחרי שבחרתם תיקייה, <strong>תופיע למעלה שורה כחולה. לחצו בה <bdi dir="ltr">Manage</bdi>.</strong></p>

<p><strong>ייפתח חלון, ובו לוחצים <bdi dir="ltr">Trust</bdi>.</strong></p>

<aside class="content-box warning">
<h3>ואז יופיע מסך שנראה חשוב, והוא לא</h3>
<p>אחרי האישור ייפתח מסך גדול בשם <bdi dir="ltr">Workspace Trust</bdi>, עם שתי עמודות וסימני וי ואיקס. <strong>אל תקראו אותו. אין בו שום דבר שאתם צריכים.</strong></p>
<p><strong>הוא רק מאשר שאישרתם. סגרו אותו ב-<bdi dir="ltr">X</bdi> ותמשיכו.</strong></p>
<p>אנחנו אומרים את זה במפורש כי הוא נראה כמו משהו שאסור לסגור בלי להבין, <strong>והוא בדיוק ההפך.</strong></p>
</aside>

__FIG_TRUST__

<p><strong>ואיך יודעים שהצלחתם:</strong> בסרגל האייקונים שבצד, <strong>הכוכבית של <bdi dir="ltr">Claude</bdi> מופיעה.</strong> זו הבדיקה היחידה שצריך.</p>

<h3>שלב 2 · מנקים את המסך</h3>

<p><strong>מה שתראו עכשיו הוא לא מה שאתם צריכים,</strong> ובואו נעבור על זה בלי להיבהל.</p>

<ul class="bullets">
<li><strong>באמצע</strong> יש מסך פתיחה של <bdi dir="ltr">VS Code</bdi> עם קישורים והסברים. לא קשור אלינו.</li>
<li><strong>ובצד</strong> יש חלונית שיחה - <strong>ואינה של <bdi dir="ltr">Claude</bdi>.</strong> היא של <bdi dir="ltr">VS Code</bdi> עצמו.</li>
</ul>

<ol class="steps">
<li><strong>את המסך שבאמצע:</strong> שלוש הנקודות שמעליו, ואז <bdi dir="ltr">Close All</bdi>.</li>
<li><strong>ואת חלונית השיחה שבצד:</strong> ה-<bdi dir="ltr">X</bdi> שבפינה שלה.</li>
</ol>

<h3>שלב 3 · פותחים את השיחה של <bdi dir="ltr">Claude</bdi></h3>

<ol class="steps">
<li><strong>לוחצים על הכוכבית של <bdi dir="ltr">Claude</bdi></strong> בסרגל האייקונים שבצד.</li>
<li><strong>ולוחצים <bdi dir="ltr">New session</bdi>.</strong></li>
</ol>

__FIG_ACTIVITYBAR__

<p><strong>וכך נראית החלונית ברגע שהיא נפתחת:</strong></p>

__FIG_NEWSESSION__

<p><strong>ורק עכשיו נפתחת השיחה.</strong> מכאן והלאה מדביקים ועובדים.</p>

<h3>שלב 4 · ואם רוצים לראות את התיקייה</h3>

<p><strong>לוחצים על אייקון המסמכים</strong> שבראש סרגל האייקונים, וסרגל הקבצים נפתח עם שם התיקייה והקבצים שבה.</p>

__FIG_EXPLORERICON__

<p><strong>וזה גם שימושי מעבר לנוחות:</strong> שם התיקייה שרשום שם הוא <strong>הדרך לוודא שהשיחה באמת על התיק שרציתם</strong>, ולא על תיק אחר שנשאר פתוח מקודם.</p>

<aside class="content-box recommendation">
<p><strong>ארבעת השלבים האלה הם כל מה שצריך, והם חוזרים על עצמם בכל תרגיל.</strong> אנחנו נזכיר אותם בקצרה בכל פעם, כדי שלא תצטרכו לחזור לכאן.</p>
</aside>
</section>

<section class="guide-section" id="panic">
<span class="section-number">03</span>
<h2><bdi dir="ltr">Claude</bdi> מתארח כאן, ולכן לפעמים צריך עוד לחיצה</h2>

<p>נתחיל בהודאה: <strong>זה לא פשוט כמו לחזור לשיחה בצ'אט.</strong> בדפדפן הכל במקום אחד, השיחות מסודרות זו מתחת לזו, ואי אפשר ללכת לאיבוד. <strong>כאן זה אחרת, וזה יכול להבהיל בפעם הראשונה.</strong></p>

<p><strong>אז בואו נבין למה, כי ברגע שהאסימון הזה נופל רוב הפחד נעלם.</strong></p>

<p><bdi dir="ltr">Claude Code</bdi> אינו תוכנה משלו ואינו האפליקציה של <bdi dir="ltr">Claude</bdi>. <strong>הוא מתארח בתוך <bdi dir="ltr">VS Code</bdi></strong>, שהיא סביבה גדולה ועצמאית לגמרי, עם החלונות שלה, הלשוניות שלה, ההודעות שלה - <strong>ואפילו חלונות שיחה משלה שאינם של <bdi dir="ltr">Claude</bdi> בכלל.</strong></p>

<p><strong>ומכאן הכל מתיישב:</strong> אנחנו אורחים בבית של מישהו אחר. לכן לפעמים נדרשות שתי לחיצות במקום אחת כדי להגיע למקום שרצינו, ולכן קופצות הודעות שאינן קשורות אלינו. <strong>שום דבר מזה אינו תקלה, ושום דבר מזה לא שבר כלום.</strong></p>

<aside class="content-box recommendation">
<h3>ובשביל זה אנחנו כאן</h3>
<p><strong>לא נשאיר אתכם לבד מול מסך שלא ברור.</strong> בפרק הזה ריכזנו את המצבים שיכולים לעצור אתכם באמצע, כל אחד עם מה שרואים, מה קרה באמת, ומה עושים. <strong>קראו אותו עכשיו, וחזרו אליו כשמשהו ייראה מוזר.</strong></p>
<p><strong>ואם בכל זאת נתקעתם - פנו אלינו.</strong> דרך האתר, בקבוצות הוואטסאפ שלנו שכידוע לכם אינן שקטות במיוחד, או במייל שמופיע באתר. <strong>עדיף שתשאלו אותנו מאשר שתוותרו.</strong></p>
</aside>

<h3>1 · פתחתי תיקייה, ו-<bdi dir="ltr">Claude</bdi> נעלם</h3>

<p><strong>מה שרואים:</strong> פתחתם תיקייה חדשה, ופתאום אין חלונית של <bdi dir="ltr">Claude</bdi> ואין אפילו את הסמל שלו בצד. <strong>נראה כאילו הוא הוסר מהמחשב.</strong></p>

<p><strong>מה קרה באמת:</strong> <bdi dir="ltr">VS Code</bdi> לא פותח תוספים בתיקייה שהוא עוד לא מכיר, עד שתאשרו שאתם בוטחים בה. <strong>זו הגנה, לא תקלה.</strong></p>

<p><strong>מה עושים:</strong> למעלה תופיע שורה כחולה. <strong>לוחצים בה <bdi dir="ltr">Manage</bdi>, ובחלון שנפתח לוחצים <bdi dir="ltr">Trust</bdi>.</strong> מרגע זה <bdi dir="ltr">Claude</bdi> חוזר.</p>

<aside class="content-box warning">
<p><strong>סליחה שנחזור על זה גם בהמשך.</strong> זה השלב שהכי קל לשכוח, ובלעדיו נראה שהכלי פשוט לא עובד.</p>
</aside>

<h3>2 · יש כאן עוד חלונות צ'אט, ואני לא יודע באיזה לכתוב</h3>

__FIG_PANEL__


<p><strong>מה שרואים:</strong> יותר מחלונית שיחה אחת, וכולן נראות דומה.</p>

<p><strong>מה קרה באמת:</strong> ל-<bdi dir="ltr">VS Code</bdi> יש חלוניות צ'אט משלו ושל תוספים אחרים. <strong>מי שיכתוב בחלונית הלא נכונה יקבל תשובה ממישהו אחר לגמרי, או שלא יקבל כלום.</strong></p>

<p><strong>איך מזהים את של <bdi dir="ltr">Claude</bdi>, ושלושה סימנים שכל אחד מהם מספיק:</strong></p>

<ul class="bullets">
<li>הכותרת <bdi dir="ltr">Claude Code</bdi> והכוכבית הכתומה.</li>
<li>בתחתית תיבת הכתיבה מופיע שם המודל, למשל <bdi dir="ltr">Opus 5</bdi>. <strong>בחלוניות אחרות זה לא מופיע.</strong></li>
<li>ובסרגל האייקונים שבצד, הכוכבית הכתומה מחזירה תמיד לחלונית הנכונה.</li>
</ul>

<h3>3 · <bdi dir="ltr">Claude</bdi> היה כאן ופתאום איננו</h3>

<p><strong>מה שרואים:</strong> לחצתם על שם של קובץ בשיחה, הקובץ נפתח, <strong>ובמקום השיחה יש עכשיו מסמך.</strong></p>

<p><strong>מה קרה באמת:</strong> החלונית של <bdi dir="ltr">Claude</bdi> היא לשונית, בדיוק כמו קובץ. <strong>היא לא נסגרה, היא מאחור.</strong></p>

<p><strong>מה עושים:</strong> למעלה, בשורת הלשוניות, <strong>לוחצים על הלשונית עם הכוכבית הכתומה.</strong></p>

<h3>4 · המסך התמלא בלשוניות</h3>

__FIG_CLOSEALL__


<p><strong>מה שרואים:</strong> אחרי כמה לחיצות המסך עמוס, והחלונית של <bdi dir="ltr">Claude</bdi> הצטמצמה לפינה.</p>

<p><strong>מה עושים:</strong> שלוש הנקודות בפינת אזור הלשוניות, ואז <bdi dir="ltr">Close All</bdi>. <strong>או בקיצור: <bdi dir="ltr">Ctrl+K</bdi> ואחריו <bdi dir="ltr">W</bdi>.</strong></p>

<p><strong>ואל תחששו לסגור.</strong> שום דבר לא נמחק, והקבצים נשארים בתיקייה. <strong>כדי לעבוד מספיקות התיקייה בצד וחלונית <bdi dir="ltr">Claude</bdi> באמצע.</strong></p>

<h3>5 · קפץ חלון שמציע להתקין משהו</h3>

<p><strong>מה שרואים:</strong> חלון קטן שמציע להתקין תוסף, למשל לצפייה בקובצי <bdi dir="ltr">PDF</bdi>.</p>

__FIG_INSTALLPOPUP__

<p><strong>מה זה בעצם:</strong> <bdi dir="ltr">VS Code</bdi> ראה שיש בתיקייה קובץ <bdi dir="ltr">PDF</bdi>, ומציע לכם תוסף שיציג אותו על המסך. <strong>ההצעה אינה מגיעה מ-<bdi dir="ltr">Claude</bdi> ואינה קשורה למשימה,</strong> והתוסף עצמו נכתב בידי מפתח חיצוני ולא בידי מיקרוסופט או <bdi dir="ltr">Anthropic</bdi>.</p>

<p><strong>מה עושים: סוגרים אותו ב-<bdi dir="ltr">X</bdi>.</strong> <bdi dir="ltr">Claude</bdi> קורא את המסמכים בעצמו, בלי שום תוספת.</p>

<aside class="content-box warning">
<h3>ולמה לא ללחוץ <bdi dir="ltr">Install</bdi> סתם כדי שייעלם</h3>
<p><strong>תוסף מקבל גישה לקבצים שבתיקייה הפתוחה,</strong> ואצלכם זו תיקיית תיק. <strong>התקנה היא החלטה, לא סגירה של חלון.</strong></p>
<p>ואם התקנתם בטעות - <strong>לא קרה אסון</strong>, אבל אין סיבה. הצילום נעשה על התרגיל הזה עצמו, והמשימה רצה בלי התוסף.</p>
</aside>

<p><strong>וכלל כללי שחוסך את כל השאלות מהסוג הזה: כל דבר שקופץ ומציע להתקין - לא צריך.</strong></p>

<h3>6 · השיחות שלי נעלמו</h3>

<p><strong>וזה הרגע שהכי מפחיד בכל המדריך, אז נעצור עליו.</strong></p>

<p>בדפדפן, כל השיחות שלכם יושבות בצד, אחת מתחת לשנייה. <strong>אתם אף פעם לא צריכים לחשוב עליהן. הן פשוט שם.</strong></p>

<p><strong>וכאן, ברגע שפותחים תיקייה, המסך מראה שיחה ריקה.</strong> אין רשימה בצד, אין היסטוריה, אין שום דבר שמזכיר שעבדתם כאן אתמול. <strong>וההרגשה היא שהכל נמחק.</strong></p>

<p><strong>שום דבר לא נמחק.</strong> כל מילה שנכתבה כאן שמורה, וכל שיחה תיפתח בדיוק כפי שהשארתם אותה.</p>

<p><strong>מה שהשתנה הוא רק איפה הן מסודרות:</strong> לא ברשימה אחת בצד, אלא <strong>לפי תיק.</strong> כל תיקייה מחזיקה את השיחות שנעשו בה.</p>

<h4>לחזור לשיחה בתיק שאתם עובדים בו עכשיו</h4>

<p><strong>לחיצה אחת.</strong> בראש חלונית <bdi dir="ltr">Claude Code</bdi>, ליד שם השיחה, יש <strong>אייקון של שעון</strong>. לוחצים עליו ונפתחת רשימת כל השיחות שהיו בתיקייה, עם שדה חיפוש ועם הזמן שעבר מכל אחת. <strong>לוחצים על שיחה, והיא נפתחת עם כל ההיסטוריה.</strong></p>

<p>ולידו יש פלוס, שפותח שיחה חדשה.</p>

__FIG_SESSIONS__

__FIG_HISTORY__

<h4>ולחזור לשיחה שהייתה בתיק אחר · שלוש פעולות</h4>

<ol class="steps">
<li><strong>בוחרים את התיקייה.</strong> <bdi dir="ltr">File</bdi> ואז <bdi dir="ltr">Open Recent</bdi>, ומשם את התיק. ואם זו תיקייה שלא נפתחה כאן קודם, תופיע השורה הכחולה: <bdi dir="ltr">Manage</bdi> ואז <bdi dir="ltr">Trust</bdi>.</li>
<li><strong>פותחים את החלונית בצד.</strong> <bdi dir="ltr">Ctrl+Shift+P</bdi>, מקלידים <bdi dir="ltr">claude</bdi>, ובוחרים <bdi dir="ltr">Open in Side Bar</bdi>.</li>
<li><strong>לוחצים על השעון</strong> ובוחרים את השיחה.</li>
</ol>

<aside class="content-box warning">
<p><strong>ובין הפעולה הראשונה לשנייה תראו שוב שיחה ריקה. אל תיבהלו, ואל תסיקו שאיבדתם משהו.</strong> השיחות של התיק הזה מחכות מאחורי אייקון השעון, ואתם שתי לחיצות ממנו.</p>
</aside>

__FIG_PALETTE__

<aside class="content-box info">
<h3>ואם אין שעון בכלל</h3>
<p>סימן שהחלונית פתוחה כלשונית באמצע המסך ולא בצד. <strong>במצב הזה אין לה שורה עליונה משלה, והאייקונים שרואים למעלה שייכים ל-<bdi dir="ltr">VS Code</bdi> ולא לקלוד.</strong> הפעולה השנייה שלמעלה מחזירה אותה לצד.</p>
</aside>

<aside class="content-box recommendation">
<h3>ולמה זה בעצם לטובתכם</h3>
<p>שיחה על תיק אחד לא תופיע כשתפתחו תיקייה של תיק אחר. <strong>כל תיק והשיחות שלו, בלי ערבוב בין לקוחות</strong> - ובלי סיכוי לפתוח בטעות שיחה על תיק אחר מול לקוח שיושב מולכם.</p>
</aside>

<h3>7 · הדבקתי את הפרומפט והוא הפך לקובץ קטן</h3>

<p><strong>מה שרואים:</strong> הדבקתם טקסט ארוך, <strong>והוא לא נשאר בתיבה.</strong> במקומו הופיע מלבן קטן מעל התיבה, עם שם של קובץ. <strong>והתיבה עצמה נראית ריקה.</strong></p>

<p><strong>מה קרה באמת:</strong> כשמדביקים טקסט ארוך, <bdi dir="ltr">Claude Code</bdi> שומר אותו כקובץ ומצרף אותו להודעה במקום להציג אותו כולו בתיבה. <strong>זו התנהגות רגילה, וקיימת כמעט בכל כלי מהסוג הזה.</strong></p>

<p><strong>והבקשה שלכם לא אבדה. היא בתוך הקובץ הזה, במלואה.</strong></p>

<aside class="content-box warning">
<h3>ומכאן הנקודה שעוצרת אנשים</h3>
<p><strong>חץ השליחה יישאר אפור ולא נלחץ.</strong> קובץ מצורף לבדו אינו מספיק - <bdi dir="ltr">Claude</bdi> צריך גם מילה מכם.</p>
<p><strong>כתבו בתיבה מילה אחת כלשהי</strong> - "קדימה", "התחל", "הרץ" - <strong>והחץ יהפוך לאדום ולחיץ.</strong> לחצו עליו.</p>
<p><strong>והמילה עצמה אינה משנה דבר.</strong> היא לא הוראה ולא הנחיה. <strong><bdi dir="ltr">Claude</bdi> מתייחס לקובץ המצורף כאל הבקשה,</strong> והמילה רק מאפשרת לכם ללחוץ על החץ.</p>
</aside>

<p><strong>ואיך יודעים שזה עבד:</strong> הוא יתחיל לעבוד לפי מה שכתוב בקובץ, בדיוק כאילו הדבקתם את הטקסט בתיבה.</p>

<aside class="content-box info">
<p><strong>ואם הטקסט כן נשאר בתיבה - הכל תקין גם כן.</strong> זה תלוי באורך, ושתי הדרכים עובדות אותו דבר.</p>
</aside>

<h3>8 · איך עוברים לתיקייה אחרת</h3>

__FIG_RECENT__


<p><bdi dir="ltr">File</bdi> ואז <bdi dir="ltr">Open Recent</bdi>, ושם רשימת התיקיות שפתחתם לאחרונה. או <bdi dir="ltr">Open Folder</bdi> לתיקייה חדשה.</p>

<p><strong>ושימו לב: זו רשימת תיקיות, לא רשימת שיחות.</strong> אחרי שהתיקייה נפתחת, מגיעים לשיחה דרך <bdi dir="ltr">Session history</bdi> שבסעיף הקודם. <strong>קודם התיקייה, ואז השיחה.</strong></p>

<h3>9 · הוא אמר שיצר קבצים, ואני לא רואה אותם</h3>

<p><strong>או ההפך: מחקנו קבצים והם עדיין מופיעים.</strong></p>

<p><strong>מה קרה באמת:</strong> רשימת הקבצים בצד לא תמיד מתעדכנת מיד. <strong>הקבצים כבר במקום, זו רק התצוגה.</strong></p>

<p><strong>מה עושים:</strong> לוחצים על שם התיקייה ברשימה, או על אייקון הרענון שבראש הרשימה.</p>

<aside class="content-box recommendation">
<h3>ואם כלום מזה לא עזר</h3>
<p><strong>סגרו את <bdi dir="ltr">VS Code</bdi> ופתחו מחדש.</strong> זה נשמע פשוט מדי, וזה פותר את רוב הדברים המוזרים. <strong>שום שיחה ושום קובץ לא ילכו לאיבוד</strong> - הכל שמור, וה-<bdi dir="ltr">Session history</bdi> יחכה לכם בדיוק כפי שהיה.</p>
</aside>
</section>

<section class="guide-section" id="ex1">
<span class="section-number">05</span>
<h2>תרגיל 1 · ארבעים סרוקים מקבלים שם</h2>

<p><strong>איפה עובדים:</strong> ב-<bdi dir="ltr">VS Code</bdi> · <strong>כמה זמן:</strong> כשמונה דקות, ורובן הוא עובד ואתם לא</p>

<h3>המטרה</h3>

<p>בכל תיק יש תיקייה כזאת. קוראים לה "סרוקים", או "לתיוק", או סתם "חדש", <strong>ובתוכה עשרות קבצים בשמות שאף אחד לא בחר:</strong> <bdi dir="ltr">scan_0030</bdi>, <bdi dir="ltr">doc4_final_v2</bdi>, <bdi>מסמך חדש (7)</bdi>.</p>

<p><strong>כדי לדעת מה יש שם צריך לפתוח אותם אחד אחד.</strong> ולכן זה לא נעשה.</p>

<p>בתרגיל הזה נבקש ממנו לפתוח את כולם, לקרוא מה כתוב בכל אחד, <strong>ולתת לכל אחד שם שאומר מה הוא.</strong></p>

<aside class="content-box info">
<h3>ושימו לב לדבר אחד שלא היה במדריך למתחילים</h3>
<p><strong>המסמכים האלה הם תמונה.</strong> אין בהם טקסט, <bdi dir="ltr">Ctrl+F</bdi> לא ימצא בהם מילה, ואי אפשר להעתיק מהם דבר. <strong>בדיוק כמו מה שמגיע אליכם מהצד השני.</strong></p>
</aside>

<h3>ההוראה, ולמה היא כתובה ככה</h3>

<p><strong>שלושה דברים בה אינם מובנים מאליהם:</strong></p>

<ul class="bullets">
<li><strong>"הסתכל על כל עמוד כמו על תמונה".</strong> בלי המשפט הזה הוא יוצא לחפש במחשב תוכנות שמפענחות סריקות, <strong>ומבזבז דקות על משהו שהוא יודע לעשות בעצמו.</strong></li>
<li><strong>"אל תשנה שם ואל תזיז שום קובץ קיים".</strong> נהלי המשרד שבתיקייה אוסרים לגעת במסמך מקור, וזה נכון גם בחיים. <strong>לכן הוא יעתיק לתיקייה חדשה וישאיר את המקור כפי שהוא.</strong></li>
<li><strong>ובקשה לקובץ אינדקס.</strong> בלעדיו יש לכם ארבעים קבצים בשמות יפים ואין לכם דרך לדעת מה השתנה. <strong>איתו יש לכם גם ביקורת.</strong></li>
</ul>

<div class="copy-block">
  <div class="copy-heading">
    <strong>ההוראה, להעתקה</strong>
    <button class="copy-button" data-copy-target="ex1-prompt" type="button">העתקת ההוראה</button>
  </div>
  <div class="copy-body" id="ex1-prompt">קרא את CLAUDE.md שבתיקייה ופעל לפי נהלי המשרד שכתובים בו.

בתיקיית המשנה "סרוקים-לתיוק" יש ארבעים מסמכים סרוקים. כולם תמונה בלבד, אין בהם טקסט להעתקה, והשמות שלהם חסרי משמעות. פשוט הסתכל על כל עמוד כמו על תמונה וקרא מה כתוב בו. אל תחפש במחשב תוכנות פענוח ואל תתקין כלום, אתה יודע לקרוא תמונה בעצמך.

לכל מסמך זהה: מה סוג המסמך, מה התאריך שמופיע בו, ומה הנושא שלו במילים ספורות.

נהלי המשרד אוסרים לשנות שם למסמך מקור, ולכן אל תשנה שם ואל תזיז שום קובץ קיים. במקום זה צור בתיקייה תיקיית משנה חדשה בשם "מתויק", והעתק אליה את כל ארבעים המסמכים בשמות תקינים לפי כלל שמות הקבצים שבנהלי המשרד.

בנוסף הפק בתיקייה קובץ אינדקס בשם לפי נהלי המשרד, ובו טבלה: שם הקובץ המקורי, השם החדש, סוג המסמך, התאריך שבמסמך, והנושא. ובסוף חלק בשם "טעון בדיקה" לכל מסמך שלא הצלחת לקרוא או שהתאריך בו לא היה ברור.

אל תקבע מה הדין ואל תכתוב מי צודק. עובדות ומקורות בלבד.</div>
  <span class="copy-status" aria-live="polite" aria-atomic="true"></span>
</div>

<h3>מה יקרה אחרי שתדביקו</h3>

<p><strong>הוא ידווח לכם שורה אחרי שורה.</strong> קודם יקרא את קובץ הנהלים, ואז תראו אותו כותב משהו כמו <em>"אין צורך בכלי פענוח, כל קובץ עוטף תמונה אחת, אני מחלץ אותה וקורא ישירות"</em> - <strong>וזו החלטה שהוא מקבל לבד.</strong></p>

<p>ואז: <em>"קריא. עכשיו קורא את כל ארבעים העמודים."</em></p>

__FIG_OCRLINES__

<p><strong>כשמונה דקות, ורובן אתם לא עושים כלום.</strong> ובסוף יהיו בתיקייה שני דברים חדשים: תיקייה בשם <bdi>מתויק</bdi> ובה ארבעים עותקים בשמות תקינים, וקובץ אינדקס.</p>

<h3>ומה שקיבלנו כשהרצנו את זה</h3>

<p><strong>ארבעים מתוך ארבעים התאריכים נכונים.</strong> בדקנו אחד אחד מול רשימה שהוכנה מראש. <strong>בלי טעות אחת, וכל תאריך נקרא מתוך תמונה.</strong></p>

<p>והשמות יצאו כך: <bdi>2025-08-12_הסכם-שכירות_טיוטה-1.pdf</bdi></p>

<p><strong>תאריך, סוג המסמך, הנושא - בדיוק לפי כלל שמות הקבצים שבקובץ הנהלים.</strong> ולא ביקשנו את זה בשום מקום בהוראה. <strong>הוא קרא את הנהלים והחיל אותם.</strong></p>

__FIG_SUMMARY__

<aside class="content-box legal-example">
<h3>והחלק שלא ציפינו לו</h3>
<p>בסוף האינדקס הוא הוסיף <strong>שלושה עשר פריטים ב"טעון בדיקה"</strong>. הוא לא רק תייק - <strong>הוא קרא את המסמכים והשווה ביניהם:</strong></p>
<ul class="bullets">
<li><strong>"בכל ארבעים הקבצים התאריך שבשם הקובץ שונה מהתאריך שבגוף המסמך. התיוק בוצע לפי גוף המסמך."</strong> הוא זיהה שהשמות משקרים, והעדיף את המסמך.</li>
<li>"שתי טיוטות ההסכם נושאות נוסח שונה של סעיף 14, ואין בתיק הסכם חתום."</li>
<li>"שני פרוטוקולים בכותרות זהות ובגוף שונה."</li>
<li>"חסרות קבלות דמי שכירות לחודשיים."</li>
</ul>
<p><strong>אף אחד מהדברים האלה לא כתוב באף מסמך בודד.</strong> הם נמצאים רק בהשוואה בין מסמכים, וכדי לראות אותם צריך להחזיק את כולם בראש באותו רגע.</p>
</aside>

__FIG_FLAGGED__

<aside class="content-box recommendation">
<p><strong>נתקעתם? משהו נראה אחרת ממה שכתוב כאן?</strong> שווה לחזור לפרק <strong>"<bdi dir="ltr">Claude</bdi> מתארח כאן"</strong> - יש סיכוי טוב שהתשובה כבר מחכה שם.</p>
</aside>
</section>

<section class="guide-section" id="ex2">
<span class="section-number">06</span>
<h2>תרגיל 2 · מאות עמודים, ושמונה שורות</h2>

<p><strong>איפה עובדים:</strong> ב-<bdi dir="ltr">VS Code</bdi> · <strong>כמה זמן:</strong> כרבע שעה, וכולה שלו</p>

<h3>המטרה</h3>

<p><strong>פרוטוקולים של ארבעה ימי דיונים.</strong> אתם צריכים מהם דבר אחד: כל מקום שבו נאמר מועד תשלום. <strong>עם מספר עמוד ומספר שורה, כי כך מפנים בסיכומים.</strong></p>

<aside class="content-box info">
<h3>ולמה זה לא חיפוש מילה</h3>
<p>בפרוטוקולים האלה יש <strong>מאות אזכורים של תשלומים בלי מועד</strong>, ו<strong>מאות תאריכים שאינם מועדי תשלום.</strong></p>
<p>מי שיחפש את המילה "תשלום" יקבל ערימה. מי שיחפש תאריכים יקבל ערימה אחרת. <strong>מה שצריך הוא ההצטלבות, וזה דורש להבין מה נאמר ולא רק למצוא מילה.</strong></p>
</aside>

<h3>ההוראה, ולמה היא כתובה ככה</h3>

<ul class="bullets">
<li><strong>"ההפניה חייבת להיות מדויקת".</strong> זו לא קפדנות לשמה: <strong>הפניה שגויה בסיכומים גרועה מהיעדר הפניה.</strong></li>
<li><strong>אמרנו לו מראש שיש הרבה רעש</strong> - תשלומים בלי מועד, תאריכים שאינם תשלומים - <strong>כדי שידע שהמשימה היא להבחין ולא לאסוף.</strong></li>
<li><strong>וביקשנו חלק "טעון בדיקה"</strong> לכל מקום שבו לא היה בטוח. <strong>וזה החלק שהפך למעניין ביותר.</strong></li>
</ul>

<div class="copy-block">
  <div class="copy-heading">
    <strong>ההוראה, להעתקה</strong>
    <button class="copy-button" data-copy-target="ex2-prompt" type="button">העתקת ההוראה</button>
  </div>
  <div class="copy-body" id="ex2-prompt">קרא את CLAUDE.md שבתיקייה ופעל לפי נהלי המשרד שכתובים בו.

בתיקיית המשנה "פרוטוקולים" יש ארבעה קובצי פרוטוקול של ימי דיונים, מאות עמודים בסך הכול. בכל עמוד יש מספר עמוד, ובכל עמוד השורות ממוספרות.

המשימה: אתר כל מקום שבו נאמר בדיון מועד תשלום, כלומר תאריך שבו תשלום כלשהו אמור להתבצע או שנטען שהיה אמור להתבצע.

שים לב: יש בפרוטוקולים הרבה מאוד אזכורים של תשלומים בלי מועד, וגם הרבה תאריכים שאינם מועדי תשלום. מה שמחפשים הוא רק הצטלבות של השניים: תשלום שנקוב לו מועד.

הפק בתיקייה קובץ בשם לפי נהלי המשרד, ובו טבלה של כל מועד תשלום שמצאת, ובה: מספר העמוד, מספר השורה, התאריך שנאמר, מי אמר את זה, וציטוט קצר של המשפט עצמו.

ההפניה לעמוד ולשורה חייבת להיות מדויקת, כי כך מפנים בסיכומים.

ובסוף חלק בשם "טעון בדיקה" לכל מקום שבו לא היית בטוח אם מדובר במועד תשלום.

אל תקבע מה הדין ואל תכתוב מי צודק. עובדות ומקורות בלבד.</div>
  <span class="copy-status" aria-live="polite" aria-atomic="true"></span>
</div>

<h3>מה יקרה אחרי שתדביקו</h3>

<p><strong>הוא יקרא את כל הקבצים, וזה ייקח לו זמן.</strong> אצלנו כרבע שעה על כתשעת אלפים שורות. <strong>זה הזמן ללכת להכין קפה.</strong></p>

__FIG_EX2WORK__

<p>בסוף יהיה בתיקייה קובץ עם טבלה, ובה לכל מועד: עמוד, שורה, התאריך, מי אמר את זה, וציטוט קצר.</p>

<h3>ומה שקיבלנו כשהרצנו את זה</h3>

<p><strong>כשש שורות בטבלה, וכל אחת מהן נכונה.</strong> בדקנו כל הפניה מול הפרוטוקול עצמו: <strong>עמוד ושורה מדויקים, אפס שורות מומצאות.</strong></p>

__FIG_EX2RESULT__

<aside class="content-box info">
<h3>ואם יצא לכם מספר אחר, זה תקין</h3>
<p><strong>הרצנו את זה יותר מפעם אחת, ומספר השורות לא היה זהה.</strong> פעם שש בטבלה ושתיים ב"טעון בדיקה", ופעם חמש ושלוש.</p>
<p><strong>וההבדל אינו טעות.</strong> הוא נובע ממשפט אחד שבאמת אפשר לקרוא בשתי דרכים, ובכל הרצה הוא מוכרע אחרת. <strong>מה שקבוע הוא שכל הפניה מדויקת, ושמה שלא ברור מסומן ולא מוכרע.</strong></p>
<p>אל תספרו שורות. <strong>קראו את הנימוקים.</strong></p>
</aside>

<p>ומה שהוא <strong>לא</strong> הכניס לטבלה אלא ל"טעון בדיקה", עם הנימוק:</p>

<aside class="content-box legal-example">
<p><em>"עמוד 344 שורה 10: 'דרישת התשלום שיצאה מהמשרד שלי נקבה ב-15 במרץ'. לא ברור מלשון האמירה אם 15.03 הוא המועד שנדרש בו התשלום, או התאריך שבו יצאה הדרישה. <strong>יש לבדוק מול דרישת התשלום עצמה.</strong>"</em></p>
<p><em>"עמוד 432 שורה 8: 'בפגישה ב-26 בפברואר סוכם שמכתב הכוונות יימסר לפני התשלום'. <strong>התאריך הוא מועד הפגישה. התשלום נזכר ביחס לסדר, בלי מועד משלו.</strong>"</em></p>
<p><em>"עמוד 530 שורה 25: 'ההצהרה למיסוי הוגשה ב-22 במרץ'. <strong>מועד הגשה, לא מועד תשלום.</strong>"</em></p>
</aside>

<p><strong>ועוד דבר שהוא שם לב אליו ואנחנו לא:</strong> חלק מהשורות בטבלה נוקבות יום וחודש <strong>בלי שנה</strong>, והוא סימן זאת בנפרד. <strong>וגם: הפנייה החוזרת ל"מכתב מיום העשרים ושלושה" נבדקה ולא נכללה</strong>, מפני שהיא תאריך של מכתב ולא של תשלום.</p>

<aside class="content-box recommendation">
<h3>והרגע</h3>
<p><strong>זה לא הטבלה. הטבלה נחמדה.</strong></p>
<p><strong>הרגע הוא שהוא נתקל במשפט דו-משמעי, סירב להכריע, וכתב בדיוק למה ומה צריך לבדוק כדי לדעת.</strong></p>
<p>זה בדיוק מה שאתם רוצים ממתמחה, ובדרך כלל לא מקבלים.</p>
</aside>
</section>

<section class="guide-section" id="ex3">
<span class="section-number">07</span>
<h2>תרגיל 3 · הכול חזר</h2>

<p><strong>איפה עובדים:</strong> ב-<bdi dir="ltr">VS Code</bdi> · <strong>כמה זמן:</strong> כחמש דקות</p>

<h3>המטרה</h3>

<p><strong>זה החשש שעוצר עורכי דין יותר מכל דבר אחר:</strong> "ומה אם הוא יעשה משהו לתיק שלי שאני לא רוצה?"</p>

<p>אז נעשה בדיוק את זה. <strong>ניתן לו לייצר שישה קבצים בתיקייה, ואז נחזיר את הכל אחורה בשתי לחיצות</strong> - ונראה במו עינינו מה בדיוק חוזר.</p>

<h3>ההוראה</h3>

<p><strong>הפעם היא קצרה ופשוטה בכוונה</strong>, כי מה שמעניין אינו התוצר אלא מה שקורה אחריו.</p>

<div class="copy-block">
  <div class="copy-heading">
    <strong>ההוראה, להעתקה</strong>
    <button class="copy-button" data-copy-target="ex3-prompt" type="button">העתקת ההוראה</button>
  </div>
  <div class="copy-body" id="ex3-prompt">עבור על חמשת מסמכי התיק שבתיקייה וקרא אותם. שניים מהם סרוקים, אז פשוט הסתכל על העמודים כמו על תמונה.

לכל אחד מחמשת המסמכים הכן קובץ תקציר נפרד בתיקייה, בשם לפי נהלי המשרד, ובו: מה המסמך, מתי, בין מי למי, ומה העיקר בו בשלוש שורות.

בנוסף הכן קובץ אחד שמרכז את חמשת התקצירים לציר זמן אחד.</div>
  <span class="copy-status" aria-live="polite" aria-atomic="true"></span>
</div>

<h3>מה יקרה אחרי שתדביקו</h3>

<p>הוא יקרא את חמשת המסמכים ויכתוב <strong>שישה קבצים חדשים</strong> - חמישה תקצירים וציר זמן. <strong>תראו אותם מופיעים בסייר הקבצים שבצד.</strong></p>

__FIG_SIXFILES__

<h3>ועכשיו הדבר עצמו</h3>

<ol class="steps">
<li><strong>לחצו פעם אחת בתוך תיבת הכתיבה</strong> של <bdi dir="ltr">Claude</bdi>, כדי שהסמן יהיה שם.</li>
<li><strong>הקישו <bdi dir="ltr">Esc</bdi> פעמיים.</strong></li>
</ol>

<aside class="content-box warning">
<p><strong>וזה חשוב: <bdi dir="ltr">Esc</bdi> כפול עובד רק כשהסמן בתוך תיבת הכתיבה.</strong> אם הפוקוס על סייר הקבצים או על מסמך פתוח, לא יקרה כלום, ותחשבו שאין דבר כזה.</p>
</aside>

<p>ייפתח מסך בשם <bdi dir="ltr">Rewind to...</bdi> ובו רשימת נקודות החזרה. <strong>בחרו את השורה שלפני שהתחיל, והקישו <bdi dir="ltr">Enter</bdi>.</strong></p>

<h3>ומה שיופיע אז הוא כל התרגיל</h3>

<p><strong>מסך שאומר לכם בדיוק מה עומד לקרות, לפני שהוא קורה:</strong></p>

<aside class="content-box legal-example">
<p><strong><bdi dir="ltr">226 lines will be removed and 0 lines will be added across 6 files</bdi></strong></p>
<p><strong>ומתחתיו ששת הקבצים, אחד אחד, בשמם המלא.</strong></p>
<p>ומיד אחריהם שורה שכדאי לקרוא לאט:</p>
<p><em><bdi dir="ltr">Rewinding does not affect files edited manually or via bash.</bdi></em></p>
<p><strong>כלומר: מה שערכתם ביד, או שנעשה מחוץ לו, לא חוזר.</strong> הוא אומר לכם את הגבול של עצמו.</p>
</aside>

__FIG_REWIND__

<p><strong>לחצו <bdi dir="ltr">Continue</bdi>.</strong></p>

<h3>ומה שקרה כשהרצנו את זה</h3>

<p><strong>ששת הקבצים נמחקו, וחמשת מסמכי המקור נשארו בדיוק כפי שהיו.</strong> בדקנו בתיקייה עצמה, לא במסך.</p>

<aside class="content-box warning">
<h3>ודבר אחד שיבלבל אתכם</h3>
<p><strong>סייר הקבצים לא מתרענן מיד.</strong> הקבצים כבר נמחקו, אבל ממשיכים להופיע ברשימה. <strong>לחצו על שם התיקייה או על אייקון הרענון - הם כבר לא שם.</strong></p>
<p>בלי התזכורת הזאת הייתם מסיקים שזה נכשל.</p>
</aside>

<aside class="content-box recommendation">
<h3>והרגע</h3>
<p><strong>הבקשה שלכם חוזרת לתיבת הכתיבה, מוכנה לעריכה.</strong></p>
<p><strong>וזה בעצם כל הרעיון.</strong> זו לא פעולת "בטל", זו פעולת <strong>"נסה שוב אחרת"</strong>: הכל חזר למקום, והבקשה מחכה לכם כדי שתשנו בה מילה ותשלחו שוב.</p>
</aside>
</section>

<section class="guide-section" id="ex4">
<span class="section-number">08</span>
<h2>תרגיל 4 · הוא בודק את עצמו</h2>

<p><strong>איפה עובדים:</strong> ב-<bdi dir="ltr">VS Code</bdi> · <strong>כמה זמן:</strong> כרבע שעה</p>

<h3>המטרה</h3>

<p>עד עכשיו הוא עשה עבודה ואתם בדקתם אותה. <strong>הפעם נבקש ממנו לבדוק את עצמו.</strong></p>

<p>שני שלבים: קודם הוא בונה טבלה של ארבעים מסמכים, <strong>ואז פותח עשרים מהם מחדש ומוודא מול המסמך עצמו שמה שכתב נכון.</strong> ומתקן מה שלא.</p>

<aside class="content-box info">
<h3>וזה ההבדל האמיתי בין צ׳אט לבין מה שיושב מולכם</h3>
<p><strong>צ׳אט לא חוזר למסמך אחרי שענה. אין לו למה לחזור.</strong> התשובה שלו היא מה שהוא זוכר מהרגע שקרא.</p>
<p>כאן המסמכים נשארים בתיקייה, <strong>והוא יכול לפתוח אותם שוב ולהשוות.</strong></p>
</aside>

<h3>ההוראה, ולמה היא כתובה ככה</h3>

<ul class="bullets">
<li><strong>"בחר עשרים באקראי".</strong> לא "בדוק את כולם" - כי אז זו סתם עבודה כפולה. <strong>מדגם מקרי הוא איך שבודקים באמת.</strong></li>
<li><strong>"תקן בטבלה עצמה".</strong> לא מספיק לדווח על טעות. <strong>שיתקן אותה.</strong></li>
<li><strong>ודוח נפרד</strong> שאומר כמה נבדקו, כמה נמצאו, ומה תוקן. <strong>בלי זה אין לכם דרך לדעת שהבדיקה בכלל קרתה.</strong></li>
</ul>

<div class="copy-block">
  <div class="copy-heading">
    <strong>ההוראה, להעתקה</strong>
    <button class="copy-button" data-copy-target="ex4-prompt" type="button">העתקת ההוראה</button>
  </div>
  <div class="copy-body" id="ex4-prompt">בתיקיית המשנה "סרוקים-לתיוק" יש ארבעים מסמכים סרוקים. כולם תמונה בלבד, אין בהם טקסט להעתקה. פשוט הסתכל על כל עמוד כמו על תמונה וקרא מה כתוב בו. אל תחפש תוכנות פענוח ואל תתקין כלום.

קרא את CLAUDE.md שבתיקייה ופעל לפי נהלי המשרד שכתובים בו.

השלב הראשון: בנה טבלה של כל ארבעים המסמכים, ובה לכל מסמך: שם הקובץ, סוג המסמך, התאריך שמופיע בגוף המסמך, והנושא במילים ספורות. שמור אותה בקובץ בתיקייה, בשם לפי נהלי המשרד.

השלב השני, וזה העיקר: אחרי שסיימת את הטבלה, בחר עשרים מסמכים באקראי מתוך הארבעים, פתח כל אחד מהם שוב, ובדוק מול המסמך עצמו אם מה שכתבת בטבלה נכון.

לכל אחד מהעשרים כתוב: מה כתבת בטבלה, מה כתוב במסמך, והאם זה תואם. כל מקום שאינו תואם - תקן בטבלה עצמה.

ובסוף הפק דוח קצר בקובץ נפרד ובו: כמה מסמכים נבדקו, בכמה מהם נמצאה אי-התאמה, מה בדיוק תוקן בכל אחד, ומה נשאר לא ברור.

אל תשנה, תמחק או תשנה שם לאף מסמך מקור.</div>
  <span class="copy-status" aria-live="polite" aria-atomic="true"></span>
</div>

<h3>מה יקרה אחרי שתדביקו</h3>

<p><strong>תראו אותו עובד פעמיים.</strong> קודם קורא ארבעים מסמכים ובונה טבלה, <strong>ואז חוזר ופותח מסמכים בפעם השנייה.</strong> זה החלק ששווה להסתכל בו.</p>

<p>בסוף יהיו בתיקייה שני קבצים: הטבלה, ודוח הבדיקה.</p>

__FIG_EX4BEFORE__

<h3>וזה הרגע שבשבילו עשינו את התרגיל</h3>

__FIG_EX4RECHECK__

<p>הוא לא הסתפק בקריאה חוזרת של מה שכבר חילץ. <strong>הוא חילץ את התמונות מחדש, לתיקייה נפרדת, כדי שההשוואה תהיה מול המסמך ולא מול הזיכרון שלו.</strong> וגם ספר שבכל אחד מארבעים הקבצים יש עמוד אחד ותמונה אחת, כלומר שלא נשאר בהם תוכן שלא נקרא.</p>

<h3>ומה שקיבלנו כשהרצנו את זה</h3>

<p><strong>עשרים נבדקו. שמונה עשרה תאמו. שתיים לא.</strong></p>

__FIG_EX4SUMMARY__

<aside class="content-box legal-example">
<h3>ואחת מהשתיים אינה זניחה בכלל</h3>
<p>בטבלה הוא כתב שהמזגן הותקן <strong>"ובנוכחותו"</strong>, כלומר בנוכחות המשכיר.</p>
<p>במסמך עצמו כתוב <strong>"ובנוכחות שכן".</strong></p>
<p><strong>ובתיק הזה, מי נכח בהתקנה הוא בדיוק מה ששנוי במחלוקת.</strong> הוא תפס את זה בסבב השני, כתב שאין מדובר באותה עובדה, ותיקן בטבלה.</p>
<p><em>ואנחנו פתחנו את הסריקה עצמה ובדקנו. כתוב בה בדיוק כפי שהוא אמר.</em></p>
</aside>

<aside class="content-box info">
<h3>ואם יצא לכם מספר אחר, זה תקין</h3>
<p><strong>העשרים נבחרים בהגרלה, ולכן כל הרצה בודקת מסמכים אחרים.</strong> אצלנו יצאו פעם עשרים מתוך עשרים תואמים, ופעם שמונה עשרה מתוך עשרים.</p>
<p><strong>מה שקבוע הוא לא המספר.</strong> קבוע זה שהוא חוזר למסמכים, מדווח על כל אחד בנפרד, ומתקן את מה שמצא.</p>
</aside>

<h3>והרגע, והוא לא הטבלה</h3>

<p>בסוף הדוח הוא הוסיף מיוזמתו, בלי שנשאל:</p>

<aside class="content-box recommendation">
<p><em>"הערה על תוקף הבדיקה: <strong>אני זה שכתב את הטבלה ואני זה שבדק אותה</strong>, ולכן טעות קריאה שחזרה על עצמה בשני הסבבים לא הייתה מתגלה כאן."</em></p>
<p><strong>הוא אמר לכם את המגבלה של הבדיקה שהוא עצמו ביצע.</strong></p>
<p>לא "בדקתי והכל תקין", אלא <strong>"בדקתי, וזה מה שהבדיקה שלי לא יכולה לתפוס".</strong> זה בדיוק מה שאתם רוצים ממתמחה, ובדרך כלל לא מקבלים.</p>
</aside>

<p><strong>ובנוסף שלוש הערות תפעוליות שהוא הוסיף:</strong> ששמות הקבצים מטעים ולכן תייק לפי גוף המסמך · ששתי טיוטות ההסכם נושאות נוסח סותר לסעיף 14 ואין בתיק הסכם חתום · <strong>ושלושה מסמכים נסרקו כתמונת ראי, שהוא קרא אותם בכיוון ההפוך והמליץ לאמת מול המקור.</strong></p>

<p><strong>ובסוף, שני הקבצים בתיקייה:</strong> הטבלה המתוקנת, ודוח הבדיקה.</p>

__FIG_EX4FILES__
</section>

<section class="guide-section" id="ex5">
<span class="section-number">09</span>
<h2>תרגיל 5 · הוא בונה כלי שעובד</h2>

<p><strong>איפה עובדים:</strong> ב-<bdi dir="ltr">VS Code</bdi> · <strong>כמה זמן:</strong> כשבע דקות</p>

<h3>המטרה</h3>

<p>בהסכם המכר שבתיקייה יש סעיף 4.1: <strong>הערת אזהרה תירשם תוך שבעה ימי עסקים ממועד החתימה.</strong></p>

<p><strong>ושבעה ימי עסקים זה לא שבעה ימים.</strong> צריך לדלג על שישי ושבת, ועל חגים, ולספור. <strong>וזה בדיוק הדבר שנופלים בו כשסופרים ביד</strong>, ושאף אחד לא רוצה לעשות פעמיים.</p>

<p><strong>אז נבקש ממנו לבנות דף שעושה את זה.</strong> מזינים תאריך חתימה, ומקבלים את המועד ואת כל לוח העסקה.</p>

<h3>ההוראה, ולמה היא ארוכה</h3>

<p><strong>זו ההוראה הארוכה ביותר במדריך, ובכוונה.</strong> כשמבקשים כלי ולא תשובה, כל דבר שלא תבקשו במפורש - לא יהיה שם.</p>

<ul class="bullets">
<li><strong>"בורר תאריכים, ולא פורמט אמריקאי".</strong> בלי זה מי שיקליד <bdi dir="ltr">04/02</bdi> ויתכוון ל-4 בפברואר יקבל חישוב על 2 באפריל, <strong>ולא יידע.</strong></li>
<li><strong>"אם אינך יודע אילו חגים חלים, אל תנחש".</strong> חג שגוי בחישוב משפטי גרוע מהיעדר חג.</li>
<li><strong>"דווח על חג רק אם הוא באמת השפיע".</strong> על השורה הזאת נרחיב עוד רגע.</li>
<li><strong>"אל תוסיף כפתור חשב".</strong> כפתור שלא עושה כלום גרוע מהיעדר כפתור, <strong>כי אינכם יודעים אם מה שמוצג מעודכן.</strong></li>
</ul>

<div class="copy-block">
  <div class="copy-heading">
    <strong>ההוראה, להעתקה</strong>
    <button class="copy-button" data-copy-target="ex5-prompt" type="button">העתקת ההוראה</button>
  </div>
  <div class="copy-body" id="ex5-prompt">בתיקייה יש הסכם מכר. קרא אותו.

בנה לי דף שאפשר לפתוח בדפדפן בלחיצה כפולה, ושבו מזינים תאריך חתימה של עסקה ומקבלים את לוח המועדים שלה במלואו, לפי המנגנונים שבהסכם הזה.

הדף צריך:

לקבל תאריך חתימה בשלושה שדות נפרדים: יום, חודש, שנה. אל תשתמש בשדה תאריך של הדפדפן, כי הוא מוצג לפי שפת הדפדפן ולא לפי שפת הדף, ומי שהדפדפן שלו באנגלית יראה חודש לפני יום.

ומיד ליד השדות הצג את התאריך שנבחר במילים, למשל "4 בפברואר 2026, יום רביעי", כדי שאפשר יהיה לוודא בעין שלא הוזן תאריך אחר.

לחשב את המועד לרישום הערת אזהרה לפי סעיף 4.1, כלומר שבעה ימי עסקים ממועד החתימה. ימי עסקים בישראל אינם כוללים שישי, שבת וחגים.

לאפשר להוסיף ימי חג ושבתון, וגם הם ייבחרו בבורר תאריכים ולא יוקלדו. אפשר להוסיף כמה, ואפשר להסיר. אם אינך יודע בוודאות אילו חגים חלים, אל תנחש: כתוב בדף איזו הנחה הנחת.

לדווח על ימי חג רק אם הם נפלו בתוך תקופת הספירה והשפיעו עליה בפועל. אם הוזן חג שאינו רלוונטי, אמור זאת בנפרד ובמפורש. אל תדווח שהוצא חג כשהתוצאה זהה לחישוב בלי חגים.

להציג את כל מועדי התשלום ואת מועד המסירה שבהסכם, עם הסכומים והשיעורים, ולסמן כל מועד שכבר חלף.

להציג טבלה שמראה את ספירת שבעת ימי העסקים יום אחר יום, עם הסיבה לכל דילוג.

ולעבוד בעברית, מימין לשמאל, בלי חיבור לאינטרנט ובלי שום התקנה.

אל תוסיף כפתור "חשב". התוצאה צריכה להתעדכן לבד בכל שינוי.

שמור אותו בתיקייה בשם לפי נהלי המשרד, עם סיומת html.

בסוף כתוב לי בקצרה מה בנית, איזה סעיף בהסכם עומד מאחורי כל חישוב, ומה לא הצלחת לוודא.

אל תשנה, תמחק או תשנה שם לאף מסמך קיים בתיקייה.</div>
  <span class="copy-status" aria-live="polite" aria-atomic="true"></span>
</div>

<h3>מה יקרה אחרי שתדביקו</h3>

<p>הוא יקרא את ההסכם ויכתוב קובץ אחד עם סיומת <bdi dir="ltr">html</bdi>. <strong>לחיצה ימנית עליו בסייר ← <bdi dir="ltr">Reveal in File Explorer</bdi> ← לחיצה כפולה, והוא נפתח בדפדפן.</strong></p>

<h3>וכך נראה הדף כשהוא נפתח</h3>

__FIG_EX5PAGE__

<p><strong>שימו לב לשורת הכתובת שלמעלה.</strong> כתוב בה <bdi dir="ltr">File</bdi> ואחריו נתיב במחשב שלכם. <strong>הדף הזה אינו אתר ואינו מחובר לאינטרנט</strong> - הוא קובץ אחד שיושב בתיקיית התיק, ואפשר לשלוח אותו במייל כמו כל מסמך.</p>

<h3>שדה התאריך, ולמה הוא נראה ככה</h3>

__FIG_EX5FIELDS__

<p><strong>שלושה שדות נפרדים, ולידם התאריך במילים.</strong> ביקשנו את זה בהוראה במפורש, כי שדה התאריך הרגיל של הדפדפן מוצג לפי שפת הדפדפן: <strong>מי שהדפדפן שלו באנגלית יראה חודש לפני יום, ו-4 בפברואר ייקרא כ-2 באפריל.</strong> בלוח מועדים זו טעות שאי אפשר להרשות.</p>

<h3>ומה שקיבלנו כשהרצנו את זה</h3>

<p><strong>דף עובד, ואימתנו כל מספר שבו ביד.</strong></p>

__FIG_EX5RESULT__

<p>וכשמשנים את התאריך, המספר משתנה: <strong>חתימה ב-4 בפברואר נותנת 15.02.2026, וחתימה ב-15 במאי נותנת 25.05.2026.</strong> ספרנו את שניהם ביד מול לוח שנה, ושניהם נכונים כולל שם היום.</p>

<h3>ואפשר לבדוק אחריו, יום אחר יום</h3>

__FIG_EX5DAYCOUNT__

<p><strong>זה ההבדל בין כלי שאומר לכם מספר לבין כלי שאפשר לבדוק.</strong> לא צריך להאמין לו, אפשר לספור אחריו.</p>

<h3>ודבר אחד שהוא סירב לעשות</h3>

__FIG_EX5NOTE__

<p><strong>כשהזנו תאריך שונה מזה שבהסכם, הוא לא הזיז את שאר המועדים.</strong> הוא הסביר שמועדי התשלום והמסירה נקובים בהסכם כתאריכי לוח קבועים, ושאין בו נוסחה שמזיזה אותם לפי מועד החתימה.</p>

<p><strong>הוא יכול היה בקלות "לחשב" אותם מחדש ולהיראות חכם יותר.</strong> הוא העדיף לומר מה הוא לא יודע.</p>

<p>חתימה ב-04.02 נותנת 15.02 · ב-05.01 נותנת 14.01 · ב-08.01 נותנת 19.01 · ב-02.04 נותנת 13.04. <strong>ספירת ימי עסקים אמיתית, לא שבעה ימי לוח.</strong> וכל התאריכים, הסכומים והאחוזים בלוח המלא נכונים.</p>

<aside class="content-box legal-example">
<h3>ושתי התנהגויות ששוות יותר מהדף</h3>
<p><strong>הוא סירב לנחש על חגים:</strong> <em>"לא אימתתי אילו חגים חלים ב-2026, ולכן לא הנחתי דבר. החישוב מדלג על שישי ושבת בלבד."</em> <strong>ובנה שדה למי שיודע, במקום להמציא תשובה.</strong></p>
<p><strong>והוא תיקן את הבקשה שלנו:</strong> כתבנו "שלושת מועדי התשלום", והוא ענה שההסכם מונה <strong>ארבעה</strong> - הרביעי הוא היתרה במסירה - <strong>והציג את כולם.</strong></p>
</aside>

<h3>ועכשיו החלק שבגללו התרגיל הזה אחרון</h3>

<p><strong>בגרסה הראשונה שבנינו מצאנו שלושה ליקויים.</strong> ואת שלושתם מצאנו כי בדקנו, לא כי הוא אמר.</p>

<ul class="bullets">
<li><strong>כפתור שלא עשה כלום.</strong> התוצאה התעדכנה לבד ממילא.</li>
<li><strong>שני שדות תאריך זה ליד זה, בשני פורמטים הפוכים.</strong></li>
<li><strong>ובאג של ממש:</strong> הדף כתב "הוצאו מהספירה ימי חג" גם כשהחג היה מחוץ לתקופה ולא השפיע כלל. <strong>ורק טבלת הספירה יום אחר יום הוכיחה זאת</strong> - אותו יום הופיע בה כיום עסקים רגיל.</li>
</ul>

<aside class="content-box recommendation">
<h3>והרגע</h3>
<p><strong>הוא בנה כלי שמראה את עבודתו.</strong> לא רק תוצאה, אלא ספירה מלאה שאפשר לבדוק שורה-שורה - <strong>ובזכותה תפסנו טעות שהסיכום שלו הסתיר.</strong></p>
<p><strong>וזה המסר של המדריך כולו:</strong> לא "הוא בנה, אז זה נכון", אלא <strong>"הוא בנה, וגם נתן לי איך לבדוק - אז בדקתי, ומצאתי".</strong></p>
<p>ההוראה שלמעלה כבר כוללת את שלושת התיקונים. <strong>אתם מקבלים את הגרסה שעברה בדיקה.</strong></p>
</aside>
</section>

<section class="guide-section" id="why">
<span class="section-number">02</span>
<h2>למה זה שונה מכל מה שעשיתם עד כאן</h2>

<p>בכל מה שלמדתם עד עכשיו, וגם בכל מה שאתם מכירים מהעבודה בדפדפן, אתם נמצאים בקצה אחד: אתם כותבים, אתם ממתינים, אתם מקבלים. תמיד יש בן אדם שיוזם.</p>

<p><strong>כאן אין בן אדם.</strong> יש מועד, ויש עבודה שנעשית בלי אף אחד בחדר.</p>

<p>זה ההבדל בין תוכנה שעונה לכם, לבין תוכנה שעובדת אצלכם.</p>

<aside class="content-box recommendation">
<h3>ולכן בפרק הזה לא נכתוב שום דבר בחלונית השיחה</h3>
<p>בכל התרגילים עד כאן הדבקתם בקשה בחלונית, לחצתם, וראיתם תשובה. <strong>כאן לא.</strong></p>
<p>במקום זה נמלא טופס קצר, <strong>ובתוכו שדה אחד שהוא הבקשה עצמה.</strong> נכתוב אותה פעם אחת, והיא תרוץ שוב ושוב - כל יום ראשון, או בכל מועד שתבחרו - בלי שאף אחד יקליד אותה מחדש.</p>
<p><strong>אל תחפשו איפה להדביק פרומפט. אין כזה בפרק הזה, וזו כל הנקודה.</strong></p>
</aside>

<aside class="content-box info">
<h3>ולמה דווקא רשימת מועדים</h3>
<p>כי זה מה שקורה לתיק אחרי שסוגרים אותו: לא שוכחים אותו, פשוט לא פותחים אותו יותר. עד שמישהו מהצד השני מזכיר. משימה שעוברת על התיק כל שבוע היא הדבר הכי קרוב לעין שנשארת פקוחה.</p>
</aside>
</section>

<section class="guide-section" id="open">
<span class="section-number">02</span>
<h2>פותחים את המסך הנכון</h2>

<p><strong>למעלה, ליד <bdi dir="ltr">Home</bdi>, לחצו על <bdi dir="ltr">Code</bdi>.</strong> זו אותה אפליקציה שאתם מכירים, וזה הצד שבו יושב <bdi dir="ltr">Claude Code</bdi>.</p>

<p><strong>ואז בסרגל הצד לחצו <bdi dir="ltr">More</bdi>, ואחריו <bdi dir="ltr">Routines</bdi>.</strong></p>

__SHOT_283__

__SHOT_278__

<aside class="content-box warning">
<h3>שימו לב שאתם במקום הנכון</h3>
<p>בצד של <bdi dir="ltr">Home</bdi> יש בסרגל קטגוריה בשם <bdi dir="ltr">Scheduled</bdi>. היא נראית בדיוק כמו מה שאנחנו מחפשים, <strong>והמשימה שלכם לא תופיע בה לעולם.</strong> אלה שתי מערכות נפרדות שאינן מדברות ביניהן. אם הגעתם למסך שכתוב בו <bdi dir="ltr">No scheduled tasks yet</bdi> - אתם בצד הלא נכון.</p>
</aside>

__FIG_WRONGSCREEN__


</section>

<section class="guide-section" id="local">
<span class="section-number">03</span>
<h2><bdi dir="ltr">Local</bdi>, ולא ענן</h2>

<p>בפינה למעלה יש <bdi dir="ltr">New routine</bdi> ולידו חץ קטן.</p>

<p><strong>לחצו על החץ, ובחרו <bdi dir="ltr">Local</bdi>.</strong> לא על הכפתור עצמו, ולא על תיבת הכתיבה הגדולה שבאמצע הדף.</p>

__SHOT_284__

__FIG_LOCALCLOUD__

<aside class="content-box warning">
<h3>למה זה קריטי</h3>
<p>תיבת הכתיבה שבאמצע הדף בונה משימה שרצה בענן, <strong>ומשימת ענן אינה רואה את הקבצים שעל המחשב שלכם.</strong> תקבלו משהו שנראה בדיוק כמו הדבר הנכון, שירוץ יפה, ושידווח לכם שלא מצא כלום.</p>
<p><strong>איך מזהים שטעיתם:</strong> אם בטופס יש <bdi dir="ltr">Select a repository</bdi> או <bdi dir="ltr">Select a cloud environment</bdi>, ואין בו שדה לבחירת תיקייה - זו משימת ענן. לחצו <bdi dir="ltr">Cancel</bdi> והתחילו מהחץ.</p>
</aside>

__SHOT_285__
</section>

<section class="guide-section" id="form">
<span class="section-number">04</span>
<h2>ממלאים ארבעה שדות</h2>

<p>זה הטופס הנכון. יש בו שדה לבחירת תיקייה, בורר מודל, ואפשרות <bdi dir="ltr">Manual</bdi> בשורת התזמון.</p>

__SHOT_287__

<h3>השדה הראשון, ורק הוא באנגלית</h3>

<div class="copy-block">
  <div class="copy-heading">
    <strong><bdi dir="ltr">Name</bdi></strong>
    <button class="copy-button" data-copy-target="ch-name" type="button">העתקה</button>
  </div>
  <div class="copy-body" id="ch-name">deadlines-birosh</div>
  <span class="copy-status" aria-live="polite" aria-atomic="true"></span>
</div>

<aside class="content-box warning">
<h3>השדה הזה אינו מקבל עברית</h3>
<p>הוא הופך את מה שתכתבו לשם תיקייה במחשב, ומעברית לא נשאר לו דבר. אם תכתבו בעברית תקבלו שורה אדומה: <bdi dir="ltr">Name must contain at least one letter or number</bdi>. <strong>זה השדה היחיד בטופס שחייב להיות באנגלית. כל השאר בעברית.</strong></p>
</aside>

__SHOT_288__

<h3>שני השדות הבאים, בעברית</h3>

<div class="copy-block">
  <div class="copy-heading">
    <strong><bdi dir="ltr">Description</bdi></strong>
    <button class="copy-button" data-copy-target="ch-desc" type="button">העתקה</button>
  </div>
  <div class="copy-body" id="ch-desc">איתור כל מועד מחייב בתיק והפקת קובץ מה נדרש</div>
  <span class="copy-status" aria-live="polite" aria-atomic="true"></span>
</div>

<h3>ההוראה עצמה, ומה ביקשנו בה</h3>

<p>זו הבקשה שהמשימה תבצע בכל פעם שהיא רצה. <strong>לפני שאתם מדביקים אותה, שווה שתדעו מה כתוב בה</strong> - כי ביום שתרצו לשנות אותה לתיק שלכם, תדעו איפה לגעת.</p>

<ul class="bullets">
<li><strong>"קרא את <bdi dir="ltr">CLAUDE.md</bdi> ופעל לפי נהלי המשרד".</strong> שורה אחת שחוסכת לנו לחזור על כל הכללים בכל בקשה: איך כותבים תאריכים, איך קוראים לקבצים, ומה חייב להופיע בכל תוצר.</li>
<li><strong>"הסתכל על העמודים הסרוקים כמו על תמונה".</strong> בלי המשפט הזה הוא יוצא לחפש במחשב תוכנות שמפענחות סריקות, ומבזבז זמן על משהו שהוא יודע לעשות בעצמו.</li>
<li><strong>שתי טבלאות, ולא אחת.</strong> הראשונה היא מה שעוד לפנינו. <strong>השנייה, החשובה, היא מועדים שכבר חלפו ואין במסמכים אסמכתה שהם בוצעו</strong> - וזה מה שלא רואים בשום מסמך בודד.</li>
<li><strong>"אל תקבע מה הדין ואל תכתוב מי צודק".</strong> אנחנו רוצים עובדות, מקורות ופערים. <strong>ההכרעה נשארת אצלכם.</strong></li>
</ul>

<p>העתיקו בלחיצה, והדביקו בשדה <bdi dir="ltr">Instructions</bdi>:</p>

<div class="copy-block">
  <div class="copy-heading">
    <strong><bdi dir="ltr">Instructions</bdi></strong>
    <button class="copy-button" data-copy-target="ch-instr" type="button">העתקת ההוראה</button>
  </div>
  <div class="copy-body" id="ch-instr">__INSTR__</div>
  <span class="copy-status" aria-live="polite" aria-atomic="true"></span>
</div>

<aside class="content-box info">
<h3>ומה יקרה אחרי שתדביקו</h3>
<p>שום דבר, עדיין. <strong>ההוראה רק נשמרת.</strong> היא תתחיל לעבוד רק כשתלחצו <bdi dir="ltr">Create</bdi> ואחריו <bdi dir="ltr">Run now</bdi>, ואת זה נעשה בעוד רגע.</p>
<p>וכשזה יקרה: תיפתח שיחה לבדה, היא תעבוד כשלוש דקות, <strong>ובסוף יופיע בתיקייה קובץ חדש</strong> ובו שתי הטבלאות והחלק של "טעון בדיקה". <strong>שם הקובץ ייצא לפי נהלי המשרד</strong> בלי שביקשנו את זה בשום מקום.</p>
</aside>

<h3>והשדה שתשכחו</h3>

<p><strong><bdi dir="ltr">Select folder</bdi></strong> נמצא מתחת לתיבת ההוראות, בפינה השמאלית התחתונה שלה. בחרו את התיקייה <bdi>תיק-הברוש-14-לתרגול</bdi> שהורדתם.</p>

<aside class="content-box warning">
<h3>וכשתשכחו אותו, לא תקבלו הודעת שגיאה</h3>
<p>הכפתור <bdi dir="ltr">Create</bdi> פשוט יישאר אפור. <strong>הוא אפור כל עוד לא נבחרה תיקייה</strong>, ואין שום דבר על המסך שיאמר לכם את זה.</p>
</aside>

<ul class="bullets">
<li><strong>באותה שורה, בצד השני,</strong> כתוב <bdi dir="ltr">Sonnet 5</bdi>. לחצו ובחרו <bdi dir="ltr">Opus 5</bdi>. המשימה צריכה לקרוא מסמכים סרוקים ולהצליב תאריכים בין חמישה מסמכים, וזה לא המקום לחסוך.</li>
<li><strong>בשורת <bdi dir="ltr">Schedule</bdi></strong> לחצו <bdi dir="ltr">Manual</bdi>, הראשון בשורה. השורה <bdi dir="ltr">At 09:00</bdi> תיעלם, וזה נכון: משימה שרצה רק כשלוחצים עליה. במשרד תבחרו כאן <bdi dir="ltr">Weekly</bdi> ותקבעו יום ושעה.</li>
<li><strong><bdi dir="ltr">Worktree</bdi></strong> - להשאיר ריק.</li>
</ul>

__FIG_GREYCREATE__

<p>כך נראה הטופס כשהוא מוכן, והכפתור <bdi dir="ltr">Create</bdi> נדלק:</p>

__SHOT_291__
</section>

<section class="guide-section" id="run">
<span class="section-number">05</span>
<h2><bdi dir="ltr">Create</bdi>, ואז <bdi dir="ltr">Run now</bdi></h2>

<p>בדף שנפתח, למעלה בקצה, יש כפתור שחור: <strong><bdi dir="ltr">Run now</bdi></strong>.</p>



<p><strong>ומכאן אתם לא עושים כלום.</strong></p>

<p>תוך שניות תקפוץ התראה בפינת המסך, <bdi dir="ltr">Scheduled task started</bdi>, ובסרגל תיפתח שיחה חדשה בלי שפתחתם אותה. לחצו עליה והסתכלו.</p>

<p><strong>זו הפעם הראשונה שאתם רואים את <bdi dir="ltr">Claude</bdi> עובד כשלא כתבתם כלום.</strong></p>

__SHOT_282__

<aside class="content-box recommendation">
<h3>אם היא עוצרת ומופיעה בקשת אישור</h3>
<p>אשרו, ואם יש שם האפשרות <bdi dir="ltr">always allow</bdi> - בחרו דווקא בה.</p>
<p><strong>וזו הסיבה שאנחנו מריצים עכשיו ולא ביום ראשון. ההרצה הראשונה איננה בדיקה, היא ההרשאה.</strong> האישורים שתיתנו נשמרים על המשימה עצמה, ומהרגע הזה היא רצה לבדה בלי לעצור. משימה שלא עברה את ההרצה המושגחת הזאת תיתקע בשלוש לפנות בוקר ותמתין לכם עד הבוקר, ובבוקר לא יהיה קובץ ולא תדעו למה.</p>
<p>בדף המשימה יש קטגוריה בשם <bdi dir="ltr">Always allowed</bdi>, וכתוב בה שאישורים שתיתנו יופיעו שם. <strong>כל עוד היא ריקה, המשימה עלולה להיעצר.</strong></p>
</aside>

__PLACEHOLDER_PERM__

<p><strong>איך יודעים שהיא סיימה:</strong> הסיבוב בתחתית השיחה נעלם, והיא כותבת סיכום של מה שעשתה. הקובץ יושב בתיקייה.</p>

__PLACEHOLDER_DONE__
</section>

<section class="guide-section" id="result">
<span class="section-number">06</span>
<h2>מה היא החזירה, ולמה זה מרשים</h2>

<p>בהרצה שלנו הקובץ נכתב שלוש דקות אחרי הלחיצה. בתוכו שתי טבלאות ועשרה סעיפי "טעון בדיקה", וכל שורה עם התאריך, מה נדרש, מי הצד החייב, ומאיזה מסמך ומאיזה סעיף.</p>

<h3>ושלושה דברים ששווה לעצור עליהם</h3>

<p><strong>האחד, שם הקובץ.</strong> לא כתבנו לה מילה על פורמט תאריכים או על מבנה שמות. כתבנו שורה אחת: "קרא את <bdi dir="ltr">CLAUDE.md</bdi> ופעל לפי נהלי המשרד". הקובץ יצא בשם <bdi>2026-08-14_ריכוז-מועדים_תיק-הברוש-14</bdi> - תאריך במבנה שנה-חודש-יום, קו תחתון, סוג המסמך, קו תחתון, הנושא. <strong>בדיוק לפי הנהלים.</strong> כלומר כל מי שיפעיל את זה במשרד יקבל את אותה תבנית. גם מתמחה. גם בשלוש לפנות בוקר.</p>

<p><strong>השני, מה שהיא הוציאה מהסרוקים.</strong> מספר האסמכתה של הערת האזהרה, <bdi dir="ltr">41982/2026</bdi>, והמשכנתה של 1,180,000 ש"ח לטובת בנק לאומי מ-19.06.2019. שניהם קיימים רק בנסח הטאבו הסרוק, שהוא תמונה. אין בו טקסט. <bdi dir="ltr">Ctrl+F</bdi> לא מוצא בו כלום. <strong>היא הסתכלה על העמוד וקראה אותו.</strong></p>

<p><strong>והשלישי, מה שאין.</strong> הטבלה השנייה היא מועדים שכבר חלפו ואין במסמכים אסמכתה שבוצעו. <strong>אף אחד מהפערים האלה אינו כתוב באף מסמך.</strong> הם נמצאים רק במרווח שבין מסמך אחד לשני.</p>

<aside class="content-box legal-example">
<h3>והדוגמה שממחישה את זה</h3>
<p>התאריך 15.06.2026, המועד להמצאת מכתב הכוונות, <strong>אינו מופיע בשום מסמך בתיק.</strong> הוא נגזר מכלל שנקבע בפרוטוקול, שלושים יום לפני התשלום השלישי, ומהמועד שנקבע בהסכם.</p>
<p><strong>והיא כתבה את זה במפורש:</strong> שהתאריך אינו נקוב, שהוא מחושב, ושאם ישתנה מועד התשלום השלישי ישתנה גם הוא.</p>
<p>וגם: היא כתבה מה היא לא בדקה - שלוש תיקיות המשנה שבתיק, שלא נסקרו, וייתכן שיש בהן מועדים נוספים.</p>
</aside>
</section>

<section class="guide-section" id="truth">
<span class="section-number">07</span>
<h2>מה שחייבים לדעת לפני שסומכים על זה</h2>

<p><strong>שלושה תנאים, וכולם מתקיימים או שכלום לא קורה:</strong></p>

<ul class="checklist">
<li>האפליקציה פתוחה. גם בשורת המשימות, לא חייבת להיות על המסך.</li>
<li>המחשב ער.</li>
<li>ולמשימה יש הרשאות מוכנות מראש, מההרצה המושגחת.</li>
</ul>

<aside class="content-box warning">
<h3>ומה קורה כשהמחשב היה ישן</h3>
<p>האפליקציה בודקת בהפעלה אם פוספסו הרצות בשבעת הימים האחרונים, ומריצה <strong>אחת בלבד</strong> - את האחרונה שפוספסה. משימה יומית שפוספסה שישה ימים תרוץ פעם אחת.</p>
<p><strong>ולכן משימה שנקבעה לתשע בבוקר עלולה לרוץ באחת עשרה בלילה.</strong> אם העיתוי חשוב לכם, כתבו את זה לתוך ההוראה עצמה. למשל: "אם השעה אחרי חמש אחר הצהריים, אל תפיק את הקובץ אלא רק סכם מה פוספס".</p>
</aside>

<p><strong>ואיפה בודקים אם היא רצה:</strong> בדף המשימה יש <bdi dir="ltr">History</bdi>, ובו כל ההרצות כולל אלה שדולגו. מעבירים עכבר על שורה מדולגת ורואים למה: המחשב היה ישן, ההרצה הקודמת עוד לא הסתיימה, או שרצו באותו רגע משימות אחרות.</p>

<aside class="content-box info">
<h3>ודבר אחד שיבלבל אתכם</h3>
<p>משימה שהסתיימה נעלמת מהרשימה. יש בדף <bdi dir="ltr">Routines</bdi> מתג בשם <bdi dir="ltr">Include completed</bdi>, <strong>והוא חוזר לכבוי בכל כניסה.</strong> אם המשימה שלכם "נעלמה" - הדליקו אותו.</p>
</aside>

__FIG_INCLUDECOMPLETED__

<aside class="content-box warning">
<h3>ושני דברים שיפילו לכם את המשימה ביום שתכתבו אחת משלכם</h3>
<p><strong>לכל הרצה אין זיכרון.</strong> לא מהשיחה שבה הגדרתם את המשימה, ולא מההרצה של אתמול. <strong>"תבדוק כמו שסיכמנו" לא יעבוד,</strong> כי אין "סיכמנו". ההוראה צריכה לעמוד לבדה, כאילו נתתם אותה למישהו שרואה את התיק בפעם הראשונה.</p>
<p><strong>וצריך לכתוב מה קורה כשאין ממצאים.</strong> בלי זה תקבלו בכל יום פסקה מנומסת שמסבירה שהכל בסדר, ותוך שבוע תפסיקו לפתוח את הקובץ. <strong>כתבו במפורש: אם אין ממצאים, כתוב שורה אחת שאין, ואל תפיק דוח.</strong></p>
</aside>

<h3>ומה עם הענן</h3>
<p>יש גם משימות שרצות בענן ואינן דורשות שהמחשב שלכם יהיה פתוח בכלל. <strong>לתיקי לקוחות הן אינן רלוונטיות</strong>, כי הן אינן רואות קבצים שעל המחשב שלכם. עבודה על תיק עוברת תמיד דרך המשימה המקומית.</p>
</section>

</main>

__DESKTOP_TOC__
</div>

<footer><bdi dir="ltr">Legal Mind</bdi> | מדריך ההמשך על <bdi dir="ltr">Claude Code</bdi> לעורכי דין | טיוטה לבדיקה</footer>

<script>
(function(){
  document.addEventListener("click", function(ev){
    var btn = ev.target.closest(".copy-button");
    if(!btn) return;
    var block = btn.closest(".copy-block");
    var src = document.getElementById(btn.getAttribute("data-copy-target"));
    var status = block ? block.querySelector(".copy-status") : null;
    if(!src) return;
    var text = src.innerText.replace(/ /g, " ").trim();
    var done = function(ok){
      if(!status) return;
      status.textContent = ok ? "הועתק" : "ההעתקה לא הצליחה. סמנו את הטקסט והעתיקו ידנית.";
      status.style.color = ok ? "" : "var(--red)";
      window.setTimeout(function(){ status.textContent = ""; }, 3000);
    };
    if(navigator.clipboard && window.isSecureContext){
      navigator.clipboard.writeText(text).then(function(){ done(true); }, function(){ fallback(); });
    } else { fallback(); }
    function fallback(){
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.setAttribute("readonly", "");
      ta.style.position = "fixed";
      ta.style.top = "-1000px";
      document.body.appendChild(ta);
      ta.select();
      var ok = false;
      try { ok = document.execCommand("copy"); } catch(e) { ok = false; }
      document.body.removeChild(ta);
      done(ok);
    }
  });
})();

/* הגדלת צילום מסך.
   על מסך קטן כל צילום מוקטן עד שאי אפשר לקרוא בו מילה, ולכן לחיצה עליו
   פותחת אותו בגודלו המלא. הסימונים האדומים משוכפלים איתו כי הם ממוקמים
   באחוזים, ולכן הם נשארים בדיוק על אותם רכיבים. */
(function(){
  "use strict";
  var frames = [].slice.call(document.querySelectorAll(".shot-frame"));
  if(!frames.length) return;

  var box = document.createElement("div");
  box.className = "zoomer";
  box.setAttribute("role", "dialog");
  box.setAttribute("aria-modal", "true");
  box.setAttribute("aria-label", "צילום מסך בגודל מלא");
  box.innerHTML = '<button type="button" class="zoomer-close">סגירה</button>' +
                  '<div class="zoomer-stage"></div>' +
                  '<div class="zoomer-cap"><p class="zoomer-cap-text"></p>' +
                  '<p class="zoomer-pan">הצילום רחב מהמסך. אפשר לגרור אותו הצידה כדי לראות את כולו.</p></div>';
  document.body.appendChild(box);

  var stage = box.querySelector(".zoomer-stage");
  var cap = box.querySelector(".zoomer-cap");
  var capText = box.querySelector(".zoomer-cap-text");
  var closeBtn = box.querySelector(".zoomer-close");
  var opener = null;

  function open(frame){
    var img = frame.querySelector("img");
    if(!img) return;
    stage.innerHTML = frame.innerHTML;
    /* גודל טבעי, ולא "עד רוחב המסך" - אחרת על טלפון מקבלים שוב תמונה
       מוקטנת שאי אפשר לקרוא בה, וההגדלה לא עשתה כלום */
    var nat = img.naturalWidth || img.width;
    stage.style.width = nat + "px";
    stage.style.maxWidth = "none";
    var fig = frame.closest("figure");
    var c = fig ? fig.querySelector(".shot-caption") : null;
    capText.textContent = c ? c.textContent : "";
    cap.classList.toggle("is-wide", nat > (window.innerWidth - 20));
    opener = frame;
    box.classList.add("is-open");
    document.body.style.overflow = "hidden";
    closeBtn.focus();
  }
  function close(){
    box.classList.remove("is-open");
    document.body.style.overflow = "";
    stage.innerHTML = "";
    if(opener) opener.focus();
    opener = null;
  }

  /* ההזמנה להגדיל מופיעה רק על צילום שבאמת מוצג מוקטן. על צילום שממילא
     בגודלו הטבעי היא הבטחה ריקה, ועשרים שורות כאלה הן רעש */
  function wire(){
    frames.forEach(function(frame){
      var img = frame.querySelector("img");
      if(!img || !img.naturalWidth) return;
      var shrunk = img.getBoundingClientRect().width < img.naturalWidth * 0.96;
      if(!shrunk || frame.dataset.zoom) return;
      frame.dataset.zoom = "1";
      frame.setAttribute("tabindex", "0");
      frame.setAttribute("role", "button");
      frame.setAttribute("aria-label", "הגדלת הצילום");
      frame.style.cursor = "zoom-in";
      frame.addEventListener("click", function(){ open(frame); });
      frame.addEventListener("keydown", function(ev){
        if(ev.key === "Enter" || ev.key === " "){ ev.preventDefault(); open(frame); }
      });
      var fig = frame.closest("figure");
      var capEl = fig ? fig.querySelector(".shot-caption") : null;
      if(capEl && !fig.querySelector(".shot-hint")){
        var hint = document.createElement("p");
        hint.className = "shot-hint";
        hint.textContent = "לחיצה על הצילום פותחת אותו בגודל מלא.";
        capEl.insertAdjacentElement("afterend", hint);
      }
    });
  }
  wire();
  window.addEventListener("load", wire);
  window.addEventListener("resize", wire);
  frames.forEach(function(frame){
    var img = frame.querySelector("img");
    if(img && !img.complete) img.addEventListener("load", wire);
  });

  closeBtn.addEventListener("click", close);
  box.addEventListener("click", function(ev){
    if(ev.target === box) close();
  });
  document.addEventListener("keydown", function(ev){
    if(ev.key === "Escape" && box.classList.contains("is-open")) close();
  });
})();

/* סימון הפרק הפעיל בסרגל הצד, זהה להתנהגות בסדרת Excel */
(function(){
  "use strict";
  var sections = [].slice.call(document.querySelectorAll(".guide-section[id]"));
  var links = [].slice.call(document.querySelectorAll(".desktop-toc a[href^='#']"));
  if(!sections.length || !links.length) return;
  var linked = sections.filter(function(s){
    return links.some(function(a){ return a.getAttribute("href") === "#" + s.id; });
  });
  if(!linked.length) return;
  var current = null;
  function set(id){
    if(id === current) return;
    current = id;
    links.forEach(function(a){
      if(a.getAttribute("href") === "#" + id){ a.setAttribute("aria-current","location"); }
      else { a.removeAttribute("aria-current"); }
    });
  }
  function pick(){
    var line = window.innerHeight * 0.25, best = linked[0];
    for(var i = 0; i < linked.length; i++){
      if(linked[i].getBoundingClientRect().top <= line){ best = linked[i]; } else { break; }
    }
    set(best.id);
  }
  pick();
  window.addEventListener("scroll", pick, {passive:true});
  window.addEventListener("resize", pick, {passive:true});
})();



</script>

</body>
</html>
"""

HTML = HTML.replace("__SHOT_283__", shot("283",
    "כך נראה סרגל הצד באפליקציה אחרי המעבר ללשונית Code",
    targets=[("left:51%;top:22%;width:47%;height:16%", "", 1),
             ("left:2%;top:82%;width:96%;height:16%", "", 2)],
    legend=["הלשונית <bdi dir=\"ltr\">Code</bdi>, ליד <bdi dir=\"ltr\">Home</bdi>. לחיצה אחת, ואתם בצד שבו יושב <bdi dir=\"ltr\">Claude Code</bdi>.",
            "<bdi dir=\"ltr\">Routines</bdi> בתחתית הסרגל. כאן מנהלים את המשימות שרצות לבד."]))

HTML = HTML.replace("__SHOT_278__", shot("278",
    "אם אינכם רואים את Routines בסרגל, הוא מוסתר מתחת ל-More",
    targets=[("left:3%;top:6%;width:94%;height:30%", "", 1)],
    legend=["לוחצים <bdi dir=\"ltr\">More</bdi>, ו-<bdi dir=\"ltr\">Routines</bdi> הוא הפריט הראשון שנפתח."]))

HTML = HTML.replace("__SHOT_284__", shot("284",
    "דף Routines. שימו לב לשני מקומות שנראים דומים ואינם עושים את אותו דבר",
    targets=[("left:88.5%;top:8%;width:10%;height:20%", "", 1),
             ("left:2%;top:38%;width:96%;height:30%", "", 2)],
    legend=["הכפתור <bdi dir=\"ltr\">New routine</bdi> והחץ שלידו. <strong>מכאן נעבוד</strong>, ובוחרים <bdi dir=\"ltr\">Local</bdi>.",
            "תיבת הכתיבה שבאמצע הדף. <strong>היא בונה משימה שרצה בענן ואינה רואה קבצים במחשב שלכם.</strong> אל תשתמשו בה."]))

HTML = HTML.replace("__SHOT_285__", shot("285",
    "כך נראה הטופס הלא נכון, זה של משימת הענן",
    targets=[("left:25%;top:41%;width:72%;height:5%", "", 1)],
    legend=["<bdi dir=\"ltr\">Select a repository</bdi> ו-<bdi dir=\"ltr\">Select a cloud environment</bdi>, <strong>ואין שדה לבחירת תיקייה.</strong> אם אתם רואים את השורה הזו, לחצו <bdi dir=\"ltr\">Cancel</bdi> והתחילו מהחץ."]))

HTML = HTML.replace("__SHOT_287__", shot("287",
    "וכך נראה הטופס הנכון, של המשימה המקומית, לפני שמילאתם אותו",
    targets=[("left:25%;top:63.5%;width:14%;height:5%", "", 1),
             ("left:25%;top:75%;width:8%;height:5%", "", 2)],
    legend=["<bdi dir=\"ltr\">Select folder</bdi>. <strong>זה השדה שתשכחו</strong>, ובלעדיו הכפתור <bdi dir=\"ltr\">Create</bdi> נשאר אפור בלי שום הודעת שגיאה.",
            "שורת <bdi dir=\"ltr\">Schedule</bdi>. <bdi dir=\"ltr\">Manual</bdi> הוא הראשון בשורה."]))

HTML = HTML.replace("__SHOT_288__", shot("288",
    "מה שקורה כששדה השם נכתב בעברית",
    targets=[("left:3.5%;top:11%;width:71%;height:8%", "", 1)],
    legend=["<bdi dir=\"ltr\">Name must contain at least one letter or number</bdi>. השדה הזה הופך את מה שתכתבו לשם תיקייה במחשב, ולכן <strong>רק הוא חייב להיות באנגלית.</strong>"]))

HTML = HTML.replace("__SHOT_291__", shot("291",
    "הטופס מוכן. שלושת הדברים שהופכים אותו לתקין",
    targets=[("left:25%;top:78%;width:25%;height:5%", "", 1),
             ("left:88%;top:75%;width:10%;height:5%", "", 2),
             ("left:25%;top:88%;width:8%;height:5%", "", 3),
             ("left:89%;top:93.5%;width:9%;height:5%", "", 4)],
    legend=["התיקייה נבחרה, והנתיב שלה מופיע כאן.",
            "המודל שונה ל-<bdi dir=\"ltr\">Opus 5</bdi>.",
            "<bdi dir=\"ltr\">Manual</bdi> מסומן, ושורת השעה נעלמה.",
            "<strong>והכפתור <bdi dir=\"ltr\">Create</bdi> נדלק.</strong> אם הוא עדיין אפור, חזרו לסימון 1."]))

HTML = HTML.replace("__SHOT_282__", shot("282",
    "השיחה שנפתחה לבד ועובדת, בלי שכתבתם בה מילה",
    targets=[("left:4%;top:60.5%;width:6%;height:5%", "", 1)],
    legend=["הסימן המסתובב. כל עוד הוא שם, היא עדיין עובדת. כשהוא נעלם והיא כותבת סיכום, היא סיימה."]))

HTML = HTML.replace("__PLACEHOLDER_PERM__", placeholder("בקשת האישור טרם צולמה. בהרצות שביצענו היא לא קפצה, ולכן אין כאן צילום ולא נמציא אחד."))
HTML = HTML.replace("__PLACEHOLDER_DONE__", placeholder("שני צילומים חסרים כאן: השיחה הגמורה עם הסיכום, והקובץ החדש יושב בתיקייה בסייר הקבצים."))
HTML = HTML.replace("__INSTR__", INSTR)


HTML = HTML.replace("__FIG_SUMMARY__", shot("cut-run-summary",
    "הסיכום שהוא כתב בסוף ההרצה, מילה במילה",
    targets=[("left:2%;top:12%;width:96%;height:12%", "", 1),
             ("left:2%;top:61%;width:96%;height:8%", "", 2),
             ("left:2%;top:83%;width:96%;height:14%", "", 3)],
    legend=["<strong>הוא מסביר איך קרא מסמכים שהם תמונה</strong>, ומציין שלא הותקנה שום תוכנה ולא נעשה שימוש בכלי פענוח.",
            "<strong>ומיוזמתו: \"לא שונה שם, לא נמחק ולא הועבר אף קובץ מקור. 40 קבצים נשארו בדיוק כפי שהיו.\"</strong>",
            "ובסוף, <strong>שלושה עשר פריטים ב\"טעון בדיקה\"</strong> - פערים שהוא מצא בהשוואה בין המסמכים, ואף אחד מהם אינו כתוב במסמך בודד."]))

HTML = HTML.replace("__FIG_RECENT__", shot("cut-open-recent",
    "התפריט שמחליף את התיקייה. שימו לב: זו רשימת תיקיות, לא רשימת שיחות",
    targets=[("left:1%;top:0.5%;width:5%;height:6%", "badge-inside-left", 1),
             ("left:2%;top:48%;width:39%;height:6%", "", 2),
             ("left:44%;top:55%;width:55%;height:44%", "", 3)],
    legend=["התפריט <bdi dir=\"ltr\">File</bdi>.",
            "<bdi dir=\"ltr\">Open Recent</bdi>, ומשם נפתחת הרשימה שמימין.",
            "<strong>וזו רשימת תיקיות, לא רשימת שיחות.</strong> בחירה בה מחליפה את התיקייה ופותחת שיחה חדשה וריקה. <strong>לשיחות מגיעים אחר כך, דרך אייקון השעון.</strong>"]))

HTML = HTML.replace("__FIG_PALETTE__", shot("vs-16",
    "רשימת הפקודות אחרי Ctrl+Shift+P והקלדת claude",
    targets=[("left:1.5%;top:2.5%;width:94%;height:6.5%", "badge-right", 1),
             ("left:2%;top:53.5%;width:94%;height:4.5%", "", 2)],
    legend=["מקלידים כאן <bdi dir=\"ltr\">claude</bdi>, וכל מה שקלוד קוד יודע לעשות מופיע ברשימה.",
            "<bdi dir=\"ltr\">Open in Side Bar</bdi>. <strong>זו הפקודה שמחזירה את החלונית לצד, ורק שם יש לה שעון.</strong>"]))

HTML = HTML.replace("__FIG_CLOSEALL__", shot("vs-13",
    "התפריט שסוגר את כל הלשוניות בבת אחת",
    targets=[("left:90.5%;top:1.5%;width:7.5%;height:7.5%", "", 1),
             ("left:6.5%;top:29%;width:86%;height:9%", "", 2)],
    legend=["שלוש הנקודות, בפינה שמעל הלשוניות.",
            "<bdi dir=\"ltr\">Close All</bdi> סוגר את כולן. <strong>שום דבר לא נמחק</strong> - הקבצים נשארים בתיקייה, רק המסך מתפנה."]))

HTML = HTML.replace("__FIG_PANEL__", shot("cut-panel-top",
    "ראש החלונית בסרגל הצד. כאן מזהים שאתם במקום הנכון, וכאן מגיעים לשיחות",
    targets=[("left:12.5%;top:8%;width:21.5%;height:32%", "", 1),
             ("left:2.5%;top:10%;width:8.5%;height:30%", "badge-inside-left", 2),
             ("left:82.5%;top:52%;width:5%;height:34%", "", 3),
             ("left:90%;top:52%;width:5%;height:34%", "badge-above", 4)],
    legend=["הלשונית <bdi dir=\"ltr\">Claude Code</bdi>. <strong>כשהיא מודגשת, אתם בחלונית הנכונה.</strong>",
            "והלשונית <bdi dir=\"ltr\">Chat</bdi> שלידה <strong>אינה של <bdi dir=\"ltr\">Claude</bdi>.</strong> היא של <bdi dir=\"ltr\">VS Code</bdi>, ומי שיכתוב בה יקבל תשובה ממישהו אחר.",
            "<strong>אייקון השעון.</strong> לחיצה עליו פותחת את כל השיחות שהיו בתיקייה הזאת.",
            "והפלוס שלידו <strong>פותח שיחה חדשה.</strong> אל תלחצו עליו כשאתם מחפשים שיחה ישנה."]))

HTML = HTML.replace("__FIG_EX2WORK__", shot("ex2-02",
    "הוא פותח את ארבעת הפרוטוקולים וסופר את השורות בכל אחד",
    legend=None))

HTML = HTML.replace("__FIG_EX2RESULT__", shot("ex2-04",
    "מה שהוא החזיר: טבלה עם הפניה מדויקת, ולידה מה שהוא סירב להכניס אליה",
    targets=[("left:2.7%;top:14.1%;width:29.6%;height:34.7%", "badge-above", 1),
             ("left:5.8%;top:52.8%;width:92.1%;height:8%", "badge-outside-left", 2)],
    legend=["<strong>הטבלה. לכל מועד: עמוד, שורה, תאריך ותוכן.</strong> פתחנו את הפרוטוקולים ובדקנו כל אחת משש השורות - כולן מדויקות.",
            "<strong>וזה החלק המעניין:</strong> שני תאריכים שנמצאים צמוד לאזכור תשלום <strong>ואינם מועדי תשלום</strong> - אחד מועד פגישה, אחד מועד הגשה למיסוי. <strong>הוא לא הכניס אותם לטבלה, וכתב למה.</strong>"]))

HTML = HTML.replace("__FIG_EX4BEFORE__", shot("ex4-before",
    "התיקייה לפני שהוא התחיל: תיקיית הסרוקים וקובץ הנהלים בלבד",
    legend=None))

HTML = HTML.replace("__FIG_EX4RECHECK__", shot("ex4-recheck",
    "השורה שבה הוא מודיע שהוא חוזר לקרוא מחדש, ולא מסתמך על מה שכבר קרא",
    legend=None))

HTML = HTML.replace("__FIG_EX4SUMMARY__", shot("ex4-summary",
    "הדוח שהוא כתב: כמה נבדקו, כמה תאמו, ומה בדיוק תוקן",
    legend=None))

HTML = HTML.replace("__FIG_EX4FILES__", shot("ex4-files",
    "והתיקייה בסוף: הטבלה ודוח הבדיקה, זה לצד זה",
    legend=None))

HTML = HTML.replace("__FIG_EX5PAGE__", shot("ex5-page",
    "הדף שהוא בנה, פתוח בדפדפן. קובץ אחד שיושב בתיקיית התיק",
    legend=None))

HTML = HTML.replace("__FIG_EX5FIELDS__", shot("ex5-fields",
    "שדה התאריך: יום, חודש ושנה בנפרד, ולידם התאריך במילים",
    legend=None))

HTML = HTML.replace("__FIG_EX5RESULT__", shot("ex5-result",
    "התוצאה, ולידה הסעיף שממנו היא נגזרת",
    targets=[("left:69.6%;top:50.1%;width:28%;height:11.1%", "badge-outside-left", 1),
             ("left:75.2%;top:88.7%;width:23.3%;height:7.8%", "badge-outside-left", 2)],
    legend=["<strong>המועד האחרון לרישום הערת אזהרה, עם שם היום.</strong> ומתחתיו כתוב אם הוא כבר חלף וכמה ימים עברו.",
            "<bdi dir=\"ltr\">הצג את ספירת הימים יום-יום</bdi>. <strong>לחיצה עליו פותחת את החישוב עצמו</strong>, ואת זה נראה מיד."]))

HTML = HTML.replace("__FIG_EX5DAYCOUNT__", shot("ex5-daycount",
    "ספירת שבעת ימי העסקים, יום אחר יום, עם הסיבה לכל דילוג",
    targets=[("left:59%;top:22.3%;width:6%;height:14.2%", "badge-outside-left", 1)],
    legend=["<strong>שישי ושבת מסומנים \"לא\", ולידם כתוב למה.</strong> הספירה מדלגת עליהם וממשיכה, ולכן שבעה ימי עסקים נמשכים אחד עשר ימי לוח."]))

HTML = HTML.replace("__FIG_EX5NOTE__", shot("ex5-note",
    "ההערה שמופיעה כשמזינים תאריך שונה מזה שבהסכם",
    legend=None))

HTML = HTML.replace("__FIG_CHAOS__", shot("open-chaos",
    "המסך מיד אחרי פתיחת תיקייה. באמצע מסך פתיחה של VS Code, בצד חלונית שיחה שאינה של קלוד, וקלוד עצמו עוד לא נפתח",
    legend=None))

HTML = HTML.replace("__FIG_TRUST__", shot("open-trust",
    "מסך Workspace Trust. אין בו שום דבר שאתם צריכים, וסוגרים אותו ב-X שבפינה השמאלית העליונה",
    legend=None))

HTML = HTML.replace("__FIG_NEWSESSION__", shot("cut-newsession",
    "חלונית Claude Code אחרי לחיצה על הכוכבית",
    targets=[("left:4.3%;top:20.7%;width:42.4%;height:11.4%", "badge-right", 1)],
    legend=["<bdi dir=\"ltr\">New session</bdi>. <strong>לחיצה אחת, ורק אז נפתחת תיבת הכתיבה.</strong> ו<bdi dir=\"ltr\">No sessions yet</bdi> שכתוב מתחת פירושו שזו תיקייה חדשה שעוד לא עבדתם בה, לא שמשהו נמחק."]))

HTML = HTML.replace("__FIG_EXPLORERICON__", shot("open-explorer-icon",
    "אייקון המסמכים, העליון בסרגל. VS Code עצמו כותב את שמו כשעוברים עליו עם העכבר",
    legend=None))

HTML = HTML.replace("__FIG_INSTALLPOPUP__", shot("cut-install-popup",
    "החלון שקופץ ומציע להתקין תוסף. הוא לא קשור למשימה",
    targets=[("left:93.1%;top:3.8%;width:5.4%;height:22.9%", "badge-below", 1),
             ("left:53.8%;top:61%;width:11%;height:32.4%", "badge-outside-left", 2)],
    legend=["<strong>ה-<bdi dir=\"ltr\">X</bdi>. זה הכפתור היחיד שאתם צריכים כאן.</strong>",
            "<bdi dir=\"ltr\">Install</bdi>. <strong>אל תלחצו עליו כדי שהחלון ייעלם</strong> - הוא מתקין תוסף שמקבל גישה לקבצים שבתיקייה, ואצלכם זו תיקיית תיק."]))

HTML = HTML.replace("__FIG_INCLUDECOMPLETED__", shot("cut-include-completed",
    "המתג שמחזיר משימות שהסתיימו לרשימה",
    targets=[("left:52.8%;top:14.3%;width:5.5%;height:28.6%", "badge-below", 1)],
    legend=["<bdi dir=\"ltr\">Include completed</bdi>, ולידו מספר המשימות שמוסתרות כרגע. <strong>הוא כבוי כברירת מחדל וחוזר לכבוי בכל כניסה</strong> - וזו כל הסיבה שנדמה שהמשימה נמחקה."]))

HTML = HTML.replace("__FIG_FLAGGED__", shot("cut-flagged",
    "החלק שלא ביקשנו: מה שהוא סימן כטעון בדיקה, מתוך ההרצה עצמה",
    targets=[("left:80.6%;top:1.3%;width:17%;height:11.1%", "badge-outside-left", 1),
             ("left:38.9%;top:48.2%;width:60.6%;height:9.4%", "badge-outside-left", 2)],
    legend=["שלושה עשר פריטים. <strong>הוא לא נשאל עליהם</strong> - הוא הגיע אליהם תוך כדי הקריאה.",
            "וזה הפריט שממחיש הכי טוב למה זה שונה: <strong>שתי טיוטות עם נוסח שונה לאותו סעיף, ובלי הסכם חתום בתיק.</strong> מי שקורא מסמך אחד לא יראה את זה לעולם."]))

HTML = HTML.replace("__FIG_WRONGSCREEN__", shot("cut-wrong-screen",
    "המסך הדומה, זה שאינו שלנו. אם הגעתם לכאן, חזרו אחורה",
    targets=[("left:40.1%;top:83.4%;width:20%;height:6.1%", "badge-below", 1)],
    legend=["<bdi dir=\"ltr\">No scheduled tasks yet</bdi>. <strong>השורה הזאת אומרת שאתם במערכת השנייה,</strong> ולא שהמשימה שלכם נעלמה. היא יושבת ב-<bdi dir=\"ltr\">Routines</bdi>, בצד של <bdi dir=\"ltr\">Code</bdi>."]))

HTML = HTML.replace("__FIG_OCRLINES__", shot("cut-ocr-lines",
    "השורות שהוא כתב תוך כדי ההרצה, מילה במילה",
    targets=[("left:0.5%;top:34.5%;width:98.8%;height:12.1%", "badge-above", 1),
             ("left:0.5%;top:66.8%;width:33.5%;height:11.6%", "badge-below", 2)],
    legend=["<strong>ההחלטה שהוא קיבל לבד:</strong> אין צורך בכלי פענוח, כל קובץ עוטף תמונה אחת, הוא מחלץ אותה וקורא ישירות.",
            "<strong>ואישור שזה עבד:</strong> קריא, עכשיו קורא את כל ארבעים העמודים. <strong>מכאן זה זמן שלו, לא שלכם.</strong>"]))

HTML = HTML.replace("__FIG_LOCALCLOUD__", shot("cut-local-cloud",
    "מה שנפתח מהחץ: שתי אפשרויות בלבד",
    targets=[("left:22.8%;top:37.3%;width:68.5%;height:20%", "", 1)],
    legend=["<bdi dir=\"ltr\">Local</bdi>, העליונה. <strong>היא זו שרואה את הקבצים שעל המחשב שלכם.</strong> <bdi dir=\"ltr\">Cloud</bdi> שמתחתיה רצה בשרת של <bdi dir=\"ltr\">Anthropic</bdi>, ואין לה גישה לתיקייה."]))

HTML = HTML.replace("__FIG_GREYCREATE__", shot("cut-grey-create",
    "תחתית הטופס לפני שבחרתם תיקייה. שלושת הדברים שצריך לגעת בהם, וכפתור אפור",
    targets=[("left:1.6%;top:17.9%;width:15.5%;height:12.2%", "", 1),
             ("left:88.6%;top:4.1%;width:10.2%;height:10.6%", "", 2),
             ("left:90.6%;top:84.1%;width:9%;height:14.2%", "badge-above", 3)],
    legend=["<bdi dir=\"ltr\">Select folder</bdi>. <strong>זה השדה שנשכח, והוא היחיד שמונע מהטופס להישלח.</strong>",
            "ובצד השני של אותה שורה, <bdi dir=\"ltr\">Sonnet 5</bdi>. לחצו ובחרו <bdi dir=\"ltr\">Opus 5</bdi>.",
            "<bdi dir=\"ltr\">Create</bdi>, ובצילום הזה הוא אפור. <strong>כך הוא נראה כל עוד לא נבחרה תיקייה</strong> - בלי הודעה, בלי סימן אדום, בלי כלום."]))

HTML = HTML.replace("__FIG_ACTIVITYBAR__", shot("cut-activitybar",
    "סרגל האייקונים שבשמאל המסך. הכוכבית הכתומה היא קלוד",
    targets=[("left:14.3%;top:49.5%;width:71.4%;height:6.4%", "badge-below", 1)],
    legend=["<strong>הכוכבית הכתומה.</strong> לחיצה עליה פותחת את חלונית <bdi dir=\"ltr\">Claude Code</bdi>, ושם לוחצים <bdi dir=\"ltr\">New session</bdi>. <strong>אם אינכם רואים אותה, התיקייה עדיין לא אושרה</strong> - חזרו לשלב 1. והאייקון העליון בסרגל, זה שנראה כמו שני דפים, הוא שפותח את רשימת הקבצים."]))

HTML = HTML.replace("__FIG_SIXFILES__", shot("vs-02",
    "סייר הקבצים אחרי שהוא סיים. מסמכי המקור למעלה, ומתחתיהם מה שהוא כתב",
    targets=[("left:14%;top:32.7%;width:85%;height:26.3%", "", 1),
             ("left:14%;top:60.2%;width:85%;height:31.3%", "badge-below", 2)],
    legend=["חמשת מסמכי התיק, כפי שהיו. <strong>הוא לא נגע בהם.</strong>",
            "וששת הקבצים שהוא כתב: חמישה תקצירים וציר זמן אחד. <strong>לחיצה על כל אחד פותחת אותו לקריאה.</strong>"]))

HTML = HTML.replace("__FIG_SESSIONS__", shot("cut-sessions",
    "מה שנפתח בלחיצה על השעון: כל השיחות שהיו בתיקייה הזאת",
    targets=[("left:0.6%;top:44.2%;width:86.7%;height:12.4%", "", 1),
             ("left:0.6%;top:70.8%;width:86.7%;height:26.5%", "", 2)],
    legend=["<bdi dir=\"ltr\">Local</bdi> הן השיחות שנעשו במחשב הזה, ו<bdi dir=\"ltr\">Web</bdi> הן שיחות מהדפדפן. <strong>מה שעשיתם כאן נמצא ב-<bdi dir=\"ltr\">Local</bdi>.</strong>",
            "השיחות עצמן, ולצד כל אחת כמה זמן עבר ממנה. <strong>לחיצה על שורה פותחת את השיחה עם כל מה שנכתב בה</strong> - ולמעלה יש שדה חיפוש, אם הצטברו הרבה."]))

HTML = HTML.replace("__FIG_REWIND__", shot("vs-01",
    "מסך האישור של החזרה לאחור. הוא מפרט מה יימחק לפני שהוא מוחק",
    targets=[("left:2.8%;top:78.2%;width:94%;height:7.7%", "badge-right", 1)],
    legend=["<bdi dir=\"ltr\">Continue</bdi> מבצע את החזרה. <strong>עד שלא לוחצים עליו, שום דבר עדיין לא נמחק</strong> - ו<bdi dir=\"ltr\">Never mind</bdi> שמתחתיו מבטל הכל."]))

HTML = HTML.replace("__FIG_HISTORY__", shot("cut-history-restored",
    "כך נראית שיחה שחזרה: השם שלה בראש החלונית, וכל מה שנכתב בה קודם",
    targets=[("left:3.4%;top:19%;width:68.3%;height:8.6%", "", 1),
             ("left:83.5%;top:19%;width:4.2%;height:8.6%", "", 2),
             ("left:12%;top:38%;width:83%;height:48%", "", 3)],
    legend=["שם השיחה. <strong>אם כתוב כאן <bdi dir=\"ltr\">Untitled</bdi>, אתם בשיחה חדשה וריקה.</strong> אם כתוב שם - זו שיחה שחזרה.",
            "אייקון השעון, שממנו הגעתם לכאן. <strong>לחיצה עליו תמיד מחזירה את רשימת השיחות.</strong>",
            "וכל מה שנכתב בשיחה קודם, <strong>בדיוק כפי שהשארתם.</strong>"]))

# tables of contents, generated from the sections so they can never drift
items = re.findall(r'<section class="guide-section" id="([^"]+)">.*?<h2>(.*?)</h2>', HTML, re.S)
_rows_list = []
for _i, (_sid, _t) in enumerate(items, 1):
    _rows_list.append('<li><a href="#%s"><span>%02d</span>%s</a></li>' % (_sid, _i, _t.strip()))
_rows = chr(10).join(_rows_list)
HTML = HTML.replace("__DESKTOP_TOC__",
    '<aside class="desktop-toc">' + chr(10) + '<h2>תוכן המדריך</h2>' + chr(10) + '<ol>' + chr(10) + _rows + chr(10) + '</ol>' + chr(10) + '</aside>')
HTML = HTML.replace("__MOBILE_TOC__",
    '<nav class="mobile-toc"><details><summary>תוכן המדריך</summary><ol>' + chr(10) + _rows + chr(10) + '</ol></details></nav>')

# renumber sections sequentially so inserts never desync the numbering
_n = [0]
def _renum(m):
    _n[0] += 1
    return '<span class="section-number">%02d</span>' % _n[0]
HTML = re.sub(r'<span class="section-number">\d+</span>', _renum, HTML)


_left = re.findall(r"__[A-Z_]{3,}__", HTML)
assert not _left, "placeholders left unreplaced: " + ", ".join(sorted(set(_left)))

OUT = os.path.join(ROOT, "claude-code", "sequel-preview")
os.makedirs(OUT, exist_ok=True)
p = os.path.join(OUT, "index.html")
open(p, "w", encoding="utf-8").write(HTML)
print("wrote", p, os.path.getsize(p), "bytes")

