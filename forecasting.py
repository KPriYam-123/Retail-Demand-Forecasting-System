import pandas as pd
import numpy as np
from datetime import timedelta
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_percentage_error, r2_score
import matplotlib.pyplot as plt


# --------------------------------------------
# FEATURE ENGINEERING
# --------------------------------------------
def create_features(df):
    df = df.sort_values("date")

    df["units_sold_lag_1"] = df["units_sold"].shift(1)
    df["units_sold_lag_7"] = df["units_sold"].shift(7)
    df["units_sold_lag_30"] = df["units_sold"].shift(30)

    df["rolling_mean_7"] = df["units_sold"].rolling(7).mean()
    df["rolling_mean_30"] = df["units_sold"].rolling(30).mean()

    df["day_of_week"] = df["date"].dt.dayofweek
    df["month"] = df["date"].dt.month
    df["quarter"] = df["date"].dt.quarter

    return df.dropna()


# --------------------------------------------
# TRAIN MODELS PER PRODUCT
# --------------------------------------------
def train_models(df_fe, feature_cols):
    models = {}
    metrics = {}

    for pid in df_fe["product_id"].unique():
        product_data = df_fe[df_fe["product_id"] == pid]
        if len(product_data) < 60:
            continue

        X = product_data[feature_cols]
        y = product_data["units_sold"]

        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, shuffle=False
        )

        train_data = lgb.Dataset(X_train, label=y_train)
        val_data = lgb.Dataset(X_val, label=y_val)

        params = {
            "objective": "regression",
            "metric": "mae",
            "learning_rate": 0.05,
            "num_leaves": 31,
            "max_depth": -1,
            "verbosity": -1,
        }

        model = lgb.train(
            params,
            train_data,
            valid_sets=[val_data],
            num_boost_round=300,
            early_stopping_rounds=30,
            verbose_eval=False
        )

        models[pid] = model

        # Validation metrics
        preds = model.predict(X_val)
        metrics[pid] = {
            "mape": float(mean_absolute_percentage_error(y_val, preds)),
            "r2": float(r2_score(y_val, preds))
        }

    return models, metrics


# --------------------------------------------
# FORECASTING
# --------------------------------------------
def forecast_products(df_fe, models, feature_cols, forecast_days=30):
    results = []

    for pid, model in models.items():
        product_data = df_fe[df_fe["product_id"] == pid].sort_values("date")
        last_row = product_data.tail(1)
        last_date = last_row["date"].iloc[0]

        forecast_vals = []
        forecast_dates = []

        row = last_row.copy()

        for i in range(forecast_days):
            X = row[feature_cols]
            pred = model.predict(X)[0]
            pred = max(0, pred)

            forecast_vals.append(pred)
            forecast_dates.append((last_date + timedelta(days=i + 1)).strftime("%Y-%m-%d"))

            # Update features for next day
            row["units_sold"] = pred
            row["units_sold_lag_1"] = pred
            row["units_sold_lag_7"] = pred
            row["units_sold_lag_30"] = pred
            row["rolling_mean_7"] = pred
            row["rolling_mean_30"] = pred

        results.append({
            "product_id": pid,
            "forecast_values": forecast_vals,
            "forecast_dates": forecast_dates
        })

    return results


# --------------------------------------------
# GRAPHS
# --------------------------------------------
def bargraph_total_sales(df):
    prod_sales = df.groupby("product_id")["units_sold"].sum()

    plt.figure(figsize=(12, 5))
    plt.bar(prod_sales.index, prod_sales.values)
    plt.title("Total Units Sold per Product")
    plt.xlabel("Product ID")
    plt.ylabel("Units Sold")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def plot_forecast(product_id, forecast_dates, forecast_values):
    plt.figure(figsize=(12, 5))
    plt.plot(forecast_dates, forecast_values, marker="o")
    plt.xticks(rotation=45)
    plt.title(f"30-Day Forecast for {product_id}")
    plt.xlabel("Date")
    plt.ylabel("Predicted Units Sold")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def bargraph_forecast(product_id, forecast_values):
    plt.figure(figsize=(12, 4))
    plt.bar(range(1, len(forecast_values) + 1), forecast_values)
    plt.title(f"30-Day Demand Forecast for {product_id}")
    plt.xlabel("Forecast Day")
    plt.ylabel("Units")
    plt.tight_layout()
    plt.show()


# --------------------------------------------
# MAIN EXECUTION
# --------------------------------------------
if __name__ == "__main__":
    df = pd.read_csv("dataset_final.csv")
    df["date"] = pd.to_datetime(df["date"])

    # Feature engineering per product
    fe_list = []
    for pid in df["product_id"].unique():
        temp = df[df["product_id"] == pid].copy()
        temp = create_features(temp)
        fe_list.append(temp)

    df_fe = pd.concat(fe_list)

    feature_cols = [
        "units_sold_lag_1", "units_sold_lag_7", "units_sold_lag_30",
        "rolling_mean_7", "rolling_mean_30",
        "day_of_week", "month", "quarter"
    ]

    # Train ML models
    models, metrics = train_models(df_fe, feature_cols)

    # Forecast
    forecasts = forecast_products(df_fe, models, feature_cols, forecast_days=30)

    # -----------------------
    # GENERATE GRAPHS
    # -----------------------
    bargraph_total_sales(df)

    for f in forecasts:
        plot_forecast(f["product_id"], f["forecast_dates"], f["forecast_values"])
        bargraph_forecast(f["product_id"], f["forecast_values"])

    print("\nForecasting complete!")
    print("Metrics:")
    print(metrics)
