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
    # Get basic recommendations
    recommendations = get_top_k_recommendations(model, dataset, user_id, topk)
    
    explanation_data = {
        'kg_available': False,
        'item_explanations': {},
        'attention_info': None
    }
    
    if not KG_AVAILABLE:
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
