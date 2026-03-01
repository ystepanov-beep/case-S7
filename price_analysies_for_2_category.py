import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing

iod_ids = [74, 75, 79, 80, 81, 82, 83, 85, 86, 87, 88, 93, 94, 95, 96,
           101, 102, 103, 104, 105, 106, 109, 110, 111, 112, 117,
           118, 119, 120, 122, 123, 124, 125, 126, 127]

df_orders = pd.read_excel("S7 case (1).xlsx", sheet_name="final_orders_train")
df_orders["order_date"] = pd.to_datetime(df_orders["order_date"])

df_orders = df_orders[df_orders["prod_id"].isin(iod_ids)]
df_orders["unit_price"] = df_orders["amount"] / df_orders["qty"]

price_forecasts = {}

for pid in iod_ids:

    sku_data = df_orders[df_orders["prod_id"] == pid]

    monthly_price = (
        sku_data.groupby(pd.Grouper(key="order_date", freq="MS"))["unit_price"]
        .mean()
        .dropna()
    )

    if len(monthly_price) < 4:
        price_forecasts[pid] = monthly_price.mean()
        continue

    try:
        log_price = np.log(monthly_price)

        model = ExponentialSmoothing(
            log_price,
            trend="add",
            seasonal=None,
            initialization_method="estimated"
        ).fit()

        log_forecast = model.forecast(12)

        forecast = np.exp(log_forecast)

        price_forecasts[pid] = forecast.mean()

    except:
        price_forecasts[pid] = monthly_price.mean()

price_df = pd.DataFrame({
    "product_id": price_forecasts.keys(),
    "forecast_price_next_12m": price_forecasts.values()
}).sort_values("forecast_price_next_12m", ascending=False)

print(price_df)