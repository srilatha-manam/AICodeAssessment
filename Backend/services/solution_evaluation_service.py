import httpx
# This module provides functionality to evaluate code solutions using the Judge0 API.
# It sends the code, language ID, and input to the API and returns the evaluation result.

# Judge0 API URL and headers for authentication
JUDGE0_URL = "https://judge0-ce.p.rapidapi.com/submissions?base64_encoded=false&wait=true"
HEADERS = {
    "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com",
    "X-RapidAPI-Key": "<e4cfe2c982msh0c0641fd6f48054p19a36ajsn8f073aa0610e>"  # 🔐 Replace with your actual key
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
    async with httpx.AsyncClient() as client:
        # Send a POST request to the JUDGE0_URL with the payload and HEADERS
        response = await client.post(JUDGE0_URL, headers=HEADERS, json=payload)
        # Raise an exception if the response status code is not 200
        # Return the response as a json object
        response.raise_for_status()
        return response.json()
