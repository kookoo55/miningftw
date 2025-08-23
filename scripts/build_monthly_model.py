# scripts/build_monthly_model.py
import json, math
import pandas as pd
from pathlib import Path

_TWO32 = 2**32

def _days_in_month(dt: pd.Timestamp) -> int:
    eom = dt + pd.offsets.MonthEnd(0)
    return (eom - dt).days + 1

def _network_hashrate_hs(difficulty: float, block_time_s: float) -> float:
    return float(difficulty) * _TWO32 / float(block_time_s)

def _extract_specs(csv_path: Path, model_name: str):
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")
    df = pd.read_csv(csv_path)

    # model column
    model_col = None
    for c in df.columns:
        if c.strip().lower() == "model" or "model" in c.strip().lower():
            model_col = c
            break
    if model_col is None:
        raise ValueError(f"No 'model' column in {csv_path.name}")

    # match row
    mask = df[model_col].astype(str).str.strip().str.lower() == model_name.strip().lower()
    if not mask.any():
        raise ValueError(f"Model '{model_name}' not found in {csv_path.name}. Available: {df[model_col].tolist()}")
    row = df.loc[mask].iloc[0]

    # hashrate + unit
    hr_col, unit_kind = None, None
    for c in df.columns:
        cl = c.lower()
        if "hashrate" in cl:
            hr_col = c
            if "th/s" in cl:
                unit_kind = "TH/s"
            elif "gh/s" in cl:
                unit_kind = "GH/s"
            break
    if hr_col is None or unit_kind is None:
        raise ValueError(f"Could not determine hashrate/unit from columns in {csv_path.name}")

    # power (W)
    pwr_col = None
    for c in df.columns:
        if "power" in c.lower() and "(w" in c.lower():
            pwr_col = c
            break
    if pwr_col is None:
        raise ValueError(f"Could not find power (W) column in {csv_path.name}")

    per_unit_hash = float(row[hr_col])
    power_w_each = float(row[pwr_col])
    return per_unit_hash, unit_kind, power_w_each

def _fleet_hashrate_hs(units: int, per_unit_hash: float, unit_kind: str) -> float:
    scale = 1e12 if unit_kind.upper().startswith("TH") else 1e9
    return float(units) * float(per_unit_hash) * scale

def _coins_per_day_from_difficulty(conf: dict, units: int, per_unit_hash: float, unit_kind: str) -> float:
    if not conf.get("use_difficulty", False):
        return 0.0
    diff0 = float(conf["difficulty_now"])
    block_time_s = float(conf["block_time_s"])
    reward = float(conf["block_reward"])
    fee = float(conf.get("pool_fee_pct", 0.0))
    net_hash = _network_hashrate_hs(diff0, block_time_s)
    miner_hash = _fleet_hashrate_hs(units, per_unit_hash, unit_kind)
    share = 0.0 if net_hash <= 0 else (miner_hash / net_hash)
    blocks_per_day = 86400.0 / block_time_s
    return share * blocks_per_day * reward * (1.0 - fee)

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

    # ALWAYS read specs from CSVs
    btc_hash, btc_unit_kind, btc_power_each = _extract_specs(repo_root / btc_conf["source_csv"], btc_conf["model_name"])
    etc_hash, etc_unit_kind, etc_power_each = _extract_specs(repo_root / etc_conf["source_csv"], etc_conf["model_name"])

    btc_units = int(btc_conf["units"])
    etc_units = int(etc_conf["units"])

    btc_price0 = float(btc_conf["base_price_usd"])
    etc_price0 = float(etc_conf["base_price_usd"])
    btc_price_growth = float(btc_conf.get("annual_price_pct", 0.0))
    etc_price_growth = float(etc_conf.get("annual_price_pct", 0.0))
    btc_diff_growth  = float(btc_conf.get("annual_difficulty_pct", 0.0))
    etc_diff_growth  = float(etc_conf.get("annual_difficulty_pct", 0.0))

    btc_day0 = _coins_per_day_from_difficulty(btc_conf, btc_units, btc_hash, btc_unit_kind)
    etc_day0 = _coins_per_day_from_difficulty(etc_conf, etc_units, etc_hash, etc_unit_kind)

    rows = []
    for p in months:
        dt = p.to_timestamp()
        year_index = dt.year - start.year

        btc_price = btc_price0 * ((1.0 + btc_price_growth) ** year_index)
        etc_price = etc_price0 * ((1.0 + etc_price_growth) ** year_index)

        btc_day   = btc_day0 / ((1.0 + btc_diff_growth) ** year_index)
        etc_day   = etc_day0 / ((1.0 + etc_diff_growth) ** year_index)

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
            "btc_model": btc_conf["model_name"],
            "etc_model": etc_conf["model_name"],
            "btc_units": btc_units,
            "etc_units": etc_units,
            "btc_unit_hash": btc_hash,
            "etc_unit_hash": etc_hash,
            "btc_unit_hash_unit": btc_unit_kind,
            "etc_unit_hash_unit": etc_unit_kind,
            "btc_unit_power_w": btc_power_each,
            "etc_unit_power_w": etc_power_each,
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
    out = repo_root / "data" / "monthly_model_2025_2030.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"Wrote {out}")