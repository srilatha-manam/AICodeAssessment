# Backend/routers/ai_code_assessment_routers.py - Simplified dynamic generation

from fastapi import APIRouter, HTTPException, Query
from models.code_evaluation_model import CodeSubmission, EvaluationResult
from services import code_assessment_service
from services.gemini_evaluation_service import evaluate_code_with_gemini
from logging_config import logger

router = APIRouter(
    prefix="/api/v1/code-assessment",
    tags=["Code Assessment"],
    responses={404: {"description": "Not found"}}
)

@router.get("/load-question")
async def get_question(difficulty: str = Query(None, description="Question difficulty: Easy, Moderate, Hard")):
    """Generate a fresh question every time - fully dynamic"""
    try:
        logger.info(f"Request for new question with difficulty: {difficulty}")
        question = await code_assessment_service.get_random_question(difficulty)
        
        if not question:
            raise HTTPException(status_code=500, detail="Failed to generate question")
        
        return {
            "id": question.id,
            "title": question.title,
            "description": question.description,
            "examples": [
                {
                    "input": example.input,
                    "output": example.output,
                    "explanation": example.explanation
                }
                for example in question.examples
            ],
            "difficultylevel": question.difficultylevel,
            "generated_at": "real-time",
            "type": "dynamic_ai_generated"
        }
        
    except Exception as e:
        logger.error(f"Error getting question: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate question: {str(e)}")

@router.post("/evaluate-code")
async def evaluate_code(submission: CodeSubmission):
    """Evaluate submitted code with AI feedback"""
    try:       
        print("contoller is called",flush=True)       
        result= await code_assessment_service.evaluate_submission(submission)     
        
        return {
            "correct": result.correct,
            "expected": result.expected,
            "actual": result.actual,
            "status": result.status,
            "feedback": result.feedback,           
            "has_ai_feedback": result.feedback is not None,
            "judge0_response": result.full_judge_response
        }
        
    except ValueError as e:
        logger.error(f"Validation error in evaluate_code: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in evaluate_code: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Code evaluation failed: {str(e)}")

@router.get("/question/{question_id}")
async def get_question_by_id(question_id: int):
    """Get current question by ID"""
    try:
        question = await code_assessment_service.get_question_by_id(question_id)
        if not question:
            raise HTTPException(status_code=404, detail=f"Question {question_id} not found")
        
        return {
            "id": question.id,
            "title": question.title,
            "description": question.description,
            "examples": [
                {
                    "input": example.input,
                    "output": example.output,
                    "explanation": example.explanation
                }
                for example in question.examples
            ],
            "difficultylevel": question.difficultylevel
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting question by ID: {e}")
        raise HTTPException(status_code=500, detail="Failed to load question by ID")
@router.post("/gemini-evaluatation", response_model=EvaluationResult)
async def evaluate_with_gemini_only(submission: CodeSubmission):
    return await evaluate_code_with_gemini(submission)

from models.code_evaluation_model import DifficultyRequest

@router.post("/load-question-by-difficulty")
async def load_question_from_body(req: DifficultyRequest):
    """
    Load a question based on difficulty level passed in the request body.
    """
    try:
        # Log the POST request to load question for the given difficulty level
        logger.info(f"POST request to load question for difficulty: {req.difficulty}")
        # Get a random question from the interview service based on the difficulty level
        question = await code_assessment_service.get_random_question(req.difficulty)

        # If no question is found for the given difficulty level, raise an HTTPException
        if not question:
            raise HTTPException(status_code=404, detail="No question found for given difficulty level")
        
        # Return the question details in a dictionary
        return {
            "id": question.id,
            "title": question.title,
            "description": question.description,
            "examples": [
                {
                    "input": example.input,
                    "output": example.output,
                    "explanation": example.explanation
                }
                for example in question.examples
            ],
            "difficultylevel": question.difficultylevel,
            "generated_at": "real-time",
            "type": "dynamic_ai_generated"
        }

    except Exception as e:
        # Log the error if the question cannot be loaded
        logger.error(f"Failed to load question by difficulty from body: {e}")
        # Raise an HTTPException with the error message
        raise HTTPException(status_code=500, detail=f"Error loading question: {str(e)}")



