#!/usr/bin/env python3
"""
Quick test to verify actual HTML content of report forms
"""
import requests
from requests.auth import HTTPBasicAuth

def test_report_form_content():
    print("🔍 TESTING REPORT FORM CONTENT")
    print("=" * 50)
    
    # Create session and attempt login
    session = requests.Session()
    
    # Get login page
    login_response = session.get("http://localhost:5000/login")
    print(f"Login page status: {login_response.status_code}")
    
    # Attempt login with testuser
    login_data = {
        'email': 'testuser@example.com',
        'password': 'password123'
    }
    
    login_post = session.post("http://localhost:5000/login", data=login_data)
    print(f"Login attempt status: {login_post.status_code}")
    print(f"Login attempt URL: {login_post.url}")
    
    # Try to access report form
    report_response = session.get("http://localhost:5000/report/submit")
    print(f"Report form status: {report_response.status_code}")
    
    if report_response.status_code == 200:
        content = report_response.text
        print("\n📋 FORM CONTENT ANALYSIS:")
        print("-" * 30)
        
        # Save the actual HTML for inspection
        with open("debug_report_form.html", "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ HTML content saved to debug_report_form.html")
        
        # Check for key elements
        checks = [
            ("Report Types", any(rtype in content.lower() for rtype in ["harassment", "fraud", "inappropriate"])),
            ("Severity Levels", any(sev in content.lower() for sev in ["low", "medium", "high", "critical"])),
            ("Description Field", "description" in content.lower()),
            ("Title Field", "title" in content.lower()),
            ("Evidence Field", "evidence" in content.lower()),
            ("Submit Button", "submit" in content.lower()),
            ("Form Tag", "<form" in content.lower()),
            ("Select Elements", "select" in content.lower()),
        ]
        
        for check_name, found in checks:
            status = "✅ FOUND" if found else "❌ MISSING"
            print(f"{status}: {check_name}")
        
        # Check specific form elements
        print(f"\n🔍 SPECIFIC CONTENT SEARCH:")
        print(f"Contains 'report_type': {'report_type' in content}")
        print(f"Contains 'severity': {'severity' in content}")
        print(f"Contains 'harassment': {'harassment' in content}")
        print(f"Contains form action: {'action=' in content}")
        
        # Show a snippet of the form area
        if "<form" in content:
            form_start = content.find("<form")
            form_end = content.find("</form>", form_start) + 7
            if form_end > form_start:
                form_content = content[form_start:form_end]
                print(f"\n📝 FORM SNIPPET (first 500 chars):")
                print(form_content[:500] + "..." if len(form_content) > 500 else form_content)
    else:
        print(f"❌ Could not access report form: {report_response.status_code}")
        print(f"Response URL: {report_response.url}")

if __name__ == '__main__':
    test_report_form_content()
