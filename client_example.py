"""Simple streaming client for local testing."""
import json
import sys
import uuid

import requests

BASE_URL = "http://localhost:8000"


def chat(message: str) -> None:
    payload = {
        "messages": [{"role": "user", "content": message}],
        "conversationId": str(uuid.uuid4()),
    }
    with requests.post(f"{BASE_URL}/api/chat", json=payload, stream=True, timeout=60) as resp:
        if resp.status_code != 200:
            print(f"Error {resp.status_code}: {resp.text}")
            return
        for line in resp.iter_lines():
            if not line:
                continue
            data = json.loads(line)
            if "delta" in data:
                print(data["delta"], end="", flush=True)
            elif data.get("done"):
                print()  # final newline


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "What is your current role?"
    chat(question)
