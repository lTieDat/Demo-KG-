import sys
import os
import torch

# Add backend to path
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_path)

from dependencies import get_model_manager
from utils.recommendations import get_top_k_recommendations

def test_mapping():
    manager = get_model_manager()
    
    # Try to find a model checkpoint to load
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(backend_path)))
    saved_dir = os.path.join(base_path, 'saved')
    
    checkpoint = None
    for root, dirs, files in os.walk(saved_dir):
        for file in files:
            if file.endswith('.pth'):
                checkpoint = os.path.join(root, file)
                break
        if checkpoint: break
        
    if not checkpoint:
        print("No checkpoint found to test.")
        # Create a mock setup if no checkpoint
        print("Falling back to internal logic check...")
        return

    print(f"Loading model: {checkpoint}")
    try:
        manager.load_model(checkpoint)
        model, dataset, config = manager.get_model()
    except Exception as e:
        print(f"Failed to load model: {e}")
        return
    
    if not dataset:
        print("Dataset failed to load.")
        return

    # Test student ID to token mapping
    # Let's find a valid student ID from user_feat
    user_feat = dataset.user_feat
    if 'student_id' in user_feat.column_names:
        test_student_id = user_feat['student_id'][0]
        print(f"\nTesting mapping for student_id: {test_student_id}")
        
        idx = (user_feat['student_id'] == test_student_id).nonzero()[0]
        if len(idx) > 0:
            token_id = str(user_feat[dataset.uid_field][idx[0].item()])
            print(f"SUCCESS: Mapped {test_student_id} to user_id token: {token_id}")
            
            # Test recommendations
            recs = get_top_k_recommendations(model, dataset, test_student_id, k=5)
            print(f"Recommendations for {test_student_id}: {recs}")
            if recs:
                print("SUCCESS: Got recommendations!")
            else:
                print("FAILED: No recommendations found.")
        else:
            print(f"FAILED: Student ID {test_student_id} not found in user_feat.")
    else:
        print("FAILED: 'student_id' column not in user_feat.")

if __name__ == "__main__":
    test_mapping()
