# services/gemini_feedback_template_service.py

import os
import google.generativeai as genai
import logging
import json
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "fallback_if_missing")
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
{code}

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

        if not response or not response.candidates or not response.candidates[0].content.parts:
            logger.error("Gemini response is empty or missing required parts.")
            return {}

        text = response.candidates[0].content.parts[0].text.strip()

        # ✅ Strip markdown-style formatting
        if text.startswith("```json"):
            text = text[len("```json"):].strip()
        if text.endswith("```"):
            text = text[:-3].strip()

        logger.debug(f"Cleaned Gemini text:\n{text}")

        # ✅ Safely parse JSON
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini output: {e}\nText was:\n{text}")
            return {}

    except Exception as e:
        logger.error(f"Gemini feedback generation failed: {e}", exc_info=True)
        return {}
