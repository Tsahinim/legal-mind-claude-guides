import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

const checker = fileURLToPath(new URL('./qa.mjs', import.meta.url));
const page = (body) => `<html lang="he" dir="rtl"><head><title>בדיקה</title></head><body><h1>בדיקה</h1>${body}</body></html>`;
// Minimal complete guide series, so every case exercises the real release gate.
const guides = [
  'Pin chat | Move to project | New project | בדיקת הצלחה | הצילומים בסעיף זה מתייחסים לממשק בדפדפן או באפליקציה למחשב',
  'Web search | Research | תחילת הבדיקה, לא סיומה | מה עושים כאשר אין מקור מתאים? | מה אי אפשר לקבוע | אין צורך לבחור בו קודם בתוך אותה שיחה',
  'Code execution and file creation | Publish | Share | מסמך ארוך יותר שומרים במסמך פרטי ומאושר או ב־Project אישי ייעודי',
  'Project Files | Set project instructions | 100 עמודים או פחות | Can use | Can edit | Share project | כיצד משתפים Project?',
  'Customize &gt; Skills | Upload a skill | שלבי בניית Skill - מבט כללי | מריצים משימת דוגמה',
  'Browse connectors | Add custom connector | Desktop Extension | שילוב מידע ממספר מקורות באותה משימה | Always allow | Needs approval | Blocked | מה עושים אם <bdi dir="ltr">Browse connectors</bdi> אינו מופיע? | אי אפשר לשתף שיחה שמכילה תוכן שסונכרן באמצעות Connector | Project פרטי'
];

function check(body) {
  const fixture = fs.mkdtempSync(path.join(os.tmpdir(), 'legal-mind-qa-'));
  try {
    guides.forEach((text, i) => {
      const dir = path.join(fixture, `guide-${i + 1}`);
      fs.mkdirSync(dir);
      fs.writeFileSync(path.join(dir, 'index.html'), page(`<p>${text}</p><p id="סעיף">תוכן</p>`));
    });
    fs.writeFileSync(path.join(fixture, 'index.html'), page(body));
    fs.writeFileSync(path.join(fixture, 'work book.xlsx'), 'download fixture');
    fs.writeFileSync(path.join(fixture, 'shot.png'), 'image existence fixture');
    return spawnSync(process.execPath, [checker], { cwd: fixture, encoding: 'utf8' });
  } finally {
    const resolvedFixture = fs.realpathSync(fixture);
    assert.equal(path.dirname(resolvedFixture), fs.realpathSync(os.tmpdir()));
    assert(path.basename(resolvedFixture).startsWith('legal-mind-qa-'));
    fs.rmSync(resolvedFixture, { recursive: true, force: true });
  }
}

function passes(body) {
  const result = check(body);
  assert.equal(result.status, 0, result.stderr || result.error?.message);
}

function fails(body, message) {
  const result = check(body);
  assert.equal(result.status, 1, result.stdout);
  assert.match(result.stderr, message);
}

test('resolves local URL queries, encoded paths and same/cross-page fragments', () => {
  passes('<p id="כאן">עוגן</p><a href="work%20book.xlsx?v=3">הורדה</a>' +
    '<a href="?v=3#%D7%9B%D7%90%D7%9F">כאן</a>' +
    '<a href="guide-2/?v=3#%D7%A1%D7%A2%D7%99%D7%A3">סעיף</a>' +
    '<a href="/guide-2/#סעיף">נתיב מהשורש</a>' +
    '<img src="shot.png?v=3" alt="צילום מסך">');
});

test('embedded images and protocol-relative URLs are not local filesystem paths', () => {
  passes('<a href="data:image/png;base64,AAAA">תמונה</a>' +
    '<a href="//example.com/guide/">מדריך</a><img src="data:image/png;base64,AAAA" alt="תרשים">');
});

test('query parameters do not hide missing local files', () => {
  fails('<a href="missing.xlsx?v=3">הורדה</a>', /קישור מקומי שבור missing\.xlsx\?v=3/);
  fails('<img src="missing.png?v=3" alt="צילום מסך">', /תמונה חסרה missing\.png\?v=3/);
});

test('missing and malformed fragment targets still fail', () => {
  fails('<a href="#missing">עוגן</a>', /עוגן יעד חסר #missing/);
  fails('<a href="guide-2/?v=3#missing">עוגן</a>', /עוגן יעד חסר guide-2/);
  fails('<a href="#%invalid">עוגן</a>', /כתובת קישור לא תקינה/);
});

test('accepts explicitly decorative images but requires alt for informative images', () => {
  passes('<img src="shot.png" alt="" aria-hidden="true"><img src="shot.png" alt="" role="presentation">');
  fails('<img src="shot.png">', /תמונה ללא alt/);
  fails('<img src="shot.png" alt="">', /תמונה ללא alt/);
  fails('<img src="shot.png" data-alt="צילום מסך">', /תמונה ללא alt/);
  fails('<img src="shot.png" aria-hidden="true">', /תמונה ללא alt/);
});

test('reads quoted attributes correctly and rejects markup accidentally pasted into alt', () => {
  passes('<img src = "shot.png" alt = "מסך 3 > 2">');
  fails('<img src="shot.png" alt="הסבר <strong>מודגש</strong>">', /תגיות HTML בתוך alt/);
});

test('inline code does not create phantom spaces before punctuation', () => {
  passes('<p>לוחצים על <code>Open</code>, ואז שומרים.</p>' +
    '<p>פקודת דוגמה: <code>echo x ; echo y</code>.</p>');
  fails('<p>לוחצים על <code>Open</code> , ואז שומרים.</p>', /רווח חשוד לפני סימן פיסוק/);
  fails('<p>מילה , המשך.</p>', /רווח חשוד לפני סימן פיסוק/);
});

test('comments neither create failures nor supply working anchor targets', () => {
  passes('<!-- <img src="missing.png"><p>מילה , המשך.</p> בדיקת קבלה -->');
  fails('<!-- <span id="missing"></span> --><a href="#missing">עוגן</a>', /עוגן יעד חסר/);
});

test('editorial, duplicate-ID and new-window checks remain active', () => {
  fails('<p>בדיקת קבלה</p>', /ניסוח שנפסל בעריכה/);
  fails('<a href="https://example.com" target="_blank">קישור</a>', /ללא rel=noopener/);
  fails('<p id="duplicate">א</p><p id="duplicate">ב</p>', /מזהי עוגן כפולים/);
});
