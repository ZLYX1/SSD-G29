/**
 * Enhanced Messaging JavaScript with End-to-End Encryption Support
 * Integrates with encryption.js for secure messaging
 */

class SecureMessaging {
    constructor() {
        this.currentUserId = null;
        this.currentConversationId = null;
        this.encryptionEnabled = true;
        this.messageContainer = null;
        this.conversationList = null;
        this.isSubmitting = false; // Lock to prevent multiple submissions
        this.init();
    }

    init() {
        // Get user ID from the page
        this.currentUserId = window.currentUserId || null;
        
        // Get DOM elements
        this.messageContainer = document.getElementById('chatMessages');
        this.conversationList = document.getElementById('conversationsList');
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Check if encryption is available
        this.checkEncryptionSupport();
    }

    checkEncryptionSupport() {
        if (!window.crypto || !window.crypto.subtle) {
            this.encryptionEnabled = false;
            this.showEncryptionWarning();
        } else if (!window.MessageEncryption) {
            this.encryptionEnabled = false;
        } else {
            // MessageEncryption class is available
            this.encryptionEnabled = true;
        }
    }

    showEncryptionWarning() {
        const warningDiv = document.createElement('div');
        warningDiv.className = 'alert alert-warning';
        warningDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle"></i>
            <strong>Security Notice:</strong> End-to-end encryption is not available in this browser. 
            Messages will be sent as plain text.
        `;
        
        const container = document.querySelector('.messaging-container');
        if (container) {
            container.insertBefore(warningDiv, container.firstChild);
        }
    }

    setupEventListeners() {
        // NOTE: Send message form is handled by onsubmit="sendMessage(event)" in HTML
        // Don't add duplicate event listeners here to avoid multiple submissions
        
        // Conversation switching
        if (this.conversationList) {
            this.conversationList.addEventListener('click', (e) => {
                const conversationItem = e.target.closest('.conversation-item');
                if (conversationItem) {
                    const userId = conversationItem.dataset.userId;
                    if (userId) {
                        this.switchConversation(parseInt(userId));
                    }
                }
            });
        }

        // Auto-refresh messages
        this.startMessageRefresh();
    }

    async handleSendMessage(e) {
        e.preventDefault();
        
        // Prevent multiple concurrent submissions
        if (this.isSubmitting) {
            return;
        }
        
        this.isSubmitting = true;
        
        const form = e.target;
        const messageInput = form.querySelector('textarea[name="content"]') || form.querySelector('input[name="content"]');
        const recipientInput = form.querySelector('input[name="recipient_id"]');
        
        if (!messageInput || !recipientInput) {
            return;
        }

        const content = messageInput.value.trim();
        const recipientId = parseInt(recipientInput.value);
        
        if (!content || !recipientId) {
            return;
        }

        // Show sending indicator
        const sendButton = form.querySelector('button[type="submit"]');
        const originalText = sendButton ? sendButton.textContent : 'Send';
        
        try {
            if (sendButton) {
                sendButton.textContent = 'Sending...';
                sendButton.disabled = true;
            }

            let messageData = {
                recipient_id: recipientId,
                content: content
            };

            // Try to encrypt if encryption is enabled
            if (this.encryptionEnabled && window.MessageEncryption) {
                try {
                    // Create encryption instance if needed (should already exist from init)
                    if (!window.messageEncryption) {
                        window.messageEncryption = new window.MessageEncryption();
                    }
                    
                    // Generate conversation ID from user IDs (deterministic)
                    const currentUserId = window.currentUserId || parseInt(document.getElementById('currentUserId')?.value);
                    const conversationId = `${Math.min(currentUserId, recipientId)}_${Math.max(currentUserId, recipientId)}`;
                    
                    const conversationKey = await window.messageEncryption.getConversationKey(conversationId);
                    const encryptedData = await window.messageEncryption.encryptMessage(content, conversationKey);
                    
                    messageData = {
                        recipient_id: recipientId,
                        encrypted_data: encryptedData
                    };
                } catch (encError) {
                    // Keep the original messageData with plain content
                }
            }

            // Send the message
            const response = await fetch('/messaging/send', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.csrf_token
                },
                body: JSON.stringify(messageData)
            });

            const result = await response.json();

            if (result.success) {
                // Clear the input
                messageInput.value = '';
                
                // Add message to UI immediately
                this.addMessageToUI(result.message);
                
                // Scroll to bottom
                this.scrollToBottom();
                
                // Refresh conversation list to update last message
                this.refreshConversationList();
            } else {
                alert('Failed to send message: ' + result.error);
            }

        } catch (error) {
            alert('Failed to send message. Please try again.');
        } finally {
            // Release the submission lock
            this.isSubmitting = false;
            
            // Reset send button
            const sendButton = form.querySelector('button[type="submit"]');
            if (sendButton) {
                sendButton.textContent = originalText;
                sendButton.disabled = false;
            }
        }
    }

    async switchConversation(userId) {
        this.currentConversationId = userId;
        
        try {
            // Load messages for this conversation
            await this.loadMessages(userId);
            
            // Update UI to show active conversation
            this.updateActiveConversation(userId);
            
            // Mark messages as read
            this.markMessagesAsRead(userId);
            
        } catch (error) {
            // Error switching conversation
        }
    }

    async loadMessages(userId) {
        try {
            const response = await fetch(`/messaging/api/messages/${userId}`);
            const data = await response.json();
            
            if (data.messages) {
                // Clear current messages
                if (this.messageContainer) {
                    this.messageContainer.innerHTML = '';
                }
                
                // Decrypt and add each message
                for (const message of data.messages) {
                    await this.addMessageToUI(message);
                }
                
                this.scrollToBottom();
            }
        } catch (error) {
            // Error loading messages
        }
    }

    async addMessageToUI(message) {
        if (!this.messageContainer) return;

        let displayContent = message.content;

        // Try to decrypt if this is an encrypted message
        if (message.is_encrypted && this.encryptionEnabled && window.messageEncryption) {
            try {
                const otherUserId = message.sender_id === this.currentUserId ? 
                    message.recipient_id : message.sender_id;
                
                // Generate conversation ID in the same format as encryption
                const conversationId = `${Math.min(this.currentUserId, otherUserId)}_${Math.max(this.currentUserId, otherUserId)}`;
                
                const conversationKey = await window.messageEncryption.getConversationKey(conversationId);
                
                displayContent = await window.messageEncryption.decryptMessage({
                    encrypted_content: message.encrypted_content,
                    nonce: message.nonce,
                    algorithm: message.algorithm
                }, conversationKey);
                
            } catch (decError) {
                displayContent = '[Failed to decrypt message]';
            }
        }

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${message.sender_id === this.currentUserId ? 'sent' : 'received'}`;
        
        const encryptionIcon = message.is_encrypted ? 
            '<i class="fas fa-lock text-success" title="Encrypted"></i>' : 
            '<i class="fas fa-unlock text-muted" title="Not encrypted"></i>';
        
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-text">${this.escapeHtml(displayContent)}</div>
                <div class="message-meta">
                    <span class="message-time">${this.formatTimestamp(message.timestamp)}</span>
                    ${encryptionIcon}
                </div>
            </div>
        `;

        this.messageContainer.appendChild(messageDiv);
        
        // Scroll to bottom after adding the message
        this.scrollToBottom();
    }

    updateActiveConversation(userId) {
        // Remove active class from all conversations
        const conversations = document.querySelectorAll('.conversation-item');
        conversations.forEach(conv => conv.classList.remove('active'));
        
        // Add active class to current conversation
        const activeConv = document.querySelector(`.conversation-item[data-user-id="${userId}"]`);
        if (activeConv) {
            activeConv.classList.add('active');
        }
    }

    async markMessagesAsRead(userId) {
        try {
            await fetch(`/messaging/mark-read/${userId}`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': window.csrf_token
                }
            });
        } catch (error) {
            // Error marking messages as read
        }
    }

    async refreshConversationList() {
        try {
            const response = await fetch('/messaging/api/conversations');
            const data = await response.json();
            
            if (data.conversations && this.conversationList) {
                this.updateConversationList(data.conversations);
            }
        } catch (error) {
            // Error refreshing conversations
        }
    }

    updateConversationList(conversations) {
        // This would update the conversation list UI
        // Implementation depends on the specific HTML structure
    }

    startMessageRefresh() {
        // Refresh messages every 5 seconds if viewing a conversation
        setInterval(() => {
            if (this.currentConversationId) {
                this.loadMessages(this.currentConversationId);
            }
        }, 5000);

        // Refresh conversation list every 10 seconds
        setInterval(() => {
            this.refreshConversationList();
        }, 10000);
    }

    scrollToBottom() {
        if (this.messageContainer) {
            // Use requestAnimationFrame to ensure DOM updates are complete
            requestAnimationFrame(() => {
                this.messageContainer.scrollTop = this.messageContainer.scrollHeight;
            });
        }
    }

    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffMinutes = Math.floor(diffMs / (1000 * 60));
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

        // Same day - show time only
        if (diffDays === 0) {
            return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        }
        // Yesterday
        else if (diffDays === 1) {
            return 'Yesterday ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        }
        // Less than 7 days - show day and time
        else if (diffDays < 7) {
            return date.toLocaleDateString([], { weekday: 'short' }) + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        }
        // Older messages - show month/day and time
        else {
            return date.toLocaleDateString([], { month: '2-digit', day: '2-digit' }) + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Method to decrypt existing messages in the DOM on page load
    async decryptExistingMessages() {
        if (!this.encryptionEnabled || !window.messageEncryption) {
            return;
        }

        // Find all message elements that contain encrypted content
        const messageElements = document.querySelectorAll('.message');

        for (const messageElement of messageElements) {
            try {
                const messageContent = messageElement.querySelector('.message-content');
                const encryptedIcon = messageElement.querySelector('.fas.fa-lock');
                
                // Check if this is an encrypted message that needs decryption
                if (messageContent && encryptedIcon && 
                    messageContent.textContent.includes('[Encrypted Message - Decrypting...]')) {
                    
                    // Extract message data from data attributes if available
                    const messageData = {
                        encrypted_content: messageElement.dataset.encryptedContent,
                        nonce: messageElement.dataset.nonce,
                        algorithm: messageElement.dataset.algorithm,
                        sender_id: parseInt(messageElement.dataset.senderId),
                        recipient_id: parseInt(messageElement.dataset.recipientId),
                        is_encrypted: true
                    };
                    
                    // Skip if we don't have the required data attributes
                    if (!messageData.encrypted_content || !messageData.nonce) {
                        continue;
                    }
                    
                    // Determine the other user ID
                    const otherUserId = messageData.sender_id === this.currentUserId ? 
                        messageData.recipient_id : messageData.sender_id;
                    
                    // Generate conversation ID in the same format as encryption
                    const conversationId = `${Math.min(this.currentUserId, otherUserId)}_${Math.max(this.currentUserId, otherUserId)}`;
                    
                    // Get the conversation key
                    const conversationKey = await window.messageEncryption.getConversationKey(conversationId);
                    
                    // Decrypt the message
                    const decryptedContent = await window.messageEncryption.decryptMessage({
                        encrypted_content: messageData.encrypted_content,
                        nonce: messageData.nonce,
                        algorithm: messageData.algorithm
                    }, conversationKey);
                    
                    // Update the message content in the DOM
                    messageContent.textContent = decryptedContent;
                    
                } else {
                    // Message already decrypted or not encrypted
                }
            } catch (error) {
                // Error decrypting existing message
            }
        }
        
        // Scroll to bottom after decrypting all messages
        this.scrollToBottom();
    }

    // Method to toggle encryption for testing
    toggleEncryption() {
        this.encryptionEnabled = !this.encryptionEnabled;
        
        const statusDiv = document.getElementById('encryption-status');
        if (statusDiv) {
            statusDiv.textContent = this.encryptionEnabled ? 'Encrypted' : 'Plain Text';
            statusDiv.className = this.encryptionEnabled ? 'text-success' : 'text-warning';
        }
    }
}

// Export the class for use in templates
window.SecureMessaging = SecureMessaging;

// Safe initialization function to prevent multiple instances
window.initializeSecureMessaging = function() {
    // Ensure we have an encryption instance before doing anything
    if (window.MessageEncryption && !window.messageEncryption) {
        window.messageEncryption = new window.MessageEncryption();
    }

    if (!window.secureMessaging) {
        window.secureMessaging = new SecureMessaging();
        
        // Decrypt existing messages on page load
        setTimeout(async () => {
            try {
                await window.secureMessaging.decryptExistingMessages();
            } catch (error) {
                // Error decrypting existing messages
            }
        }, 500);
        
        return true;
    } else {
        return false;
    }
};
