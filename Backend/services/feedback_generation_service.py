from transformers import GPT2Tokenizer, GPT2LMHeadModel
import torch
import json

# Load model and tokenizer
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")

# Set pad token to eos token (needed for generate)
tokenizer.pad_token = tokenizer.eos_token
model.eval()

async def generate_feedback(code: str, question_desc: str) -> dict:
    prompt = f"""
You are a code reviewer AI.

Task: Evaluate the following Python code in the context of the given question description.

Question Description:
{question_desc}

Code:
{code}

{{
  "feedback": {{
    "correctness": {{
      "status": "pass",
      "comments": "The function correctly calculates 2% of the input amount."
    }},
    "edge_cases": {{
      "status": "fail",
      "comments": "No validation for non-numeric inputs or negative values."
    }},
    "readability": {{
      "status": "pass",
      "comments": "The code is short and uses meaningful variable names."
    }},
    "structure": {{
      "status": "pass",
      "comments": "The function is modular and well-scoped."
    }},
    "error_handling": {{
      "status": "fail",
      "comments": "No error handling for invalid input types like strings or None."
    }},
    "performance": {{
      "status": "pass",
      "comments": "No performance issues for this simple calculation."
    }},
    "suggestions": [
      "Add input type checks to prevent runtime errors.",
      "Include docstrings to describe function purpose and parameters.",
      "Consider raising exceptions for invalid inputs."
    ],
    "summary": {{
      "overall_score": 4.2
    }}
  }}
}}

Only return valid JSON.
"""

    try:
        # Tokenize with truncation to avoid exceeding GPT-2's limit
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to("cpu")
        
        # Generate output
        outputs = model.generate(
            **inputs,
            max_new_tokens=100,
            temperature=0.7,
            pad_token_id=tokenizer.eos_token_id
        )

        # Decode response
        response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"Feedback Generation Response Text: {response_text}")
        start = response_text.find("{")
        end = response_text.rfind("}") + 1
        return json.loads(response_text[start:end])

    except Exception as e:
        return {"error": str(e), "raw": response_text if 'response_text' in locals() else ""}
