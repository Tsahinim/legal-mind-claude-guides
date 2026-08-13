# מפרט כפתור המקור
מפרט קבוע למדריך Gemini Notebook · 13 באוגוסט 2026

**הכלל:** אין ציטוט בלי כפתור. **הכפתור בשורה נפרדת מתחת לציטוט**,
ולצדו כיתוב שנוקב בשם המסמך.

---

## המבנה

```
[ הציטוט באנגלית ]
[ הציטוט בעברית ]
                          ← שורה חדשה
[↗]  לקריאת המסמך המלא — שם המסמך המדויק
```

**כשבפרק יש שני ציטוטים משני מסמכים — שני כפתורים נפרדים**,
כל אחד מתחת לציטוט שלו. **לא מאגדים.**

---

## הכיתוב

**תמיד מתחיל ב"לקריאת המסמך המלא", ואחריו קו מפריד ושם המסמך.**

**אסור:** "מקור" · "קרא עוד" · "לחצו כאן" · "ראו כאן"
**מפני שהם אינם אומרים לקורא מה הוא עומד לפתוח.**

**ולמה זה קריטי דווקא במדריך הזה:** הציטוטים מגיעים מארבעה סוגי מסמכים
בעלי משקל משפטי שונה. **הכיתוב הוא שמסמן את ההבדל, בלי להסביר אותו במילים.**

---

## הנוסחים המדויקים, לפי מקור

| מקור | הכיתוב על הכפתור | קישור |
|---|---|---|
| **תנאי שירות** | לקריאת המסמך המלא — תנאי השירות הספציפיים של Google Workspace, סעיף 12.11 | https://workspace.google.com/terms/service-terms/ |
| **DPA** | לקריאת המסמך המלא — הסכם עיבוד הנתונים של Google Cloud | https://cloud.google.com/terms/data-processing-addendum/ |
| **מרכזת פרטיות** | לקריאת המסמך המלא — מרכזת הפרטיות של Google Workspace | https://knowledge.workspace.google.com/admin/generative-ai/generative-ai-in-google-workspace-privacy-hub |
| **מרכז עזרה** | לקריאת המסמך המלא — מרכז העזרה של Google Workspace | https://knowledge.workspace.google.com/admin/gemini/gemini-for-google-workspace-faq |
| **את 1/22** | לקריאת המסמך המלא — גילוי דעת את/1/22, ועדת האתיקה של לשכת עורכי הדין | https://rotenberglaw.co.il/_Uploads/dbsAttachedFiles/ethics_committee_opinion_1-22_full.pdf |
| **את 60/24** | לקריאת המסמך המלא — גילוי דעת את/60/24 בעניין שימוש בבינה מלאכותית | https://www.gov.il/BlobFolder/generalpage/ai_info_law/he/גילוי%20דעת%20בעניין%20שימוש%20בבינה%20מלאכותית%20בעבודת%20עורכי%20הדין%20(2024).pdf |
| **מגבלות המוצר** | לקריאת המסמך המלא — שאלות ותשובות, Gemini Notebook | https://support.google.com/gemininotebook/answer/16269187 |

---

## HTML

```html
<blockquote class="src-quote">
  <p lang="en" dir="ltr">Google will not use customer data to train or improve generative AI models</p>
  <p>‏Google לא תשתמש בנתוני לקוחות כדי לאמן או לשפר מודלים של AI גנרטיבי.</p>
</blockquote>
<p class="src-link">
  <a class="src-btn" href="https://workspace.google.com/terms/service-terms/"
     target="_blank" rel="noopener">↗</a>
  <span>לקריאת המסמך המלא — תנאי השירות הספציפיים של Google Workspace, סעיף 12.11</span>
</p>
```

**הערות מימוש:**
הציטוט האנגלי מקבל `lang="en" dir="ltr"` כדי שלא יתהפך ·
`target="_blank"` כדי שהקורא לא יאבד את מקומו במדריך ·
`rel="noopener"` מטעמי אבטחה · **הכפתור והכיתוב באותה שורה, הכפתור ראשון.**

---

## בדיקות QA למפרט הזה

**כל ציטוט במדריך נושא כפתור.** ספירת `blockquote.src-quote`
מול ספירת `p.src-link` חייבת להיות זהה.

**כל קישור מחזיר 200.** נבדק לפני פרסום ובכל עדכון.

**אין כיתוב גנרי.** חיפוש אחר "מקור", "קרא עוד" ו"לחצו כאן"
מחזיר אפס תוצאות.

**כל ציטוט באנגלית מלווה בתרגום לעברית**, ובאותו סדר תמיד:
אנגלית למעלה, עברית מתחת.
