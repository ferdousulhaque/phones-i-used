# Phone Images & Validation — Design Spec

## Overview

Add phone model images, autocomplete search, and input validation to the Phones I Used timeline app. Data sourced from Wikipedia/Wikimedia Commons via a build-time scraper, served as a static JSON file, searched with Fuse.js fuzzy matching.

## Goals

- Show real phone images in timeline cards instead of emoji placeholders
- Autocomplete phone model input from a curated dataset of ~300-500 popular models
- Validate year input (1990-2026) with inline error feedback
- Keep zero-backend architecture — all data is static
- No images stored in repo — hotlink from Wikimedia Commons
- Backward compatible with existing shared URL hashes

## Non-Goals

- Comprehensive phone database (every model ever made)
- Runtime scraping or API calls to external services
- User accounts, server-side storage
- Pre-1990 phone coverage

---

## 1. Data Pipeline (Scraper)

**File:** `scripts/scrape-phones.py` (Python 3)

**Dependencies:** `requests`, `beautifulsoup4`

**Source:** Wikipedia "List of [Brand] mobile phones" articles.

**Brands covered:**
Nokia, Samsung, Apple (iPhone), Motorola, Sony Ericsson/Sony, LG, HTC, Huawei, OnePlus, Google (Pixel), Xiaomi, BlackBerry, Oppo, Vivo, Realme

**Process:**
1. Fetch each brand's Wikipedia list page
2. Parse model names and release years from tables
3. For each model, fetch the phone's own Wikipedia article and extract the infobox thumbnail image URL (Wikimedia Commons)
4. Filter to years 2000-2026 only
5. Models without images get `null` for the image field
6. Output `phones.json` in project root

**Rate limiting:** 1-second delay between Wikipedia requests. Descriptive User-Agent header.

**Execution:** Manual — run `python scripts/scrape-phones.py` to refresh. Not automated.

---

## 2. Data Schema (`phones.json`)

```json
[
  {
    "brand": "Nokia",
    "name": "Nokia 3310",
    "year": 2000,
    "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/..."
  },
  {
    "brand": "Apple",
    "name": "iPhone 4",
    "year": 2010,
    "image": null
  }
]
```

- Flat array, ~300-500 entries
- `name` includes brand prefix (e.g., "Samsung Galaxy S24" not "Galaxy S24")
- `year` is integer — release year
- `image` is full Wikimedia Commons thumbnail URL, or `null`
- No `id` field — `brand + name` is unique
- Estimated size: ~50-80KB uncompressed, ~15-20KB gzipped
- Sorted alphabetically by brand, then by year

---

## 3. Frontend — Autocomplete UI

**New dependency:** Fuse.js v7 from CDN (`https://cdn.jsdelivr.net/npm/fuse.js@7.0.0`), ~6KB gzipped.

**Behavior:**
1. On page load, fetch `phones.json` and build a Fuse index on `name` and `brand` fields
2. Phone name input triggers autocomplete after 2+ characters typed
3. Dropdown shows max 8 results, each row: `brand · model name · year`
4. Selection fills phone name and auto-fills year field
5. Free-text entry still allowed — user can ignore dropdown

**Dropdown styling:**
- Absolute positioned below input
- Glass-card style matching app aesthetic
- `bg-white/10` highlight on focused item
- Keyboard navigable: arrow keys, Enter to select, Escape to dismiss
- Dismiss on click outside

**Graceful degradation:**
- If `phones.json` fetch fails, autocomplete silently disabled
- App works identically to current version — free-text, no images
- No error shown to user

---

## 4. Frontend — Year Validation

**Input:** Remains a number field.

**Valid range:** 1990-2026

**Validation triggers:** On blur and on Generate button click.

**Error display:**
- Inline text below input: `text-red-400 text-xs`
- Input border: `border-red-400` on error
- Messages: "Year required" (empty), "Enter year between 1990-2026" (out of range)
- Errors clear as user types valid value

**Generate button:**
- Validates all entries before generating timeline
- If any invalid, scrolls to first error, blocks generation
- Replaces current `alert()` with inline validation

**Pre-2000 phones (1990-1999):**
- Fully allowed
- Timeline shows default phone icon (image data covers 2000+ only)
- No warning or special treatment

---

## 5. Frontend — Timeline with Images

**Card changes:**
- Emoji placeholder replaced with `<img>` tag
- Image sized ~80x100px, `object-contain`, centered
- `loading="lazy"` for off-screen cards

**Default fallback:**
- Inline SVG smartphone silhouette for: no image match, custom entries, pre-2000 phones
- Applied via `onerror` handler on `<img>` — no broken image icon ever visible
- Same dimensions as real images to prevent layout shift

**Image matching at generate time:**
1. Look up entry's `name` in phones.json dataset
2. Exact match on `name` field first
3. Fall back to Fuse fuzzy match with score threshold 0.3
4. No match = default SVG icon

**URL hash unchanged:**
- Format stays `#phones=year,name|year,name|...`
- No image URLs stored in hash
- Images resolved at render time from JSON data
- Existing shared links gain images automatically

---

## File Changes Summary

| File | Change |
|------|--------|
| `scripts/scrape-phones.py` | New — Wikipedia scraper |
| `phones.json` | New — generated phone dataset |
| `index.html` | Modified — Fuse.js CDN, autocomplete, validation, image cards |
| `.gitignore` | May need update if `phones.json` should/shouldn't be committed |

**Note:** `phones.json` should be committed to repo (it's the generated dataset viewers need). Only images are not stored — they're hotlinked from Wikimedia Commons.
