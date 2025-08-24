
import json
import pandas as pd
from pathlib import Path

def build_accrual(assumptions: dict, repo_root: Path) -> pd.DataFrame:
    monthly_path = repo_root / "data" / "monthly_model_2025_2030.csv"
    if not monthly_path.exists():
        raise SystemExit(f"Missing monthly model CSV: {monthly_path}")
    df = pd.read_csv(monthly_path)
    for c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="ignore")
    out = df.groupby("year").agg({
        "btc_revenue_accrual":"sum",
        "etc_revenue_accrual":"sum",
        "btc_power_cost":"sum",
        "etc_power_cost":"sum"
    }).reset_index()
    out["total_revenue"] = out["btc_revenue_accrual"] + out["etc_revenue_accrual"]
    out["total_power_cost"] = out["btc_power_cost"] + out["etc_power_cost"]
    out["operating_profit"] = out["total_revenue"] - out["total_power_cost"]
    return out

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
