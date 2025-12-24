from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import os
from dependencies import get_model_manager
from utils.models import get_compatible_checkpoints
from functools import lru_cache
from datetime import datetime, timedelta

router = APIRouter()

# Cache for model list
_model_cache = None
_cache_timestamp = None
CACHE_DURATION = timedelta(minutes=5)

class ModelLoadRequest(BaseModel):
    filename: str

def get_model_directory():
    """Get the path to the saved models directory"""
    model_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../saved"))
    if not os.path.exists(model_dir):
        model_dir = "saved"
    return model_dir

@router.get("/")
async def list_models():
    global _model_cache, _cache_timestamp
    
    # Check if cache is valid
    if _model_cache is not None and _cache_timestamp is not None:
        if datetime.now() - _cache_timestamp < CACHE_DURATION:
            return _model_cache
    
    model_dir = get_model_directory()
    
    if not os.path.exists(model_dir):
        return {"compatible": [], "incompatible": [], "error": "Model directory not found"}

    compatible, incompatible = get_compatible_checkpoints(model_dir)
    
    # Serialize for JSON
    compatible_list = [{"filename": f, "info": info} for f, info in compatible]
    incompatible_list = [{"filename": f, "info": info} for f, info in incompatible]
    
    result = {
        "compatible": compatible_list,
        "incompatible": incompatible_list
    }
    
    # Update cache
    _model_cache = result
    _cache_timestamp = datetime.now()
    
    return result

@router.post("/load")
async def load_model(request: ModelLoadRequest, manager = Depends(get_model_manager)):
    import sys
    print(f"ROUTER: Received load request for {request.filename}")
    sys.stdout.flush()
    model_dir = get_model_directory()
    model_path = os.path.join(model_dir, request.filename)
    
    if not os.path.exists(model_path):
        raise HTTPException(status_code=404, detail="Model file not found")
        
    success = manager.load_model(model_path)
    if success:
        return {"status": "success", "message": f"Model {request.filename} loaded successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to load model")
