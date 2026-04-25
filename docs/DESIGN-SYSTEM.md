# DESIGN-SYSTEM — visual spec for the `ainfera` CLI

This document is the visual companion to `BRAND-WORDS.md`. Where
`BRAND-WORDS` governs *what* we say, `DESIGN-SYSTEM` governs *how it
looks* in the terminal.

The numbered sections are stable anchors and may be referenced by
PR templates and CI checks (e.g. `§6 hue rule`).

---

## §1 — Brand palette

The canonical palette is navy-anchored:

| Token              | Hex       | Use |
| ------------------ | --------- | --- |
| `ainfera.brand`    | `#2878B5` | Wordmark, primary headings, hyperlink accents |
| `ainfera.hover`    | `#4A9FD9` | Lighter navy for hover/secondary accents |
| `ainfera.highlight`| `#7EC4EF` | High-contrast highlight on dark surfaces |
| `ainfera.surface`  | `#001E41` | Deepest brand surface (banner backgrounds) |
| `ainfera.text`     | `#F7F5F0` | Primary text on dark surface |
| `ainfera.muted`    | `#64748B` | De-emphasized labels, hints, captions |

The brand palette is *identity*, not status. It carries no
"good/bad" semantics — see §6.

## §2 — Typography (terminal output)

Terminals don't ship typefaces; we lean on weight and style instead:

| Role     | Rich style attribute     |
| -------- | ------------------------ |
| Heading  | `bold`                   |
| Subhead  | `bold dim`               |
| Body     | `default`                |
| Label    | `italic`                 |
| Caption  | `dim`                    |
| Code     | wrap in backticks; let the terminal render mono |

## §3 — Iconography

ASCII / Unicode glyphs only. No images, no escape-art logos:

| Glyph | Meaning                                      |
| ----- | -------------------------------------------- |
| `◆`   | Wordmark mark (header banner)                |
| `▸`   | Step indicator (in-progress)                 |
| `✓`   | Step indicator (complete) / affirmative      |
| `✗`   | Failure / negative                           |
| `→`   | Hint / next-action pointer                   |
| `⚠`   | Warning glyph (no color — see §6)            |

## §4 — Layout

- 2-space leading indent on all printed lines (gutter)
- Single blank line between logical sections
- Tables: Rich `Table` with `box=ROUNDED`, header style `bold`
- Banners: print mark, then product line, then blank line
- Wrap long output at 80 cols; trust bars at 20 cols

## §5 — Trust score visualization

Five bars, one per ATS dimension (`Safety · Reliability · Quality
· Performance · Reputation`). Bars are filled with `█` and ticks
of `▉ ▊ ▋ ▌ ▍ ▎ ▏` for fractional eighths:

```
Safety:      0.91 ████████▉
Reliability: 0.88 ████████▊
Quality:     0.85 ████████▍
Performance: 0.87 ████████▋
Reputation:  0.82 ████████▏
ATS: AA 847
```

The bar width is 20 characters at score `1.00`. The dimension
label is left-padded to the longest label in the set so the bar
left edges align.

## §6 — Hue rule (status semantics)

**Status colors do not exist in this CLI.** Success, warning, and
error states are conveyed by *weight and intensity*, never by hue:

| Style token         | Rich attribute | Used for                      |
| ------------------- | -------------- | ----------------------------- |
| `ainfera.success`   | `default`      | Success, "ok", normal state   |
| `ainfera.warning`   | `dim`          | Caution, soft warnings        |
| `ainfera.error`     | `bold`         | Errors, critical failures     |
| `ainfera.info`      | `italic`       | Informational asides          |
| `ainfera.muted`     | `dim`          | De-emphasized text            |

Rationale: hue-based status (red/yellow/green) fails on
colorblind terminals, light-on-dark inversions, locked-down CI
log viewers, and any `NO_COLOR=1` environment. Weight/intensity
survives all of those.

The brand navy (`ainfera.brand`, `ainfera.highlight`) may be used
for *identity* — the wordmark, headings, table headers — but
never to encode "this is good" or "this failed."

**Forbidden in `src/`:**

- Rich color markup like `[red]`, `[green]`, `[yellow]`,
  `[orange]`, `[blue]`, `[magenta]`, `[cyan]`
- Inline `style="red"` / `style="green"` etc. in Rich calls
- Hex colors that read as red/yellow/green semantically tied to
  status names (`success=#5B8C6A`, `warning=#D4A43A`,
  `error=#C4453A`)

Pre-push grep:

```bash
grep -rEn "\[(red|green|yellow|orange|blue|magenta|cyan)\]|\[bold (red|green|yellow|orange|blue|magenta|cyan)\]" src/
grep -rEn "style=\"(red|green|yellow|orange|blue|magenta|cyan)" src/
```

## §7 — Trust grade rendering

Grades render as `bold` (top half: AAA, AA, A, BBB) or `dim`
(bottom half: BB, B) — no hue. `CCC` quarantine state renders as
`bold` with the prefix glyph `✗`.

## §8 — `NO_COLOR` and accessibility

The CLI must respect `NO_COLOR=1`. Because §6 forbids hue-based
status anyway, the only effect of `NO_COLOR=1` is suppressing the
brand navy on the wordmark and headers — the semantics of the
output are unchanged.
