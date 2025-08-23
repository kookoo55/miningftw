
import json
import pandas as pd
from pathlib import Path

def _days_in_month(dt: pd.Timestamp) -> int:
    eom = dt + pd.offsets.MonthEnd(0)
    return (eom - dt).days + 1

def _safe_read_specs(csv_path: Path):
    if not csv_path.exists():
        return None, None
    try:
        df = pd.read_csv(csv_path)
        cols = {c.lower(): c for c in df.columns}
        units = None
        power_each = None
        for key in cols:
            if "unit" in key or "qty" in key or "count" in key:
                units = int(pd.to_numeric(df[cols[key]], errors="coerce").fillna(0).sum())
                break
        for key in cols:
            if "power" in key and ("w" in key or "watt" in key):
                s = pd.to_numeric(df[cols[key]], errors="coerce").dropna()
                if not s.empty:
                    power_each = float(s.iloc[0])
                    break
        return units, power_each
    except Exception:
        return None, None

def build_monthly_model(assumptions: dict, repo_root: Path) -> pd.DataFrame:
    start = pd.Timestamp(assumptions["start_month"] + "-01")
    end   = pd.Timestamp(assumptions["end_month"] + "-01") + pd.offsets.MonthEnd(0)
    months = pd.period_range(start=start, end=end, freq="M")

    winter = set(assumptions.get("winter_months", [10,11,12,1,2,3,4]))
    sell_lag = int(assumptions.get("sell_lag_months", 12))
    base_elec = float(assumptions.get("elec_rate_usd_per_kwh", 0.081))
    annual_power_pct = float(assumptions.get("annual_power_pct", 0.0))

    btc_conf = assumptions["btc"]
    etc_conf = assumptions["etc"]

    if not assumptions.get("use_default", True):
        b_units, b_power = _safe_read_specs(repo_root / btc_conf.get("source_csv", ""))
        e_units, e_power = _safe_read_specs(repo_root / etc_conf.get("source_csv", ""))
    else:
        b_units, b_power = None, None
        e_units, e_power = None, None

    btc_units = int(btc_conf["units"] if b_units is None else b_units)
    btc_power_each = float(btc_conf["power_w_each"] if b_power is None else b_power)
    etc_units = int(etc_conf["units"] if e_units is None else e_units)
    etc_power_each = float(etc_conf["power_w_each"] if e_power is None else e_power)

    btc_price0 = float(btc_conf["base_price_usd"])
    etc_price0 = float(etc_conf["base_price_usd"])
    btc_day0   = float(btc_conf["baseline_coins_per_day"])
    etc_day0   = float(etc_conf["baseline_coins_per_day"])
    btc_price_growth = float(btc_conf.get("annual_price_pct", 0.0))
    etc_price_growth = float(etc_conf.get("annual_price_pct", 0.0))
    btc_diff_growth  = float(btc_conf.get("annual_difficulty_pct", 0.0))
    etc_diff_growth  = float(etc_conf.get("annual_difficulty_pct", 0.0))

    rows = []
    for p in months:
        dt = p.to_timestamp()
        year_index = dt.year - start.year

        btc_price = btc_price0 * ((1.0 + btc_price_growth) ** year_index)
        etc_price = etc_price0 * ((1.0 + etc_price_growth) ** year_index)
        btc_day   = btc_day0   / ((1.0 + btc_diff_growth) ** year_index)
        etc_day   = etc_day0   / ((1.0 + etc_diff_growth) ** year_index)
        elec_rate = base_elec  * ((1.0 + annual_power_pct) ** year_index)

        d = _days_in_month(dt)
        is_winter = (dt.month in winter)

        btc_kwh_day = btc_units * btc_power_each * 24 / 1000.0
        etc_kwh_day = etc_units * etc_power_each * 24 / 1000.0

        btc_coins = (btc_day * d) if is_winter else 0.0
        etc_coins = (etc_day * d) if is_winter else 0.0
        btc_rev   = btc_coins * btc_price
        etc_rev   = etc_coins * etc_price

        btc_kwh = (btc_kwh_day * d) if is_winter else 0.0
        etc_kwh = (etc_kwh_day * d) if is_winter else 0.0
        btc_pow = btc_kwh * elec_rate
        etc_pow = etc_kwh * elec_rate

        rows.append({
            "period": dt.strftime("%Y-%m-01"),
            "year": dt.year,
            "month": dt.month,
            "is_winter": is_winter,
            "btc_coins_mined": btc_coins,
            "etc_coins_mined": etc_coins,
            "btc_revenue_accrual": btc_rev,
            "etc_revenue_accrual": etc_rev,
            "btc_kwh": btc_kwh,
            "etc_kwh": etc_kwh,
            "btc_power_cost": btc_pow,
            "etc_power_cost": etc_pow,
            "btc_cash_sales": 0.0,
            "etc_cash_sales": 0.0
        })

    df = pd.DataFrame(rows).sort_values("period").reset_index(drop=True)
    df["btc_cash_sales"] = df["btc_revenue_accrual"].shift(sell_lag).fillna(0.0)
    df["etc_cash_sales"] = df["etc_revenue_accrual"].shift(sell_lag).fillna(0.0)
    return df

if __name__ == "__main__":
    repo_root = Path(".")
    conf_path = repo_root / "config" / "assumptions.json"
    if not conf_path.exists():
        raise SystemExit(f"Missing assumptions file: {conf_path}")
    assumptions = json.loads(conf_path.read_text())
    df = build_monthly_model(assumptions, repo_root)
    out = repo_root / "data" / "monthly_model_2025_2030_full.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"Wrote {out}")
