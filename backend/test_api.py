import requests
import json
import os
import time

# --- Configuration ---
BASE_URL = "http://127.0.0.1:8000"
QUERY_ENDPOINT = f"{BASE_URL}/api/tutor/query/"
# NOTE: Replace 'test_audio.mp3' with a real, small audio file in your backend folder
# Or use a placeholder file if you don't have one ready (though a real file is better)
AUDIO_FILE_PATH = "test_audio.mp3" 

def test_root_endpoint():
    print(f"--- 1. Testing GET {BASE_URL}/ ---")
    try:
        response = requests.get(BASE_URL)
        response.raise_for_status()
        print(f"✅ Root Health Check: Status {response.status_code}")
        print(f"   Response: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Root Check FAILED: {e}")

def test_query_endpoint():
    print(f"\n--- 2. Testing POST {QUERY_ENDPOINT} (Full Pipeline) ---")
    if not os.path.exists(AUDIO_FILE_PATH):
        print(f"❌ ERROR: Test audio file not found at '{AUDIO_FILE_PATH}'.")
        print("   Please place a small .mp3 or .wav file in the backend folder named 'test_audio.mp3'.")
        return

    # Use a dummy file for the upload
    files = {'audio_file': (AUDIO_FILE_PATH, open(AUDIO_FILE_PATH, 'rb'), 'audio/mpeg')}

    try:
        start_time = time.time()
        response = requests.post(QUERY_ENDPOINT, files=files)
        end_time = time.time()
        
        response.raise_for_status() # Raise exception for 4xx or 5xx status codes
        
        data = response.json()
        
        print(f"✅ Pipeline Success: Status {response.status_code} in {end_time - start_time:.2f}s")
        print("\n--- Pipeline Data Received ---")
        print(f"Query (Whisper Mock): {data.get('query')}")
        print(f"Explanation (FLAN-T5): {data.get('explanation_text')[:60]}...")
        print(f"Lip-Sync JSON Mock: {data.get('lip_sync_json')}")
        print(f"Audio Stream URL: {data.get('audio_url')}")
        
        # NOTE: Check your Uvicorn terminal for the MongoDB log confirmation!

    except requests.exceptions.HTTPError as e:
        print(f"❌ Pipeline FAILED: HTTP Error {response.status_code}")
        try:
            print(f"   Detail: {response.json().get('detail')}")
        except:
            print("   Response was not JSON.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Pipeline FAILED: Connection Error: {e}")

if __name__ == "__main__":
    test_root_endpoint()
    test_query_endpoint()