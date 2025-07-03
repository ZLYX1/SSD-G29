#!/usr/bin/env python3
"""
Profile Security and Validation Test Suite
Tests profile editing security features and validation
"""

import sys
import os
import requests
import re
from urllib.parse import urljoin

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class ProfileSecurityTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.csrf_token = None
        
    def get_csrf_token(self, url):
        """Extract CSRF token from a page"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            # Try to find CSRF token in meta tag
            meta_match = re.search(r'<meta name="csrf-token" content="([^"]+)"', response.text)
            if meta_match:
                return meta_match.group(1)
            
            # Try to find CSRF token in form
            form_match = re.search(r'<input[^>]*name="csrf_token"[^>]*value="([^"]+)"', response.text)
            if form_match:
                return form_match.group(1)
                
            return None
        except Exception as e:
            print(f"Error getting CSRF token: {e}")
            return None
    
    def test_profile_validation(self):
        """Test profile form validation"""
        print("\n=== Testing Profile Validation ===")
        
        # Test cases for profile validation
        test_cases = [
            {
                "name": "Profile Validation - Empty Name",
                "data": {"name": "", "bio": "Test bio", "availability": "Available"},
                "should_fail": True
            },
            {
                "name": "Profile Validation - Short Name",
                "data": {"name": "A", "bio": "Test bio", "availability": "Available"},
                "should_fail": True
            },
            {
                "name": "Profile Validation - Long Name",
                "data": {"name": "A" * 101, "bio": "Test bio", "availability": "Available"},
                "should_fail": True
            },
            {
                "name": "Profile Validation - Invalid Name Characters",
                "data": {"name": "Test123!@#", "bio": "Test bio", "availability": "Available"},
                "should_fail": True
            },
            {
                "name": "Profile Validation - Long Bio",
                "data": {"name": "Test User", "bio": "A" * 501, "availability": "Available"},
                "should_fail": True
            },
            {
                "name": "Profile Validation - Invalid Availability",
                "data": {"name": "Test User", "bio": "Test bio", "availability": "Invalid Status"},
                "should_fail": True
            },
            {
                "name": "Profile Validation - Valid Data",
                "data": {"name": "Test User", "bio": "This is a valid bio", "availability": "Available"},
                "should_fail": False
            }
        ]
        
        for test_case in test_cases:
            print(f"\nTesting: {test_case['name']}")
            
            # Get CSRF token
            profile_url = urljoin(self.base_url, "/profile/")
            csrf_token = self.get_csrf_token(profile_url)
            
            if not csrf_token:
                print("❌ Could not get CSRF token")
                continue
            
            # Prepare form data
            form_data = test_case['data'].copy()
            form_data['csrf_token'] = csrf_token
            
            # Submit form
            try:
                response = self.session.post(profile_url, data=form_data)
                
                if test_case['should_fail']:
                    # Should see error messages
                    if "danger" in response.text.lower() or "error" in response.text.lower():
                        print("✅ Validation correctly rejected invalid data")
                    else:
                        print("❌ Validation should have failed but didn't")
                else:
                    # Should succeed
                    if response.status_code == 200 and "success" in response.text.lower():
                        print("✅ Valid data accepted")
                    else:
                        print("❌ Valid data was rejected")
                        
            except Exception as e:
                print(f"❌ Request failed: {e}")
    
    def test_profile_csrf_protection(self):
        """Test CSRF protection on profile forms"""
        print("\n=== Testing Profile CSRF Protection ===")
        
        profile_url = urljoin(self.base_url, "/profile/")
        
        # Test 1: Submit form without CSRF token
        print("\nTest 1: Submit without CSRF token")
        form_data = {
            "name": "Test User",
            "bio": "Test bio",
            "availability": "Available"
        }
        
        try:
            response = self.session.post(profile_url, data=form_data)
            if response.status_code == 400 or "csrf" in response.text.lower():
                print("✅ CSRF protection active - request blocked")
            else:
                print("❌ CSRF protection missing - request succeeded")
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        # Test 2: Submit with invalid CSRF token
        print("\nTest 2: Submit with invalid CSRF token")
        form_data['csrf_token'] = "invalid_token_123"
        
        try:
            response = self.session.post(profile_url, data=form_data)
            if response.status_code == 400 or "csrf" in response.text.lower():
                print("✅ CSRF protection active - invalid token rejected")
            else:
                print("❌ CSRF protection bypassed with invalid token")
        except Exception as e:
            print(f"❌ Request failed: {e}")
    
    def test_photo_upload_security(self):
        """Test photo upload security"""
        print("\n=== Testing Photo Upload Security ===")
        
        presigned_url = urljoin(self.base_url, "/profile/generate-presigned-url")
        
        # Test valid file type
        print("\nTest 1: Valid image file type")
        test_data = {
            "file_name": "test.jpg",
            "file_type": "image/jpeg"
        }
        
        try:
            response = self.session.post(presigned_url, json=test_data)
            if response.status_code == 200:
                print("✅ Valid image type accepted")
            else:
                print(f"❌ Valid image type rejected: {response.status_code}")
        except Exception as e:
            print(f"❌ Request failed: {e}")
        
        # Test invalid file type
        print("\nTest 2: Invalid file type")
        test_data = {
            "file_name": "test.exe",
            "file_type": "application/exe"
        }
        
        try:
            response = self.session.post(presigned_url, json=test_data)
            if response.status_code == 400:
                print("✅ Invalid file type correctly rejected")
            else:
                print(f"❌ Invalid file type accepted: {response.status_code}")
        except Exception as e:
            print(f"❌ Request failed: {e}")
    
    def test_csp_headers(self):
        """Test Content Security Policy headers"""
        print("\n=== Testing CSP Headers ===")
        
        test_urls = [
            "/",
            "/profile/",
            "/auth/login",
            "/auth/register"
        ]
        
        for url_path in test_urls:
            print(f"\nTesting CSP for: {url_path}")
            try:
                url = urljoin(self.base_url, url_path)
                response = self.session.get(url)
                
                # Check for CSP header
                csp_header = response.headers.get('Content-Security-Policy')
                if csp_header:
                    print("✅ CSP header present")
                    
                    # Check for key CSP directives
                    required_directives = [
                        'default-src',
                        'script-src',
                        'style-src',
                        'img-src',
                        'object-src',
                        'base-uri',
                        'form-action'
                    ]
                    
                    for directive in required_directives:
                        if directive in csp_header:
                            print(f"  ✅ {directive} directive found")
                        else:
                            print(f"  ❌ {directive} directive missing")
                else:
                    print("❌ CSP header missing")
                
                # Check other security headers
                security_headers = [
                    'X-Content-Type-Options',
                    'X-Frame-Options',
                    'X-XSS-Protection',
                    'Referrer-Policy'
                ]
                
                for header in security_headers:
                    if response.headers.get(header):
                        print(f"  ✅ {header} header present")
                    else:
                        print(f"  ❌ {header} header missing")
                        
            except Exception as e:
                print(f"❌ Request failed for {url_path}: {e}")
    
    def run_all_tests(self):
        """Run all profile security tests"""
        print("Starting Profile Security Test Suite")
        print("=" * 50)
        
        # Note: These tests assume the server is running and accessible
        try:
            # Test basic connectivity
            response = self.session.get(self.base_url)
            if response.status_code != 200:
                print(f"❌ Server not accessible at {self.base_url}")
                return
        except Exception as e:
            print(f"❌ Cannot connect to server: {e}")
            print("Note: Make sure the Flask application is running")
            return
        
        self.test_profile_validation()
        self.test_profile_csrf_protection()
        self.test_photo_upload_security()
        self.test_csp_headers()
        
        print("\n" + "=" * 50)
        print("Profile Security Test Suite Complete")

if __name__ == "__main__":
    tester = ProfileSecurityTester()
    tester.run_all_tests()
