// Enhanced debugging script to test messaging encryption API
// Paste this into browser console on the messaging page

console.log("🔧 DEBUGGING MESSAGING ENCRYPTION API");

// Function to test encryption directly
async function testEncryptionAPI() {
    try {
        console.log("📋 TEST: Creating MessageEncryption instance");
        const encryption = new MessageEncryption();
        
        console.log("📋 TEST: Getting conversation key for 15_18");
        const key = await encryption.getConversationKey("15_18");
        console.log("✅ Key generated:", key);
        
        console.log("📋 TEST: Encrypting test message");
        const testMessage = "Hello, this is a test!";
        const encryptedData = await encryption.encryptMessage(testMessage, key);
        console.log("✅ Encrypted data:", encryptedData);
        
        // Test the exact payload that would be sent
        const payload = {
            recipient_id: 18,
            encrypted_data: encryptedData
        };
        
        console.log("📋 TEST: Payload that would be sent to server:");
        console.log(JSON.stringify(payload, null, 2));
        
        // Test actual API call
        console.log("📋 TEST: Making actual API call");
        const response = await fetch('/messaging/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.csrf_token
            },
            body: JSON.stringify(payload)
        });
        
        const result = await response.json();
        console.log("📋 TEST: API Response:", result);
        
        if (result.success) {
            console.log("✅ Message sent successfully!");
        } else {
            console.error("❌ Message failed:", result.error);
        }
        
    } catch (error) {
        console.error("❌ Test failed:", error);
    }
}

// Function to check form elements
function debugFormElements() {
    console.log("🔍 FORM DEBUG: Checking form elements");
    
    const forms = document.querySelectorAll('form');
    console.log(`Found ${forms.length} forms`);
    
    forms.forEach((form, index) => {
        console.log(`Form ${index}:`, form);
        console.log(`  - ID: ${form.id}`);
        console.log(`  - Action: ${form.action}`);
        console.log(`  - Method: ${form.method}`);
        
        const textareas = form.querySelectorAll('textarea');
        const inputs = form.querySelectorAll('input');
        
        console.log(`  - Textareas: ${textareas.length}`);
        textareas.forEach((ta, i) => {
            console.log(`    ${i}: name="${ta.name}", value="${ta.value}"`);
        });
        
        console.log(`  - Inputs: ${inputs.length}`);
        inputs.forEach((input, i) => {
            console.log(`    ${i}: name="${input.name}", type="${input.type}", value="${input.value}"`);
        });
    });
}

// Function to test what happens when form is submitted
function debugFormSubmission() {
    console.log("🔍 FORM SUBMISSION DEBUG");
    
    const form = document.getElementById('messageForm') || document.getElementById('send-message-form');
    if (!form) {
        console.error("❌ No message form found");
        return;
    }
    
    console.log("✅ Form found:", form);
    
    const messageInput = form.querySelector('textarea[name="content"]') || form.querySelector('input[name="content"]');
    const recipientInput = form.querySelector('input[name="recipient_id"]');
    
    console.log("Message input:", messageInput);
    console.log("Recipient input:", recipientInput);
    
    if (messageInput) {
        console.log("Message input value:", messageInput.value);
    }
    if (recipientInput) {
        console.log("Recipient input value:", recipientInput.value);
    }
    
    // Check current user ID
    const currentUserId = window.currentUserId || parseInt(document.getElementById('currentUserId')?.value);
    console.log("Current user ID:", currentUserId);
    
    // Check CSRF token
    console.log("CSRF token:", window.csrf_token);
}

// Run all debug functions
console.log("🚀 Starting comprehensive debugging...");
debugFormElements();
debugFormSubmission();

// Auto-run encryption test
console.log("🔐 Running encryption API test...");
testEncryptionAPI();
