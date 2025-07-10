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
		this.isSubmitting = false;
		this.init();
	}

	init() {
		this.currentUserId = window.currentUserId || null;
		this.messageContainer = document.getElementById('chatMessages');
		this.conversationList = document.getElementById('conversationsList');
		this.setupEventListeners();
		this.checkEncryptionSupport();
	}

	checkEncryptionSupport() {
		if (!window.crypto || !window.crypto.subtle || !window.MessageEncryption) {
			this.encryptionEnabled = false;
			this.showEncryptionWarning();
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
		if (container) container.insertBefore(warningDiv, container.firstChild);
	}

	setupEventListeners() {
		if (this.conversationList) {
			this.conversationList.addEventListener('click', (e) => {
				const item = e.target.closest('.conversation-item');
				if (item) {
					const userId = item.dataset.userId;
					if (userId) this.switchConversation(parseInt(userId));
				}
			});
		}
		this.startMessageRefresh();
	}

	async handleSendMessage(e) {
		e.preventDefault();
		if (this.isSubmitting) return;
		this.isSubmitting = true;

		const form = e.target;
		const messageInput = form.querySelector('textarea[name="content"]') || form.querySelector('input[name="content"]');
		const recipientInput = form.querySelector('input[name="recipient_id"]');
		if (!messageInput || !recipientInput) return;

		const content = messageInput.value.trim();
		const recipientId = parseInt(recipientInput.value);
		if (!content || !recipientId) return;

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

			if (this.encryptionEnabled && window.MessageEncryption) {
				if (!window.messageEncryption) {
					window.messageEncryption = new window.MessageEncryption();
				}
				const currentUserId = window.currentUserId || parseInt(document.getElementById('currentUserId')?.value);
				const conversationId = `${Math.min(currentUserId, recipientId)}_${Math.max(currentUserId, recipientId)}`;
				const key = await window.messageEncryption.getConversationKey(conversationId);
				const encryptedData = await window.messageEncryption.encryptMessage(content, key);

				messageData = {
					recipient_id: recipientId,
					encrypted_data: encryptedData
				};
			}

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
				messageInput.value = '';
				this.addMessageToUI(result.message);
				this.scrollToBottom();
				this.refreshConversationList();
			} else {
				alert('Failed to send message: ' + result.error);
			}
		} catch (err) {
			alert('Failed to send message. Please try again.');
		} finally {
			this.isSubmitting = false;
			if (sendButton) {
				sendButton.textContent = originalText;
				sendButton.disabled = false;
			}
		}
	}

	async switchConversation(userId) {
		this.currentConversationId = userId;
		try {
			await this.loadMessages(userId);
			this.updateActiveConversation(userId);
			this.markMessagesAsRead(userId);
		} catch (err) {}
	}

	async loadMessages(userId) {
		try {
			const response = await fetch(`/messaging/api/messages/${userId}`);
			const data = await response.json();
			if (data.messages && this.messageContainer) {
				this.messageContainer.innerHTML = '';
				for (const message of data.messages) {
					await this.addMessageToUI(message);
				}
				this.scrollToBottom();
			}
		} catch (err) {}
	}

	async addMessageToUI(message) {
		if (!this.messageContainer) return;
		let content = message.content;

		if (message.is_encrypted && this.encryptionEnabled && window.messageEncryption) {
			try {
				const otherId = message.sender_id === this.currentUserId ? message.recipient_id : message.sender_id;
				const convId = `${Math.min(this.currentUserId, otherId)}_${Math.max(this.currentUserId, otherId)}`;
				const key = await window.messageEncryption.getConversationKey(convId);
				content = await window.messageEncryption.decryptMessage({
					encrypted_content: message.encrypted_content,
					nonce: message.nonce,
					algorithm: message.algorithm
				}, key);
			} catch (err) {
				content = '[Failed to decrypt message]';
			}
		}

		const div = document.createElement('div');
		div.className = `message ${message.sender_id === this.currentUserId ? 'sent' : 'received'}`;
		const lock = message.is_encrypted ?
			'<i class="fas fa-lock text-success" title="Encrypted"></i>' :
			'<i class="fas fa-unlock text-muted" title="Not encrypted"></i>';

		div.innerHTML = `
			<div class="message-content">
				<div class="message-text">${this.escapeHtml(content)}</div>
				<div class="message-meta">
					<span class="message-time">${this.formatTimestamp(message.timestamp)}</span>
					${lock}
				</div>
			</div>
		`;
		this.messageContainer.appendChild(div);
		this.scrollToBottom();
	}

	updateActiveConversation(userId) {
		document.querySelectorAll('.conversation-item').forEach(item => item.classList.remove('active'));
		const active = document.querySelector(`.conversation-item[data-user-id="${userId}"]`);
		if (active) active.classList.add('active');
	}

	async markMessagesAsRead(userId) {
		try {
			await fetch(`/messaging/mark-read/${userId}`, {
				method: 'POST',
				headers: { 'X-CSRFToken': window.csrf_token }
			});
		} catch (err) {}
	}

	async refreshConversationList() {
		try {
			const response = await fetch('/messaging/api/conversations');
			const data = await response.json();
			if (data.conversations && this.conversationList) {
				this.updateConversationList(data.conversations);
			}
		} catch (err) {}
	}

	updateConversationList(conversations) {
		// Placeholder: dynamically update conversation list
	}

	startMessageRefresh() {
		setInterval(() => {
			if (this.currentConversationId) {
				this.loadMessages(this.currentConversationId);
			}
		}, 5000);

		setInterval(() => {
			this.refreshConversationList();
		}, 10000);
	}

	scrollToBottom() {
		if (this.messageContainer) {
			requestAnimationFrame(() => {
				this.messageContainer.scrollTop = this.messageContainer.scrollHeight;
			});
		}
	}

	formatTimestamp(ts) {
		const d = new Date(ts);
		const now = new Date();
		const days = Math.floor((now - d) / (1000 * 60 * 60 * 24));
		if (days === 0) return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
		if (days === 1) return 'Yesterday ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
		if (days < 7) return d.toLocaleDateString([], { weekday: 'short' }) + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
		return d.toLocaleDateString([], { month: '2-digit', day: '2-digit' }) + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
	}

	escapeHtml(text) {
		const div = document.createElement('div');
		div.textContent = text;
		return div.innerHTML;
	}

	async decryptExistingMessages() {
		if (!this.encryptionEnabled || !window.messageEncryption) return;

		const elements = document.querySelectorAll('.message');
		for (const el of elements) {
			try {
				const content = el.querySelector('.message-content');
				const lock = el.querySelector('.fas.fa-lock');
				if (content && lock && content.textContent.includes('[Encrypted Message - Decrypting...]')) {
					const data = {
						encrypted_content: el.dataset.encryptedContent,
						nonce: el.dataset.nonce,
						algorithm: el.dataset.algorithm,
						sender_id: parseInt(el.dataset.senderId),
						recipient_id: parseInt(el.dataset.recipientId),
						is_encrypted: true
					};
					const other = data.sender_id === this.currentUserId ? data.recipient_id : data.sender_id;
					const convId = `${Math.min(this.currentUserId, other)}_${Math.max(this.currentUserId, other)}`;
					const key = await window.messageEncryption.getConversationKey(convId);
					const decrypted = await window.messageEncryption.decryptMessage({
						encrypted_content: data.encrypted_content,
						nonce: data.nonce,
						algorithm: data.algorithm
					}, key);
					content.textContent = decrypted;
				}
			} catch (err) {}
		}
		this.scrollToBottom();
	}

	toggleEncryption() {
		this.encryptionEnabled = !this.encryptionEnabled;
		const status = document.getElementById('encryption-status');
		if (status) {
			status.textContent = this.encryptionEnabled ? 'Encrypted' : 'Plain Text';
			status.className = this.encryptionEnabled ? 'text-success' : 'text-warning';
		}
	}
}

// Export and initialize
window.SecureMessaging = SecureMessaging;

window.initializeSecureMessaging = function () {
	if (window.MessageEncryption && !window.messageEncryption) {
		window.messageEncryption = new window.MessageEncryption();
	}
	if (!window.secureMessaging) {
		window.secureMessaging = new SecureMessaging();
		setTimeout(async () => {
			try {
				await window.secureMessaging.decryptExistingMessages();
			} catch (err) {}
		}, 500);
		return true;
	}
	return false;
};

// ✅ Global fallback-aware function used by <form onsubmit="sendMessage(event)">
window.sendMessage = function (event) {
	event.preventDefault();
	const isProduction = window.location.hostname !== 'localhost' && !window.location.hostname.includes('127.0.0.1');

	if (window.secureMessaging && typeof window.secureMessaging.handleSendMessage === 'function') {
		window.secureMessaging.handleSendMessage(event);
	} else if (isProduction) {
		alert("🔒 Encrypted messaging is required in production. Please refresh or contact support.");
		console.error("❌ SecureMessaging not available in production — message blocked.");
	} else {
		console.warn("⚠️ SecureMessaging unavailable — plaintext fallback only allowed in development.");
		if (typeof sendMessageFallback === 'function') {
			sendMessageFallback(event);
		} else {
			alert("Plaintext fallback not available.");
		}
	}
};
