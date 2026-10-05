# Excel mobile checks

Run from the repository root with Node.js, Playwright and Google Chrome available.
If Playwright is installed outside this repository, set `PLAYWRIGHT_MODULE` to its
absolute module path. Start `node scripts/serve.mjs` in another terminal, then run:

```text
node scripts/mobile-audit.cjs
node scripts/mobile-interactions.cjs
node scripts/mobile-links.cjs
node --test scripts/qa.test.mjs
node scripts/qa.mjs
```

The first three commands save screenshots and JSON evidence in `../mobile-qa`.
The layout check covers the main hub and all five Excel pages at widths 320, 390,
768, 820, 1024 and 1440. It forces lazy images to load before checking them.
The interaction check exercises all 33 copy buttons against the real clipboard,
blocked copying, TOC navigation, image annotations, native emulated touch panning,
keyboard activation, focus containment and focus restoration.
The resource check verifies local links, anchors, assets and downloads and compares
existing teaching text with HEAD before committing. The requested community/footer
and image-description repairs are excluded from that text comparison. It now also
requires the repository-wide QA gate to pass.

## 2026-10-05 result

- Base: `a4b11c2bbe57466ccd20b01c9a9b13aef59b4e61`.
- Scoped layout, interaction and resource checks pass.
- Five Excel pages: 183 local links, 94 fragment references, 122 images and eight
  download links; existing teaching text unchanged.
- The repository-wide gate passes: 50 pages, 1089 links, 734 images and 605 anchors.
  Repairs include 11 malformed Excel image descriptions, 15 missing screenshot
  descriptions, one broken internal anchor, punctuation and trailing whitespace.
  The checker now handles query strings, data URLs and inline code correctly;
  nine regression test groups verify that genuine errors are still rejected.
- The community section matches the supplied landing-page reference and stacks
  on phones. Its WhatsApp invitation comes from that page; Facebook and LinkedIn
  use the exact URLs supplied by the user. All four targets and touch areas were
  checked at 320, 390, 768, 1024 and 1272 pixels. Heebo is hosted locally with OFL.
- Checked in Chrome with touch/viewport emulation, not on physical iOS/Android
  devices or Safari.
- The supplied Google Drive HTML is a redirect to `/excel/`; no separate Drive
  content replacement is required.
