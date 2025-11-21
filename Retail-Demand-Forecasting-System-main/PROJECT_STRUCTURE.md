# Retail Forecasting System - Project Structure

```
retail-forecasting-system/
│
├── README.md                          # Main documentation
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment variables template
├── docker-compose.yml                 # Docker configuration
│
├── ml_pipeline/                       # Machine Learning Pipeline
│   ├── __init__.py
│   ├── train.py                       # Main training script
│   ├── feature_engineering.py         # Feature engineering module
│   ├── model_training.py              # Model training (LightGBM, Prophet)
│   ├── inventory_optimizer.py         # Inventory optimization logic
│   └── models/                        # Saved trained models directory
│
├── backend/                           # FastAPI Backend
│   ├── Dockerfile                     # Backend Docker config
│   ├── saved_models/                  # Trained models storage
│   │   ├── models.pkl
│   │   ├── metrics.csv
│   │   ├── feature_importance.json
│   │   └── metadata.json
│   ├── data/                          # Data storage
│   │   └── uploads/                   # Uploaded datasets
│   └── app/                           # Application code
│       ├── __init__.py
│       ├── main.py                    # FastAPI app & endpoints
│       ├── routers/                   # API route handlers (optional)
│       ├── services/                  # Business logic (optional)
│       ├── models/                    # Pydantic models (optional)
│       └── utils/                     # Utility functions (optional)
│
├── frontend/                          # Next.js Frontend
│   ├── Dockerfile                     # Frontend Docker config
│   ├── package.json                   # Node dependencies
│   ├── next.config.js                 # Next.js configuration
│   ├── tsconfig.json                  # TypeScript configuration
│   ├── tailwind.config.js             # Tailwind CSS config
│   ├── postcss.config.js              # PostCSS config
│   └── src/
│       └── app/                       # Next.js App Router
│           ├── globals.css            # Global styles
│           ├── layout.tsx             # Root layout
│           ├── page.tsx               # Home page (upload & stats)
│           ├── dashboard/             # Dashboard page
│           │   └── page.tsx
│           ├── products/              # Products list page
│           │   └── page.tsx
│           ├── product/               # Product detail page
│           │   └── [id]/
│           │       └── page.tsx
│           └── inventory/             # Inventory optimization page
│               └── page.tsx
│
├── deployment/                        # Deployment configurations
│   ├── DEPLOYMENT.md                  # Deployment guide
│   ├── render.yaml                    # Render config (optional)
│   └── vercel.json                    # Vercel config (optional)
│
├── tests/                             # Unit & Integration tests
│   ├── test_features.py
│   ├── test_models.py
│   ├── test_api.py
│   └── test_inventory.py
│
└── notebooks/                         # Jupyter notebooks (optional)
    ├── EDA.ipynb                      # Exploratory data analysis
    ├── Feature_Engineering.ipynb      # Feature engineering experiments
    └── Model_Evaluation.ipynb         # Model performance analysis
```

---

## 📁 Key Directories Explained

### `ml_pipeline/`
Contains all machine learning code:
- Feature engineering with 40+ features
- Model training (LightGBM, Prophet)
- Inventory optimization algorithms
- Training script for batch processing

### `backend/`
FastAPI REST API:
- Upload endpoint for datasets
- Forecast generation endpoint
- Inventory optimization endpoint
- Product-specific data retrieval
- Profit/Loss simulation

### `frontend/`
Next.js dashboard:
- Modern React interface with TypeScript
- Tailwind CSS for styling
- Plotly for interactive charts
- Product search and filtering
- Real-time inventory recommendations

### `deployment/`
Production deployment configs:
- Docker setup
- Cloud platform configurations
- Deployment guides

---

## 🔧 How It Works

1. **Upload Dataset** → Stored in `backend/data/uploads/`
2. **Train Models** → Run `ml_pipeline/train.py` → Saves to `backend/saved_models/`
3. **Start Backend** → Loads models → Serves API at port 8000
4. **Start Frontend** → Connects to API → Serves UI at port 3000
5. **Generate Forecasts** → ML models predict → Results returned as JSON
6. **Optimize Inventory** → Algorithms calculate → Recommendations displayed

---

## 📊 Data Flow

```
CSV Upload → Feature Engineering → Model Training → Predictions → API Response → Frontend Display
```

---

## 🎯 Main Entry Points

- **Training**: `python ml_pipeline/train.py --data dataset.csv`
- **Backend**: `python backend/app/main.py`
- **Frontend**: `cd frontend && npm run dev`
- **Docker**: `docker-compose up`

---

**Total Files**: ~30 Python/TypeScript files + configs
**Total Lines**: ~5000+ lines of production code
**Documentation**: Complete README + API docs + deployment guide
