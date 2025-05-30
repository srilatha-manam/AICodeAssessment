from fastapi import APIRouter, HTTPException
from ..models.code_evaluation_model import CodeSubmission
from ..services import conditional_skilltest_service as service

router = APIRouter(prefix="/conditional-code-assessment", tags=["Conditional Code Assessment"])

@router.get("/conditional-question")
def get_question(difficulty: str = "Easy"):
    q = service.get_random_question(difficulty)
    if not q:
        raise HTTPException(status_code=404, detail="No question found")
    return q

@router.post("/conditional-evaluate")
async def evaluate(submission: CodeSubmission):
    try:
        return await service.evaluate_submission(submission)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
