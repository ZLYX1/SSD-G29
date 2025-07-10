/**
 * End-to-End Encryption for Safe Companions Messaging
 * Uses AES-GCM 128-bit encryption for client-side message encryption
 */

class MessageEncryption {
	constructor() {
		this.cryptoAlgorithm = 'AES-GCM';        // For Web Crypto API
		this.protocolAlgorithm = 'AES-GCM-128';  // For backend protocol
		this.keyLength = 128;
		this.keys = new Map(); // Store conversation keys
		this.initPromise = this.init();
	}

	async init() {
		if (!window.crypto || !window.crypto.subtle) {
			throw new Error('Web Crypto API not supported in this browser');
		}
	}

	async generateKey() {
		await this.initPromise;
		return await window.crypto.subtle.generateKey(
			{ name: this.cryptoAlgorithm, length: this.keyLength },
			true,
			['encrypt', 'decrypt']
		);
	}

	async exportKey(key) {
		await this.initPromise;
		const exported = await window.crypto.subtle.exportKey('raw', key);
		return new Uint8Array(exported);
	}

	async importKey(keyData) {
		await this.initPromise;
		return await window.crypto.subtle.importKey(
			'raw',
			keyData,
			{ name: this.cryptoAlgorithm, length: this.keyLength },
			true,
			['encrypt', 'decrypt']
		);
	}

	async encryptMessage(message, key) {
		await this.initPromise;

		const encoder = new TextEncoder();
		const data = encoder.encode(message);
		const nonce = window.crypto.getRandomValues(new Uint8Array(12));

		const encrypted = await window.crypto.subtle.encrypt(
			{ name: this.cryptoAlgorithm, iv: nonce },
			key,
			data
		);

		return {
			encrypted_content: this.arrayBufferToBase64(encrypted),
			nonce: this.arrayBufferToBase64(nonce),
			algorithm: this.protocolAlgorithm
		};
	}

	async decryptMessage(encryptedData, key) {
		await this.initPromise;

		try {
			const encrypted = this.base64ToArrayBuffer(encryptedData.encrypted_content);
			const nonce = this.base64ToArrayBuffer(encryptedData.nonce);

			const decrypted = await window.crypto.subtle.decrypt(
				{ name: this.cryptoAlgorithm, iv: nonce },
				key,
				encrypted
			);

			const decoder = new TextDecoder();
			return decoder.decode(decrypted);
		} catch (error) {
			return '[Failed to decrypt message]';
		}
	}

	async deriveConversationKey(userId1, userId2) {
		const sortedIds = [userId1, userId2].sort((a, b) => a - b);
		const seedString = `conversation-${sortedIds[0]}-${sortedIds[1]}`;
		const encoder = new TextEncoder();
		const seedData = encoder.encode(seedString);
		const hashBuffer = await window.crypto.subtle.digest('SHA-256', seedData);
		const keyData = hashBuffer.slice(0, 16); // 128 bits

		return await window.crypto.subtle.importKey(
			'raw',
			keyData,
			{ name: this.cryptoAlgorithm, length: this.keyLength },
			true,
			['encrypt', 'decrypt']
		);
	}

	async getConversationKey(conversationId) {
		if (this.keys.has(conversationId)) {
			return this.keys.get(conversationId);
		}

		try {
			const userIds = conversationId.toString().split('_').map(id => parseInt(id));
			if (userIds.length === 2 && userIds.every(id => !isNaN(id))) {
				const key = await this.deriveConversationKey(userIds[0], userIds[1]);
				this.keys.set(conversationId, key);
				return key;
			}
		} catch (error) {
			// fallback below
		}

		const key = await this.generateKey();
		this.keys.set(conversationId, key);
		return key;
	}

	arrayBufferToBase64(buffer) {
		const bytes = new Uint8Array(buffer);
		let binary = '';
		for (let i = 0; i < bytes.byteLength; i++) {
			binary += String.fromCharCode(bytes[i]);
		}
		return window.btoa(binary);
	}

	base64ToArrayBuffer(base64) {
		const binary = window.atob(base64);
		const bytes = new Uint8Array(binary.length);
		for (let i = 0; i < binary.length; i++) {
			bytes[i] = binary.charCodeAt(i);
		}
		return bytes.buffer;
	}

	clearKeys() {
		this.keys.clear();
	}
}

// ===========================================
// SecureMessaging wrapper for encrypted send
// ===========================================
class SecureMessaging {
	constructor() {
		this.encryption = new MessageEncryption();
	}

	async handleSendMessage(event) {
		event.preventDefault();

		const messageInput = document.getElementById("messageText");
		const content = messageInput.value.trim();
		if (!content) return;

		const currentUserId = parseInt(document.getElementById("currentUserId").value);
		const recipientId = parseInt(document.getElementById("currentConversationId").value);
		const conversationId = [currentUserId, recipientId].sort((a, b) => a - b).join("_");

		try {
			const key = await this.encryption.getConversationKey(conversationId);
			const encryptedPayload = await this.encryption.encryptMessage(content, key);

			const response = await fetch("/messaging/send", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					"X-CSRFToken": window.csrf_token,
				},
				body: JSON.stringify({
					recipient_id: recipientId,
					encrypted_data: encryptedPayload,
				}),
			});

			const result = await response.json();
			if (result.success) {
				messageInput.value = "";
				addMessageToChat(result.message);
				scrollToBottom();
			} else {
				alert("❌ Failed to send message: " + result.error);
			}
		} catch (err) {
			alert("Encryption failed: " + err.message);
		}
	}
}

// ===========================================
// DOM-Ready Initialization
// ===========================================
let messageEncryption = null;

document.addEventListener('DOMContentLoaded', function () {
	try {
		messageEncryption = new MessageEncryption();

		// Wait briefly, then assign secureMessaging wrapper
		setTimeout(() => {
			if (messageEncryption) {
				window.secureMessaging = new SecureMessaging();
				console.log("✅ SecureMessaging initialized");
			}
		}, 200);
	} catch (error) {
		console.warn("⚠️ Failed to initialize encryption", error);
	}
});

// Export classes for use elsewhere
window.MessageEncryption = MessageEncryption;
window.messageEncryption = messageEncryption;
window.SecureMessaging = SecureMessaging;
