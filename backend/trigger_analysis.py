import requests
import json

# URL of the local testing endpoint
url = "http://127.0.0.1:5000/api/analysis/test-local-optimized"

# Data to be sent in the POST request
# Note: You need to have a file at this path for the backend to find.
# We created an empty 'dummy_video.mp4' for this purpose.
payload = {
    "video_path": "uploads/dummy_video.mp4",
    "case_id": "keep-alive-case",
    "max_frames": 10,
    "strategy": "uniform"
}

# Headers for the request
headers = {
    "Content-Type": "application/json"
}

def trigger_analysis():
    """
    Sends a request to the backend to start a video analysis task.
    This will engage Celery and Redis, keeping the services active.
    """
    try:
        print(f"Sending request to {url} with payload:")
        print(json.dumps(payload, indent=2))
        
        response = requests.post(url, headers=headers, json=payload)
        
        print(f"\\nResponse Status Code: {response.status_code}")
        
        if response.status_code == 202:
            print("Successfully started analysis task!")
            print("Response from server:")
            print(json.dumps(response.json(), indent=2))
        else:
            print("Failed to start analysis task.")
            print("Response from server:")
            try:
                print(json.dumps(response.json(), indent=2))
            except json.JSONDecodeError:
                print(response.text)
                
    except requests.exceptions.ConnectionError as e:
        print(f"\\nError: Could not connect to the server at {url}.")
        print("Please make sure your Flask backend is running.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    trigger_analysis() 