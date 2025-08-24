import json
import pandas as pd
import numpy as np
from pathlib import Path

MONEY_BASE = [
    "btc_revenue_accrual", "etc_revenue_accrual",
    "btc_power_cost", "etc_power_cost",
]

def _round_money_and_totals(df: pd.DataFrame) -> pd.DataFrame:
    # Round base money first to avoid absurd % from penny-level denominators
    for c in MONEY_BASE:
        if c in df.columns:
            df[c] = df[c].round(2)

    # Totals & profits (rounded)
    df["total_revenue"] = (df.get("btc_revenue_accrual", 0.0) +
                           df.get("etc_revenue_accrual", 0.0)).round(2)
    df["total_power_cost"] = (df.get("btc_power_cost", 0.0) +
                              df.get("etc_power_cost", 0.0)).round(2)

    df["btc_operating_profit"] = (df.get("btc_revenue_accrual", 0.0) -
                                  df.get("btc_power_cost", 0.0)).round(2)
    df["etc_operating_profit"] = (df.get("etc_revenue_accrual", 0.0) -
                                  df.get("etc_power_cost", 0.0)).round(2)
    df["operating_profit_total"] = (df["total_revenue"] -
                                    df["total_power_cost"]).round(2)
    return df

def _safe_margin(numer: pd.Series, denom: pd.Series) -> pd.Series:
    # If revenue < $1, treat margin as 0% to avoid crazy % from near-zero
    numer = numer.astype(float)
    denom = denom.astype(float)
    return pd.Series(
        np.where(denom >= 1.0, 100.0 * numer / denom, 0.0),
        index=numer.index
    ).round(2)

def build_accrual(assumptions: dict, repo_root: Path) -> pd.DataFrame:
    monthly_path = repo_root / "data" / "monthly_model_2025_2030.csv"
    if not monthly_path.exists():
        raise SystemExit(f"Missing monthly model CSV: {monthly_path}")

    df = pd.read_csv(monthly_path)

    # Required columns
    req = ["year", "btc_revenue_accrual", "etc_revenue_accrual",
           "btc_power_cost", "etc_power_cost"]
    for c in req:
        if c not in df.columns:
            raise SystemExit(f"Monthly model missing column: {c}")

    g = df.groupby("year", as_index=False).agg({
        "btc_revenue_accrual": "sum",
        "etc_revenue_accrual": "sum",
        "btc_power_cost": "sum",
        "etc_power_cost": "sum",
    })

    g = _round_money_and_totals(g)

    # Margins (%)
    g["btc_margin_pct"] = _safe_margin(g["btc_operating_profit"], g["btc_revenue_accrual"])
    g["etc_margin_pct"] = _safe_margin(g["etc_operating_profit"], g["etc_revenue_accrual"])
    g["margin_pct_total"] = _safe_margin(g["operating_profit_total"], g["total_revenue"])

    cols = [
        "year",
        "btc_revenue_accrual", "etc_revenue_accrual", "total_revenue",
        "btc_power_cost", "etc_power_cost", "total_power_cost",
        "btc_operating_profit", "etc_operating_profit", "operating_profit_total",
        "btc_margin_pct", "etc_margin_pct", "margin_pct_total",
    ]
    return g[cols]

if __name__ == "__main__":
    repo_root = Path(".")
    conf_path = repo_root / "config" / "assumptions.json"
    if not conf_path.exists():
        raise SystemExit(f"Missing assumptions file: {conf_path}")
    assumptions = json.loads(conf_path.read_text())
    out = build_accrual(assumptions, repo_root)
    out_path = repo_root / "data" / "annual_pnl_accrual.csv"
    out.to_csv(out_path, index=False)
    print(f"Wrote {out_path}")