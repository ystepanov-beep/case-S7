import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt

plt.style.use("seaborn-v0_8")

ids_to_buy = [0, 1, 6, 15, 21, 22, 25, 26, 30, 31, 32, 37, 42, 43, 45,
              46, 47, 48, 50, 54, 56, 58, 61, 63, 67, 70, 71]

df = pd.read_excel("S7 case (1).xlsx", sheet_name="final_consumtion_train")
df["consumtion_date"] = pd.to_datetime(df["consumtion_date"])

df_cat4 = df[(df["category"] == 4) &
             (df["product_id"].isin(ids_to_buy)) &
             (df["consumtion_date"] >= "2022-01-01")]

sku_base = {}
sku_forecasts = {}

for pid in ids_to_buy:

    sku_data = df_cat4[df_cat4["product_id"] == pid]

    monthly = (
        sku_data.groupby(pd.Grouper(key="consumtion_date", freq="MS"))["qty"]
        .sum()
        .asfreq("MS")
        .fillna(0)
    )

    if monthly.empty:
        sku_base[pid] = 0
        sku_forecasts[pid] = 0
        continue

    if monthly.sum() == 0 or len(monthly) < 18 or monthly.std() == 0:
        base = monthly.mean() * 14
        base = 0 if np.isnan(base) else base
        sku_base[pid] = base
        sku_forecasts[pid] = base
        continue

    try:
        monthly_log = np.log1p(monthly)

        model = sm.tsa.statespace.SARIMAX(
            monthly_log,
            order=(1,0,1),
            seasonal_order=(0,1,1,12),
            enforce_stationarity=True,
            enforce_invertibility=True
        ).fit(disp=False)

        forecast = model.get_forecast(steps=14)
        mean_forecast = np.expm1(forecast.predicted_mean)

        base = mean_forecast.sum()
        residuals = model.resid
        sigma = np.std(residuals)

        Z = 1.28
        buffer = Z * sigma * np.sqrt(14)

        base = 0 if np.isnan(base) else base
        total = base + (0 if np.isnan(buffer) else buffer)

        sku_base[pid] = base
        sku_forecasts[pid] = total

    except:
        base = monthly.mean() * 14
        base = 0 if np.isnan(base) else base
        sku_base[pid] = base
        sku_forecasts[pid] = base

sku_base = {k: (0 if np.isnan(v) else v) for k, v in sku_base.items()}
sku_forecasts = {k: (0 if np.isnan(v) else v) for k, v in sku_forecasts.items()}

total_base = sum(sku_base.values())
total_purchase = sum(sku_forecasts.values())

purchase_df = pd.DataFrame({
    "product_id": sku_forecasts.keys(),
    "base_forecast_14m": sku_base.values(),
    "purchase_qty_14m_plan": np.round(list(sku_forecasts.values()), 0)
}).sort_values("purchase_qty_14m_plan", ascending=False)

print("Total base forecast:", round(total_base))
print("Total purchase:", round(total_purchase))
print(purchase_df)

historical_total = (
    df_cat4.groupby(pd.Grouper(key="consumtion_date", freq="MS"))["qty"]
    .sum()
    .asfreq("MS")
)

future_index = pd.date_range(
    start=historical_total.index.max() + pd.offsets.MonthBegin(),
    periods=14,
    freq="MS"
)

total_forecast_series = pd.Series(0, index=future_index)

for pid in ids_to_buy:

    sku_data = df_cat4[df_cat4["product_id"] == pid]

    monthly = (
        sku_data.groupby(pd.Grouper(key="consumtion_date", freq="MS"))["qty"]
        .sum()
        .asfreq("MS")
        .fillna(0)
    )

    if monthly.empty:
        continue

    if monthly.sum() == 0 or len(monthly) < 18 or monthly.std() == 0:
        future = pd.Series([monthly.mean()] * 14, index=future_index)

    else:
        try:
            monthly_log = np.log1p(monthly)

            model = sm.tsa.statespace.SARIMAX(
                monthly_log,
                order=(1,0,1),
                seasonal_order=(0,1,1,12),
                enforce_stationarity=True,
                enforce_invertibility=True
            ).fit(disp=False)

            forecast = model.get_forecast(steps=14)
            future = np.expm1(forecast.predicted_mean)
            future.index = future_index

        except:
            future = pd.Series([monthly.mean()] * 14, index=future_index)

    total_forecast_series += future

plt.figure(figsize=(12,6))
plt.plot(historical_total)
plt.plot(total_forecast_series)
plt.tight_layout()
plt.show()