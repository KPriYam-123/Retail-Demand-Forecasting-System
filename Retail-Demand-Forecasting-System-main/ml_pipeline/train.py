"""
Main Training Pipeline
======================
Complete training script for the retail forecasting system.
Run this script to train models on your dataset.
"""

import pandas as pd
import numpy as np
import os
import sys
import argparse
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml_pipeline.feature_engineering import FeatureEngineer, create_train_test_split
from ml_pipeline.model_training import DemandForecaster
from ml_pipeline.inventory_optimizer import InventoryOptimizer


def main(data_path: str, output_dir: str = 'saved_models', 
         model_type: str = 'lightgbm', top_n_products: int = None):
    """
    Main training pipeline.
    
    Args:
        data_path: Path to the dataset CSV file
        output_dir: Directory to save trained models
        model_type: 'lightgbm' or 'prophet'
        top_n_products: Number of top products to train (None = all)
    """
    print("=" * 70)
    print("RETAIL DEMAND FORECASTING - TRAINING PIPELINE")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Step 1: Load data
    print("Step 1: Loading dataset...")
    print("-" * 70)
    df = pd.read_csv(data_path)
    print(f"✓ Loaded {len(df):,} rows with {len(df.columns)} columns")
    print(f"✓ Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"✓ Products: {df['product_id'].nunique():,}")
    print()
    
    # Step 2: Feature Engineering
    print("Step 2: Feature Engineering...")
    print("-" * 70)
    fe = FeatureEngineer()
    df_featured = fe.engineer_all_features(df)
    feature_cols = fe.get_feature_columns(df_featured)
    print(f"✓ Created {len(feature_cols)} features")
    print()
    
    # Step 3: Select products (optional)
    if top_n_products:
        print(f"Step 3: Selecting top {top_n_products} products by sales...")
        print("-" * 70)
        top_products = df.groupby('product_id')['units_sold'].sum()\
            .sort_values(ascending=False).head(top_n_products).index.tolist()
        df_featured = df_featured[df_featured['product_id'].isin(top_products)]
        print(f"✓ Selected {len(top_products)} products")
        print()
    
    # Step 4: Train models
    print("Step 4: Training models...")
    print("-" * 70)
    forecaster = DemandForecaster(model_type=model_type)
    
    metrics = forecaster.train_product_models(
        df_featured,
        feature_cols=feature_cols,
        val_split=0.2
    )
    print()
    
    # Step 5: Save models
    print("Step 5: Saving models...")
    print("-" * 70)
    os.makedirs(output_dir, exist_ok=True)
    forecaster.save_models(output_dir)
    print()
    
    # Step 6: Display results
    print("=" * 70)
    print("TRAINING COMPLETE!")
    print("=" * 70)
    print(f"Models trained: {len(forecaster.models)}")
    print(f"Model type: {model_type}")
    print(f"Output directory: {output_dir}")
    print()
    print("Performance Summary:")
    print(f"  Average Validation MAPE: {metrics['val_mape'].mean():.2f}%")
    print(f"  Average Validation RMSE: {metrics['val_rmse'].mean():.2f}")
    print(f"  Average Validation MAE: {metrics['val_mae'].mean():.2f}")
    print(f"  Average Validation R²: {metrics['val_r2'].mean():.3f}")
    print()
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    return forecaster, metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Train retail demand forecasting models')
    parser.add_argument('--data', type=str, required=True,
                       help='Path to the dataset CSV file')
    parser.add_argument('--output', type=str, default='saved_models',
                       help='Output directory for models')
    parser.add_argument('--model', type=str, default='lightgbm',
                       choices=['lightgbm', 'prophet'],
                       help='Model type to train')
    parser.add_argument('--top-n', type=int, default=None,
                       help='Number of top products to train (None = all)')
    
    args = parser.parse_args()
    
    main(
        data_path=args.data,
        output_dir=args.output,
        model_type=args.model,
        top_n_products=args.top_n
    )
