#!/usr/bin/env python3
"""Test CSRF context processor and token generation"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

def test_csrf_context():
    """Test if CSRF token is correctly injected into template context"""
    with app.test_client() as client:
        with app.test_request_context():
            # Get the context processor
            context_processors = app.template_context_processors[None]
            print(f"Found {len(context_processors)} context processors")
            
            # Test the inject_csrf_token function
            for processor in context_processors:
                result = processor()
                if 'csrf_token' in result:
                    csrf_token_func = result['csrf_token']
                    print(f"CSRF token function: {csrf_token_func}")
                    print(f"CSRF token function type: {type(csrf_token_func)}")
                    
                    # Try to call the function
                    try:
                        token = csrf_token_func()
                        print(f"Generated CSRF token: {token}")
                        print(f"Token type: {type(token)}")
                        print(f"Token length: {len(token)}")
                        return True
                    except Exception as e:
                        print(f"Error calling CSRF token function: {e}")
                        return False
            
            print("No CSRF token found in context processors")
            return False

def test_template_rendering():
    """Test if templates render correctly with CSRF token"""
    with app.test_client() as client:
        try:
            # Test a simple page that uses base.html
            response = client.get('/')
            print(f"Home page status: {response.status_code}")
            
            # Check if the page contains the CSRF meta tag
            if b'csrf-token' in response.data:
                print("✓ CSRF token meta tag found in response")
            else:
                print("✗ CSRF token meta tag NOT found in response")
            
            # Test login page specifically
            response = client.get('/auth/login')
            print(f"Login page status: {response.status_code}")
            
            if response.status_code == 200:
                print("✓ Login page rendered successfully")
                if b'csrf-token' in response.data:
                    print("✓ CSRF token meta tag found in login page")
                else:
                    print("✗ CSRF token meta tag NOT found in login page")
                
                # Look for CSRF token in form
                if b'csrf_token' in response.data:
                    print("✓ CSRF token found in form")
                else:
                    print("✗ CSRF token NOT found in form")
                    
                return True
            else:
                print(f"✗ Login page failed with status {response.status_code}")
                print(f"Response data: {response.data.decode()}")
                return False
                
        except Exception as e:
            print(f"Error rendering template: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("Testing CSRF context processor...")
    context_ok = test_csrf_context()
    
    print("\nTesting template rendering...")
    template_ok = test_template_rendering()
    
    if context_ok and template_ok:
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed!")
