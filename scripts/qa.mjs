#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const root = process.cwd();
const required = [
  "index.html",
  "404.html",
  "assets",
  "skills/index.html",
  ".nojekyll",
  ...Array.from({ length: 6 }, (_, index) => `guide-${index + 1}/index.html`),
];
const failures = [];
const checked = {
  htmlFiles: 0,
  links: 0,
  images: 0,
  anchors: 0,
  cssUrls: 0,
};

const fail = (message) => failures.push(message);
const relative = (file) => path.relative(root, file).replaceAll("\\", "/");

for (const entry of required) {
  if (!fs.existsSync(path.join(root, entry))) {
    fail(`חסר רכיב חובה: ${entry}`);
  }
}

function walk(directory) {
  const result = [];
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    if (entry.name === ".git" || entry.name === "node_modules") continue;
    const full = path.join(directory, entry.name);
    if (entry.isDirectory()) result.push(...walk(full));
    else result.push(full);
  }
  return result;
}

const allFiles = walk(root);
const htmlFiles = allFiles.filter((file) => file.endsWith(".html"));
const htmlCache = new Map(
  htmlFiles.map((file) => [file, fs.readFileSync(file, "utf8")]),
);
const idsByFile = new Map();

function attributes(tag) {
  const result = new Map();
  const expression = /([^\s"'=<>`]+)\s*=\s*(?:"([^"]*)"|'([^']*)')/g;
  for (const match of tag.matchAll(expression)) {
    result.set(match[1].toLowerCase(), match[2] ?? match[3] ?? "");
  }
  return result;
}

function idsFor(file) {
  if (idsByFile.has(file)) return idsByFile.get(file);
  const html = htmlCache.get(file);
  const ids = new Set();
  const duplicates = new Set();
  for (const match of html.matchAll(/\bid\s*=\s*(?:"([^"]+)"|'([^']+)')/gi)) {
    const id = match[1] ?? match[2];
    if (ids.has(id)) duplicates.add(id);
    ids.add(id);
  }
  for (const id of duplicates) fail(`${relative(file)}: מזהה כפול #${id}`);
  idsByFile.set(file, ids);
  return ids;
}

function isExternal(value) {
  return /^(?:https?:|mailto:|tel:|javascript:|blob:)/i.test(value);
}

function resolveTarget(sourceFile, rawValue) {
  const value = rawValue.trim();
  if (!value || isExternal(value)) return null;
  if (/^data:/i.test(value)) return { data: true, value };

  const hashIndex = value.indexOf("#");
  const queryIndex = value.indexOf("?");
  const pathEndCandidates = [hashIndex, queryIndex].filter((index) => index >= 0);
  const pathEnd = pathEndCandidates.length ? Math.min(...pathEndCandidates) : value.length;
  const rawPath = value.slice(0, pathEnd);
  const fragment = hashIndex >= 0
    ? value.slice(hashIndex + 1).split("?")[0]
    : "";

  let decodedPath;
  let decodedFragment;
  try {
    decodedPath = decodeURIComponent(rawPath);
    decodedFragment = decodeURIComponent(fragment);
  } catch {
    fail(`${relative(sourceFile)}: כתובת אינה מקודדת באופן תקין: ${value}`);
    return null;
  }

  let target = decodedPath.startsWith("/")
    ? path.join(root, decodedPath.replace(/^[/\\]+/, ""))
    : path.resolve(path.dirname(sourceFile), decodedPath || ".");
  if (!target.startsWith(root)) {
    fail(`${relative(sourceFile)}: קישור יוצא משורש המאגר: ${value}`);
    return null;
  }
  if (fs.existsSync(target) && fs.statSync(target).isDirectory()) {
    target = path.join(target, "index.html");
  }
  return { target, fragment: decodedFragment, value };
}

function validateReference(sourceFile, value, kind) {
  const resolved = resolveTarget(sourceFile, value);
  if (!resolved) return;
  if (resolved.data) {
    if (kind === "image" && !/^data:image\/[a-z0-9.+-]+;base64,[a-z0-9+/=\s]+$/i.test(resolved.value)) {
      fail(`${relative(sourceFile)}: נתוני תמונה משובצים אינם תקינים`);
    }
    return;
  }
  if (!fs.existsSync(resolved.target)) {
    fail(`${relative(sourceFile)}: יעד ${kind} חסר: ${value}`);
    return;
  }
  if (resolved.fragment) {
    checked.anchors += 1;
    if (!resolved.target.endsWith(".html")) {
      fail(`${relative(sourceFile)}: עוגן מפנה לקובץ שאינו HTML: ${value}`);
      return;
    }
    const targetHtml = htmlCache.get(resolved.target)
      ?? fs.readFileSync(resolved.target, "utf8");
    if (!htmlCache.has(resolved.target)) htmlCache.set(resolved.target, targetHtml);
    const namedAnchors = new Set(
      [...targetHtml.matchAll(/<a\b[^>]*\bname\s*=\s*(?:"([^"]+)"|'([^']+)')[^>]*>/gi)]
        .map((match) => match[1] ?? match[2]),
    );
    if (!idsFor(resolved.target).has(resolved.fragment) && !namedAnchors.has(resolved.fragment)) {
      fail(`${relative(sourceFile)}: עוגן חסר ביעד: ${value}`);
    }
  }
}

for (const file of htmlFiles) {
  checked.htmlFiles += 1;
  const html = htmlCache.get(file);
  idsFor(file);

  const htmlTag = html.match(/<html\b[^>]*>/i)?.[0] ?? "";
  const htmlAttrs = attributes(htmlTag);
  if (htmlAttrs.get("dir")?.toLowerCase() !== "rtl") {
    fail(`${relative(file)}: חסר dir="rtl"`);
  }
  if (htmlAttrs.get("lang")?.toLowerCase() !== "he") {
    fail(`${relative(file)}: חסר lang="he"`);
  }

  for (const match of html.matchAll(/<a\b[^>]*>/gi)) {
    const href = attributes(match[0]).get("href");
    if (href === undefined) continue;
    checked.links += 1;
    validateReference(file, href, "קישור");
  }

  for (const match of html.matchAll(/<img\b[^>]*>/gi)) {
    const attrs = attributes(match[0]);
    const src = attrs.get("src");
    checked.images += 1;
    if (!src) fail(`${relative(file)}: תמונה ללא src`);
    else validateReference(file, src, "image");
    if (!attrs.get("alt")?.trim()) fail(`${relative(file)}: תמונה ללא alt`);
  }

  for (const attribute of ["src", "poster"]) {
    const expression = new RegExp(`<(?!(?:img)\\b)[a-z][^>]*\\b${attribute}\\s*=\\s*(?:"([^"]+)"|'([^']+)')[^>]*>`, "gi");
    for (const match of html.matchAll(expression)) {
      validateReference(file, match[1] ?? match[2], "משאב");
    }
  }
}

for (const file of allFiles.filter((candidate) => candidate.endsWith(".css"))) {
  const css = fs.readFileSync(file, "utf8");
  for (const match of css.matchAll(/url\(\s*(?:"([^"]+)"|'([^']+)'|([^)'"\s]+))\s*\)/gi)) {
    const value = match[1] ?? match[2] ?? match[3];
    checked.cssUrls += 1;
    validateReference(file, value, "משאב CSS");
  }
}

const hub = htmlCache.get(path.join(root, "index.html")) ?? "";
for (let guide = 1; guide <= 6; guide += 1) {
  if (!new RegExp(`href\\s*=\\s*["'][^"']*guide-${guide}(?:/|/index\\.html|index\\.html)`, "i").test(hub)) {
    fail(`index.html: אין קישור למדריך ${guide}`);
  }
}

for (let guide = 1; guide <= 6; guide += 1) {
  const file = path.join(root, `guide-${guide}`, "index.html");
  if (!htmlCache.has(file)) continue;
  const html = htmlCache.get(file);
  const localLinks = [...html.matchAll(/<a\b[^>]*>/gi)]
    .map((match) => attributes(match[0]).get("href"))
    .filter(Boolean);
  if (!localLinks.some((href) => /(?:^|\/)(?:index\.html)?(?:#.*)?$/.test(href) && href.includes(".."))) {
    fail(`guide-${guide}/index.html: חסר קישור חזרה למרכז`);
  }
  if (guide > 1 && !localLinks.some((href) => href.includes(`guide-${guide - 1}`))) {
    fail(`guide-${guide}/index.html: חסר קישור למדריך הקודם`);
  }
  if (guide < 6 && !localLinks.some((href) => href.includes(`guide-${guide + 1}`))) {
    fail(`guide-${guide}/index.html: חסר קישור למדריך הבא`);
  }
}

console.log(
  `QA: ${checked.htmlFiles} קובצי HTML, ${checked.links} קישורים, `
  + `${checked.images} תמונות, ${checked.anchors} עוגנים ו-${checked.cssUrls} משאבי CSS.`,
);

if (failures.length) {
  console.error(`נמצאו ${failures.length} תקלות:`);
  failures.forEach((failure) => console.error(`- ${failure}`));
  process.exitCode = 1;
} else {
  console.log("כל בדיקות ה-QA עברו בהצלחה.");
}
