import json
import logging
from utils.key_rotator import rotate_gemini_keys

logger = logging.getLogger(__name__)

#check the prompt can be improvised further
def prompt_for_evaliation(question_title, question_description,  code, language):
    # This function generates a prompt for a test generator
    return f"""
You are an expert programming evaluator and code reviewer.

A candidate submitted the following code for the problem titled **"{question_title}"** .

### Problem Description:
{question_description}

### Code (Language: {language}):
{code}

### TASK:

1. Generate at least 3 meaningful test cases (including edge and corner cases) based on the above description and constraints.
2. Run the candidate's code logic against these cases **mentally** and compare expected vs actual outputs.
3. Evaluate correctness, logic, code quality, and give detailed structured feedback.

Return ONLY JSON in the following structure:

{{
  "correct": boolean,
  "expected": "Expected outputs joined by \\n",
  "actual": "Candidate's simulated outputs joined by \\n",
  "status": "Passed" or "Failed",
  "feedback": {{
    "problem_solving_score": 0-100,
    "code_quality_score": 0-100,
    "algorithm_design": "string",
    "debugging_and_testing": "string",
    "completion_status": "string",
    "language_proficiency": "string",
    "readability": "string",
    "critical_errors": ["string"],
    "problem_understanding_issues": ["string"],
    "language_specific_issues": ["string"],
    "approach_summary": "string",   
    "improvement_suggestions": ["string"],
    "strengths": ["string"],
    "areas_of_concern": ["string"],
    "ai_observations": ["string"]
  }}
}}
"""

# Define an asynchronous function to generate test and feedback using Gemini
async def code_evaluation_by_gemini(code, question_title, question_description, language):
    try:
        prompt = prompt_for_evaliation(
            question_title, question_description, code, language
        )

        logger.info("Sending Gemini test generation + feedback prompt...")
        response = await rotate_gemini_keys(prompt)

        if not response or not response.candidates or not response.candidates[0].content.parts:
            logger.error("Gemini response is empty or malformed.")
            return {}

        text = response.candidates[0].content.parts[0].text.strip()
        if text.startswith("```json"):
            text = text[len("```json"):].strip()
        if text.endswith("```"):
            text = text[:-3].strip()

        return json.loads(text)
    except Exception as e:
        logger.error(f"Failed to generate Gemini-only test & feedback: {e}", exc_info=True)
        return {}
