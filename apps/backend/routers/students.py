from fastapi import APIRouter, HTTPException, Depends, Query
from dependencies import get_model_manager
import os
import pandas as pd
import numpy as np

router = APIRouter()

@router.get("/")
async def search_students(query: str = "", limit: int = 10, manager = Depends(get_model_manager)):
    """
    Search for students in the .user file using student_id or name.
    """
    try:
        current_subject = manager.get_current_subject()
        if not current_subject:
            return []

        # Determine user file path
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        
        if current_subject == 'algorithm':
            user_file = os.path.join(base_path, 'dataset', 'ctdlgt', 'ctdlgt.user')
        else:
            user_file = os.path.join(base_path, 'dataset', 'cpp', 'cpp.user')
            
        if not os.path.exists(user_file):
            print(f"DEBUG: User file not found: {user_file}")
            return []

        # Read the .user file directly
        # Format: user_id:token\tstudent_id:token\tname:token_seq...
        results = []
        query_lower = query.lower()
        
        with open(user_file, 'r', encoding='utf-8') as f:
            header_line = f.readline().strip()
            if not header_line:
                return []
            
            headers = [h.split(':')[0] for h in header_line.split('\t')]
            
            # Find indices for important columns
            try:
                uid_idx = headers.index('user_id')
                sid_idx = headers.index('student_id') if 'student_id' in headers else -1
                name_idx = headers.index('name') if 'name' in headers else -1
            except ValueError:
                print(f"DEBUG: Required columns missing in {user_file}")
                return []
                
            for line in f:
                parts = line.strip().split('\t')
                if not parts:
                    continue
                
                # Extract values
                uid = parts[uid_idx]
                sid = parts[sid_idx] if sid_idx != -1 and sid_idx < len(parts) else uid
                name = parts[name_idx] if name_idx != -1 and name_idx < len(parts) else f"Student {sid}"
                
                # Filter
                match = False
                if not query:
                    match = True
                else:
                    if query_lower in uid.lower() or query_lower in sid.lower() or query_lower in name.lower():
                        match = True
                
                if match:
                    results.append({
                        'id': uid,           # Token ID for model (Used in next API call)
                        'student_id': sid,  # Original student code
                        'name': name,
                        'subject': current_subject
                    })
                
                if len(results) >= limit:
                    break
                    
        print(f"DEBUG: Manual search for '{query}' returned {len(results)} results from {user_file}")
        return results

    except Exception as e:
        print(f"Error searching students from file: {e}")
        import traceback
        traceback.print_exc()
        return []

    except Exception as e:
        print(f"Error searching students: {e}")
        import traceback
        traceback.print_exc()
        return []
        
    return results
