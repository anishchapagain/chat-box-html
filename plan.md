# Application Overview Plan

## 1. Purpose
This project is an omnichannel customer-support chatbot that handles:
- WhatsApp Cloud API messages (mobile and WhatsApp Web)
- Website chat messages

Both channels feed into the same backend service so teams can switch between auto-bot and human support.

## 2. Core Architecture
- Backend: FastAPI (async)
- Frontend: React dashboard (`frontend/dashboard.html`) for agents
- Realtime staff updates: WebSocket broadcast
- Data layer: SQLAlchemy models with SQLite for local development (`backend/capitalmax.db`), PostgreSQL-ready
- Language handling: English, Nepali, and Romanized Nepali detection

## 3. Conversation Model
- `ACTIVE_AUTO`: Default for all inbound conversations; bot replies automatically.
- `ACTIVE_HUMAN`: Agent takes over from dashboard after accept action.
- `CLOSED`: Conversation resolved/ended by agent action.
- `PENDING_HUMAN`: Legacy/manual status (not used as automatic default path).
- Agent actions:
  - `Accept Chat` -> switch to `ACTIVE_HUMAN`
  - `Resolve Chat` -> switch to `CLOSED`

## 4. Inbound/Outbound Flow
1. User sends message to WhatsApp business number or website chat.
2. Webhook receives event:
   - WhatsApp: `/api/v1/webhook/whatsapp`
   - Web chat: `/webhook/web`
3. Request enters Omnichannel service and language detection.
4. Default route is `ACTIVE_AUTO` (bot response); dashboard can later promote to human via Accept.
5. Response is sent back to the same user/channel.
6. Dashboard queue/updates are pushed live through WebSockets.

## 5. WhatsApp Cloud API Setup Requirements
- Create Meta Developer app (Business type)
- Add WhatsApp product
- Capture and store in `.env`:
  - `WHATSAPP_TOKEN`
  - `WHATSAPP_PHONE_ID`
  - `WHATSAPP_VERIFY_TOKEN`
- Configure webhook callback to `/api/v1/webhook/whatsapp`
- Subscribe to `messages` webhook field
- For production, add live phone number and use permanent system-user token

## 6. Local Run Workflow (3 terminals)
1. Backend:
   - `uvicorn main:app --reload`
2. Frontend dashboard:
   - `python3 -m http.server 3000`
   - Open `http://localhost:3000/dashboard.html`
3. WhatsApp simulation:
   - `python3 mock_whatsapp.py 9811122233 "what is management fee"`

## 7. Current Status and Gap
Confirmed as supported:
- Omnichannel ingestion (WhatsApp + website)
- Auto vs human response control
- Multilingual message handling
- Async backend behavior and realtime dashboard updates

Possible pending enhancement:
- If required, outbound WhatsApp replies may need explicit quoted-context linkage to the users original message (point needs final confirmation).

## 8. Major Technical Updates (April 19, 2026)
- WebSocket route is now mounted in FastAPI app startup:
  - `app.include_router(websockets.router, prefix=settings.API_V1_STR)`
  - This enables `ws://127.0.0.1:8000/api/v1/ws/dashboard` to actually connect.
- Finalized status policy in `OmnichannelService`:
  - All inbound messages stay in `ACTIVE_AUTO` by default.
  - No keyword-based automatic switch to human queue.
  - Human takeover only happens from dashboard action (`Accept`).
- Dashboard persistence was implemented:
  - New API: `GET /api/v1/agent/chats` returns open (`ACTIVE_AUTO`, `PENDING_HUMAN`, `ACTIVE_HUMAN`) conversations with message history.
  - `frontend/dashboard.html` now loads chats from backend on page load, so refresh no longer loses data.
- Auto-mode visibility was added to dashboard:
  - `ACTIVE_AUTO` conversations are now shown in a dedicated queue section (`Auto Active (Bot)`).
  - These chats can be accepted directly from dashboard to switch into `ACTIVE_HUMAN`.
  - Auto conversations are now broadcast to dashboard in real time (user message and bot reply events).
- Agent actions now persist via backend:
  - Accept chat -> `POST /api/v1/agent/status` with `ACTIVE_HUMAN`
  - Resolve chat -> `POST /api/v1/agent/status` with `CLOSED`
  - Send reply -> `POST /api/v1/agent/reply`
- Conversation targeting hardening:
  - Added optional `conversation_id` in status/reply APIs.
  - Frontend now sends `conversation_id` to avoid ambiguity when same user has multiple conversations.
- Database path consistency fix:
  - `DATABASE_URL` now resolves to absolute local path (`backend/capitalmax.db`), not working-directory-relative path.
  - This prevents split data across multiple `capitalmax.db` files.

## 9. Data Model and Persistence Notes
- `users` table:
  - One row per unique `identifier` (phone number or web session ID).
- `conversations` table:
  - Links to user, stores channel and lifecycle status.
  - Status enum: `ACTIVE_AUTO`, `PENDING_HUMAN`, `ACTIVE_HUMAN`, `CLOSED`.
- `interaction_logs` table:
  - Stores every inbound and outbound message (USER/BOT/AGENT), detected language, timestamp, and optional FAQ match.
- `faqs` table:
  - Structure exists for multilingual FAQ answers and keywords.
  - Current matching logic is mocked in service layer and should be replaced with real retrieval/search.

## 10. Current API Surface for Agent Dashboard
- `GET /api/v1/agent/chats`
  - Purpose: load current open queue and active chats with history.
  - Includes statuses: `ACTIVE_AUTO`, `PENDING_HUMAN`, `ACTIVE_HUMAN`.
- `POST /api/v1/agent/status`
  - Purpose: set conversation status (`ACTIVE_HUMAN`, `CLOSED`, etc.).
  - Preferred identifier: `conversation_id` (exact conversation update).
- `POST /api/v1/agent/reply`
  - Purpose: log agent reply and dispatch outbound message through channel adapter.
- `POST /api/v1/webhook/whatsapp`
  - Purpose: ingest WhatsApp events from Meta and route through omnichannel service.
- `POST /api/v1/webhook/web`
  - Purpose: ingest website widget messages and route through omnichannel service.
- `GET /api/v1/webhook/whatsapp`
  - Purpose: Meta webhook verification handshake (`hub.challenge` flow).
- `WS /api/v1/ws/dashboard`
  - Purpose: push `new_message` and `status_change` events to connected dashboards.

## 11. Developer Runbook (Reliable Local Setup)
1. Install backend dependencies:
   - `pip install -r backend/requirements.txt`
2. Start backend from `backend/` directory:
   - `uvicorn main:app --reload`
3. Start frontend static host:
   - From project root or `frontend/`: `python3 -m http.server 3000`
4. Open dashboard:
   - `http://localhost:3000/frontend/dashboard.html` (if serving from project root)
   - or `http://localhost:3000/dashboard.html` (if serving from `frontend/` directory)
5. Send test WhatsApp message:
   - `python3 mock_whatsapp.py 11111111 "what is management fee"`
6. Confirm expected behavior:
   - Message appears in `Auto Active (Bot)` queue as `ACTIVE_AUTO`.
   - Click `Accept` and verify it moves to `My Active Chats` as `ACTIVE_HUMAN`.
   - Refresh dashboard and verify chat remains visible (loaded from DB).

## 12. Troubleshooting Guide
- Symptom: `Unsupported upgrade request` or `No supported WebSocket library detected`
  - Fix: ensure backend env has WebSocket support (`websockets` or `uvicorn[standard]`).
- Symptom: message seen before refresh but disappears after refresh
  - Check that `GET /api/v1/agent/chats` returns data.
  - Check backend is using the intended DB file (`backend/capitalmax.db`).
- Symptom: message is auto-answered but not shown in dashboard
  - Verify conversation status is included in open-chat API filter (`ACTIVE_AUTO` should be included).
  - Verify dashboard has the `Auto Active (Bot)` list section enabled.
- Symptom: dashboard not connecting
  - Verify backend includes websocket router and dashboard is using correct WS URL.
- Symptom: message unexpectedly changes to human status without agent action
  - Check any direct calls to `POST /api/v1/agent/status` and validate no external automation is changing status.

## 13. Known Limitations and Next Engineering Steps
- WhatsApp outbound is currently a stub (`print`) and not yet calling live Meta Graph API.
- FAQ matching is mock logic; replace with real multilingual retrieval pipeline.
- No auth/role model yet for agent dashboard endpoints.
- No assignment ownership model (`agent_id`) implemented for concurrent multi-agent handling.
- Consider adding migration tooling (Alembic) and seed scripts for deterministic local setup.

## 14. TODO (Immediate)
Tomorrow workflow (practical implementation order):
1. Replace mock FAQ engine with real scoring
   - Implement `FAQService.find_best_match()` to return: `faq_id`, `answer`, `score`, `matched_lang`.
   - Read FAQs from DB (`faqs`), choose language-specific keyword/answer columns by detected language.
   - Remove hardcoded mock reply string path.
2. Add robust language detection for `EN`, `NE`, `NE_ROM`
   - Keep Devanagari check for `NE`.
   - Improve Romanized Nepali detection using word list frequency (not single-letter tokens).
   - Remove weak token rules that cause false positives (for example single token like `k`).
3. Add confidence gating for auto response
   - Add config values (env-based): `FAQ_AUTO_THRESHOLD` (example `0.62`) and `FAQ_MARGIN_THRESHOLD` (example `0.08`).
   - If `score >= threshold` and `best-second >= margin`: send answer and keep `ACTIVE_AUTO`.
   - If below threshold: send explicit fallback message and keep conversation visible for agent accept flow.
4. Seed initial multilingual FAQ dataset
   - Insert starter records from Section 17 into `faqs`.
   - Ensure each row has usable `keywords_en/keywords_ne/keywords_ne_rom` and `answer_en/answer_ne/answer_ne_rom`.
5. Observability and audit improvements
   - Log `detected_lang`, `matched_lang`, `score`, `threshold`, decision (`AUTO_ANSWER` vs `FALLBACK`) in `omnichannel_events.log`.
   - Keep existing outbound/inbound/status logs.
6. Dashboard behavior check
   - Verify `ACTIVE_AUTO` chats remain listed in `Auto Active (Bot)`.
   - Verify `Accept` moves to `ACTIVE_HUMAN` and enables manual reply input.
   - Verify `Resolve` moves chat to `CLOSED`.
7. Acceptance test matrix (run before merge)
   - EN strong match: `what is management fee` -> confident auto answer.
   - EN weak/no match: random question -> fallback message + visible for agent.
   - NE query (Devanagari) -> Nepali answer if FAQ exists.
   - NE_ROM query -> Romanized Nepali answer if FAQ exists.
   - Refresh dashboard -> chat/history persists.
   - Log file includes scoring decision details for each message.

Definition of done for tomorrow:
- No mock FAQ response format remains in user-facing replies.
- FAQ answers are served from DB for strong matches.
- Weak matches are safely handled with fallback.
- Language and scoring decision is traceable in logs.
- Closed chat history is queryable and visible in dedicated history UI.
- Same-user repeat messages create/continue conversations according to status policy and are easy for agents to trace.

## 15. File-Based Event Logging (New)
- Log file path:
  - `backend/logs/omnichannel_events.log`
- Format:
  - One JSON object per line (JSONL style) with UTC timestamp, event type, and structured details.
- Current logged events:
  - `incoming_message`
  - `message_routed_to_dashboard`
  - `auto_response_generated`
  - `conversation_status_changed`
  - `agent_reply_logged`
  - `outbound_message`
- Typical fields captured:
  - `conversation_id`
  - `user_identifier` / `recipient_identifier`
  - `channel` (e.g., `WHATSAPP`, `WEB_WIDGET`)
  - `conversation_status`
  - `sender`
  - `message_content` and generated response text
  - `detected_language` and optional FAQ match ID
- Rotation policy:
  - Rotating file handler, 5 MB per file, 5 backup files.

## 16. Practical Conversation Policy (Recommended)
- Current implemented behavior:
  - All inbound messages start/stay `ACTIVE_AUTO`.
  - Bot sends auto reply using current FAQ service logic.
  - Agent must click `Accept` to move chat to `ACTIVE_HUMAN`.
- Recommended production behavior (realistic WhatsApp flow):
  - Attempt FAQ match with confidence threshold.
  - If confidence is high:
    - Send auto answer and keep `ACTIVE_AUTO`.
  - If confidence is low or FAQ is missing:
    - Send fallback acknowledgment (for example: "I am connecting you to an agent.").
    - Place conversation into staff queue (`PENDING_HUMAN` or equivalent queue state).
    - Staff accepts chat -> `ACTIVE_HUMAN` and continues manual replies.
- Message to-fro expectations:
  - User should always receive a response (auto answer or fallback handoff message).
  - Conversation history should remain visible to both bot and agent in one thread.
  - Handoff should be explicit and auditable in logs/status transitions.

## 17. Sample FAQ Seed Content
- Use these as starter records for the `faqs` table.
- `keywords_*` can be stored as comma-separated tokens in current schema.

| category | keywords_en | keywords_ne | keywords_ne_rom | answer_en | answer_ne | answer_ne_rom |
|---|---|---|---|---|---|---|
| account_opening | open account,new account,create account,account opening | खाता खोल्ने,नयाँ खाता,डिम्याट खाता | khata kholne,naya khata,demat khata | You can open an account online by submitting KYC details and identity documents. We can share the official onboarding link. | तपाईँ KYC विवरण र परिचयपत्र कागजात पेश गरेर अनलाइन खाता खोल्न सक्नुहुन्छ। हामी आधिकारिक दर्ता लिंक पठाउन सक्छौँ। | Tapai KYC details ra ID documents diyera online khata kholna saknuhunchha. Hami official onboarding link pathauna sakchhau. |
| management_fee | management fee,annual fee,yearly charge,maintenance fee | व्यवस्थापन शुल्क,वार्षिक शुल्क,नवीकरण शुल्क | management fee,barshik sulka,renew charge | The management fee is charged annually. Exact amount depends on your account plan and services. | व्यवस्थापन शुल्क वार्षिक रूपमा लाग्छ। ठ्याक्कै रकम तपाईँको खाता योजना र सेवामा निर्भर हुन्छ। | Management fee barshik lagcha. Thyakai amount tapai ko account plan ra service ma bhar parchha. |
| science_fee | science fee,science stream fee,science tuition | विज्ञान शुल्क,विज्ञान संकाय शुल्क | science fee,bigyan sulka,science stream fee | Science fee varies by grade and course package. Please share grade/class so we can provide exact pricing. | विज्ञान शुल्क कक्षा र कोर्स प्याकेज अनुसार फरक हुन्छ। कृपया कक्षा जानकारी दिनुहोस्, हामी ठ्याक्कै शुल्क बताउँछौँ। | Science fee class ra package anusaar फरक हुन्छ. Kripaya class info dinuhos, hami exact fee dinchhau. |
| account_balance | balance,check balance,available balance | ब्यालेन्स,बचत रकम,उपलब्ध रकम | balance herne,available balance,check balance | Please log in to your dashboard to view real-time balance. If needed, we can guide you step-by-step. | रियल-टाइम ब्यालेन्स हेर्न ड्यासबोर्डमा लगइन गर्नुहोस्। चाहिएको खण्डमा हामी चरणबद्ध सहयोग गर्न सक्छौँ। | Real-time balance herna dashboard ma login garnuhos. Chahiyo bhane hami step-by-step help garchhau. |
| office_hours | office hours,working hours,open time,close time | कार्यालय समय,सेवा समय,खुल्ने समय | office time,kaaryalaya samaya,khulne samaya | Our support hours are Sunday to Friday, 10:00 AM to 5:00 PM (local time). | हाम्रो सहयोग समय आइतबारदेखि शुक्रबार, बिहान १०:०० देखि साँझ ५:०० सम्म हो। | Hamro support hours Aaitabar dekhi Shukrabar, bihana 10 baje dekhi beluka 5 baje samma ho. |
| contact_support | contact support,agent,human help,call me | सहयोग,एजेन्ट,मानव सहयोग | agent sanga kura,manche support,human help | I can connect you to a human agent. Please share your preferred callback number and time. | म तपाईँलाई मानव एजेन्टसँग जोड्न सक्छु। कृपया सम्पर्क नम्बर र उपयुक्त समय दिनुहोस्। | Ma tapai lai human agent sanga jodna sakchu. Kripaya contact number ra suitable time dinuhos. |
| kyc_update | update kyc,change kyc,address update,document update | KYC अपडेट,ठेगाना परिवर्तन,कागजात अपडेट | kyc update,thegana update,document update | To update KYC, submit your new document and address proof through the KYC update portal. | KYC अपडेट गर्न नयाँ कागजात र ठेगाना प्रमाण KYC पोर्टलमार्फत पेश गर्नुहोस्। | KYC update garna naya document ra address proof KYC portal bata submit garnuhos. |
| reset_password | reset password,forgot password,password change | पासवर्ड रिसेट,पासवर्ड बिर्सें,पासवर्ड परिवर्तन | password reset,password birse,password change | Use the Forgot Password option on login. You will receive an OTP to set a new password securely. | लगइनमा Forgot Password विकल्प प्रयोग गर्नुहोस्। नयाँ पासवर्ड सेट गर्न OTP प्राप्त हुनेछ। | Login ma Forgot Password option use garnuhos. Naya password set garna OTP auncha. |

Example classification guidance:
- If score >= threshold: send `answer_*` in detected language and keep `ACTIVE_AUTO`.
- If score < threshold: send fallback handoff message and queue for agent review.

## 18. Repeat User + History Scenario
- Proposed UI:
  - Add `history.html` for `CLOSED` conversations only.
  - Provide filters by phone/identifier, date, channel, and agent-handled status.
  - Show full transcript from `interaction_logs` and summary from `conversations`.
- Same phone number workflow (example: `1111999`):
  - First interaction: user message -> auto/human flow -> agent resolves -> status becomes `CLOSED`.
  - Later interaction from same number:
    - System keeps same `users.identifier`.
    - Because prior conversation is `CLOSED`, backend creates a new conversation row (new `conversation_id`) and starts in `ACTIVE_AUTO`.
    - Dashboard should show this as a fresh active chat while preserving old transcript in history.
- Backend/API additions recommended:
  - `GET /api/v1/agent/chats/history` with pagination and filters (`identifier`, `date_from`, `date_to`, `channel`).
  - Optional `GET /api/v1/agent/chats/{conversation_id}` for full transcript retrieval.
  - Optional `GET /api/v1/agent/users/{identifier}/conversations` to show past + current conversations for one user.

## 19. NLU/RASA Architecture (Professional Upgrade)
Based on professional investigation, the project will transition from keyword matching to a semantic NLU-driven architecture (Rasa-lite).

### 19.1. NLU Engine: Vector Similarity
- **Core Technology**: `sentence-transformers` using a multilingual model (e.g., `paraphrase-multilingual-MiniLM-L12-v2`).
- **Multilingual Support**: Bridges English and Nepali (Devanagari) in the same vector space.
- **Romanized Nepali (NE_ROM)**: Handled via specific training examples in `nlu.yml` to bridge the gap where pre-trained models are weaker.

### 19.2. Rasa-Style Configuration (YAML)
- **`nlu.yml`**: Defines intents and training examples across all three languages (EN, NE, NE_ROM).
- **`domain.yml`**: Defines multilingual responses (`utter_...`) and categories.
- **`stories.yml`**: Maps intent sequences to actions (e.g., `contact_support` -> `action_handoff`).

### 19.3. Implementation Strategy
1. **Lightweight Integration**: No standalone Rasa server; implement a `NLUService` within FastAPI using `scikit-learn` for similarity computation.
2. **Confidence Gating**:
   - **High Confidence (> 0.75)**: Auto-reply using matched FAQ.
   - **Low Confidence (< 0.75)**: Fallback message and route to `PENDING_HUMAN`.
3. **Active Learning Workflow**:
   - Log low-confidence queries to `omnichannel_events.log` (JSONL).
   - Agent reviews logs to "teach" the bot by adding examples to `nlu.yml`.
4. **Data Sync**: The `faqs` database table will remain as a persistent cache of the YAML-defined responses for high-speed retrieval.

