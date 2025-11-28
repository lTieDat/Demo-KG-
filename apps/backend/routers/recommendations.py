from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
from dependencies import get_model_manager
from utils.recommendations import get_top_k_recommendations
from item_utils import get_item_display_info
from llm_explainer import MistralCloudExplainer, OllamaExplainer, LocalLLMExplainer
import os
import traceback

router = APIRouter()

class RecommendationRequest(BaseModel):
    student_id: int
    top_k: int = 10

class ExplainRequest(BaseModel):
    student_code: str
    recommendations: List[Dict]
    service: str = "mistral" # mistral, ollama, local
    model_name: Optional[str] = None
    api_key: Optional[str] = None
    ollama_url: Optional[str] = None

@router.get("/{student_id}")
async def get_recommendations(student_id: int, top_k: int = 10, manager = Depends(get_model_manager)):
    try:
        config, model, dataset, item_details = manager.get_model_components()
        
        if model is None:
            raise HTTPException(status_code=400, detail="Model not loaded")
            
        recs = get_top_k_recommendations(model, dataset, student_id, topk=top_k)
        
        formatted_recs = []
        for item_internal_id, item_external_id, score in recs:
            item_info = get_item_display_info(item_external_id, item_details)
            formatted_recs.append({
                "internal_id": item_internal_id,
                "external_id": item_external_id,
                "score": score,
                "info": item_info
            })
            
        return {"recommendations": formatted_recs}
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in get_recommendations: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/explain")
async def explain_recommendations(request: ExplainRequest):
    try:
        explanation = ""
        
        # Prepare rec data for explainer
        rec_data = []
        for rec in request.recommendations:
            # Handle different structures if needed, but assuming it matches what we return
            info = rec.get("info", {})
            rec_data.append({
                "title": info.get("title", "Unknown"),
                "topic": info.get("topic", "Unknown"),
                "difficulty": info.get("difficulty", "Unknown"),
                "score": rec.get("score", 0)
            })


        if request.service == "mistral":
            api_key = request.api_key or os.getenv("MISTRALAI_API_KEY")
            print(f"DEBUG: API key from request: {bool(request.api_key)}")
            print(f"DEBUG: API key from env: {bool(os.getenv('MISTRALAI_API_KEY'))}")
            print(f"DEBUG: Final API key: {bool(api_key)}")
            if not api_key:
                raise HTTPException(status_code=400, detail="Mistral API Key required")
            
            explainer = MistralCloudExplainer(api_key, request.model_name or "mistral-small-latest")
            explanation = explainer.explain_recommendations(request.student_code, rec_data)
            
        elif request.service == "ollama":
            explainer = OllamaExplainer(
                model_name=request.model_name or "mistral",
                base_url=request.ollama_url or "http://localhost:11434"
            )
            explanation = explainer.explain_recommendations(request.student_code, rec_data)
            
        else:
            explainer = LocalLLMExplainer()
            explanation = explainer.explain_recommendations(request.student_code, rec_data)
            
        return {"explanation": explanation}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
