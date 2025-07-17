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
# Define an asynchronous function called get_random_question that takes an optional parameter difficulty of type str
# and returns an optional Question object
async def get_random_question(difficulty: Optional[str] = None) -> Optional[Question]:
    # Call the csv_get_random_question function and return its result
    return await csv_get_random_question(difficulty)

# Define an asynchronous function called get_question_by_id that takes an integer argument called question_id
async def get_question_by_id(question_id: int) -> Optional[Question]:
    # Return the result of the csv_get_question_by_id function, passing in the question_id argument
    return await csv_get_question_by_id(question_id)

# Define an asynchronous function called get_questions_by_difficulty that takes a string parameter called difficulty and returns a list of Question objects
async def get_questions_by_difficulty(difficulty: str) -> List[Question]:
    # Return the result of calling the csv_get_questions_by_difficulty function with the difficulty parameter
    return await csv_get_questions_by_difficulty(difficulty)

# Define an asynchronous function called get_all_questions that returns a list of Question objects
async def get_all_questions() -> List[Question]:
    # Call the csv_get_all_questions function and return its result
    return await csv_get_all_questions()
def get_language_name(language_id: int) -> str:
    """Map Judge0 language IDs to readable language names"""
    language_map = {
        71: "Python",
        62: "Java",      
        50: "C",
        54: "C++",
        51: "C#", 
     
        # Add more mappings as needed
    }
    return language_map.get(language_id, "Python") 

# Define an asynchronous function to evaluate a code submission
async def evaluate_submission(submission: CodeSubmission) -> EvaluationResult:
    try:
        logger.info("Evaluating submission")
        print("Evaluating submission")
        question = await get_question_by_id(submission.question_id)
        if not question:
            raise ValueError(f"Question with ID {submission.question_id} not found")

        language_name = get_language_name(submission.language_id)
        test_case_results = []
        passed_count = 0
        actual_outputs = []

        logger.info(f"Running code for question {question.id} with {len(question.examples)} test cases")

        start_time = time.perf_counter()

        for idx, example in enumerate(question.examples):
            logger.info(f"Running test case {idx + 1}: {example.input.strip()}")
            print(f"Running test case {idx + 1}: {example.input.strip()}")
            execution_result = await evaluate_code(
                code=submission.code,
                language_id=submission.language_id,
                stdin=example.input.strip()
            )
            print(f"Execution result: {execution_result}")
            stdout = (execution_result.get("stdout") or "").strip()
            expected = example.output.strip()

            is_passed = stdout == expected
            if is_passed:
                passed_count += 1

            actual_outputs.append(stdout)
            test_case_results.append({
                "input": example.input,
                "expected": expected,
                "actual": stdout,
                "status": "Passed" if is_passed else "Failed",
                "error": execution_result.get("stderr") or execution_result.get("compile_output") or ""
            })

        end_time = time.perf_counter()
        total_time = f"{round(end_time - start_time, 2)}s"

        correctness = passed_count == len(question.examples)
        edge_cases_flag = passed_count == len(question.examples) and len(question.examples) > 2

        feedback = await generate_recruiter_feedback(
            code=submission.code,
            language=language_name,
            question_description=question.description,
            judge_result={
                "status": "Passed" if correctness else "Failed",
                "stderr": "",
                "compile_output": "",
                "stdout": "\n".join(actual_outputs),
                "time": total_time,
                "memory": 0,
                "passed": passed_count,
                "total": len(question.examples),
                "edge_cases_handled": edge_cases_flag
            },
            expected_outputs=[ex.output for ex in question.examples],
            actual_output="\n".join(actual_outputs),
            time_taken=total_time,
            attempts=["Attempt 1", "Attempt 2", "Attempt 3"]
        )

        logger.info("Submission evaluation complete")
        return EvaluationResult(
            correct=correctness,
            expected="\n".join([ex.output for ex in question.examples]),
            actual="\n".join(actual_outputs),
            status="Passed" if correctness else "Failed",
            feedback=feedback,
            full_judge_response={"results": test_case_results}
        )

    except Exception as e:
        logger.error(f"Evaluation failed: {e}", exc_info=True)
        raise