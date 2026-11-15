
import requests
import os
from dotenv import load_dotenv
print("========== API.PY LOADED ==========")


# Load API key from .env file
load_dotenv()

api_key = os.getenv("JOOBLE_API_KEY")

url = f"https://jooble.org/api/{api_key}" if api_key else None


# Fetch jobs from Jooble
def fetch_jobs(role):

    print("========== FETCH_JOBS FUNCTION CALLED ==========")
    # Check API key
    if not api_key:
        raise ValueError("Jooble API key not found in .env file.")

    # Prepare request data
    data = {
        "keywords": role,
        "location": "India"
    }

    try:

        # Send request to Jooble
        response = requests.post(
            url,
            json=data,
            timeout=30
        )

        response.raise_for_status()

        # Convert response into JSON
        result = response.json()

        # Debug information
        print("\n--- JOOBLE API DEBUG ---")

        print("Response keys:", result.keys())

        print("Total jobs:", result.get("totalCount"))

        print("Jobs received:", len(result.get("jobs", [])))

        if result.get("jobs"):
            print("First job:", result["jobs"][0])

        # Return job data
        return {
            "total_count": result.get("totalCount", 0),
            "jobs": result.get("jobs", [])
        }

    except requests.RequestException as error:

        raise RuntimeError(
            f"Unable to fetch jobs: {error}"
        )

    except ValueError as error:

        raise RuntimeError(
            f"Invalid response from Jooble API: {error}"
        )
