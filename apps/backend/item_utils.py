import os
import pandas as pd

def load_item_details(dataset_name='cpp'):
    """
    Load item details based on the dataset name.
    
    Args:
        dataset_name (str): The name of the dataset ('algorithm' or 'cpp')
    """
    
    # __file__ is apps/backend/item_utils.py
    # dirname(file) is apps/backend
    # dirname(dirname(file)) is apps
    # dirname(dirname(dirname(file))) is project root (e:\DoAn\Web)
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    if dataset_name == 'algorithm':
        dataset_folder = 'dataset/ctdlgt'
        item_file = 'ctdlgt.item'
    else:
        dataset_folder = 'dataset/cpp'
        item_file = 'cpp.item'
        
    item_path = os.path.join(base_path, dataset_folder, item_file)
    
    # Fallback to current working directory if not found
    if not os.path.exists(item_path):
        item_path = os.path.abspath(os.path.join(dataset_folder, item_file))

    items = {}
    
    def clean_value(val, field_type):
        if not val: return val
        # Remove RecBole prefixes
        val = str(val).replace('T_', '').replace('L_', '').replace('_', ' ')
        return val.strip()

    try:
        if os.path.exists(item_path):
             with open(item_path, 'r', encoding='utf-8') as f:
                header_line = f.readline().strip()
                if not header_line:
                    return {}
                header = header_line.split('\t')
                
                for line in f:
                    parts = line.strip().split('\t')
                    if not parts or not parts[0]:
                        continue
                        
                    item_id = parts[0]
                    item_data = {}
                    
                    # map known headers
                    for i, col in enumerate(header):
                        if i < len(parts):
                            clean_col = col.split(':')[0]
                            val = parts[i]
                            # Clean specific fields
                            if clean_col in ['type', 'level', 'group']:
                                val = clean_value(val, clean_col)
                            item_data[clean_col] = val
                    
                    # Ensure 'name' or 'title' mapping for standard UI fields
                    if 'name' in item_data and 'title' not in item_data:
                        item_data['title'] = item_data['name']
                    if 'type' in item_data and 'topic' not in item_data:
                        item_data['topic'] = item_data['type']
                    if 'level' in item_data and 'difficulty' not in item_data:
                        item_data['difficulty'] = item_data['level']
                        
                    items[item_id] = item_data
        else:
            print(f"Warning: Item file not found at {item_path}")

    except Exception as e:
        print(f"Error loading item details from {item_path}: {e}")
        import traceback
        traceback.print_exc()
        return {}

    return items
