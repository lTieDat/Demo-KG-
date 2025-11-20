"""
User history utilities for AI explainer
"""
import pandas as pd
import os


def get_user_history(dataset, user_id, limit=10):
    """
    Get interaction history for a user from dataset
    
    Args:
        dataset: RecBole dataset object
        user_id: Internal user ID
        limit: Maximum number of items to return
        
    Returns:
        List of item IDs that user has interacted with
    """
    try:
        # Get interaction data
        inter_feat = dataset.inter_feat
        uid_field = dataset.uid_field
        iid_field = dataset.iid_field
        
        # Filter by user
        user_interactions = inter_feat[inter_feat[uid_field] == user_id]
        
        # Get item IDs
        item_ids = user_interactions[iid_field].tolist()
        
        # Limit results
        return item_ids[:limit]
        
    except Exception as e:
        print(f"Error getting user history: {e}")
        return []


def get_user_history_with_details(dataset, user_id, item_details, limit=10):
    """
    Get interaction history with item details
    
    Args:
        dataset: RecBole dataset object
        user_id: Internal user ID
        item_details: Dict mapping item_id to item info
        limit: Maximum number of items to return
        
    Returns:
        List of dicts with item details
    """
    try:
        item_ids = get_user_history(dataset, user_id, limit)
        
        # Get item tokens (external IDs)
        iid_field = dataset.iid_field
        item_id2token = dataset.field2id_token[iid_field]
        
        history = []
        for item_id in item_ids:
            if item_id < len(item_id2token):
                item_token = item_id2token[item_id]
                if item_token in item_details:
                    item_info = item_details[item_token]
                    history.append({
                        "item_id": item_token,
                        "title": item_info.get("title", "Unknown"),
                        "topic": item_info.get("topic", "Unknown"),
                        "difficulty": item_info.get("difficulty", "Unknown")
                    })
        
        return history
        
    except Exception as e:
        print(f"Error getting user history with details: {e}")
        return []
