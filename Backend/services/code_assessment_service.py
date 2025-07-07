# load_and_evaluation_service.py

from typing import List, Optional
from models.code_evaluation_model import Question, CodeSubmission, EvaluationResult
from services.solution_evaluation_service import evaluate_code
from services.question_loader_service import (    
    get_question_by_id as csv_get_question_by_id,
    get_random_question as csv_get_random_question,
    get_questions_by_difficulty as csv_get_questions_by_difficulty,
    get_all_questions as csv_get_all_questions   
)
from services.feedback_to_recuriter import generate_recruiter_feedback
from logging_config import logger
import time

# Use CSV-based question loading functions
async def get_random_question(difficulty: Optional[str] = None) -> Optional[Question]:
    return await csv_get_random_question(difficulty)

async def get_question_by_id(question_id: int) -> Optional[Question]:
    return await csv_get_question_by_id(question_id)

async def get_questions_by_difficulty(difficulty: str) -> List[Question]:
    return await csv_get_questions_by_difficulty(difficulty)

async def get_all_questions() -> List[Question]:
    return await csv_get_all_questions()
def get_language_name(language_id: int) -> str:
    """Map Judge0 language IDs to readable language names"""
    language_map = {
        71: "Python",
        62: "Java",
        63: "JavaScript",
        50: "C",
        54: "C++",
        51: "C#",
        72: "Ruby",
        73: "Rust",
        74: "TypeScript",
        # Add more mappings as needed
    }
    return language_map.get(language_id, "Python") 

# Define an asynchronous function to evaluate a code submission
async def evaluate_submission(submission: CodeSubmission) -> EvaluationResult:
    try:
        print("evaluating submission")
        question = await get_question_by_id(submission.question_id)
        if not question:
            raise ValueError(f"Question with ID {submission.question_id} not found")

        test_input = "\n".join([example.input for example in question.examples])
        expected_outputs = [example.output.strip() for example in question.examples]
        language_name = get_language_name(submission.language_id)

        try:
            logger.info(f"Executing code for question {submission.question_id}")
            
            # Start timer
            start_time = time.perf_counter()
            execution_result = await evaluate_code(
                submission.code,
                submission.language_id,
                test_input
            )

            # End timer
            end_time = time.perf_counter()
            time_taken_seconds = end_time - start_time
            time_taken = f"{round(time_taken_seconds, 2)}s"

            logger.info(f"Judge0 response: {execution_result}")

            status_obj = execution_result.get("status", {})
            status = status_obj.get("description", "Unknown") if isinstance(status_obj, dict) else "Unknown"

            actual_output = (execution_result.get("stdout") or "").strip()
            error_message = execution_result.get("stderr") or ""
            compile_output = execution_result.get("compile_output") or ""

            actual_outputs = actual_output.split('\n') if actual_output else []
            actual_outputs_clean = [output.strip() for output in actual_outputs if output is not None]
            expected_outputs_clean = [output.strip() for output in expected_outputs if output is not None]

            passed_count = sum(1 for actual, expected in zip(actual_outputs_clean, expected_outputs_clean) if actual == expected)
            edge_cases_flag = len(expected_outputs) > 2 and passed_count == len(expected_outputs)

            correctness = (
                status.lower() in ["accepted", "correct answer", "accepted (correct answer)"] and
                passed_count == len(expected_outputs)
            )

            # Placeholder for 3 attempts
            attempts = [
                "Attempt 1", "Attempt 2", "Attempt 3"
            ]

            feedback = await generate_recruiter_feedback(
                code=submission.code,
                language=language_name,
                question_description=question.description,
                judge_result={
                    "status": status,
                    "stderr": error_message,
                    "compile_output": compile_output,
                    "stdout": actual_output,
                    "time": execution_result.get("time"),
                    "memory": execution_result.get("memory"),
                    "passed": passed_count,
                    "total": len(expected_outputs),
                    "edge_cases_handled": edge_cases_flag
                },
                expected_outputs=expected_outputs,
                actual_output=actual_output,
                time_taken=time_taken,
                attempts=attempts
            )
            print("Question loaded:", question)
            print("Test input:", test_input)
            print("Expected outputs:", expected_outputs)
            print("Judge0 execution result:", execution_result)
            print("Feedback from Gemini:", feedback)

            return EvaluationResult(
                correct=correctness,
                expected="\n".join(expected_outputs),
                actual=actual_output,
                status=status,
                feedback=feedback,
                full_judge_response=execution_result
            )

        except Exception as execution_error:
            logger.error(f"Code execution error: {execution_error}")
            raise

    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        raise