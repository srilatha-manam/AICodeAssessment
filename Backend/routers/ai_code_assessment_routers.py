# Backend/routers/ai_code_assessment_routers.py - Simplified dynamic generation

from fastapi import APIRouter, HTTPException, Query
from models.code_evaluation_model import CodeSubmission
from services import load_and_evaluation_service as interview_service
from services import code_assessment_service
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
        question = await interview_service.get_random_question(difficulty)
        
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
        #result = await interview_service.evaluate_submission(submission)
        result= await code_assessment_service.evaluate_submission(submission)
        
        # Format feedback for better display
        formatted_feedback = None
        if result.feedback:
            if result.correct:
                formatted_feedback = format_success_feedback(result.feedback)
            else:
                formatted_feedback = format_failure_feedback(result.feedback)
        
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
        question = await interview_service.get_question_by_id(question_id)
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

@router.get("/stats")
async def get_generation_stats():
    """Get statistics about question generation"""
    try:
        stats = interview_service.get_generation_stats()
        return {
            "generation_stats": stats,
            "message": "Dynamic generation - each question is unique"
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")

@router.post("/reset")
async def reset_generation_history():
    """Reset generation history for fresh start"""
    try:
        success = interview_service.clear_generation_history()
        if success:
            return {"message": "Generation history cleared - ready for fresh questions"}
        else:
            raise HTTPException(status_code=500, detail="Failed to reset history")
    except Exception as e:
        logger.error(f"Error resetting history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reset: {str(e)}")

def format_success_feedback(feedback_data: dict) -> str:
    """Format success feedback for display"""
    # Import the updated function from feedback service
    from services.feedback_generation_service import format_feedback_for_display
    return format_feedback_for_display(feedback_data)

def format_failure_feedback(feedback_data: dict) -> str:
    """Format failure feedback for display"""
    # Import the updated function from feedback service
    from services.feedback_generation_service import format_failure_feedback_for_display
    return format_failure_feedback_for_display(feedback_data)