import sys
import os
from collections import defaultdict

# Add current dir to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from enhanced_kg_explainer import EnhancedKGExplainer
except ImportError:
    # Handle local path if running from root
    sys.path.append(os.path.join(os.getcwd(), 'apps/backend'))
    from enhanced_kg_explainer import EnhancedKGExplainer

def test_explainer():
    print("Testing EnhancedKGExplainer...")
    explainer = EnhancedKGExplainer()
    
    # Mock data
    user_id = "student_123"
    item_id = "E1" # Binary Search Tree Operations (hypothetical)
    user_history = ["E2", "E3"] # Previous exercises
    
    # Mock edge attention scores
    edge_attention = {
        ("E2", "has_topic", "T_BST"): 0.89,
        ("T_BST", "topic_of", "E1"): 0.76,
        ("E1", "has_topic", "T_BST"): 0.70,
        ("E3", "has_level", "L_2"): 0.82,
        ("L_2", "level_of", "E1"): 0.68,
        ("E1", "has_level", "L_2"): 0.55
    }
    
    # 1. Test single item explanation
    print("\n--- Testing explain_single_item ---")
    data = explainer.explain_single_item(user_id, item_id, user_history, edge_attention)
    
    # Use encode/decode to avoid console encoding issues on Windows
    def safe_print(text):
        try:
            print(text)
        except UnicodeEncodeError:
            print(text.encode('ascii', 'ignore').decode('ascii'))

    safe_print(f"Item Name: {data['item_name']}")
    safe_print(f"Entity ID: {data['entity_id']}")
    print(f"Number of paths found: {len(data['paths_from_history'])}")
    print("\nTechnical Input Data:")
    safe_print(data['input_data_technical'])
    
    print("\nFallback Explanation Output:")
    safe_print(data['kg_context_text'])
    
    # 2. Test full report
    print("\n--- Testing explain_recommendations (Full Report) ---")
    recommendations = [
        {'id': 'E1', 'name': 'AVL Tree Balance'},
        {'id': 'E4', 'name': 'Heap Sort'}
    ]
    report = explainer.explain_recommendations(user_id, recommendations, user_history, edge_attention)
    safe_print(report)

if __name__ == "__main__":
    test_explainer()
