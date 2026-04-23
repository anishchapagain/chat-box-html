import requests
import json

# --- CONFIGURATION ---
# Using the token from your 'Access Token.txt'
ACCESS_TOKEN = "EAASH52f0fPMBRRkjQv25nsujiW6vt1X7ua3uKS9FZBOM9u7rX2UdPbLTO0sgxty92dk30wIz8TIZCPNX8kdufzOyRpvUjrkor0N0nEpezYkN4FlI7zVh9TbAjsRNSxXh5wcCl97aFd59Y47ilWTv5bGVwrHV5fxFTT4St3EsyqENFl3v6foEMOsXE3ecj3ZBZCYcAZCWiKZCr5ZCujdQLHMO9FWZCi7cMAAZCM2bE99L6ZCekmTZBbaM46FAUp8Bg9zgZBJAKk4TQzRs84YlirdgK8LwmG9P"
PHONE_NUMBER_ID = "1026264880577891"
RECIPIENT_NUMBER = "9779840065449"

url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json",
}

# Sending the standard 'hello_world' template
data = {
    "messaging_product": "whatsapp",
    "to": RECIPIENT_NUMBER,
    "type": "template",
    "template": {
        "name": "hello_world",
        "language": {"code": "en_US"},
    },
}

print(f"Sending message to {RECIPIENT_NUMBER}...")
try:
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    print("\n✅ Success!")
    print("\n--- RESPONSE JSON ---")
    print(json.dumps(response.json(), indent=2))
except requests.exceptions.HTTPError as e:
    print("\n❌ Failed!")
    print(f"Status Code: {response.status_code}")
    print("\n--- ERROR DETAIL ---")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
except Exception as e:
    print(f"\nAn error occurred: {e}")
