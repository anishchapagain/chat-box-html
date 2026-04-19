from datetime import datetime
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.core.database import get_db
from app.core.schemas import IncomingMessage, ChannelType, ConversationStatus
from app.services.omnichannel import OmnichannelService
from app.core.config import settings
from app.core.audit_log import log_event

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


# --- NEW ENDPOINTS FOR AGENT DASHBOARD & TESTING ---

from pydantic import BaseModel

class StatusChangeRequest(BaseModel):
    conversation_id: str | None = None
    identifier: str
    channel: ChannelType
    status: str

class AgentReplyRequest(BaseModel):
    conversation_id: str | None = None
    recipient_identifier: str
    channel: ChannelType
    content: str

@router.get("/agent/chats")
async def get_agent_chats(db: Session = Depends(get_db)):
    """
    Loads open chats for the dashboard from DB so refresh does not lose state.
    """
    from app.models.models import Conversation

    open_statuses = [
        ConversationStatus.ACTIVE_AUTO,
        ConversationStatus.PENDING_HUMAN,
        ConversationStatus.ACTIVE_HUMAN,
    ]
    conversations = (
        db.query(Conversation)
        .options(joinedload(Conversation.user), joinedload(Conversation.logs))
        .filter(Conversation.status.in_(open_statuses))
        .order_by(Conversation.created_at.desc())
        .all()
    )

    chats = []
    for conv in conversations:
        logs = sorted(conv.logs, key=lambda log: log.timestamp or datetime.min)
        chats.append(
            {
                "id": conv.id,
                "user_identifier": conv.user.identifier if conv.user else "",
                "status": conv.status.value,
                "channel": conv.channel.value,
                "messages": [
                    {
                        "sender": log.sender_type.value,
                        "content": log.message_content,
                        "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                    }
                    for log in logs
                ],
            }
        )

    return {"chats": chats}

@router.post("/agent/status")
async def change_status(req: StatusChangeRequest, db: Session = Depends(get_db)):
    """Simulates an agent claiming or resolving a chat from the dashboard."""
    from app.models.models import User, Conversation
    conv = None

    if req.conversation_id:
        conv = db.query(Conversation).filter(Conversation.id == req.conversation_id).first()
    else:
        user = db.query(User).filter(User.identifier == req.identifier).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        conv = (
            db.query(Conversation)
            .filter(
                Conversation.user_id == user.id,
                Conversation.channel == req.channel,
                Conversation.status.in_(
                    [
                        ConversationStatus.PENDING_HUMAN,
                        ConversationStatus.ACTIVE_HUMAN,
                        ConversationStatus.ACTIVE_AUTO,
                    ]
                ),
            )
            .order_by(Conversation.created_at.desc())
            .first()
        )
    
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    conv.status = req.status
    db.commit()
    log_event(
        "conversation_status_changed",
        conversation_id=conv.id,
        user_identifier=req.identifier,
        channel=req.channel,
        new_status=req.status,
    )
    
    # Notify dashboard of status change
    import asyncio
    from app.api.websockets import manager
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(manager.broadcast({"type": "status_change", "conversation_id": conv.id, "new_status": req.status}))
    except RuntimeError:
        asyncio.run(manager.broadcast({"type": "status_change", "conversation_id": conv.id, "new_status": req.status}))
        
    return {"status": "success", "new_status": req.status}


@router.post("/agent/reply")
async def agent_reply(req: AgentReplyRequest, db: Session = Depends(get_db)):
    """Simulates an agent sending a reply from the dashboard to a user."""
    from app.models.models import User, Conversation, InteractionLog
    from app.core.schemas import SenderType
    conv = None

    if req.conversation_id:
        conv = db.query(Conversation).filter(Conversation.id == req.conversation_id).first()
    else:
        user = db.query(User).filter(User.identifier == req.recipient_identifier).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        conv = (
            db.query(Conversation)
            .filter(
                Conversation.user_id == user.id,
                Conversation.channel == req.channel,
                Conversation.status.in_(
                    [
                        ConversationStatus.PENDING_HUMAN,
                        ConversationStatus.ACTIVE_HUMAN,
                    ]
                ),
            )
            .order_by(Conversation.created_at.desc())
            .first()
        )
    
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    # Log the agent's message
    log = InteractionLog(
        conversation_id=conv.id,
        sender_type=SenderType.AGENT,
        message_content=req.content
    )
    db.add(log)
    db.commit()
    log_event(
        "agent_reply_logged",
        conversation_id=conv.id,
        recipient_identifier=req.recipient_identifier,
        channel=req.channel,
        message_content=req.content,
        sender="AGENT",
    )
    
    # Send it out to WhatsApp or the Web Widget
    OmnichannelService.send_outbound_message(
        req.recipient_identifier,
        req.channel,
        req.content,
        conversation_id=conv.id,
    )
    return {"status": "success", "sent": req.content}

# --- END OF NEW ENDPOINTS ---

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
