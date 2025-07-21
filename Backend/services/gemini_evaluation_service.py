# Backend/services/gemini_evaluation_service.py
# This service handles code evaluation using Gemini AI 
from datetime import datetime
from models.code_evaluation_model import CodeSubmission, EvaluationResult
from services.question_loader_service import get_question_by_id as csv_get_question_by_id
from services.gemini_evaluation_template  import code_evaluation_by_gemini
from logging_config import logger


def get_language_name(language_id: int) -> str:
    language_map = {
        71: "Python",
        62: "Java",
        50: "C",
        54: "C++",
        51: "C#",
    }
    return language_map.get(language_id, "Python")


async def evaluate_code_with_gemini(submission: CodeSubmission) -> EvaluationResult:
    try:
        # Log that the submission is being evaluated with Gemini only
        logger.info("Evaluating submission with Gemini only")
        # Get the question associated with the submission
        question = await csv_get_question_by_id(submission.question_id)
        # If the question is not found, raise an error
        if not question:
            raise ValueError(f"Question with ID {submission.question_id} not found")

        # Get the language name associated with the submission
        language_name = get_language_name(submission.language_id)

        # Call Gemini to generate test cases and evaluate code
        start_time = datetime.utcnow()
        gemini_response = await code_evaluation_by_gemini(
            code=submission.code,
            language=language_name,
            question_title=question.title,
            question_description=question.description           
            
        )

        end_time = datetime.utcnow()
        total_time = f"{(end_time - start_time).total_seconds():.2f}s"

        # Return the evaluation result
        return EvaluationResult(
            correct=gemini_response.get("correct", False),
            expected=gemini_response.get("expected", ""),
            actual=gemini_response.get("actual", ""),
            status=gemini_response.get("status", "Failed"),
            feedback={**gemini_response.get("feedback", {}), "timestamp": datetime.utcnow().isoformat()},
            full_judge_response={"gemini_test_results": gemini_response.get("feedback", {})}
        )

    except Exception as e:
        # Log any errors that occur during the evaluation
        logger.error(f"Gemini-only evaluation failed: {e}", exc_info=True)
        # Raise the error
        raise
