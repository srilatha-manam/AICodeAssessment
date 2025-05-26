import random
from ..models/code_evaluation_model import CodeSubmission, EvaluationResult
from ..services.question_loader_service import load_questions
from ..services.solution_evaluation_service import evaluate_code

# This module provides functionality to evaluate code submissions against predefined questions.
questions = load_questions()

#Define a function called get_random_question that returns a random question from the questions list
def get_random_question():
    return random.choice(questions)

# Define an asynchronous function to evaluate a code submission
async def evaluate_submission(submission: CodeSubmission) -> EvaluationResult:
    # Get the question associated with the submission
    question = next((q for q in questions if q.id == submission.question_id), None)
    # If the question does not exist, raise a ValueError
    if not question:
        raise ValueError("Invalid Question ID")

    # Evaluate the code submission using the question's test input
    result = await evaluate_code(submission.code, submission.language_id, question.test_input)
    # Get the output of the code submission
    output = (result.get("stdout") or "").strip()
    # Get the expected output of the question
    expected = question.expected_output.strip()

    # Return an EvaluationResult object with the evaluation results
    return EvaluationResult(
        correct=output == expected,
        expected=expected,
        actual=output,
        status=result.get("status", {}).get("description", "Unknown")
    )
