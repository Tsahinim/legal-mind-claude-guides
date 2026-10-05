# Excel mobile checks

Run from the repository root with Node.js, Playwright and Google Chrome available.
If Playwright is installed outside this repository, set `PLAYWRIGHT_MODULE` to its
absolute module path. Start `node scripts/serve.mjs` in another terminal, then run:

```text
node scripts/mobile-audit.cjs
node scripts/mobile-interactions.cjs
node scripts/mobile-links.cjs
node scripts/qa.mjs
```

The first three commands save screenshots and JSON evidence in `../mobile-qa`.
The layout check covers the main hub and all five Excel pages at widths 320, 390,
768, 820, 1024 and 1440. It forces lazy images to load before checking them.
The interaction check exercises all 33 copy buttons against the real clipboard,
blocked copying, TOC navigation, image annotations, native emulated touch panning,
keyboard activation, focus containment and focus restoration.
The resource check verifies local links, anchors, assets and downloads and compares
professional text with HEAD before committing. It also records the repository-wide
QA result and requires its findings to match HEAD's HTML (supplied in memory).

## 2026-10-05 result

- Base: `a4b11c2bbe57466ccd20b01c9a9b13aef59b4e61`.
- Scoped layout, interaction and resource checks pass.
- Five Excel pages: 183 local links, 94 fragment references, 120 images and eight
  download links; professional text unchanged.
- The full repository gate still exits 1 with exactly the same findings as the
  base. These include existing missing alt text, editorial whitespace, one missing
  anchor elsewhere, and false positives for query strings/data URLs. It is not a
  successful release gate; leave the change unpublished until resolved.
- Checked in Chrome with touch/viewport emulation, not on physical iOS/Android
  devices or Safari.
- The supplied Google Drive HTML is a redirect to `/excel/`; no separate Drive
  content replacement is required.
