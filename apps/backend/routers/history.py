from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict
from dependencies import get_model_manager

router = APIRouter()

@router.get("/{student_id}/history")
async def get_student_history(student_id: str, manager = Depends(get_model_manager)):
    """
    Get list of exercises the student has interacted with (done).
    """
    try:
        model, dataset, _ = manager.get_model()
        if not dataset:
             raise HTTPException(status_code=400, detail="Dataset not loaded")
             
        # Normalize student_id (e.g., 'B23...') to internal user_id
        # Similar logic to students.py search but assumes valid student_id passed from frontend
        
        user_id_str = str(student_id)
        token_id = None
        
        # 1. Map student_id to token
        # If dataset has token map, check direct
        if user_id_str in dataset.field2token_id[dataset.uid_field]:
             token_id = user_id_str
        else:
             # Check user_feat for student_id mapping
             user_feat = dataset.user_feat
             if 'student_id' in user_feat.columns:
                 mask = user_feat['student_id'] == user_id_str
                 if mask.any():
                     # Get the user token (user_id field)
                     idx = mask.idxmax() # First match
                     token_id = str(user_feat[dataset.uid_field][idx])
        
        if not token_id:
             # If strictly not found, return empty or 404. Let's return empty for robustness.
             return []
             
        # 2. Get internal UID
        uid = dataset.token2id(dataset.uid_field, [token_id])[0]
        
        # 3. Get interactions
        # inter_feat is the interaction table
        # We need to filter where user_id == uid
        # Optimized for RecBole dataset structure
        
        # Method A: Use uid2index if available (user-based interaction lists)
        # RecBole inter_feat is usually one big tensor.
        
        # Manual mask is safest across RecBole versions
        mask = dataset.inter_feat[dataset.uid_field] == uid
        
        # Get item indices
        iids = dataset.inter_feat[dataset.iid_field][mask]
        
        # Timestamp/Correctness if available
        # timestamps = dataset.inter_feat['timestamp'][mask]
        
        if hasattr(iids, 'numpy'): iids = iids.numpy()
        elif hasattr(iids, 'values'): iids = iids.values
        
        # 4. Map back to external Item info
        history_items = []
        item_details = manager.get_item_details() or {}
        
        for iid in iids:
            # Internal item ID -> External Token
            item_token = dataset.id2token(dataset.iid_field, iid)
            if item_token == '[PAD]': continue
            
            # Get metadata
            details = item_details.get(item_token, {})
            
            history_items.append({
                'id': item_token,
                'name': details.get('title', f'Bài tập {item_token}'),
                'topic': details.get('topic', 'Chưa phân loại'),
                'difficulty': details.get('difficulty', 'Unknown'),
                # 'timestamp': ...
            })
            
        # Reverse to show latest first? RecBole usually stores chronological
        return history_items[::-1]

    except Exception as e:
        print(f"Error fetching history: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
