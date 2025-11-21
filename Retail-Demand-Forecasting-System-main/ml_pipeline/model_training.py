"""
Model Training Module for Retail Demand Forecasting
===================================================
This module handles model training, evaluation, and prediction using:
- LightGBM (Gradient Boosting)
- Prophet (Facebook's time-series model)
- Ensemble methods
"""

import pandas as pd
import numpy as np

# Compatibility shim: NumPy 2.0 removed `find_common_type` which
# older versions of LightGBM call. Provide a thin replacement that
# maps to `numpy.result_type` so LightGBM can determine a common dtype.
try:
    _ = np.find_common_type  # type: ignore
except AttributeError:
    def find_common_type(array_types, scalar_types):
        # If no scalar types provided, include 0 to emulate previous
        # `find_common_type(..., [])` semantics.
        args = []
        for t in array_types:
            args.append(t)
        if scalar_types:
            args.extend(scalar_types)
        else:
            args.append(0)
        return np.result_type(*args)

    np.find_common_type = find_common_type  # type: ignore

import lightgbm as lgb
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    print("Warning: Prophet not available. Using LightGBM only.")
import pickle
import json
from typing import Dict, List, Tuple, Any
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')


class DemandForecaster:
    """
    Comprehensive demand forecasting model using LightGBM and Prophet.
    """
    
    def __init__(self, model_type: str = 'lightgbm'):
        """
        Initialize the forecaster.
        
        Args:
            model_type: 'lightgbm' or 'prophet'
        """
        if model_type == 'prophet' and not PROPHET_AVAILABLE:
            print("Prophet not available, defaulting to LightGBM")
            model_type = 'lightgbm'
        self.model_type = model_type
        self.models = {}  # Store models per product
        self.feature_importance = {}
        self.metrics = {}
        
    def train_lightgbm(self, X_train: pd.DataFrame, y_train: pd.Series,
                      X_val: pd.DataFrame = None, y_val: pd.Series = None,
                      params: Dict = None) -> lgb.Booster:
        """
        Train LightGBM model.
        
        Args:
            X_train: Training features
            y_train: Training target
            X_val: Validation features
            y_val: Validation target
            params: LightGBM parameters
            
        Returns:
            Trained LightGBM model
        """
        if params is None:
            params = {
                'objective': 'regression',
                'metric': 'rmse',
                'boosting_type': 'gbdt',
                'num_leaves': 31,
                'learning_rate': 0.05,
                'feature_fraction': 0.9,
                'bagging_fraction': 0.8,
                'bagging_freq': 5,
                'verbose': -1,
                'min_child_samples': 20,
                'reg_alpha': 0.1,
                'reg_lambda': 0.1
            }
        
        # Create datasets
        train_data = lgb.Dataset(X_train, label=y_train)
        valid_sets = [train_data]
        
        if X_val is not None and y_val is not None:
            val_data = lgb.Dataset(X_val, label=y_val, reference=train_data)
            valid_sets.append(val_data)
        
        # Train model
        model = lgb.train(
            params,
            train_data,
            num_boost_round=1000,
            valid_sets=valid_sets,
            callbacks=[
                lgb.early_stopping(stopping_rounds=50, verbose=False),
                lgb.log_evaluation(period=0)
            ]
        )
        
        return model
    
    def train_prophet(self, df: pd.DataFrame, date_col: str = 'date',
                     target_col: str = 'units_sold'):
        """
        Train Prophet model.
        
        Args:
            df: Dataframe with date and target columns
            date_col: Date column name
            target_col: Target column name
            
        Returns:
            Trained Prophet model
        """
        if not PROPHET_AVAILABLE:
            raise ImportError("Prophet is not installed. Please install it or use LightGBM.")
        
        # Prepare data for Prophet
        prophet_df = df[[date_col, target_col]].copy()
        prophet_df.columns = ['ds', 'y']
        
        # Initialize and fit Prophet
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            changepoint_prior_scale=0.05,
            seasonality_prior_scale=10.0
        )
        
        model.fit(prophet_df)
        return model
    
    def train_product_models(self, df: pd.DataFrame, 
                           feature_cols: List[str],
                           target_col: str = 'units_sold',
                           product_id_col: str = 'product_id',
                           date_col: str = 'date',
                           val_split: float = 0.2) -> Dict:
        """
        Train separate models for each product.
        
        Args:
            df: Input dataframe
            feature_cols: List of feature columns
            target_col: Target column name
            product_id_col: Product ID column
            date_col: Date column
            val_split: Validation split ratio
            
        Returns:
            Dictionary of metrics
        """
        products = df[product_id_col].unique()
        print(f"Training models for {len(products)} products...")
        
        all_metrics = []
        
        for i, product_id in enumerate(products, 1):
            product_df = df[df[product_id_col] == product_id].copy()
            
            # Skip products with insufficient data
            if len(product_df) < 60:
                continue
            
            # Sort by date
            product_df = product_df.sort_values(date_col)
            
            # Split train/validation
            val_size = int(len(product_df) * val_split)
            train_df = product_df.iloc[:-val_size]
            val_df = product_df.iloc[-val_size:]
            
            if len(train_df) < 30:
                continue
            
            # Prepare features
            X_train = train_df[feature_cols]
            y_train = train_df[target_col]
            X_val = val_df[feature_cols]
            y_val = val_df[target_col]
            
            if self.model_type == 'lightgbm':
                # Train LightGBM
                model = self.train_lightgbm(X_train, y_train, X_val, y_val)
                
                # Predictions
                train_pred = model.predict(X_train, num_iteration=model.best_iteration)
                val_pred = model.predict(X_val, num_iteration=model.best_iteration)
                
                # Feature importance
                self.feature_importance[product_id] = dict(zip(
                    feature_cols,
                    model.feature_importance(importance_type='gain')
                ))
                
            elif self.model_type == 'prophet':
                # Train Prophet
                model = self.train_prophet(train_df, date_col, target_col)
                
                # Predictions
                future_train = train_df[[date_col]].copy()
                future_train.columns = ['ds']
                train_pred = model.predict(future_train)['yhat'].values
                
                future_val = val_df[[date_col]].copy()
                future_val.columns = ['ds']
                val_pred = model.predict(future_val)['yhat'].values
            
            # Ensure non-negative predictions
            train_pred = np.maximum(train_pred, 0)
            val_pred = np.maximum(val_pred, 0)
            
            # Calculate metrics
            metrics = self.calculate_metrics(y_train, train_pred, y_val, val_pred)
            metrics['product_id'] = product_id
            metrics['n_samples'] = len(product_df)
            all_metrics.append(metrics)
            
            # Store model
            self.models[product_id] = model
            
            if i % 10 == 0:
                print(f"  Trained {i}/{len(products)} models...")
        
        # Store metrics
        self.metrics = pd.DataFrame(all_metrics)
        
        print(f"\n✓ Training complete! {len(self.models)} models trained.")
        print(f"Average Validation MAPE: {self.metrics['val_mape'].mean():.2f}%")
        print(f"Average Validation RMSE: {self.metrics['val_rmse'].mean():.2f}")
        
        return self.metrics
    
    def calculate_metrics(self, y_train: np.ndarray, train_pred: np.ndarray,
                         y_val: np.ndarray, val_pred: np.ndarray) -> Dict:
        """
        Calculate comprehensive evaluation metrics.
        
        Args:
            y_train: Training actuals
            train_pred: Training predictions
            y_val: Validation actuals
            val_pred: Validation predictions
            
        Returns:
            Dictionary of metrics
        """
        def mape(y_true, y_pred):
            """Mean Absolute Percentage Error"""
            y_true, y_pred = np.array(y_true), np.array(y_pred)
            mask = y_true != 0
            if mask.sum() == 0:
                return 0.0
            return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
        
        def wmape(y_true, y_pred):
            """Weighted Mean Absolute Percentage Error"""
            return np.sum(np.abs(y_true - y_pred)) / np.sum(np.abs(y_true)) * 100
        
        metrics = {
            'train_mae': mean_absolute_error(y_train, train_pred),
            'train_rmse': np.sqrt(mean_squared_error(y_train, train_pred)),
            'train_mape': mape(y_train, train_pred),
            'train_r2': r2_score(y_train, train_pred),
            'val_mae': mean_absolute_error(y_val, val_pred),
            'val_rmse': np.sqrt(mean_squared_error(y_val, val_pred)),
            'val_mape': mape(y_val, val_pred),
            'val_wmape': wmape(y_val, val_pred),
            'val_r2': r2_score(y_val, val_pred)
        }
        
        return metrics
    
    def predict(self, X: pd.DataFrame, product_id: str) -> np.ndarray:
        """
        Make predictions for a specific product.
        
        Args:
            X: Features dataframe
            product_id: Product identifier
            
        Returns:
            Predictions array
        """
        if product_id not in self.models:
            raise ValueError(f"No model found for product {product_id}")
        
        model = self.models[product_id]
        
        if self.model_type == 'lightgbm':
            predictions = model.predict(X, num_iteration=model.best_iteration)
        elif self.model_type == 'prophet':
            future_df = pd.DataFrame({'ds': X['date']})
            predictions = model.predict(future_df)['yhat'].values
        
        # Ensure non-negative
        predictions = np.maximum(predictions, 0)
        return predictions
    
    def forecast_future(self, product_id: str, days: int = 30,
                       last_features: pd.DataFrame = None) -> pd.DataFrame:
        """
        Forecast future demand for a product.
        
        Args:
            product_id: Product identifier
            days: Number of days to forecast
            last_features: Last known features (for LightGBM)
            
        Returns:
            Forecast dataframe
        """
        if product_id not in self.models:
            raise ValueError(f"No model found for product {product_id}")
        
        model = self.models[product_id]
        
        if self.model_type == 'prophet':
            future = model.make_future_dataframe(periods=days)
            forecast = model.predict(future)
            forecast = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(days)
            forecast.columns = ['date', 'forecast', 'lower_bound', 'upper_bound']
        else:
            # For LightGBM, we need historical features (simplified version)
            # In production, implement proper recursive forecasting
            if last_features is None:
                raise ValueError("last_features required for LightGBM forecasting")
            
            # Simple approach: replicate last features
            forecast_df = pd.DataFrame()
            forecast_df['forecast'] = [model.predict(last_features, 
                                                     num_iteration=model.best_iteration)[0]] * days
            forecast_df['date'] = pd.date_range(start=pd.Timestamp.now(), periods=days)
            forecast_df['lower_bound'] = forecast_df['forecast'] * 0.8
            forecast_df['upper_bound'] = forecast_df['forecast'] * 1.2
        
        # Ensure non-negative
        forecast['forecast'] = forecast['forecast'].clip(lower=0)
        forecast['lower_bound'] = forecast['lower_bound'].clip(lower=0)
        forecast['upper_bound'] = forecast['upper_bound'].clip(lower=0)
        
        return forecast
    
    def save_models(self, path: str):
        """
        Save all trained models.
        
        Args:
            path: Directory path to save models
        """
        import os
        os.makedirs(path, exist_ok=True)
        
        # Save models
        with open(f'{path}/models.pkl', 'wb') as f:
            pickle.dump(self.models, f)
        
        # Save metrics
        self.metrics.to_csv(f'{path}/metrics.csv', index=False)
        
        # Save feature importance
        with open(f'{path}/feature_importance.json', 'w') as f:
            json.dump(self.feature_importance, f, indent=2)
        
        # Save metadata
        metadata = {
            'model_type': self.model_type,
            'n_products': len(self.models),
            'avg_val_mape': float(self.metrics['val_mape'].mean()),
            'avg_val_rmse': float(self.metrics['val_rmse'].mean())
        }
        
        with open(f'{path}/metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✓ Models saved to {path}")
    
    def load_models(self, path: str):
        """
        Load trained models.
        
        Args:
            path: Directory path containing saved models
        """
        # Load models
        with open(f'{path}/models.pkl', 'rb') as f:
            self.models = pickle.load(f)
        
        # Load metrics
        self.metrics = pd.read_csv(f'{path}/metrics.csv')
        
        # Load feature importance
        with open(f'{path}/feature_importance.json', 'r') as f:
            self.feature_importance = json.load(f)
        
        # Load metadata
        with open(f'{path}/metadata.json', 'r') as f:
            metadata = json.load(f)
            self.model_type = metadata['model_type']
        
        print(f"✓ Models loaded from {path}")
        print(f"  Loaded {len(self.models)} models")


if __name__ == "__main__":
    print("Model Training Module")
    print("=" * 50)
    print("This module provides comprehensive model training for retail forecasting.")
    print("\nSupported Models:")
    print("- LightGBM (Gradient Boosting)")
    print("- Prophet (Time-series)")
    print("\nMetrics:")
    print("- MAPE (Mean Absolute Percentage Error)")
    print("- RMSE (Root Mean Squared Error)")
    print("- MAE (Mean Absolute Error)")
    print("- R² Score")
