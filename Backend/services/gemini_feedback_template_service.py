import logging
import json
from dotenv import load_dotenv
from utils.key_rotator import rotate_gemini_keys  


load_dotenv()
logger = logging.getLogger(__name__)

def build_prompt_for_feedback(code, question_description, language, judge_result, expected_outputs, actual_output) -> str:
    # This function builds a prompt for feedback on a candidate's code submission
    return f"""
You are a technical interviewer evaluating a candidate’s code submission for a programming challenge.

Please review the provided information below:

---

**Question Description**:  
{question_description}

**Language Used**:  
{language}

**Submitted Code**:  
{code}

**Expected Outputs**:  
{expected_outputs}

**Actual Output**:  
{actual_output}

**Execution Details** (from code runner / Judge0):  
{judge_result}
---
Your goal is to deeply analyze the candidate's solution and return **honest, structured feedback**.

Please consider the following when evaluating:
- The **logical correctness** of the approach.
- Whether the candidate **understood the problem** or misinterpreted key parts.
- Quality and **readability** of the code structure and syntax, based on the programming language.
- Use of efficient or inefficient algorithms.
- Handling of **edge cases**, failure conditions, and completeness.
- Any **compilation or runtime errors**, and whether they were fixed.
- Comments or structure suggesting multiple **approaches attempted**.
- Partial correctness (e.g., only some test cases passed).
- Any signs of **template reuse** or generic code not tailored to the problem.

---

Return a **raw JSON object only**, with no markdown or formatting. The object must include:

"problem_solving_score": int (0 to 100),         
  "code_quality_score": int (0 to 100),         
  "algorithm_design": "string",                    
  "debugging_and_testing": "string",               
  "completion_status": "string",                   
  "language_proficiency": "string",                 
  "readability": "string",                          
  "critical_errors": ["string"],                    
  "problem_understanding_issues": ["string"],       
  "language_specific_issues": ["string"],           
  "approach_summary": "string",                    
  "peer_comparison": "string",                      
  "improvement_suggestions": ["string"],            
  "strengths": ["string"],                          
  "areas_of_concern": ["string"],                   
  "ai_observations": ["string"]                    

"""

#retry added in key rotation function
async def generate_feedback_with_gemini(code, question_description, language, judge_result, expected_outputs, actual_output) -> dict:
    # Try to generate feedback using the Gemini model
    try:
        # Build the prompt for the feedback
        prompt = build_prompt_for_feedback(
            code=code,
            question_description=question_description,
            language=language,
            judge_result=judge_result,
            expected_outputs=expected_outputs,
            actual_output=actual_output
        )

        # Log that the prompt is being sent to the Gemini model with key rotation
        logger.info("Sending prompt to Gemini model with key rotation...")
        # Send the prompt to the Gemini model and get the response
        response = await rotate_gemini_keys(prompt)

        # Check if the response is empty or missing required parts
        if not response or not response.candidates or not response.candidates[0].content.parts:
            # Log an error if the response is empty or missing required parts
            logger.error("Gemini response is empty or missing required parts.")
            # Return an empty dictionary
            return {}

        # Get the text from the response
        text = response.candidates[0].content.parts[0].text.strip()

        # Strip markdown-style formatting
        if text.startswith("```json"):
            text = text[len("```json"):].strip()
        if text.endswith("```"):
            text = text[:-3].strip()

        # Log the cleaned Gemini text
        logger.debug(f"Cleaned Gemini text:\n{text}")

        # Try to parse the text as JSON
        try:
            # Return the parsed JSON
            return json.loads(text)
        # Catch any JSONDecodeError and log an error
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini output: {e}\nText was:\n{text}")
            # Return an empty dictionary
            return {}

    # Catch any other exceptions and log an error
    except Exception as e:
        logger.error(f"Gemini feedback generation failed: {e}", exc_info=True)
        # Return an empty dictionary
        return {}
