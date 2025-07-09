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
        this.messageContainer = document.getElementById('message-container');
        this.conversationList = document.getElementById('conversation-list');
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Check if encryption is available
        this.checkEncryptionSupport();
        
        console.log('SecureMessaging initialized');
    }

    checkEncryptionSupport() {
        if (!window.crypto || !window.crypto.subtle) {
            console.warn('Web Crypto API not supported - falling back to plain text');
            this.encryptionEnabled = false;
            this.showEncryptionWarning();
        } else if (!window.MessageEncryption) {
            console.warn('MessageEncryption class not available - falling back to plain text');
            this.encryptionEnabled = false;
        } else {
            // MessageEncryption class is available
            this.encryptionEnabled = true;
            console.log('Encryption support confirmed');
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
            console.log("⏳ SEND MESSAGE: Already submitting, ignoring duplicate request");
            return;
        }
        
        this.isSubmitting = true;
        console.log("🚀 SEND MESSAGE: Form submitted (locked)");
        
        const form = e.target;
        const messageInput = form.querySelector('textarea[name="content"]') || form.querySelector('input[name="content"]');
        const recipientInput = form.querySelector('input[name="recipient_id"]');
        
        console.log("📋 SEND MESSAGE: Form elements found");
        console.log("  - Form:", form);
        console.log("  - Message input:", messageInput);
        console.log("  - Recipient input:", recipientInput);
        
        if (!messageInput || !recipientInput) {
            console.error('❌ SEND MESSAGE: Required form elements not found');
            console.log('Form:', form);
            console.log('Message input:', messageInput);
            console.log('Recipient input:', recipientInput);
            return;
        }

        const content = messageInput.value.trim();
        const recipientId = parseInt(recipientInput.value);
        
        console.log("📋 SEND MESSAGE: Form values");
        console.log("  - Content:", content);
        console.log("  - Recipient ID:", recipientId);
        
        if (!content || !recipientId) {
            console.warn("⚠️ SEND MESSAGE: Empty content or invalid recipient ID");
            return;
        }

        // Show sending indicator
        const sendButton = form.querySelector('button[type="submit"]');
        const originalText = sendButton ? sendButton.textContent : 'Send';
        
        console.log("📋 SEND MESSAGE: Send button found:", sendButton);
        
        try {
            if (sendButton) {
                sendButton.textContent = 'Sending...';
                sendButton.disabled = true;
            }

            let messageData = {
                recipient_id: recipientId,
                content: content
            };
            
            console.log("📋 SEND MESSAGE: Initial message data:", messageData);

            // Try to encrypt if encryption is enabled
            if (this.encryptionEnabled && window.MessageEncryption) {
                console.log("🔐 SEND MESSAGE: Encryption enabled, attempting to encrypt");
                
                try {
                    // Create encryption instance if needed (should already exist from init)
                    if (!window.messageEncryption) {
                        console.log("🔐 SEND MESSAGE: Creating new MessageEncryption instance");
                        window.messageEncryption = new window.MessageEncryption();
                    } else {
                        console.log("🔐 SEND MESSAGE: Using existing MessageEncryption instance");
                    }
                    
                    // Generate conversation ID from user IDs (deterministic)
                    const currentUserId = window.currentUserId || parseInt(document.getElementById('currentUserId')?.value);
                    const conversationId = `${Math.min(currentUserId, recipientId)}_${Math.max(currentUserId, recipientId)}`;
                    
                    console.log("🔐 SEND MESSAGE: Conversation details");
                    console.log("  - Current user ID:", currentUserId);
                    console.log("  - Recipient ID:", recipientId);
                    console.log("  - Conversation ID:", conversationId);
                    
                    const conversationKey = await window.messageEncryption.getConversationKey(conversationId);
                    console.log("🔐 SEND MESSAGE: Got conversation key");
                    
                    const encryptedData = await window.messageEncryption.encryptMessage(content, conversationKey);
                    console.log("🔐 SEND MESSAGE: Message encrypted successfully");
                    console.log("  - Encrypted data:", encryptedData);
                    
                    messageData = {
                        recipient_id: recipientId,
                        encrypted_data: encryptedData
                    };
                    
                    console.log("🔐 SEND MESSAGE: Updated message data with encryption:", messageData);
                    console.log('Message encrypted successfully');
                } catch (encError) {
                    console.warn('❌ SEND MESSAGE: Encryption failed, falling back to plain text:', encError);
                    // Keep the original messageData with plain content
                }
            } else {
                console.log("📝 SEND MESSAGE: Encryption disabled or not available, using plain text");
            }

            console.log("🌐 SEND MESSAGE: Sending API request");
            console.log("  - URL: /messaging/send");
            console.log("  - Method: POST");
            console.log("  - Headers: Content-Type: application/json, X-CSRFToken:", window.csrf_token);
            console.log("  - Body:", JSON.stringify(messageData, null, 2));

            // Send the message
            const response = await fetch('/messaging/send', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.csrf_token
                },
                body: JSON.stringify(messageData)
            });

            console.log("🌐 SEND MESSAGE: Got response");
            console.log("  - Status:", response.status);
            console.log("  - Status text:", response.statusText);

            const result = await response.json();
            console.log("🌐 SEND MESSAGE: Response data:", result);

            if (result.success) {
                console.log("✅ SEND MESSAGE: Message sent successfully");
                
                // Clear the input
                messageInput.value = '';
                
                // Add message to UI immediately
                this.addMessageToUI(result.message);
                
                // Scroll to bottom
                this.scrollToBottom();
                
                // Refresh conversation list to update last message
                this.refreshConversationList();
            } else {
                console.error("❌ SEND MESSAGE: Server returned error:", result.error);
                alert('Failed to send message: ' + result.error);
            }

        } catch (error) {
            console.error('❌ SEND MESSAGE: Network/parsing error:', error);
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
            
            console.log("🔄 SEND MESSAGE: Send button reset and lock released");
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
            console.error('Error switching conversation:', error);
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
            console.error('Error loading messages:', error);
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
                console.log('🔓 DECRYPT: Attempting to decrypt message');
                console.log('  - Current user ID:', this.currentUserId);
                console.log('  - Other user ID:', otherUserId);
                console.log('  - Conversation ID:', conversationId);
                
                const conversationKey = await window.messageEncryption.getConversationKey(conversationId);
                console.log('🔓 DECRYPT: Got conversation key');
                
                displayContent = await window.messageEncryption.decryptMessage({
                    encrypted_content: message.encrypted_content,
                    nonce: message.nonce,
                    algorithm: message.algorithm
                }, conversationKey);
                
                console.log('🔓 DECRYPT: Successfully decrypted message');
                
            } catch (decError) {
                console.error('🔓 DECRYPT: Decryption failed:', decError);
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
            console.error('Error marking messages as read:', error);
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
            console.error('Error refreshing conversations:', error);
        }
    }

    updateConversationList(conversations) {
        // This would update the conversation list UI
        // Implementation depends on the specific HTML structure
        console.log('Updating conversation list:', conversations);
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
            this.messageContainer.scrollTop = this.messageContainer.scrollHeight;
        }
    }

    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

        if (diffDays === 0) {
            return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        } else if (diffDays === 1) {
            return 'Yesterday';
        } else if (diffDays < 7) {
            return date.toLocaleDateString([], { weekday: 'short' });
        } else {
            return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Method to decrypt existing messages in the DOM on page load
    async decryptExistingMessages() {
        console.log('🔍 Searching for existing encrypted messages to decrypt...');
        
        if (!this.encryptionEnabled || !window.messageEncryption) {
            console.log('❌ Encryption disabled or not available');
            return;
        }

        // Find all message elements that contain encrypted content
        const messageElements = document.querySelectorAll('.message');
        console.log(`📋 Found ${messageElements.length} message elements`);

        for (const messageElement of messageElements) {
            try {
                const messageContent = messageElement.querySelector('.message-content');
                const encryptedIcon = messageElement.querySelector('.fas.fa-lock');
                
                // Check if this is an encrypted message that needs decryption
                if (messageContent && encryptedIcon && 
                    messageContent.textContent.includes('[Encrypted Message - Decrypting...]')) {
                    
                    console.log('🔍 Found encrypted message to decrypt');
                    
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
                        console.log('⚠️ Missing encryption data attributes, skipping...');
                        continue;
                    }
                    
                    // Determine the other user ID
                    const otherUserId = messageData.sender_id === this.currentUserId ? 
                        messageData.recipient_id : messageData.sender_id;
                    
                    // Generate conversation ID in the same format as encryption
                    const conversationId = `${Math.min(this.currentUserId, otherUserId)}_${Math.max(this.currentUserId, otherUserId)}`;
                    
                    console.log('🔓 DECRYPT EXISTING: Attempting to decrypt message');
                    console.log('  - Current user ID:', this.currentUserId);
                    console.log('  - Other user ID:', otherUserId);
                    console.log('  - Conversation ID:', conversationId);
                    
                    // Get the conversation key
                    const conversationKey = await window.messageEncryption.getConversationKey(conversationId);
                    console.log('🔓 DECRYPT EXISTING: Got conversation key');
                    
                    // Decrypt the message
                    const decryptedContent = await window.messageEncryption.decryptMessage({
                        encrypted_content: messageData.encrypted_content,
                        nonce: messageData.nonce,
                        algorithm: messageData.algorithm
                    }, conversationKey);
                    
                    console.log('🔓 DECRYPT EXISTING: Successfully decrypted message');
                    
                    // Update the message content in the DOM
                    messageContent.textContent = decryptedContent;
                    
                } else {
                    console.log('ℹ️ Message already decrypted or not encrypted');
                }
            } catch (error) {
                console.error('❌ Error decrypting existing message:', error);
            }
        }
        
        console.log('✅ Finished decrypting existing messages');
    }

    // Method to toggle encryption for testing
    toggleEncryption() {
        this.encryptionEnabled = !this.encryptionEnabled;
        console.log('Encryption', this.encryptionEnabled ? 'enabled' : 'disabled');
        
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
        console.log('🔐 INIT: Creating MessageEncryption instance');
        window.messageEncryption = new window.MessageEncryption();
    }

    if (!window.secureMessaging) {
        console.log('🔧 Initializing SecureMessaging...');
        window.secureMessaging = new SecureMessaging();
        console.log('✅ SecureMessaging initialized successfully');
        
        // Decrypt existing messages on page load
        setTimeout(async () => {
            try {
                await window.secureMessaging.decryptExistingMessages();
            } catch (error) {
                console.error('❌ Error decrypting existing messages:', error);
            }
        }, 500);
        
        return true;
    } else {
        console.log('✅ SecureMessaging already initialized');
        return false;
    }
};
