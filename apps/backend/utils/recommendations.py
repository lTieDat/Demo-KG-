"""
Recommendation generation utilities with KG explanations
"""
import torch
from recbole.data.interaction import Interaction
from typing import List, Tuple, Dict, Optional

# Import KG explainer components
try:
    from kg_explainer import KGExplainer
    from attention_extractor import FastAttentionExtractor
    KG_AVAILABLE = True
except ImportError:
    KG_AVAILABLE = False


def get_top_k_recommendations(model, dataset, user_id, topk=10):
    """
    Lấy top-k recommendation cho user
    """
    try:
        model.eval()
        uid_field = dataset.uid_field
        iid_field = dataset.iid_field

        # Kiểm tra user_id hợp lệ
        if user_id >= dataset.user_num or user_id < 0:
            raise ValueError(
                f"User ID {user_id} không hợp lệ. Phải trong khoảng 0-{dataset.user_num-1}"
            )

        # Tạo input cho user
        user_inter = Interaction({uid_field: torch.tensor([user_id])})

        with torch.no_grad():
            scores = model.full_sort_predict(
                user_inter.to(model.device)
            )  # [1, num_items]
            scores = scores.view(-1)

            # Lấy top-k items
            topk_scores, topk_iids = torch.topk(scores, min(topk, len(scores)))

            # Convert về tên item nếu có mapping
            item_id2token = dataset.field2id_token[iid_field]

            results = []
            for i, iid in enumerate(topk_iids):
                item_internal_id = int(iid.item())

                # Xử lý item_id2token có thể là dict hoặc array
                if hasattr(item_id2token, "get"):
                    # Nếu là dictionary
                    item_external_id = item_id2token.get(
                        item_internal_id, f"Item_{item_internal_id}"
                    )
                elif hasattr(item_id2token, "__getitem__"):
                    # Nếu là array/list
                    try:
                        item_external_id = item_id2token[item_internal_id]
                    except (IndexError, KeyError):
                        item_external_id = f"Item_{item_internal_id}"
                else:
                    # Fallback
                    item_external_id = f"Item_{item_internal_id}"

                score = float(topk_scores[i].item())
                results.append((item_internal_id, item_external_id, score))

            return results

    except Exception as e:
        raise Exception(f"Lỗi trong get_top_k_recommendations: {str(e)}")


def get_recommendations_with_explanations(
    model,
    dataset,
    user_id: int,
    topk: int = 10,
    user_history: Optional[List[str]] = None,
    extract_attention: bool = False,
    item_details: Dict = None
) -> Tuple[List[Tuple], Dict]:
    """
    Lấy recommendations kèm theo KG explanations
    
    Args:
        model: KGIN model
        dataset: RecBole dataset
        user_id: User ID
        topk: Number of recommendations
        user_history: List of item IDs user has completed
        extract_attention: Whether to extract attention weights (slower)
    
    Returns:
        Tuple of (recommendations, explanation_data)
        - recommendations: List of (item_internal_id, item_external_id, score)
        - explanation_data: Dict with KG context and optional attention info
    """
    # Create explainer and extractor
    from enhanced_kg_explainer import create_enhanced_explainer
    from attention_extractor import AttentionExtractor
    from recbole.data.interaction import Interaction
    
    explainer = create_enhanced_explainer()
    extractor = AttentionExtractor(model, dataset)
    
    # 1. Get raw scores and items using RecBole directly
    model.eval()
    uid_field = dataset.uid_field
    iid_field = dataset.iid_field
    
    user_inter = Interaction({uid_field: torch.tensor([user_id])})
    with torch.no_grad():
        all_scores = model.full_sort_predict(user_inter.to(model.device)).view(-1)
        topk_scores, topk_iids_internal = torch.topk(all_scores, min(topk, len(all_scores)))
    
    # Convert internal IDs to external IDs
    item_id2token = dataset.field2id_token[iid_field]
    
    # 2. Extract attention if requested
    attention_weights = {}
    if extract_attention:
        # Pass internal user and item IDs to the extractor
        # Use our new extract_kgat_attention method if we want path-level, 
        # but for now extract_attention_for_user is fine as a fallback
        attention_info = extractor.extract_attention_for_user(user_id)
        attention_weights = attention_info.get('relation_attention', {})
    
    # 3. Generate explanations for top-K
    formatted_recommendations = []
    item_explanations = {}
    
    for i, item_internal_id_tensor in enumerate(topk_iids_internal):
        item_internal_id = int(item_internal_id_tensor.item())
        score = float(topk_scores[i].item())
        
        # Get external ID
        try:
            item_external_id = item_id2token[item_internal_id]
        except:
            item_external_id = str(item_internal_id)
            
        formatted_recommendations.append((item_internal_id, item_external_id, score))
        
        # Prepare item for explainer
        item_name = item_details.get(str(item_external_id), {}).get('name', str(item_external_id))
        
        # Enhanced explanation outputting Dict for router
        item_explanation_dict = explainer.explain_single_item(
            str(user_id), 
            str(item_external_id),
            user_history or [],
            attention_weights
        )
        
        item_explanations[str(item_external_id)] = {
            'kg_explanation': item_explanation_dict,
            'kg_context_text': item_explanation_dict['kg_context_text'],
            'score': score
        }
        
    explanation_data = {
        'kg_available': True,
        'item_explanations': item_explanations,
        'attention_info': attention_weights
    }
    
    return formatted_recommendations, explanation_data
        print("KG modules not available")
        return recommendations, explanation_data
    
    try:
        # Initialize KG explainer
        kg_explainer = KGExplainer()
        explanation_data['kg_available'] = True
    
        # Extract KG explanations for each recommended item
        for item_internal_id, item_external_id, score in recommendations:
            try:
                kg_explanation = kg_explainer.explain_item(
                    item_external_id,
                    user_history=user_history
                )
                
                # Format for LLM
                kg_context = kg_explainer.format_kg_context_for_llm(kg_explanation, item_details=item_details)
                
                explanation_data['item_explanations'][item_external_id] = {
                    'kg_explanation': kg_explanation,
                    'kg_context_text': kg_context,
                    'score': score
                }
            except Exception as e:
                print(f"Warning: Could not get KG explanation for {item_external_id}: {e}")
                continue
    
        # Optionally extract attention weights
        if extract_attention:
            try:
                attention_extractor = FastAttentionExtractor(model, dataset)
                attention_info = attention_extractor.extract_attention_for_user(
                    user_id,
                    enable_hooks=extract_attention
                )
                explanation_data['attention_info'] = attention_info
            except Exception as e:
                print(f"Warning: Could not extract attention weights: {e}")
    
    except Exception as e:
        print(f"Error initializing KG explainer: {e}")
        import traceback
        traceback.print_exc()
        explanation_data['kg_available'] = False
    
    return recommendations, explanation_data
