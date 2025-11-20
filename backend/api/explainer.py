"""
AI Explainer API endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sys
import os

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

try:
    from llm_explainer import MistralCloudExplainer, OllamaExplainer
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

from api.models import get_loaded_model
from utils.user_history import get_user_history_with_details
from item_utils import load_item_details

router = APIRouter()

class ExplainRequest(BaseModel):
    student_code: str
    user_id: int  # Added user_id to get history
    recommendations: List[Dict[str, Any]]
    service: str = "mistral"  # "mistral" or "ollama"
    model_name: str = "mistral-small-latest"  # For Mistral
    ollama_url: str = "http://localhost:11434"  # For Ollama

@router.post("/generate")
async def generate_explanation(request: ExplainRequest):
    """Generate AI explanation for recommendations"""
    if not LLM_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="LLM services not available. Install required packages."
        )
    
    try:
        # Get loaded model and dataset
        config, model, dataset = get_loaded_model()
        
        # Get user history
        item_details = load_item_details()
        user_history = get_user_history_with_details(
            dataset, 
            request.user_id, 
            item_details, 
            limit=5
        )
        
        # Prepare recommendation data
        rec_data = []
        for rec in request.recommendations:
            rec_data.append({
                "title": rec.get("title", ""),
                "topic": rec.get("topic", ""),
                "sub_topic": rec.get("sub_topic", ""),
                "difficulty": rec.get("difficulty", ""),
                "score": rec.get("score", 0)
            })
        
        # Generate explanation based on service
        if request.service == "mistral":
            api_key = os.getenv("MISTRALAI_API_KEY")
            if not api_key:
                raise HTTPException(
                    status_code=400,
                    detail="MISTRALAI_API_KEY not found in environment variables"
                )
            
            explainer = MistralCloudExplainer(api_key, request.model_name)
            explanation = explainer.explain_recommendations_with_history(
                request.student_code, 
                rec_data,
                user_history
            )
            
        elif request.service == "ollama":
            explainer = OllamaExplainer(request.model_name, request.ollama_url)
            explanation = explainer.explain_recommendations_with_history(
                request.student_code, 
                rec_data,
                user_history
            )
            
        else:
            raise HTTPException(status_code=400, detail="Invalid service. Use 'mistral' or 'ollama'")
        
        return {
            "explanation": explanation,
            "service": request.service,
            "model": request.model_name,
            "user_history_count": len(user_history)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        print(f"ERROR in explainer: {error_detail}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def check_health():
    """Check if LLM services are available"""
    return {
        "llm_available": LLM_AVAILABLE,
        "mistral_key_set": bool(os.getenv("MISTRALAI_API_KEY"))
    }
