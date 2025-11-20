"""
Model management API endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sys
import os

# Add parent directory to path to import utils
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from utils.models import get_compatible_checkpoints, load_trained_model, check_checkpoint_compatibility

router = APIRouter()

# Global state for loaded model
current_model = {
    "config": None,
    "model": None,
    "dataset": None,
    "model_path": None
}

class ModelLoadRequest(BaseModel):
    model_path: str

class ModelInfo(BaseModel):
    filename: str
    epoch: Any
    score: Any
    dataset: str
    embedding_size: Any
    user_count: Any
    entity_count: Any
    relation_count: Any
    compatible: bool

@router.get("/list")
async def list_models():
    """List all available models"""
    try:
        model_dir = os.path.join(os.path.dirname(__file__), "..", "..", "saved")
        compatible, incompatible = get_compatible_checkpoints(model_dir)
        
        return {
            "compatible": [
                {
                    "filename": filename,
                    "info": info
                }
                for filename, info in compatible
            ],
            "incompatible": [
                {
                    "filename": filename,
                    "info": info
                }
                for filename, info in incompatible
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/load")
async def load_model(request: ModelLoadRequest):
    """Load a specific model"""
    try:
        model_path = os.path.join(os.path.dirname(__file__), "..", "..", "saved", request.model_path)
        
        if not os.path.exists(model_path):
            raise HTTPException(status_code=404, detail="Model file not found")
        
        # Load model (this will take some time)
        config, model, dataset = load_trained_model(model_path)
        
        if config is None or model is None or dataset is None:
            raise HTTPException(status_code=500, detail="Failed to load model")
        
        # Store in global state
        current_model["config"] = config
        current_model["model"] = model
        current_model["dataset"] = dataset
        current_model["model_path"] = request.model_path
        
        # Get model info
        info = check_checkpoint_compatibility(model_path)
        
        return {
            "status": "success",
            "message": "Model loaded successfully",
            "model_info": info,
            "dataset_info": {
                "user_num": int(dataset.user_num),
                "item_num": int(dataset.item_num)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/current")
async def get_current_model():
    """Get currently loaded model info"""
    if current_model["model"] is None:
        raise HTTPException(status_code=404, detail="No model loaded")
    
    model_path = os.path.join(os.path.dirname(__file__), "..", "..", "saved", current_model["model_path"])
    info = check_checkpoint_compatibility(model_path)
    
    return {
        "model_info": info,
        "dataset_info": {
            "user_num": int(current_model["dataset"].user_num),
            "item_num": int(current_model["dataset"].item_num)
        }
    }

def get_loaded_model():
    """Helper to get loaded model (used by other routers)"""
    if current_model["model"] is None:
        raise HTTPException(status_code=400, detail="No model loaded. Please load a model first.")
    return current_model["config"], current_model["model"], current_model["dataset"]
