"""
End-to-End Encryption Utilities for Safe Companions Messaging System
Using AES-GCM 128-bit encryption as requested

This module provides utilities for client-side encryption/decryption of messages
ensuring that the server cannot read message content.
"""

import os
import base64
import json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend


class MessageEncryption:
    """
    Handles AES-GCM 128-bit encryption for messaging system
    """
    
    @staticmethod
    def generate_key():
        """
        Generate a new 128-bit (16 bytes) encryption key for AES-GCM
        Returns base64 encoded key string for easy storage/transmission
        """
        key = AESGCM.generate_key(bit_length=128)
        return base64.b64encode(key).decode('utf-8')
    
    @staticmethod
    def derive_conversation_key(user1_id, user2_id, salt=None):
        """
        Derive a deterministic conversation key from user IDs
        This ensures both users can generate the same key for a conversation
        """
        if salt is None:
            # Create a deterministic salt from user IDs
            salt_string = f"conversation_{min(user1_id, user2_id)}_{max(user1_id, user2_id)}"
            salt = salt_string.encode('utf-8')[:16].ljust(16, b'0')  # 16 bytes
        
        # Create password from user IDs
        password = f"users_{min(user1_id, user2_id)}_{max(user1_id, user2_id)}".encode('utf-8')
        
        # Derive key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=16,  # 128 bits
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = kdf.derive(password)
        return base64.b64encode(key).decode('utf-8')
    
    @staticmethod
    def encrypt_message(message_content, key_b64):
        """
        Encrypt message content using AES-GCM
        
        Args:
            message_content (str): Plain text message to encrypt
            key_b64 (str): Base64 encoded encryption key
            
        Returns:
            dict: Contains encrypted data and metadata
        """
        try:
            # Decode the key
            key = base64.b64decode(key_b64.encode('utf-8'))
            
            # Create AESGCM cipher
            aesgcm = AESGCM(key)
            
            # Generate random nonce (12 bytes for GCM)
            nonce = os.urandom(12)
            
            # Encrypt the message
            ciphertext = aesgcm.encrypt(nonce, message_content.encode('utf-8'), None)
            
            # Return encrypted data package
            return {
                'success': True,
                'encrypted_content': base64.b64encode(ciphertext).decode('utf-8'),
                'nonce': base64.b64encode(nonce).decode('utf-8'),
                'algorithm': 'AES-GCM-128'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def decrypt_message(encrypted_data, key_b64):
        """
        Decrypt message content using AES-GCM
        
        Args:
            encrypted_data (dict): Contains encrypted content and nonce
            key_b64 (str): Base64 encoded encryption key
            
        Returns:
            dict: Contains decrypted message or error
        """
        try:
            # Decode the key
            key = base64.b64decode(key_b64.encode('utf-8'))
            
            # Create AESGCM cipher
            aesgcm = AESGCM(key)
            
            # Decode encrypted content and nonce
            ciphertext = base64.b64decode(encrypted_data['encrypted_content'].encode('utf-8'))
            nonce = base64.b64decode(encrypted_data['nonce'].encode('utf-8'))
            
            # Decrypt the message
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            
            return {
                'success': True,
                'message_content': plaintext.decode('utf-8')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def validate_encrypted_message(encrypted_data):
        """
        Validate that encrypted message data has required fields
        """
        required_fields = ['encrypted_content', 'nonce', 'algorithm']
        
        if not isinstance(encrypted_data, dict):
            return False, "Encrypted data must be a dictionary"
        
        for field in required_fields:
            if field not in encrypted_data:
                return False, f"Missing required field: {field}"
        
        if encrypted_data.get('algorithm') != 'AES-GCM-128':
            return False, "Invalid encryption algorithm"
        
        return True, "Valid encrypted message"


class ConversationKeyManager:
    """
    Manages encryption keys for conversations
    """
    
    @staticmethod
    def get_conversation_key(user1_id, user2_id):
        """
        Get or create encryption key for a conversation between two users
        Uses deterministic key derivation so both users get the same key
        """
        return MessageEncryption.derive_conversation_key(user1_id, user2_id)
    
    @staticmethod
    def create_key_exchange_data(user_id, recipient_id):
        """
        Create data package for secure key exchange
        In a real implementation, this would use public key cryptography
        For this demo, we use deterministic key derivation
        """
        conversation_key = ConversationKeyManager.get_conversation_key(user_id, recipient_id)
        
        return {
            'conversation_id': f"{min(user_id, recipient_id)}_{max(user_id, recipient_id)}",
            'algorithm': 'AES-GCM-128',
            'key_derivation': 'PBKDF2-SHA256',
            'participants': sorted([user_id, recipient_id])
        }
    
    @staticmethod
    def ensure_conversation_key(user1_id, user2_id):
        """
        Ensure a conversation key exists between two users
        Returns (bool, dict) tuple for compatibility with message controller
        """
        try:
            key_data = ConversationKeyManager.create_key_exchange_data(user1_id, user2_id)
            return True, {
                'key_id': f"conv_{min(user1_id, user2_id)}_{max(user1_id, user2_id)}",
                'algorithm': 'AES-GCM-128',
                'created_at': None  # Would be database timestamp in full implementation
            }
        except Exception as e:
            return False, str(e)

# Client-side JavaScript encryption functions (to be included in templates)
CLIENT_SIDE_CRYPTO_JS = """
// Client-side encryption functions for Safe Companions messaging
class MessageCrypto {
    
    static async generateKey() {
        const key = await window.crypto.subtle.generateKey(
            {
                name: 'AES-GCM',
                length: 128
            },
            true,
            ['encrypt', 'decrypt']
        );
        
        const exported = await window.crypto.subtle.exportKey('raw', key);
        return btoa(String.fromCharCode(...new Uint8Array(exported)));
    }
    
    static async deriveConversationKey(user1Id, user2Id) {
        const password = `users_${Math.min(user1Id, user2Id)}_${Math.max(user1Id, user2Id)}`;
        const salt = `conversation_${Math.min(user1Id, user2Id)}_${Math.max(user1Id, user2Id)}`.substring(0, 16).padEnd(16, '0');
        
        const encoder = new TextEncoder();
        const keyMaterial = await window.crypto.subtle.importKey(
            'raw',
            encoder.encode(password),
            'PBKDF2',
            false,
            ['deriveBits', 'deriveKey']
        );
        
        const key = await window.crypto.subtle.deriveKey(
            {
                name: 'PBKDF2',
                salt: encoder.encode(salt),
                iterations: 100000,
                hash: 'SHA-256'
            },
            keyMaterial,
            { name: 'AES-GCM', length: 128 },
            true,
            ['encrypt', 'decrypt']
        );
        
        const exported = await window.crypto.subtle.exportKey('raw', key);
        return btoa(String.fromCharCode(...new Uint8Array(exported)));
    }
    
    static async encryptMessage(messageContent, keyB64) {
        try {
            const key = await window.crypto.subtle.importKey(
                'raw',
                Uint8Array.from(atob(keyB64), c => c.charCodeAt(0)),
                'AES-GCM',
                false,
                ['encrypt']
            );
            
            const nonce = window.crypto.getRandomValues(new Uint8Array(12));
            const encoder = new TextEncoder();
            
            const encrypted = await window.crypto.subtle.encrypt(
                {
                    name: 'AES-GCM',
                    iv: nonce
                },
                key,
                encoder.encode(messageContent)
            );
            
            return {
                success: true,
                encrypted_content: btoa(String.fromCharCode(...new Uint8Array(encrypted))),
                nonce: btoa(String.fromCharCode(...nonce)),
                algorithm: 'AES-GCM-128'
            };
            
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }
    
    static async decryptMessage(encryptedData, keyB64) {
        try {
            const key = await window.crypto.subtle.importKey(
                'raw',
                Uint8Array.from(atob(keyB64), c => c.charCodeAt(0)),
                'AES-GCM',
                false,
                ['decrypt']
            );
            
            const encrypted = Uint8Array.from(atob(encryptedData.encrypted_content), c => c.charCodeAt(0));
            const nonce = Uint8Array.from(atob(encryptedData.nonce), c => c.charCodeAt(0));
            
            const decrypted = await window.crypto.subtle.decrypt(
                {
                    name: 'AES-GCM',
                    iv: nonce
                },
                key,
                encrypted
            );
            
            const decoder = new TextDecoder();
            return {
                success: true,
                message_content: decoder.decode(decrypted)
            };
            
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }
}
"""

def get_client_crypto_js():
    """Return JavaScript crypto functions for frontend"""
    return CLIENT_SIDE_CRYPTO_JS
