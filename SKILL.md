---
name: chatbotwhats-maintainer
description: Maintain and extend the ChatBotWhats project (FastAPI omnichannel backend plus web chat widget). Use when Codex needs to modify webhook handling, conversation state routing, NLU/guardrail behavior, WhatsApp or web outbound messaging, dashboard chat/status/reply APIs, or local debugging/run configuration for this repository.
---

# ChatBotWhats Maintainer Skill

## Follow This Scope
- Work in `D:\PythonProjects\ChatBotWhats`.
- Treat `backend/` as the production app surface.
- Treat root mock/test scripts as local development helpers.

## Use This Project Map
- `backend/main.py`: Start FastAPI app, mount routers, create tables for local dev.
- `backend/app/api/webhooks.py`: Web and WhatsApp webhooks, dashboard REST endpoints.
- `backend/app/api/websockets.py`: Dashboard websocket broadcast manager.
- `backend/app/services/omnichannel.py`: Core routing and state machine logic.
- `backend/app/services/nlu_service.py`: Intent matching and fallback logic.
- `backend/app/services/whatsapp_service.py`: WhatsApp Graph API adapter.
- `backend/app/core/config.py`: Settings and `.env` loading.
- `backend/app/core/database.py`: SQLAlchemy engine/session setup.
- `backend/app/models/models.py`: Users, conversations, logs, FAQ models.
- `KnowBase/`: Domain and NLU data files.
- `index.html`, `css/`, `js/`: Web chat widget demo and behavior.

## Preserve These Behavioral Invariants
- Normalize inbound payloads into `IncomingMessage` at webhook boundaries.
- Keep conversation states consistent: `ACTIVE_AUTO`, `PENDING_HUMAN`, `ACTIVE_HUMAN`.
- Keep profanity guardrail as early-exit behavior.
- Keep escalation guardrail able to move chats into human queue.
- Keep dashboard websocket broadcasts for message/status events.
- Keep outbound dispatch channel-specific (`WHATSAPP`, `WEB_WIDGET`).

## Run Locally
```powershell
pip install -r backend\requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

## Verify After Changes
- Check `GET /` returns API running response.
- Check `/api/v1/openapi.json` is available.
- Exercise changed endpoints in `backend/app/api/webhooks.py`.
- Confirm websocket flow for `/api/v1/ws/dashboard` if routing/status logic changed.

## Use These Key Config Values
Set via `.env` (defaults exist in `backend/app/core/config.py`):
- `DATABASE_URL`
- `WHATSAPP_TOKEN`
- `WHATSAPP_VERIFY_TOKEN`
- `WHATSAPP_PHONE_ID`
- `NLU_THRESHOLD`
- `NE_ROM_KEYWORDS`
- `GUARDRAIL_KEYWORDS`
- `PROFANITY_KEYWORDS`
- `PROFANITY_RESPONSE`

## Apply Safe Change Rules
- Read target module and direct dependencies before editing.
- Keep request/response schemas backward-compatible unless explicitly asked to break them.
- Keep `log_event` calls aligned with flow changes.
- Do not commit credentials or tokens.
- Treat `webhook_server.py` as non-production helper code; avoid copying hardcoded secrets patterns.
