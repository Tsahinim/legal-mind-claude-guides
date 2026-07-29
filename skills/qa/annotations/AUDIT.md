# Skills screenshot annotation audit

Audit date: 2026-07-29
Browser viewports: desktop 1440×1000; mobile 390×844

## Scope and inventory

The complete five-guide series was inspected in a real browser.

| Page | Annotated screenshots | Markers | Legend explanations |
| --- | ---: | ---: | ---: |
| `skills/guide-1/index.html` | 0 | 0 | 0 |
| `skills/guide-2/index.html` | 0 | 0 | 0 |
| `skills/guide-3/index.html` | 8 | 10 | 10 |
| `skills/guide-4/index.html` | 8 | 12 | 12 |
| `skills/guide-5/index.html` | 0 | 0 | 0 |
| **Total** | **16** | **22** | **22** |

The screenshots are embedded PNG data URLs rather than separate image files. Their original pixels and accessibility descriptions were preserved.

## Per-screenshot findings

“Badge sufficient?” is “No” in every row: the number identifies the matching explanation, but the target itself also needs a visible outline.

| ID | Page and section | Embedded image | Markers / explanations | Explanation target | Marker before | Correct target and annotation |
| --- | --- | --- | ---: | --- | --- | --- |
| G3-1 | Guide 3 — ראיון האפיון בשיחה | 957×357 PNG | 1 / 1 | Mixed PDF, Word, email and images option | On the selected row; approximately correct | Selected option row; full-width rectangle with attached badge |
| G3-2 | Guide 3 — ראיון האפיון בשיחה | 931×345 PNG | 1 / 1 | “טבלה בתוך הצ'אט + קובץ” | On option 3, PDF; incorrect coordinate | Option 4 row; full-width rectangle with attached badge |
| G3-3 | Guide 3 — ראיון האפיון בשיחה | 936×342 PNG | 1 / 1 | Include event with “תאריך לא ודאי” | On option 3; incorrect coordinate | Option 2 row; full-width rectangle with attached badge |
| G3-4 | Guide 3 — יצירת הסקיל | 725×538 PNG | 1 / 1 | `legal-chronology` result row, Save skill and download controls | Badge covered the Save skill area | Result row; rectangle with badge on the row edge |
| G3-5 | Guide 3 — יצירת הסקיל | 330×86 PNG | 1 / 1 | “Skill saved” toast and Manage link | Badge covered the toast text | Entire toast; rectangle with badge outside the text |
| G3-6 | Guide 3 — יצירת הסקיל | 947×420 PNG | 1 / 1 | Active `legal-chronology` row | Badge sat in the header/empty area | Exact first skill row; full-width rectangle |
| G3-7 | Guide 3 — אנטומיה של הסקיל המשפטי שיצרנו | 941×827 PNG | 1 / 1 | “עקרון-העל: איסור המצאת תאריכים” | Badge covered the heading | Heading and rule line; rectangle with badge on the edge |
| G3-8 | Guide 3 — דוגמה מלאה: מקלט מבולגן לטבלה מסודרת | 1867×887 PNG | 3 / 3 | Left test summary; right chronology table; undated events and sources | Three approximate badges without target boundaries | Three separate region rectangles, each with its matching badge |
| G4-1 | Guide 4 — איתור אזור הסקילים | 357×295 PNG | 1 / 1 | Customize navigation row | Badge covered the label | Customize row; rectangle with badge beside it |
| G4-2 | Guide 4 — איתור אזור הסקילים | 1186×767 PNG | 2 / 2 | Skills sub-navigation; Add menu and its three actions | Badges covered the Skills label and Add control | Two rectangles: Skills row and open Add menu |
| G4-3 | Guide 4 — התקנת סקיל שהכנו | 893×338 PNG | 1 / 1 | `legal-docx` skill row | Badge appeared between the preceding and target rows | Exact `legal-docx` row; full-width rectangle |
| G4-4 | Guide 4 — התקנת סקיל שהכנו | 933×873 PNG | 1 / 1 | Enabled toggle | Near the toggle but without a boundary | Tight circular outline around the toggle; badge offset beside it |
| G4-5 | Guide 4 — ספריית הסקילים | 367×77 PNG | 1 / 1 | Browse button | Badge sat between Browse and Add and obscured the controls | Tight rectangle around Browse; badge on its edge |
| G4-6 | Guide 4 — ספריית הסקילים | 1272×880 PNG | 3 / 3 | Skills category; Search skills field; install plus | Badges were approximate; marker 3 was in empty card space | Two rectangles and a circle around the exact plus control |
| G4-7 | Guide 4 — כיצד יודעים שהסקיל הופעל | 957×151 PNG | 2 / 2 | Request text; send button | Badges covered both targets | Request-field rectangle and send-button circle |
| G4-8 | Guide 4 — כיצד יודעים שהסקיל הופעל | 952×350 PNG | 1 / 1 | “Loaded docx skill” status row | Badge floated above/right of the row | Tight row rectangle with badge on its edge |

## Root cause

The problem was a combination of:

1. **CSS rendering:** existing target rectangles used the generic `.mk` class, but `.mk` was already the circular legend-number style. The inline `left`, `top`, `width` and `height` values therefore did not create positioned overlays.
2. **Incorrect coordinates:** several standalone badge coordinates targeted the wrong option, the row header, or empty card space.
3. **Insufficient annotation design:** standalone badges did not surround the referenced control or region and sometimes covered important text.
4. **Responsive readability:** percentage coordinates scaled with the image, so there was no general responsive drift. However, fixed-size standalone badges occupied a larger portion of the interface at mobile width and hid more content.

Image aspect ratios and image sizing were correct. The source PNGs were not modified.

## Implementation

- Added the reusable `.shot-target`, `.shot-target-badge` and circular-target variants.
- Kept every target inside its `.shot-frame`, so all coordinates remain relative to the displayed image.
- Replaced all 22 standalone badges with 22 outlined targets and attached badges.
- Used thinner outlines and smaller badges below 640px.
- Preserved all legend text, alt text, source images, links, anchors and navigation.

## Browser validation

Every screenshot was rendered again at both viewports. For every desktop and mobile rendering:

- target count = badge count = legend explanation count;
- no `.shot-marker` standalone badge remains;
- all embedded images loaded at their original natural dimensions;
- outlines remained attached to the same image-relative target while scaling;
- badges did not cover the target’s important text;
- desktop and mobile legends remained readable.

## Before-and-after evidence

Each link is a real browser viewport capture. Every changed image has desktop and mobile before/after evidence.

| ID | Desktop before | Desktop after | Mobile before | Mobile after |
| --- | --- | --- | --- | --- |
| G3-1 | [before](before/desktop/guide-3-shot-1-desktop.png) | [after](after/desktop/guide-3-shot-1-desktop.png) | [before](before/mobile/guide-3-shot-1-mobile.png) | [after](after/mobile/guide-3-shot-1-mobile.png) |
| G3-2 | [before](before/desktop/guide-3-shot-2-desktop.png) | [after](after/desktop/guide-3-shot-2-desktop.png) | [before](before/mobile/guide-3-shot-2-mobile.png) | [after](after/mobile/guide-3-shot-2-mobile.png) |
| G3-3 | [before](before/desktop/guide-3-shot-3-desktop.png) | [after](after/desktop/guide-3-shot-3-desktop.png) | [before](before/mobile/guide-3-shot-3-mobile.png) | [after](after/mobile/guide-3-shot-3-mobile.png) |
| G3-4 | [before](before/desktop/guide-3-shot-4-desktop.png) | [after](after/desktop/guide-3-shot-4-desktop.png) | [before](before/mobile/guide-3-shot-4-mobile.png) | [after](after/mobile/guide-3-shot-4-mobile.png) |
| G3-5 | [before](before/desktop/guide-3-shot-5-desktop.png) | [after](after/desktop/guide-3-shot-5-desktop.png) | [before](before/mobile/guide-3-shot-5-mobile.png) | [after](after/mobile/guide-3-shot-5-mobile.png) |
| G3-6 | [before](before/desktop/guide-3-shot-6-desktop.png) | [after](after/desktop/guide-3-shot-6-desktop.png) | [before](before/mobile/guide-3-shot-6-mobile.png) | [after](after/mobile/guide-3-shot-6-mobile.png) |
| G3-7 | [before](before/desktop/guide-3-shot-7-desktop.png) | [after](after/desktop/guide-3-shot-7-desktop.png) | [before](before/mobile/guide-3-shot-7-mobile.png) | [after](after/mobile/guide-3-shot-7-mobile.png) |
| G3-8 | [before](before/desktop/guide-3-shot-8-desktop.png) | [after](after/desktop/guide-3-shot-8-desktop.png) | [before](before/mobile/guide-3-shot-8-mobile.png) | [after](after/mobile/guide-3-shot-8-mobile.png) |
| G4-1 | [before](before/desktop/guide-4-shot-1-desktop.png) | [after](after/desktop/guide-4-shot-1-desktop.png) | [before](before/mobile/guide-4-shot-1-mobile.png) | [after](after/mobile/guide-4-shot-1-mobile.png) |
| G4-2 | [before](before/desktop/guide-4-shot-2-desktop.png) | [after](after/desktop/guide-4-shot-2-desktop.png) | [before](before/mobile/guide-4-shot-2-mobile.png) | [after](after/mobile/guide-4-shot-2-mobile.png) |
| G4-3 | [before](before/desktop/guide-4-shot-3-desktop.png) | [after](after/desktop/guide-4-shot-3-desktop.png) | [before](before/mobile/guide-4-shot-3-mobile.png) | [after](after/mobile/guide-4-shot-3-mobile.png) |
| G4-4 | [before](before/desktop/guide-4-shot-4-desktop.png) | [after](after/desktop/guide-4-shot-4-desktop.png) | [before](before/mobile/guide-4-shot-4-mobile.png) | [after](after/mobile/guide-4-shot-4-mobile.png) |
| G4-5 | [before](before/desktop/guide-4-shot-5-desktop.png) | [after](after/desktop/guide-4-shot-5-desktop.png) | [before](before/mobile/guide-4-shot-5-mobile.png) | [after](after/mobile/guide-4-shot-5-mobile.png) |
| G4-6 | [before](before/desktop/guide-4-shot-6-desktop.png) | [after](after/desktop/guide-4-shot-6-desktop.png) | [before](before/mobile/guide-4-shot-6-mobile.png) | [after](after/mobile/guide-4-shot-6-mobile.png) |
| G4-7 | [before](before/desktop/guide-4-shot-7-desktop.png) | [after](after/desktop/guide-4-shot-7-desktop.png) | [before](before/mobile/guide-4-shot-7-mobile.png) | [after](after/mobile/guide-4-shot-7-mobile.png) |
| G4-8 | [before](before/desktop/guide-4-shot-8-desktop.png) | [after](after/desktop/guide-4-shot-8-desktop.png) | [before](before/mobile/guide-4-shot-8-mobile.png) | [after](after/mobile/guide-4-shot-8-mobile.png) |

## Repository validation

- `node scripts/qa.mjs`: passed — 14 pages, 312 links, 60 images and 156 anchors checked.
- `git diff --check`: passed.
- A byte-level comparison against `origin/main` confirmed that all 16 embedded PNG payloads and their alt text are unchanged.
- After removing annotation markup from both versions, the guide content is identical to `origin/main`; no unrelated prose, links, anchors or navigation changed.
