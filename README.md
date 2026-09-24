# construction-data

General construction reference data in plain CSV: cost codes, classification, units, waste factors,
scope pay units, a trade sequence, a glossary and cost-control metric formulas. Plus a small,
documented pipeline for pulling **public-domain** construction price series from the US Bureau of Labor
Statistics.

Nothing here is copied from a commercial estimating database, and nothing here is anybody's project data.
Most of it is authored reference material you can use as a starting point and then replace with your own
numbers — which is the point, because your own history beats any published table.

## What is in the repository

| Dataset | Rows | What it is |
| --- | --- | --- |
| [`data/cost-codes/starter-cost-code-taxonomy.csv`](data/cost-codes/starter-cost-code-taxonomy.csv) | 142 | A starter cost code list mapped to CSI divisions, with cost type and unit of measure |
| [`data/classification/csi-divisions.csv`](data/classification/csi-divisions.csv) | 34 | The CSI division numbers and titles used as the mapping key, in three groups |
| [`data/measures/unit-conversions.csv`](data/measures/unit-conversions.csv) | 47 | Conversions that matter on site, including material-specific factors that are not simple arithmetic |
| [`data/measures/waste-factors.csv`](data/measures/waste-factors.csv) | 24 | Planning ranges for waste by material, with the drivers behind each range |
| [`data/measures/earthwork-volume-factors.csv`](data/measures/earthwork-volume-factors.csv) | 7 | Bank, loose and compacted volume factors by soil type |
| [`data/scope/pay-units.csv`](data/scope/pay-units.csv) | 46 | Typical pay unit and measurement basis per scope item, with what is usually excluded |
| [`data/schedule/typical-trade-sequence.csv`](data/schedule/typical-trade-sequence.csv) | 30 | A typical commercial sequence: predecessor, duration driver and the constraint that usually bites |
| [`data/glossary/glossary.csv`](data/glossary/glossary.csv) | 87 | Terms across contracts, cost control, field, safety and finance |
| [`data/metrics/metric-formulas.csv`](data/metrics/metric-formulas.csv) | 24 | Cost and schedule metrics with formulas, inputs and the caveat that stops you misreading them |
| [`samples/bls-ppi-construction-materials.csv`](samples/bls-ppi-construction-materials.csv) | 220 | A live sample pull from the BLS public API — see [`samples/README.md`](samples/README.md) |

## Design rules

- **CSV only.** No proprietary formats, no database, no build step. Open it in Excel, load it in pandas,
  diff it in a pull request.
- **Every dataset says where it came from.** Authored data is licensed CC BY 4.0. Fetched public data keeps
  its source URL, licence and fetch date in every row. See [`SOURCES.md`](SOURCES.md).
- **No invented precision.** Where a value genuinely varies — waste, swell, asphalt yield — the dataset
  carries a range and the reason for the range, not a single confident number.
- **No vendor pricing.** Unit costs, production rates and material prices are deliberately absent: the
  reputable ones are licensed commercial products and the rest are guesses. The BLS pipeline is the way to
  get a real, citable price index instead.
- **No proprietary code lists.** Mapping is to CSI **division titles** only. The full MasterFormat section
  numbering is licensed from CSI, so the cost code taxonomy here uses its own independent numbering.

## Using it

```bash
# anywhere: plain CSV, so anything that reads a file works
python3 -c "import csv;print(sum(1 for _ in csv.DictReader(open('data/glossary/glossary.csv'))))"
```

Common starting points:

- **Setting up a new company cost code list** — start from `starter-cost-code-taxonomy.csv`, delete what you
  do not do, then map to your accounting system's own codes. Do not rename codes once jobs are posted to them.
- **Checking a unit conversion** — `unit-conversions.csv` covers the awkward ones (concrete by the cubic yard
  to tons, rebar by bar size, asphalt by square yard per inch).
- **Sizing waste on a budget** — `waste-factors.csv` gives a planning range and the drivers; replace it with
  your own history as soon as you have three comparable jobs.
- **Building a schedule template** — `typical-trade-sequence.csv` gives the logic skeleton and, more usefully,
  the typical constraint that delays each step.

## Validating the data

```bash
python3 scripts/validate.py
```

The validator checks that every CSV parses, that column counts and required cells are consistent, that key
columns are unique, that percentage ranges run low to high, that the glossary is alphabetised, and that every
dataset is listed in the README and in `SOURCES.md`. It runs in CI on every push.

## Refreshing the BLS sample

```bash
python3 scripts/fetch_bls_ppi.py --series WPU1017,WPU0811 --start 2023 --end 2026 \
    --out samples/bls-ppi-construction-materials.csv
```

The script uses the official BLS public API. It does not scrape `download.bls.gov`, which denies automated
retrieval. The public API does not return series titles, so the sample carries series IDs only — confirm any
title at `https://data.bls.gov/timeseries/<SERIES_ID>` before you publish it.

## Contributing

Corrections with a source beat opinions. If you are changing a number, say where it came from and what it
applies to. If you are adding a dataset, add it to the README table and to `SOURCES.md` or the validator
will fail the build.

## Licence

Authored reference data and documentation: CC BY 4.0. Fetched public data: as per its source, recorded per
row. See [`LICENSE`](LICENSE) and [`SOURCES.md`](SOURCES.md).

## Disclaimer

This is general reference material, not advice for a specific project. Ranges are planning values, not
standards. Contract, safety and compliance decisions belong with your contracts, your competent persons,
your lawyer and your broker.
