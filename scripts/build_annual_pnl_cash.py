
import json
import pandas as pd
from pathlib import Path

def build_cash(assumptions: dict, repo_root: Path) -> pd.DataFrame:
    monthly_path = repo_root / "data" / "monthly_model_2025_2030.csv"
    if not monthly_path.exists():
        raise SystemExit(f"Missing monthly model CSV: {monthly_path}")
    df = pd.read_csv(monthly_path)
    for c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="ignore")

    sell_lag = int(assumptions.get("sell_lag_months", 12))
    dt_period = pd.to_datetime(df["period"], errors="coerce")
    cash_dt = dt_period + pd.DateOffset(months=sell_lag)
    cash_year = cash_dt.dt.year

    df["revenue_accrual_total"] = df["btc_revenue_accrual"] + df["etc_revenue_accrual"]
    cash_sales_by_year = df.groupby(cash_year)["revenue_accrual_total"].sum()

    df["power_cost_total"] = df["btc_power_cost"] + df["etc_power_cost"]
    power_by_year = df.groupby(dt_period.dt.year)["power_cost_total"].sum()

    years = sorted(set(cash_sales_by_year.index.tolist()) | set(power_by_year.index.tolist()))
    out = pd.DataFrame({"year": years})
    out["total_sales"] = out["year"].map(cash_sales_by_year).fillna(0.0)
    out["total_power_cost"] = out["year"].map(power_by_year).fillna(0.0)
    out["operating_profit"] = out["total_sales"] - out["total_power_cost"]
    return out

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
