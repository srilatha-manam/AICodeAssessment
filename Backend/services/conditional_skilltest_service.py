from ..models.code_evaluation_model import CodeSubmission, EvaluationResult
from .question_loader_service import load_all_questions
from .solution_evaluation_service import evaluate_code
from ..logging_config import logger

def get_random_question(difficulty: str):
    all_questions = load_all_questions()
    filtered = [q for q in all_questions if q.difficultylevel.lower() == difficulty.lower()]
    import random
    return random.choice(filtered) if filtered else None

async def evaluate_submission(submission: CodeSubmission) -> dict:
    questions = load_all_questions()
    question = next((q for q in questions if q.id == submission.question_id), None)
    if not question:
        raise ValueError("Invalid Question ID")

    passed_count = 0
    results = []
    for example in question.examples:
        try:
            res = await evaluate_code(submission.code, submission.language_id, example.input)
            actual = (res.get("stdout") or "").strip()
            expected = example.output.strip()
            is_correct = actual == expected
            results.append((is_correct, expected, actual))
            if is_correct:
                passed_count += 1
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            results.append((False, example.output, "Error"))

    total = len(results)
    percent_score = (passed_count / total) * 100
    qualified = percent_score >= 60

    return {
        "correct": passed_count == total,
        "percentage": percent_score,
        "qualified_for_next_round": qualified,
        "passed_testcases": passed_count,
        "total_testcases": total,
        "expected_outputs": [e for (_, e, _) in results],
        "actual_outputs": [a for (_, _, a) in results]
    }
