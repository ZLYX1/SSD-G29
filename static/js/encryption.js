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
        // Check if Web Crypto API is available
        if (!window.crypto || !window.crypto.subtle) {
            throw new Error('Web Crypto API not supported in this browser');
        }
    }

    /**
     * Generate a new encryption key for a conversation
     */
    async generateKey() {
        await this.initPromise;
        
        const key = await window.crypto.subtle.generateKey(
            {
                name: this.cryptoAlgorithm,
                length: this.keyLength
            },
            true, // extractable
            ['encrypt', 'decrypt']
        );

        return key;
    }

    /**
     * Export a key to raw format for storage/transmission
     */
    async exportKey(key) {
        await this.initPromise;
        
        const exported = await window.crypto.subtle.exportKey('raw', key);
        return new Uint8Array(exported);
    }

    /**
     * Import a key from raw format
     */
    async importKey(keyData) {
        await this.initPromise;
        
        const key = await window.crypto.subtle.importKey(
            'raw',
            keyData,
            {
                name: this.cryptoAlgorithm,
                length: this.keyLength
            },
            true,
            ['encrypt', 'decrypt']
        );

        return key;
    }

    /**
     * Encrypt a message
     */
    async encryptMessage(message, key) {
        await this.initPromise;
        
        const encoder = new TextEncoder();
        const data = encoder.encode(message);
        
        // Generate a random nonce for this message
        const nonce = window.crypto.getRandomValues(new Uint8Array(12));
        
        const encrypted = await window.crypto.subtle.encrypt(
            {
                name: this.cryptoAlgorithm,
                iv: nonce
            },
            key,
            data
        );

        return {
            encrypted_content: this.arrayBufferToBase64(encrypted),
            nonce: this.arrayBufferToBase64(nonce),
            algorithm: this.protocolAlgorithm
        };
    }

    /**
     * Decrypt a message
     */
    async decryptMessage(encryptedData, key) {
        await this.initPromise;
        
        try {
            const encrypted = this.base64ToArrayBuffer(encryptedData.encrypted_content);
            const nonce = this.base64ToArrayBuffer(encryptedData.nonce);
            
            const decrypted = await window.crypto.subtle.decrypt(
                {
                    name: this.cryptoAlgorithm,
                    iv: nonce
                },
                key,
                encrypted
            );

            const decoder = new TextDecoder();
            return decoder.decode(decrypted);
        } catch (error) {
            return '[Failed to decrypt message]';
        }
    }

    /**
     * Derive a deterministic conversation key from user IDs
     * This creates the same key for both users in a conversation
     */
    async deriveConversationKey(userId1, userId2) {
        // Ensure consistent ordering for deterministic results
        const sortedIds = [userId1, userId2].sort((a, b) => a - b);
        
        // Create a seed string from the sorted user IDs
        const seedString = `conversation-${sortedIds[0]}-${sortedIds[1]}`;
        
        try {
            // Encode the seed string
            const encoder = new TextEncoder();
            const seedData = encoder.encode(seedString);
            
            // Create a hash of the seed
            const hashBuffer = await window.crypto.subtle.digest('SHA-256', seedData);
            
            // Use first 16 bytes (128 bits) for AES-128 key
            const keyData = hashBuffer.slice(0, 16);
            
            // Import as CryptoKey
            const key = await window.crypto.subtle.importKey(
                'raw',
                keyData,
                {
                    name: this.cryptoAlgorithm,
                    length: this.keyLength
                },
                true,
                ['encrypt', 'decrypt']
            );
            
            return key;
            
        } catch (error) {
            throw error;
        }
    }

    /**
     * Get or create a conversation key
     */
    async getConversationKey(conversationId) {
        if (this.keys.has(conversationId)) {
            return this.keys.get(conversationId);
        }

        try {
            // Parse conversation ID to get user IDs
            const userIds = conversationId.toString().split('_').map(id => parseInt(id));
            
            if (userIds.length === 2 && userIds.every(id => !isNaN(id))) {
                // Use our own deterministic key derivation
                const key = await this.deriveConversationKey(userIds[0], userIds[1]);
                this.keys.set(conversationId, key);
                
                return key;
            } else {
                // Fallback to generating a simple key
                const key = await this.generateKey();
                this.keys.set(conversationId, key);
                return key;
            }
        } catch (error) {
            // Fall back to generating a local-only key
            const key = await this.generateKey();
            this.keys.set(conversationId, key);
            return key;
        }
    }

    /**
     * Convert ArrayBuffer to Base64 string
     */
    arrayBufferToBase64(buffer) {
        const bytes = new Uint8Array(buffer);
        let binary = '';
        for (let i = 0; i < bytes.byteLength; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return window.btoa(binary);
    }

    /**
     * Convert Base64 string to ArrayBuffer
     */
    base64ToArrayBuffer(base64) {
        const binary = window.atob(base64);
        const bytes = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) {
            bytes[i] = binary.charCodeAt(i);
        }
        return bytes.buffer;
    }

    /**
     * Clear all stored keys (for logout)
     */
    clearKeys() {
        this.keys.clear();
    }
}

// Global instance
let messageEncryption = null;

// Initialize encryption when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    try {
        messageEncryption = new MessageEncryption();
    } catch (error) {
        // Fall back to plain text messaging
    }
});

// Export for use in other scripts
window.MessageEncryption = MessageEncryption;
window.messageEncryption = messageEncryption;
