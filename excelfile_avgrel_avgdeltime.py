import pandas as pd
import numpy as np

input_file = "cases7.xlsx"
output_file = "final_report_full.xlsx"

DATE_START = "2020-01-01"
DATE_FEB_2022 = "2022-02-01"
DATE_JAN_2024 = "2024-01-01"

print(f"Reading: {input_file}")
try:
    df = pd.read_excel(input_file)
except FileNotFoundError:
    print("File not found")
    raise SystemExit

col_time = "delivery_time"
col_rel = "Product reliability"

def to_float(x):
    if isinstance(x, str):
        x = x.strip().replace(" ", "").replace("\xa0", "").replace(",", ".")
        if x == "":
            return np.nan
    return pd.to_numeric(x, errors="coerce")

df[col_time] = df[col_time].apply(to_float)
df[col_rel] = df[col_rel].apply(to_float)

df["delivery_date"] = pd.to_datetime(df["delivery_date"])
df = df[df["delivery_date"] >= DATE_START]

df["prod_id"] = df["prod_id"].astype(str).str.strip()
df["category"] = df["category"].astype(str).str.strip()

ids = df["prod_id"].unique()
print(f"Unique IDs: {len(ids)}")

rows = []

for pid in ids:
    sub = df[df["prod_id"] == pid]
    cat = sub["category"].iloc[0] if "category" in sub.columns else ""

    p1 = sub[sub["delivery_date"] < DATE_FEB_2022]
    p2 = sub[(sub["delivery_date"] >= DATE_FEB_2022) & (sub["delivery_date"] < DATE_JAN_2024)]
    p3 = sub[sub["delivery_date"] >= DATE_JAN_2024]

    def stats(data):
        n = len(data)
        if n == 0:
            return 0, 0.0, 0.0

        avg_r = round(data[col_rel].mean(), 2)

        avg_t = data[col_time].mean()
        if pd.isna(avg_t):
            avg_t = "*"
        else:
            avg_t = round(avg_t, 2)

        return n, avg_r, avg_t

    q1, r1, t1 = stats(p1)
    q2, r2, t2 = stats(p2)
    q3, r3, t3 = stats(p3)

    rows.append({
        "id": pid,
        "prod_category": cat,
        "qty1": q1,
        "avg_product_reliability1": r1,
        "avg_delivery_time1": t1,
        "qty2": q2,
        "avg_product_reliability2": r2,
        "avg_delivery_time2": t2,
        "qty3": q3,
        "avg_product_reliability3": r3,
        "avg_delivery_time3": t3
    })

final_df = pd.DataFrame(rows)

try:
    final_df["tmp"] = pd.to_numeric(final_df["id"])
    final_df = final_df.sort_values("tmp").drop(columns=["tmp"])
except:
    final_df = final_df.sort_values("id")

print(f"Saving: {output_file}")
final_df.to_excel(output_file, index=False)
print("Done")