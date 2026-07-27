import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const htmlFiles = [];
function walk(dir) {
  for (const ent of fs.readdirSync(dir, { withFileTypes: true })) {
    if (ent.name === '.git' || ent.name === 'node_modules') continue;
    const p = path.join(dir, ent.name);
    if (ent.isDirectory()) walk(p);
    else if (ent.name.endsWith('.html')) htmlFiles.push(p);
  }
}
walk(root);

const errors = [];
const counts = { pages: 0, links: 0, images: 0, anchors: 0 };
const attr = (tag, name) => {
  const m = tag.match(new RegExp(`\\b${name}=["']([^"']*)["']`, 'i'));
  return m ? m[1] : null;
};
const escapeRegExp = (value) => value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

for (const file of htmlFiles) {
  const rel = path.relative(root, file).replaceAll('\\', '/');
  const html = fs.readFileSync(file, 'utf8');
  counts.pages++;

  if (!/<html[^>]*\blang=["']he["'][^>]*>/i.test(html)) errors.push(`${rel}: lang=he חסר`);
  if (!/<html[^>]*\bdir=["']rtl["'][^>]*>/i.test(html)) errors.push(`${rel}: dir=rtl חסר`);
  const h1Count = (html.match(/<h1\b/gi) || []).length;
  if (h1Count !== 1) errors.push(`${rel}: נדרשת כותרת H1 אחת, נמצאו ${h1Count}`);

  const ids = [...html.matchAll(/\bid=["']([^"']+)["']/gi)].map((x) => x[1]);
  counts.anchors += ids.length;
  const duplicateIds = ids.filter((x, i) => ids.indexOf(x) !== i);
  if (duplicateIds.length) errors.push(`${rel}: מזהי עוגן כפולים ${[...new Set(duplicateIds)].join(', ')}`);

  for (const m of html.matchAll(/<a\b[^>]*>/gi)) {
    counts.links++;
    const href = attr(m[0], 'href');
    if (!href || /^(https?:|mailto:|tel:|javascript:)/i.test(href)) continue;
    if (href.startsWith('#')) {
      if (href.length > 1 && !ids.includes(decodeURIComponent(href.slice(1)))) errors.push(`${rel}: עוגן חסר ${href}`);
      continue;
    }
    const [raw, target] = href.split('#');
    const dest = path.resolve(path.dirname(file), decodeURIComponent(raw));
    const resolved = fs.existsSync(dest) && fs.statSync(dest).isDirectory() ? path.join(dest, 'index.html') : dest;
    if (!fs.existsSync(resolved)) errors.push(`${rel}: קישור מקומי שבור ${href}`);
    else if (target) {
      const destHtml = fs.readFileSync(resolved, 'utf8');
      if (!new RegExp(`\\bid=["']${escapeRegExp(target)}["']`, 'i').test(destHtml)) errors.push(`${rel}: עוגן יעד חסר ${href}`);
    }
  }

  for (const m of html.matchAll(/<img\b[^>]*>/gi)) {
    counts.images++;
    const src = attr(m[0], 'src');
    const alt = attr(m[0], 'alt');
    if (!alt?.trim()) errors.push(`${rel}: תמונה ללא alt`);
    if (src && !/^(data:|https?:)/i.test(src)) {
      const dest = path.resolve(path.dirname(file), decodeURIComponent(src));
      if (!fs.existsSync(dest)) errors.push(`${rel}: תמונה חסרה ${src}`);
    }
  }

  for (const m of html.matchAll(/<a\b[^>]*target=["']_blank["'][^>]*>/gi)) {
    const relValue = attr(m[0], 'rel') || '';
    if (!/noopener/i.test(relValue)) errors.push(`${rel}: קישור target=_blank ללא rel=noopener`);
  }

  const prose = html
    .replace(/<style[\s\S]*?<\/style>/gi, '')
    .replace(/<script[\s\S]*?<\/script>/gi, '')
    .replace(/<code[\s\S]*?<\/code>/gi, '')
    .replace(/<pre[\s\S]*?<\/pre>/gi, '')
    .replace(/<[^>]+>/g, '');
  if (/\s+[,.!?;:](?![A-Za-z])/u.test(prose)) errors.push(`${rel}: נמצא רווח חשוד לפני סימן פיסוק`);

  // Inline English labels must attach correctly to Hebrew maqaf and punctuation.
  if (/<\/(?:bdi|code|strong)>\s+[,.!?;:]/iu.test(html)) errors.push(`${rel}: רווח מיותר בין מונח באנגלית לסימן פיסוק`);
  if (/־\s+<(?:bdi|code|strong)\b/iu.test(html)) errors.push(`${rel}: רווח מיותר אחרי מקף עברי לפני מונח באנגלית`);
  if (/בחשבון\s+בחשבון/u.test(prose)) errors.push(`${rel}: כפילות מילים - בחשבון בחשבון`);
}


// Editorial and pedagogical release gates
const allText = htmlFiles.map((file) => fs.readFileSync(file, 'utf8')
  .replace(/<style[\s\S]*?<\/style>/gi, '')
  .replace(/<script[\s\S]*?<\/script>/gi, '')
  .replace(/<[^>]+>/g, ' ')
  .replace(/\s+/g, ' ')).join(' ');

const bannedEditorialPhrases = [
  'כוח שמחייב מקור לכל פרט',
  'Connector אחד יכול להביא יומן',
  'שער מעבר',
  'שער עצירה',
  'לפתוח גישה לאחרים',
  'רשימת המקורות היא נקודת כניסה',
  'השכבה השלישית חשובה לא פחות',
  'שיפור מדורג: התשובה הראשונה היא נקודת התחלה',
  'לכתוב Instructions שמחברות',
  'פחות מ־100 עמודים',
  'מתי להשתמש בתהליך קבוע',
  'מה עושים בפיילוט הראשון?',
  'בדיקת קבלה',
  'להכין בריף',
  'כפתור השיתוף שמופיע בחלק העליון',
  'בחשבון בחשבון'
];
for (const phrase of bannedEditorialPhrases) {
  if (allText.includes(phrase)) errors.push(`נמצא ניסוח שנפסל בעריכה: ${phrase}`);
}

const requiredByPage = {
  'guide-1/index.html': [
    'Pin chat', 'Move to project', 'New project', 'בדיקת הצלחה',
    'הצילומים בסעיף זה מתייחסים לממשק בדפדפן או באפליקציה למחשב'
  ],
  'guide-2/index.html': [
    'Web search', 'Research', 'תחילת הבדיקה, לא סיומה',
    'מה עושים כאשר אין מקור מתאים?', 'מה אי אפשר לקבוע',
    'אין צורך לבחור בו קודם בתוך אותה שיחה'
  ],
  'guide-3/index.html': [
    'Code execution and file creation', 'Publish', 'Share',
    'מסמך ארוך יותר שומרים במסמך פרטי ומאושר או ב־Project אישי ייעודי'
  ],
  'guide-4/index.html': [
    'Project Files', 'Set project instructions', '100 עמודים או פחות',
    'Can use', 'Can edit', 'Share project', 'כיצד משתפים Project?'
  ],
  'guide-5/index.html': [
    'Customize &gt; Skills', 'Upload a skill', 'שלבי בניית Skill - מבט כללי',
    'מריצים משימת דוגמה'
  ],
  'guide-6/index.html': [
    'Browse connectors', 'Add custom connector', 'Desktop Extension',
    'שילוב מידע ממספר מקורות באותה משימה', 'Always allow', 'Needs approval', 'Blocked',
    'מה עושים אם <bdi dir="ltr">Browse connectors</bdi> אינו מופיע?'
  ]
};
const guide2File = path.join(root, 'guide-2/index.html');
if (fs.existsSync(guide2File) && fs.readFileSync(guide2File, 'utf8').includes('Web Search')) {
  errors.push('guide-2/index.html: יש להשתמש בשם הממשק העדכני Web search, לא Web Search');
}

for (const [rel, phrases] of Object.entries(requiredByPage)) {
  const file = path.join(root, rel);
  if (!fs.existsSync(file)) { errors.push(`${rel}: עמוד נדרש חסר`); continue; }
  const html = fs.readFileSync(file, 'utf8');
  for (const phrase of phrases) if (!html.includes(phrase)) errors.push(`${rel}: תוכן חובה חסר - ${phrase}`);
}

for (const file of htmlFiles) {
  const rel = path.relative(root, file).replaceAll('\\', '/');
  const lines = fs.readFileSync(file, 'utf8').split(/\r?\n/);
  lines.forEach((line, i) => {
    if (/\s+$/.test(line)) errors.push(`${rel}:${i + 1}: רווחים מיותרים בסוף שורה`);
  });
}

console.log(`QA: ${counts.pages} עמודים, ${counts.links} קישורים, ${counts.images} תמונות, ${counts.anchors} עוגנים`);

const guide6File = path.join(root, 'guide-6/index.html');
if (fs.existsSync(guide6File)) {
  const guide6 = fs.readFileSync(guide6File, 'utf8');
  for (const phrase of ['אי אפשר לשתף שיחה שמכילה תוכן שסונכרן באמצעות Connector', 'Project פרטי']) {
    if (!guide6.includes(phrase)) errors.push(`guide-6/index.html: חסר הסבר עדכני על מגבלות שיתוף תוכן מ-Connector: ${phrase}`);
  }
}

if (errors.length) {
  console.error(errors.join('\n'));
  process.exit(1);
}
console.log('QA עבר בהצלחה');
