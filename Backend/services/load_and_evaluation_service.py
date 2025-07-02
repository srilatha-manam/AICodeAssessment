# load_and_evaluation_service.py

from typing import List, Optional
from models.code_evaluation_model import Question, Example, CodeSubmission, EvaluationResult
from services.feedback_generation_service import (
    generate_feedback_for_success, 
    generate_feedback_for_failure,
    format_failure_feedback_for_display,
    get_language_name
)
from services.solution_evaluation_service import evaluate_code
from services.question_loader_service import (
    load_questions_from_csv,
    get_question_by_id as csv_get_question_by_id,
    get_random_question as csv_get_random_question,
    get_questions_by_difficulty as csv_get_questions_by_difficulty,
    get_all_questions as csv_get_all_questions
)
from logging_config import logger

# Use CSV-based question loading functions
async def get_random_question(difficulty: Optional[str] = None) -> Optional[Question]:
    """
    Get a random question, optionally filtered by difficulty
    """
    return await csv_get_random_question(difficulty)

async def get_question_by_id(question_id: int) -> Optional[Question]:
    """
    Get a specific question by its ID
    """
    return await csv_get_question_by_id(question_id)

async def get_questions_by_difficulty(difficulty: str) -> List[Question]:
    """
    Get all questions filtered by difficulty level
    """
    return await csv_get_questions_by_difficulty(difficulty)

async def get_all_questions() -> List[Question]:
    """
    Get all available questions
    """
    return await csv_get_all_questions()

async def evaluate_submission(submission: CodeSubmission) -> EvaluationResult:
    """
    Enhanced evaluation that generates AI feedback for both success and failure cases
    """
    try:
        # Get the question details
        question = await get_question_by_id(submission.question_id)
        if not question:
            raise ValueError(f"Question with ID {submission.question_id} not found")
        
        # Prepare test input from examples
        test_input = "\n".join([example.input for example in question.examples])
        expected_outputs = [example.output.strip() for example in question.examples]
        
        # Get language name for better feedback
        language_name = get_language_name(submission.language_id)
        
        try:
            # Execute the code using Judge0
            logger.info(f"Executing code for question {submission.question_id}")
            execution_result = await evaluate_code(
                submission.code, 
                submission.language_id, 
                test_input
            )
            
            logger.info(f"Judge0 response: {execution_result}")
            
            # Extract execution details with proper null checks
            status_obj = execution_result.get("status", {})
            if isinstance(status_obj, dict):
                status = status_obj.get("description", "Unknown")
            else:
                status = "Unknown"
            
            # Handle None values from Judge0 API
            actual_output = execution_result.get("stdout") or ""
            if actual_output:
                actual_output = actual_output.strip()
            
            error_message = execution_result.get("stderr") or ""
            compile_output = execution_result.get("compile_output") or ""
            
            # Determine if execution was successful
            execution_successful = status.lower() in [
                "accepted", 
                "accepted (correct answer)",
                "correct answer"
            ]
            
            # Check correctness by comparing outputs with null safety
            actual_outputs = []
            if actual_output:
                actual_outputs = actual_output.split('\n')
            
            # Clean up outputs for comparison
            actual_outputs_clean = [output.strip() for output in actual_outputs if output is not None]
            expected_outputs_clean = [output.strip() for output in expected_outputs if output is not None]
            correctness = (
                execution_successful and 
                len(actual_outputs_clean) == len(expected_outputs_clean) and
                all(actual.strip() == expected.strip() 
                    for actual, expected in zip(actual_outputs_clean, expected_outputs_clean)
                    if actual is not None and expected is not None)
            )
            
            # Generate appropriate feedback based on execution result
            feedback = None
            
            if execution_successful and correctness:
                # Code executed successfully and produced correct output
                feedback = await generate_feedback_for_success(
                    code=submission.code,
                    question_desc=question.description,
                    language=language_name
                )
                logger.info(f"Generated success feedback for question {submission.question_id}")
            else:
                # Code failed to execute or produced wrong output
                feedback = await generate_feedback_for_failure(
                    code=submission.code,
                    question_desc=question.description,
                    correctness=correctness,
                    status=status,
                    expected="\n".join(expected_outputs),
                    actual_output=actual_output,
                    error_message=error_message or compile_output,
                    language=language_name
                )
                logger.info(f"Generated failure feedback for question {submission.question_id}")
            
            # Create evaluation result
            result = EvaluationResult(
                correct=correctness,
                expected="\n".join(expected_outputs),
                actual=actual_output,
                status=status,
                feedback=feedback
            )
            
            return result
            
        except Exception as execution_error:
            # Handle code execution errors
            logger.error(f"Code execution error: {execution_error}")
            
            error_feedback = await generate_feedback_for_failure(
                code=submission.code,
                question_desc=question.description,
                correctness=False,
                status="Execution Error",
                expected="\n".join(expected_outputs),
                actual_output="",
                error_message=str(execution_error),
                language=language_name
            )
            
            result = EvaluationResult(
                correct=False,
                expected="\n".join(expected_outputs),
                actual="Code execution failed",
                status=f"Error: {str(execution_error)}",
                feedback=error_feedback
            )
            
            return result
            
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        # Handle general evaluation errors
        error_feedback = await generate_feedback_for_failure(
            code=submission.code,
            question_desc="Unknown question",
            correctness=False,
            status="Evaluation Error",
            expected="Unknown",
            actual_output="",
            error_message=str(e),
            language="Python"
        )
        
        result = EvaluationResult(
            correct=False,
            expected="Evaluation failed",
            actual="Evaluation failed",
            status=f"Error: {str(e)}",
            feedback=error_feedback
        )
        
        return result

# Additional utility functions

# async def get_questions_by_difficulty(difficulty: str) -> List[Question]:
#     """
#     Get all questions filtered by difficulty level
#     """
#     try:
#         questions = await load_questions_from_json()
#         return [q for q in questions if q.difficultylevel.lower() == difficulty.lower()]
#     except Exception as e:
#         logger.error(f"Error getting questions by difficulty: {e}")
#         return []

# async def get_all_questions() -> List[Question]:
#     """
#     Get all available questions
#     """
#     try:
#         return await load_questions_from_json()
#     except Exception as e:
#         logger.error(f"Error getting all questions: {e}")
#         return []