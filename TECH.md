# ChatMax Chat Agent - Technical Deployment Guide

This document explains how to deploy the lightweight, responsive, WhatsApp-themed Chat Agent into your existing website (https://chatmax.com.np/).

## 1. Prerequisites

The chat agent consists of two files:
- `chat-agent.css`: Contains all the styles for the chat interface.
- `chat-agent.js`: Contains the JavaScript logic for the chat interactions.

You do **not** need Python or any backend server to run this agent. It runs entirely in the user's browser (client-side).

## 2. Plan

sequenceDiagram
    autonumber
    actor User
    participant CA as Chat Agent (Frontend)
    participant Server as ChatMax Backend (Proxy)
    participant TS as Ticketing System (External)

    Note over User, CA: 1. Initiation & Data Collection (State Machine)
    User->>CA: "Raise a Ticket" (Button click or text)
    CA-->>User: "I can help. What is your Name?"
    User->>CA: "John Doe"
    CA-->>User: "What is your Phone Number?"
    User->>CA: "9800000000"
    CA-->>User: "Please describe your issue."
    User->>CA: "Cannot access Demat account."
    
    Note over CA, Server: 2. Secure API Submission
    CA->>CA: Show "Submitting..." indicator
    CA->>Server: HTTP POST /api/create-ticket<br>{name, phone, issue}
    
    Note over Server, TS: 3. Backend Processing & Security
    Server->>Server: Authenticate request<br>Attach Secret API Keys
    Server->>TS: Create Ticket API Call
    TS-->>Server: 201 Created <br>{ ticketId: "TKT-10293" }
    
    Note over Server, User: 4. Confirmation & Display
    Server-->>CA: 200 OK <br>{ status: "success", ticketId: "TKT-10293" }
    CA-->>User: "Ticket created! Your ID is #TKT-10293."


Visual Architecture Summary (Text Infographic)
[ USER'S BROWSER ]
       |
       |  1. Chat Interface (chat-agent.js)
       |     - Collects: Name, Phone, Issue
       |     - Validates input locally
       |
       V
[ INTERNET ] -- (Sends JSON Data via fetch API)
       |
       V
[ CHATMAX SERVER ] (Your domain's backend)
       |  2. Webhook / Proxy Endpoint
       |     - Receives JSON payload
       |     - Applies API Keys / Auth Tokens (Keeps them secret!)
       |     - Formats payload for external system
       |
       V
[ EXTERNAL TICKETING SYSTEM ] (e.g., Jira, Zendesk)
       |  3. System creates ticket
       |     - Returns { ticket_id: "TKT-123" }
       |
       V
[ BACK TO USER ]
          4. Chat Agent displays: "Your ticket ID is TKT-123"

## 2. File Placement

Upload `chat-agent.css` and `chat-agent.js` to your web server (e.g., inside a `/assets/css/` and `/assets/js/` directory).

## 3. Embedding into Your Website

To deploy the chat agent across all pages, edit your website's main layout file (e.g., `header.php`, `footer.php`, `index.html`, or your master template) and add the following lines.

### Add CSS
In the `<head>` section of your HTML, link the CSS file:

```html
<link rel="stylesheet" href="path/to/chat-agent.css">
```

### Add JavaScript
Right before the closing `</body>` tag, add the JS script and initialize it:

<!-- Load the Chat Agent Script -->
<script src="path/to/chat-agent.js"></script>

<!-- Initialize the Chat Agent -->
<script>
    document.addEventListener('DOMContentLoaded', function() {
        const chatAgent = new ChatMaxChatAgent({
            botName: 'ChatMax Support',
            welcomeMessage: 'Hello! Welcome to ChatMax Securities. How can I help you today?',
            
            // Optional: Customize Quick Replies (Buttons)
            quickReplies: [
                { label: 'Trading Account', text: 'How to open a trading account?' },
                { label: 'DEMAT Account', text: 'How to open a DEMAT account?' },
                { label: 'Contact Details', text: 'What are your contact details?' },
                { label: 'Services', text: 'What services do you offer?' }
            ],

            // Optional: Customize Automatic Keyword Replies
            autoReplies: {
                'trading account': 'To open a Trading Account, you can process your KYC online through our website or visit our office. [Click here to open](https://tms62.nepsetms.com.np/client-registration)',
                'demat account': 'You can open a DEMAT & Meroshare account online through our website. [Click here to open](https://dp.chatmax.com.np/DPForm?type=demat)',
                'contact': 'ChatMax Securities Limited (Broker No. ##)\\nPutalisadak - 28, Kathmandu, Nepal\\nPhone: 01-4412345 / 4423456\\nEmail: contact@chatmax.com.np',
                'services': 'We offer Stock Brokerage Services, Depository Services (DEMAT), and full customer support for trading at NEPSE.',
                'hello': 'Hi there! How can I assist you with your investment journey today?',
                'hi': 'Hello! How can we help you?',
                'thank': 'You are welcome! Let us know if you need any more help.',
                'bye': 'Goodbye! Happy trading!'
            },
            
            // Default reply when no keyword matches
            defaultReply: "I'm sorry, I don't have a specific answer for that. Please call us at 01-4412345 or email us at contact@chatmax.com.np for detailed support."
        });
    });
</script>

## 4. Configuration Options
The `ChatMaxChatAgent` class accepts an optional configuration object. If you omit any property, the agent falls back to the sensible defaults defined in the script.

| Property | Type | Description |
| :--- | :--- | :--- |
| `botName` | String | The title shown in the header of the chat window. |
| `welcomeMessage` | String | The initial message sent by the bot upon loading. |
| `quickReplies` | Array of Objects | Buttons shown after the bot speaks. Format: `{ label: "Button Text", text: "What user says when clicked" }` |
| `autoReplies` | Object | Key-value pairs for keyword matching. If the user's message contains the key (lowercase), the bot replies with the value. You can use markdown-style links like `[Link Text](URL)`. `\n` creates a new line. |
| `defaultReply` | String | The fallback message if the bot doesn't recognize any keywords in the user's input. |

## 5. Notes on Responsive Design
The agent is designed to be fully responsive:

- On desktop, it floats quietly at the bottom right.
- On mobile devices (max-width 480px), the chat window expands to fill most of the screen when opened, providing an app-like experience.

## 6. Maintenance: How to Add New Questions and Answers
You can easily update the questions and answers without touching the core `chat-agent.js` file. All configurations are handled in the HTML file where you initialize the agent.

### A. Updating the Clickable Buttons (Quick Replies)
To add a new button that users can click, update the `quickReplies` array in your initialization script.

Format:

```javascript
quickReplies: [
    { label: 'Trading Account', text: 'How to open a trading account?' },
    // Add your new button here:
    { label: 'New Topic', text: 'Tell me about the new topic.' }
]
```
- **label**: This is the short text that appears on the button.
- **text**: This is the exact phrase that gets sent as a message when the user clicks the button.

### B. Updating the Bot's Answers (Auto Replies)
To teach the bot how to answer new questions, update the `autoReplies` object. The bot uses simple keyword matching.

Format:

```javascript
autoReplies: {
    'trading account': 'To open a Trading Account, you can process your KYC online...',
    // Add your new keyword and answer here:
    'new topic': 'Here is the information about the new topic. You can learn more [here](https://chatmax.com.np).'
}
```

- **The Key (Left Side)**: This must be in lowercase. The bot will check if the user's typed message (or clicked button text) contains this keyword/phrase. E.g., 'new topic'.
- **The Value (Right Side)**: This is the response the bot will give.
- **Links**: Use standard Markdown formatting for links: `[Visible Text](https://link-url.com)`.
- **Line Breaks**: Use `\n` to force a new line in the bot's message.

## 7 Omnichannel Backend Entity Flowchart
flowchart TD
    %% Define External Actors
    UserWA(User via WhatsApp API) -.->|JSON| WebhookWA(webhooks.py: WhatsApp Endpoint)
    UserWeb(User via Web Widget) -.->|JSON| WebhookWeb(webhooks.py: Web Endpoint)
    AgentDash(Agent Dashboard / React) -.->|WebSockets| WebhookWS(WebSocket Endpoint)

    %% Webhook Normalization
    subgraph FastAPI Routers
        WebhookWA -->|Normalizes to 'IncomingMessage'| Router
        WebhookWeb -->|Normalizes to 'IncomingMessage'| Router
    end

    %% Core Services
    subgraph Omnichannel Service (omnichannel.py)
        Router(OmnichannelService.process_incoming_message)
        
        Router --> IdentifyUser[1. Identify User in DB]
        IdentifyUser --> IdentifyConv[2. Find/Create Active Conversation]
        IdentifyConv --> DetectLang[3. LanguageService.detect_language]
        DetectLang --> LogUserMsg[4. Log Message to InteractionLog]
        
        LogUserMsg --> StateCheck{5. Check Conversation Status}
        
        %% State Branches
        StateCheck -->|ACTIVE_HUMAN| HumanRoute[Route to Agent Dashboard]
        StateCheck -->|ACTIVE_AUTO| AutoRoute[FAQService.find_best_match]
        
        %% Auto Route Details
        AutoRoute --> GetFAQ[(Query 'faqs' DB by Language)]
        GetFAQ --> FormatReply[Format Bot Answer]
        FormatReply --> LogBotMsg[6. Log Bot Reply to InteractionLog]
        LogBotMsg --> SendOutbound[7. Send Outbound Message]
        
        %% Human Route Details
        HumanRoute --> WebhookWS
        WebhookWS -.-> AgentDash
        AgentDash -.->|Agent Types Reply| SendOutboundAgent[Agent sends reply via API]
        SendOutboundAgent --> LogAgentMsg[Log Agent Reply to InteractionLog]
        LogAgentMsg --> SendOutbound
    end

    %% Outbound Dispatcher
    subgraph Outbound Dispatcher
        SendOutbound --> ChannelCheck{Which Channel?}
        ChannelCheck -->|WhatsApp| OutWA[Call Meta Graph API]
        ChannelCheck -->|Web Widget| OutWeb[Send via WebSockets]
    end
    
    OutWA -.-> UserWA
    OutWeb -.-> UserWeb
    
    %% Database Note
    Database[(PostgreSQL DB)]
    IdentifyUser -.-> Database
    IdentifyConv -.-> Database
    LogUserMsg -.-> Database
    GetFAQ -.-> Database
    LogBotMsg -.-> Database
    LogAgentMsg -.-> Database

    classDef external fill:#f9f,stroke:#333,stroke-width:2px;
    classDef process fill:#bbf,stroke:#333,stroke-width:2px;
    classDef decision fill:#ff9,stroke:#333,stroke-width:2px;
    classDef db fill:#fbd,stroke:#333,stroke-width:2px;

    class UserWA,UserWeb,AgentDash external;
    class Router,IdentifyUser,IdentifyConv,DetectLang,LogUserMsg,AutoRoute,FormatReply,LogBotMsg,SendOutbound,SendOutboundAgent,LogAgentMsg,OutWA,OutWeb process;
    class StateCheck,ChannelCheck decision;
    class Database,GetFAQ db;

### Step-by-Step Breakdown of the Flow:
Ingestion & Normalization: webhooks.py receives a raw payload from Meta (WhatsApp) or your Website. It extracts just the text and the phone number/session ID, converting it into a strict Pydantic IncomingMessage object.

User & Conversation Linking: OmnichannelService takes the IncomingMessage. It talks to the Database to find out who this user is and if they currently have an open chat (Conversation).

Language & Logging: The text is passed to LanguageService to detect English vs. Nepali. Then, the raw message is permanently saved to the InteractionLog table.

The State Fork: The system checks the status of the Conversation:

If AUTO_MODE: It queries the faqs database using the detected language. It formulates a reply, logs the bot's reply to the database, and sends it out.

If HUMAN_MODE: The bot stays quiet. The message is simply routed up to the React Agent Dashboard for a human to read.

Outbound Dispatch: When the bot (or the human agent) creates a response, the SendOutbound function checks the channel. If it's a WhatsApp user, it fires an HTTP request to Meta's servers. If it's a web user, it fires a WebSocket event back to the browser.