"""
Example usage of the ChatBot API with session management.
This demonstrates how to interact with the API endpoints.
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def main():
    print("=" * 50)
    print("ChatBot API - Example Usage")
    print("=" * 50)

    # 1. Health check
    print("\n1. Health Check")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # 2. Send first message — no session_id yet, server will create one
    print("\n2. First Message (new session)")
    response = requests.post(
        f"{BASE_URL}/chat",
        json={"message": "siapa kamu?"}
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")

    # Save session_id for subsequent requests
    session_id = data["session_id"]
    headers = {"X-Session-Id": session_id}
    print(f"\n>>> Using session_id: {session_id}")

    # 3. Send second message (maintains context via session)
    print("\n3. Second Message (with context)")
    response = requests.post(
        f"{BASE_URL}/chat",
        json={"message": "apa nama kamu?"},
        headers=headers
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # 4. Reference previous conversation
    print("\n4. Reference Previous Conversation")
    response = requests.post(
        f"{BASE_URL}/chat",
        json={"message": "apa yang kami bicarakan tadi?"},
        headers=headers
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # 5. Get conversation history
    print("\n5. Conversation History")
    response = requests.get(f"{BASE_URL}/history", headers=headers)
    print(f"Status: {response.status_code}")
    history = response.json()
    print(f"Total messages: {len(history['history'])}")
    print(json.dumps(history, indent=2))

    # 6. Clear history (keeps session alive)
    print("\n6. Clear History")
    response = requests.post(f"{BASE_URL}/clear", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # 7. Delete session entirely
    print("\n7. Delete Session")
    response = requests.delete(f"{BASE_URL}/session", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    print("\n" + "=" * 50)
    print("Example completed!")
    print("=" * 50)

if __name__ == "__main__":
    main()