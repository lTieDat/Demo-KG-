# KGCN Recommendation System - FastAPI Version

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install fastapi uvicorn python-multipart pydantic python-dotenv

# Run server
cd backend
python main.py
```

### Access
- Frontend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📖 Usage

1. **Load Model** - Select and load a trained model
2. **Choose Student** - Search or select from dropdown
3. **Generate Recommendations** - Click to get top-K recommendations
4. **AI Explanation** (Optional) - Get AI-powered insights

## 🔌 API Endpoints

- `GET /api/models/list` - List models
- `POST /api/models/load` - Load model
- `POST /api/recommendations/generate` - Generate recommendations
- `POST /api/explainer/generate` - AI explanation

## 🎨 Tech Stack

- **Backend**: FastAPI + Python
- **Frontend**: HTML + Tailwind CSS + Vanilla JS
- **ML**: PyTorch + RecBole + KGCN

## 📝 Features

✅ Modern responsive UI
✅ RESTful API
✅ Real-time search
✅ AI explanations (Mistral/Ollama)
✅ Toast notifications
