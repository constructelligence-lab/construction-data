# Sources and provenance

Every dataset in this repository is either **authored** here or **fetched** from a named public source.
Nothing is scraped from a site that denies automated access, and nothing is copied from a licensed commercial
product.

| Dataset | Origin | Licence | How to verify |
| --- | --- | --- | --- |
| `data/cost-codes/starter-cost-code-taxonomy.csv` | Authored | CC BY 4.0 | Compare against your own chart of accounts and division mapping |
| `data/classification/csi-divisions.csv` | CSI division numbers and titles (public division-level list) | CSI retains rights in MasterFormat; titles reproduced here for mapping | Check current division titles with CSI |
| `data/measures/unit-conversions.csv` | Authored, with standard physical constants and ASTM nominal bar weights | CC BY 4.0 | ASTM A615 tables for bar weights; any engineering handbook for the constants |
| `data/measures/waste-factors.csv` | Authored planning ranges | CC BY 4.0 | Replace with your own installed-versus-purchased history |
| `data/measures/earthwork-volume-factors.csv` | Authored planning ranges | CC BY 4.0 | Compare with your own truck counts and compaction test records |
| `data/scope/pay-units.csv` | Authored | CC BY 4.0 | Compare against your own subcontracts and schedule of values |
| `data/schedule/typical-trade-sequence.csv` | Authored | CC BY 4.0 | Compare against a real baseline schedule from a completed job |
| `data/glossary/glossary.csv` | Authored | CC BY 4.0 | Contract and regulatory definitions take precedence over these |
| `data/metrics/metric-formulas.csv` | Authored, standard formulas | CC BY 4.0 | Any cost-control reference; confirm your contract's own definitions |
| `samples/bls-ppi-construction-materials.csv` | US Bureau of Labor Statistics public API | US federal government work — public domain | Re-run `scripts/fetch_bls_ppi.py`; the `fetched_on` column shows the retrieval date |

## Notes on the fetched data

**BLS Producer Price Index.** Retrieved from the official public API at `https://api.bls.gov/publicAPI/v1/timeseries/data/`
using [`scripts/fetch_bls_ppi.py`](scripts/fetch_bls_ppi.py). The Bureau of Labor Statistics denies automated
retrieval of its `download.bls.gov` flat files ("Access Denied — bot activity"), so this repository uses the
sanctioned API instead and does not scrape.

The public API returns values **without series titles**. Rather than guess what a series ID means, the sample
carries the ID only: confirm any title at `https://data.bls.gov/timeseries/<SERIES_ID>` before publishing or
relying on it. Without a BLS registration key the API limits requests to 25 series and 10 years each, and
applies a daily quota per IP address.

## What is deliberately not here

- **Unit costs, production rates and material prices.** The credible ones (RSMeans-style databases, vendor
  price books) are licensed commercial products. Everything else is a guess, and a guess with a decimal point
  is worse than no number.
- **Full MasterFormat section numbering.** Licensed from CSI. This repository maps to division titles only and
  uses its own cost code numbering.
- **Any project, client or company data.** No job names, no actuals, no timecards, no drawings, no imagery.
- **Labour rates and wage determinations.** These are jurisdiction- and trade-specific; use the official
  published determinations for the project's location.
