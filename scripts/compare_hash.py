#!/usr/bin/env python3
"""
Compare BTC vs ETC hashrates by normalizing units.
- BTC sheet uses TH/s; ETC uses GH/s.
Outputs:
  reports/hash_compare.csv  (normalized table)
  reports/hash_compare.md   (short human-readable summary)
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True, parents=True)

btc_path = DATA / "btc_miner_sheet.csv"
etc_path = DATA / "etc_miner_sheet.csv"

btc = pd.read_csv(btc_path)
etc = pd.read_csv(etc_path)

# Expect columns: 'model', 'hashrate (TH/s)' on BTC; 'model', 'hashrate (GH/s)' on ETC
def safe_num(x):
    try:
        return float(x)
    except Exception:
        return float('nan')

# Normalize
btc_norm = btc.copy()
if 'hashrate (TH/s)' in btc_norm.columns:
    btc_norm['hashrate_GHps'] = btc_norm['hashrate (TH/s)'].apply(safe_num) * 1000.0
    btc_norm['hashrate_THps'] = btc_norm['hashrate (TH/s)'].apply(safe_num)
else:
    btc_norm['hashrate_GHps'] = float('nan')
    btc_norm['hashrate_THps'] = float('nan')

etc_norm = etc.copy()
if 'hashrate (GH/s)' in etc_norm.columns:
    etc_norm['hashrate_GHps'] = etc_norm['hashrate (GH/s)'].apply(safe_num)
    etc_norm['hashrate_THps'] = etc_norm['hashrate (GH/s)'].apply(safe_num) / 1000.0
else:
    etc_norm['hashrate_GHps'] = float('nan')
    etc_norm['hashrate_THps'] = float('nan')

# Add chain column & select core fields
btc_sel = btc_norm.copy()
btc_sel['chain'] = 'BTC'
etc_sel = etc_norm.copy()
etc_sel['chain'] = 'ETC'

def pick_cols(df):
    cols = []
    for c in ['chain','model','hashrate (TH/s)','hashrate (GH/s)','hashrate_THps','hashrate_GHps','power (W)']:
        if c in df.columns:
            cols.append(c)
    return df[cols]

btc_out = pick_cols(btc_sel)
etc_out = pick_cols(etc_sel)

combined = pd.concat([btc_out, etc_out], ignore_index=True)

# Efficiency (if power available)
if 'power (W)' in combined.columns:
    combined['J_per_GH'] = combined.apply(
        lambda r: (float(r['power (W)']) / float(r['hashrate_GHps'])) if (pd.notna(r.get('power (W)')) and pd.notna(r.get('hashrate_GHps')) and r.get('hashrate_GHps') not in [0.0, 0]) else float('nan'),
        axis=1
    )
    combined['J_per_TH'] = combined.apply(
        lambda r: (float(r['power (W)']) / float(r['hashrate_THps'])) if (pd.notna(r.get('power (W)')) and pd.notna(r.get('hashrate_THps')) and r.get('hashrate_THps') not in [0.0, 0]) else float('nan'),
        axis=1
    )

# Write CSV
out_csv = REPORTS / "hash_compare.csv"
combined.to_csv(out_csv, index=False)

# Write simple MD
lines = ["# Hashrate Comparison (normalized)\n",
         f"- Source: {btc_path.name} (BTC) & {etc_path.name} (ETC)\n",
         "- BTC TH/s → GH/s ×1000; ETC GH/s → TH/s ÷1000.\n",
         f"- Rows: {len(combined)}\n"]
md = "\n".join(lines)
(out_md := REPORTS / "hash_compare.md").write_text(md)

print(f"Wrote: {out_csv}")
print(f"Wrote: {out_md}")
