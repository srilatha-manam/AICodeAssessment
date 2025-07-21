# services/solution_evaluation_service.py

import os
import httpx
import asyncio
from dotenv import load_dotenv
from logging_config import logger
from utils.key_rotator import rotate_judge0_keys  

# Load environment variables
load_dotenv()

# Base URL (don't include submission params here)
BASE_URL = "https://judge0-ce.p.rapidapi.com"
JUDGE0_API_HOST = os.getenv("JUDGE0_API_HOST")

async def evaluate_code(code: str, language_id: int, stdin: str) -> dict:
    """
    Evaluate code using Judge0 with key rotation support.
    """
    payload = {
        "language_id": language_id,
        "source_code": code,
        "stdin": stdin
    }
    print(payload)
    logger.info(f"Submitting code to Judge0 (language_id={language_id})")

    try:
        # Submit code using key rotation
        submit_result = await rotate_judge0_keys(payload, JUDGE0_API_HOST) #API fallback
        
        token = submit_result.get("token")
        used_key = submit_result.get("used_key")

        if not token:
            logger.error("No token received from Judge0.")
            return create_error_response("Submission token not received")

        # Step 2: Poll for result
        result_url = f"{BASE_URL}/submissions/{token}?base64_encoded=false&fields=stdout,stderr,compile_output,message,status,language_id,stdin,source_code,expected_output,cpu_time_limit,memory_limit,time,memory"
        headers = {
            "Content-Type": "application/json",
            "X-RapidAPI-Host": JUDGE0_API_HOST,
            "X-RapidAPI-Key": used_key
        }
        timeout_config = httpx.Timeout(timeout=30.0, read=90.0) # Set read timeout to 90 seconds

        async with httpx.AsyncClient(timeout=timeout_config) as client: # Used 30 second timeout to avoid hanging indefinitely
            for attempt in range(10):  # Maximum of 10 attempts for retry
                print("Polling for Judge0 result...")
                result_response = await client.get(result_url, headers=headers)
                result_response.raise_for_status()
                result = result_response.json()

                status_id = result.get("status", {}).get("id", 0)
                print(f"Judge0 status ID: {status_id}")
                if status_id in [1, 2]:  # 1 = In Queue, 2 = Processing
                    logger.info(f"Waiting for Judge0 result... (Attempt {attempt + 1})")
                    print(f"Waiting for Judge0 result... (Attempt {attempt + 1})")
                    await asyncio.sleep(1) # Wait 1 second before next attempt
                elif status_id == 3:
                    logger.info("Judge0 execution completed successfully.")
                    break
                else:
                    break
            else:
                logger.warning("Judge0 timed out after polling.")
                return create_error_response("Execution timed out. Judge0 did not respond in time.")
            print(f"Judge0 result: {result}")    
            print("calling validate_and_clean_judge0_response")
            return validate_and_clean_judge0_response(result)

    except Exception as e:
        logger.critical(f"Unexpected error in evaluate_code: {e}", exc_info=True)
        return create_error_response(f"Unexpected error: {str(e)}")


def validate_and_clean_judge0_response(response: dict) -> dict:
    """
    Clean and validate Judge0 response, handle nulls and format output.
    """
    try:
        print(f"now i am in validate_and_clean_judge0_response")
        cleaned_response = {
            "stdout": response.get("stdout") or "",
            "stderr": response.get("stderr") or "",
            "compile_output": response.get("compile_output") or "",
            "message": response.get("message") or "",
            "status": {
                "id": response.get("status", {}).get("id", 0),
                "description": response.get("status", {}).get("description", "Unknown")
            },
            "language_id": response.get("language_id"),
            "stdin": response.get("stdin") or "",
            "source_code": response.get("source_code") or "",
            "expected_output": response.get("expected_output") or "",
            "cpu_time_limit": response.get("cpu_time_limit"),
            "memory_limit": response.get("memory_limit"),
            "time": response.get("time") or "0",
            "memory": response.get("memory") or 0
        }
        print(f"Cleaned Judge0 response: {cleaned_response}")
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
        "stdout": "",
        "stderr": error_message,
        "compile_output": "",
        "message": error_message,
        "status": {
            "id": 0,
            "description": "Internal Error"
        },
        "time": "0",
        "memory": 0,
        "error": True
    }
