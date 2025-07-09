#!/usr/bin/env python3
"""
Comprehensive test for Safe Companions messaging encryption functionality.
This script tests the complete encryption pipeline including:
1. User login
2. JavaScript encryption key generation
3. Message sending and receiving
4. End-to-end encryption verification
"""

import time
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MessageEncryptionTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.driver = None
        self.setup_driver()

    def setup_driver(self):
        """Setup Chrome driver with appropriate options"""
        chrome_options = Options()
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_window_size(1200, 800)
            logger.info("Chrome driver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {e}")
            raise

    def wait_for_element(self, by, value, timeout=10):
        """Wait for an element to be present and return it"""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def wait_for_clickable(self, by, value, timeout=10):
        """Wait for an element to be clickable and return it"""
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )

    def login(self, email, password):
        """Login with given credentials"""
        logger.info(f"Attempting to login with email: {email}")
        
        # Navigate to login page
        self.driver.get(f"{self.base_url}/login")
        
        # Fill in login form
        email_field = self.wait_for_element(By.NAME, "email")
        password_field = self.wait_for_element(By.NAME, "password")
        
        email_field.clear()
        email_field.send_keys(email)
        password_field.clear()
        password_field.send_keys(password)
        
        # Submit form
        login_button = self.wait_for_clickable(By.XPATH, "//button[@type='submit']")
        login_button.click()
        
        # Wait for redirect
        time.sleep(2)
        
        # Check if login was successful
        current_url = self.driver.current_url
        if "/login" not in current_url:
            logger.info(f"Login successful for {email}")
            return True
        else:
            logger.error(f"Login failed for {email}")
            return False

    def navigate_to_messaging(self):
        """Navigate to the messaging page"""
        logger.info("Navigating to messaging page")
        self.driver.get(f"{self.base_url}/messaging")
        time.sleep(3)

    def check_console_errors(self):
        """Check browser console for JavaScript errors"""
        logger.info("Checking browser console for errors...")
        
        # Get console logs
        logs = self.driver.get_log('browser')
        
        errors = []
        warnings = []
        infos = []
        
        for log in logs:
            if log['level'] == 'SEVERE':
                errors.append(log)
            elif log['level'] == 'WARNING':
                warnings.append(log)
            else:
                infos.append(log)
        
        logger.info(f"Console summary: {len(errors)} errors, {len(warnings)} warnings, {len(infos)} info messages")
        
        if errors:
            logger.error("JavaScript errors found:")
            for error in errors:
                logger.error(f"  - {error['message']}")
        
        if warnings:
            logger.warning("JavaScript warnings found:")
            for warning in warnings:
                logger.warning(f"  - {warning['message']}")
        
        return errors, warnings, infos

    def test_encryption_debug_output(self):
        """Test that encryption debug output is working"""
        logger.info("Testing encryption debug output...")
        
        # Execute JavaScript to trigger encryption operations
        try:
            # Test basic encryption initialization
            result = self.driver.execute_script("""
                console.log('🧪 TEST: Starting encryption debug test');
                
                // Check if MessageEncryption class exists
                if (typeof MessageEncryption === 'undefined') {
                    console.error('❌ MessageEncryption class not found');
                    return { error: 'MessageEncryption class not found' };
                }
                
                // Create an instance
                const encryption = new MessageEncryption();
                console.log('✅ MessageEncryption instance created');
                
                // Test conversation key generation
                return encryption.getConversationKey('1_2').then(key => {
                    console.log('✅ Conversation key generated successfully');
                    return { success: true, keyGenerated: true };
                }).catch(error => {
                    console.error('❌ Conversation key generation failed:', error);
                    return { error: 'Conversation key generation failed: ' + error.message };
                });
            """)
            
            logger.info(f"JavaScript execution result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to execute JavaScript: {e}")
            return {"error": f"JavaScript execution failed: {str(e)}"}

    def test_message_encryption_flow(self):
        """Test the complete message encryption flow"""
        logger.info("Testing complete message encryption flow...")
        
        try:
            result = self.driver.execute_script("""
                console.log('🧪 TEST: Starting complete encryption flow test');
                
                return new Promise((resolve, reject) => {
                    try {
                        const encryption = new MessageEncryption();
                        const testMessage = 'Hello, this is a test encrypted message!';
                        const conversationId = '1_2';
                        
                        console.log('🧪 TEST: Starting encryption of test message:', testMessage);
                        
                        encryption.encrypt(testMessage, conversationId).then(encrypted => {
                            console.log('✅ Message encrypted successfully:', encrypted);
                            
                            // Now try to decrypt
                            return encryption.decrypt(encrypted, conversationId);
                        }).then(decrypted => {
                            console.log('✅ Message decrypted successfully:', decrypted);
                            
                            const success = decrypted === testMessage;
                            console.log('🧪 TEST: Encryption round-trip test:', success ? 'PASSED' : 'FAILED');
                            
                            resolve({
                                success: success,
                                original: testMessage,
                                decrypted: decrypted,
                                roundTripWorking: success
                            });
                        }).catch(error => {
                            console.error('❌ Encryption flow failed:', error);
                            resolve({ error: 'Encryption flow failed: ' + error.message });
                        });
                    } catch (error) {
                        console.error('❌ JavaScript error in encryption test:', error);
                        resolve({ error: 'JavaScript error: ' + error.message });
                    }
                });
            """)
            
            logger.info(f"Encryption flow test result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to test encryption flow: {e}")
            return {"error": f"Encryption flow test failed: {str(e)}"}

    def run_comprehensive_test(self):
        """Run a comprehensive test of the messaging encryption system"""
        logger.info("🚀 Starting comprehensive messaging encryption test")
        
        results = {
            "login_test": False,
            "navigation_test": False,
            "console_errors": [],
            "encryption_debug_test": {},
            "encryption_flow_test": {},
            "overall_success": False
        }
        
        try:
            # Test 1: Login
            logger.info("=== TEST 1: User Login ===")
            if self.login("seeker1@example.com", "password123"):
                results["login_test"] = True
                logger.info("✅ Login test PASSED")
            else:
                logger.error("❌ Login test FAILED")
                return results
            
            # Test 2: Navigate to messaging
            logger.info("=== TEST 2: Navigation to Messaging ===")
            self.navigate_to_messaging()
            if "messaging" in self.driver.current_url:
                results["navigation_test"] = True
                logger.info("✅ Navigation test PASSED")
            else:
                logger.error("❌ Navigation test FAILED")
                return results
            
            # Test 3: Check console errors
            logger.info("=== TEST 3: Console Error Check ===")
            errors, warnings, infos = self.check_console_errors()
            results["console_errors"] = {
                "errors": [e['message'] for e in errors],
                "warnings": [w['message'] for w in warnings],
                "error_count": len(errors)
            }
            
            if len(errors) == 0:
                logger.info("✅ Console error check PASSED (no JavaScript errors)")
            else:
                logger.warning(f"⚠️  Console error check found {len(errors)} errors")
            
            # Test 4: Encryption debug output
            logger.info("=== TEST 4: Encryption Debug Test ===")
            results["encryption_debug_test"] = self.test_encryption_debug_output()
            if results["encryption_debug_test"].get("success"):
                logger.info("✅ Encryption debug test PASSED")
            else:
                logger.error("❌ Encryption debug test FAILED")
            
            # Test 5: Complete encryption flow
            logger.info("=== TEST 5: Encryption Flow Test ===")
            results["encryption_flow_test"] = self.test_message_encryption_flow()
            if results["encryption_flow_test"].get("roundTripWorking"):
                logger.info("✅ Encryption flow test PASSED")
            else:
                logger.error("❌ Encryption flow test FAILED")
            
            # Overall assessment
            results["overall_success"] = (
                results["login_test"] and
                results["navigation_test"] and
                results["console_errors"]["error_count"] == 0 and
                results["encryption_debug_test"].get("success", False) and
                results["encryption_flow_test"].get("roundTripWorking", False)
            )
            
            logger.info("=== FINAL RESULTS ===")
            logger.info(f"Login: {'✅ PASS' if results['login_test'] else '❌ FAIL'}")
            logger.info(f"Navigation: {'✅ PASS' if results['navigation_test'] else '❌ FAIL'}")
            error_count = results['console_errors']['error_count']
            console_status = '✅ PASS' if error_count == 0 else f'❌ FAIL ({error_count} errors)'
            logger.info(f"Console Errors: {console_status}")
            logger.info(f"Encryption Debug: {'✅ PASS' if results['encryption_debug_test'].get('success') else '❌ FAIL'}")
            logger.info(f"Encryption Flow: {'✅ PASS' if results['encryption_flow_test'].get('roundTripWorking') else '❌ FAIL'}")
            logger.info(f"Overall: {'🎉 ALL TESTS PASSED' if results['overall_success'] else '❌ SOME TESTS FAILED'}")
            
        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            results["execution_error"] = str(e)
        
        return results

    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser driver closed")

def main():
    """Main function to run the test"""
    tester = None
    try:
        tester = MessageEncryptionTester()
        results = tester.run_comprehensive_test()
        
        # Print summary
        print("\n" + "="*60)
        print("MESSAGING ENCRYPTION TEST SUMMARY")
        print("="*60)
        print(json.dumps(results, indent=2))
        print("="*60)
        
        return results["overall_success"]
        
    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        return False
    finally:
        if tester:
            tester.cleanup()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
