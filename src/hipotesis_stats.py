"""Compute cross-tab stats for hypothesis report (Fase 5)."""
from pathlib import Path

import pandas as pd
from scipy.stats import chi2_contingency, mannwhitneyu

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "raw" / "ecommerce.csv"
TARGET = "Churn"


def churn_rate(mask: pd.Series) -> tuple[float, int]:
    sub = df[mask]
    return float(sub[TARGET].mean()), len(sub)


def chi2_binary(group_col: pd.Series, label: str) -> dict:
    table = pd.crosstab(group_col, df[TARGET])
    chi2, p, _, _ = chi2_contingency(table)
    rates = df.groupby(group_col)[TARGET].mean()
    return {"label": label, "chi2": chi2, "p": p, "rates": rates.to_dict()}


df = pd.read_csv(DATA_PATH)
base_churn = df[TARGET].mean()

print(f"Base churn: {base_churn:.1%}\n")

# Means by churn
print("=== Medias activo vs churn ===")
for c in [
    "Tenure",
    "SatisfactionScore",
    "DaySinceLastOrder",
    "CashbackAmount",
    "NumberOfDeviceRegistered",
    "WarehouseToHome",
    "CouponUsed",
    "OrderCount",
]:
    m0 = df.loc[df[TARGET] == 0, c].mean()
    m1 = df.loc[df[TARGET] == 1, c].mean()
    print(f"{c}: activo={m0:.2f} churn={m1:.2f} diff={m1 - m0:+.2f}")

# H1 Tenure
df["tenure_short"] = df["Tenure"] < 6
r_short, n_short = churn_rate(df["tenure_short"])
r_long, n_long = churn_rate(~df["tenure_short"] & df["Tenure"].notna())
print(f"\nH1 Tenure<6: {r_short:.1%} (n={n_short}) vs >=6: {r_long:.1%} (n={n_long})")
print(chi2_binary(df["tenure_short"], "H1"))

# H2 Complain
r_c1, n_c1 = churn_rate(df["Complain"] == 1)
r_c0, n_c0 = churn_rate(df["Complain"] == 0)
print(f"\nH2 Complain=1: {r_c1:.1%} vs 0: {r_c0:.1%}")
print(chi2_binary(df["Complain"] == 1, "H2"))

# H3 Satisfaction low vs high
df["sat_low"] = df["SatisfactionScore"] <= 2
df["sat_high"] = df["SatisfactionScore"] >= 4
r_sl, _ = churn_rate(df["sat_low"])
r_sh, _ = churn_rate(df["sat_high"])
print(f"\nH3 sat<=2: {r_sl:.1%} vs sat>=4: {r_sh:.1%}")

# H4 Days
df["days_recent"] = df["DaySinceLastOrder"] <= 7
df["days_8_30"] = (df["DaySinceLastOrder"] > 7) & (df["DaySinceLastOrder"] <= 30)
r_d7, n_d7 = churn_rate(df["days_recent"])
r_d30, n_d30 = churn_rate(df["days_8_30"])
print(f"\nH4 0-7d: {r_d7:.1%} (n={n_d7}) vs 8-30d: {r_d30:.1%} (n={n_d30})")

# H5 Happy churner
h5_mask = (
    (df["Tenure"] < 6)
    & (df["SatisfactionScore"] >= 4)
    & (df["DaySinceLastOrder"] <= 7)
    & (df["Complain"] == 0)
)
r_h5, n_h5 = churn_rate(h5_mask)
h5_ctrl = (df["Tenure"] >= 6) & (df["SatisfactionScore"] >= 4) & (df["Complain"] == 0)
r_h5c, n_h5c = churn_rate(h5_ctrl)
print(f"\nH5 happy churner: {r_h5:.1%} (n={n_h5}) vs control tenure>=6 sat>=4: {r_h5c:.1%} (n={n_h5c})")

# H6 Promo capture
coupon_med = df["CouponUsed"].median()
cash_med = df["CashbackAmount"].median()
h6_mask = (df["Tenure"] < 6) & (df["CouponUsed"] > coupon_med) & (df["CashbackAmount"] < cash_med)
r_h6, n_h6 = churn_rate(h6_mask)
h6_ctrl = (df["Tenure"] < 6) & ~((df["CouponUsed"] > coupon_med) & (df["CashbackAmount"] < cash_med))
r_h6c, n_h6c = churn_rate(h6_ctrl)
print(f"\nH6 promo capture: {r_h6:.1%} (n={n_h6}) vs otros nuevos: {r_h6c:.1%} (n={n_h6c})")

# H7 Devices x tenure
print("\nH7 Devices x Tenure:")
for d in [1, 2, 3, 4]:
    for short in [True, False]:
        m = (df["NumberOfDeviceRegistered"] == d) & (
            (df["Tenure"] < 6) if short else (df["Tenure"] >= 6)
        )
        r, n = churn_rate(m)
        if n > 20:
            print(f"  devices={d} tenure_short={short}: {r:.1%} n={n}")

# Sat x Tenure matrix
print("\nSat x Tenure:")
df["tbin"] = pd.cut(df["Tenure"], [0, 6, 999], labels=["<6", "6+"], right=False)
for t in ["<6", "6+"]:
    for s in [1, 3, 5]:
        m = (df["tbin"] == t) & (df["SatisfactionScore"] == s)
        r, n = churn_rate(m)
        if n > 20:
            print(f"  {t} sat={s}: {r:.1%} n={n}")

# Tenure x Days
print("\nTenure x Days:")
for t_short in [True, False]:
    for recent in [True, False]:
        m = (df["Tenure"] < 6 if t_short else df["Tenure"] >= 6) & (
            df["DaySinceLastOrder"] <= 7 if recent else (df["DaySinceLastOrder"] > 7)
        )
        r, n = churn_rate(m)
        if n > 20:
            print(f"  tenure_short={t_short} recent={recent}: {r:.1%} n={n}")

# Warehouse x tenure
wh_med = df["WarehouseToHome"].median()
h_wh = (df["Tenure"] < 6) & (df["WarehouseToHome"] > wh_med)
r_wh, n_wh = churn_rate(h_wh)
h_wh_l = (df["Tenure"] < 6) & (df["WarehouseToHome"] <= wh_med)
r_whl, n_whl = churn_rate(h_wh_l)
print(f"\nWarehouse alto + tenure<6: {r_wh:.1%} n={n_wh} vs bajo: {r_whl:.1%} n={n_whl}")

# Mann-Whitney for continuous
u, p = mannwhitneyu(
    df.loc[df[TARGET] == 0, "CashbackAmount"].dropna(),
    df.loc[df[TARGET] == 1, "CashbackAmount"].dropna(),
    alternative="greater",
)
print(f"\nCashback activo > churn Mann-Whitney p={p:.2e}")
