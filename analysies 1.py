import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import ExponentialSmoothing

file_path = "S7 case (1).xlsx"

consumtion = pd.read_excel(file_path, sheet_name="final_consumtion_train")
orders = pd.read_excel(file_path, sheet_name="final_orders_train")

consumtion["consumtion_date"] = pd.to_datetime(consumtion["consumtion_date"])
orders["order_date"] = pd.to_datetime(orders["order_date"])

consumtion = consumtion[consumtion["consumtion_date"] >= "2020-01-01"]
orders = orders[orders["order_date"] >= "2020-01-01"]

ids = [5, 34, 35]
forecast_horizon = 12

consumtion_grouped = (
    consumtion
    .groupby(["product_id", "consumtion_date"])["qty"]
    .sum()
    .reset_index()
)

orders_grouped = (
    orders
    .groupby(["prod_id", "order_date"])["qty"]
    .sum()
    .reset_index()
)

colors = {5: "blue", 34: "green", 35: "red"}

plt.figure(figsize=(16, 9))

all_forecasts = []

for i in ids:

    c_data = consumtion_grouped[consumtion_grouped["product_id"] == i]
    c_data = c_data.sort_values("consumtion_date")
    c_data["cum_qty"] = c_data["qty"].cumsum()

    plt.plot(
        c_data["consumtion_date"],
        c_data["cum_qty"],
        color=colors[i],
        linestyle="-",
        marker="o",
        markersize=3,
        label=f"consumtion {i}"
    )

    o_data = orders_grouped[orders_grouped["prod_id"] == i]
    o_data = o_data.sort_values("order_date")
    o_data["cum_qty"] = o_data["qty"].cumsum()

    plt.plot(
        o_data["order_date"],
        o_data["cum_qty"],
        color=colors[i],
        linestyle="--",
        marker="x",
        markersize=3,
        label=f"orders {i}"
    )

    monthly = (
        consumtion[consumtion["product_id"] == i]
        .set_index("consumtion_date")
        .resample("ME")["qty"]
        .sum()
    )

    if len(monthly) > 2:

        model = ExponentialSmoothing(
            monthly,
            trend="add",
            damped_trend=True,
            seasonal=None
        ).fit()

        forecast_full = model.forecast(24)

        if i == 34:
            start_date = pd.Timestamp("2025-09-30")
            forecast = forecast_full[forecast_full.index >= start_date].head(forecast_horizon)
        else:
            forecast = forecast_full.head(forecast_horizon)

        last_cum_value = c_data["cum_qty"].iloc[-1]
        forecast_cum = forecast.cumsum() + last_cum_value

        plt.plot(
            forecast_cum.index,
            forecast_cum,
            color=colors[i],
            linewidth=3,
            alpha=0.8,
            label=f"forecast consumtion {i}"
        )

        df_forecast = pd.DataFrame({
            "product_id": i,
            "month": forecast.index,
            "forecast_qty": forecast.values
        })

        all_forecasts.append(df_forecast)

plt.title("Cumulative Consumtion & Orders with Forecast")
plt.xlabel("Date")
plt.ylabel("Cumulative Quantity")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

forecast_table = pd.concat(all_forecasts, ignore_index=True)

print(forecast_table)

forecast_table.to_excel("monthly_forecast_by_product.xlsx", index=False)