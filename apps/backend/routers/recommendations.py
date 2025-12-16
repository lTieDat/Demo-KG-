from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional, Dict
from dependencies import get_model_manager
from utils.recommendations import get_top_k_recommendations, get_recommendations_with_explanations
from item_utils import get_item_display_info
from llm_explainer import MistralCloudExplainer, OllamaExplainer, LocalLLMExplainer
from kg_based_explainer import KGBasedExplainer
from cache_manager import cache_user_recommendations, get_cache_stats
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


@router.get("/{student_id}/explained")
async def get_explained_recommendations(
    student_id: int,
    top_k: int = Query(10, ge=1, le=50),
    extract_attention: bool = Query(False),
    manager = Depends(get_model_manager)
):
    """
    Get recommendations with KG-based explanations
    
    Args:
        student_id: Student ID
        top_k: Number of recommendations (1-50)
        extract_attention: Whether to extract attention weights (slower)
    
    Returns:
        Recommendations with KG context for each item
    """
    try:
        config, model, dataset, item_details = manager.get_model_components()
        
        if model is None:
            raise HTTPException(status_code=400, detail="Model not loaded")
        # Get user history (last 5 completed items)
        user_history = []
        try:
            # Get internal user ID
            uid_field = dataset.uid_field
            iid_field = dataset.iid_field
            
            # Find the user's internal ID
            if hasattr(dataset, 'token2id') and uid_field in dataset.token2id:
                # Direct lookup if available
                user_internal_id = dataset.token2id[uid_field].get(str(student_id))
            else:
                # Fallback: iterate (slower but safer)
                user_internal_id = None
                # dataset.field2id_token[uid_field] is a list/array where index is internal_id
                tokens = dataset.field2id_token[uid_field]
                try:
                    # student_id comes in as int from URL path, but tokens are likely str
                    user_internal_id = list(tokens).index(str(student_id))
                except ValueError:
                    pass
            
            if user_internal_id is not None:
                # Get interactions using inter_feat
                # RecBole dataset.inter_feat is an Interaction object
                inter_feat = dataset.inter_feat
                uids = inter_feat[uid_field]
                iids = inter_feat[iid_field]
                
                # Filter interactions for this user
                # Note: this might be slow for massive datasets, but fine for demo
                mask = (uids == user_internal_id)
                user_item_indices = iids[mask]
                
                # Convert back to external item IDs
                item_tokens = dataset.field2id_token[iid_field]
                history_items = []
                for idx in user_item_indices[-5:]: # Get last 5
                    try:
                        token = item_tokens[int(idx)]
                        history_items.append(token)
                    except:
                        continue
                
                user_history = history_items
                print(f"DEBUG: Retrieved history for user {student_id}: {user_history}")
        
        except Exception as e:
            print(f"Warning: Could not retrieve user history: {e}")
            user_history = ['E1', 'E2', 'E3'] # Fallback

        
        # Get recommendations with KG explanations
        recommendations, explanation_data = get_recommendations_with_explanations(
            model=model,
            dataset=dataset,
            user_id=student_id,
            topk=top_k,
            user_history=user_history,
            extract_attention=extract_attention,
            item_details=item_details
        )
        
        # Format response with item details and KG context
        formatted_recs = []
        for item_internal_id, item_external_id, score in recommendations:
            item_info = get_item_display_info(item_external_id, item_details)
            
            # Get KG explanation for this item
            kg_explanation = None
            if explanation_data['kg_available'] and item_external_id in explanation_data['item_explanations']:
                kg_exp_data = explanation_data['item_explanations'][item_external_id]
                kg_explanation = {
                    'metadata': kg_exp_data['kg_explanation']['metadata'],
                    'shared_entities': kg_exp_data['kg_explanation']['shared_entities'],
                    'paths_from_history': kg_exp_data['kg_explanation']['paths_from_history'],
                    'kg_context_text': kg_exp_data['kg_context_text']
                }
            
            formatted_recs.append({
                "internal_id": item_internal_id,
                "external_id": item_external_id,
                "score": score,
                "info": item_info,
                "kg_explanation": kg_explanation
            })
        
        return {
            "student_id": student_id,
            "recommendations": formatted_recs,
            "kg_available": explanation_data.get('kg_available', False) if explanation_data else False,
            "attention_available": False  # Always false for now, can be enabled later
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in get_explained_recommendations: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/cache/stats")
async def get_cache_statistics():
    """Get cache statistics for monitoring"""
    return get_cache_stats()

@router.post("/explain")
async def explain_recommendations(request: ExplainRequest):
    try:
        # Prepare rec data and extract KG explanations
        rec_data = []
        kg_explanation_data = []  # Full KG explanation objects
        
        for rec in request.recommendations:
            info = rec.get("info", {})
            rec_data.append({
                "title": info.get("title", "Unknown"),
                "topic": info.get("topic", "Unknown"),
                "difficulty": info.get("difficulty", "Unknown"),
                "score": rec.get("score", 0)
            })
            
            # Extract full KG explanation object
            kg_exp = rec.get("kg_explanation")
            if kg_exp:
                kg_explanation_data.append(kg_exp)
            else:
                kg_explanation_data.append(None)

        # Use KG-based explainer by default (no LLM needed!)
        if request.service == "kg" or not request.service or request.service == "local":
            kg_explainer = KGBasedExplainer()
            explanation = kg_explainer.explain_recommendations(
                student_code=request.student_code,
                recommendations=rec_data,
                kg_contexts=kg_explanation_data
            )
            
        elif request.service == "mistral":
            # LLM enhancement with KG context
            api_key = request.api_key or os.getenv("MISTRALAI_API_KEY")
            if not api_key:
                raise HTTPException(status_code=400, detail="Mistral API Key required")
            
            # Combine KG contexts for LLM
            combined_kg_context = None
            if kg_explanation_data:
                kg_texts = [kg.get("kg_context_text", "") for kg in kg_explanation_data if kg]
                if kg_texts:
                    combined_kg_context = "\n\n".join([f"Bài {i+1}:\n{ctx}" for i, ctx in enumerate(kg_texts)])
            
            explainer = MistralCloudExplainer(api_key, request.model_name or "mistral-small-latest")
            explanation = explainer.explain_recommendations(
                request.student_code, 
                rec_data,
                kg_context=combined_kg_context
            )
            
        elif request.service == "ollama":
            # LLM enhancement with KG context
            combined_kg_context = None
            if kg_explanation_data:
                kg_texts = [kg.get("kg_context_text", "") for kg in kg_explanation_data if kg]
                if kg_texts:
                    combined_kg_context = "\n\n".join([f"Bài {i+1}:\n{ctx}" for i, ctx in enumerate(kg_texts)])
            
            explainer = OllamaExplainer(
                model_name=request.model_name or "mistral",
                base_url=request.ollama_url or "http://localhost:11434"
            )
            explanation = explainer.explain_recommendations(
                request.student_code, 
                rec_data,
                kg_context=combined_kg_context
            )
        else:
            # Default to KG-based
            kg_explainer = KGBasedExplainer()
            explanation = kg_explainer.explain_recommendations(
                student_code=request.student_code,
                recommendations=rec_data,
                kg_contexts=kg_explanation_data
            )
            
        return {"explanation": explanation}
        
    except Exception as e:
        print(f"Error in explain_recommendations: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
