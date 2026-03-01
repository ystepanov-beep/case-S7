import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing

ids_to_buy = [0, 1, 6, 15, 21, 22, 25, 26, 30, 31, 32, 37, 42, 43, 45,
              46, 47, 48, 50, 54, 56, 58, 61, 63, 67, 70, 71]

df_orders = pd.read_excel("S7 case (1).xlsx", sheet_name="final_orders_train")
df_orders["order_date"] = pd.to_datetime(df_orders["order_date"])

df_orders = df_orders[df_orders["prod_id"].isin(ids_to_buy)]
df_orders["unit_price"] = df_orders["amount"] / df_orders["qty"]

price_forecasts = []

for pid in ids_to_buy:
    
    sku_data = df_orders[df_orders["prod_id"] == pid]
    
    monthly_price = (
        sku_data
        .groupby(pd.Grouper(key="order_date", freq="MS"))["unit_price"]
        .mean()
        .dropna()
    )
    
    if len(monthly_price) < 4:
        forecast_price = monthly_price.mean()
    else:
        try:
            model = ExponentialSmoothing(
                monthly_price,
                trend=None,
                seasonal=None,
                initialization_method="estimated"
            ).fit()
            
            forecast = model.forecast(12)
            forecast_price = forecast.mean()
            
        except:
            forecast_price = monthly_price.mean()
    
    price_forecasts.append({
        "prod_id": pid,
        "forecast_price_next_12m_avg": forecast_price
    })

price_forecast_df = pd.DataFrame(price_forecasts)

print(price_forecast_df)