# services/gemini_feedback_template_service.py

import os
import google.generativeai as genai
import logging

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyA2yG9LDl-UnfWv7B1UnsjXPXoa8Qk-3_s")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

logger = logging.getLogger(__name__)

def build_prompt_for_feedback(code, question_description, language, judge_result, expected_outputs, actual_output) -> str:
    return f"""
You are a technical interviewer assessing a coding solution.

---

**Question Description**:
{question_description}

**Language Used**: {language}

**Submitted Code**:

**Expected Outputs**:
{expected_outputs}

**Actual Output**:
{actual_output}

**Execution Details**:
{judge_result}

---

Provide a structured JSON response with the following fields (no markdown, only raw JSON object):
- problem_solving_score (0–100)
- code_quality_score (0–100)
- efficiency_score (0–100)
- readability
- algorithm_design
- debugging_and_testing
- completion_status
- language_proficiency
- approach_summary
- peer_comparison
- improvement_suggestions
- strengths
- areas_of_concern
- ai_observations
"""

async def generate_feedback_with_gemini(code, question_description, language, judge_result, expected_outputs, actual_output) -> dict:
    try:
        prompt = build_prompt_for_feedback(
            code=code,
            question_description=question_description,
            language=language,
            judge_result=judge_result,
            expected_outputs=expected_outputs,
            actual_output=actual_output
        )
        logger.info("Sending prompt to Gemini model for feedback...")
        response = model.generate_content(prompt)

        if not response.candidates:
            logger.error("Gemini returned no candidates.")
            return {}

        text = response.candidates[0].content.parts[0].text
        import json
        return json.loads(text)

    except Exception as e:
        logger.error(f"Gemini feedback generation failed: {e}")
        raise  
