import numpy_compat
import patch_recbole
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from routers import models, students, recommendations, graph, history
import traceback
import time
from dotenv import load_dotenv
import os

# Load environment variables from root .env file
env_path = os.path.join(os.path.dirname(__file__), '../../.env')
print(f"Loading .env from: {os.path.abspath(env_path)}")
print(f".env file exists: {os.path.exists(env_path)}")
load_dotenv(env_path)
print(f"MISTRALAI_API_KEY loaded: {bool(os.getenv('MISTRALAI_API_KEY'))}")
if os.getenv('MISTRALAI_API_KEY'):
    print(f"API Key starts with: {os.getenv('MISTRALAI_API_KEY')[:10]}...")

app = FastAPI(title="KG Recommender API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Debug middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    import sys
    start_time = time.time()
    print(f"DEBUG: Incoming request: {request.method} {request.url}")
    sys.stdout.flush()
    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        print(f"DEBUG: Response status: {response.status_code} (took {process_time:.2f}ms)")
        return response
    except Exception as e:
        print(f"DEBUG: UNHANDLED EXCEPTION in middleware: {e}")
        traceback.print_exc()
        raise e

# Include routers
app.include_router(models.router, prefix="/api/models", tags=["models"])
app.include_router(students.router, prefix="/api/students", tags=["students"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["recommendations"])
app.include_router(history.router, prefix="/api", tags=["history"])
app.include_router(graph.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to KG Recommender API"}
