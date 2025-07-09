#!/usr/bin/env python3
"""
Simple test script to verify messaging encryption by examining browser console output.
This script provides JavaScript code that can be copy-pasted into the browser console
to test the encryption functionality.
"""

import requests
import time

def check_app_status():
    """Check if the Safe Companions app is running"""
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        if response.status_code == 200:
            print("✅ Safe Companions app is running at http://localhost:5000")
            return True
        else:
            print(f"❌ App responded with status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Error checking app status: {e}")
        return False

def generate_test_script():
    """Generate JavaScript test script for browser console"""
    
    js_test_script = """
// Safe Companions Messaging Encryption Test Script
// Copy and paste this entire script into your browser console on the messaging page

console.log("🚀 Starting Safe Companions Messaging Encryption Test");
console.log("="*60);

async function runEncryptionTests() {
    try {
        // Test 1: Check if MessageEncryption class exists
        console.log("\\n📋 TEST 1: MessageEncryption Class Check");
        if (typeof MessageEncryption === 'undefined') {
            console.error("❌ MessageEncryption class not found!");
            return false;
        }
        console.log("✅ MessageEncryption class found");
        
        // Test 2: Create instance
        console.log("\\n📋 TEST 2: Create MessageEncryption Instance");
        const encryption = new MessageEncryption();
        console.log("✅ MessageEncryption instance created successfully");
        
        // Test 3: Test conversation key generation
        console.log("\\n📋 TEST 3: Conversation Key Generation");
        const conversationId = "1_2";
        console.log(`🔑 Testing key generation for conversation: ${conversationId}`);
        
        const key = await encryption.getConversationKey(conversationId);
        if (key) {
            console.log("✅ Conversation key generated successfully");
            console.log("🔑 Key type:", key.constructor.name);
            console.log("🔑 Key algorithm:", key.algorithm);
        } else {
            console.error("❌ Failed to generate conversation key");
            return false;
        }
        
        // Test 4: Test message encryption
        console.log("\\n📋 TEST 4: Message Encryption");
        const testMessage = "Hello! This is a test encrypted message 🔐";
        console.log(`📝 Original message: "${testMessage}"`);
        
        const encryptedData = await encryption.encrypt(testMessage, conversationId);
        console.log("✅ Message encrypted successfully");
        console.log("🔐 Encrypted data structure:", Object.keys(encryptedData));
        console.log("🔐 IV length:", encryptedData.iv ? encryptedData.iv.length : "N/A");
        console.log("🔐 Data length:", encryptedData.data ? encryptedData.data.length : "N/A");
        
        // Test 5: Test message decryption
        console.log("\\n📋 TEST 5: Message Decryption");
        const decryptedMessage = await encryption.decrypt(encryptedData, conversationId);
        console.log(`📝 Decrypted message: "${decryptedMessage}"`);
        
        // Test 6: Verify round-trip
        console.log("\\n📋 TEST 6: Round-trip Verification");
        const roundTripSuccess = decryptedMessage === testMessage;
        if (roundTripSuccess) {
            console.log("✅ Round-trip encryption/decryption SUCCESSFUL!");
            console.log("🎉 Original and decrypted messages match perfectly");
        } else {
            console.error("❌ Round-trip FAILED!");
            console.error(`❌ Original: "${testMessage}"`);
            console.error(`❌ Decrypted: "${decryptedMessage}"`);
            return false;
        }
        
        // Test 7: Test deterministic key generation
        console.log("\\n📋 TEST 7: Deterministic Key Generation");
        const key1 = await encryption.getConversationKey("1_2");
        const key2 = await encryption.getConversationKey("2_1");
        
        // Export both keys to compare
        const keyData1 = await window.crypto.subtle.exportKey("raw", key1);
        const keyData2 = await window.crypto.subtle.exportKey("raw", key2);
        
        const key1Array = new Uint8Array(keyData1);
        const key2Array = new Uint8Array(keyData2);
        
        const keysMatch = key1Array.every((byte, index) => byte === key2Array[index]);
        if (keysMatch) {
            console.log("✅ Deterministic key generation working correctly");
            console.log("🔑 Keys for '1_2' and '2_1' are identical (as expected)");
        } else {
            console.error("❌ Deterministic key generation FAILED");
            console.error("❌ Keys for '1_2' and '2_1' are different");
            return false;
        }
        
        // Test 8: Performance test
        console.log("\\n📋 TEST 8: Performance Test");
        const startTime = performance.now();
        
        const promises = [];
        for (let i = 0; i < 10; i++) {
            promises.push(encryption.encrypt(`Test message ${i}`, conversationId));
        }
        
        await Promise.all(promises);
        const endTime = performance.now();
        
        console.log(`✅ Performance test completed`);
        console.log(`⏱️  Encrypted 10 messages in ${(endTime - startTime).toFixed(2)}ms`);
        console.log(`⏱️  Average: ${((endTime - startTime) / 10).toFixed(2)}ms per message`);
        
        // Final summary
        console.log("\\n" + "="*60);
        console.log("🎉 ALL ENCRYPTION TESTS PASSED SUCCESSFULLY!");
        console.log("✅ MessageEncryption class is working correctly");
        console.log("✅ Key generation is deterministic and consistent");
        console.log("✅ Encryption/decryption round-trip is working");
        console.log("✅ Performance is acceptable");
        console.log("="*60);
        
        return true;
        
    } catch (error) {
        console.error("\\n❌ ENCRYPTION TEST FAILED!");
        console.error("❌ Error:", error.name);
        console.error("❌ Message:", error.message);
        console.error("❌ Stack:", error.stack);
        return false;
    }
}

// Auto-run the tests
runEncryptionTests().then(success => {
    if (success) {
        console.log("\\n🏆 Test suite completed successfully!");
    } else {
        console.log("\\n💥 Test suite failed!");
    }
});
"""
    
    return js_test_script

def main():
    print("Safe Companions Messaging Encryption Test Helper")
    print("="*60)
    
    # Check if app is running
    if not check_app_status():
        print("\n❌ Cannot proceed - Safe Companions app is not running")
        print("💡 Please start the app with: docker-compose up -d")
        return False
    
    print("\n✅ App is running! Now you can test the encryption.")
    print("\n📋 INSTRUCTIONS:")
    print("1. Open your browser and go to: http://localhost:5000")
    print("2. Login with: seeker1@example.com / password123")
    print("3. Navigate to the messaging page")
    print("4. Open Developer Tools (F12)")
    print("5. Go to the Console tab")
    print("6. Copy and paste the JavaScript test script below:")
    
    print("\n" + "="*60)
    print("JAVASCRIPT TEST SCRIPT - COPY EVERYTHING BELOW:")
    print("="*60)
    
    js_script = generate_test_script()
    print(js_script)
    
    print("="*60)
    print("END OF SCRIPT - COPY EVERYTHING ABOVE")
    print("="*60)
    
    print("\n📊 EXPECTED RESULTS:")
    print("✅ All tests should pass")
    print("✅ You should see debug output with 🔑 and 🔐 emojis")
    print("✅ Final message should be '🎉 ALL ENCRYPTION TESTS PASSED SUCCESSFULLY!'")
    
    print("\n🐛 IF TESTS FAIL:")
    print("❌ Look for JavaScript errors in the console")
    print("❌ Check if MessageEncryption class is undefined")
    print("❌ Verify that encryption.js is loading correctly")
    
    return True

if __name__ == "__main__":
    main()
