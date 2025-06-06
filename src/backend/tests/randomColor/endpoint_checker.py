import requests
import os
import json
from dotenv import load_dotenv

# Load the same .env file your flask app uses
load_dotenv()

# Get the API key from the environment
API_KEY = os.getenv("FLUTTER_API_KEY")
if not API_KEY:
    raise ValueError("FLUTTER_API_KEY not found in .env file")

# The URL of your running Flask app
FLASK_SERVER_URL = "http://127.0.0.1:5000/random"

headers = {
    "X-API-KEY": API_KEY,
    "Content-Type": "application/json"
}

print(f"--- Sending request to {FLASK_SERVER_URL} ---")

try:
    response = requests.get(FLASK_SERVER_URL, headers=headers)

    print(f"Status Code: {response.status_code}")
    print("Headers:")
    for key, value in response.headers.items():
        print(f"  {key}: {value}")

    print("\nBody:")
    # Try to parse and pretty-print JSON, fall back to raw text if it fails
    try:
        print(json.dumps(response.json(), indent=2))
    except json.JSONDecodeError:
        print(response.text)

    # Raise an exception for bad status codes (4xx or 5xx)
    response.raise_for_status()

except requests.exceptions.RequestException as e:
    print(f"\n--- An error occurred ---")
    print(e)