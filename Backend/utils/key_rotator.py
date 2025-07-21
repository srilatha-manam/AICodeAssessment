import os
import ast
import httpx
from typing import List
import asyncio

def get_env_keys(key_name: str) -> List[str]:   
    # Get the environment variable with the given key name
    # If the environment variable does not exist, return an empty list
    return ast.literal_eval(os.getenv(key_name, "[]"))


async def rotate_judge0_keys(payload: dict, host: str) -> dict:
    # Get the Judge0 API keys from the environment variables
    keys = get_env_keys("JUDGE0_API_KEYS")
    # Set the URL for the Judge0 API
    url = f"https://{host}/submissions?base64_encoded=false"
    # Set the base headers for the request
    headers_base = {
        "Content-Type": "application/json",
        "X-RapidAPI-Host": host
    }

    # Use an asynchronous HTTP client to make the request
    async with httpx.AsyncClient(timeout=20.0) as client:
        # Loop through each key
        for key in keys:
            # Set the headers for the request with the current key
            headers = {**headers_base, "X-RapidAPI-Key": key}
            try:
                # Make the POST request with the current key
                res = await client.post(url, headers=headers, json=payload)
                # If the status code is 429, continue to the next key
                if res.status_code == 429:  # Too Many Requests
                    continue  # Try next key
                # Raise an exception if the request was unsuccessful
                res.raise_for_status()
                # Get the token from the response
                token = res.json().get("token")
                # Return the token and the used key
                return {"token": token, "used_key": key}
            except Exception as e:
                # Continue to the next key if an exception is raised
                continue

    # Raise an exception if all keys have been exhausted or are invalid
    raise Exception("All Judge0 keys exhausted or invalid.")


import asyncio

async def rotate_gemini_keys(prompt: str, model_name: str = "gemini-1.5-flash", timeout: int = 30) -> str: # This function rotates through the Gemini API keys and returns the response from the first key that works
    #timeout is set to 30 seconds, can be adjusted as needed
    # Import the necessary modules
    from google.generativeai import configure, GenerativeModel

    # Get the Gemini API keys from the environment
    keys = get_env_keys("GEMINI_API_KEYS")

    # Loop through each key
    for key in keys:
        try:
            # Configure the API with the current key
            configure(api_key=key)
            # Create a new model with the given model name
            model = GenerativeModel(model_name)

            # enforce timeout on the model call
            # Wait for the model to generate content with the given prompt
            loop = asyncio.get_event_loop()  

            # Run blocking Gemini SDK call inside executor with timeout
            response = await asyncio.wait_for(
                loop.run_in_executor(None, lambda: model.generate_content(prompt)),
                timeout=timeout
            )

            # If the response is valid, return it
            if response and response.candidates:
                return response

        except asyncio.TimeoutError:
            # Timeout fallback — try next key
            continue

        except Exception as e:
            # If the exception is related to quota or exceeded, try next key
            if "quota" in str(e).lower() or "exceeded" in str(e).lower():
                continue
            else:
                # Otherwise, raise the exception
                raise e

    # If all keys have been exhausted or failed, raise an exception
    raise Exception("All Gemini keys exhausted or failed.")

