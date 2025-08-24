import json
import pandas as pd
import numpy as np
from pathlib import Path

MONEY_BASE = [
    "btc_cash_sales", "etc_cash_sales",
    "btc_power_cost", "etc_power_cost",
]

def _round_money_and_totals(df: pd.DataFrame) -> pd.DataFrame:
    for c in MONEY_BASE:
        if c in df.columns:
            df[c] = df[c].round(2)

    df["total_sales"] = (df.get("btc_cash_sales", 0.0) +
                         df.get("etc_cash_sales", 0.0)).round(2)
    df["total_power_cost"] = (df.get("btc_power_cost", 0.0) +
                              df.get("etc_power_cost", 0.0)).round(2)

    df["btc_operating_profit"] = (df.get("btc_cash_sales", 0.0) -
                                  df.get("btc_power_cost", 0.0)).round(2)
    df["etc_operating_profit"] = (df.get("etc_cash_sales", 0.0) -
                                  df.get("etc_power_cost", 0.0)).round(2)
    df["operating_profit_total"] = (df["total_sales"] -
                                    df["total_power_cost"]).round(2)
    return df

def _safe_margin(numer: pd.Series, denom: pd.Series) -> pd.Series:
    numer = numer.astype(float)
    denom = denom.astype(float)
    return pd.Series(
        np.where(denom >= 1.0, 100.0 * numer / denom, 0.0),
        index=numer.index
    ).round(2)

def build_cash(assumptions: dict, repo_root: Path) -> pd.DataFrame:
    monthly_path = repo_root / "data" / "monthly_model_2025_2030.csv"
    if not monthly_path.exists():
        raise SystemExit(f"Missing monthly model CSV: {monthly_path}")

    df = pd.read_csv(monthly_path)

    # Required columns
    req = ["year", "btc_cash_sales", "etc_cash_sales",
           "btc_power_cost", "etc_power_cost"]
    for c in req:
        if c not in df.columns:
            raise SystemExit(f"Monthly model missing column: {c}")

    # Sum cash sales and power costs by calendar year
    g_sales = df.groupby("year", as_index=False).agg({
        "btc_cash_sales": "sum",
        "etc_cash_sales": "sum",
    })
    g_power = df.groupby("year", as_index=False).agg({
        "btc_power_cost": "sum",
        "etc_power_cost": "sum",
    })

    out = pd.merge(g_sales, g_power, on="year", how="outer").fillna(0.0)

    out = _round_money_and_totals(out)

    # Margins (%)
    out["btc_margin_pct"] = _safe_margin(out["btc_operating_profit"], out["btc_cash_sales"])
    out["etc_margin_pct"] = _safe_margin(out["etc_operating_profit"], out["etc_cash_sales"])
    out["margin_pct_total"] = _safe_margin(out["operating_profit_total"], out["total_sales"])

    cols = [
        "year",
        "btc_cash_sales", "etc_cash_sales", "total_sales",
        "btc_power_cost", "etc_power_cost", "total_power_cost",
        "btc_operating_profit", "etc_operating_profit", "operating_profit_total",
        "btc_margin_pct", "etc_margin_pct", "margin_pct_total",
    ]
    return out[cols]

if __name__ == "__main__":
    repo_root = Path(".")
    conf_path = repo_root / "config" / "assumptions.json"
    if not conf_path.exists():
        raise SystemExit(f"Missing assumptions file: {conf_path}")
    assumptions = json.loads(conf_path.read_text())
    out = build_cash(assumptions, repo_root)
    out_path = repo_root / "data" / "annual_pnl_cash.csv"
    out.to_csv(out_path, index=False)
    print(f"Wrote {out_path}")