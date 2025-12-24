import sys
import os
import sys
import os

# Add current dir to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dependencies import get_model_manager_instance
from utils.recommendations import get_top_k_recommendations

def test_repro():
    print("Initializing Model Manager...")
    manager = get_model_manager_instance()
    # Force load 'cpp' or 'algorithm' depending on environment, let's assume 'cpp' as default or try to detect
    # The default manager might lazy load.
    
    # We need to ensure the correct dataset is loaded. The user's screenshot showed "Lê Khải Hoàn" which looks like a student name.
    # The screenshot had "SỐ LẦN XUẤT HIỆN" (ID 97).
    
    print("Loading Model...")
    model, dataset, _ = manager.get_model()
    
    if not model:
        print("Model failed to load.")
        return

    # User from screenshot
    student_id = "B23DCCN031" 
    target_item_name = "SẮP XẾP XEN KẼ - 2"
    
    print(f"\n--- Diagnosing User: {student_id} ---")
    
    # 1. Check ID Mapping Logic (Simulate logic from utils/recommendations.py)
    user_id_str = str(student_id)
    token_id = None
    
    # Check direct
    if user_id_str in dataset.field2token_id[dataset.uid_field]:
        print(f"Direct match found in field2token_id: {user_id_str}")
        token_id = user_id_str
    else:
        print("No direct match. Checking user_feat for 'student_id'...")
        user_feat = dataset.user_feat
        if user_feat is not None and 'student_id' in user_feat.columns:
            target_id = user_id_str.lower()
            mask = user_feat['student_id'].astype(str).str.lower() == target_id
            matching_indices = mask[mask].index
            
            if len(matching_indices) > 0:
                print(f"Found {len(matching_indices)} match(es) in user_feat.")
                row_idx = matching_indices[0]
                internal_uid_val = user_feat[dataset.uid_field][row_idx]
                
                try:
                    if isinstance(internal_uid_val, (int, np.integer)):
                        token_id = dataset.id2token(dataset.uid_field, internal_uid_val)
                    else:
                        token_id = str(internal_uid_val)
                except:
                    token_id = str(internal_uid_val)
                
                print(f"Mapped to Token ID: {token_id}")
            else:
                print("No match found in user_feat['student_id'].")
        else:
            print("user_feat is None or has no 'student_id' column.")
            
    if not token_id:
        print("CRITICAL: Could not resolve student_id to token_id.")
        return

    # 2. Check History
    uid_series = dataset.token2id(dataset.uid_field, [token_id])
    internal_uid = uid_series[0]
    
    mask = dataset.inter_feat[dataset.uid_field] == internal_uid
    history_iids = dataset.inter_feat[dataset.iid_field][mask]
    
    print(f"History Item Count: {len(history_iids)}")
    
    history_names = set()
    item_details = manager.get_item_details() or {}
    
    # Get external history IDs
    if len(history_iids) > 0:
        if hasattr(history_iids, 'cpu'): history_iids = history_iids.cpu()
        hist_tokens = dataset.id2token(dataset.iid_field, history_iids)
        print(f"Sample History Items (first 5): {hist_tokens[:5]}")
        hist_set = set([str(x) for x in hist_tokens])
        
        # Check names
        for t in hist_set:
            name = item_details.get(str(t), {}).get('title', '').upper()
            history_names.add(name)
            if name == target_item_name.upper():
                print(f"FOUND IN HISTORY: ID={t}, Name={name}")
    else:
        hist_set = set()
        print("WARNING: History is empty for this user!")

    # 3. Get Recommendations
    print("\n--- Getting Recommendations ---")
    recs = get_top_k_recommendations(model, dataset, student_id, k=10)
    print(f"Recommendations IDs: {recs}")
    
    # 4. Check Overlap
    print("\n--- Checking for Overlaps ---")
    for r in recs:
        r_str = str(r)
        r_name = item_details.get(r_str, {}).get('title', '').upper()
        
        print(f"Rec Item: {r_str} | Name: {r_name}")
        
        if r_str in hist_set:
             print(f"  -> CRITICAL FAIL: ID {r_str} is in history set!")
        
        if r_name in history_names:
             print(f"  -> NAME CLASH: Name '{r_name}' is already in user history under a different ID?")
             
    print("\nDone.")

if __name__ == "__main__":
    test_repro()
