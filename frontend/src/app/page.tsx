'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import axios from 'axios'
import dynamic from 'next/dynamic'

// Dynamically import Plotly to avoid SSR issues
const Plot = dynamic(() => import('react-plotly.js'), { ssr: false })

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface Stats {
  total_rows: number
  total_products: number
  date_range: {
    start: string
    end: string
    days: number
  }
  sales_summary: {
    total_units_sold: number
    avg_daily_units: number
    max_daily_units: number
  }
  revenue_summary?: {
    total_revenue: number
    avg_daily_revenue: number
  }
  top_products: { [key: string]: number }
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [uploadSuccess, setUploadSuccess] = useState(false)
  const [stats, setStats] = useState<Stats | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [forecasting, setForecasting] = useState(false)
  const [forecastComplete, setForecastComplete] = useState(false)
  const [forecastResults, setForecastResults] = useState<any>(null)

  // Check for existing data on load
  useEffect(() => {
    checkExistingData()
  }, [])

  const checkExistingData = async () => {
    try {
      const response = await axios.get(`${API_URL}/stats`)
      setStats(response.data)
      setUploadSuccess(true)
    } catch (err) {
      // No data uploaded yet
      console.log('No existing data')
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      setError(null)
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first')
      return
    }

    setUploading(true)
    setError(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await axios.post(`${API_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setUploadSuccess(true)
      
      // Fetch stats
      const statsResponse = await axios.get(`${API_URL}/stats`)
      setStats(statsResponse.data)
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  const handleForecast = async () => {
    setForecasting(true)
    setError(null)

    try {
      const response = await axios.post(`${API_URL}/forecast`, {
        forecast_days: 30,
        retrain: true
      })
      
      setForecastComplete(true)
      setForecastResults(response.data)
      console.log('Forecast results:', response.data)
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Forecasting failed')
    } finally {
      setForecasting(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-900">
              🛒 Retail Demand Forecasting System
            </h1>
            <nav className="flex space-x-4">
              <Link href="/" className="text-blue-600 hover:text-blue-800 font-medium">
                Home
              </Link>
              <Link href="/dashboard" className="text-gray-600 hover:text-gray-800 font-medium">
                Dashboard
              </Link>
              <Link href="/products" className="text-gray-600 hover:text-gray-800 font-medium">
                Products
              </Link>
              <Link href="/inventory" className="text-gray-600 hover:text-gray-800 font-medium">
                Inventory
              </Link>
            </nav>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-extrabold text-gray-900 mb-4">
            AI-Powered Demand Forecasting & Inventory Optimization
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            Upload your retail sales data and get 30-day forecasts with intelligent inventory recommendations
          </p>
        </div>

        {/* Upload Section */}
        {!uploadSuccess ? (
          <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
            <h3 className="text-2xl font-bold mb-6">Step 1: Upload Your Dataset</h3>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
              <input
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                className="hidden"
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className="cursor-pointer inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                📁 Choose CSV File
              </label>
              {file && (
                <p className="mt-4 text-gray-700">
                  Selected: <span className="font-semibold">{file.name}</span>
                </p>
              )}
              <button
                onClick={handleUpload}
                disabled={!file || uploading}
                className="ml-4 inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-green-600 hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {uploading ? '⏳ Uploading...' : '🚀 Upload & Process'}
              </button>
            </div>
            {error && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
                <p className="text-red-800">{error}</p>
              </div>
            )}
          </div>
        ) : (
          <>
            {/* Stats Dashboard */}
            <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
              <h3 className="text-2xl font-bold mb-6">📊 Dataset Overview</h3>
              {stats && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {/* Total Records */}
                  <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg p-6 text-white">
                    <h4 className="text-sm font-medium uppercase tracking-wide">Total Records</h4>
                    <p className="text-4xl font-bold mt-2">{stats.total_rows.toLocaleString()}</p>
                  </div>

                  {/* Total Products */}
                  <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-lg p-6 text-white">
                    <h4 className="text-sm font-medium uppercase tracking-wide">Total Products</h4>
                    <p className="text-4xl font-bold mt-2">{stats.total_products.toLocaleString()}</p>
                  </div>

                  {/* Total Sales */}
                  <div className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg p-6 text-white">
                    <h4 className="text-sm font-medium uppercase tracking-wide">Total Units Sold</h4>
                    <p className="text-4xl font-bold mt-2">
                      {stats.sales_summary.total_units_sold.toLocaleString()}
                    </p>
                  </div>

                  {/* Date Range */}
                  <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
                    <h4 className="text-sm font-medium text-gray-600 uppercase tracking-wide">Date Range</h4>
                    <p className="text-lg font-semibold mt-2">
                      {stats.date_range.start} to {stats.date_range.end}
                    </p>
                    <p className="text-sm text-gray-600">{stats.date_range.days} days</p>
                  </div>

                  {/* Average Daily Sales */}
                  <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
                    <h4 className="text-sm font-medium text-gray-600 uppercase tracking-wide">
                      Avg Daily Units
                    </h4>
                    <p className="text-lg font-semibold mt-2">
                      {stats.sales_summary.avg_daily_units.toFixed(2)}
                    </p>
                  </div>

                  {/* Max Daily Sales */}
                  <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
                    <h4 className="text-sm font-medium text-gray-600 uppercase tracking-wide">
                      Max Daily Units
                    </h4>
                    <p className="text-lg font-semibold mt-2">
                      {stats.sales_summary.max_daily_units.toLocaleString()}
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Forecast Section */}
            <div className="bg-white rounded-lg shadow-lg p-8">
              <h3 className="text-2xl font-bold mb-6">Step 2: Generate Forecasts</h3>
              <p className="text-gray-600 mb-6">
                Train machine learning models and generate 30-day demand forecasts for your products.
              </p>
              <button
                onClick={handleForecast}
                disabled={forecasting}
                className="inline-flex items-center px-8 py-4 border border-transparent text-lg font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {forecasting ? '🔄 Training Models...' : '🤖 Train & Forecast'}
              </button>
              {forecastComplete && (
                <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-md">
                  <p className="text-green-800 font-semibold">
                    ✓ Forecasting complete! Visit the Dashboard or Products page to view results.
                  </p>
                </div>
              )}
            </div>
          </>
        )}

        {/* Features Section */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-4xl mb-4">📈</div>
            <h3 className="text-xl font-bold mb-2">Demand Forecasting</h3>
            <p className="text-gray-600">
              30-day forecasts using LightGBM and Prophet models with 95% confidence intervals
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-4xl mb-4">📦</div>
            <h3 className="text-xl font-bold mb-2">Inventory Optimization</h3>
            <p className="text-gray-600">
              Calculate safety stock, reorder points, and EOQ with stockout predictions
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-4xl mb-4">💰</div>
            <h3 className="text-xl font-bold mb-2">Profit/Loss Analysis</h3>
            <p className="text-gray-600">
              Simulate scenarios and optimize inventory for maximum profitability
            </p>
          </div>
        </div>

        {/* Forecast Results Section */}
        {forecastResults && (
          <div className="mt-12 bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              📊 Forecast Results - Next 30 Days
            </h2>
            
            {/* Summary */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg p-6 text-white">
                <div className="text-sm opacity-90">Total Products Forecasted</div>
                <div className="text-4xl font-bold mt-2">{forecastResults.total_products || 0}</div>
              </div>
              <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-lg p-6 text-white">
                <div className="text-sm opacity-90">Forecast Period</div>
                <div className="text-4xl font-bold mt-2">{forecastResults.forecast_days || 30} Days</div>
              </div>
              <div className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg p-6 text-white">
                <div className="text-sm opacity-90">Total Forecasted Demand</div>
                <div className="text-4xl font-bold mt-2">
                  {forecastResults.forecasts?.reduce((sum: number, f: any) => 
                    sum + (f.forecast_values?.reduce((a: number, b: number) => a + b, 0) || 0), 0
                  ).toLocaleString() || 0}
                </div>
              </div>
            </div>

            {/* Product Forecast Table */}
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Product ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      30-Day Forecast
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Daily Average
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      MAPE (%)
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      R² Score
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {forecastResults.forecasts?.map((forecast: any, idx: number) => {
                    const totalDemand = forecast.forecast_values?.reduce((a: number, b: number) => a + b, 0) || 0
                    const avgDaily = totalDemand / (forecastResults.forecast_days || 30)
                    
                    return (
                      <tr key={idx} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {forecast.product_id}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          <span className="font-semibold text-blue-600">{Math.round(totalDemand).toLocaleString()}</span> units
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {Math.round(avgDaily).toLocaleString()} units/day
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          <span className={`font-semibold ${
                            (forecast.metrics?.val_mape || 0) < 10 ? 'text-green-600' : 
                            (forecast.metrics?.val_mape || 0) < 20 ? 'text-yellow-600' : 
                            'text-red-600'
                          }`}>
                            {forecast.metrics?.val_mape?.toFixed(2) || 'N/A'}%
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {forecast.metrics?.val_r2?.toFixed(3) || 'N/A'}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>

            <div className="mt-6 flex justify-center space-x-4">
              <Link 
                href="/products"
                className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 font-medium"
              >
                View Detailed Forecasts →
              </Link>
              <Link 
                href="/dashboard"
                className="bg-gray-600 text-white px-6 py-3 rounded-lg hover:bg-gray-700 font-medium"
              >
                Go to Dashboard →
              </Link>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white mt-12 border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-gray-600">
            Retail Demand Forecasting System v1.0.0 | Powered by LightGBM & Next.js
          </p>
        </div>
      </footer>
    </div>
  )
}
