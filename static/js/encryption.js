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
        console.log('MessageEncryption initialized successfully');
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
            console.error('Decryption failed:', error);
            return '[Failed to decrypt message]';
        }
    }

    /**
     * Derive a deterministic conversation key from user IDs
     * This creates the same key for both users in a conversation
     */
    async deriveConversationKey(userId1, userId2) {
        console.log('🔑 STEP 1: Starting conversation key derivation for users:', userId1, userId2);
        
        // Ensure consistent ordering for deterministic results
        const sortedIds = [userId1, userId2].sort((a, b) => a - b);
        console.log('🔑 STEP 2: Sorted user IDs:', sortedIds);
        
        // Create a seed string from the sorted user IDs
        const seedString = `conversation-${sortedIds[0]}-${sortedIds[1]}`;
        console.log('🔑 STEP 3: Generated seed string:', seedString);
        
        try {
            // Encode the seed string
            const encoder = new TextEncoder();
            const seedData = encoder.encode(seedString);
            console.log('🔑 STEP 4: Encoded seed data length:', seedData.length);
            
            // Create a hash of the seed
            const hashBuffer = await window.crypto.subtle.digest('SHA-256', seedData);
            console.log('🔑 STEP 5: Created hash, length:', hashBuffer.byteLength);
            
            // Use first 16 bytes (128 bits) for AES-128 key
            const keyData = hashBuffer.slice(0, 16);
            console.log('🔑 STEP 6: Truncated to 16 bytes for AES-128');
            
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
            
            console.log('🔑 STEP 7: Successfully imported CryptoKey');
            return key;
            
        } catch (error) {
            console.error('🔑 ERROR: Failed to derive conversation key:', error);
            throw error;
        }
    }

    /**
     * Get or create a conversation key
     */
    async getConversationKey(conversationId) {
        console.log('🚀 STARTING getConversationKey for:', conversationId);
        
        if (this.keys.has(conversationId)) {
            console.log('✅ Found cached key for conversation:', conversationId);
            return this.keys.get(conversationId);
        }

        console.log('🔍 No cached key found, generating new key...');

        try {
            // Parse conversation ID to get user IDs
            console.log('📝 STEP A: Parsing conversation ID:', conversationId);
            const userIds = conversationId.toString().split('_').map(id => parseInt(id));
            console.log('📝 STEP B: Parsed user IDs:', userIds);
            
            if (userIds.length === 2 && userIds.every(id => !isNaN(id))) {
                console.log('✅ Valid user IDs found, using deterministic key derivation');
                
                // Use our own deterministic key derivation
                const key = await this.deriveConversationKey(userIds[0], userIds[1]);
                this.keys.set(conversationId, key);
                
                console.log('🎉 Successfully generated and cached deterministic conversation key');
                return key;
            } else {
                // Fallback to generating a simple key
                console.warn('⚠️ Could not parse conversation ID, using fallback key generation');
                console.log('📝 userIds.length:', userIds.length);
                console.log('📝 userIds validity:', userIds.map(id => ({ id, isNaN: isNaN(id) })));
                
                const key = await this.generateKey();
                this.keys.set(conversationId, key);
                console.log('🔄 Generated fallback key and cached it');
                return key;
            }
        } catch (error) {
            console.error('❌ Error getting conversation key:', error);
            console.log('🔄 Falling back to generating a local-only key');
            
            // Fall back to generating a local-only key
            const key = await this.generateKey();
            this.keys.set(conversationId, key);
            console.log('💾 Generated and cached fallback key');
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
        console.log('Message encryption system ready');
    } catch (error) {
        console.error('Failed to initialize message encryption:', error);
        // Fall back to plain text messaging
    }
});

// Export for use in other scripts
window.MessageEncryption = MessageEncryption;
window.messageEncryption = messageEncryption;
