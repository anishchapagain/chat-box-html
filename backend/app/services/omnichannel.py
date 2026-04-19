import re
import asyncio
from sqlalchemy.orm import Session
from app.models.models import User, Conversation, InteractionLog, FAQ
from app.core.schemas import IncomingMessage, ChannelType, ConversationStatus, SenderType, DetectedLanguage
from app.api.websockets import manager

class LanguageService:
    @staticmethod
    def detect_language(text: str) -> DetectedLanguage:
        """
        Mock NLP Language Detection.
        In production, this would use a dedicated NLP model (e.g., fastText or an LLM).
        """
        text_lower = text.lower()
        
        # Simple heuristic: Devnagari characters -> Nepali
        if re.search(r'[\u0900-\u097F]', text):
            return DetectedLanguage.NE
            
        # Romanized Nepali keywords
        ne_rom_keywords = ['kasto', 'k', 'ho', 'kasari', 'khata', 'kholne', 'laagi']
        if any(word in text_lower for word in ne_rom_keywords):
            return DetectedLanguage.NE_ROM
            
        # Default fallback
        return DetectedLanguage.EN

class FAQService:
    @staticmethod
    def find_best_match(db: Session, text: str, lang: DetectedLanguage):
        """
        Mock FAQ search based on language.
        In production, this would be a full-text search or vector similarity search.
        """
        # For this prototype, we will just return a mocked string
        return None, f"[Mock matched FAQ answer in {lang.value}] for: {text}"

class OmnichannelService:
    @staticmethod
    def process_incoming_message(db: Session, msg: IncomingMessage):
        # 1. Identify User
        user = db.query(User).filter(User.identifier == msg.identifier).first()
        if not user:
            user = User(identifier=msg.identifier)
            db.add(user)
            db.commit()
            db.refresh(user)

        # 2. Identify or Create Active Conversation
        conv = db.query(Conversation).filter(
            Conversation.user_id == user.id,
            Conversation.channel == msg.channel,
            Conversation.status.in_([ConversationStatus.ACTIVE_AUTO, ConversationStatus.PENDING_HUMAN, ConversationStatus.ACTIVE_HUMAN])
        ).first()

        if not conv:
            conv = Conversation(user_id=user.id, channel=msg.channel)
            db.add(conv)
            db.commit()
            db.refresh(conv)

        # 3. Log Incoming User Message
        detected_lang = LanguageService.detect_language(msg.content)
        user_log = InteractionLog(
            conversation_id=conv.id,
            sender_type=SenderType.USER,
            message_content=msg.content,
            detected_language=detected_lang
        )
        db.add(user_log)
        db.commit()

        # 4. State Machine Routing
        if conv.status == ConversationStatus.ACTIVE_HUMAN or conv.status == ConversationStatus.PENDING_HUMAN:
            # Route to Dashboard via WebSockets
            payload = {
                "type": "new_message",
                "conversation_id": conv.id,
                "user_identifier": user.identifier,
                "channel": msg.channel.value,
                "content": msg.content,
                "sender": "USER",
                "status": conv.status.value
            }
            # Use asyncio to run the async broadcast inside this synchronous function
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(manager.broadcast(payload))
            except RuntimeError:
                asyncio.run(manager.broadcast(payload))
            
        elif conv.status == ConversationStatus.ACTIVE_AUTO:
            # Process Auto Mode
            faq_id, answer = FAQService.find_best_match(db, msg.content, detected_lang)
            
            # Log Bot Response
            bot_log = InteractionLog(
                conversation_id=conv.id,
                sender_type=SenderType.BOT,
                message_content=answer,
                matched_faq_id=faq_id,
                detected_language=detected_lang
            )
            db.add(bot_log)
            db.commit()
            
            # Send message back to channel
            OmnichannelService.send_outbound_message(msg.identifier, msg.channel, answer)

    @staticmethod
    def send_outbound_message(identifier: str, channel: ChannelType, content: str):
        """
        Generic sender function. Routes to the specific platform adapter.
        """
        if channel == ChannelType.WHATSAPP:
            print(f"[WHATSAPP OUT] To {identifier}: {content}")
            # Call Meta Graph API here
        elif channel == ChannelType.WEB_WIDGET:
            print(f"[WEB OUT] To {identifier}: {content}")
            # Send via WebSockets to Web Widget