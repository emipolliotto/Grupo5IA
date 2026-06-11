"""Cross-tab stats without external deps."""
import csv
import math
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "raw" / "ecommerce.csv"

rows = []
with open(DATA_PATH, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append(r)


def fval(row, col):
    v = row.get(col, "")
    if v in ("", None):
        return None
    return float(v)


def churn_rate(mask):
    sub = [r for r, m in zip(rows, mask) if m]
    if not sub:
        return 0.0, 0
    churn = sum(1 for r in sub if int(float(r["Churn"])) == 1)
    return churn / len(sub), len(sub)


def chi2_2x2(a_pos, a_neg, b_pos, b_neg):
    table = [[a_pos, a_neg], [b_pos, b_neg]]
    n = sum(sum(r) for r in table)
    row_tot = [sum(r) for r in table]
    col_tot = [table[0][c] + table[1][c] for c in range(2)]
    chi2 = 0.0
    for i in range(2):
        for j in range(2):
            exp = row_tot[i] * col_tot[j] / n
            if exp > 0:
                chi2 += (table[i][j] - exp) ** 2 / exp
    # df=1, approximate p via normal for large n
    return chi2


n = len(rows)
base = sum(1 for r in rows if int(float(r["Churn"])) == 1) / n
print(f"Base churn: {base:.1%} n={n}")

# Means
for col in [
    "Tenure",
    "SatisfactionScore",
    "DaySinceLastOrder",
    "CashbackAmount",
    "NumberOfDeviceRegistered",
    "WarehouseToHome",
    "CouponUsed",
]:
    vals0 = [fval(r, col) for r in rows if int(float(r["Churn"])) == 0 and fval(r, col) is not None]
    vals1 = [fval(r, col) for r in rows if int(float(r["Churn"])) == 1 and fval(r, col) is not None]
    m0 = sum(vals0) / len(vals0)
    m1 = sum(vals1) / len(vals1)
    print(f"{col}: activo={m0:.2f} churn={m1:.2f} diff={m1-m0:+.2f}")

# H1
mask_short = [fval(r, "Tenure") is not None and fval(r, "Tenure") < 6 for r in rows]
mask_long = [fval(r, "Tenure") is not None and fval(r, "Tenure") >= 6 for r in rows]
r1, n1 = churn_rate(mask_short)
r1b, n1b = churn_rate(mask_long)
print(f"\nH1 Tenure<6: {r1:.1%} n={n1} vs >=6: {r1b:.1%} n={n1b} lift={r1/r1b:.1f}x")

# H2
mask_c1 = [int(float(r["Complain"])) == 1 for r in rows]
mask_c0 = [int(float(r["Complain"])) == 0 for r in rows]
r2, n2 = churn_rate(mask_c1)
r2b, n2b = churn_rate(mask_c0)
print(f"H2 Complain=1: {r2:.1%} n={n2} vs 0: {r2b:.1%} n={n2b} lift={r2/r2b:.1f}x")

# H3
mask_sl = [fval(r, "SatisfactionScore") is not None and fval(r, "SatisfactionScore") <= 2 for r in rows]
mask_sh = [fval(r, "SatisfactionScore") is not None and fval(r, "SatisfactionScore") >= 4 for r in rows]
r3l, n3l = churn_rate(mask_sl)
r3h, n3h = churn_rate(mask_sh)
print(f"H3 sat<=2: {r3l:.1%} n={n3l} vs sat>=4: {r3h:.1%} n={n3h}")

# H4
mask_d7 = [fval(r, "DaySinceLastOrder") is not None and fval(r, "DaySinceLastOrder") <= 7 for r in rows]
mask_d30 = [
    fval(r, "DaySinceLastOrder") is not None
    and 7 < fval(r, "DaySinceLastOrder") <= 30
    for r in rows
]
r4a, n4a = churn_rate(mask_d7)
r4b, n4b = churn_rate(mask_d30)
print(f"H4 0-7d: {r4a:.1%} n={n4a} vs 8-30d: {r4b:.1%} n={n4b}")

# coupon/cash medians
coupons = [fval(r, "CouponUsed") for r in rows if fval(r, "CouponUsed") is not None]
cashbacks = [fval(r, "CashbackAmount") for r in rows if fval(r, "CashbackAmount") is not None]
coupons.sort()
cashbacks.sort()
c_med = coupons[len(coupons) // 2]
cash_med = cashbacks[len(cashbacks) // 2]
wh_vals = [fval(r, "WarehouseToHome") for r in rows if fval(r, "WarehouseToHome") is not None]
wh_vals.sort()
wh_med = wh_vals[len(wh_vals) // 2]

# H5
mask_h5 = []
for r in rows:
    t = fval(r, "Tenure")
    s = fval(r, "SatisfactionScore")
    d = fval(r, "DaySinceLastOrder")
    c = int(float(r["Complain"]))
    mask_h5.append(t is not None and t < 6 and s is not None and s >= 4 and d is not None and d <= 7 and c == 0)
r5, n5 = churn_rate(mask_h5)

mask_h5c = []
for r in rows:
    t = fval(r, "Tenure")
    s = fval(r, "SatisfactionScore")
    c = int(float(r["Complain"]))
    mask_h5c.append(t is not None and t >= 6 and s is not None and s >= 4 and c == 0)
r5c, n5c = churn_rate(mask_h5c)
print(f"H5 happy churner: {r5:.1%} n={n5} vs control: {r5c:.1%} n={n5c}")

# H6
mask_h6 = []
mask_h6_other = []
for r in rows:
    t = fval(r, "Tenure")
    cu = fval(r, "CouponUsed")
    ca = fval(r, "CashbackAmount")
    is_new = t is not None and t < 6
    promo = cu is not None and ca is not None and cu > c_med and ca < cash_med
    mask_h6.append(is_new and promo)
    mask_h6_other.append(is_new and not promo)
r6, n6 = churn_rate(mask_h6)
r6b, n6b = churn_rate(mask_h6_other)
print(f"H6 promo capture: {r6:.1%} n={n6} vs otros nuevos: {r6b:.1%} n={n6b}")

# H7 devices
print("H7:")
for d in [1, 2, 3, 4]:
    for short in [True, False]:
        mask = []
        for r in rows:
            t = fval(r, "Tenure")
            dev = fval(r, "NumberOfDeviceRegistered")
            if t is None or dev is None:
                mask.append(False)
            elif short:
                mask.append(t < 6 and dev == d)
            else:
                mask.append(t >= 6 and dev == d)
        r, nn = churn_rate(mask)
        if nn > 20:
            print(f"  dev={d} short={short}: {r:.1%} n={nn}")

# Sat x tenure
print("Sat x Tenure:")
for t_short in [True, False]:
    for s in [1, 3, 5]:
        mask = []
        for r in rows:
            t = fval(r, "Tenure")
            sc = fval(r, "SatisfactionScore")
            if t is None or sc is None:
                mask.append(False)
            elif t_short:
                mask.append(t < 6 and sc == s)
            else:
                mask.append(t >= 6 and sc == s)
        r, nn = churn_rate(mask)
        if nn > 20:
            print(f"  short={t_short} sat={s}: {r:.1%} n={nn}")

# Tenure x days
print("Tenure x Days:")
for t_short in [True, False]:
    for recent in [True, False]:
        mask = []
        for r in rows:
            t = fval(r, "Tenure")
            d = fval(r, "DaySinceLastOrder")
            if t is None or d is None:
                mask.append(False)
            elif t_short and recent:
                mask.append(t < 6 and d <= 7)
            elif t_short:
                mask.append(t < 6 and d > 7)
            elif recent:
                mask.append(t >= 6 and d <= 7)
            else:
                mask.append(t >= 6 and d > 7)
        r, nn = churn_rate(mask)
        if nn > 20:
            print(f"  short={t_short} recent={recent}: {r:.1%} n={nn}")

# Warehouse
mask_wh = []
mask_whl = []
for r in rows:
    t = fval(r, "Tenure")
    w = fval(r, "WarehouseToHome")
    if t is not None and t < 6 and w is not None:
        mask_wh.append(w > wh_med)
        mask_whl.append(w <= wh_med)
    else:
        mask_wh.append(False)
        mask_whl.append(False)
rwh, nwh = churn_rate(mask_wh)
rwhl, nwhl = churn_rate(mask_whl)
print(f"Warehouse alto+new: {rwh:.1%} n={nwh} vs bajo: {rwhl:.1%} n={nwhl}")

# Interaction tenure complain
print("Tenure x Complain:")
for t_short in [True, False]:
    for comp in [0, 1]:
        mask = []
        for r in rows:
            t = fval(r, "Tenure")
            if t is None:
                mask.append(False)
            elif t_short:
                mask.append(t < 6 and int(float(r["Complain"])) == comp)
            else:
                mask.append(t >= 6 and int(float(r["Complain"])) == comp)
        r, nn = churn_rate(mask)
        print(f"  short={t_short} complain={comp}: {r:.1%} n={nn}")
