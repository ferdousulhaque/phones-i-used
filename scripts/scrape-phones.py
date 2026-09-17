#!/usr/bin/env python3
"""
Scrape popular phone models from Wikipedia and output phones.json.

Usage: python scripts/scrape-phones.py
Output: phones.json in the project root directory.

Rate-limited to 1 request/second. Be respectful to Wikipedia servers.
"""

import json
import re
import time
import os
import sys
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "phones.json")

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "PhonesIUsedBot/1.0 (https://github.com; educational project; scrape-phones.py)"
})

WIKI_BASE = "https://en.wikipedia.org"

BRAND_PAGES = {
    "Nokia": "/wiki/List_of_Nokia_products",
    "Samsung": "/wiki/Samsung_Galaxy",
    "Apple": "/wiki/IPhone",
    "Motorola": "/wiki/List_of_Motorola_products",
    "Sony": "/wiki/List_of_Sony_Mobile_products",
    "LG": "/wiki/List_of_LG_mobile_phones",
    "HTC": "/wiki/List_of_HTC_phones",
    "Huawei": "/wiki/List_of_Huawei_phones",
    "OnePlus": "/wiki/OnePlus",
    "Google": "/wiki/Pixel_(smartphone)",
    "Xiaomi": "/wiki/List_of_Xiaomi_products",
    "BlackBerry": "/wiki/List_of_BlackBerry_products",
    "Oppo": "/wiki/List_of_Oppo_smartphones",
    "Vivo": "/wiki/List_of_Vivo_smartphones",
    "Realme": "/wiki/Realme",
}

FALLBACK_PHONES = [
    {"brand": "Apple", "name": "iPhone", "year": 2007},
    {"brand": "Apple", "name": "iPhone 3G", "year": 2008},
    {"brand": "Apple", "name": "iPhone 3GS", "year": 2009},
    {"brand": "Apple", "name": "iPhone 4", "year": 2010},
    {"brand": "Apple", "name": "iPhone 4S", "year": 2011},
    {"brand": "Apple", "name": "iPhone 5", "year": 2012},
    {"brand": "Apple", "name": "iPhone 5S", "year": 2013},
    {"brand": "Apple", "name": "iPhone 5C", "year": 2013},
    {"brand": "Apple", "name": "iPhone 6", "year": 2014},
    {"brand": "Apple", "name": "iPhone 6 Plus", "year": 2014},
    {"brand": "Apple", "name": "iPhone 6S", "year": 2015},
    {"brand": "Apple", "name": "iPhone 6S Plus", "year": 2015},
    {"brand": "Apple", "name": "iPhone SE", "year": 2016},
    {"brand": "Apple", "name": "iPhone 7", "year": 2016},
    {"brand": "Apple", "name": "iPhone 7 Plus", "year": 2016},
    {"brand": "Apple", "name": "iPhone 8", "year": 2017},
    {"brand": "Apple", "name": "iPhone 8 Plus", "year": 2017},
    {"brand": "Apple", "name": "iPhone X", "year": 2017},
    {"brand": "Apple", "name": "iPhone XR", "year": 2018},
    {"brand": "Apple", "name": "iPhone XS", "year": 2018},
    {"brand": "Apple", "name": "iPhone XS Max", "year": 2018},
    {"brand": "Apple", "name": "iPhone 11", "year": 2019},
    {"brand": "Apple", "name": "iPhone 11 Pro", "year": 2019},
    {"brand": "Apple", "name": "iPhone 11 Pro Max", "year": 2019},
    {"brand": "Apple", "name": "iPhone SE 2nd generation", "year": 2020},
    {"brand": "Apple", "name": "iPhone 12", "year": 2020},
    {"brand": "Apple", "name": "iPhone 12 Mini", "year": 2020},
    {"brand": "Apple", "name": "iPhone 12 Pro", "year": 2020},
    {"brand": "Apple", "name": "iPhone 12 Pro Max", "year": 2020},
    {"brand": "Apple", "name": "iPhone 13", "year": 2021},
    {"brand": "Apple", "name": "iPhone 13 Mini", "year": 2021},
    {"brand": "Apple", "name": "iPhone 13 Pro", "year": 2021},
    {"brand": "Apple", "name": "iPhone 13 Pro Max", "year": 2021},
    {"brand": "Apple", "name": "iPhone SE 3rd generation", "year": 2022},
    {"brand": "Apple", "name": "iPhone 14", "year": 2022},
    {"brand": "Apple", "name": "iPhone 14 Plus", "year": 2022},
    {"brand": "Apple", "name": "iPhone 14 Pro", "year": 2022},
    {"brand": "Apple", "name": "iPhone 14 Pro Max", "year": 2022},
    {"brand": "Apple", "name": "iPhone 15", "year": 2023},
    {"brand": "Apple", "name": "iPhone 15 Plus", "year": 2023},
    {"brand": "Apple", "name": "iPhone 15 Pro", "year": 2023},
    {"brand": "Apple", "name": "iPhone 15 Pro Max", "year": 2023},
    {"brand": "Apple", "name": "iPhone 16", "year": 2024},
    {"brand": "Apple", "name": "iPhone 16 Plus", "year": 2024},
    {"brand": "Apple", "name": "iPhone 16 Pro", "year": 2024},
    {"brand": "Apple", "name": "iPhone 16 Pro Max", "year": 2024},
    {"brand": "Nokia", "name": "Nokia 3310", "year": 2000},
    {"brand": "Nokia", "name": "Nokia 1100", "year": 2003},
    {"brand": "Nokia", "name": "Nokia N73", "year": 2006},
    {"brand": "Nokia", "name": "Nokia N95", "year": 2007},
    {"brand": "Samsung", "name": "Samsung Galaxy S", "year": 2010},
    {"brand": "Samsung", "name": "Samsung Galaxy S II", "year": 2011},
    {"brand": "Samsung", "name": "Samsung Galaxy S III", "year": 2012},
    {"brand": "Samsung", "name": "Samsung Galaxy S4", "year": 2013},
    {"brand": "Samsung", "name": "Samsung Galaxy S5", "year": 2014},
    {"brand": "Samsung", "name": "Samsung Galaxy S6", "year": 2015},
    {"brand": "Samsung", "name": "Samsung Galaxy S7", "year": 2016},
    {"brand": "Samsung", "name": "Samsung Galaxy S8", "year": 2017},
    {"brand": "Samsung", "name": "Samsung Galaxy S9", "year": 2018},
    {"brand": "Samsung", "name": "Samsung Galaxy S10", "year": 2019},
    {"brand": "Samsung", "name": "Samsung Galaxy S20", "year": 2020},
    {"brand": "Samsung", "name": "Samsung Galaxy S21", "year": 2021},
    {"brand": "Samsung", "name": "Samsung Galaxy S22", "year": 2022},
    {"brand": "Samsung", "name": "Samsung Galaxy S23", "year": 2023},
    {"brand": "Samsung", "name": "Samsung Galaxy S24", "year": 2024},
    {"brand": "Samsung", "name": "Samsung Galaxy Note", "year": 2011},
    {"brand": "Samsung", "name": "Samsung Galaxy Note 10", "year": 2019},
    {"brand": "Samsung", "name": "Samsung Galaxy Note 20", "year": 2020},
    {"brand": "Google", "name": "Google Pixel", "year": 2016},
    {"brand": "Google", "name": "Google Pixel 2", "year": 2017},
    {"brand": "Google", "name": "Google Pixel 3", "year": 2018},
    {"brand": "Google", "name": "Google Pixel 4", "year": 2019},
    {"brand": "Google", "name": "Google Pixel 5", "year": 2020},
    {"brand": "Google", "name": "Google Pixel 6", "year": 2021},
    {"brand": "Google", "name": "Google Pixel 7", "year": 2022},
    {"brand": "Google", "name": "Google Pixel 8", "year": 2023},
    {"brand": "Google", "name": "Google Pixel 9", "year": 2024},
    {"brand": "Motorola", "name": "Motorola Razr V3", "year": 2004},
    {"brand": "Motorola", "name": "Motorola Moto G", "year": 2013},
    {"brand": "HTC", "name": "HTC One M7", "year": 2013},
    {"brand": "HTC", "name": "HTC One M8", "year": 2014},
    {"brand": "OnePlus", "name": "OnePlus One", "year": 2014},
    {"brand": "OnePlus", "name": "OnePlus 3", "year": 2016},
    {"brand": "OnePlus", "name": "OnePlus 5", "year": 2017},
    {"brand": "OnePlus", "name": "OnePlus 6", "year": 2018},
    {"brand": "OnePlus", "name": "OnePlus 7 Pro", "year": 2019},
    {"brand": "OnePlus", "name": "OnePlus 8", "year": 2020},
    {"brand": "OnePlus", "name": "OnePlus 9", "year": 2021},
    {"brand": "Huawei", "name": "Huawei P30 Pro", "year": 2019},
    {"brand": "Huawei", "name": "Huawei Mate 20 Pro", "year": 2018},
    {"brand": "Xiaomi", "name": "Xiaomi Mi 3", "year": 2013},
    {"brand": "Xiaomi", "name": "Xiaomi Mi 5", "year": 2016},
    {"brand": "Xiaomi", "name": "Xiaomi Redmi Note 7", "year": 2019},
    {"brand": "BlackBerry", "name": "BlackBerry Bold 9700", "year": 2009},
    {"brand": "BlackBerry", "name": "BlackBerry Curve 8520", "year": 2009},
    {"brand": "Sony", "name": "Sony Ericsson W810i", "year": 2006},
    {"brand": "Sony", "name": "Sony Xperia Z", "year": 2013},
    {"brand": "LG", "name": "LG G2", "year": 2013},
    {"brand": "LG", "name": "LG G3", "year": 2014},
    {"brand": "LG", "name": "LG Nexus 5", "year": 2013},
]


def fetch_page(path):
    """Fetch a Wikipedia page. Returns BeautifulSoup or None."""
    url = WIKI_BASE + path
    try:
        resp = SESSION.get(url, timeout=15)
        resp.raise_for_status()
        time.sleep(1)
        return BeautifulSoup(resp.text, "html.parser")
    except requests.RequestException as e:
        print(f"  Warning: failed to fetch {url}: {e}", file=sys.stderr)
        return None


def extract_year(text):
    """Extract a 4-digit year (2000-2026) from text. Returns int or None."""
    match = re.search(r'\b(20[0-2]\d)\b', text)
    if match:
        year = int(match.group(1))
        if 2000 <= year <= 2026:
            return year
    return None


def get_thumbnail_from_article(article_path):
    """Fetch a phone's Wikipedia article and extract the infobox thumbnail URL."""
    soup = fetch_page(article_path)
    if not soup:
        return None

    infobox = soup.find("table", class_="infobox")
    if infobox:
        img = infobox.find("img")
        if img and img.get("src"):
            src = img["src"]
            if src.startswith("//"):
                src = "https:" + src
            src = re.sub(r'/(\d+)px-', '/200px-', src)
            return src

    content = soup.find("div", class_="mw-parser-output")
    if content:
        img = content.find("img", width=True)
        if img and img.get("src") and int(img.get("width", 0)) > 50:
            src = img["src"]
            if src.startswith("//"):
                src = "https:" + src
            src = re.sub(r'/(\d+)px-', '/200px-', src)
            return src

    return None


def scrape_brand_phones(brand, page_path):
    """Scrape phone models for a single brand. Returns list of dicts."""
    print(f"Scraping {brand}...")
    soup = fetch_page(page_path)
    if not soup:
        return []

    phones = []
    seen_names = set()

    for table in soup.find_all("table", class_="wikitable"):
        for row in table.find_all("tr")[1:]:
            cells = row.find_all(["td", "th"])
            if len(cells) < 2:
                continue

            name_cell = cells[0]
            link = name_cell.find("a")
            raw_name = link.get_text(strip=True) if link else name_cell.get_text(strip=True)

            if not raw_name or len(raw_name) < 2:
                continue

            if re.search(r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\b', raw_name):
                continue
            if re.search(r'^\[?\d+\]?$', raw_name.strip()):
                continue
            if re.search(r'\b(Release|Series|series|Tab |Tablet|Discontinued|Overview|Features|Specifications)\b', raw_name, re.IGNORECASE):
                continue

            row_text = row.get_text(" ", strip=True)
            year = extract_year(row_text)

            if not year:
                continue

            name = raw_name
            if not name.lower().startswith(brand.lower()):
                name = f"{brand} {name}"

            if name.lower() in seen_names:
                continue
            seen_names.add(name.lower())

            article_path = None
            if link and link.get("href", "").startswith("/wiki/"):
                article_path = link["href"]

            image = None
            if article_path:
                image = get_thumbnail_from_article(article_path)

            phones.append({
                "brand": brand,
                "name": name,
                "year": year,
                "image": image,
            })

    if not phones:
        content = soup.find("div", class_="mw-parser-output")
        if content:
            for li in content.find_all("li"):
                link = li.find("a")
                if not link or not link.get("href", "").startswith("/wiki/"):
                    continue
                raw_name = link.get_text(strip=True)
                if not raw_name or len(raw_name) < 3:
                    continue

                if re.search(r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\b', raw_name):
                    continue
                if re.search(r'^\[?\d+\]?$', raw_name.strip()):
                    continue
                if re.search(r'\b(Release|Series|series|Tab |Tablet|Discontinued|Overview|Features|Specifications)\b', raw_name, re.IGNORECASE):
                    continue

                li_text = li.get_text(" ", strip=True)
                year = extract_year(li_text)
                if not year:
                    continue

                name = raw_name
                if not name.lower().startswith(brand.lower()):
                    name = f"{brand} {name}"

                if name.lower() in seen_names:
                    continue
                seen_names.add(name.lower())

                image = get_thumbnail_from_article(link["href"])

                phones.append({
                    "brand": brand,
                    "name": name,
                    "year": year,
                    "image": image,
                })

    print(f"  Found {len(phones)} models for {brand}")
    return phones


def merge_fallbacks(scraped):
    """Merge fallback phones into scraped data. Scraped data wins on duplicates."""
    scraped_names = {p["name"].lower() for p in scraped}
    merged = list(scraped)
    added = 0
    for fb in FALLBACK_PHONES:
        if fb["name"].lower() not in scraped_names:
            merged.append({**fb, "image": None})
            added += 1
    if added:
        print(f"Added {added} fallback phones not found by scraper")
    return merged


def main():
    all_phones = []

    for brand, page_path in BRAND_PAGES.items():
        phones = scrape_brand_phones(brand, page_path)
        all_phones.extend(phones)

    all_phones = merge_fallbacks(all_phones)

    all_phones.sort(key=lambda p: (p["brand"].lower(), p["year"], p["name"].lower()))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_phones, f, indent=2, ensure_ascii=False)

    print(f"\nDone! Wrote {len(all_phones)} phones to {OUTPUT_FILE}")

    with_images = sum(1 for p in all_phones if p["image"])
    print(f"  {with_images} with images, {len(all_phones) - with_images} without")
    brands = set(p["brand"] for p in all_phones)
    print(f"  Brands: {', '.join(sorted(brands))}")


if __name__ == "__main__":
    main()
