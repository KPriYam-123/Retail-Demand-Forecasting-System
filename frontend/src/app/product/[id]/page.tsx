'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import axios from 'axios'
import dynamic from 'next/dynamic'

const Plot = dynamic(() => import('react-plotly.js'), { ssr: false })

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function ProductDetailPage() {
  const params = useParams()
  const productId = params.id as string
  
  const [productData, setProductData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [inventoryParams, setInventoryParams] = useState({
    current_inventory: 100,
    unit_cost: 10,
    unit_price: 15,
    lead_time_days: 7
  })
  const [inventoryResult, setInventoryResult] = useState<any>(null)
  const [optimizing, setOptimizing] = useState(false)

  useEffect(() => {
    if (productId) {
      fetchProductData()
    }
  }, [productId])

  const fetchProductData = async () => {
    try {
      const response = await axios.get(`${API_URL}/product/${productId}`)
      setProductData(response.data)
    } catch (error) {
      console.error('Error fetching product data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleOptimizeInventory = async () => {
    setOptimizing(true)
    try {
      const response = await axios.post(`${API_URL}/inventory`, {
        product_id: productId,
        ...inventoryParams
      })
      setInventoryResult(response.data)
    } catch (error) {
      console.error('Error optimizing inventory:', error)
      alert('Failed to optimize inventory. Make sure forecast has been run first.')
    } finally {
      setOptimizing(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Loading product data...</p>
        </div>
      </div>
    )
  }

  if (!productData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Product Not Found</h2>
          <Link href="/products" className="text-blue-600 hover:text-blue-800">
            ← Back to Products
          </Link>
        </div>
      </div>
    )
  }

  // Prepare historical data for chart
  const historicalDates = productData.recent_history?.map((h: any) => h.date) || []
  const historicalSales = productData.recent_history?.map((h: any) => h.units_sold) || []

  // Prepare forecast data if available
  const forecastDates = productData.forecast?.forecast_dates || []
  const forecastValues = productData.forecast?.forecast_values || []
  const lowerBound = productData.forecast?.lower_bound || []
  const upperBound = productData.forecast?.upper_bound || []

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <Link href="/products" className="text-sm text-blue-600 hover:text-blue-800 mb-2 inline-block">
                ← Back to Products
              </Link>
              <h1 className="text-3xl font-bold text-gray-900">Product Details</h1>
              <p className="text-gray-600 mt-1">ID: {productId}</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-600 uppercase">Total Records</h3>
            <p className="text-3xl font-bold text-gray-900 mt-2">
              {productData.total_records}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-600 uppercase">Total Units Sold</h3>
            <p className="text-3xl font-bold text-blue-600 mt-2">
              {productData.sales.total_units.toFixed(0)}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-600 uppercase">Avg Daily Sales</h3>
            <p className="text-3xl font-bold text-green-600 mt-2">
              {productData.sales.avg_daily_units.toFixed(2)}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-medium text-gray-600 uppercase">Max Daily Sales</h3>
            <p className="text-3xl font-bold text-purple-600 mt-2">
              {productData.sales.max_daily_units.toFixed(0)}
            </p>
          </div>
        </div>

        {/* Forecast Chart */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-2xl font-bold mb-6">Sales History & Forecast</h2>
          {typeof window !== 'undefined' && (
            <Plot
              data={[
                {
                  x: historicalDates,
                  y: historicalSales,
                  type: 'scatter',
                  mode: 'lines',
                  name: 'Historical Sales',
                  line: { color: '#2563eb', width: 2 }
                },
                ...(forecastValues.length > 0 ? [{
                  x: forecastDates,
                  y: forecastValues,
                  type: 'scatter' as const,
                  mode: 'lines' as const,
                  name: 'Forecast',
                  line: { color: '#dc2626', width: 2, dash: 'dash' as const }
                }] : []),
                ...(upperBound.length > 0 ? [{
                  x: forecastDates,
                  y: upperBound,
                  type: 'scatter' as const,
                  mode: 'lines' as const,
                  name: 'Upper Bound (95%)',
                  line: { color: '#dc2626', width: 1, dash: 'dot' as const },
                  opacity: 0.3
                }] : []),
                ...(lowerBound.length > 0 ? [{
                  x: forecastDates,
                  y: lowerBound,
                  type: 'scatter' as const,
                  mode: 'lines' as const,
                  name: 'Lower Bound (95%)',
                  line: { color: '#dc2626', width: 1, dash: 'dot' as const },
                  opacity: 0.3,
                  fill: 'tonexty',
                  fillcolor: 'rgba(220, 38, 38, 0.1)'
                }] : [])
              ]}
              layout={{
                autosize: true,
                height: 400,
                xaxis: { title: 'Date' },
                yaxis: { title: 'Units Sold' },
                hovermode: 'x unified',
                showlegend: true,
                legend: { x: 0, y: 1 }
              }}
              config={{ responsive: true }}
              style={{ width: '100%' }}
            />
          )}
        </div>

        {/* Inventory Optimization */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-2xl font-bold mb-6">Inventory Optimization</h2>
          
          {/* Input Parameters */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Current Inventory
              </label>
              <input
                type="number"
                value={inventoryParams.current_inventory}
                onChange={(e) => setInventoryParams({
                  ...inventoryParams,
                  current_inventory: parseFloat(e.target.value)
                })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Unit Cost ($)
              </label>
              <input
                type="number"
                value={inventoryParams.unit_cost}
                onChange={(e) => setInventoryParams({
                  ...inventoryParams,
                  unit_cost: parseFloat(e.target.value)
                })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Unit Price ($)
              </label>
              <input
                type="number"
                value={inventoryParams.unit_price}
                onChange={(e) => setInventoryParams({
                  ...inventoryParams,
                  unit_price: parseFloat(e.target.value)
                })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Lead Time (days)
              </label>
              <input
                type="number"
                value={inventoryParams.lead_time_days}
                onChange={(e) => setInventoryParams({
                  ...inventoryParams,
                  lead_time_days: parseInt(e.target.value)
                })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
          </div>

          <button
            onClick={handleOptimizeInventory}
            disabled={optimizing}
            className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400"
          >
            {optimizing ? 'Optimizing...' : 'Calculate Optimization'}
          </button>

          {/* Results */}
          {inventoryResult && (
            <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="text-sm font-medium text-blue-900 uppercase">Safety Stock</h3>
                <p className="text-2xl font-bold text-blue-600 mt-2">
                  {inventoryResult.safety_stock.toFixed(0)} units
                </p>
              </div>
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h3 className="text-sm font-medium text-green-900 uppercase">Reorder Point</h3>
                <p className="text-2xl font-bold text-green-600 mt-2">
                  {inventoryResult.reorder_point.toFixed(0)} units
                </p>
              </div>
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                <h3 className="text-sm font-medium text-purple-900 uppercase">Order Quantity (EOQ)</h3>
                <p className="text-2xl font-bold text-purple-600 mt-2">
                  {inventoryResult.economic_order_quantity.toFixed(0)} units
                </p>
              </div>
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <h3 className="text-sm font-medium text-yellow-900 uppercase">Days Until Stockout</h3>
                <p className="text-2xl font-bold text-yellow-600 mt-2">
                  {inventoryResult.days_until_stockout} days
                </p>
              </div>
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <h3 className="text-sm font-medium text-red-900 uppercase">Stockout Date</h3>
                <p className="text-lg font-bold text-red-600 mt-2">
                  {inventoryResult.stockout_date}
                </p>
              </div>
              <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
                <h3 className="text-sm font-medium text-indigo-900 uppercase">Expected Profit</h3>
                <p className="text-2xl font-bold text-indigo-600 mt-2">
                  ${inventoryResult.net_profit.toFixed(2)}
                </p>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
