import requests
import json
import time
import sys

URL = "http://127.0.0.1:8000/api/v1/webhook/whatsapp"

def send_mock_message(phone_number, text):
    payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "mock_waba_id",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {
                        "display_phone_number": "16505551111",
                        "phone_number_id": "mock_phone_id"
                    },
                    "contacts": [{
                        "profile": {"name": "Test User"},
                        "wa_id": phone_number
                    }],
                    "messages": [{
                        "from": phone_number,
                        "id": "wamid.mock123456789",
                        "timestamp": str(int(time.time())),
                        "type": "text",
                        "text": {"body": text}
                    }]
                },
                "field": "messages"
            }]
        }]
    }

    try:
        response = requests.post(URL, json=payload)
        print(f"[{response.status_code}] Sent '{text}' from {phone_number}")
    except Exception as e:
        print(f"Failed to connect to backend: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python mock_whatsapp.py <phone_number> <message_text>")
        print("Example: python mock_whatsapp.py 9800000000 'I need human help'")
    else:
        phone = sys.argv[1]
        msg = " ".join(sys.argv[2:])
        send_mock_message(phone, msg)