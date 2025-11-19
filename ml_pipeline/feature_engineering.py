"""
Feature Engineering Module for Retail Demand Forecasting
=========================================================
This module handles all feature engineering tasks including:
- Lag features (1, 7, 14, 30 days)
- Rolling window statistics (mean, std, min, max)
- Calendar features (day of week, month, quarter, holidays)
- Trend and seasonality features
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class FeatureEngineer:
    """
    Comprehensive feature engineering for time-series demand forecasting.
    """
    
    def __init__(self, date_col: str = 'date', target_col: str = 'units_sold', 
                 product_id_col: str = 'product_id'):
        """
        Initialize the feature engineer.
        
        Args:
            date_col: Name of the date column
            target_col: Name of the target variable (units sold)
            product_id_col: Name of the product identifier column
        """
        self.date_col = date_col
        self.target_col = target_col
        self.product_id_col = product_id_col
        
    def prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare the dataset with proper data types and sorting.
        
        Args:
            df: Input dataframe
            
        Returns:
            Prepared dataframe
        """
        df = df.copy()
        df[self.date_col] = pd.to_datetime(df[self.date_col])
        df = df.sort_values([self.product_id_col, self.date_col]).reset_index(drop=True)
        return df
    
    def create_lag_features(self, df: pd.DataFrame, 
                          lags: List[int] = [1, 7, 14, 30]) -> pd.DataFrame:
        """
        Create lag features for each product.
        
        Args:
            df: Input dataframe
            lags: List of lag periods
            
        Returns:
            Dataframe with lag features
        """
        df = df.copy()
        
        for lag in lags:
            df[f'lag_{lag}'] = df.groupby(self.product_id_col)[self.target_col].shift(lag)
        
        return df
    
    def create_rolling_features(self, df: pd.DataFrame, 
                               windows: List[int] = [7, 14, 30]) -> pd.DataFrame:
        """
        Create rolling window statistics.
        
        Args:
            df: Input dataframe
            windows: List of window sizes
            
        Returns:
            Dataframe with rolling features
        """
        df = df.copy()
        
        for window in windows:
            # Rolling mean
            df[f'ma_{window}'] = df.groupby(self.product_id_col)[self.target_col]\
                .rolling(window=window, min_periods=1).mean().reset_index(0, drop=True)
            
            # Rolling std
            df[f'std_{window}'] = df.groupby(self.product_id_col)[self.target_col]\
                .rolling(window=window, min_periods=1).std().reset_index(0, drop=True)
            
            # Rolling min
            df[f'min_{window}'] = df.groupby(self.product_id_col)[self.target_col]\
                .rolling(window=window, min_periods=1).min().reset_index(0, drop=True)
            
            # Rolling max
            df[f'max_{window}'] = df.groupby(self.product_id_col)[self.target_col]\
                .rolling(window=window, min_periods=1).max().reset_index(0, drop=True)
        
        return df
    
    def create_calendar_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create calendar-based features.
        
        Args:
            df: Input dataframe
            
        Returns:
            Dataframe with calendar features
        """
        df = df.copy()
        
        # Day of week (0=Monday, 6=Sunday)
        df['day_of_week'] = df[self.date_col].dt.dayofweek
        
        # Is weekend
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        
        # Day of month
        df['day_of_month'] = df[self.date_col].dt.day
        
        # Week of year
        df['week_of_year'] = df[self.date_col].dt.isocalendar().week
        
        # Month
        df['month'] = df[self.date_col].dt.month
        
        # Quarter
        df['quarter'] = df[self.date_col].dt.quarter
        
        # Year
        df['year'] = df[self.date_col].dt.year
        
        # Is month start/end
        df['is_month_start'] = df[self.date_col].dt.is_month_start.astype(int)
        df['is_month_end'] = df[self.date_col].dt.is_month_end.astype(int)
        
        # Cyclical encoding for month and day_of_week
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        df['dow_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['dow_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        
        return df
    
    def create_trend_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create trend and seasonality features.
        
        Args:
            df: Input dataframe
            
        Returns:
            Dataframe with trend features
        """
        df = df.copy()
        
        # Days since first sale for each product
        df['days_since_first'] = df.groupby(self.product_id_col)[self.date_col]\
            .transform(lambda x: (x - x.min()).dt.days)
        
        # Cumulative sum of sales
        df['cumsum_sales'] = df.groupby(self.product_id_col)[self.target_col].cumsum()
        
        # Growth rate (week over week)
        df['growth_7d'] = df.groupby(self.product_id_col)[self.target_col]\
            .pct_change(periods=7).fillna(0)
        
        # Exponential weighted mean
        df['ewm_7'] = df.groupby(self.product_id_col)[self.target_col]\
            .transform(lambda x: x.ewm(span=7, adjust=False).mean())
        
        df['ewm_30'] = df.groupby(self.product_id_col)[self.target_col]\
            .transform(lambda x: x.ewm(span=30, adjust=False).mean())
        
        return df
    
    def create_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create interaction features.
        
        Args:
            df: Input dataframe
            
        Returns:
            Dataframe with interaction features
        """
        df = df.copy()
        
        # Price-related features if price and revenue exist
        if 'price' in df.columns and 'revenue' in df.columns:
            df['price_per_unit'] = df['price']
            
            # Only create revenue_per_order if order_count exists
            if 'order_count' in df.columns:
                df['revenue_per_order'] = df['revenue'] / (df['order_count'] + 1)
        
        # Promo interaction with weekend
        if 'promo_flag' in df.columns and 'is_weekend' in df.columns:
            df['promo_weekend'] = df['promo_flag'] * df['is_weekend']
        elif 'promotion' in df.columns and 'is_weekend' in df.columns:
            df['promo_weekend'] = df['promotion'] * df['is_weekend']
        
        return df
    
    def engineer_all_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply all feature engineering steps.
        
        Args:
            df: Input dataframe
            
        Returns:
            Fully engineered dataframe
        """
        print("Starting feature engineering pipeline...")
        
        # Prepare data
        df = self.prepare_data(df)
        print(f"✓ Data prepared: {len(df)} rows")
        
        # Create calendar features
        df = self.create_calendar_features(df)
        print("✓ Calendar features created")
        
        # Create lag features
        df = self.create_lag_features(df)
        print("✓ Lag features created")
        
        # Create rolling features
        df = self.create_rolling_features(df)
        print("✓ Rolling window features created")
        
        # Create trend features
        df = self.create_trend_features(df)
        print("✓ Trend features created")
        
        # Create interaction features
        df = self.create_interaction_features(df)
        print("✓ Interaction features created")
        
        # Fill NaN values
        df = df.fillna(0)
        
        print(f"✓ Feature engineering complete! Total features: {len(df.columns)}")
        return df
    
    def get_feature_columns(self, df: pd.DataFrame) -> List[str]:
        """
        Get list of feature columns (excluding date, product_id, target).
        
        Args:
            df: Dataframe
            
        Returns:
            List of feature column names
        """
        exclude_cols = [self.date_col, self.product_id_col, self.target_col, 
                       'revenue', 'cogs_total', 'profit', 'order_category', 
                       'category', 'product_name', 'day_of_week']
        
        # Get all columns except excluded ones
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        # Filter to only numeric columns
        numeric_cols = df[feature_cols].select_dtypes(include=[np.number]).columns.tolist()
        
        return numeric_cols


def create_train_test_split(df: pd.DataFrame, 
                            test_days: int = 30,
                            product_id_col: str = 'product_id',
                            date_col: str = 'date') -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Create train/test split based on time.
    
    Args:
        df: Input dataframe
        test_days: Number of days for test set
        product_id_col: Product ID column name
        date_col: Date column name
        
    Returns:
        Tuple of (train_df, test_df)
    """
    df = df.sort_values([product_id_col, date_col])
    
    # Get the split date
    max_date = df[date_col].max()
    split_date = max_date - timedelta(days=test_days)
    
    train_df = df[df[date_col] <= split_date].copy()
    test_df = df[df[date_col] > split_date].copy()
    
    print(f"Train set: {len(train_df)} rows ({train_df[date_col].min()} to {train_df[date_col].max()})")
    print(f"Test set: {len(test_df)} rows ({test_df[date_col].min()} to {test_df[date_col].max()})")
    
    return train_df, test_df


if __name__ == "__main__":
    # Example usage
    print("Feature Engineering Module")
    print("=" * 50)
    print("This module provides comprehensive feature engineering for retail forecasting.")
    print("\nKey Features:")
    print("- Lag features (1, 7, 14, 30 days)")
    print("- Rolling statistics (mean, std, min, max)")
    print("- Calendar features (day, week, month, cyclical encoding)")
    print("- Trend and growth features")
    print("- Interaction features")
