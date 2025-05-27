import random
from ..models.code_evaluation_model import CodeSubmission, EvaluationResult
from .question_loader_service import load_random_question 
from ..logging_config import logger

# This module provides functionality to evaluate code submissions against predefined questions.

#Define a function called get_random_question that returns a random question from the questions list
def get_random_question():
    return load_random_question()

# Define an asynchronous function to evaluate a code submission
async def evaluate_submission(submission: CodeSubmission) -> EvaluationResult:
    # Get the question associated with the submission
    question = next((q for q in questions if q.id == submission.question_id), None)
    # If the question does not exist, raise a ValueError
    if not question:
        logger.error(f"Invalid Question ID: {submission.question_id}")
        raise ValueError("Invalid Question ID")
    try:
        # Evaluate the code submission using the question's test input
        result = await evaluate_code(submission.code, submission.language_id, question.test_input)
        # Get the output of the code submission
        output = (result.get("stdout") or "").strip()
        # Get the expected output of the question
        expected = question.expected_output.strip()
    except Exception as e:
        logger.critical(f"Code evaluation failed for Question ID {submission.question_id}: {e}", exc_info=True)
        raise ValueError("Error evaluating code")
    

    # Return an EvaluationResult object with the evaluation results
    return EvaluationResult(
        correct=output == expected,
        expected=expected,
        actual=output,
        status=result.get("status", {}).get("description", "Unknown")
    )
