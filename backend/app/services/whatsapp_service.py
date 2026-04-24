import requests
import json
from app.core.config import settings
from app.core.audit_log import log_event

class WhatsAppService:
    @staticmethod
    def send_text_message(to: str, text: str, conversation_id: str | None = None):
        """
        Sends a free-text message using the Meta Graph API.
        """
        url = f"https://graph.facebook.com/v19.0/{settings.WHATSAPP_PHONE_ID}/messages"
        headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
            "Content-Type": "application/json",
        }
        data = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": text},
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            result = response.json()
            
            if response.status_code == 200:
                msg_id = result.get("messages", [{}])[0].get("id")
                print(f"✅ WhatsApp Sent: {msg_id}")
                return True, msg_id
            else:
                error_msg = result.get("error", {}).get("message", "Unknown error")
                print(f"❌ WhatsApp Error: {error_msg}")
                log_event(
                    "whatsapp_delivery_failed",
                    conversation_id=conversation_id,
                    recipient=to,
                    error=error_msg
                )
                return False, error_msg
        except Exception as e:
            print(f"❌ WhatsApp Connection Error: {e}")
            return False, str(e)

    @staticmethod
    def send_template_message(to: str, template_name: str, language_code: str = "en_US", conversation_id: str | None = None):
        """
        Sends a template message (useful for initiating conversations).
        """
        url = f"https://graph.facebook.com/v19.0/{settings.WHATSAPP_PHONE_ID}/messages"
        headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
            "Content-Type": "application/json",
        }
        data = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code},
            },
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            result = response.json()
            if response.status_code == 200:
                return True, result.get("messages", [{}])[0].get("id")
            return False, result.get("error", {}).get("message")
        except Exception as e:
            return False, str(e)
