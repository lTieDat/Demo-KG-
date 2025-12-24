import torch
import numpy as np

def get_top_k_recommendations(model, dataset, user_id, k=10, item_details=None):
    """
    Get top K recommendations for a specific user using the model and dataset.
    
    Args:
        model: Trained RecBole model
        dataset: RecBole dataset object
        user_id (str): External user ID
        k (int): Number of recommendations
        item_details (dict, optional): Mapping of item_id -> details for advanced filtering.
        
    Returns:
        list: List of item IDs (external)
        list: List of scores (if needed, or just items)
    """
    try:
        # Normalize user_id to string and remove .0 if it's a float-string
        user_id_str = str(user_id)
        if user_id_str.endswith('.0'):
            user_id_str = user_id_str[:-2]
            
        token_id = None
        
        # 1. Check if it's already a valid user_id token
        if user_id_str in dataset.field2token_id[dataset.uid_field]:
             token_id = user_id_str
        else:
             # 2. Try to map from student_id (e.g. B23DCCN010)
             user_feat = dataset.user_feat
             if user_feat is not None and 'student_id' in user_feat.columns:
                 # Normalize target ID for comparison
                 target_id = user_id_str.lower()
                 # Higher chance student_id is stored as string/token
                 mask = user_feat['student_id'].astype(str).str.lower() == target_id
                 matching_indices = mask[mask].index
                 
                 if len(matching_indices) > 0:
                     row_idx = matching_indices[0]
                     # Get the internal uid from this row
                     internal_uid_val = user_feat[dataset.uid_field][row_idx]
                     
                     # Map internal ID back to token
                     try:
                         if isinstance(internal_uid_val, (int, np.integer)):
                             token_id = dataset.id2token(dataset.uid_field, internal_uid_val)
                         else:
                             token_id = str(internal_uid_val)
                     except:
                         token_id = str(internal_uid_val)
        
        if not token_id:
            # Fallback or return empty
            return []
             
        uid_series = dataset.token2id(dataset.uid_field, [token_id])
        
        # Get internal user ID
        internal_uid = uid_series[0]
        
        # Use model.full_sort_predict() directly instead of full_sort_topk
        # This avoids the test_data=None error
        from recbole.data.interaction import Interaction
        # Convert to long tensor explicitly for indexing
        user_inter = Interaction({dataset.uid_field: torch.tensor([internal_uid], dtype=torch.long)})
        
        model.eval()
        with torch.no_grad():
            scores = model.full_sort_predict(user_inter.to(model.device))
            scores = scores.view(-1)
            
            # Mask items already in history to prevent re-recommendation
            # Get history indices
            try:
                # Use inter_matrix if available for speed, or manual mask
                # Manual mask on inter_feat
                mask = dataset.inter_feat[dataset.uid_field] == internal_uid
                history_iids = dataset.inter_feat[dataset.iid_field][mask]
                
                # Ensure history_iids is on the same device as scores
                if hasattr(history_iids, 'to'):
                    history_iids = history_iids.to(model.device)
                else:
                    history_iids = torch.tensor(history_iids).to(model.device)

                # Set scores of history items to -inf
                scores[history_iids] = -float('inf')
            except Exception as e:
                print(f"Warning: Could not mask history: {e}")
            
            # Get top k items
            # We get more than k just in case we need to filter post-hoc
            topk_scores, topk_iids = torch.topk(scores, min(k + 20, len(scores)))
        
        # Convert internal IDs back to external tokens
        external_item_ids = dataset.id2token(dataset.iid_field, topk_iids.cpu().numpy())
        
        # Double check filtering (Post-processing)
        # It is possible masking failed or didn't catch everything. 
        # So we explicitly filter against the history item set again.
        
        # Get history tokens for filtering
        hist_tokens = set()
        hist_names = set()
        
        if hasattr(history_iids, 'cpu'):
             # Convert to numpy first
             hist_tokens_np = dataset.id2token(dataset.iid_field, history_iids.cpu().numpy())
             # Force string conversion for robust comparison
             hist_tokens = set([str(x) for x in hist_tokens_np])
             
             if item_details:
                 for t in hist_tokens:
                     t_str = str(t)
                     info = item_details.get(t_str, {})
                     # Collect titles for duplicate checking
                     # Use 'title' or 'name'
                     name = info.get('title', info.get('name', ''))
                     if name:
                         hist_names.add(name.strip().lower())

             # Also print debug info if possible (will show in server logs)
             print(f"DEBUG: Recommendation Filtering - User {user_id} has {len(hist_tokens)} history items, {len(hist_names)} unique names.")

        final_recs = []
        for item in external_item_ids:
            item_str = str(item)
            
            # 1. ID Check
            if item_str in hist_tokens or item_str == '[PAD]':
                continue
                
            # 2. Name Check (if details are available)
            if item_details:
                info = item_details.get(item_str, {})
                name = info.get('title', info.get('name', ''))
                if name and name.strip().lower() in hist_names:
                    # Skip if name matches something in history
                    continue

            final_recs.append(item_str)
            if len(final_recs) == k:
                break
        
        return final_recs
        
    except Exception as e:
        print(f"Error getting recommendations: {e}")
        import traceback
        traceback.print_exc()
        return []

def get_recommendations_with_explanations(model, dataset, user_id, k=10, item_details=None):
    """
    Get recommendations enriched with item details.
    """
    rec_ids = get_top_k_recommendations(model, dataset, user_id, k, item_details=item_details)
    
    results = []
    if item_details:
        for i, iid in enumerate(rec_ids):
            details = item_details.get(str(iid), {})
            # Construct a rich object
            results.append({
                'internal_id': str(iid),
                'external_id': str(iid),
                'score': 0.99 - (i * 0.01),
                'info': {
                    'title': details.get('title', details.get('name', f'Bài tập {iid}')),
                    'topic': details.get('topic', details.get('type', 'Unknown')),
                    'difficulty': details.get('difficulty', details.get('level', 'Medium'))
                },
                'kg_explanation': {} 
            })
    else:
        # Minimal info
        for i, iid in enumerate(rec_ids):
            results.append({
                'internal_id': str(iid),
                'external_id': str(iid),
                'score': 0.99 - (i * 0.01),
                'info': {'title': f'Bài tập {iid}', 'topic': 'Unknown', 'difficulty': 'Medium'}
            })
            
    return results
