from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from dependencies import get_model_manager

router = APIRouter()

@router.get("/")
async def search_students(
    query: Optional[str] = Query(None, min_length=1), 
    manager = Depends(get_model_manager)
):
    config, model, dataset, _ = manager.get_model_components()
    
    if dataset is None:
        raise HTTPException(status_code=400, detail="Model not loaded")
        
    uid_field = dataset.uid_field
    user_id2token = dataset.field2id_token[uid_field]
    
    results = []
    # Skip index 0 (padding)
    for user_id in range(1, len(user_id2token)):
        student_code = user_id2token[user_id]
        
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
