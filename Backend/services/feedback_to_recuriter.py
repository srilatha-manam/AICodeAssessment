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
        "problem_solving_score_out_of_100": ai_feedback["problem_solving_score"],
        "code_correctness_score_out_of_100": passed / total * 100 if total else 0,
        "code_quality_score_out_of_100": ai_feedback["code_quality_score"],
        "efficiency_score_out_of_100": ai_feedback["efficiency_score"],

        "test_case_coverage": {
            "passed": passed,
            "total": total,
            "coverage_percent": round(coverage_percent, 2),
            "edge_cases_handled": edge_cases_handled
        },

        "language_used": language,
        "language_proficiency_comments": ai_feedback["language_proficiency"],
        "code_readability_feedback": ai_feedback["readability"],
        "algorithm_design_feedback": ai_feedback["algorithm_design"],
        "debugging_and_testing_skills_feedback": ai_feedback["debugging_and_testing"],
        "code_compilation_status": (
            "Compiled Successfully" if not judge_result.get("compile_output") else "Compilation Error"
        ),
        "runtime_error_occurred": bool(judge_result.get("stderr")),
        "logical_accuracy": logical_accuracy,
        "code_completion_status": ai_feedback["completion_status"],
        "time_taken": time_taken,
        "attempt_summary": {
            "attempts_made": len(attempts),
            "approach_used": ai_feedback["approach_summary"],
            "changes_over_attempts": attempts
        },        
        "observations": ai_feedback["ai_observations"],
        "improvement_suggestions": ai_feedback["improvement_suggestions"],
        "strengths": ai_feedback["strengths"],
        "areas_of_concern": ai_feedback["areas_of_concern"],
        "verdict": verdict,
        "timestamp": datetime.utcnow().isoformat()
    }
