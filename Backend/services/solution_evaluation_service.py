# solution_evaluation_service.py - Enhanced version

from dotenv import load_dotenv
load_dotenv()

import httpx
from logging_config import logger
import os
import json

# Judge0 API URL and headers for authentication
JUDGE0_URL = os.getenv("JUDGE0_API_URL")
JUDGE0_API_HOST = os.getenv("JUDGE0_API_HOST")
JUDGE0_API_KEY = os.getenv("JUDGE0_API_KEY")

HEADERS = {
    "X-RapidAPI-Host": JUDGE0_API_HOST,
    "X-RapidAPI-Key": JUDGE0_API_KEY,
    "Content-Type": "application/json"
}

async def evaluate_code(code: str, language_id: int, stdin: str) -> dict:
    """
    Enhanced code evaluation with better error handling and null safety
    """
    # Create a dictionary called payload that contains the language_id, source_code, and stdin
    payload = {
        "language_id": language_id,
        "source_code": code,
        "stdin": stdin
    }
    
    logger.info(f"Sending code evaluation request: language_id={language_id}, stdin_length={len(stdin)}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Send a POST request to the Judge0 API with the payload and headers
            response = await client.post(JUDGE0_URL, headers=HEADERS, json=payload)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Judge0 API response status: {response.status_code}")
            
            # Validate and clean the response
            cleaned_result = validate_and_clean_judge0_response(result)
            
            return cleaned_result
            
    except httpx.TimeoutException as e:
        logger.error(f"Timeout error while evaluating code: {e}")
        return create_error_response("Timeout: Code execution took too long")
        
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error while evaluating code: {e.response.status_code} - {e.response.text}")
        return create_error_response(f"HTTP Error {e.response.status_code}: {e.response.text}")
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error from Judge0 API: {e}")
        return create_error_response("Invalid response from code execution service")
        
    except Exception as e:
        logger.critical(f"Unexpected error in evaluate_code: {e}", exc_info=True)
        return create_error_response(f"Unexpected error: {str(e)}")

def validate_and_clean_judge0_response(response: dict) -> dict:
    """
    Validate and clean Judge0 API response to handle null values
    """
    try:
        cleaned_response = {
            "stdout": response.get("stdout") or "",
            "stderr": response.get("stderr") or "",
            "compile_output": response.get("compile_output") or "",
            "message": response.get("message") or "",
            "status": {
                "id": response.get("status", {}).get("id", 0) if response.get("status") else 0,
                "description": response.get("status", {}).get("description", "Unknown") if response.get("status") else "Unknown"
            },
            "language_id": response.get("language_id"),
            "stdin": response.get("stdin", ""),
            "source_code": response.get("source_code", ""),
            "expected_output": response.get("expected_output", ""),
            "cpu_time_limit": response.get("cpu_time_limit"),
            "memory_limit": response.get("memory_limit"),
            "time": response.get("time") or "0",
            "memory": response.get("memory") or 0
        }
        
        logger.info(f"Cleaned Judge0 response: status={cleaned_response['status']['description']}")
        return cleaned_response
        
    except Exception as e:
        logger.error(f"Error cleaning Judge0 response: {e}")
        return create_error_response("Error processing execution results")

def create_error_response(error_message: str) -> dict:
    """
    Create a standardized error response when Judge0 API fails
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