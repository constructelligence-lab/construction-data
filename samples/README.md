# Samples

## `bls-ppi-construction-materials.csv`

A live pull from the US Bureau of Labor Statistics public API, kept in the repository so the pipeline can be
inspected without a network connection. 220 monthly observations across 5 series, covering 2023 through the
most recent published month at the time of the pull.

**How it was generated** (exact command):

```bash
python3 scripts/fetch_bls_ppi.py \
    --series WPU1017,WPU0811,WPU1321,WPU0721,WPU1311 \
    --start 2023 --end 2026 \
    --out samples/bls-ppi-construction-materials.csv
```

**Columns:** `series_id`, `year`, `period`, `period_name`, `value`, `source_url`, `licence`, `fetched_on`.

**What is verified:** the series IDs returned data from the official API on the `fetched_on` date, and the
values are as published.

**What is deliberately not claimed:** the *titles* of these series. The public API does not return series
catalog data without a registered key, so this repository does not invent labels. Confirm each ID at
`https://data.bls.gov/timeseries/<SERIES_ID>` before using or republishing it.

**Refreshing:** re-run the command above. The BLS API is the sanctioned programmatic route; its
`download.bls.gov` flat files deny automated retrieval, and this repository does not scrape them.
