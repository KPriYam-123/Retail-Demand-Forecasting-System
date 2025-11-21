"use client"

import Link from 'next/link'
import { useEffect, useState } from 'react'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function DashboardPage() {
  const [modelsTrained, setModelsTrained] = useState<number | null>(null)
  const [avgMAPE, setAvgMAPE] = useState<number | null>(null)
  const [avgRMSE, setAvgRMSE] = useState<number | null>(null)

  useEffect(() => {
    fetchModelMetrics()
  }, [])

  const fetchModelMetrics = async () => {
    try {
      const res = await axios.get(`${API_URL}/model_metrics`)
      setModelsTrained(res.data.models_trained ?? 0)
      setAvgMAPE(res.data.avg_val_mape ?? 0)
      setAvgRMSE(res.data.avg_val_rmse ?? 0)
    } catch (err) {
      console.error('Failed to fetch model metrics', err)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <nav className="flex space-x-4">
              <Link href="/" className="text-gray-600 hover:text-gray-800 font-medium">
                Home
              </Link>
              <Link href="/dashboard" className="text-blue-600 hover:text-blue-800 font-medium">
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

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Advanced Analytics Dashboard
          </h2>
          <p className="text-gray-600 mb-6">
            This page can display aggregate forecasts, model performance metrics, and business KPIs.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h3 className="text-sm font-medium text-blue-900 uppercase">Models Trained</h3>
              <p className="text-4xl font-bold text-blue-600 mt-2">{modelsTrained ?? '-'}</p>
              <p className="text-sm text-blue-700 mt-2">Run forecast to train models</p>
            </div>
            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <h3 className="text-sm font-medium text-green-900 uppercase">Avg MAPE</h3>
              <p className="text-4xl font-bold text-green-600 mt-2">{avgMAPE !== null ? avgMAPE.toFixed(2) + '%' : '-'}</p>
              <p className="text-sm text-green-700 mt-2">Model accuracy metric</p>
            </div>
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
              <h3 className="text-sm font-medium text-purple-900 uppercase">Avg RMSE</h3>
              <p className="text-4xl font-bold text-purple-600 mt-2">{avgRMSE !== null ? avgRMSE.toFixed(2) : '-'}</p>
              <p className="text-sm text-purple-700 mt-2">Error metric</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
