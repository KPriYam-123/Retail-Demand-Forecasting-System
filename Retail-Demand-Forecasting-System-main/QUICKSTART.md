# 🚀 Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites

✅ Python 3.9 or higher  
✅ Node.js 18 or higher  
✅ Your retail dataset CSV file  

---

## 🏃 Quick Setup (5 Steps)

### Step 1: Install Python Dependencies

```bash
# Navigate to project directory
cd retail-forecasting-system

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Train Your Models

```bash
# Train on your dataset (replace with your file path)
python ml_pipeline/train.py --data ../dataset_final.csv --output backend/saved_models --top-n 20

# This will:
# ✓ Load your data
# ✓ Engineer 40+ features
# ✓ Train LightGBM models
# ✓ Save models for API use
# Takes ~2-5 minutes for 20 products
```

### Step 3: Start the Backend API

```bash
# From project root
cd backend/app

# Run the server
python main.py

# You should see:
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

Keep this terminal open!

### Step 4: Install Frontend Dependencies

```bash
# Open NEW terminal
cd retail-forecasting-system/frontend

# Install packages
npm install

# Create environment file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

### Step 5: Start the Frontend

```bash
# Still in frontend directory
npm run dev

# You should see:
# ▲ Next.js 14.0.0
# - Local:        http://localhost:3000
```

---

## 🎉 You're Ready!

Open your browser to: **http://localhost:3000**

### What to Do Next:

1. **Upload Dataset**: Click "Choose CSV File" and upload your dataset
2. **Generate Forecasts**: Click "Train & Forecast" button
3. **Explore Products**: Navigate to Products page
4. **View Details**: Click on any product to see forecasts
5. **Optimize Inventory**: Enter parameters and get recommendations

---

## 📊 Sample Workflow

```
1. Home Page → Upload dataset_final.csv
   ↓
2. Click "Train & Forecast" → Wait ~2 minutes
   ↓
3. Go to "Products" → See all products
   ↓
4. Click on a product → View forecast chart
   ↓
5. Scroll down → Enter inventory parameters
   ↓
6. Click "Calculate" → Get recommendations!
```

---

## 🔧 Common Issues

**Issue**: `Module not found`  
**Fix**: Make sure you activated virtual environment and installed requirements

**Issue**: `Port 8000 already in use`  
**Fix**: Kill the process or change port in backend

**Issue**: `Frontend can't connect to API`  
**Fix**: Verify backend is running on port 8000

**Issue**: `Models not found`  
**Fix**: Run the training script first (Step 2)

---

## 🎯 Test with Sample Data

If you don't have data yet, the system expects CSV with these columns:
- `date` (YYYY-MM-DD)
- `product_id` (string)
- `units_sold` (integer)
- Optional: `price`, `revenue`, `unit_cost`, `promo_flag`

---

## 📱 What You'll See

### Home Page
- Upload interface
- Dataset statistics
- Train forecast button

### Products Page
- Searchable product list
- Sales statistics
- Quick view links

### Product Detail Page
- Historical sales chart
- 30-day forecast with confidence intervals
- Inventory optimization calculator
- Key metrics

### Inventory Page
- Batch optimization tool
- Multiple product analysis
- Export recommendations

---

## 💡 Pro Tips

1. **Start Small**: Train on top 20 products first (`--top-n 20`)
2. **Check Metrics**: Look for MAPE < 15% for good accuracy
3. **Adjust Parameters**: Tweak inventory costs based on your business
4. **Save Results**: Models are saved automatically
5. **Re-train**: Run training script again to update models

---

## 🆘 Need Help?

- Check the main [README.md](README.md) for detailed docs
- See [API Documentation](README.md#api-documentation)
- Review [Deployment Guide](deployment/DEPLOYMENT.md)
- Check logs in terminal for errors

---

## ✨ Next Steps

Once you're comfortable:
- Deploy to production (see DEPLOYMENT.md)
- Add more products to training
- Customize the frontend
- Integrate with your systems
- Set up monitoring

---

**Happy Forecasting! 📈**

Need more info? Check the full README.md
