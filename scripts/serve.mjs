#!/usr/bin/env node

import fs from "node:fs";
import http from "node:http";
import path from "node:path";

const root = process.cwd();
const port = Number(process.env.PORT || 4173);
const mimeTypes = {
  ".css": "text/css; charset=utf-8",
  ".html": "text/html; charset=utf-8",
  ".ico": "image/x-icon",
  ".jpeg": "image/jpeg",
  ".jpg": "image/jpeg",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".png": "image/png",
  ".svg": "image/svg+xml",
  ".webp": "image/webp",
};

http.createServer((request, response) => {
  const requestedPath = decodeURIComponent(new URL(request.url, "http://localhost").pathname);
  let file = path.resolve(root, `.${requestedPath}`);
  if (!file.startsWith(root)) {
    response.writeHead(403).end("Forbidden");
    return;
  }
  if (fs.existsSync(file) && fs.statSync(file).isDirectory()) {
    file = path.join(file, "index.html");
  }
  if (!fs.existsSync(file) || !fs.statSync(file).isFile()) {
    file = path.join(root, "404.html");
    response.writeHead(404, { "Content-Type": mimeTypes[".html"] });
    response.end(fs.readFileSync(file));
    return;
  }
  response.writeHead(200, {
    "Content-Type": mimeTypes[path.extname(file).toLowerCase()] ?? "application/octet-stream",
  });
  fs.createReadStream(file).pipe(response);
}).listen(port, "127.0.0.1", () => {
  console.log(`Legal Mind RC2: http://127.0.0.1:${port}/`);
});
