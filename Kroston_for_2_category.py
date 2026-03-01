import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.style.use("seaborn-v0_8")

iod_ids = [74, 75, 79, 80, 81, 82, 83, 85, 86, 87, 88, 93, 94, 95, 96,
           101, 102, 103, 104, 105, 106, 109, 110, 111, 112, 117,
           118, 119, 120, 122, 123, 124, 125, 126, 127]

df = pd.read_excel("S7 case (1).xlsx", sheet_name="final_consumtion_train")
df["consumtion_date"] = pd.to_datetime(df["consumtion_date"])

df_cat2 = df[
    (df["category"] == 2) &
    (df["product_id"].isin(iod_ids)) &
    (df["consumtion_date"] >= "2020-01-01")
]

def croston_monthly(series, alpha=0.1):

    demand = series.values
    q = 0
    a = 0
    p = 0
    first = True

    for t in range(len(demand)):
        if demand[t] > 0:
            if first:
                q = demand[t]
                a = 1
                first = False
            else:
                q = q + alpha * (demand[t] - q)
                a = a + alpha * (p - a)
            p = 1
        else:
            p += 1

    return q / a if a != 0 else 0

sku_plan = {}
buffer_percent = 0.15

for pid in iod_ids:

    sku_data = df_cat2[df_cat2["product_id"] == pid]

    monthly = (
        sku_data.groupby(pd.Grouper(key="consumtion_date", freq="MS"))["qty"]
        .sum()
        .asfreq("MS")
        .fillna(0)
    )

    if monthly.sum() == 0:
        sku_plan[pid] = 0
        continue

    monthly_rate = croston_monthly(monthly, alpha=0.1)

    base_14m = monthly_rate * 14
    purchase_qty = base_14m * (1 + buffer_percent)

    sku_plan[pid] = purchase_qty

purchase_df = pd.DataFrame({
    "product_id": sku_plan.keys(),
    "purchase_qty_14m": np.round(list(sku_plan.values()), 0)
}).sort_values("purchase_qty_14m", ascending=False)

total_purchase = sum(sku_plan.values())

print("Total 14M purchase:", round(total_purchase))
print(purchase_df)

historical_total = (
    df_cat2.groupby(pd.Grouper(key="consumtion_date", freq="MS"))["qty"]
    .sum()
    .asfreq("MS")
)

plt.figure(figsize=(12,6))
plt.plot(historical_total)
plt.title("Category 2 Historical Demand")
plt.tight_layout()
plt.show()