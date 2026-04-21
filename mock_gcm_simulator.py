import requests
import time
import sys

URL = "http://127.0.0.1:8000/api/v1/webhook/whatsapp"

# Simulation Scenarios: [Language/Type, Message, Expected Intent/Behavior]
GCM_SCENARIOS = [
    # English
    ("EN", "Where is Global College of Management?", "location"),
    ("EN", "How to apply for admission?", "admission_apply"),
    ("EN", "Do you have a basketball court?", "sports_facilities"),
    
    # Romanized Nepali (NE_ROM)
    ("NE_ROM", "college kahan chha?", "location"),
    ("NE_ROM", "admission kasari line?", "admission_apply"),
    ("NE_ROM", "scholarship pauchha ki nai?", "scholarship_info"),
    
    # Devanagari Nepali (NE)
    ("NE", "कलेज कहाँ छ?", "location"),
    ("NE", "भर्ना कसरी हुने?", "admission_apply"),
    
    # Guardrails: Human Escalation
    ("GUARD", "I need urgent help from a human", "PENDING_HUMAN (Escalation)"),
    ("GUARD", "talk to person", "PENDING_HUMAN (Escalation)"),
    
    # Guardrails: Profanity
    ("PROFANITY", "you are a badword1", "Flagged/No Processing"),
]

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
                        "profile": {"name": "GCM Tester"},
                        "wa_id": phone_number
                    }],
                    "messages": [{
                        "from": phone_number,
                        "id": f"wamid.{int(time.time())}",
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
        return response.status_code
    except Exception as e:
        print(f"Error: {e}")
        return None

def run_simulation():
    print("="*50)
    print("GCM EDUCATION DOMAIN: BATCH SIMULATION")
    print("="*50)
    
    test_phone = "980000GCM"
    
    for lang, msg, expected in GCM_SCENARIOS:
        print(f"\n[TESTING {lang}] Message: '{msg}'")
        print(f"Expected: {expected}")
        status = send_mock_message(test_phone, msg)
        if status == 200:
            print("Status: SUCCESS (Message Delivered to Backend)")
        else:
            print(f"Status: FAILED (Code: {status})")
        time.sleep(1) # Small delay to avoid timestamp collision
        
    print("\n" + "="*50)
    print("SIMULATION COMPLETE")
    print("Check backend console logs and 'omnichannel_events.log' for NLU matches.")
    print("="*50)

if __name__ == "__main__":
    run_simulation()
