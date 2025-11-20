"""
FastAPI main application
"""
import sys
import os

# Load .env from project root (one level up from backend/)
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path)

# Patch DGL's edge_subgraph to handle preserve_nodes parameter
import dgl
_original_edge_subgraph = dgl.DGLGraph.edge_subgraph

def patched_edge_subgraph(self, edges, *args, **kwargs):
    # Remove preserve_nodes if present (not supported in DGL 1.1.2)
    kwargs.pop('preserve_nodes', None)
    return _original_edge_subgraph(self, edges, *args, **kwargs)

dgl.DGLGraph.edge_subgraph = patched_edge_subgraph

# Monkey-patch to handle missing KGCN_UserKG class
from recbole.model.knowledge_aware_recommender import KGCN
import recbole.model.knowledge_aware_recommender.kgcn as kgcn_module

# Add KGCN_UserKG as an alias to KGCN in the kgcn module
kgcn_module.KGCN_UserKG = KGCN

# Create a fake kgcn_userkg module that points to the kgcn module
sys.modules['recbole.model.knowledge_aware_recommender.kgcn_userkg'] = kgcn_module

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from api import models, recommendations, explainer

# Create FastAPI app
app = FastAPI(
    title="KGCN Recommendation System API",
    description="Knowledge Graph Convolutional Network for Code Exercise Recommendations",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(models.router, prefix="/api/models", tags=["models"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["recommendations"])
app.include_router(explainer.router, prefix="/api/explainer", tags=["explainer"])

# Mount static files
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=os.path.join(frontend_path, "static")), name="static")

# Serve frontend
@app.get("/")
async def read_root():
    """Serve the main HTML page"""
    return FileResponse(os.path.join(frontend_path, "index.html"))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
