# miningftw

Forecasting & analysis for a winter-only BTC/ETC mining setup. It does not support calculations for BTC & ETC mining together. 
This repo stores canonical miner sheets, a monthly model generator, and CI that snapshots data for easy verification.

## How it works
1) For each chain, the script **finds the row** where `model` equals the `model_name` in assumptions (case-insensitive).  
2) It **extracts per‑unit hashrate and power** from the CSV (TH/s for BTC, GH/s for ETC).  
3) It computes **coins/day**:
   - If `use_difficulty=true`: coins/day = (miner_share × blocks/day × block_reward) × (1−pool_fee)
   - Then applies **annual difficulty %** (harder → fewer coins) and winter-only schedule.
4) Prices can grow per year via `annual_price_pct`. Electricity rate can grow via `annual_power_pct`.  
5) Sales are recognized with a **12‑month lag** (`sell_lag_months`) to target LTCG.

## Repo layout
```
data/
  btc_miner_sheet.csv
  etc_miner_sheet.csv
  packages/
    data_csvs.zip
    manifest.json
reports/
  DATA_SNAPSHOT.md
config/
  assumptions.json
scripts/
  build_monthly_model.py
```

## Run
```bash
python3 scripts/build_monthly_model.py
# writes data/monthly_model_2025_2030_full.csv
```

## Assumptions (keys)
### Below are the default values used in the calculations.
```json
{
  "start_month": "2025-10",
  "end_month": "2030-12",
  "winter_months": [10,11,12,1,2,3,4],
  "sell_lag_months": 12,
  "elec_rate_usd_per_kwh": 0.081,
  "annual_power_pct": 0.0,
  "btc": {
    "model_name": "s21+",
    "base_price_usd": 125000.0,
    "annual_price_pct": 0.0,
    "use_difficulty": true,
    "difficulty_now": 8.6e13,
    "annual_difficulty_pct": 0.0,
    "block_time_s": 600.0,
    "block_reward": 3.125,
    "pool_fee_pct": 0.01,
    "units": 6,
    "source_csv": "data/btc_miner_sheet.csv"
  },
  "etc": {
    "model_name": "jasminer x4-q",
    "base_price_usd": 24.0,
    "annual_price_pct": 0.0,
    "use_difficulty": true,
    "difficulty_now": 1.7e14,
    "annual_difficulty_pct": 0.0,
    "block_time_s": 13.5,
    "block_reward": 2.56,
    "pool_fee_pct": 0.01,
    "units": 20,
    "source_csv": "data/etc_miner_sheet.csv"
  }
}
```