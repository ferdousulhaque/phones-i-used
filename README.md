# 📱 Phones I Used

A small nostalgia project for visualizing the phones you've owned or used over time.

This repo contains a single-page web app that renders a horizontal timeline of devices, plus a helper script to gather phone model data from Wikipedia.

## What it does

- Displays a visual timeline of phones by year
- Lets you browse brands and device names
- Includes a searchable, scrollable interface
- Uses a structured `phones.json` dataset for the timeline
- Can regenerate the dataset with the scraper script

## Project structure

- `index.html` — the interactive front-end
- `phones.json` — phone data used by the timeline
- `scripts/scrape-phones.py` — scraper for pulling phone models from Wikipedia
- `scripts/requirements.txt` — Python dependencies for the scraper

## Quick start

### Run the site locally

From the project root:

```bash
python3 -m http.server 8000
```

Then open:

```text
http://localhost:8000
```

## Refresh the phone data

Install dependencies:

```bash
python3 -m pip install -r scripts/requirements.txt
```

Then run:

```bash
python3 scripts/scrape-phones.py
```

This writes a refreshed `phones.json` file in the project root.

## Notes

- The scraper is intentionally rate-limited and polite to Wikipedia.
- If scraping fails or data is incomplete, the script falls back to a curated list of common models.
- The UI is static HTML/JavaScript, so there is no build or framework setup required.

## License

This project is for personal/demo use unless otherwise specified.
