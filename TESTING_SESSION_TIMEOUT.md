# 🧪 Manual Session Timeout Testing Guide

## **How to Test Session Timeout with Warnings**

### **Prerequisites**
- Application is running at `http://localhost:5000`
- You have test user credentials:
  - **Admin:** admin@example.com / password123
  - **Seeker:** seeker@example.com / password123
  - **Escort:** escort@example.com / password123

---

## **Test Method 1: Quick Test (5-10 seconds)**

### **Step 1: Open Test Page**
1. Open browser and go to: `http://localhost:5000/test-session-timeout`
2. You should see the "Session Timeout Test Page"

### **Step 2: Quick Timeout Test**
1. Click **"Test Quick Timeout"** button
2. Wait 5 seconds - you should see a warning modal appear
3. The modal should show:
   - ⚠️ "Session Timeout Warning" title
   - Countdown showing remaining time
   - Two buttons: "Stay Logged In" and "Logout Now"

### **Step 3: Test User Actions**
1. **Test "Stay Logged In":**
   - Click "Stay Logged In" button
   - Modal should close and session should extend
   - Status should show "✅ Session extended successfully"

2. **Test "Logout Now":**
   - Run the test again
   - When modal appears, click "Logout Now"
   - Should show logout confirmation

---

## **Test Method 2: Real Application Test**

### **Step 1: Login to Application**
1. Go to: `http://localhost:5000/auth/?mode=login`
2. Login with: `admin@example.com` / `password123`
3. You should be redirected to the dashboard

### **Step 2: Verify Session Timeout is Active**
1. Open browser developer tools (F12)
2. Go to **Console** tab
3. Check if you see session timeout initialization messages
4. Look for: "Session timeout system initialized"

### **Step 3: Test Session Check API**
1. In the browser console, run:
   ```javascript
   fetch('/auth/session-check')
     .then(response => response.json())
     .then(data => console.log('Session status:', data));
   ```
2. You should see: `{valid: true, user_id: [number]}`

### **Step 4: Test Session Extension API**
1. In the browser console, run:
   ```javascript
   fetch('/auth/extend-session', {
     method: 'POST',
     headers: {'Content-Type': 'application/json'},
     body: JSON.stringify({})
   })
   .then(response => response.json())
   .then(data => console.log('Extend result:', data));
   ```
2. You should see: `{success: true, message: "Session extended successfully"}`

---

## **Test Method 3: Real Session Timeout (30 minutes)**

### **Step 1: Setup for Long Test**
1. Login to the application
2. Note the current time
3. Leave the browser window open but don't interact with it

### **Step 2: Wait for Warning (25 minutes)**
1. After 25 minutes (5 minutes before 30-minute timeout)
2. You should see the warning modal appear automatically
3. The modal should show a 5-minute countdown

### **Step 3: Test Warning Behavior**
1. **Do Nothing:** Wait 5 more minutes, session should expire and redirect to login
2. **Extend Session:** Click "Stay Logged In" to extend for another 30 minutes
3. **Logout:** Click "Logout Now" to logout immediately

---

## **Test Method 4: Activity Detection Test**

### **Step 1: Login and Monitor**
1. Login to the application
2. Open browser developer tools
3. Monitor the console for session timeout messages

### **Step 2: Test Activity Extension**
1. After 10-15 minutes, perform user actions:
   - Click navigation links
   - Scroll the page
   - Move the mouse
   - Type in any form fields
2. Check if session timer resets with activity

### **Step 3: Verify Activity Tracking**
1. Check that user activities extend the session automatically
2. Verify that the 30-minute timer resets when you're active

---

## **Test Method 5: API Testing with Postman/Curl**

### **Step 1: Test Session Check Endpoint**
```bash
# Check session status
curl -X GET http://localhost:5000/auth/session-check \
  -H "Cookie: session=[your-session-cookie]"
```

### **Step 2: Test Session Extension Endpoint**
```bash
# Extend session
curl -X POST http://localhost:5000/auth/extend-session \
  -H "Cookie: session=[your-session-cookie]" \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## **Expected Results**

### **✅ Success Indicators:**
- Warning modal appears 5 minutes before timeout
- Session extends when "Stay Logged In" is clicked
- Session expires after 30 minutes of inactivity
- User activity resets the session timer
- APIs return correct JSON responses
- Automatic redirect to login when session expires

### **❌ Failure Indicators:**
- No warning modal appears
- Session doesn't extend when requested
- Session expires immediately
- APIs return error responses
- No automatic activity detection
- No redirect on session expiry

---

## **Troubleshooting**

### **If Warning Modal Doesn't Appear:**
1. Check browser console for JavaScript errors
2. Verify that `session-timeout.js` is loaded
3. Check that user ID is set in the body data attribute
4. Ensure you're logged in with a valid session

### **If Session Check API Fails:**
1. Verify you're logged in
2. Check that the `/auth/session-check` endpoint exists
3. Verify database connection is working
4. Check server logs for errors

### **If Session Extension Fails:**
1. Verify CSRF token is being sent
2. Check that you're authenticated
3. Verify the `/auth/extend-session` endpoint exists
4. Check for rate limiting restrictions

---

## **Security Verification**

### **Test Security Features:**
1. **CSRF Protection:** Session extension requires proper CSRF token
2. **Authentication:** All session operations require valid login
3. **Rate Limiting:** Multiple rapid session checks are rate limited
4. **Account Validation:** Locked accounts cannot extend sessions

### **Test Edge Cases:**
1. **Invalid Session:** Clear cookies and test session check
2. **Expired Session:** Wait for full timeout and test behavior
3. **Multiple Windows:** Test session behavior across multiple browser windows
4. **Network Issues:** Test behavior when server is unreachable

---

## **Automated Testing Commands**

```bash
# Run all session timeout tests
docker exec -it safe-companions-web-dev python tests/security/test_session_timeout.py

# Run final integration tests
docker exec -it safe-companions-web-dev python tests/security/test_final_integration.py

# Check application logs
docker logs safe-companions-web-dev --tail=50
```

---

## **What to Look For**

### **In Browser Console:**
- Session timeout initialization messages
- Activity detection events
- Warning modal triggers
- Session extension confirmations

### **In Application:**
- Warning modal with countdown timer
- Proper button functionality
- Smooth user experience
- No JavaScript errors

### **In Server Logs:**
- Session check requests
- Session extension requests
- Session timeout events
- No server errors

---

**🎯 Summary:** The session timeout feature should provide a seamless user experience with clear warnings and easy session extension options while maintaining security through automatic timeout after inactivity.
