# KG Recommender System - Monorepo

A Knowledge Graph-based exercise recommendation system using Graph Neural Networks, built with FastAPI backend and React frontend.

## 📋 Prerequisites

Before you begin, ensure you have the following installed on your system:

### Required Software
- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 18+** - [Download Node.js](https://nodejs.org/)
- **npm 10+** - Comes bundled with Node.js
- **Git** - For cloning the repository

### Optional but Recommended
- **Python Virtual Environment** - `venv` or `conda` for isolated Python dependencies
- **VS Code** or your preferred IDE

### API Keys (Required for AI Features)
You'll need API keys for the AI explanation features:
- **Mistral AI API Key** - [Get API Key](https://console.mistral.ai/)
- **OpenAI API Key** (optional) - [Get API Key](https://platform.openai.com/)

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Demo-KG-
```

### 2. Environment Setup

#### Create Environment File
Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
MISTRAL_API_KEY=your_mistral_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # Optional
```

> [!IMPORTANT]
> Never commit your `.env` file to version control. It's already included in `.gitignore`.

---

## 📦 Installing Dependencies

This monorepo uses **Turborepo** to manage both backend and frontend applications.

### Backend Dependencies (Python)

#### Option 1: Using Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r apps/backend/requirements.txt
```

#### Option 2: Using Conda
```bash
# Create conda environment
conda create -n kg-recommender python=3.8

# Activate environment
conda activate kg-recommender

# Install dependencies
pip install -r apps/backend/requirements.txt
```

#### Option 3: Global Installation (Not Recommended)
```bash
pip install -r apps/backend/requirements.txt
```

#### Backend Dependencies Installed
The `requirements.txt` includes:
- **FastAPI** - Modern web framework for building APIs
- **Uvicorn** - ASGI server for FastAPI
- **RecBole** - Recommendation system library
- **PyTorch** - Deep learning framework
- **DGL** - Deep Graph Library for GNN
- **NumPy** (<2.0) - Numerical computing
- **Pandas** - Data manipulation
- **OpenAI** - OpenAI API client
- **Mistral AI** - Mistral AI API client
- **python-dotenv** - Environment variable management

---

### Frontend Dependencies (Node.js)

The frontend uses **npm workspaces** managed by Turborepo. Install all dependencies from the root:

```bash
# From the root directory
npm install
```

This single command will:
- Install root-level dependencies (Turborepo)
- Install frontend dependencies in `apps/frontend/`
- Set up the monorepo workspace

#### Frontend Dependencies Installed
Key packages include:
- **React 19** - UI library
- **Vite** - Fast build tool and dev server
- **React Router** - Client-side routing
- **Axios** - HTTP client for API calls
- **Shadcn UI** - UI component library (Radix UI + Tailwind CSS)
- **Lucide React** - Icon library
- **react-markdown** - Markdown rendering
- **remark-gfm** - GitHub Flavored Markdown support

---

## 🏃 Running the Application

### Development Mode (Both Backend + Frontend)

From the root directory, run:

```bash
npm run dev
```

This command uses **Turborepo** to run both applications concurrently:
- **Backend (FastAPI)**: [http://localhost:8000](http://localhost:8000)
  - API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
  - Alternative Docs: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Frontend (React)**: [http://localhost:5173](http://localhost:5173)

### Running Services Individually

#### Backend Only
```bash
cd apps/backend
uvicorn main:app --reload --port 8000
```

#### Frontend Only
```bash
cd apps/frontend
npm run dev
```

---

## 📁 Project Structure

```
Demo-KG-/
├── apps/
│   ├── backend/              # FastAPI application
│   │   ├── main.py          # Entry point
│   │   ├── routers/         # API endpoints
│   │   │   ├── models.py    # Model management
│   │   │   ├── recommendations.py
│   │   │   └── students.py
│   │   ├── requirements.txt # Python dependencies
│   │   └── .env            # Environment variables
│   │
│   └── frontend/            # React application
│       ├── src/
│       │   ├── pages/       # Page components
│       │   │   ├── Home.jsx
│       │   │   └── Dashboard.jsx
│       │   ├── components/  # Reusable components
│       │   ├── services/    # API client
│       │   └── main.jsx     # Entry point
│       ├── package.json     # Frontend dependencies
│       └── vite.config.js   # Vite configuration
│
├── dataset/                 # Shared dataset files
├── saved/                   # Trained ML models
├── .env                     # Environment variables (create from .env.example)
├── .env.example            # Environment template
├── package.json            # Root package (Turborepo)
├── turbo.json              # Turborepo configuration
└── README.md               # This file
```

---

## ✅ Verification Steps

1. **Open the Frontend**: Navigate to [http://localhost:5173](http://localhost:5173)
2. **Home Page**: You should see the "KG Recommender System" landing page
3. **Load a Model**: Select a compatible model from the list and click "Load Model"
4. **Dashboard**: After loading, you'll be redirected to the Dashboard
5. **Search Student**: Type a student code (e.g., "B21") in the search box
6. **View Recommendations**: Select a student to see personalized exercise recommendations
7. **AI Analysis**: Click "Get AI Explanation" to generate AI-powered insights

---

## 🛠️ Troubleshooting

### Backend Issues

#### Port Already in Use
```bash
# Find and kill process on port 8000 (Windows)
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# On macOS/Linux
lsof -ti:8000 | xargs kill -9
```

#### NumPy Version Conflicts
If you encounter NumPy errors, ensure you have NumPy < 2.0:
```bash
pip install "numpy<2.0" --force-reinstall
```

#### Missing API Keys
If AI explanations fail, check that your `.env` file contains valid API keys:
```bash
# Verify .env file exists
cat .env  # macOS/Linux
type .env  # Windows
```

### Frontend Issues

#### Node Modules Issues
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### Port 5173 Already in Use
Vite will automatically try the next available port (5174, 5175, etc.)

#### Build Errors
```bash
# Clear Vite cache
rm -rf apps/frontend/node_modules/.vite
npm run dev
```

---

## 🧪 Building for Production

### Build All
```bash
npm run build
```

### Build Backend
```bash
cd apps/backend
# Backend doesn't require a build step, just ensure dependencies are installed
```

### Build Frontend
```bash
cd apps/frontend
npm run build
# Output will be in apps/frontend/dist/
```

---

## 📚 Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **RecBole** - Recommendation algorithms
- **PyTorch** - Deep learning
- **DGL** - Graph Neural Networks
- **Mistral AI / OpenAI** - LLM for explanations

### Frontend
- **React 19** - UI framework
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Shadcn UI** - Component library
- **React Router** - Navigation
- **Axios** - HTTP client

### DevOps
- **Turborepo** - Monorepo build system
- **npm Workspaces** - Dependency management

---

## 📄 License

[Add your license information here]

## 🤝 Contributing

[Add contribution guidelines here]

## 📧 Support

For issues or questions, please [open an issue](link-to-issues) or contact the development team.

