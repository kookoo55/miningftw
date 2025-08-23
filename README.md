# miningftw

Forecasting & analysis for a winter-only BTC/ETC mining setup.  
This repo stores canonical miner sheets, a monthly model generator, and CI that snapshots data for easy verification.

---

## Repo layout

```
data/
  btc_miner_sheet.csv
  etc_miner_sheet.csv
  packages/
    data_csvs.zip
    manifest.json        # machine-readable snapshot of all CSVs
reports/
  DATA_SNAPSHOT.md       # human-readable preview (headers, row counts, samples)
config/
  assumptions.json       # model knobs (prices, difficulty, power; growth %; dates)
scripts/
  build_monthly_model.py # produces monthly model CSV
.github/
  workflows/
    (data snapshot workflows live here)
```

---

## CSV schemas (canonical)

**BTC — `data/btc_miner_sheet.csv`**  
Headers (from `manifest.json`):  
`model, hashrate(TH/s), power(W), hashrate(TH/s)/power(W), price, price/hashrate(TH/s), x4 cost, x6 cost, x4 hashrate , x6 hashrate, Unnamed: 10, link`

**ETC — `data/etc_miner_sheet.csv`**  
Headers:  
`model, hashrate (GH/s), power (W), hashrate (GH/s)/power (W), price, price/hashrate(GH/s), x4 cost, x6 cost, x4 hashrate (GH/s), x6 hashrate (GH/s), Unnamed: 10, link`

> Unit convention: BTC hashrate in **TH/s**, ETC hashrate in **GH/s**. Power in **W**.

---

## Assumptions file (`config/assumptions.json`)

Key fields (defaults shown):

```json
{
  "use_default": true,
  "start_month": "2025-10",
  "end_month": "2030-12",
  "winter_months": [10,11,12,1,2,3,4],
  "sell_lag_months": 12,
  "pool_fee_pct": 1.0,
  "elec_rate_usd_per_kwh": 0.081,
  "annual_power_pct": 0.0,
  "btc": {
    "base_price_usd": 125000.0,
    "annual_price_pct": 0.0,
    "annual_difficulty_pct": 0.0,
    "baseline_coins_per_day": 0.0005760,
    "units": 6,
    "power_w_each": 3510.0,
    "hash_unit": "TH/s",
    "source_csv": "data/btc_miner_sheet.csv"
  },
  "etc": {
    "base_price_usd": 24.0,
    "annual_price_pct": 0.0,
    "annual_difficulty_pct": 0.0,
    "baseline_coins_per_day": 1.16917,
    "units": 20,
    "power_w_each": 370.0,
    "hash_unit": "GH/s",
    "source_csv": "data/etc_miner_sheet.csv"
  }
}
```

- Set `"use_default": false` to let the script pull `units`/`power` heuristically from the CSVs.

---

## Generate the monthly model

Produces winter-only monthly rows from **Oct 2025 → Dec 2030** with separate BTC/ETC columns and cash-lagged sales.

```bash
# From repo root
python scripts/build_monthly_model.py
# Output:
# data/monthly_model_2025_2030_full.csv
```

Columns in the model:
`period, year, month, is_winter, btc_coins_mined, etc_coins_mined, btc_revenue_accrual, etc_revenue_accrual, btc_kwh, etc_kwh, btc_power_cost, etc_power_cost, btc_cash_sales, etc_cash_sales`

---

## Data snapshots (automation)

A GitHub Actions workflow bundles CSVs and publishes:
- `data/packages/manifest.json` (headers, row counts, samples, sha256)
- `reports/DATA_SNAPSHOT.md` (human preview)
- `data/packages/data_csvs.zip`

These files live on `main` so downstream tools (and humans) can verify data without downloading raw blobs.

---

## Common tasks

- **Update assumptions** → edit `config/assumptions.json`, then run the model.
- **Swap miner specs** → edit rows in `data/*_miner_sheet.csv` (BTC = TH/s, ETC = GH/s), set `"use_default": false` if you want the script to read from CSVs.
- **Refresh snapshot** → push any CSV change; the workflow will rebuild `manifest.json` + `DATA_SNAPSHOT.md`.

---

## Quick checks

- Latest snapshot: `reports/DATA_SNAPSHOT.md`  
- Machine-readable manifest: `data/packages/manifest.json`

---

## Notes

- Mining months are limited to **Oct–Apr** (winter).  
- Sales recognized on a **12-month lag** to target long-term capital gains.  
- Pool fee assumed **1%** already reflected in baseline coins/day.
