from fastapi import APIRouter, HTTPException
from ..models.code_evaluation_model import CodeSubmission
from ..services import load_and_evaluation_service as interview_service
# This module defines the API endpoints for automatic code assessment related operations.

router = APIRouter(
    prefix="/code-assessment",
    tags=["Code Assessment"],
    responses={404: {"description": "Not found"}}
)

# API endpoint to get a random question for the code assessment
@router.get("/question")
async def get_question():
    
    return await interview_service.get_random_question()

#endpoint to evaluate the submitted code against the question
@router.post("/evaluate")
async def evaluate_code(submission: CodeSubmission):
    try:       
        result = await interview_service.evaluate_submission(submission)        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Code evaluation failed")

# API endpoint to get a question by its ID
@router.get("/question/{question_id}")
async def get_question_by_id(question_id: int):
    try:
        return await interview_service.get_question_by_id(question_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to load question by ID")
