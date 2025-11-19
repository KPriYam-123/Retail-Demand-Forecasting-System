"""
FastAPI Backend for Retail Demand Forecasting System
====================================================
This module provides REST API endpoints for:
- Dataset upload
- Demand forecasting
- Inventory optimization
- Product-level data
- Profit/Loss simulation
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import pandas as pd
import numpy as np
import json
import os
import sys
from datetime import datetime, timedelta
import pickle
import io

# Add project root directory to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from ml_pipeline.feature_engineering import FeatureEngineer, create_train_test_split
from ml_pipeline.model_training import DemandForecaster
from ml_pipeline.inventory_optimizer import InventoryOptimizer

# Initialize FastAPI app
app = FastAPI(
    title="Retail Demand Forecasting API",
    description="Production API for retail demand forecasting and inventory optimization",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for storing data and models
UPLOAD_DIR = "data/uploads"
MODEL_DIR = "saved_models"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

# In-memory storage (in production, use a database)
dataset_store = {}
model_store = {}
forecast_store = {}
inventory_store = {}


# Pydantic models for request/response
class ForecastRequest(BaseModel):
    product_ids: Optional[List[str]] = None
    forecast_days: int = 30
    retrain: bool = False


class InventoryRequest(BaseModel):
    product_id: str
    current_inventory: float
    unit_cost: float
    unit_price: float
    lead_time_days: int = 7


class ProfitLossRequest(BaseModel):
    product_id: str
    current_inventory: float
    unit_cost: float
    unit_price: float
    holding_cost_per_unit: float = 0.5
    stockout_cost_per_unit: float = 5.0


class UploadResponse(BaseModel):
    message: str
    filename: str
    rows: int
    columns: int
    products: int
    date_range: Dict[str, str]


class ForecastResponse(BaseModel):
    product_id: str
    forecast_days: int
    forecast_values: List[float]
    forecast_dates: List[str]
    lower_bound: List[float]
    upper_bound: List[float]
    metrics: Dict[str, float]


# Utility functions
def load_dataset(filename: str) -> pd.DataFrame:
    """Load dataset from uploads directory."""
    filepath = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Dataset not found")
    return pd.read_csv(filepath)


def save_dataset(df: pd.DataFrame, filename: str) -> str:
    """Save dataset to uploads directory."""
    filepath = os.path.join(UPLOAD_DIR, filename)
    df.to_csv(filepath, index=False)
    return filepath


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Retail Demand Forecasting API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/upload - Upload dataset",
            "forecast": "/forecast - Generate forecasts",
            "inventory": "/inventory - Get inventory recommendations",
            "product": "/product/{id} - Get product-specific data",
            "profit_loss": "/profit-loss - Simulate profit/loss",
            "stats": "/stats - Get dataset statistics"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models_loaded": len(model_store),
        "datasets_loaded": len(dataset_store)
    }


@app.post("/upload", response_model=UploadResponse)
async def upload_dataset(file: UploadFile = File(...)):
    """
    Upload and process retail dataset.
    
    Expected columns: date, product_id, units_sold, price, revenue, unit_cost, etc.
    """
    try:
        # Read uploaded file
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        
        # Validate required columns
        required_cols = ['date', 'product_id', 'units_sold']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {missing_cols}"
            )
        
        # Save dataset
        filename = f"dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        save_dataset(df, filename)
        
        # Store in memory
        dataset_store['current'] = df
        dataset_store['filename'] = filename
        
        # Get statistics
        df['date'] = pd.to_datetime(df['date'])
        stats = {
            "message": "Dataset uploaded successfully",
            "filename": filename,
            "rows": len(df),
            "columns": len(df.columns),
            "products": df['product_id'].nunique(),
            "date_range": {
                "start": df['date'].min().strftime('%Y-%m-%d'),
                "end": df['date'].max().strftime('%Y-%m-%d')
            }
        }
        
        return UploadResponse(**stats)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.get("/stats")
async def get_statistics():
    """Get dataset statistics and summary."""
    if 'current' not in dataset_store:
        raise HTTPException(status_code=404, detail="No dataset loaded. Please upload first.")
    
    df = dataset_store['current']
    df['date'] = pd.to_datetime(df['date'])
    
    # Overall statistics
    stats = {
        "total_rows": len(df),
        "total_products": df['product_id'].nunique(),
        "date_range": {
            "start": df['date'].min().strftime('%Y-%m-%d'),
            "end": df['date'].max().strftime('%Y-%m-%d'),
            "days": (df['date'].max() - df['date'].min()).days
        },
        "sales_summary": {
            "total_units_sold": float(df['units_sold'].sum()),
            "avg_daily_units": float(df['units_sold'].mean()),
            "max_daily_units": float(df['units_sold'].max())
        }
    }
    
    # Add revenue stats if available
    if 'revenue' in df.columns:
        stats["revenue_summary"] = {
            "total_revenue": float(df['revenue'].sum()),
            "avg_daily_revenue": float(df['revenue'].mean())
        }
    
    # Top products
    top_products = df.groupby('product_id')['units_sold'].sum()\
        .sort_values(ascending=False).head(10)
    stats["top_products"] = top_products.to_dict()
    
    return stats


@app.post("/forecast")
async def generate_forecast(request: ForecastRequest):
    """
    Generate demand forecasts for products.
    
    Args:
        product_ids: List of product IDs (if None, forecast all)
        forecast_days: Number of days to forecast (default 30)
        retrain: Whether to retrain models (default False)
    """
    if 'current' not in dataset_store:
        raise HTTPException(status_code=404, detail="No dataset loaded. Please upload first.")
    
    try:
        df = dataset_store['current'].copy()
        
        # Feature engineering
        print("Starting feature engineering...")
        fe = FeatureEngineer()
        df_featured = fe.engineer_all_features(df)
        
        # Get feature columns
        feature_cols = fe.get_feature_columns(df_featured)
        print(f"Feature columns: {len(feature_cols)}")
        
        # Determine products to forecast
        if request.product_ids:
            products = request.product_ids
        else:
            products = df['product_id'].unique()[:20]  # Limit to 20 for demo
        
        # Train or load models
        if request.retrain or 'forecaster' not in model_store:
            print("Training models...")
            forecaster = DemandForecaster(model_type='lightgbm')
            
            # Filter to selected products for faster training
            df_train = df_featured[df_featured['product_id'].isin(products)]
            
            # Train models
            metrics = forecaster.train_product_models(
                df_train,
                feature_cols=feature_cols,
                val_split=0.2
            )
            
            # Save models
            forecaster.save_models(MODEL_DIR)
            model_store['forecaster'] = forecaster
        else:
            forecaster = model_store['forecaster']
        
        # Generate forecasts
        forecasts = []
        for product_id in products:
            if product_id not in forecaster.models:
                continue
            
            # Get last known data for the product
            product_df = df_featured[df_featured['product_id'] == product_id]\
                .sort_values('date').tail(1)
            
            if len(product_df) == 0:
                continue
            
            # Simple forecast (in production, implement proper recursive forecasting)
            last_features = product_df[feature_cols]
            model = forecaster.models[product_id]
            
            # Generate 30-day forecast
            forecast_values = []
            for i in range(request.forecast_days):
                pred = model.predict(last_features, num_iteration=model.best_iteration)[0]
                forecast_values.append(max(0, pred))
            
            forecast_values = np.array(forecast_values)
            
            # Calculate confidence intervals (simplified)
            forecast_std = np.std(forecast_values) if len(forecast_values) > 1 else 1.0
            lower_bound = forecast_values - 1.96 * forecast_std
            upper_bound = forecast_values + 1.96 * forecast_std
            
            # Generate dates
            last_date = pd.to_datetime(product_df['date'].iloc[0])
            forecast_dates = [(last_date + timedelta(days=i+1)).strftime('%Y-%m-%d') 
                             for i in range(request.forecast_days)]
            
            # Get metrics
            product_metrics = forecaster.metrics[
                forecaster.metrics['product_id'] == product_id
            ].to_dict('records')[0] if len(forecaster.metrics) > 0 else {}
            
            forecast_data = {
                "product_id": product_id,
                "forecast_days": request.forecast_days,
                "forecast_values": forecast_values.tolist(),
                "forecast_dates": forecast_dates,
                "lower_bound": lower_bound.tolist(),
                "upper_bound": upper_bound.tolist(),
                "metrics": {
                    k: float(v) for k, v in product_metrics.items() 
                    if isinstance(v, (int, float))
                }
            }
            
            forecasts.append(forecast_data)
            
            # Store forecast
            forecast_store[product_id] = forecast_data
        
        return {
            "forecasts": forecasts,
            "total_products": len(forecasts),
            "forecast_days": request.forecast_days
        }
        
    except Exception as e:
        import traceback
        print(f"Forecast error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Forecast failed: {str(e)}")


@app.post("/inventory")
async def optimize_inventory(request: InventoryRequest):
    """
    Get inventory optimization recommendations for a product.
    """
    if request.product_id not in forecast_store:
        raise HTTPException(
            status_code=404,
            detail="Forecast not found. Please run /forecast first."
        )
    
    try:
        # Get forecast
        forecast_data = forecast_store[request.product_id]
        forecast_values = np.array(forecast_data['forecast_values'])
        
        # Initialize optimizer
        optimizer = InventoryOptimizer(service_level=0.95)
        
        # Calculate forecast std
        forecast_std = np.std(forecast_values)
        
        # Optimize
        optimization = optimizer.optimize_inventory(
            product_id=request.product_id,
            forecast_30d=forecast_values,
            forecast_std=forecast_std,
            current_inventory=request.current_inventory,
            unit_cost=request.unit_cost,
            unit_price=request.unit_price,
            lead_time_days=request.lead_time_days
        )
        
        # Store result
        inventory_store[request.product_id] = optimization
        
        return optimization
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


@app.get("/product/{product_id}")
async def get_product_data(product_id: str):
    """Get all data for a specific product."""
    if 'current' not in dataset_store:
        raise HTTPException(status_code=404, detail="No dataset loaded.")
    
    df = dataset_store['current']
    product_df = df[df['product_id'] == product_id].copy()
    
    if len(product_df) == 0:
        raise HTTPException(status_code=404, detail="Product not found.")
    
    # Sort by date
    product_df['date'] = pd.to_datetime(product_df['date'])
    product_df = product_df.sort_values('date')
    
    # Basic statistics
    stats = {
        "product_id": product_id,
        "total_records": len(product_df),
        "date_range": {
            "start": product_df['date'].min().strftime('%Y-%m-%d'),
            "end": product_df['date'].max().strftime('%Y-%m-%d')
        },
        "sales": {
            "total_units": float(product_df['units_sold'].sum()),
            "avg_daily_units": float(product_df['units_sold'].mean()),
            "max_daily_units": float(product_df['units_sold'].max()),
            "min_daily_units": float(product_df['units_sold'].min())
        }
    }
    
    # Add revenue if available
    if 'revenue' in product_df.columns:
        stats["revenue"] = {
            "total": float(product_df['revenue'].sum()),
            "avg_daily": float(product_df['revenue'].mean())
        }
    
    # Historical data (last 90 days)
    recent_data = product_df.tail(90)[['date', 'units_sold']].copy()
    recent_data['date'] = recent_data['date'].dt.strftime('%Y-%m-%d')
    stats["recent_history"] = recent_data.to_dict('records')
    
    # Add forecast if available
    if product_id in forecast_store:
        stats["forecast"] = forecast_store[product_id]
    
    # Add inventory optimization if available
    if product_id in inventory_store:
        stats["inventory_optimization"] = inventory_store[product_id]
    
    return stats


@app.post("/profit-loss")
async def simulate_profit_loss(request: ProfitLossRequest):
    """Simulate profit/loss scenarios."""
    if request.product_id not in forecast_store:
        raise HTTPException(
            status_code=404,
            detail="Forecast not found. Please run /forecast first."
        )
    
    try:
        # Get forecast
        forecast_data = forecast_store[request.product_id]
        forecast_values = np.array(forecast_data['forecast_values'])
        
        # Initialize optimizer
        optimizer = InventoryOptimizer()
        
        # Calculate P/L
        pl_result = optimizer.calculate_profit_loss(
            forecast=forecast_values,
            unit_cost=request.unit_cost,
            unit_price=request.unit_price,
            current_inventory=request.current_inventory,
            holding_cost_per_unit=request.holding_cost_per_unit,
            stockout_cost_per_unit=request.stockout_cost_per_unit
        )
        
        # Add product info
        pl_result['product_id'] = request.product_id
        pl_result['forecast_period_days'] = len(forecast_values)
        
        return pl_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"P/L simulation failed: {str(e)}")


@app.get("/products")
async def list_products(limit: int = Query(100, ge=1, le=1000)):
    """List all products in the dataset."""
    if 'current' not in dataset_store:
        raise HTTPException(status_code=404, detail="No dataset loaded.")
    
    df = dataset_store['current']
    
    # Get product summary
    product_summary = df.groupby('product_id').agg({
        'units_sold': ['sum', 'mean'],
        'date': ['min', 'max']
    }).reset_index()
    
    product_summary.columns = ['product_id', 'total_sales', 'avg_daily_sales', 
                               'first_date', 'last_date']
    product_summary = product_summary.sort_values('total_sales', ascending=False)
    
    # Convert to dict
    products = product_summary.head(limit).to_dict('records')
    
    # Convert dates to strings
    for p in products:
        p['first_date'] = pd.to_datetime(p['first_date']).strftime('%Y-%m-%d')
        p['last_date'] = pd.to_datetime(p['last_date']).strftime('%Y-%m-%d')
        p['total_sales'] = float(p['total_sales'])
        p['avg_daily_sales'] = float(p['avg_daily_sales'])
    
    return {
        "products": products,
        "total_count": len(product_summary),
        "returned_count": len(products)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
