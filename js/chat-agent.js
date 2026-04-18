/**
 * ChatMax Chat Agent - Core Logic
 * 
 * To add new questions/replies, simply update the CHAT_DATA object below.
 */

const CHAT_DATA = {
    botName: 'ChatMax Support',
    welcomeMessage: 'Namaste! Welcome to ChatMax Securities. How can we assist your investment journey today?',
    
    // Buttons shown to the user
    quickReplies: [
        { label: 'Trading Account', text: 'How to open a trading account?' },
        { label: 'DEMAT Account', text: 'How to open a DEMAT account?' },
        { label: 'Market Status', text: 'What is the current NEPSE status?' },
        { label: 'Contact Us', text: 'What are your contact details?' }
    ],

    // Keyword matching logic (lowercase keys)
    autoReplies: {
        'trading account': 'To open a Trading Account (TMS), you can fill our online KYC form here: [Online Registration](https://#####.nepsetms.com.np/client-registration). You will need your Citizenship, Photo, and Bank Details.',
        'demat account': 'You can open a DEMAT & Meroshare account online through our DP portal. [Click here to open](https://dp.chatmax.com.np/DPForm?type=demat). The annual charge is Rs. 150.',
        'contact': 'ChatMax Securities Limited (Broker no. ##)\n, Kathmandu, Nepal\nPhone: 01-####### / ########\nEmail: contact@chatmax.com.np',
        'services': 'We provide Stock Brokerage, Depository Services (DEMAT), Portfolio Advisory, and support for IPO/FPO/Right Share applications.',
        'nepse': 'For real-time NEPSE data and your portfolio status, please log in to your TMS account or check the official NEPSE website.',
        'hello': 'Hello! How can we help you today with your stock market needs?',
        'hi': 'Hi! Welcome to ChatMax Support.',
        'thank': 'Happy to help! Let us know if you have more questions.',
        'bye': 'Thank you for choosing ChatMax. Happy investing!'
    },
    
    defaultReply: "I'm sorry, I don't have a specific answer for that. Please call our support desk at 01-######## or visit us at Office for detailed assistance.",
    containerId: 'chatmax-chat-container'
};

class ChatMaxChatAgent {
    constructor(userConfig = {}) {
        // Merge defaults with any user-provided overrides
        this.config = { ...CHAT_DATA, ...userConfig };
        this.isOpen = false;
        this.init();
    }

    init() {
        this.createWidget();
        this.bindEvents();
        // Show welcome message
        setTimeout(() => {
            this.addMessage(this.config.welcomeMessage, 'bot');
            this.addQuickReplies();
        }, 500);
    }

    createWidget() {
        const container = document.getElementById(this.config.containerId) || document.body;
        
        const widgetHtml = `
            <div class="chatmax-chat-widget">
                <div class="chatmax-chat-window" id="cm-chat-window">
                    <div class="chatmax-chat-header">
                        <div class="chatmax-chat-header-title">
                            <svg viewBox="0 0 24 24" width="24" height="24" fill="#fff"><path d="M12,2C6.48,2,2,6.48,2,12c0,1.82,0.49,3.53,1.35,5L2,22l5.15-1.32C8.58,21.54,10.24,22,12,22c5.52,0,10-4.48,10-10 S17.52,2,12,2z M17,15.59c-0.23,0.64-1.12,1.21-1.8,1.31c-0.62,0.09-1.42,0.18-2.39-0.14c-0.34-0.11-0.81-0.27-1.41-0.53 c-2.48-1.05-4.08-3.6-4.21-3.77c-0.13-0.17-1.01-1.34-1.01-2.56c0-1.22,0.64-1.82,0.86-2.06C7.26,7.6,7.56,7.5,7.86,7.5 c0.1,0,0.19,0,0.27,0c0.28,0,0.44,0.01,0.6,0.39c0.2,0.48,0.69,1.69,0.75,1.81c0.06,0.13,0.1,0.28,0.02,0.45 c-0.08,0.17-0.12,0.27-0.24,0.41c-0.12,0.14-0.25,0.31-0.36,0.41c-0.13,0.12-0.26,0.26-0.12,0.51c0.14,0.24,0.62,1.03,1.34,1.67 c0.93,0.83,1.71,1.09,1.96,1.21c0.24,0.12,0.39,0.1,0.53-0.06c0.14-0.16,0.62-0.72,0.78-0.97c0.16-0.25,0.33-0.21,0.55-0.13 c0.23,0.08,1.44,0.68,1.69,0.81c0.25,0.12,0.41,0.19,0.47,0.29C17.23,14.65,17.23,15.15,17,15.59z"/></svg>
                            ${this.config.botName}
                        </div>
                        <div class="chatmax-chat-header-controls">
                            <button class="chatmax-chat-control-btn" id="cm-chat-minimize" title="Minimize">&minus;</button>
                            <button class="chatmax-chat-control-btn" id="cm-chat-close" title="Close">&times;</button>
                        </div>
                    </div>
                    <div class="chatmax-chat-messages" id="cm-chat-messages">
                        <!-- Messages go here -->
                    </div>
                    <div class="chatmax-chat-input-area">
                        <input type="text" class="chatmax-chat-input" id="cm-chat-input" placeholder="Type a message...">
                        <button class="chatmax-chat-send-btn" id="cm-chat-send">
                            <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
                        </button>
                    </div>
                </div>
                <div class="chatmax-chat-fab" id="cm-chat-fab">
                    <svg viewBox="0 0 24 24"><path d="M12,2C6.48,2,2,6.48,2,12c0,1.82,0.49,3.53,1.35,5L2,22l5.15-1.32C8.58,21.54,10.24,22,12,22c5.52,0,10-4.48,10-10 S17.52,2,12,2z M17,15.59c-0.23,0.64-1.12,1.21-1.8,1.31c-0.62,0.09-1.42,0.18-2.39-0.14c-0.34-0.11-0.81-0.27-1.41-0.53 c-2.48-1.05-4.08-3.6-4.21-3.77c-0.13-0.17-1.01-1.34-1.01-2.56c0-1.22,0.64-1.82,0.86-2.06C7.26,7.6,7.56,7.5,7.86,7.5 c0.1,0,0.19,0,0.27,0c0.28,0,0.44,0.01,0.6,0.39c0.2,0.48,0.69,1.69,0.75,1.81c0.06,0.13,0.1,0.28,0.02,0.45 c-0.08,0.17-0.12,0.27-0.24,0.41c-0.12,0.14-0.25,0.31-0.36,0.41c-0.13,0.12-0.26,0.26-0.12,0.51c0.14,0.24,0.62,1.03,1.34,1.67 c0.93,0.83,1.71,1.09,1.96,1.21c0.24,0.12,0.39,0.1,0.53-0.06c0.14-0.16,0.62-0.72,0.78-0.97c0.16-0.25,0.33-0.21,0.55-0.13 c0.23,0.08,1.44,0.68,1.69,0.81c0.25,0.12,0.41,0.19,0.47,0.29C17.23,14.65,17.23,15.15,17,15.59z"/></svg>
                </div>
            </div>
        `;

        const wrapper = document.createElement('div');
        wrapper.innerHTML = widgetHtml;
        container.appendChild(wrapper.firstElementChild);

        this.elements = {
            widget: document.querySelector('.chatmax-chat-widget'),
            fab: document.getElementById('cm-chat-fab'),
            window: document.getElementById('cm-chat-window'),
            minimize: document.getElementById('cm-chat-minimize'),
            close: document.getElementById('cm-chat-close'),
            messages: document.getElementById('cm-chat-messages'),
            input: document.getElementById('cm-chat-input'),
            send: document.getElementById('cm-chat-send')
        };
    }

    bindEvents() {
        this.elements.fab.addEventListener('click', () => this.toggleChat());
        this.elements.minimize.addEventListener('click', () => this.toggleChat());
        this.elements.close.addEventListener('click', () => this.closeCompletely());
        
        this.elements.send.addEventListener('click', () => this.handleSend());
        this.elements.input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.handleSend();
        });
    }

    toggleChat() {
        this.isOpen = !this.isOpen;
        if (this.isOpen) {
            this.elements.window.classList.add('open');
            this.elements.input.focus();
        } else {
            this.elements.window.classList.remove('open');
        }
    }

    closeCompletely() {
        this.elements.widget.style.display = 'none';
    }

    handleSend() {
        const text = this.elements.input.value.trim();
        if (!text) return;

        this.addMessage(text, 'user');
        this.elements.input.value = '';

        this.showTypingIndicator();
        setTimeout(() => {
            this.removeTypingIndicator();
            this.processReply(text);
        }, 800);
    }

    handleQuickReply(text) {
        this.addMessage(text, 'user');
        this.showTypingIndicator();
        setTimeout(() => {
            this.removeTypingIndicator();
            this.processReply(text);
        }, 800);
    }

    processReply(text) {
        const lowerText = text.toLowerCase();
        let reply = this.config.defaultReply;

        for (const [keyword, response] of Object.entries(this.config.autoReplies)) {
            if (lowerText.includes(keyword)) {
                reply = response;
                break;
            }
        }

        this.addMessage(reply, 'bot');
        
        setTimeout(() => {
            this.addQuickReplies();
        }, 2000);
    }

    formatMessage(text) {
        const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
        let htmlText = text.replace(linkRegex, '<a href="$2" target="_blank" style="color: #0277bd; text-decoration: underline;">$1</a>');
        htmlText = htmlText.replace(/\n/g, '<br>');
        return htmlText;
    }

    addMessage(text, sender) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `chatmax-chat-message ${sender}`;
        msgDiv.innerHTML = this.formatMessage(text);
        
        this.elements.messages.appendChild(msgDiv);
        this.scrollToBottom();
    }

    addQuickReplies() {
        const existing = this.elements.messages.querySelector('.chatmax-chat-quick-replies');
        if (existing) existing.remove();

        if (!this.config.quickReplies || this.config.quickReplies.length === 0) return;

        const qrContainer = document.createElement('div');
        qrContainer.className = 'chatmax-chat-quick-replies';

        this.config.quickReplies.forEach(qr => {
            const btn = document.createElement('button');
            btn.className = 'chatmax-chat-quick-reply-btn';
            btn.textContent = qr.label;
            btn.onclick = () => {
                qrContainer.remove();
                this.handleQuickReply(qr.text);
            };
            qrContainer.appendChild(btn);
        });

        this.elements.messages.appendChild(qrContainer);
        this.scrollToBottom();
    }

    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'chatmax-chat-message bot typing-indicator';
        typingDiv.id = 'cm-typing-indicator';
        typingDiv.innerHTML = '<i>Typing...</i>';
        this.elements.messages.appendChild(typingDiv);
        this.scrollToBottom();
    }

    removeTypingIndicator() {
        const typingDiv = document.getElementById('cm-typing-indicator');
        if (typingDiv) typingDiv.remove();
    }

    scrollToBottom() {
        this.elements.messages.scrollTop = this.elements.messages.scrollHeight;
    }
}

// Attach to window object
window.ChatMaxChatAgent = ChatMaxChatAgent;
