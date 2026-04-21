import re
import asyncio
from sqlalchemy.orm import Session
from app.models.models import User, Conversation, InteractionLog, FAQ
from app.core.schemas import IncomingMessage, ChannelType, ConversationStatus, SenderType, DetectedLanguage
from app.api.websockets import manager
from app.core.audit_log import log_event
from app.core.config import settings

from app.services.nlu_service import nlu_service

class LanguageService:
    @staticmethod
    def detect_language(text: str) -> DetectedLanguage:
        """
        Heuristic language detection.
        Uses configurable keywords for Romanized Nepali.
        """
        text_lower = text.lower()

        # Simple heuristic: Devnagari characters -> Nepali
        if re.search(r'[\u0900-\u097F]', text):
            return DetectedLanguage.NE

        # Check if any configured keyword matches as a full word
        if any(re.search(rf'\b{word}\b', text_lower) for word in settings.NE_ROM_KEYWORDS):
            return DetectedLanguage.NE_ROM

        # Default fallback
        return DetectedLanguage.EN

class GuardrailService:
    @staticmethod
    def should_escalate_to_human(text: str) -> bool:
        """
        Check if message contains keywords that should trigger immediate human attention.
        """
        text_lower = text.lower()
        return any(re.search(rf'\b{word}\b', text_lower) for word in settings.GUARDRAIL_KEYWORDS)

    @staticmethod
    def is_profane(text: str) -> bool:
        """
        Check if message contains inappropriate language.
        """
        text_lower = text.lower()
        return any(re.search(rf'\b{word}\b', text_lower) for word in settings.PROFANITY_KEYWORDS)

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
    def _broadcast_dashboard_message(
        conv: Conversation,
        user_identifier: str,
        channel: ChannelType,
        content: str,
        sender: SenderType
    ):
        payload = {
            "type": "new_message",
            "conversation_id": conv.id,
            "user_identifier": user_identifier,
            "channel": channel.value,
            "content": content,
            "sender": sender.value,
            "status": conv.status.value,
        }
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(manager.broadcast(payload))
        except RuntimeError:
            asyncio.run(manager.broadcast(payload))

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
        
        # 3.1 Profanity Guardrail (Immediate Exit)
        if GuardrailService.is_profane(msg.content):
            log_event(
                "profanity_detected",
                conversation_id=conv.id,
                user_identifier=user.identifier,
                message_content=msg.content
            )
            OmnichannelService.send_outbound_message(
                msg.identifier,
                msg.channel,
                settings.PROFANITY_RESPONSE,
                conversation_id=conv.id
            )
            return # Stop processing this message

        user_log = InteractionLog(
            conversation_id=conv.id,
            sender_type=SenderType.USER,
            message_content=msg.content,
            detected_language=detected_lang
        )
        db.add(user_log)
        db.commit()

        # 4. Guardrail / Escalation Check
        if conv.status == ConversationStatus.ACTIVE_AUTO:
            if GuardrailService.should_escalate_to_human(msg.content):
                conv.status = ConversationStatus.PENDING_HUMAN
                db.commit()
                log_event(
                    "conversation_status_changed",
                    conversation_id=conv.id,
                    new_status=conv.status,
                    reason="guardrail_escalation"
                )

        # 5. State Machine Routing
        if conv.status == ConversationStatus.ACTIVE_HUMAN or conv.status == ConversationStatus.PENDING_HUMAN:
            OmnichannelService._broadcast_dashboard_message(
                conv=conv,
                user_identifier=user.identifier,
                channel=msg.channel,
                content=msg.content,
                sender=SenderType.USER,
            )
            log_event(
                "message_routed_to_dashboard",
                conversation_id=conv.id,
                user_identifier=user.identifier,
                channel=msg.channel,
                conversation_status=conv.status,
                route="HUMAN_QUEUE",
                message_content=msg.content,
            )
            
        elif conv.status == ConversationStatus.ACTIVE_AUTO:
            # Product rule: all incoming messages remain in ACTIVE_AUTO unless an agent explicitly accepts from dashboard.
            OmnichannelService._broadcast_dashboard_message(
                conv=conv,
                user_identifier=user.identifier,
                channel=msg.channel,
                content=msg.content,
                sender=SenderType.USER,
            )

            # Process Auto Mode
            # faq_id, answer = FAQService.find_best_match(db, msg.content, detected_lang)

            # Process Auto Mode (NLU Engine)
            intent, confidence = nlu_service.find_best_match(msg.content)
            
            if intent:
                answer = nlu_service.get_response(intent, detected_lang)
                decision = "AUTO_ANSWER"
            else:
                answer = nlu_service.get_fallback_response(detected_lang)
                decision = "FALLBACK"
                # If fallback, we could optionally move to PENDING_HUMAN here
                # but following Section 3 of plan.md: "All inbound messages stay in ACTIVE_AUTO by default."
                # Section 16 recommends: "Place conversation into staff queue (PENDING_HUMAN or equivalent)"
                # Let's stick to ACTIVE_AUTO but send fallback, and the agent will see it in the "Auto" queue.

            # Log Bot Response
            bot_log = InteractionLog(
                conversation_id=conv.id,
                sender_type=SenderType.BOT,
                message_content=answer,
                matched_faq_id=intent, # Store intent name ( matched_faq_id=faq_id)
                detected_language=detected_lang
            )
            db.add(bot_log)
            db.commit()
            
            OmnichannelService._broadcast_dashboard_message(
                conv=conv,
                user_identifier=user.identifier,
                channel=msg.channel,
                content=answer,
                sender=SenderType.BOT,
            )
            
            log_event(
                "auto_response_generated",
                conversation_id=conv.id,
                user_identifier=user.identifier,
                channel=msg.channel,
                conversation_status=conv.status,
                detected_language=detected_lang,
                matched_intent=intent, # matched_faq_id=faq_id,
                confidence=float(confidence),
                decision=decision,
                response_content=answer,
            )
            
            # Send message back to channel
            OmnichannelService.send_outbound_message(
                msg.identifier,
                msg.channel,
                answer,
                conversation_id=conv.id,
            )

    @staticmethod
    def send_outbound_message(
        identifier: str,
        channel: ChannelType,
        content: str,
        conversation_id: str | None = None,
    ):
        """
        Generic sender function. Routes to the specific platform adapter.
        """
        log_event(
            "outbound_message",
            conversation_id=conversation_id,
            recipient_identifier=identifier,
            channel=channel,
            message_content=content,
        )
        if channel == ChannelType.WHATSAPP:
            print(f"[WHATSAPP OUT] To {identifier}: {content}")
            # Call Meta Graph API here
        elif channel == ChannelType.WEB_WIDGET:
            print(f"[WEB OUT] To {identifier}: {content}")
            # Send via WebSockets to Web Widget
