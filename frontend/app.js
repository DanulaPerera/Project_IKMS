/**
 * IKMS Conversational QA Chat Application
 * 
 * Handles all frontend logic for the conversational question-answering interface,
 * including API communication, message display, and session management.
 */

class ChatApp {
    constructor() {
        // API configuration - dynamically detect base URL
        // Use current origin when deployed, localhost for local development
        this.apiBase = window.location.hostname === 'localhost'
            ? 'http://localhost:8000'
            : window.location.origin;

        // Session state
        this.sessionId = null;
        this.turnNumber = 0;
        this.isProcessing = false;

        // DOM elements
        this.elements = {
            messagesContainer: document.getElementById('messages-container'),
            questionInput: document.getElementById('question-input'),
            sendBtn: document.getElementById('send-btn'),
            typingIndicator: document.getElementById('typing-indicator'),
            sessionIdDisplay: document.getElementById('session-id-display'),
            turnCounter: document.getElementById('turn-counter'),
            newSessionBtn: document.getElementById('new-session-btn'),
            clearSessionBtn: document.getElementById('clear-session-btn'),
            uploadDocBtn: document.getElementById('upload-doc-btn'),
            fileInput: document.getElementById('file-input')
        };

        this.init();
    }

    /**
     * Initialize the application
     */
    init() {
        this.attachEventListeners();
        this.createNewSession();
        this.setupTextareaAutoResize();
    }

    /**
     * Attach event listeners to UI elements
     */
    attachEventListeners() {
        // Send message on button click
        this.elements.sendBtn.addEventListener('click', () => this.sendMessage());

        // Send message on Enter key (Shift+Enter for new line)
        this.elements.questionInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Session management buttons
        this.elements.newSessionBtn.addEventListener('click', () => this.createNewSession());
        this.elements.clearSessionBtn.addEventListener('click', () => this.clearSession());

        // Document upload handlers
        this.elements.uploadDocBtn.addEventListener('click', () => {
            this.elements.fileInput.click();
        });
        this.elements.fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.uploadDocument(e.target.files[0]);
                // Reset file input so the same file can be uploaded again if needed
                e.target.value = '';
            }
        });
    }

    /**
     * Setup auto-resize for textarea
     */
    setupTextareaAutoResize() {
        const textarea = this.elements.questionInput;
        textarea.addEventListener('input', () => {
            textarea.style.height = 'auto';
            textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
        });
    }

    /**
     * Send a message to the conversational QA API
     */
    async sendMessage() {
        const question = this.elements.questionInput.value.trim();

        // Validation
        if (!question || this.isProcessing) return;

        // Update UI
        this.isProcessing = true;
        this.elements.sendBtn.disabled = true;
        this.addMessage(question, 'user');
        this.elements.questionInput.value = '';
        this.elements.questionInput.style.height = 'auto';
        this.showTypingIndicator();

        try {
            const response = await fetch(`${this.apiBase}/qa/conversation`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    question: question,
                    session_id: this.sessionId
                })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            this.hideTypingIndicator();

            // Update session info
            this.sessionId = data.session_id;
            this.turnNumber = data.turn_number;
            this.updateSessionInfo();

            // Display assistant message
            this.addMessage(data.answer, 'assistant', {
                context: data.context,
                historyUsed: data.history_used
            });

        } catch (error) {
            this.hideTypingIndicator();
            console.error('Error sending message:', error);

            this.addMessage(
                `❌ Sorry, I encountered an error: ${error.message}. Please check that the server is running and try again.`,
                'assistant',
                { isError: true }
            );
        } finally {
            this.isProcessing = false;
            this.elements.sendBtn.disabled = false;
            this.elements.questionInput.focus();
        }
    }

    /**
     * Add a message to the chat display
     * 
     * @param {string} content - Message content
     * @param {string} sender - 'user' or 'assistant'
     * @param {Object} metadata - Additional metadata (context, historyUsed, etc.)
     */
    addMessage(content, sender, metadata = {}) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;

        // Create avatar
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';

        if (sender === 'user') {
            avatarDiv.innerHTML = `
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2a5 5 0 100 10 5 5 0 000-10zm0 12c-4.42 0-8 1.79-8 4v2h16v-2c0-2.21-3.58-4-8-4z"/>
                </svg>
            `;
        } else {
            avatarDiv.innerHTML = `
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2a9 9 0 00-9 9v7a2 2 0 002 2h2v-6H5v-3a7 7 0 0114 0v3h-2v6h2a2 2 0 002-2v-7a9 9 0 00-9-9z"/>
                </svg>
            `;
        }

        // Create content
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        // Format message content (preserve line breaks)
        const formattedContent = content.split('\n').map(line =>
            `<p>${this.escapeHtml(line) || '&nbsp;'}</p>`
        ).join('');
        contentDiv.innerHTML = formattedContent;

        // Add metadata badges
        if (metadata.historyUsed && sender === 'assistant') {
            const badge = document.createElement('span');
            badge.className = 'history-badge';
            badge.textContent = '🔗 Context-aware response';
            contentDiv.appendChild(badge);
        }

        // Assemble message
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);

        this.elements.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }

    /**
     * Show typing indicator
     */
    showTypingIndicator() {
        this.elements.typingIndicator.classList.remove('hidden');
        this.scrollToBottom();
    }

    /**
     * Hide typing indicator
     */
    hideTypingIndicator() {
        this.elements.typingIndicator.classList.add('hidden');
    }

    /**
     * Scroll chat container to bottom
     */
    scrollToBottom() {
        const container = this.elements.messagesContainer.parentElement;
        setTimeout(() => {
            container.scrollTop = container.scrollHeight;
        }, 100);
    }

    /**
     * Create a new conversation session
     */
    async createNewSession() {
        try {
            const response = await fetch(`${this.apiBase}/qa/session/new`, {
                method: 'POST'
            });

            if (!response.ok) {
                throw new Error('Failed to create new session');
            }

            const data = await response.json();
            this.sessionId = data.session_id;
            this.turnNumber = 0;
            this.updateSessionInfo();
            this.clearMessages();

            console.log('New session created:', this.sessionId);

        } catch (error) {
            console.error('Error creating session:', error);
            alert('Failed to create new session. Please refresh the page.');
        }
    }

    /**
     * Clear the current session's history
     */
    async clearSession() {
        if (!this.sessionId) return;

        if (!confirm('Are you sure you want to clear this conversation history?')) {
            return;
        }

        try {
            const response = await fetch(`${this.apiBase}/qa/session/${this.sessionId}/clear`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                throw new Error('Failed to clear session');
            }

            this.turnNumber = 0;
            this.updateSessionInfo();
            this.clearMessages();

            console.log('Session cleared:', this.sessionId);

        } catch (error) {
            console.error('Error clearing session:', error);
            alert('Failed to clear session history.');
        }
    }

    /**
     * Upload a PDF document to be indexed
     * 
     * @param {File} file - The file to upload
     */
    async uploadDocument(file) {
        // Validate file type
        if (!file.type.includes('pdf') && !file.name.toLowerCase().endsWith('.pdf')) {
            this.addMessage(
                '❌ Please upload a PDF file. Only PDF documents are supported for indexing.',
                'assistant',
                { isError: true }
            );
            return;
        }

        // Show upload progress message
        const uploadingMsg = `📤 Uploading "${file.name}"... Please wait.`;
        this.addMessage(uploadingMsg, 'assistant');
        this.showTypingIndicator();

        try {
            // Create form data
            const formData = new FormData();
            formData.append('file', file);

            // Upload to server
            const response = await fetch(`${this.apiBase}/index-pdf`, {
                method: 'POST',
                body: formData
            });

            this.hideTypingIndicator();

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Upload failed with status ${response.status}`);
            }

            const data = await response.json();

            // Display success message
            const successMsg = `✅ Document "${data.filename}" uploaded successfully!\n\n` +
                `📊 Indexed ${data.chunks_indexed} chunks.\n` +
                `💬 You can now ask questions about this document.`;
            this.addMessage(successMsg, 'assistant');

            console.log('Document uploaded:', data);

        } catch (error) {
            this.hideTypingIndicator();
            console.error('Error uploading document:', error);

            this.addMessage(
                `❌ Failed to upload document: ${error.message}\n\n` +
                `Please make sure the server is running and try again.`,
                'assistant',
                { isError: true }
            );
        }
    }

    /**
     * Update session info display
     */
    updateSessionInfo() {
        const shortId = this.sessionId ? this.sessionId.substring(0, 8) : '-';
        this.elements.sessionIdDisplay.querySelector('code').textContent = shortId;
        this.elements.turnCounter.textContent = `Turn: ${this.turnNumber}`;
    }

    /**
     * Clear all messages from the display
     */
    clearMessages() {
        this.elements.messagesContainer.innerHTML = `
            <div class="message assistant-message welcome">
                <div class="message-avatar">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 2a9 9 0 00-9 9v7a2 2 0 002 2h2v-6H5v-3a7 7 0 0114 0v3h-2v6h2a2 2 0 002-2v-7a9 9 0 00-9-9z"/>
                    </svg>
                </div>
                <div class="message-content">
                    <p><strong>Welcome back!</strong></p>
                    <p>I'm ready to help you explore your documents. Ask me anything!</p>
                    <p class="tip">💡 <em>Tip: I can remember our conversation, so feel free to ask follow-up questions.</em></p>
                </div>
            </div>
        `;
    }

    /**
     * Escape HTML to prevent XSS
     * 
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.chatApp = new ChatApp();
    console.log('IKMS Conversational QA Chat App initialized');
});
