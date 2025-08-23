#!/usr/bin/env python3
import argparse, re, sys, shutil
from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

def parse_set_clause(s: str):
    # parse "col1=val1, col2=val2" allowing commas inside values if quoted
    # simple split by commas not inside quotes
    parts = re.findall(r'(?:[^,"]+|"[^"]*")+', s)
    updates = {}
    for p in parts:
        if '=' not in p:
            continue
        k, v = p.split('=', 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        updates[k] = v
    return updates

def coerce_value(series, val):
    # try to coerce to numeric if target column is numeric
    try:
        if pd.api.types.is_numeric_dtype(series.dtype):
            if val == "" or val.lower() == "nan":
                return pd.NA
            return pd.to_numeric(val)
    except Exception:
        pass
    return val

def main():
    ap = argparse.ArgumentParser(description="Update BTC/ETC miner CSVs (shifts latest->v1, writes new latest).")
    ap.add_argument("--sheet", choices=["btc", "etc"], required=True, help="Which sheet to update")
    ap.add_argument("--model", required=True, help="Row key value to match (default key column is 'model')")
    ap.add_argument("--key", default="model", help="Key column name (default: model)")
    ap.add_argument("--set", required=True, help='Comma-separated updates, e.g. \'power (W)=3510, hashrate (TH/s)=245\'')
    args = ap.parse_args()

    csv_name = f"{args.sheet}_miner_sheet.csv"
    path_latest = DATA_DIR / csv_name
    path_prev   = DATA_DIR / f"{args.sheet}_miner_sheet_v1.csv"

    if not path_latest.exists():
        print(f"ERROR: {path_latest} not found.", file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(path_latest)

    if args.key not in df.columns:
        print(f"ERROR: key column '{args.key}' not in columns: {list(df.columns)}", file=sys.stderr)
        sys.exit(2)

    updates = parse_set_clause(args.set)
    if not updates:
        print("ERROR: nothing to update (empty --set).", file=sys.stderr)
        sys.exit(3)

    for col in updates.keys():
        if col not in df.columns:
            print(f"ERROR: target column '{col}' not in columns: {list(df.columns)}", file=sys.stderr)
            sys.exit(4)

    mask = df[args.key].astype(str) == str(args.model)
    n_match = int(mask.sum())
    if n_match == 0:
        print(f"ERROR: no rows matched {args.key} == '{args.model}'", file=sys.stderr)
        sys.exit(5)

    # Apply updates
    for col, val in updates.items():
        df.loc[mask, col] = df.loc[mask, col].apply(lambda _: coerce_value(df[col], val))

    # Save new latest
    df.to_csv(path_latest, index=False)

    print(f"OK: updated {n_match} row(s) in {csv_name}")
    print("Applied:")
    for k, v in updates.items():
        print(f"  - {k} = {v}")
    print(f"Backup written: {path_prev}")

if __name__ == "__main__":
    main()
