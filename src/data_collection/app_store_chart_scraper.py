import argparse
import csv
import re
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def chart_url(country: str, chart: str) -> str:
    base = f"https://apps.apple.com/{country}/charts/iphone"
    charts = {
        "top_free": "top-free-apps/36",
        "top_paid": "top-paid-apps/36",
        "top_grossing": "top-grossing-apps/36",
    }
    if chart not in charts:
        raise ValueError(f"Invalid chart: {chart}")
    return f"{base}/{charts[chart]}"


def fetch(url: str, session: requests.Session, timeout=15) -> str:
    resp = session.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def parse_chart(html: str, base="https://apps.apple.com") -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    apps, seen = [], set()
    # Fallback parsing: any link with /app/.../id[digits]
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/app/" in href and re.search(r"/id(\d+)", href):
            app_id_match = re.search(r"/id(\d+)", href)
            app_id = app_id_match.group(1) if app_id_match else None
            if not app_id or app_id in seen:
                continue
            seen.add(app_id)
            name = a.get_text(strip=True) or None
            url = href if href.startswith("http") else urljoin(base, href)
            apps.append({"app_id": app_id, "name": name, "url": url})
    # Assign rank by order found
    for i, app in enumerate(apps, start=1):
        app["rank"] = i
    return apps


def itunes_lookup(app_id: str, country: str, session: requests.Session) -> dict:
    url = "https://itunes.apple.com/lookup"
    params = {"id": app_id, "country": country}
    r = session.get(url, params=params, timeout=15)
    if r.status_code != 200:
        return {}
    data = r.json()
    if data.get("resultCount", 0) == 0:
        return {}
    return data["results"][0]


def scrape_chart(country: str, chart: str, limit: int, delay: float) -> list[dict]:
    session = requests.Session()
    session.headers.update(HEADERS)
    html = fetch(chart_url(country, chart), session)
    basic = parse_chart(html)
    if limit:
        basic = basic[:limit]

    rows = []
    for app in basic:
        meta = itunes_lookup(app["app_id"], country, session)
        row = {
            "rank": app["rank"],
            "app_id": app["app_id"],
            "name": meta.get("trackName") or app.get("name"),
            "url": app["url"],
            "country": country,
            "chart_type": chart,
            "userRatingCount": meta.get("userRatingCount"),
            "averageUserRating": meta.get("averageUserRating"),
            "primaryGenreName": meta.get("primaryGenreName"),
            "price": meta.get("price"),
            "formattedPrice": meta.get("formattedPrice"),
            "sellerName": meta.get("sellerName"),
            "bundleId": meta.get("bundleId"),
            "version": meta.get("version"),
            # Use timezone-aware UTC timestamp
            "scraped_at": datetime.now().isoformat(),
        }
        rows.append(row)
        time.sleep(delay)
    return rows


def write_csv(rows: list[dict], out_path: str):
    if not rows:
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            pass
        return
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def _chart_label(chart: str) -> str:
    # Map to desired label spelling in filenames
    if chart == "top_paid":
        return "top paid"
    if chart == "top_grossing":
        return "top grossing"
    return chart  # keep "top_free" as is per request


def main():
    p = argparse.ArgumentParser(description="Scrape App Store charts with rating-count proxy")
    p.add_argument("--country", default="tr", help="ISO country code (e.g., us, tr, gb)")
    p.add_argument("--chart", default="top_free", choices=["top_free", "top_paid", "top_grossing"]) 
    p.add_argument("--limit", type=int, default=50, help="Max apps to enrich")
    p.add_argument("-o", "--out", default=None, help="Output CSV path (optional)")
    p.add_argument("--delay", type=float, default=0.8, help="Delay between lookups (seconds)")
    args = p.parse_args()

    rows = scrape_chart(args.country, args.chart, args.limit, args.delay)
    # Auto-generate filename if not provided
    if not args.out:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        label = _chart_label(args.chart)
        out_path = f"data/raw/scraped/{label}_{args.country}_{ts}.csv"
    else:
        out_path = args.out
    write_csv(rows, out_path)
    print(f"Wrote {len(rows)} rows to {out_path}")


if __name__ == "__main__":
    main()
