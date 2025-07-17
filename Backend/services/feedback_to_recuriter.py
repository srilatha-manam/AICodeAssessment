# services/recruiter_feedback_service.py

from datetime import datetime
from typing import List, Dict, Any
from services.gemini_feedback_template_service import generate_feedback_with_gemini  

def compute_verdict(score: float) -> str:
    
    if score >= 85:
        return "Excellent"
    elif score >= 70:
        return "Above Average"
    elif score >= 50:
        return "Average"
    elif score >= 35:
        return "Below Average"
    return "Needs Improvement"

async def generate_recruiter_feedback(
    code: str,
    language: str,
    question_description: str,
    judge_result: Dict[str, Any],
    expected_outputs: List[str],
    actual_output: str,
    time_taken: str,
    attempts: List[str]
) -> Dict[str, Any]:
    passed = judge_result.get("passed", 0)
    total = judge_result.get("total", len(expected_outputs))
    edge_cases_handled = judge_result.get("edge_cases_handled", False)

    coverage_percent = (passed / total * 100) if total > 0 else 0
    logical_accuracy = "Correct" if passed == total else (
        "Partially Correct" if passed > 0 else "Incorrect"
    )

    verdict_score = (coverage_percent + (100 if logical_accuracy == "Correct" else 60)) / 2
    verdict = compute_verdict(verdict_score)

    # ✅ Correct function usage
    ai_feedback = await generate_feedback_with_gemini(
        code=code,
        question_description=question_description,
        language=language,
        judge_result=judge_result,
        expected_outputs=expected_outputs,
        actual_output=actual_output
    )

    return {
    "problem_solving_score_out_of_100": ai_feedback.get("problem_solving_score", 0),
    "code_correctness_score_out_of_100": passed / total * 100 if total else 0,
    "code_quality_score_out_of_100": ai_feedback.get("code_quality_score", 0), 
    "language_used": language,
    "language_proficiency_comments": ai_feedback.get("language_proficiency", "Unavailable"),
    "code_readability_feedback": ai_feedback.get("readability", "Unavailable"),
    "algorithm_design_feedback": ai_feedback.get("algorithm_design", "Unavailable"),
    "debugging_and_testing_skills_feedback": ai_feedback.get("debugging_and_testing", "Unavailable"),
    "code_compilation_status": (
        "Compiled Successfully" if not judge_result.get("compile_output") else "Compilation Error"
    ),
    "runtime_error_occurred": bool(judge_result.get("stderr")),
    "logical_accuracy": logical_accuracy,
    "code_completion_status": ai_feedback.get("completion_status", "Unavailable"),
    "time_taken": time_taken,

    "critical_errors": ai_feedback.get("critical_errors") or ('No critical errors'),
    "problem_understanding_issues": ai_feedback.get("problem_understanding_issues") or ('No issues'),
    "language_specific_issues": ai_feedback.get("language_specific_issues") or ('No issues'),

    "attempt_summary": {
        "attempts_made": len(attempts),
        "approach_used": ai_feedback.get("approach_summary", "Unavailable"),
        "changes_over_attempts": attempts
    },
    "test_case_coverage": {
        "passed": passed,
        "total": total,
        "coverage_percent": round(coverage_percent, 2),
        "edge_cases_handled": edge_cases_handled
    },
    "observations": ai_feedback.get("ai_observations", ["AI feedback unavailable."]),
    "improvement_suggestions": ai_feedback.get("improvement_suggestions", ["Suggestion unavailable."]),
    "strengths": ai_feedback.get("strengths", []),
    "areas_of_concern": ai_feedback.get("areas_of_concern", []),
    "verdict": verdict,
    "timestamp": datetime.utcnow().isoformat()
}
