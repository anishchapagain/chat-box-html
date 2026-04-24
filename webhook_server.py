from fastapi import FastAPI, Request, Response
import uvicorn
import json

app = FastAPI()

# --- CONFIGURATION ---
# You can change this to any secret string. 
# You will enter this in the Meta Dashboard "Verify Token" field.
VERIFY_TOKEN = "OmniToken123"

@app.get("/")
async def root():
    return {"message": "WhatsApp Webhook Server is running!"}

@app.get("/webhook")
async def verify(request: Request):
    """
    Handles the verification challenge from Meta.
    """
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Webhook verified successfully!")
        return Response(content=challenge)
    
    print("❌ Webhook verification failed!")
    return Response(content="Verification failed", status_code=403)

import requests

# --- CONFIGURATION ---
# Using your credentials to send replies
# Temp Token
# ACCESS_TOKEN = "24characters_token"

# Permanent Token: 60Days
ACCESS_TOKEN = "48characters_token"
PHONE_NUMBER_ID = "1026264880577891"

def send_whatsapp_reply(to, message_text):
    """
    Sends a free-text message back to the user and returns the full response.
    """
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message_text},
    }
    response = requests.post(url, headers=headers, json=data)
    return response

@app.post("/webhook")
async def webhook(request: Request):
    """
    Handles incoming messages and status updates.
    """
    try:
        data = await request.json()
        
        entry = data.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        
        # 1. Check for Status Updates (Delivered, Read, Failed)
        statuses = value.get("statuses", [])
        if statuses:
            status = statuses[0]
            status_type = status.get("status")
            recipient = status.get("recipient_id")
            print(f"📊 Status Update: Message to {recipient} is now '{status_type}'")
            if status_type == "failed":
                errors = status.get("errors", [{}])[0]
                print(f"❌ Delivery Failed: {errors.get('message')} (Code: {errors.get('code')})")

        # 2. Check for Incoming Messages
        messages = value.get("messages", [])
        if messages:
            msg = messages[0]
            sender_id = msg.get("from")
            message_body = msg.get("text", {}).get("body", "")
            
            print(f"\n--- 📨 NEW MESSAGE FROM {sender_id} ---")
            print(f"💬 Body: '{message_body}'")

            # --- AUTO REPLY LOGIC ---
            reply_text = f"Beep Boop! 🤖 I received your message: '{message_body}'"
            print(f"🚀 Sending reply...")
            
            response = send_whatsapp_reply(sender_id, reply_text)
            result = response.json()
            
            if response.status_code == 200:
                print(f"✅ Reply accepted by Meta. ID: {result.get('messages', [{}])[0].get('id')}")
            else:
                print(f"❌ Meta Error ({response.status_code}): {json.dumps(result)}")

        return {"status": "ok"}
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    # Run the server on port 8000
    print("🚀 Starting Webhook Server on port 8000...")
    print(f"Make sure to set your Verify Token in Meta to: {VERIFY_TOKEN}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
