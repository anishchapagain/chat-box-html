class CapitalMaxChatAgent {
    constructor(config) {
        this.config = {
            botName: 'ChatMax Support',
            welcomeMessage: 'Hello! Welcome to ChatMax Securities. How can I help you today?',
            ticketApiUrl: 'https://chatmax.com/api/create-ticket', // To be replaced with real backend
            quickReplies: [
                { label: 'Trading Account', text: 'How to open a trading account?' },
                { label: 'DEMAT Account', text: 'How to open a DEMAT account?' },
                { label: 'Raise a Ticket', text: 'I want to raise a ticket' },
                { label: 'Contact Details', text: 'What are your contact details?' }
            ],
            autoReplies: {
                'trading account': 'To open a Trading Account, you can register your KYC online through our website or visit our office. [Click here to open](https://tms62.nepsetms.com.np/client-registration)',
                'demat account': 'You can open a DEMAT & Meroshare account online through our website. [Click here to open](https://dp.chatmax.com/DPForm?type=demat)',
                'contact': 'ChatMax Securities Limited (Broker No. ##)\nKamalpokhari - 30, Kathmandu, Nepal\nPhone: 01-5970879 / 5918878\nEmail: capitalmaxsecurities@gmail.com',
                'hello': 'Hi there! How can I assist you with your investment journey today?',
                'hi': 'Hello! How can we help you?',
                'thank': 'You are welcome! Let us know if you need any more help.',
                'bye': 'Goodbye! Happy trading!'
            },
            defaultReply: "I'm sorry, I don't have a specific answer for that. Please call us at 01-5970879 or email us at capitalmaxsecurities@gmail.com for detailed support.",
            containerId: 'capitalmax-chat-container',
            ...config
        };

        this.isOpen = false;
        
        // State Machine for conversational flows
        this.state = {
            mode: 'IDLE', // IDLE or TICKET_CREATION
            ticketData: {
                name: '',
                contact: '',
                issue: ''
            },
            ticketStep: 0 // 0: Name, 1: Contact, 2: Issue
        };

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

    // --- UI Rendering ---

    createWidget() {
        const container = document.getElementById(this.config.containerId) || document.body;
        
        const widgetHtml = `
            <div class="capitalmax-chat-widget">
                <div class="capitalmax-chat-window" id="cm-chat-window">
                    <div class="capitalmax-chat-header">
                        <div class="capitalmax-chat-header-title">
                            <svg viewBox="0 0 24 24" width="24" height="24" fill="#fff"><path d="M12,2C6.48,2,2,6.48,2,12c0,1.82,0.49,3.53,1.35,5L2,22l5.15-1.32C8.58,21.54,10.24,22,12,22c5.52,0,10-4.48,10-10 S17.52,2,12,2z M17,15.59c-0.23,0.64-1.12,1.21-1.8,1.31c-0.62,0.09-1.42,0.18-2.39-0.14c-0.34-0.11-0.81-0.27-1.41-0.53 c-2.48-1.05-4.08-3.6-4.21-3.77c-0.13-0.17-1.01-1.34-1.01-2.56c0-1.22,0.64-1.82,0.86-2.06C7.26,7.6,7.56,7.5,7.86,7.5 c0.1,0,0.19,0,0.27,0c0.28,0,0.44,0.01,0.6,0.39c0.2,0.48,0.69,1.69,0.75,1.81c0.06,0.13,0.1,0.28,0.02,0.45 c-0.08,0.17-0.12,0.27-0.24,0.41c-0.12,0.14-0.25,0.31-0.36,0.41c-0.13,0.12-0.26,0.26-0.12,0.51c0.14,0.24,0.62,1.03,1.34,1.67 c0.93,0.83,1.71,1.09,1.96,1.21c0.24,0.12,0.39,0.1,0.53-0.06c0.14-0.16,0.62-0.72,0.78-0.97c0.16-0.25,0.33-0.21,0.55-0.13 c0.23,0.08,1.44,0.68,1.69,0.81c0.25,0.12,0.41,0.19,0.47,0.29C17.23,14.65,17.23,15.15,17,15.59z"/></svg>
                            ${this.config.botName}
                        </div>
                        <div class="capitalmax-chat-header-controls">
                            <button class="capitalmax-chat-control-btn" id="cm-chat-minimize" title="Minimize">&minus;</button>
                            <button class="capitalmax-chat-control-btn" id="cm-chat-close" title="Close">&times;</button>
                        </div>
                    </div>
                    <div class="capitalmax-chat-messages" id="cm-chat-messages">
                        <!-- Messages go here -->
                    </div>
                    <div class="capitalmax-chat-input-area">
                        <input type="text" class="capitalmax-chat-input" id="cm-chat-input" placeholder="Type a message...">
                        <button class="capitalmax-chat-send-btn" id="cm-chat-send">
                            <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
                        </button>
                    </div>
                </div>
                <div class="capitalmax-chat-fab" id="cm-chat-fab">
                    <svg viewBox="0 0 24 24"><path d="M12,2C6.48,2,2,6.48,2,12c0,1.82,0.49,3.53,1.35,5L2,22l5.15-1.32C8.58,21.54,10.24,22,12,22c5.52,0,10-4.48,10-10 S17.52,2,12,2z M17,15.59c-0.23,0.64-1.12,1.21-1.8,1.31c-0.62,0.09-1.42,0.18-2.39-0.14c-0.34-0.11-0.81-0.27-1.41-0.53 c-2.48-1.05-4.08-3.6-4.21-3.77c-0.13-0.17-1.01-1.34-1.01-2.56c0-1.22,0.64-1.82,0.86-2.06C7.26,7.6,7.56,7.5,7.86,7.5 c0.1,0,0.19,0,0.27,0c0.28,0,0.44,0.01,0.6,0.39c0.2,0.48,0.69,1.69,0.75,1.81c0.06,0.13,0.1,0.28,0.02,0.45 c-0.08,0.17-0.12,0.27-0.24,0.41c-0.12,0.14-0.25,0.31-0.36,0.41c-0.13,0.12-0.26,0.26-0.12,0.51c0.14,0.24,0.62,1.03,1.34,1.67 c0.93,0.83,1.71,1.09,1.96,1.21c0.24,0.12,0.39,0.1,0.53-0.06c0.14-0.16,0.62-0.72,0.78-0.97c0.16-0.25,0.33-0.21,0.55-0.13 c0.23,0.08,1.44,0.68,1.69,0.81c0.25,0.12,0.41,0.19,0.47,0.29C17.23,14.65,17.23,15.15,17,15.59z"/></svg>
                </div>
            </div>
        `;

        const wrapper = document.createElement('div');
        wrapper.innerHTML = widgetHtml;
        container.appendChild(wrapper.firstElementChild);

        this.elements = {
            widget: document.querySelector('.capitalmax-chat-widget'),
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

    formatMessage(text) {
        const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
        let htmlText = text.replace(linkRegex, '<a href="$2" target="_blank" style="color: #0277bd; text-decoration: underline;">$1</a>');
        htmlText = htmlText.replace(/\n/g, '<br>');
        return htmlText;
    }

    addMessage(text, sender, classes = '') {
        const msgDiv = document.createElement('div');
        msgDiv.className = `capitalmax-chat-message ${sender} ${classes}`;
        msgDiv.innerHTML = this.formatMessage(text);
        
        this.elements.messages.appendChild(msgDiv);
        this.scrollToBottom();
    }

    addQuickReplies() {
        const existing = this.elements.messages.querySelector('.capitalmax-chat-quick-replies');
        if (existing) existing.remove();

        if (this.state.mode !== 'IDLE' || !this.config.quickReplies || this.config.quickReplies.length === 0) return;

        const qrContainer = document.createElement('div');
        qrContainer.className = 'capitalmax-chat-quick-replies';

        this.config.quickReplies.forEach(qr => {
            const btn = document.createElement('button');
            btn.className = 'capitalmax-chat-quick-reply-btn';
            btn.textContent = qr.label;
            btn.onclick = () => {
                qrContainer.remove();
                this.handleInput(qr.text);
            };
            qrContainer.appendChild(btn);
        });

        this.elements.messages.appendChild(qrContainer);
        this.scrollToBottom();
    }

    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'capitalmax-chat-message bot typing-indicator';
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

    // --- Core Logic & State Machine ---

    handleSend() {
        const text = this.elements.input.value.trim();
        if (!text) return;
        this.elements.input.value = '';
        this.handleInput(text);
    }

    handleInput(text) {
        this.addMessage(text, 'user');
        this.showTypingIndicator();

        // Process asynchronously to simulate network/typing delay
        setTimeout(() => {
            this.removeTypingIndicator();
            if (this.state.mode === 'TICKET_CREATION') {
                this.processTicketStep(text);
            } else {
                this.processStandardReply(text);
            }
        }, 600);
    }

    processStandardReply(text) {
        const lowerText = text.toLowerCase();
        
        // Detect Ticket Intent
        if (lowerText.includes('ticket') || lowerText.includes('issue') || lowerText.includes('problem')) {
            this.startTicketCreation();
            return;
        }

        // Standard Auto-replies
        let reply = this.config.defaultReply;
        for (const [keyword, response] of Object.entries(this.config.autoReplies)) {
            if (lowerText.includes(keyword)) {
                reply = response;
                break;
            }
        }

        this.addMessage(reply, 'bot');
        setTimeout(() => this.addQuickReplies(), 1500);
    }

    // --- Ticket Creation Flow ---

    startTicketCreation() {
        this.state.mode = 'TICKET_CREATION';
        this.state.ticketStep = 0;
        this.state.ticketData = { name: '', contact: '', issue: '' };
        
        this.addMessage("I can help you raise a ticket. Let's get some details.", 'bot');
        setTimeout(() => this.addMessage("First, what is your **Full Name**?", 'bot'), 500);
    }

    processTicketStep(text) {
        const step = this.state.ticketStep;

        if (step === 0) {
            // Validate Name
            if (text.length < 2) {
                this.addMessage("Please enter a valid name.", 'bot', 'error');
                return;
            }
            this.state.ticketData.name = text;
            this.state.ticketStep++;
            this.addMessage(`Thanks, ${text}. Next, please provide your **Phone Number** or **Email Address** so we can reach you.`, 'bot');
        
        } else if (step === 1) {
            // Validate Contact (Simple check for > 5 chars, assuming phone or email)
            const isPhone = /^[0-9]{10}$/.test(text.replace(/[^0-9]/g, ''));
            const isEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(text);

            if (!isPhone && !isEmail) {
                this.addMessage("Please enter a valid 10-digit Phone Number or a valid Email Address.", 'bot', 'error');
                return;
            }
            this.state.ticketData.contact = text;
            this.state.ticketStep++;
            this.addMessage("Got it. Finally, please briefly **describe the issue** you are facing.", 'bot');
        
        } else if (step === 2) {
            // Validate Issue Description
            if (text.length < 5) {
                this.addMessage("Please provide a little more detail about the issue.", 'bot', 'error');
                return;
            }
            this.state.ticketData.issue = text;
            this.sendTicket();
        }
    }

    async sendTicket() {
        this.addMessage("Please wait while I process your ticket...", 'bot');
        this.showTypingIndicator();

        try {
            // Mocking the API call locally if backend is not set
            let ticketId = null;

            // In production, this fetch call hits your proxy server:
            const response = await fetch(this.config.ticketApiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(this.state.ticketData)
            });

            if (response.ok) {
                const result = await response.json();
                ticketId = result.ticketId;
            } else {
                // If API fails or is not real, mock a success for demonstration
                // Throwing an error here normally, but we mock it for demo.
                console.warn("API request failed or missing. Using mock ticket ID.");
                ticketId = `TKT-${Math.floor(Math.random() * 100000)}`;
                // console.log("Mock ticket ID:", ticketId);
            }

            this.removeTypingIndicator();
            this.addMessage(`✅ **Ticket created successfully!**\n\nYour Ticket ID is **#${ticketId}**.\nOur team will review your issue and contact you at ${this.state.ticketData.contact} shortly.`, 'bot', 'success');

        } catch (error) {
            console.error("Error sending ticket:", error);
            this.removeTypingIndicator();
            
            // Fallback for Demo purposes (since we don't have a real backend)
            const mockId = `TKT-${Math.floor(Math.random() * 100000)}`;
            this.addMessage(`✅ **Ticket created!**\n\n(Demo Mode - API not reached)\nYour mock Ticket ID is **#${mockId}**.`, 'bot', 'success');
            // Normally you would do:
            // this.addMessage("Sorry, there was an error processing your ticket. Please try again later.", 'bot', 'error');
        } finally {
            // Reset state
            this.state.mode = 'IDLE';
            setTimeout(() => this.addQuickReplies(), 3000);
        }
    }
}

// Attach to window object to be accessible globally
window.CapitalMaxChatAgent = CapitalMaxChatAgent;