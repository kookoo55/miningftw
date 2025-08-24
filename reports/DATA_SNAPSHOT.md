# Data Snapshot

## `data/annual_pnl_accrual.csv`

- Rows: **6**
- SHA256: `4c0db800b9f1e3b39c6efbfe0e98bb80a63d3832df89cd191869bdfd07103cec`

**Headers**

`year, btc_revenue_accrual, etc_revenue_accrual, btc_power_cost, etc_power_cost, total_revenue, total_power_cost, operating_profit`

**First 5 rows**

| year | btc_revenue_accrual | etc_revenue_accrual | btc_power_cost | etc_power_cost | total_revenue | total_power_cost | operating_profit |
|---|---|---|---|---|---|---|---|
| 2025 | 9986.647772927616 | 1.3773443244485296e-05 | 3755.808 | 1323.4751999999999 | 9986.64778670106 | 5079.2832 | 4907.36458670106 |
| 2026 | 23012.710085441897 | 3.173880399816177e-05 | 8654.688 | 3049.7472 | 23012.7101171807 | 11704.4352 | 11308.2749171807 |
| 2027 | 23012.710085441897 | 3.173880399816177e-05 | 8654.688 | 3049.7472 | 23012.7101171807 | 11704.4352 | 11308.2749171807 |
| 2028 | 23121.26060471285 | 3.188851533777574e-05 | 8695.512 | 3064.1328 | 23121.260636601364 | 11759.6448 | 11361.615836601364 |
| 2029 | 23012.710085441897 | 3.173880399816177e-05 | 8654.688 | 3049.7472 | 23012.7101171807 | 11704.4352 | 11308.2749171807 |

## `data/annual_pnl_cash.csv`

- Rows: **7**
- SHA256: `8e1a97356cc3f05fa791dd122ce82c8e4d85f663db0ec64920fb3634556f4094`

**Headers**

`year, total_sales, total_power_cost, operating_profit`

**First 5 rows**

| year | total_sales | total_power_cost | operating_profit |
|---|---|---|---|
| 2025 | 0.0 | 5079.2832 | -5079.2832 |
| 2026 | 9986.647786701058 | 11704.4352 | -1717.7874132989418 |
| 2027 | 23012.7101171807 | 11704.4352 | 11308.2749171807 |
| 2028 | 23012.7101171807 | 11759.6448 | 11253.0653171807 |
| 2029 | 23121.260636601364 | 11704.4352 | 11416.825436601364 |

## `data/btc_miner_sheet.csv`

- Rows: **4**
- SHA256: `77e99f435dd5d5d3129dd12595b2b5220279281f82052f6ba6317f1b392980f4`

**Headers**

`model, hashrate(TH/s), power(W), hashrate(TH/s)/power(W), price, price/hashrate(TH/s), x4 cost, x6 cost, x4 hashrate , x6 hashrate, Unnamed: 10, link`

**First 5 rows**

| model | hashrate(TH/s) | power(W) | hashrate(TH/s)/power(W) | price | price/hashrate(TH/s) | x4 cost | x6 cost | x4 hashrate  | x6 hashrate | Unnamed: 10 | link |
|---|---|---|---|---|---|---|---|---|---|---|---|
| s21+ | 235 | 3564.0 | 0.0659 | 3349 | 14.25 | 13396 |  | 940.0 |  |  | https://asicmarketplace.com/product/bitmain-antminer-s21-plus-bitcoin-miner/ |
| s21 Pro | 245 | 3510.0 | 0.0698 | 4129 | 16.85 | 16516 |  | 980.0 |  |  | https://asicmarketplace.com/product/bitmain-antminer-s21-pro-btc-miner-234th/ |
| s21 | 200 | 3500.0 | 0.0571 | 2699 | 13.495 |  | 16194.0 |  | 1200.0 |  | https://asicmarketplace.com/product/bitmain-antminer-s21-bitcoin-asic-miner/ |
| m66 | 276 | 5492.4 | 0.05025 | 3615 | 13.10 |  | 21690.0 |  | 1656.0 |  |  |

## `data/etc_miner_sheet.csv`

- Rows: **2**
- SHA256: `d3548ef85c3d6070131cb955afdcd43109c9ff60c93dcef5f52f5c8cf2084afd`

**Headers**

`model, hashrate (GH/s), power (W), hashrate (GH/s)/power (W), price, price/hashrate(GH/s), x4 cost, x6 cost, x4 hashrate (GH/s), x6 hashrate (GH/s), Unnamed: 10, link`

**First 5 rows**

| model | hashrate (GH/s) | power (W) | hashrate (GH/s)/power (W) | price | price/hashrate(GH/s) | x4 cost | x6 cost | x4 hashrate (GH/s) | x6 hashrate (GH/s) | Unnamed: 10 | link |
|---|---|---|---|---|---|---|---|---|---|---|---|
| jasminer x16 p | 5.8 | 1900 | 0.00305 | 4269 | 736.03 |  |  |  |  |  | https://asicmarketplace.com/product/jasminer-x16-p-etc-miner-8gb/ |
| jasminer x4-q | 1.04 | 370 | 0.00281 | 829 | 797.11 |  |  |  |  |  | https://asicmarketplace.com/product/jasminer-x4-q-etc-miner-5gb-1040mh/ |

## `data/monthly_model_2025_2030.csv`

- Rows: **55**
- SHA256: `75c28eb114383f4cc16f6a3c3cabf2817406b0a098600066e56d3c2c2bc27592`

**Headers**

`period, year, month, is_winter, btc_model, etc_model, btc_units, etc_units, btc_unit_hash, etc_unit_hash, btc_unit_hash_unit, etc_unit_hash_unit, btc_unit_power_w, etc_unit_power_w, btc_coins_mined, etc_coins_mined, btc_revenue_accrual, etc_revenue_accrual, btc_kwh, etc_kwh, btc_power_cost, etc_power_cost, btc_cash_sales, etc_cash_sales`

**First 5 rows**

| period | year | month | is_winter | btc_model | etc_model | btc_units | etc_units | btc_unit_hash | etc_unit_hash | btc_unit_hash_unit | etc_unit_hash_unit | btc_unit_power_w | etc_unit_power_w | btc_coins_mined | etc_coins_mined | btc_revenue_accrual | etc_revenue_accrual | btc_kwh | etc_kwh | btc_power_cost | etc_power_cost | btc_cash_sales | etc_cash_sales |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2025-10-01 | 2025 | 10 | True | s21 | jasminer x4-q | 6 | 20 | 200.0 | 1.04 | TH/s | GH/s | 3500.0 | 370.0 | 0.027621 | 87.1563264 | 3452.625 | 2091.7518336 | 15624.0 | 5505.599999999999 | 1265.544 | 445.9536 | 0.0 | 0.0 |
| 2025-11-01 | 2025 | 11 | True | s21 | jasminer x4-q | 6 | 20 | 200.0 | 1.04 | TH/s | GH/s | 3500.0 | 370.0 | 0.02673 | 84.344832 | 3341.25 | 2024.275968 | 15120.0 | 5328.0 | 1224.72 | 431.56800000000004 | 0.0 | 0.0 |
| 2025-12-01 | 2025 | 12 | True | s21 | jasminer x4-q | 6 | 20 | 200.0 | 1.04 | TH/s | GH/s | 3500.0 | 370.0 | 0.027621 | 87.1563264 | 3452.625 | 2091.7518336 | 15624.0 | 5505.599999999999 | 1265.544 | 445.9536 | 0.0 | 0.0 |
| 2026-01-01 | 2026 | 1 | True | s21 | jasminer x4-q | 6 | 20 | 200.0 | 1.04 | TH/s | GH/s | 3500.0 | 370.0 | 0.027621 | 87.1563264 | 3452.625 | 2091.7518336 | 15624.0 | 5505.599999999999 | 1265.544 | 445.9536 | 0.0 | 0.0 |
| 2026-02-01 | 2026 | 2 | True | s21 | jasminer x4-q | 6 | 20 | 200.0 | 1.04 | TH/s | GH/s | 3500.0 | 370.0 | 0.024947999999999998 | 78.7218432 | 3118.4999999999995 | 1889.3242367999999 | 14112.0 | 4972.8 | 1143.0720000000001 | 402.7968 | 0.0 | 0.0 |
