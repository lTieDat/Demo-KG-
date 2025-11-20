"""
Recommendation API endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import sys
import os

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from utils.recommendations import get_top_k_recommendations
from item_utils import load_item_details, get_item_display_info
from api.models import get_loaded_model

router = APIRouter()

class RecommendationRequest(BaseModel):
    user_id: int
    topk: int = 10

class StudentSearchRequest(BaseModel):
    search: str = ""

@router.get("/students")
async def list_students(search: str = ""):
    """List all students with optional search"""
    try:
        config, model, dataset = get_loaded_model()
        
        uid_field = dataset.uid_field
        user_id2token = dataset.field2id_token[uid_field]
        
        # Build student list
        students = []
        for user_id in range(1, len(user_id2token)):
            student_code = user_id2token[user_id]
            if (
                isinstance(student_code, str)
                and student_code.startswith("B")
                and len(student_code) >= 8
            ):
                # Apply search filter
                if search and search.upper() not in student_code.upper():
                    continue
                    
                students.append({
                    "student_code": student_code,
                    "user_id": user_id
                })
        
        return {
            "students": students,
            "total": len(students)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/students/{student_code}")
async def get_student(student_code: str):
    """Get student details by code"""
    try:
        config, model, dataset = get_loaded_model()
        
        uid_field = dataset.uid_field
        user_id2token = dataset.field2id_token[uid_field]
        
        # Find student
        for user_id in range(1, len(user_id2token)):
            if user_id2token[user_id] == student_code:
                return {
                    "student_code": student_code,
                    "user_id": user_id
                }
        
        raise HTTPException(status_code=404, detail=f"Student {student_code} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate")
async def generate_recommendations(request: RecommendationRequest):
    """Generate recommendations for a user"""
    try:
        config, model, dataset = get_loaded_model()
        
        # Generate recommendations
        recs = get_top_k_recommendations(
            model, dataset, request.user_id, topk=request.topk
        )
        
        # Load item details
        item_details = load_item_details()
        
        # Format results
        results = []
        for item_internal_id, item_external_id, score in recs:
            item_info = get_item_display_info(item_external_id, item_details)
            results.append({
                "rank": len(results) + 1,
                "item_id": item_external_id,
                "internal_id": item_internal_id,
                "score": float(score),
                "title": item_info["title"],
                "topic": item_info["topic"],
                "sub_topic": item_info["sub_topic"],
                "difficulty": item_info["difficulty"]
            })
        
        return {
            "user_id": request.user_id,
            "topk": request.topk,
            "recommendations": results
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
