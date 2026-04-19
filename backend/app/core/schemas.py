from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime

# --- Enums ---
class ChannelType(str, Enum):
    WHATSAPP = "WHATSAPP"
    WEB_WIDGET = "WEB_WIDGET"

class ConversationStatus(str, Enum):
    ACTIVE_AUTO = "ACTIVE_AUTO"
    PENDING_HUMAN = "PENDING_HUMAN"
    ACTIVE_HUMAN = "ACTIVE_HUMAN"
    CLOSED = "CLOSED"

class SenderType(str, Enum):
    USER = "USER"
    BOT = "BOT"
    AGENT = "AGENT"

class DetectedLanguage(str, Enum):
    EN = "EN"
    NE = "NE"
    NE_ROM = "NE_ROM"

# --- Inbound Message Validation (Generic) ---
class IncomingMessage(BaseModel):
    channel: ChannelType
    identifier: str = Field(..., min_length=5, description="Phone number or web session ID")
    content: str = Field(..., min_length=1, description="The message payload from the user")

# --- Outbound Message Validation (Generic) ---
class OutboundMessage(BaseModel):
    recipient_identifier: str
    channel: ChannelType
    content: str

# --- Ticket Creation Schema (Phase 2 Specific) ---
class TicketCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    contact: str = Field(..., min_length=5, max_length=100) 
    issue: str = Field(..., min_length=5, max_length=1000)

class TicketResponse(BaseModel):
    status: str
    ticketId: str

# --- Database Read Schemas ---
class InteractionLogBase(BaseModel):
    sender_type: SenderType
    message_content: str
    detected_language: Optional[DetectedLanguage] = None
    timestamp: datetime

    class Config:
        from_attributes = True