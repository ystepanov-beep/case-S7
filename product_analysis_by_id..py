import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

file_path = "cases7.xlsx"

print("Loading data...")
try:
    df = pd.read_excel(file_path)
except FileNotFoundError:
    print(f"File not found: {file_path}")
    raise SystemExit

col_time = "delivery_time"
col_reliability = "Product reliability"

def to_float(x):
    if isinstance(x, str):
        x = x.replace(" ", "").replace("\xa0", "").replace(",", ".")
    return pd.to_numeric(x, errors="coerce")

for c in [col_time, col_reliability]:
    if c in df.columns:
        df[c] = df[c].apply(to_float)

df["delivery_date"] = pd.to_datetime(df["delivery_date"])
df["prod_id"] = df["prod_id"].astype(str)
df = df.sort_values("delivery_date")

print(f"Unique prod_id: {df['prod_id'].nunique()}")

while True:
    print("-" * 40)
    value = input("Enter prod_id (or exit): ").strip()

    if value.lower() in ["exit", "quit"]:
        print("Done")
        break

    data = df[df["prod_id"] == value]

    if data.empty:
        print("Not found")
        continue

    print(f"Rows found: {len(data)}")

    fig, axes = plt.subplots(1, 2, figsize=(17, 6))
    category = data["category"].iloc[0] if "category" in data.columns else ""
    fig.suptitle(f"prod_id: {value}  category: {category}", fontsize=14)

    ax1 = axes[0]
    ax1.plot(data["delivery_date"], data[col_time], color="gray", linewidth=2, alpha=0.6)
    sc1 = ax1.scatter(
        data["delivery_date"],
        data[col_time],
        c=data[col_time],
        cmap="RdYlGn_r",
        s=90,
        edgecolors="black"
    )
    plt.colorbar(sc1, ax=ax1)
    ax1.set_title("Delivery time")
    ax1.set_ylabel("Days")
    ax1.set_xlabel("Date")
    ax1.tick_params(axis="x", rotation=45)
    ax1.grid(True, linestyle="--", alpha=0.5)

    ax2 = axes[1]

    if col_reliability in data.columns:
        ax2.plot(data["delivery_date"], data[col_reliability], color="gray", linewidth=2, alpha=0.6)
        sc2 = ax2.scatter(
            data["delivery_date"],
            data[col_reliability],
            c=data[col_reliability],
            cmap="RdYlGn",
            s=90,
            edgecolors="black"
        )
        plt.colorbar(sc2, ax=ax2)
        ax2.set_ylim(-0.1, 1.1)
        ax2.set_title("Reliability")
        ax2.set_ylabel("0-1")
        ax2.set_xlabel("Date")
        ax2.tick_params(axis="x", rotation=45)
        ax2.grid(True, linestyle="--", alpha=0.5)
    else:
        ax2.text(0.5, 0.5, "No reliability data", ha="center")

    plt.tight_layout()
    plt.show()