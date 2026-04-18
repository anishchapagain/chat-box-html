# ChatMax Chat Agent

A lightweight, responsive, and WhatsApp-themed Chat Agent designed for seamless integration into the ChatMax Securities website. This agent provides instant support for stock brokerage services, account opening queries, and general investment assistance.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Web-orange.svg)

## 🚀 Overview

This project provides a client-side chat widget that mimics the familiar WhatsApp interface. It allows stock brokerage firms to automate common customer queries through a configurable keyword-matching system and interactive quick-reply buttons.

## ✨ Features

- **WhatsApp UI/UX**: Familiar interface including typing indicators and message bubbles.
- **Quick Replies**: Pre-defined buttons to guide users through common workflows (e.g., Opening a DEMAT account).
- **Keyword Auto-Response**: Intelligent matching for common stock market terms (TMS, KYC, NEPSE, etc.).
- **Fully Responsive**: Optimized for both desktop and mobile devices.
- **Zero Dependencies**: Built with Vanilla JS and CSS—no heavy frameworks required.
- **Markdown Support**: Bot replies support links and basic formatting.

## 📂 Project Structure

```text
D:\PythonProjects\ChatBotWhats\
├── index.html           # Professional demo landing page
├── TECH.md              # Technical deployment and API guide
├── css/
│   └── chat-agent.css   # Chat widget styling
└── js/
    └── chat-agent.js    # Core chat logic and state management
```

## 🛠️ Getting Started

### Prerequisites
- Any modern web browser.
- No backend server is required for the basic chat functionality.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/chatbotwhats.git
   ```
2. Open `index.html` in your browser to view the live demo and chat agent.

## 🔌 Integration Guide

To add the chat agent to your own website, follow these three steps:

### 1. Link Styles and Scripts
Add the CSS to your `<head>` and the JS before your closing `</body>` tag.

```html
<link rel="stylesheet" href="path/to/chat-agent.css">
<script src="path/to/chat-agent.js"></script>
```

### 2. Add the Container
Place a dedicated container div in your HTML.

```html
<div id="chatmax-chat-container"></div>
```

### 3. Initialize
Initialize the agent with your custom configurations:

```javascript
const chatAgent = new ChatMaxChatAgent({
    containerId: 'chatmax-chat-container',
    botName: 'Support Bot',
    welcomeMessage: 'How can I help you today?',
    autoReplies: {
        'trading': 'You can trade online via our TMS portal...'
    }
});
```

## ⚙️ Configuration Options

| Property | Type | Description |
| :--- | :--- | :--- |
| `botName` | String | Title displayed in the chat header. |
| `welcomeMessage` | String | The first message the bot sends. |
| `quickReplies` | Array | Buttons shown to the user. |
| `autoReplies` | Object | Key-value pairs for keyword matching. |
| `containerId` | String | The ID of the HTML element to inject the chat into. |

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For technical support or inquiries regarding ChatMax Securities services:
- **Email**: contact@chatmax.com.np
- **Phone**: 01-4412345
- **Website**: [chatmax.com.np](https://chatmax.com.np/)
>>>>>>> ed1f12c (Initial commit)
