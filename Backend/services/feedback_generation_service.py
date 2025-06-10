# # Feedback Generation Service using Hugging Face Inference API
# import os
# import requests
# import logging


# logger = logging.getLogger(__name__)

# HUGGINGFACE_API_TOKEN = os.getenv("HF_TOKEN")  
# HF_MODEL = "bigcode/starcoder2-15b"  # Good default for code tasks

# def generate_feedback(code: str, question_desc: str) -> dict:
#     """
#     Calls Hugging Face's Inference API to generate code review feedback.
#     """
#     # Create a prompt for the model to generate feedback
#     prompt = f"""   

#     Question:
#     {question_desc}

#     Submitted Code:
#     {code}

#     Evaluate and return feedback in this structured JSON format:
#     {{
#       "correctness": {{
#         "status": "pass/fail",
#         "comments": "..."
#       }},
#       "edge_cases": {{
#         "status": "pass/fail",
#         "comments": "..."
#       }},
#       "readability": {{
#         "status": "pass/fail",
#         "comments": "..."
#       }},
#       "structure": {{
#         "status": "pass/fail",
#         "comments": "..."
#       }},
#       "error_handling": {{
#         "status": "pass/fail",
#         "comments": "..."
#       }},
#       "performance": {{
#         "status": "pass/fail",
#         "comments": "..."
#       }},
#       "suggestions": [
#         "Improvement 1",
#         "Improvement 2"
#       ],
#       "summary": {{
#         "overall_score": 0.0,
#         "remarks": "..."
#       }}
#     }}

# Only return the JSON object, nothing else.
#     """

#     # Set the headers for the API request
#     headers = {
#         "Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}",
#         "Content-Type": "application/json"
#     }

#     try:
#         print("inside feedback generation service")
#         # Make the API request
#         response = requests.post(
#             f"https://api-inference.huggingface.co/{HF_MODEL}",
#             headers=headers,
#             json={"inputs": prompt},
#             timeout=30
#         )
#         print("after response")
#         response.raise_for_status()
#         print("before parsing")
#         output_text = response.json()[0]["generated_text"]
#         print("after parsing")
#         # Try to extract JSON from model output
#         import json
#         start_index = output_text.find("{")
#         end_index = output_text.rfind("}") + 1
#         print(f"before json load")
#         json_text = output_text[start_index:end_index]
#         print(f"after json load")
#         return json.loads(json_text)

#     except Exception as e:
#         # Log any errors that occur during the API request
#         logger.error(f"Feedback generation failed: {e}")
#         return {"error": "Failed to generate or parse feedback."}

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
MODEL_ID="bigcode/tiny_starcoder_py"
#MODEL_ID = "Salesforce/codegen2-350M"
#MODEL_ID = "Salesforce/codegen2-1B"  # or WizardCoder
#MODEL_ID = "codellama/CodeLlama-7b-Instruct-hf"  # Good default for code tasks
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=torch.float16, device_map="auto")

async def generate_feedback(code: str, question_desc: str) -> dict:
    prompt = f"""
You are a code reviewer AI.

Question:
{question_desc}

Submitted Code:
{code}

Please evaluate the code based on the following criteria and return feedback in valid JSON format:

{{
  "correctness": {{ "status": "pass/fail", "comments": "..." }},
  "edge_cases": {{ "status": "pass/fail", "comments": "..." }},
  "readability": {{ "status": "pass/fail", "comments": "..." }},
  "structure": {{ "status": "pass/fail", "comments": "..." }},
  "error_handling": {{ "status": "pass/fail", "comments": "..." }},
  "performance": {{ "status": "pass/fail", "comments": "..." }},
  "suggestions": ["Improvement 1", "Improvement 2"],
  "summary": {{ "overall_score": 0.0, "remarks": "..." }}
}}

Only return valid JSON.
"""
    print("inside feedback generation service")
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    print(inputs)
    outputs = model.generate(**inputs, max_new_tokens=512, temperature=0.7)
    print(outputs)
    response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(response_text)
    # Extract JSON only
    import json
    try:
        start = response_text.find("{")
        end = response_text.rfind("}") + 1
        print(f"Extracting JSON")
        return json.loads(response_text[start:end])
    except Exception as e:
        return {"error": "Could not parse model output", "raw": response_text}
