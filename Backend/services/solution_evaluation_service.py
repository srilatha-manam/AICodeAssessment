from dotenv import load_dotenv
load_dotenv()

import httpx
from ..logging_config import logger
import os
# This module provides functionality to evaluate code solutions using the Judge0 API.
# It sends the code, language ID, and input to the API and returns the evaluation result.

# Judge0 API URL and headers for authentication
JUDGE0_URL = "https://judge0-ce.p.rapidapi.com/submissions?base64_encoded=false&wait=true"
HEADERS = {
    "X-RapidAPI-Host": os.getenv("JUDGE0_API_HOST"),
    "X-RapidAPI-Key": os.getenv("JUDGE0_API_KEY")
}

# Define an asynchronous function called evaluate_code that takes the language_id, and a string representing the stdin
async def evaluate_code(code: str, language_id: int, stdin: str) -> dict:
    # Create a dictionary called payload that contains the language_id, source_code, and stdin
    payload = {
        "language_id": language_id,
        "source_code": code,
        "stdin": stdin
    }

    # Use an asynchronous with statement to create an httpx.AsyncClient object
    try:
        async with httpx.AsyncClient() as client:
            # Send a POST request to the Judge0 API with the payload and headers            
            response = await client.post(JUDGE0_URL, headers=HEADERS, json=payload)            
            response.raise_for_status()            
            return response.json()
    except httpx.HTTPStatusError as e:
        # Log an error message if an HTTP error occurs
        logger.error(f"HTTP error while evaluating code: {e.response.status_code} - {e.response.text}")
        raise
    except Exception as e:
        # Log a critical error message if an unexpected error occurs
        logger.critical(f"Unexpected error in evaluate_code: {e}", exc_info=True)
        raise
