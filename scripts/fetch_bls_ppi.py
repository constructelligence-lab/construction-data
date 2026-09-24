#!/usr/bin/env python3
"""Fetch construction material price series from the official BLS public API.

Why the API: BLS denies automated retrieval of the download.bls.gov flat files
("Access Denied ... bot activity") while api.bls.gov/publicAPI is the sanctioned
programmatic route. The public API returns values but **not** series titles, so this
script never invents a label: you supply series IDs, and you confirm their titles at
https://data.bls.gov/timeseries/<SERIES_ID> before publishing them.

Usage:
  python3 scripts/fetch_bls_ppi.py --series WPU1017,WPU0811 --start 2023 --end 2025 \
      --out samples/bls-ppi-sample.csv

Limits of the public API without a registration key: 25 series per request, 10 years
per request, and a daily request quota per IP address.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

ENDPOINT = "https://api.bls.gov/publicAPI/v1/timeseries/data/"
SOURCE_URL = "https://www.bls.gov/ppi/"
LICENCE = "US federal government work - public domain"
USER_AGENT = "construction-data (github.com/constructelligence-lab/construction-data)"


def fetch(series_ids: list[str], start: int, end: int) -> dict:
    payload = json.dumps(
        {"seriesid": series_ids, "startyear": str(start), "endyear": str(end)}
    ).encode()
    request = urllib.request.Request(
        ENDPOINT,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": USER_AGENT},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            body = json.loads(response.read().decode())
    except urllib.error.URLError as exc:  # network, DNS, TLS
        sys.exit(f"FAIL: could not reach the BLS API: {exc}")

    if body.get("status") != "REQUEST_SUCCEEDED":
        sys.exit(f"FAIL: BLS API returned status {body.get('status')!r}: {body.get('message')}")
    for message in body.get("message", []):
        print(f"note from the API: {message}", file=sys.stderr)
    return body


def write_csv(body: dict, path: Path) -> int:
    fetched_on = date.today().isoformat()
    rows: list[dict[str, str]] = []
    for series in body["Results"]["series"]:
        for point in series.get("data", []):
            period = point.get("period", "")
            rows.append(
                {
                    "series_id": series["seriesID"],
                    "year": point.get("year", ""),
                    "period": period,
                    "period_name": point.get("periodName", ""),
                    # M01-M12 are months, M13 is an annual average, Q01-Q04 are quarters
                    "value": point.get("value", ""),
                    "source_url": SOURCE_URL,
                    "licence": LICENCE,
                    "fetched_on": fetched_on,
                }
            )
    if not rows:
        sys.exit("FAIL: the API returned no data points")

    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--series", required=True, help="comma separated BLS series IDs")
    parser.add_argument("--start", type=int, required=True, help="first year, inclusive")
    parser.add_argument("--end", type=int, required=True, help="last year, inclusive")
    parser.add_argument("--out", required=True, type=Path, help="CSV file to write")
    args = parser.parse_args(argv)

    series_ids = [s.strip() for s in args.series.split(",") if s.strip()]
    if len(series_ids) > 25:
        sys.exit("FAIL: the public API accepts at most 25 series per request")
    if args.end - args.start > 10:
        sys.exit("FAIL: the public API accepts at most 10 years per request")

    body = fetch(series_ids, args.start, args.end)
    written = write_csv(body, args.out)
    print(f"wrote {written} observations for {len(body['Results']['series'])} series to {args.out}")
    print("series titles are not returned by the public API - confirm each ID at https://data.bls.gov/timeseries/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
