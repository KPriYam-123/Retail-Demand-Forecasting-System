"""
Inventory Optimization Module
==============================
This module handles inventory optimization including:
- Safety stock calculation (based on forecast uncertainty)
- Economic Order Quantity (EOQ)
- Reorder point calculation
- Stockout prediction
- Profit/Loss analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from scipy import stats


class InventoryOptimizer:
    """
    Comprehensive inventory optimization system.
    """
    
    def __init__(self, service_level: float = 0.95):
        """
        Initialize the inventory optimizer.
        
        Args:
            service_level: Target service level (default 95%)
        """
        self.service_level = service_level
        self.z_score = stats.norm.ppf(service_level)
        
    def calculate_safety_stock(self, forecast: np.ndarray,
                               forecast_std: float = None,
                               lead_time_days: int = 7) -> float:
        """
        Calculate safety stock based on forecast uncertainty.
        
        Args:
            forecast: Array of forecasted demand
            forecast_std: Standard deviation of forecast error
            lead_time_days: Lead time in days
            
        Returns:
            Safety stock quantity
        """
        if forecast_std is None:
            # Estimate from forecast variance
            forecast_std = np.std(forecast)
        
        # Safety stock = Z-score × std_dev × sqrt(lead_time)
        safety_stock = self.z_score * forecast_std * np.sqrt(lead_time_days)
        
        return max(0, safety_stock)
    
    def calculate_eoq(self, annual_demand: float, 
                     ordering_cost: float = 100,
                     holding_cost_rate: float = 0.25,
                     unit_cost: float = 10) -> float:
        """
        Calculate Economic Order Quantity (EOQ).
        
        Args:
            annual_demand: Expected annual demand
            ordering_cost: Fixed cost per order
            holding_cost_rate: Annual holding cost as % of unit cost
            unit_cost: Cost per unit
            
        Returns:
            Optimal order quantity
        """
        if annual_demand <= 0:
            return 0
        
        holding_cost = holding_cost_rate * unit_cost
        
        # EOQ formula: sqrt((2 × D × S) / H)
        # where D = annual demand, S = ordering cost, H = holding cost
        eoq = np.sqrt((2 * annual_demand * ordering_cost) / holding_cost)
        
        return max(1, eoq)
    
    def calculate_reorder_point(self, avg_daily_demand: float,
                               lead_time_days: int = 7,
                               safety_stock: float = 0) -> float:
        """
        Calculate reorder point.
        
        Args:
            avg_daily_demand: Average daily demand
            lead_time_days: Lead time in days
            safety_stock: Safety stock quantity
            
        Returns:
            Reorder point
        """
        # ROP = (Average daily demand × Lead time) + Safety stock
        reorder_point = (avg_daily_demand * lead_time_days) + safety_stock
        
        return max(0, reorder_point)
    
    def predict_stockout_day(self, current_inventory: float,
                           daily_forecast: np.ndarray,
                           current_date: datetime = None) -> Dict:
        """
        Predict when stockout will occur.
        
        Args:
            current_inventory: Current inventory level
            daily_forecast: Daily demand forecast
            current_date: Current date
            
        Returns:
            Dictionary with stockout prediction
        """
        if current_date is None:
            current_date = datetime.now()
        
        cumulative_demand = np.cumsum(daily_forecast)
        
        # Find first day when cumulative demand exceeds inventory
        stockout_idx = np.where(cumulative_demand >= current_inventory)[0]
        
        if len(stockout_idx) > 0:
            days_until_stockout = stockout_idx[0] + 1
            stockout_date = current_date + timedelta(days=int(days_until_stockout))
            will_stockout = True
        else:
            days_until_stockout = len(daily_forecast)
            stockout_date = current_date + timedelta(days=days_until_stockout)
            will_stockout = False
        
        return {
            'will_stockout': will_stockout,
            'days_until_stockout': int(days_until_stockout),
            'stockout_date': stockout_date,
            'remaining_inventory_end': float(current_inventory - cumulative_demand[-1])
        }
    
    def calculate_next_reorder_date(self, current_inventory: float,
                                   reorder_point: float,
                                   daily_forecast: np.ndarray,
                                   current_date: datetime = None) -> Dict:
        """
        Calculate when next reorder should happen.
        
        Args:
            current_inventory: Current inventory level
            reorder_point: Reorder point
            daily_forecast: Daily demand forecast
            current_date: Current date
            
        Returns:
            Dictionary with reorder information
        """
        if current_date is None:
            current_date = datetime.now()
        
        if current_inventory <= reorder_point:
            return {
                'should_reorder_now': True,
                'days_until_reorder': 0,
                'reorder_date': current_date
            }
        
        cumulative_demand = np.cumsum(daily_forecast)
        inventory_trajectory = current_inventory - cumulative_demand
        
        # Find when inventory hits reorder point
        reorder_idx = np.where(inventory_trajectory <= reorder_point)[0]
        
        if len(reorder_idx) > 0:
            days_until_reorder = reorder_idx[0] + 1
            reorder_date = current_date + timedelta(days=int(days_until_reorder))
            should_reorder = False
        else:
            days_until_reorder = len(daily_forecast)
            reorder_date = current_date + timedelta(days=days_until_reorder)
            should_reorder = False
        
        return {
            'should_reorder_now': should_reorder,
            'days_until_reorder': int(days_until_reorder),
            'reorder_date': reorder_date
        }
    
    def calculate_profit_loss(self, forecast: np.ndarray,
                            unit_cost: float,
                            unit_price: float,
                            current_inventory: float = 0,
                            holding_cost_per_unit: float = 0.5,
                            stockout_cost_per_unit: float = 5) -> Dict:
        """
        Calculate expected profit and loss.
        
        Args:
            forecast: Demand forecast
            unit_cost: Cost per unit
            unit_price: Selling price per unit
            current_inventory: Current inventory
            holding_cost_per_unit: Daily cost to hold one unit
            stockout_cost_per_unit: Cost per lost sale
            
        Returns:
            Dictionary with P/L metrics
        """
        total_demand = np.sum(forecast)
        
        # Revenue (assuming we can meet demand)
        units_sold = min(current_inventory, total_demand)
        revenue = units_sold * unit_price
        
        # Cost of goods sold
        cogs = units_sold * unit_cost
        
        # Holding cost
        avg_inventory = current_inventory / 2  # Simplified
        days = len(forecast)
        holding_cost = avg_inventory * holding_cost_per_unit * days
        
        # Stockout cost (lost sales)
        stockout_units = max(0, total_demand - current_inventory)
        stockout_cost = stockout_units * stockout_cost_per_unit
        
        # Gross profit
        gross_profit = revenue - cogs
        
        # Net profit (after costs)
        net_profit = gross_profit - holding_cost - stockout_cost
        
        # Profit margin
        profit_margin = (net_profit / revenue * 100) if revenue > 0 else 0
        
        return {
            'total_demand': float(total_demand),
            'units_sold': float(units_sold),
            'revenue': float(revenue),
            'cogs': float(cogs),
            'gross_profit': float(gross_profit),
            'holding_cost': float(holding_cost),
            'stockout_cost': float(stockout_cost),
            'stockout_units': float(stockout_units),
            'net_profit': float(net_profit),
            'profit_margin': float(profit_margin)
        }
    
    def optimize_inventory(self, product_id: str,
                          forecast_30d: np.ndarray,
                          forecast_std: float,
                          current_inventory: float,
                          unit_cost: float,
                          unit_price: float,
                          lead_time_days: int = 7,
                          ordering_cost: float = 100,
                          holding_cost_rate: float = 0.25) -> Dict:
        """
        Complete inventory optimization for a product.
        
        Args:
            product_id: Product identifier
            forecast_30d: 30-day demand forecast
            forecast_std: Forecast standard deviation
            current_inventory: Current inventory level
            unit_cost: Cost per unit
            unit_price: Selling price per unit
            lead_time_days: Lead time in days
            ordering_cost: Fixed cost per order
            holding_cost_rate: Annual holding cost rate
            
        Returns:
            Complete optimization results
        """
        # Calculate metrics
        avg_daily_demand = np.mean(forecast_30d)
        annual_demand = avg_daily_demand * 365
        
        # Safety stock
        safety_stock = self.calculate_safety_stock(
            forecast_30d, forecast_std, lead_time_days
        )
        
        # EOQ
        eoq = self.calculate_eoq(
            annual_demand, ordering_cost, holding_cost_rate, unit_cost
        )
        
        # Reorder point
        reorder_point = self.calculate_reorder_point(
            avg_daily_demand, lead_time_days, safety_stock
        )
        
        # Stockout prediction
        stockout_info = self.predict_stockout_day(
            current_inventory, forecast_30d
        )
        
        # Reorder date
        reorder_info = self.calculate_next_reorder_date(
            current_inventory, reorder_point, forecast_30d
        )
        
        # Profit/Loss
        pl_info = self.calculate_profit_loss(
            forecast_30d, unit_cost, unit_price, current_inventory
        )
        
        # Compile results
        optimization = {
            'product_id': product_id,
            'current_inventory': float(current_inventory),
            'avg_daily_demand': float(avg_daily_demand),
            'forecast_30d_total': float(np.sum(forecast_30d)),
            'safety_stock': float(safety_stock),
            'economic_order_quantity': float(eoq),
            'reorder_point': float(reorder_point),
            'recommended_order_quantity': float(eoq),
            'service_level': float(self.service_level * 100),
            **stockout_info,
            **reorder_info,
            **pl_info,
            'unit_cost': float(unit_cost),
            'unit_price': float(unit_price),
            'lead_time_days': int(lead_time_days)
        }
        
        # Convert datetime to string for JSON serialization
        if 'stockout_date' in optimization:
            optimization['stockout_date'] = optimization['stockout_date'].strftime('%Y-%m-%d')
        if 'reorder_date' in optimization:
            optimization['reorder_date'] = optimization['reorder_date'].strftime('%Y-%m-%d')
        
        return optimization
    
    def batch_optimize(self, forecasts_df: pd.DataFrame,
                      inventory_df: pd.DataFrame,
                      product_info_df: pd.DataFrame) -> pd.DataFrame:
        """
        Optimize inventory for multiple products.
        
        Args:
            forecasts_df: Dataframe with product forecasts
            inventory_df: Dataframe with current inventory levels
            product_info_df: Dataframe with product cost/price info
            
        Returns:
            Dataframe with optimization results
        """
        results = []
        
        for _, row in forecasts_df.iterrows():
            product_id = row['product_id']
            
            # Get current inventory
            inv_row = inventory_df[inventory_df['product_id'] == product_id]
            current_inventory = inv_row['current_inventory'].values[0] if len(inv_row) > 0 else 0
            
            # Get product info
            info_row = product_info_df[product_info_df['product_id'] == product_id]
            if len(info_row) == 0:
                continue
            
            unit_cost = info_row['unit_cost'].values[0]
            unit_price = info_row['unit_price'].values[0]
            
            # Get forecast
            forecast_30d = row['forecast_values']  # Assuming this is an array
            forecast_std = row['forecast_std']
            
            # Optimize
            optimization = self.optimize_inventory(
                product_id=product_id,
                forecast_30d=forecast_30d,
                forecast_std=forecast_std,
                current_inventory=current_inventory,
                unit_cost=unit_cost,
                unit_price=unit_price
            )
            
            results.append(optimization)
        
        return pd.DataFrame(results)


if __name__ == "__main__":
    print("Inventory Optimization Module")
    print("=" * 50)
    print("This module provides comprehensive inventory optimization.")
    print("\nKey Features:")
    print("- Safety stock calculation (95% service level)")
    print("- Economic Order Quantity (EOQ)")
    print("- Reorder point optimization")
    print("- Stockout prediction")
    print("- Profit/Loss analysis")
    print("\nFormulas:")
    print("- Safety Stock = Z-score × σ × √(Lead Time)")
    print("- EOQ = √((2 × D × S) / H)")
    print("- ROP = (Avg Daily Demand × Lead Time) + Safety Stock")
