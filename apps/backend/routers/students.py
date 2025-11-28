from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from dependencies import get_model_manager
import traceback

router = APIRouter()

@router.get("/")
async def search_students(
    query: Optional[str] = Query(None, min_length=1), 
    manager = Depends(get_model_manager)
):
    try:
        config, model, dataset, _ = manager.get_model_components()
        
        if dataset is None:
            raise HTTPException(status_code=400, detail="Model not loaded")
        
        # Read student IDs directly from cpp.user file
        import os
        # Get the backend directory (parent of routers)
        backend_dir = os.path.dirname(os.path.dirname(__file__))
        # Go up to Demo-KG- root and then to dataset
        user_file_path = os.path.join(backend_dir, '..', '..', 'dataset', 'cpp.user')
        user_file_path = os.path.abspath(user_file_path)
        
        # Map user_id to student_id by reading the file
        user_id_to_student_id = {}
        try:
            with open(user_file_path, 'r', encoding='utf-8') as f:
                # Skip header
                next(f)
                for line in f:
                    parts = line.strip().split('\t')
                    if len(parts) >= 2:
                        user_id = parts[0]  # This is the internal user_id
                        student_id = parts[1]  # This is the student code (B23DCCN...)
                        user_id_to_student_id[user_id] = student_id
        except Exception as e:
            print(f"Error reading user file: {str(e)}")
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"Error reading user file: {str(e)}")
        
        uid_field = dataset.uid_field
        user_id2token = dataset.field2id_token[uid_field]
        
        print(f"DEBUG: uid_field = {uid_field}")
        print(f"DEBUG: user_id2token type = {type(user_id2token)}")
        print(f"DEBUG: user_id2token length = {len(user_id2token)}")
        print(f"DEBUG: First few tokens: {user_id2token[:5] if hasattr(user_id2token, '__getitem__') else 'N/A'}")
        print(f"DEBUG: user_id_to_student_id keys sample: {list(user_id_to_student_id.keys())[:5]}")
        
        results = []
        # Skip index 0 (padding)
        for user_id in range(1, len(user_id2token)):
            user_id_token = user_id2token[user_id]
            
            # Look up student_id from our mapping
            student_code = user_id_to_student_id.get(user_id_token, user_id_token)
            
            # Basic validation for student code
            if isinstance(student_code, str) and student_code.startswith("B") and len(student_code) >= 8:
                if query:
                    if query.upper() in student_code.upper():
                        results.append({"id": user_id, "code": student_code})
                else:
                    results.append({"id": user_id, "code": student_code})
                    
        # Sort by code
        results.sort(key=lambda x: x["code"])
        
        return {"students": results, "total": len(results)}
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in search_students: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
