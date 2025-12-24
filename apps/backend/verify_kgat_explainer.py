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
    
    # VERIFICATION ASSERTIONS
    print("\n--- Running Verification Assertions ---")
    
    # 1. Check for score removal in path strings
    # We expect "A --[rel]--> B" NOT "A --[rel]--> B (0.xx)"
    has_scores = False
    for path in data['paths_from_history']:
        path_str = path['path_string']
        # Simple check for parenthesis with numbers inside
        if '(' in path_str and ')' in path_str:
            # It might have other parenthesis, but let's check if it looks like score
            import re
            if re.search(r'\(\d+\.\d+\)', path_str):
                has_scores = True
                print(f"FAILED: Found score in path: {path_str}")
    
    if not has_scores:
        print("PASSED: No scores found in path display strings.")
        
    # 2. Check for Shared Topics section in LLM input
    if "# Shared Topics" in data['input_data_technical']:
         print("PASSED: 'Shared Topics' section found in LLM input.")
    else:
         print("FAILED: 'Shared Topics' section NOT found in LLM input.")

    # 3. Check fallback explanation for natural language score usage (we want "strong", not "0.89")
    fallback_text = data['kg_context_text']
    if any(char.isdigit() for char in fallback_text if char not in ['1', '2', '3']): # Allow small numbers like item names
        # This is a loose check, but we mainly want to ensure "0.89" isn't there
        if "0." in fallback_text:
             print(f"WARNING: Found decimal numbers in fallback text: {fallback_text}")
        else:
             print("PASSED: No obvious scores in fallback text.")
    else:
        print("PASSED: No scores in fallback text.")

    
    # 2. Test full report
    print("\n--- Testing explain_recommendations (Full Report) ---")
    recommendations = [
        {'id': 'E1', 'name': 'AVL Tree Balance'},
        {'id': 'E4', 'name': 'Heap Sort'}
    ]
    report = explainer.explain_recommendations(user_id, recommendations, user_history, edge_attention)
    # safe_print(report)
    print("Report generated successfully.")

if __name__ == "__main__":
    test_explainer()
