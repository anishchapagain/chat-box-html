from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.schemas import IncomingMessage, ChannelType
from app.services.omnichannel import OmnichannelService
from app.core.config import settings

router = APIRouter()

@router.post("/webhook/web")
async def web_webhook(message: IncomingMessage, db: Session = Depends(get_db)):
    """
    Endpoint for the React/HTML Web Widget.
    """
    if message.channel != ChannelType.WEB_WIDGET:
        raise HTTPException(status_code=400, detail="Invalid channel type for this endpoint")
        
    OmnichannelService.process_incoming_message(db, message)
    return {"status": "success"}

@router.get("/webhook/whatsapp")
async def verify_whatsapp_webhook(request: Request):
    """
    Required by Meta to verify the webhook URL during setup.
    """
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
            return int(challenge)
        raise HTTPException(status_code=403, detail="Forbidden")
    raise HTTPException(status_code=400, detail="Bad Request")

@router.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Receives incoming WhatsApp messages from Meta.
    """
    body = await request.json()
    
    # Very basic parsing of the WhatsApp webhook payload
    try:
        if body.get("object") == "whatsapp_business_account":
            for entry in body.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    if "messages" in value:
                        for msg in value["messages"]:
                            phone_number = msg.get("from")
                            
                            # Handle simple text messages
                            if msg.get("type") == "text":
                                content = msg["text"]["body"]
                                
                                # Normalize to our generic schema
                                incoming = IncomingMessage(
                                    channel=ChannelType.WHATSAPP,
                                    identifier=phone_number,
                                    content=content
                                )
                                
                                # Route through generic core service
                                OmnichannelService.process_incoming_message(db, incoming)
                                
        return {"status": "success"}
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return {"status": "error"}