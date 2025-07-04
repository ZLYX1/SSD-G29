# 📧 Email Verification System - Manual Testing Guide

## 🚀 **Step-by-Step Testing Instructions**

### **Prerequisites:**
- ✅ Environment variables configured (including RECAPTCHA_SECRET_KEY)
- ✅ Database migration applied (email_verification_migration.sql)
- ✅ Flask application ready to run

---

## **Phase 1: Setup Testing** ⚙️

### 1.1 Run Unit Tests First
```bash
# Test the verification logic without full app
python test_email_verification_complete.py
```

### 1.2 Check Environment
```bash
# Verify all required environment variables
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

required = ['DATABASE_HOST', 'DATABASE_PORT', 'DATABASE_NAME', 'DATABASE_USERNAME', 'DATABASE_PASSWORD', 'RECAPTCHA_SECRET_KEY']
missing = [var for var in required if not os.environ.get(var)]
if missing:
    print(f'❌ Missing: {missing}')
else:
    print('✅ All environment variables present')
"
```

---

## **Phase 2: Database Testing** 🗄️

### 2.1 Apply Database Migration
```sql
-- Run this SQL in your PostgreSQL database:
ALTER TABLE "user" 
ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE NOT NULL,
ADD COLUMN IF NOT EXISTS email_verification_token VARCHAR(100) UNIQUE,
ADD COLUMN IF NOT EXISTS email_verification_token_expires TIMESTAMP;

-- Verify columns were added:
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'user' 
AND column_name LIKE '%email%';
```

### 2.2 Test Database Connection
```bash
# Start your Flask app (it will test DB connection)
python app.py
```
*Look for: "[INFO] Connecting to DB host..." messages*

---

## **Phase 3: Registration Flow Testing** 📝

### 3.1 Start Application
```bash
# Start Flask development server
python app.py
# Or if using Flask CLI:
flask run
```

### 3.2 Test Registration
1. **Open browser**: `http://localhost:5000/auth?mode=register`
2. **Fill registration form**:
   - Email: `testuser@example.com`
   - Password: `TestPassword123!`
   - Age: `25`
   - Gender: `Female`
   - Role: `seeker`
   - Preference: `Both`
3. **Submit form**
4. **Check console output** for verification URL:
   ```
   ==================================================
   EMAIL VERIFICATION FOR: testuser@example.com
   Verification URL: http://localhost:5000/auth/verify-email/[TOKEN]
   Token expires: 2025-07-03 19:15:36.864893
   ==================================================
   ```

### 3.3 Expected Results
- ✅ Success message: "Registration successful! Please check your email..."
- ✅ User redirected to login page
- ✅ Verification URL printed in console

---

## **Phase 4: Email Verification Testing** ✉️

### 4.1 Copy Verification URL
From console output, copy the full verification URL

### 4.2 Test Verification
1. **Paste URL in browser**
2. **Expected**: Redirect to login with success message
3. **Check database**:
   ```sql
   SELECT email, email_verified, email_verification_token 
   FROM "user" 
   WHERE email = 'testuser@example.com';
   ```
   *Should show: `email_verified = true`, `email_verification_token = null`*

---

## **Phase 5: Login Security Testing** 🔐

### 5.1 Test Unverified User Login
1. **Create second user** (don't verify email)
2. **Try to login** with unverified account
3. **Expected**: Login blocked with message:
   > "Please verify your email address before logging in. Check your inbox for the verification link."

### 5.2 Test Verified User Login
1. **Login with verified account** (from Phase 4)
2. **Expected**: Successful login and redirect to dashboard

---

## **Phase 6: Edge Case Testing** ⚠️

### 6.1 Test Expired Token
1. **Generate expired token** in database:
   ```sql
   UPDATE "user" 
   SET email_verification_token = 'expired_token_123',
       email_verification_token_expires = NOW() - INTERVAL '1 hour'
   WHERE email = 'testuser@example.com';
   ```
2. **Try verification URL**: `http://localhost:5000/auth/verify-email/expired_token_123`
3. **Expected**: Error message about expired token

### 6.2 Test Invalid Token
1. **Visit URL with invalid token**: `http://localhost:5000/auth/verify-email/invalid_token`
2. **Expected**: Error message about invalid token

### 6.3 Test Resend Verification
1. **Go to login page**
2. **Use "Resend Verification" form**
3. **Enter unverified email address**
4. **Check console** for new verification URL

---

## **Phase 7: Security Testing** 🛡️

### 7.1 Test CSRF Protection
1. **Disable JavaScript** in browser
2. **Try registration** without CSRF token
3. **Expected**: CSRF error

### 7.2 Test Token Uniqueness
1. **Register multiple users**
2. **Check database**:
   ```sql
   SELECT email_verification_token, COUNT(*) 
   FROM "user" 
   WHERE email_verification_token IS NOT NULL 
   GROUP BY email_verification_token 
   HAVING COUNT(*) > 1;
   ```
3. **Expected**: No duplicate tokens

---

## **📊 Test Results Checklist**

### **Basic Functionality:**
- [ ] Registration creates unverified user
- [ ] Verification email "sent" (URL in console)
- [ ] Verification URL works correctly
- [ ] Database updated after verification
- [ ] Verified users can login
- [ ] Unverified users cannot login

### **Security Features:**
- [ ] Tokens are cryptographically secure
- [ ] Tokens expire after 24 hours
- [ ] CSRF protection works
- [ ] No token reuse possible

### **User Experience:**
- [ ] Clear success/error messages
- [ ] Resend verification works
- [ ] Professional email template
- [ ] Intuitive flow

---

## **🐛 Common Issues & Solutions**

### **Issue: "RECAPTCHA_SECRET_KEY not found"**
**Solution**: Add to `.env` file:
```bash
RECAPTCHA_SECRET_KEY=test_secret_key_for_development
```

### **Issue: Database connection failed**
**Solution**: Check Docker is running or update DATABASE_HOST in `.env`

### **Issue: "No such table: user"**
**Solution**: Run database migration SQL script

### **Issue: Verification URL gives 404**
**Solution**: Ensure auth blueprint is registered in app.py

---

## **🎯 Success Criteria**

**Email Verification System is working correctly when:**
1. ✅ New users start as unverified
2. ✅ Verification emails are generated
3. ✅ Email verification links work
4. ✅ Unverified users cannot login
5. ✅ Verified users can login normally
6. ✅ Security measures are in place
7. ✅ User experience is smooth

---

## **📈 Next Steps After Testing**

1. **Production Email**: Configure real SMTP settings
2. **Monitoring**: Add logging for verification metrics
3. **Rate Limiting**: Prevent verification email spam
4. **Admin Interface**: Tools to manage user verification status
