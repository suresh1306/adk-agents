
import os
import requests

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("ERROR: GROQ_API_KEY not set")
    exit(1)

try:
    response = requests.get(
        "https://api.groq.com/openai/v1/models",
        headers={"Authorization": f"Bearer {api_key}"}
    )
    print(f"Status: {response.status_code}")
    print("✅ Connection successful!")
except Exception as e:
    print(f"❌ Connection failed: {e}")