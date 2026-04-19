import requests
import json
import time
import argparse
import sys

BASE_URL = "http://127.0.0.1:8000/api/v1"

def send_whatsapp(phone, text):
    """Simulates a user messaging the WhatsApp Business Account."""
    url = f"{BASE_URL}/webhook/whatsapp"
    payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "mock_waba_id",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "contacts": [{"profile": {"name": "Test WA User"}, "wa_id": phone}],
                    "messages": [{
                        "from": phone,
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
    
    print(f"\\n[->] Sending WhatsApp (from {phone}): '{text}'")
    try:
        response = requests.post(url, json=payload)
        print(f"[<-] Server Response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[!] Error: {e}")

def send_web(session_id, text):
    """Simulates a user messaging via the Website Chat Widget."""
    url = f"{BASE_URL}/webhook/web"
    payload = {
        "channel": "WEB_WIDGET",
        "identifier": session_id,
        "content": text
    }
    
    print(f"\\n[->] Sending Web Widget Msg (from {session_id}): '{text}'")
    try:
        response = requests.post(url, json=payload)
        print(f"[<-] Server Response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[!] Error: {e}")


def simulate_agent_reply(identifier, channel, text):
    """
    Simulates an Agent typing a message in the React Dashboard and sending it to a user.
    """
    url = f"{BASE_URL}/agent/reply"
    payload = {
        "recipient_identifier": identifier,
        "channel": channel,
        "content": text
    }
    
    print(f"\\n[->] Agent Reply (to {identifier} via {channel}): '{text}'")
    try:
        response = requests.post(url, json=payload)
        print(f"[<-] Server Response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[!] Error: {e}")

def change_conversation_status(identifier, channel, status):
    """
    Simulates changing the conversation state (e.g., escalating to a human or resolving).
    """
    url = f"{BASE_URL}/agent/status"
    payload = {
        "identifier": identifier,
        "channel": channel,
        "status": status
    }
    print(f"\\n[->] Changing status for {identifier} to {status}")
    try:
        response = requests.post(url, json=payload)
        print(f"[<-] Server Response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[!] Error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Capital Max Omnichannel Mock Tester")
    subparsers = parser.add_subparsers(dest="command", help="The action to simulate")

    # Command: send_wa
    wa_parser = subparsers.add_parser("send_wa", help="Simulate a WhatsApp message")
    wa_parser.add_argument("phone", type=str, help="User phone number (e.g., 9800000000)")
    wa_parser.add_argument("message", type=str, help="The message text")

    # Command: send_web
    web_parser = subparsers.add_parser("send_web", help="Simulate a Web Widget message")
    web_parser.add_argument("session", type=str, help="User web session ID (e.g., WEB123)")
    web_parser.add_argument("message", type=str, help="The message text")

    # Command: escalate
    esc_parser = subparsers.add_parser("escalate", help="Change a conversation to PENDING_HUMAN")
    esc_parser.add_argument("identifier", type=str, help="User ID (phone or session)")
    esc_parser.add_argument("channel", type=str, choices=["WHATSAPP", "WEB_WIDGET"], help="Channel")

    # Command: resolve
    res_parser = subparsers.add_parser("resolve", help="Change a conversation back to ACTIVE_AUTO")
    res_parser.add_argument("identifier", type=str, help="User ID (phone or session)")
    res_parser.add_argument("channel", type=str, choices=["WHATSAPP", "WEB_WIDGET"], help="Channel")

    # Command: agent_reply
    reply_parser = subparsers.add_parser("agent_reply", help="Simulate an Agent sending a message")
    reply_parser.add_argument("identifier", type=str, help="User ID to reply to")
    reply_parser.add_argument("channel", type=str, choices=["WHATSAPP", "WEB_WIDGET"], help="Channel")
    reply_parser.add_argument("message", type=str, help="The message text")

    args = parser.parse_args()

    if args.command == "send_wa":
        send_whatsapp(args.phone, args.message)
    elif args.command == "send_web":
        send_web(args.session, args.message)
    elif args.command == "escalate":
        change_conversation_status(args.identifier, args.channel, "PENDING_HUMAN")
    elif args.command == "resolve":
        change_conversation_status(args.identifier, args.channel, "ACTIVE_AUTO")
    elif args.command == "agent_reply":
        simulate_agent_reply(args.identifier, args.channel, args.message)
    else:
        parser.print_help()