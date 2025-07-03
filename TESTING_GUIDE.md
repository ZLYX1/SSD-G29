# 🧪 Complete Security Testing Guide

## Getting Started

### 1. Start the Application
```bash
python app.py
```
The application should start at: **http://localhost:5000**

### 2. Test Credentials
- **Admin:** admin@example.com / password123
- **Seeker:** seeker@example.com / password123  
- **Escort:** escort@example.com / password123

---

## 🛡️ Security Feature Testing

### **1. Session Timeout with Warnings (⏱️ 30-minute timeout)**

#### **Manual Test Steps:**
1. **Login** to the application
2. **Wait 25 minutes** (or modify timeout in session-timeout.js for faster testing)
3. **Expected Result:** Warning modal appears 5 minutes before timeout
4. **Test Options:**
   - Click **"Stay Logged In"** → Session extends by 30 minutes
   - Click **"Logout Now"** → Immediate logout
   - **Do nothing** → Automatic logout after countdown

#### **Quick Test (Modify timeout for testing):**
1. Edit `static/js/session-timeout.js`
2. Change `SESSION_TIMEOUT` to `2 * 60 * 1000` (2 minutes)
3. Change `WARNING_TIME` to `30 * 1000` (30 seconds)
4. Refresh page and wait 1.5 minutes for warning

#### **Browser Console Test:**
```javascript
// Force show session warning (in browser console)
if (window.sessionTimeout) {
    window.sessionTimeout.showSessionWarning();
}
```

---

### **2. CSRF Protection Testing (🛡️)**

#### **Test 1: Form CSRF Tokens**
1. **Right-click → Inspect Element** on any form
2. **Look for:** `<input type="hidden" name="csrf_token" value="...">`
3. **Expected:** All forms should have CSRF tokens

#### **Test 2: AJAX CSRF Protection**
1. **Open Browser Console** (F12)
2. **Run:** `document.querySelector('meta[name=csrf-token]').content`
3. **Expected:** Should return a CSRF token value

#### **Test 3: CSRF Attack Simulation**
1. **Try submitting form without CSRF token:**
```javascript
// In browser console - this should fail
fetch('/profile/', {
    method: 'POST',
    body: new FormData(document.querySelector('form'))
});
```
2. **Expected:** 400 error or CSRF validation failure

---

### **3. Content Security Policy (CSP) Testing (🔒)**

#### **Browser Console CSP Check:**
1. **Open Developer Tools** (F12)
2. **Go to Console tab**
3. **Look for CSP violations** (should see none with legitimate content)
4. **Network tab:** Check response headers for CSP policy

#### **CSP Headers Verification:**
1. **Network tab → Select any request**
2. **Response Headers should include:**
   - `Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'...`
   - `X-Frame-Options: DENY`
   - `X-Content-Type-Options: nosniff`
   - `X-XSS-Protection: 1; mode=block`

#### **CSP Violation Test:**
```javascript
// This should be blocked by CSP (run in console)
eval('console.log("This should be blocked")');
```

---

### **4. Profile Editing Validation Testing (👤)**

#### **Test Invalid Data:**
1. **Go to Profile page**
2. **Test invalid names:**
   - Empty name → Should show error
   - "123Test!" → Should reject special characters
   - Single character → Should require 2+ characters
   - 101+ characters → Should reject long names

3. **Test bio validation:**
   - 501+ characters → Should reject

4. **Test availability validation:**
   - Invalid selection → Should reject

#### **Test File Upload:**
1. **Try uploading invalid file types:**
   - .txt, .exe, .pdf files → Should reject
2. **Try uploading large files:**
   - >5MB files → Should reject
3. **Valid uploads:**
   - .jpg, .png files <5MB → Should accept

---

### **5. Rate Limiting & Account Lockout Testing (🚫)**

#### **Test Login Rate Limiting:**
1. **Try logging in with wrong password 6+ times rapidly**
2. **Expected:** Should get rate limited after 5 attempts
3. **Wait 30 minutes or check admin dashboard to unblock**

#### **Test Account Lockout:**
1. **Try 5 failed login attempts for same user**
2. **Expected:** Account should lock for 30 minutes
3. **Check:** Security events should be logged

#### **Admin Security Dashboard:**
1. **Login as admin:** admin@example.com / password123
2. **Visit:** http://localhost:5000/security/dashboard
3. **View:**
   - Security events
   - Rate limit entries
   - Account lockout status
   - Unblock functionality

---

## 🔧 Advanced Testing

### **1. Database Security Testing**

#### **Check Security Tables:**
```sql
-- Connect to your database and run:
SELECT COUNT(*) FROM security_event;
SELECT COUNT(*) FROM rate_limit_entry;
SELECT * FROM security_event ORDER BY timestamp DESC LIMIT 5;
```

### **2. API Endpoint Testing**

#### **Session Check API:**
```bash
curl -X GET http://localhost:5000/auth/session-check \
  -H "Cookie: session=your_session_cookie"
```

#### **Security Events API (Admin only):**
```bash
curl -X GET http://localhost:5000/security/events \
  -H "Cookie: session=admin_session_cookie"
```

### **3. Messaging & Reporting System**

#### **Test Messaging:**
1. **Login as different users**
2. **Send messages between users**
3. **Test message privacy and delivery**

#### **Test Reporting:**
1. **Report a user for inappropriate behavior**
2. **Check admin dashboard for reports**
3. **Test report handling and resolution**

---

## 🚨 Automated Testing Scripts

### **Run All Security Tests:**
```bash
# Run CSRF protection tests
python tests/security/test_csrf_protection.py

# Run session timeout tests  
python tests/security/test_session_timeout.py

# Run profile validation tests
python tests/security/test_profile_security.py

# Run CSP tests
python tests/security/test_csp.py

# Run rate limiting tests
python tests/security/test_rate_limiting.py
```

### **Manual Security Verification:**
```bash
# Run comprehensive security check
python tests/security/manual_security_test.py
```

---

## ✅ Expected Test Results

### **✅ Passing Tests Should Show:**
- Session timeout warning modal appears
- CSRF tokens present in all forms
- CSP headers block malicious content
- Profile validation rejects invalid data
- Rate limiting blocks excessive requests
- Account lockout after failed attempts
- Security events logged properly

### **❌ Security Violations Should Be Blocked:**
- Form submissions without CSRF tokens
- File uploads of wrong types/sizes
- Excessive login attempts
- Inline script execution (CSP)
- Session access after timeout
- Invalid profile data

---

## 🎯 Key Security Metrics to Verify

1. **Session Management:** ✅ 30-min timeout with 5-min warning
2. **CSRF Protection:** ✅ All forms and AJAX protected
3. **CSP Headers:** ✅ Comprehensive policy preventing XSS
4. **Input Validation:** ✅ Profile data validated server & client-side
5. **Rate Limiting:** ✅ Login, API, and user action limits
6. **Account Security:** ✅ Lockout after failed attempts
7. **Security Logging:** ✅ All events logged with details

---

## 📞 Need Help?

If any tests fail or you encounter issues:

1. **Check browser console** for JavaScript errors
2. **Check server logs** for Python errors  
3. **Verify database** tables exist and have data
4. **Confirm all files** are in place (session-timeout.js, etc.)
5. **Check CSP violations** in browser dev tools

**All security features are implemented and ready for testing!** 🚀
