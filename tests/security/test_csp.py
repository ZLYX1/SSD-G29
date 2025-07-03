#!/usr/bin/env python3
"""
CSP (Content Security Policy) Test Suite
Tests that CSP headers are properly configured and don't break functionality
"""

import sys
import os
import requests
import re
from urllib.parse import urljoin

class CSPTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_csp_presence(self):
        """Test that CSP headers are present on all pages"""
        print("\n=== Testing CSP Header Presence ===")
        
        test_pages = [
            "/",
            "/auth/login",
            "/auth/register", 
            "/profile/",
            "/booking/",
            "/browse/",
            "/payment/",
            "/messaging/"
        ]
        
        for page in test_pages:
            print(f"\nTesting: {page}")
            try:
                url = urljoin(self.base_url, page)
                response = self.session.get(url)
                
                csp_header = response.headers.get('Content-Security-Policy')
                if csp_header:
                    print("✅ CSP header present")
                    print(f"   Policy: {csp_header[:100]}...")
                else:
                    print("❌ CSP header missing")
                    
            except Exception as e:
                print(f"❌ Request failed: {e}")
    
    def test_csp_directives(self):
        """Test that required CSP directives are present"""
        print("\n=== Testing CSP Directives ===")
        
        try:
            response = self.session.get(self.base_url)
            csp_header = response.headers.get('Content-Security-Policy', '')
            
            # Required directives and their expected values
            required_directives = {
                'default-src': ["'self'"],
                'script-src': ["'self'", "'unsafe-inline'"],  # Note: unsafe-inline needed for inline scripts
                'style-src': ["'self'", "'unsafe-inline'"],   # Note: unsafe-inline needed for inline styles
                'img-src': ["'self'", "data:", "https:", "blob:"],
                'object-src': ["'none'"],
                'base-uri': ["'self'"],
                'form-action': ["'self'"],
                'frame-ancestors': ["'none'"]
            }
            
            for directive, expected_sources in required_directives.items():
                if directive in csp_header:
                    print(f"✅ {directive} directive found")
                    
                    # Check if expected sources are present
                    directive_match = re.search(f"{directive}\\s+([^;]+)", csp_header)
                    if directive_match:
                        sources = directive_match.group(1).strip()
                        for expected in expected_sources:
                            if expected in sources:
                                print(f"   ✅ {expected} source present")
                            else:
                                print(f"   ❌ {expected} source missing")
                else:
                    print(f"❌ {directive} directive missing")
                    
        except Exception as e:
            print(f"❌ Request failed: {e}")
    
    def test_security_headers(self):
        """Test that other security headers are present"""
        print("\n=== Testing Security Headers ===")
        
        security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }
        
        try:
            response = self.session.get(self.base_url)
            
            for header, expected_value in security_headers.items():
                actual_value = response.headers.get(header)
                if actual_value:
                    if expected_value.lower() in actual_value.lower():
                        print(f"✅ {header}: {actual_value}")
                    else:
                        print(f"⚠️  {header}: {actual_value} (expected {expected_value})")
                else:
                    print(f"❌ {header} missing")
                    
        except Exception as e:
            print(f"❌ Request failed: {e}")
    
    def test_inline_scripts_styles(self):
        """Test that inline scripts and styles work with CSP"""
        print("\n=== Testing Inline Scripts/Styles Compatibility ===")
        
        test_pages = [
            "/",
            "/profile/",
            "/auth/login"
        ]
        
        for page in test_pages:
            print(f"\nTesting inline content on: {page}")
            try:
                url = urljoin(self.base_url, page)
                response = self.session.get(url)
                
                # Check for inline scripts
                inline_scripts = re.findall(r'<script[^>]*>(.*?)</script>', response.text, re.DOTALL)
                if inline_scripts:
                    print(f"   📄 Found {len(inline_scripts)} inline script(s)")
                    
                    # Check if CSP allows unsafe-inline for scripts
                    csp_header = response.headers.get('Content-Security-Policy', '')
                    if "'unsafe-inline'" in csp_header and "script-src" in csp_header:
                        print("   ✅ CSP allows inline scripts")
                    else:
                        print("   ❌ CSP may block inline scripts")
                else:
                    print("   📄 No inline scripts found")
                
                # Check for inline styles
                inline_styles = re.findall(r'<style[^>]*>(.*?)</style>', response.text, re.DOTALL)
                style_attrs = re.findall(r'style="[^"]*"', response.text)
                
                if inline_styles or style_attrs:
                    total_styles = len(inline_styles) + len(style_attrs)
                    print(f"   🎨 Found {total_styles} inline style(s)")
                    
                    # Check if CSP allows unsafe-inline for styles
                    if "'unsafe-inline'" in csp_header and "style-src" in csp_header:
                        print("   ✅ CSP allows inline styles")
                    else:
                        print("   ❌ CSP may block inline styles")
                else:
                    print("   🎨 No inline styles found")
                    
            except Exception as e:
                print(f"❌ Request failed: {e}")
    
    def test_external_resources(self):
        """Test that external resources are properly allowed"""
        print("\n=== Testing External Resources ===")
        
        try:
            response = self.session.get(self.base_url)
            csp_header = response.headers.get('Content-Security-Policy', '')
            
            # Check for external CDN sources
            external_domains = [
                'cdnjs.cloudflare.com',
                'cdn.jsdelivr.net',
                'fonts.googleapis.com',
                'fonts.gstatic.com',
                'code.jquery.com'
            ]
            
            for domain in external_domains:
                if domain in csp_header:
                    print(f"✅ {domain} allowed in CSP")
                else:
                    print(f"❌ {domain} not found in CSP")
                    
            # Check for Stripe-specific domains (if using Stripe)
            stripe_domains = [
                'api.stripe.com',
                'js.stripe.com'
            ]
            
            for domain in stripe_domains:
                if domain in csp_header:
                    print(f"✅ {domain} allowed in CSP (Stripe)")
                else:
                    print(f"⚠️  {domain} not found in CSP (may be needed for Stripe)")
                    
        except Exception as e:
            print(f"❌ Request failed: {e}")
    
    def test_csp_report_uri(self):
        """Test if CSP has reporting configured"""
        print("\n=== Testing CSP Reporting ===")
        
        try:
            response = self.session.get(self.base_url)
            csp_header = response.headers.get('Content-Security-Policy', '')
            
            if 'report-uri' in csp_header:
                print("✅ CSP reporting configured")
            elif 'report-to' in csp_header:
                print("✅ CSP reporting configured (report-to)")
            else:
                print("ℹ️  CSP reporting not configured (optional)")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
    
    def run_all_tests(self):
        """Run all CSP tests"""
        print("Starting CSP Test Suite")
        print("=" * 50)
        
        # Test basic connectivity
        try:
            response = self.session.get(self.base_url)
            if response.status_code != 200:
                print(f"❌ Server not accessible at {self.base_url}")
                return
        except Exception as e:
            print(f"❌ Cannot connect to server: {e}")
            print("Note: Make sure the Flask application is running")
            return
        
        self.test_csp_presence()
        self.test_csp_directives()
        self.test_security_headers()
        self.test_inline_scripts_styles()
        self.test_external_resources()
        self.test_csp_report_uri()
        
        print("\n" + "=" * 50)
        print("CSP Test Suite Complete")
        
        print("\n📝 CSP Best Practices Recommendations:")
        print("1. Consider removing 'unsafe-inline' from script-src when possible")
        print("2. Consider removing 'unsafe-inline' from style-src when possible")
        print("3. Add CSP reporting to monitor violations")
        print("4. Test CSP in browser console for any violations")

if __name__ == "__main__":
    tester = CSPTester()
    tester.run_all_tests()
