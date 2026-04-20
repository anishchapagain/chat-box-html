# NLU Architecture & Workflow (Rasa-Lite)

This document describes how the ChatMax Omnichannel backend uses semantic Natural Language Understanding (NLU) to handle multilingual customer queries.

## 1. The NLU Workflow
1.  **Ingestion**: A message arrives via WhatsApp or Web Widget webhook.
2.  **Language Detection**: `LanguageService` identifies if the text is English (**EN**), Nepali (**NE**), or Romanized Nepali (**NE_ROM**).
3.  **Semantic Embedding**: `NLUService` converts the message into a high-dimensional vector using the `paraphrase-multilingual-MiniLM-L12-v2` transformer model.
4.  **Intent Matching**: The system calculates the **Cosine Similarity** between the user's message and all training examples in `nlu.yml`.
5.  **Confidence Gating**:
    *   **Score > 0.75**: The bot identifies the intent (e.g., `account_opening`) and fetches the localized response from `domain.yml`.
    *   **Score < 0.75**: The bot sends a localized `utter_default_fallback` message and remains in `ACTIVE_AUTO` for agent review.
6.  **Broadcast & Logging**: The message and the bot's decision (intent, confidence, decision) are pushed to the dashboard via WebSockets and saved to `omnichannel_events.log` in JSONL format.

## 2. Key Files & Components
- **Engine**: `backend/app/services/nlu_service.py` (Handles embeddings and similarity)
- **Training Data**: `backend/app/core/nlu.yml` (Intents and multilingual examples)
- **Responses**: `backend/app/core/domain.yml` (Multilingual utter templates)
- **Audit Trail**: `backend/logs/omnichannel_events.log` (JSONL logs for active learning)

## 3. Core Endpoints
- **Webhook (WhatsApp)**: `POST /api/v1/webhook/whatsapp`
- **Webhook (Web)**: `POST /api/v1/webhook/web`
- **Real-time Push**: `WS /api/v1/ws/dashboard`
- **Agent Dashboard Data**: `GET /api/v1/agent/chats`

## 4. One-Liner Execution Commands

### Start the Application
```powershell
# From backend directory
uvicorn main:app --reload
```

### Test Semantic Matching (One-Liners)
Run these from the project root in a separate terminal to simulate inbound messages:

**English Query (Semantic Match):**
```powershell
python mock_whatsapp.py 112233 "how can i create a new account"
```

**Nepali Query (Devanagari):**
```powershell
python mock_whatsapp.py 112233 "खाता खोल्ने प्रक्रिया के हो?"
```

**Romanized Nepali Query:**
```powershell
python mock_whatsapp.py 112233 "khata kholne process kasto chha"
```

**Fallback (Low Confidence):**
```powershell
python mock_whatsapp.py 112233 "where is my pizza"
```

## 5. Technical Mind-Map: How the "Brain" Works (Step-by-Step)

For the technical team, here is the architectural logic behind the `NLUService`:

### Step 1: Bootstrapping (Startup Phase)
- **Model Loading**: The `SentenceTransformer` loads the `paraphrase-multilingual-MiniLM-L12-v2` model into memory.
- **Training Vectorization**: The service reads `nlu.yml`, extracts all example sentences (EN, NE, NE_ROM), and converts them into a **384-dimensional vector matrix**.
- **Indexing**: These vectors are stored in memory for lightning-fast mathematical comparison.

### Step 2: Feature Extraction (The Transformation)
- When a user sends *"khata kholne k ho?"*, the transformer model analyzes the semantic context, not just the keywords.
- It produces a new **384-dimensional vector** representing the "meaning" of that specific query.

### Step 3: Vector Algebra (Similarity Search)
- The system performs a **Cosine Similarity** calculation between the *User Vector* and the *Training Matrix*.
- It calculates the "angular distance" between meanings.
- **Example**: "Open account" (Vector A) and "Khata kholne" (Vector B) will have a very small angle, resulting in a high similarity score (~0.85+).

### Step 4: Logic Gating (The Decision)
- **Threshold Check**: If the highest similarity score is **> 0.75**, the system accepts the match.
- **Intent Mapping**: It identifies the associated intent ID (e.g., `account_opening`).
- **Fallback Trigger**: If the score is **< 0.75** (e.g., "Tell me a joke" results in 0.12), the system aborts the auto-answer and prepares the `utter_default_fallback`.

### Step 5: Localized Response Mapping
- The system looks up the Intent ID in `domain.yml`.
- It uses the **Detected Language** (from Step 1 of the workflow) to select the specific key:
  - If `NE_ROM`, it looks for the `ne_rom` key.
  - If missing, it gracefully degrades to `en`.

### Step 6: Post-Process & Audit
- **WebSocket Broadcast**: The final content and NLU metadata are pushed to the dashboard.
- **JSONL Persistence**: The entire decision tree (Confidence, Intent, Decision) is appended to `omnichannel_events.log` for future model tuning (Active Learning).

## 6. Technology Stack & Library Details

The NLU engine is built on top of industry-standard Python libraries for Machine Learning and NLP:

### 1. `sentence-transformers` (The Core)
- **Role**: Provides the framework to generate "Dense Vector Embeddings" from text.
- **Model**: `paraphrase-multilingual-MiniLM-L12-v2`.
- **Why this model?**: It is a distilled, lightweight version of BERT trained on 50+ languages. It is optimized for "Paraphrase Identification," making it perfect for matching a user's question to a predefined intent.
- **Output**: It transforms any string (regardless of length) into a **fixed-size array of 384 floating-point numbers**.

### 2. `scikit-learn` (The Math)
- **Role**: Used specifically for the `cosine_similarity` function.
- **Logic**: Instead of calculating the "straight-line" distance (Euclidean), it calculates the **cosine of the angle** between two vectors.
- **Benefit**: This is much more effective for text because it measures the "direction" (the meaning) rather than the "magnitude" (the word count).

### 3. `PyYAML` (The Configuration)
- **Role**: Parses the `nlu.yml` and `domain.yml` files.
- **Benefit**: Provides a human-readable way to manage complex training data and multilingual responses without needing a database for every minor text change.

### 4. `numpy` (The Performance)
- **Role**: Handles the high-speed array operations required when comparing the user's vector against hundreds of training example vectors simultaneously.
- **Usage**: Specifically used for `np.argmax()` to instantly find the highest similarity score in the results array.

## 7. Multilingual Display & WhatsApp Compatibility

A common technical concern is whether non-Latin scripts (Devanagari) render correctly on user devices. The system ensures 100% display accuracy through the following:

### 1. Universal Unicode (UTF-8) Logic
- WhatsApp uses **UTF-8 encoding** globally. 
- Every character in `domain.yml` (e.g., `तपाईँलाई स्वागत छ`) is transmitted as a specific binary code defined by the Unicode standard.
- The Meta Graph API and the WhatsApp client preserve this binary integrity without "translating" or "stripping" characters.

### 2. Native Font Rendering
- Modern mobile operating systems (Android/iOS) have pre-installed system fonts for Devanagari.
- WhatsApp renders text using the phone's native system capabilities, ensuring the script looks clean and readable.

### 3. Compatibility Matrix

| Feature | Technical Status | Display Risk |
| :--- | :--- | :--- |
| **Devanagari Script** | Fully Supported (Unicode) | Zero |
| **Romanized Nepali** | Fully Supported (ASCII/UTF-8) | Zero |
| **Emoji Integration** | Fully Supported | Zero |
| **Left-to-Right (LTR)** | Standard Alignment | Zero |

### 4. Verification Consistency
What an agent sees in the **Agent Dashboard** (rendering in a modern browser) is identical to what the end-user sees in the **WhatsApp App**. Both environments utilize the same UTF-8 rendering engines, guaranteeing visual parity.
