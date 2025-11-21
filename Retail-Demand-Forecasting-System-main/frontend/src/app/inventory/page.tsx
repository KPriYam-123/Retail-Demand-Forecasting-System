'use client'

import { useState } from 'react'
import Link from 'next/link'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function InventoryPage() {
  const [products, setProducts] = useState<string[]>([])
  const [selectedProduct, setSelectedProduct] = useState('')
  const [params, setParams] = useState({
    current_inventory: 100,
    unit_cost: 10,
    unit_price: 15,
    lead_time_days: 7
  })
  const [results, setResults] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  const handleOptimize = async () => {
    if (!selectedProduct) {
      alert('Please enter a product ID')
      return
    }

    setLoading(true)
    try {
      const response = await axios.post(`${API_URL}/inventory`, {
        product_id: selectedProduct,
        ...params
      })
      setResults([response.data, ...results])
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Optimization failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-900">Inventory Optimization</h1>
            <nav className="flex space-x-4">
              <Link href="/" className="text-gray-600 hover:text-gray-800 font-medium">
                Home
              </Link>
              <Link href="/dashboard" className="text-gray-600 hover:text-gray-800 font-medium">
                Dashboard
              </Link>
              <Link href="/products" className="text-gray-600 hover:text-gray-800 font-medium">
                Products
              </Link>
              <Link href="/inventory" className="text-blue-600 hover:text-blue-800 font-medium">
                Inventory
              </Link>
            </nav>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-2xl font-bold mb-6">Calculate Inventory Recommendations</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Product ID
              </label>
              <input
                type="text"
                value={selectedProduct}
                onChange={(e) => setSelectedProduct(e.target.value)}
                placeholder="Enter product ID"
                className="w-full px-3 py-2 border border-gray-300 rounded-md bg-white text-gray-900 placeholder-gray-400"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Current Inventory
              </label>
              <input
                type="number"
                value={params.current_inventory}
                onChange={(e) => setParams({...params, current_inventory: parseFloat(e.target.value)})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md bg-white text-gray-900 placeholder-gray-400"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Unit Cost ($)
              </label>
              <input
                type="number"
                value={params.unit_cost}
                onChange={(e) => setParams({...params, unit_cost: parseFloat(e.target.value)})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md bg-white text-gray-900 placeholder-gray-400"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Unit Price ($)
              </label>
              <input
                type="number"
                value={params.unit_price}
                onChange={(e) => setParams({...params, unit_price: parseFloat(e.target.value)})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md bg-white text-gray-900 placeholder-gray-400"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Lead Time (days)
              </label>
              <input
                type="number"
                value={params.lead_time_days}
                onChange={(e) => setParams({...params, lead_time_days: parseInt(e.target.value)})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md bg-white text-gray-900 placeholder-gray-400"
              />
            </div>
          </div>

          <button
            onClick={handleOptimize}
            disabled={loading}
            className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400"
          >
            {loading ? 'Optimizing...' : 'Calculate Recommendations'}
          </button>
        </div>

        {/* Results */}
        {results.length > 0 && (
          <div className="space-y-6">
            {results.map((result, index) => (
              <div key={index} className="bg-white rounded-lg shadow p-6">
                <h3 className="text-xl font-bold mb-4">
                  Product: {result.product_id}
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <h4 className="text-xs font-medium text-blue-900 uppercase">Safety Stock</h4>
                    <p className="text-2xl font-bold text-blue-600 mt-1">
                      {result.safety_stock.toFixed(0)}
                    </p>
                  </div>
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <h4 className="text-xs font-medium text-green-900 uppercase">Reorder Point</h4>
                    <p className="text-2xl font-bold text-green-600 mt-1">
                      {result.reorder_point.toFixed(0)}
                    </p>
                  </div>
                  <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                    <h4 className="text-xs font-medium text-purple-900 uppercase">EOQ</h4>
                    <p className="text-2xl font-bold text-purple-600 mt-1">
                      {result.economic_order_quantity.toFixed(0)}
                    </p>
                  </div>
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <h4 className="text-xs font-medium text-yellow-900 uppercase">Days to Stockout</h4>
                    <p className="text-2xl font-bold text-yellow-600 mt-1">
                      {result.days_until_stockout}
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="border border-gray-200 rounded-lg p-4">
                    <h4 className="text-xs font-medium text-gray-600 uppercase">Expected Revenue</h4>
                    <p className="text-xl font-bold text-gray-900 mt-1">
                      ${result.revenue.toFixed(2)}
                    </p>
                  </div>
                  <div className="border border-gray-200 rounded-lg p-4">
                    <h4 className="text-xs font-medium text-gray-600 uppercase">Gross Profit</h4>
                    <p className="text-xl font-bold text-gray-900 mt-1">
                      ${result.gross_profit.toFixed(2)}
                    </p>
                  </div>
                  <div className="border border-gray-200 rounded-lg p-4">
                    <h4 className="text-xs font-medium text-gray-600 uppercase">Net Profit</h4>
                    <p className={`text-xl font-bold mt-1 ${result.net_profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      ${result.net_profit.toFixed(2)}
                    </p>
                  </div>
                </div>

                {result.should_reorder_now && (
                  <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-red-800 font-semibold">
                      ⚠️ Action Required: Reorder now! Inventory is below reorder point.
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
