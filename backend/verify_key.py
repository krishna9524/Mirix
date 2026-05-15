import os
import requests
from dotenv import load_dotenv

# 1. Force load the .env file
load_dotenv()
key = os.getenv("OPENROUTER_API_KEY")

print(f"Testing Key: {key}")

# 2. Send a manual request to OpenRouter
try:
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {key}",
            "HTTP-Referer": "https://mirix.app", # Fake production URL to pass strict checks
            "X-Title": "Mirix Debugger",
            "Content-Type": "application/json"
        },
        json={
            "model": "mistralai/mistral-7b-instruct:free",
            "messages": [{"role": "user", "content": "Test"}]
        }
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.text}")

    if response.status_code == 200:
        print("\n✅ SUCCESS! The key is valid. The issue is in your App code.")
    else:
        print("\n❌ FAILURE! The key/account is dead. You need a new OpenRouter account.")

except Exception as e:
    print(f"Connection Error: {e}")