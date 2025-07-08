# services/solution_evaluation_service.py

import os
import httpx
import json
import asyncio
from dotenv import load_dotenv
from logging_config import logger

# Load environment variables
load_dotenv()

# Judge0 API configuration
JUDGE0_API_HOST = os.getenv("JUDGE0_API_HOST")
JUDGE0_API_KEY = os.getenv("JUDGE0_API_KEY")

HEADERS = {
    "X-RapidAPI-Host": JUDGE0_API_HOST,
    "X-RapidAPI-Key": JUDGE0_API_KEY,
    "Content-Type": "application/json"
}

# Base URL (don't include submission params here)
BASE_URL = "https://judge0-ce.p.rapidapi.com"


async def evaluate_code(code: str, language_id: int, stdin: str) -> dict:
    """
    Evaluate code using Judge0's 2-step API (submit + fetch result).
    """
    payload = {
        "language_id": language_id,
        "source_code": code,
        "stdin": stdin
    }

    logger.info(f"Submitting code to Judge0 (language_id={language_id})")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Step 1: Submit code
            submit_response = await client.post(
                f"{BASE_URL}/submissions?base64_encoded=false",
                headers=HEADERS,
                json=payload
            )
            submit_response.raise_for_status()
            token = submit_response.json().get("token")

            if not token:
                logger.error("No token received from Judge0.")
                return create_error_response("Submission token not received")

            # Step 2: Poll for result
            result_url = f"{BASE_URL}/submissions/{token}?base64_encoded=false&fields=stdout,stderr,compile_output,message,status,language_id,stdin,source_code,expected_output,cpu_time_limit,memory_limit,time,memory"

            for attempt in range(10):  # retry max 10 times
                result_response = await client.get(result_url, headers=HEADERS)
                result_response.raise_for_status()
                result = result_response.json()

                status_id = result.get("status", {}).get("id", 0)
                if status_id in [1, 2]:  # 1 = In Queue, 2 = Processing
                    logger.info(f"Waiting for Judge0 result... (Attempt {attempt + 1})")
                    await asyncio.sleep(1)
                else:
                    break
            else:
                logger.warning("Judge0 timed out after polling.")
                return create_error_response("Execution timed out. Judge0 did not respond in time.")

            return validate_and_clean_judge0_response(result)

    except httpx.TimeoutException as e:
        logger.error(f"Timeout during Judge0 request: {e}")
        return create_error_response("Timeout: Code execution took too long")

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error from Judge0: {e.response.status_code} - {e.response.text}")
        return create_error_response(f"HTTP Error {e.response.status_code}: {e.response.text}")

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error from Judge0: {e}")
        return create_error_response("Failed to parse Judge0 response")

    except Exception as e:
        logger.critical(f"Unexpected error in evaluate_code: {e}", exc_info=True)
        return create_error_response(f"Unexpected error: {str(e)}")


def validate_and_clean_judge0_response(response: dict) -> dict:
    """
    Clean and validate Judge0 response, handle nulls and format output.
    """
    try:
        # Create a new dictionary to store the cleaned response
        cleaned_response = {
            # Get the stdout from the response, or an empty string if it doesn't exist
            "stdout": response.get("stdout") or "",
            # Get the stderr from the response, or an empty string if it doesn't exist
            "stderr": response.get("stderr") or "",
            # Get the compile_output from the response, or an empty string if it doesn't exist
            "compile_output": response.get("compile_output") or "",
            # Get the message from the response, or an empty string if it doesn't exist
            "message": response.get("message") or "",
            # Get the status from the response, or a default status if it doesn't exist
            "status": {
                # Get the id from the status, or 0 if it doesn't exist
                "id": response.get("status", {}).get("id", 0),
                # Get the description from the status, or "Unknown" if it doesn't exist
                "description": response.get("status", {}).get("description", "Unknown")
            },
            # Get the language_id from the response
            "language_id": response.get("language_id"),
            # Get the stdin from the response, or an empty string if it doesn't exist
            "stdin": response.get("stdin") or "",
            # Get the source_code from the response, or an empty string if it doesn't exist
            "source_code": response.get("source_code") or "",
            # Get the expected_output from the response, or an empty string if it doesn't exist
            "expected_output": response.get("expected_output") or "",
            # Get the cpu_time_limit from the response
            "cpu_time_limit": response.get("cpu_time_limit"),
            # Get the memory_limit from the response
            "memory_limit": response.get("memory_limit"),
            # Get the time from the response, or "0" if it doesn't exist
            "time": response.get("time") or "0",
            # Get the memory from the response, or 0 if it doesn't exist
            "memory": response.get("memory") or 0
        }

        # Log the cleaned response
        logger.info(f"Cleaned Judge0 response: status={cleaned_response['status']['description']}")
        return cleaned_response

    except Exception as e:
        logger.error(f"Error cleaning Judge0 response: {e}")
        return create_error_response("Error cleaning execution result")


def create_error_response(error_message: str) -> dict:
    """
    Generate standardized error response in case of failure.
    """
    return {
        "stdout": "",  # Empty string for standard output
        "stderr": error_message,  # Error message for standard error
        "compile_output": "",  # Empty string for compile output
        "message": error_message,  # Error message
        "status": {
            "id": 0,  # Error ID
            "description": "Internal Error"  # Error description
        },
        "time": "0",  # Time taken for execution
        "memory": 0,  # Memory used for execution
        "error": True  # Boolean indicating if there was an error
    }
