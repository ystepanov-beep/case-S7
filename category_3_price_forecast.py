import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import ExponentialSmoothing

FILE_NAME = "S7 case (1).xlsx"
CATEGORY_ID = 3
START_DATE = "2023-01-01"
FORECAST_HORIZON = 12

df = pd.read_excel(FILE_NAME, sheet_name="final_orders_train")
df.columns = df.columns.str.strip().str.lower()

df = df[df["category"] == CATEGORY_ID].copy()

df["order_date"] = pd.to_datetime(df["order_date"])
df = df[df["order_date"] >= START_DATE]

df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
df["qty"] = pd.to_numeric(df["qty"], errors="coerce")
df = df[df["qty"] > 0]

df["price"] = df["amount"] / df["qty"]

monthly_price = (
    df.set_index("order_date")
      .resample("ME")["price"]
      .mean()
      .dropna()
)

model = ExponentialSmoothing(
    monthly_price,
    trend="add",
    seasonal=None
).fit()

forecast = model.forecast(FORECAST_HORIZON)

plt.figure(figsize=(10,5))
plt.plot(monthly_price.index, monthly_price.values)
future_dates = pd.date_range(monthly_price.index[-1], periods=FORECAST_HORIZON+1, freq="ME")[1:]
plt.plot(future_dates, forecast, linestyle="--")
plt.show()

print(np.round(forecast.values, 2))