import httpx
import json
import dotenv
import os

dotenv.load_dotenv("config.env")

base_url = os.getenv("API_URL", "https://api.openai.com/v1")
api_key = os.getenv("API_KEY")
model_name = os.getenv("MODEL_NAME")

# Open Prompt File
with open("./Functions/prompt.txt", "r", encoding="utf-8") as f:
    prompt = f.read()

# Chat History Init
chat_history = [
    {
        "role": "system",
        "content": prompt
    },
    {
        "role": "user",
        "content": "How are you?"
    }
]

def request_api():
    global base_url, api_key, chat_history
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    r_json = {
        "model": model_name,
        "messages": chat_history
    }
    resp = httpx.post(
        f"{base_url}/chat/completions",
        headers=headers,
        json=r_json
    )
    return resp.text

print(request_api())