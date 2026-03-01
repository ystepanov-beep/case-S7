import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

file_path = "cases7.xlsx"

col_time = "delivery_time"
col_reliability = "Product reliability"

df = pd.read_excel(file_path)

def to_number(x):
    if isinstance(x, str):
        x = x.replace(" ", "").replace("\xa0", "").replace(",", ".")
    return pd.to_numeric(x, errors="coerce")

for c in [col_time, col_reliability, "amount"]:
    if c in df.columns:
        df[c] = df[c].apply(to_number)

df["delivery_date"] = pd.to_datetime(df["delivery_date"])
df = df.sort_values("delivery_date")
df["prod_id"] = df["prod_id"].astype(str)

plt.style.use("seaborn-v0_8-whitegrid")

for cat in sorted(df["category"].dropna().unique()):
    data = df[df["category"] == cat]
    if data.empty:
        continue

    fig, axes = plt.subplots(1, 2, figsize=(22, 9))
    fig.suptitle(f"Категория: {cat}", fontsize=18)

    ax1 = axes[0]
    sns.lineplot(
        data=data,
        x="delivery_date",
        y=col_time,
        hue="prod_id",
        palette=["gray"] * data["prod_id"].nunique(),
        legend=False,
        linewidth=1,
        alpha=0.3,
        ax=ax1
    )

    sc1 = ax1.scatter(
        data["delivery_date"],
        data[col_time],
        c=data[col_time],
        cmap="RdYlGn_r",
        s=35,
        edgecolor="black",
        linewidth=0.4
    )

    cb1 = plt.colorbar(sc1, ax=ax1)
    cb1.set_label("Дней доставки")
    ax1.set_title("Время доставки")
    ax1.set_ylabel("Дней")
    ax1.tick_params(axis="x", rotation=45)

    ax2 = axes[1]

    if col_reliability in data.columns:
        sns.lineplot(
            data=data,
            x="delivery_date",
            y=col_reliability,
            hue="prod_id",
            palette=["gray"] * data["prod_id"].nunique(),
            legend=False,
            linewidth=1,
            alpha=0.3,
            ax=ax2
        )

        sc2 = ax2.scatter(
            data["delivery_date"],
            data[col_reliability],
            c=data[col_reliability],
            cmap="RdYlGn",
            s=35,
            edgecolor="black",
            linewidth=0.4
        )

        cb2 = plt.colorbar(sc2, ax=ax2)
        cb2.set_label("Надежность")
        ax2.set_title("Надежность")
        ax2.set_ylabel("0–1")
        ax2.set_ylim(-0.1, 1.1)
        ax2.tick_params(axis="x", rotation=45)

    plt.tight_layout()
    plt.savefig(f"Chart_ProdID_Cat_{cat}.png", dpi=150)
    plt.close()

print("Готово")