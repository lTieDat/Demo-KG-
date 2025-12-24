from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from dependencies import get_model_manager
from utils.recommendations import get_recommendations_with_explanations
from kg_based_explainer import KGBasedExplainer
# from llm_explainer import MistralExplainer # If we have it

router = APIRouter()

class ExplanationRequest(BaseModel):
    user_id: str
    item_id: str
    model_type: str = "kgat" # or 'mistral'
    context: Optional[str] = None

@router.get("/{student_id}")
async def get_recommendations(student_id: str, k: int = 10, manager = Depends(get_model_manager)):
    """
    Get raw recommendations for a student.
    """
    model, dataset, _ = manager.get_model()
    if not model:
        raise HTTPException(status_code=400, detail="Model not loaded")
        
    item_details = manager.get_item_details()
    
    recs = get_recommendations_with_explanations(model, dataset, student_id, k, item_details)
    return recs

@router.get("/{student_id}/explained")
async def get_explained_recommendations(student_id: str, k: int = 5, manager = Depends(get_model_manager)):
    """
    Get recommendations with KG explanations.
    """
    model, dataset, _ = manager.get_model()
    if not model:
        raise HTTPException(status_code=400, detail="Model not loaded")
        
    item_details = manager.get_item_details()
    current_subject = manager.get_current_subject()
    
    # Get base recommendations
    recs = get_recommendations_with_explanations(model, dataset, student_id, k, item_details)
    
    # Enrich with explanations
    explainer = KGBasedExplainer(dataset_name=current_subject, model=model, dataset=dataset)
    
    for rec in recs:
        try:
            explanation = explainer.explain(student_id, rec['internal_id'])
            # Explanation might be complex object or just text
            # EnhancedKGExplainer usually returns dict or object with 'kg_context_text'
            if explanation:
                rec['kg_explanation'] = explanation
        except Exception as e:
            print(f"Error explaining item {rec['internal_id']}: {e}")
            
    return recs

@router.post("/explain")
async def explain_recommendation(request: ExplanationRequest, manager = Depends(get_model_manager)):
    """
    Generate specific explanation for a user-item pair.
    """
    current_subject = manager.get_current_subject()
    if request.model_type.lower() == 'mistral':
        # Placeholder for LLM/Mistral integration
        return {"explanation": "Mistral explanation not implemented in restoration."}
        
    model, dataset, _ = manager.get_model()
    explainer = KGBasedExplainer(dataset_name=current_subject, model=model, dataset=dataset)
    try:
        explanation = explainer.explain(request.user_id, request.item_id)
        return explanation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
