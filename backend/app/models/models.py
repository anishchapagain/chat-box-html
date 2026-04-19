from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base
from app.core.schemas import ChannelType, ConversationStatus, SenderType, DetectedLanguage

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    identifier = Column(String, unique=True, index=True, nullable=False) # Phone or Web Session ID
    name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    conversations = relationship("Conversation", back_populates="user")

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    channel = Column(Enum(ChannelType), nullable=False)
    status = Column(Enum(ConversationStatus), default=ConversationStatus.ACTIVE_AUTO, nullable=False)
    agent_id = Column(String, nullable=True) # Null if auto, populated if assigned
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="conversations")
    logs = relationship("InteractionLog", back_populates="conversation")

class InteractionLog(Base):
    __tablename__ = "interaction_logs"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    sender_type = Column(Enum(SenderType), nullable=False)
    detected_language = Column(Enum(DetectedLanguage), nullable=True)
    message_content = Column(Text, nullable=False)
    matched_faq_id = Column(String, ForeignKey("faqs.id"), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship("Conversation", back_populates="logs")
    faq = relationship("FAQ")

class FAQ(Base):
    __tablename__ = "faqs"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    category = Column(String, nullable=False)
    # Storing arrays as comma separated strings for simplicity in SQLite, in Prod use postgres ARRAY type
    keywords_en = Column(Text, nullable=True) 
    keywords_ne = Column(Text, nullable=True)
    keywords_ne_rom = Column(Text, nullable=True)
    answer_en = Column(Text, nullable=True)
    answer_ne = Column(Text, nullable=True)
    answer_ne_rom = Column(Text, nullable=True)