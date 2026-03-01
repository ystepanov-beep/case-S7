import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

FILE_NAME = "S7 case (1).xlsx"
PRODUCT_ID = 73
START_DATE = "2023-01-01"
FORECAST_HORIZON = 14
CURRENT_STOCK = 110000
SERVICE_LEVEL = 0.95
SIMULATIONS = 10000

cons = pd.read_excel(FILE_NAME, sheet_name="final_consumtion_train")
cons.columns = cons.columns.str.strip().str.lower()

cons = cons[cons["product_id"] == PRODUCT_ID].copy()
cons["consumtion_date"] = pd.to_datetime(cons["consumtion_date"])
cons = cons[cons["consumtion_date"] >= START_DATE]
cons["qty"] = pd.to_numeric(cons["qty"], errors="coerce")

upper_limit = cons["qty"].quantile(0.9999)
cons = cons[cons["qty"] <= upper_limit]

monthly_demand = (
    cons
    .set_index("consumtion_date")
    .resample("ME")["qty"]
    .sum()
)

print("\nПроверка данных:")
print("Минимум:", monthly_demand.min())
print("Максимум:", monthly_demand.max())
print("Среднее:", monthly_demand.mean())

monthly_values = monthly_demand.values

simulated_totals = np.random.choice(
    monthly_values,
    size=(SIMULATIONS, FORECAST_HORIZON),
    replace=True
).sum(axis=1)

required_stock = np.percentile(simulated_totals, SERVICE_LEVEL * 100)
prob_stockout = np.mean(simulated_totals > CURRENT_STOCK)
recommended_purchase = max(required_stock - CURRENT_STOCK, 0)

print("Средний месячный спрос:", round(monthly_demand.mean()))
print("Ожидаемый годовой спрос:", round(monthly_demand.mean() * FORECAST_HORIZON))
print("Текущий запас:", CURRENT_STOCK)
print("Вероятность дефицита:", round(prob_stockout * 100, 2), "%")
print("Необходимый запас (95% сервис):", round(required_stock))
print("Рекомендуемая закупка:", round(recommended_purchase))

plt.figure(figsize=(10,5))
plt.hist(simulated_totals, bins=40, alpha=0.7)
plt.axvline(CURRENT_STOCK, color="red", label="Текущий запас")
plt.axvline(required_stock, color="green", label="95% уровень")
plt.title("Распределение годового спроса")
plt.legend()
plt.show()