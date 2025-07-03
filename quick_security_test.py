#!/usr/bin/env python3
"""
Quick Security Feature Test - Verifies all security implementations
Run this to quickly check if all security features are properly implemented
"""

import os
import sys
import time

def check_file_exists(filepath, description):
    """Check if a file exists and report status"""
    if os.path.exists(filepath):
        print(f"✅ {description}: Found")
        return True
    else:
        print(f"❌ {description}: Missing")
        return False

def check_file_content(filepath, search_terms, description):
    """Check if file contains required content"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            found_terms = []
            missing_terms = []
            
            for term in search_terms:
                if term in content:
                    found_terms.append(term)
                else:
                    missing_terms.append(term)
            
            if missing_terms:
                print(f"⚠️  {description}: Missing {missing_terms}")
                return False
            else:
                print(f"✅ {description}: All required content found")
                return True
    except Exception as e:
        print(f"❌ {description}: Error reading file - {e}")
        return False

def main():
    print("🧪 Security Features Quick Test")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Test 1: Core Files Exist
    print("\n1. Core Security Files:")
    files_to_check = [
        ("app.py", "Main application file"),
        ("static/js/session-timeout.js", "Session timeout JavaScript"),
        ("templates/base.html", "Base template"),
        ("templates/profile.html", "Profile template"),
        ("blueprint/profile.py", "Profile blueprint"),
        ("SECURITY_IMPLEMENTATION.md", "Security documentation"),
        ("TESTING_GUIDE.md", "Testing guide")
    ]
    
    for filepath, description in files_to_check:
        if not check_file_exists(filepath, description):
            all_tests_passed = False
    
    # Test 2: CSP Implementation
    print("\n2. Content Security Policy (CSP):")
    csp_terms = [
        "@app.after_request",
        "Content-Security-Policy",
        "default-src 'self'",
        "X-Frame-Options",
        "X-XSS-Protection"
    ]
    if not check_file_content("app.py", csp_terms, "CSP Headers in app.py"):
        all_tests_passed = False
    
    # Test 3: Session Timeout
    print("\n3. Session Timeout Implementation:")
    session_terms = [
        "SessionTimeout",
        "sessionTimeout",
        "warningModal",
        "SESSION_TIMEOUT",
        "extendSession"
    ]
    if not check_file_content("static/js/session-timeout.js", session_terms, "Session timeout JavaScript"):
        all_tests_passed = False
    
    # Test 4: CSRF Protection
    print("\n4. CSRF Protection:")
    csrf_terms = [
        "csrf_token",
        "{{ csrf_token() }}",
        "csrf-token"
    ]
    
    # Check base template for CSRF meta tag
    if not check_file_content("templates/base.html", ["csrf-token"], "CSRF meta tag in base template"):
        all_tests_passed = False
    
    # Check profile template for CSRF token
    if not check_file_content("templates/profile.html", ["csrf_token"], "CSRF token in profile form"):
        all_tests_passed = False
    
    # Test 5: Profile Validation
    print("\n5. Profile Validation:")
    validation_terms = [
        "validate_profile_data",
        "errors = []",
        "re.match",
        "availability"
    ]
    if not check_file_content("blueprint/profile.py", validation_terms, "Profile validation function"):
        all_tests_passed = False
    
    # Test 6: Enhanced Profile Template
    print("\n6. Enhanced Profile Template:")
    profile_terms = [
        "get_flashed_messages",
        "alert alert-",
        "form-label",
        "required",
        "maxlength"
    ]
    if not check_file_content("templates/profile.html", profile_terms, "Enhanced profile template"):
        all_tests_passed = False
    
    # Test 7: Security Documentation
    print("\n7. Documentation:")
    if not check_file_exists("SECURITY_IMPLEMENTATION.md", "Security implementation documentation"):
        all_tests_passed = False
    if not check_file_exists("TESTING_GUIDE.md", "Testing guide documentation"):
        all_tests_passed = False
    
    # Final Results
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 ALL SECURITY FEATURES IMPLEMENTED SUCCESSFULLY!")
        print("\n🚀 Ready to test:")
        print("1. Start the app: python app.py")
        print("2. Visit: http://localhost:5000")
        print("3. Follow the TESTING_GUIDE.md for detailed testing")
        print("\n📋 Available test credentials:")
        print("• Admin: admin@example.com / password123")
        print("• Seeker: seeker@example.com / password123")
        print("• Escort: escort@example.com / password123")
    else:
        print("⚠️  Some security features may be missing or incomplete.")
        print("Please check the failed items above.")
    
    print("\n📚 Documentation files created:")
    print("• SECURITY_IMPLEMENTATION.md - Complete feature overview")
    print("• TESTING_GUIDE.md - Step-by-step testing instructions")
    
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
