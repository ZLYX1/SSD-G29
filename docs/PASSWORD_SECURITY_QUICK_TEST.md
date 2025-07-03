# Password Security System - Quick Testing Guide

## 🧪 Quick Testing Instructions

### Prerequisites
1. Ensure Flask app is running: `python app.py`
2. Database migrations completed successfully
3. Test users available in the system

### Test 1: Password Policy Page
**URL**: `http://localhost:5000/auth/password-policy`

**Expected Results**:
- ✅ Displays comprehensive password policy
- ✅ Shows password requirements and examples
- ✅ Includes security best practices
- ✅ Links to change password functionality

### Test 2: Password Change Functionality
**URL**: `http://localhost:5000/auth/change-password/<user_id>` (replace with actual user ID)

**Test Cases**:

#### Test 2.1: Weak Password Rejection
1. Enter current password
2. Try new password: `password123`
3. **Expected**: ❌ Password requirements not met

#### Test 2.2: Strong Password Acceptance
1. Enter current password
2. Try new password: `MyNewPassword2024!`
3. **Expected**: ✅ Password changed successfully

#### Test 2.3: Password History Prevention
1. Change password to: `TestPassword1!`
2. Immediately try to change back to: `TestPassword1!`
3. **Expected**: ❌ Cannot reuse recent password

### Test 3: Login Security Features

#### Test 3.1: Failed Login Attempts
1. Go to login page
2. Use correct email but wrong password
3. Try 5 times with wrong password
4. **Expected**: Account locked for 30 minutes

#### Test 3.2: Password Expiration Warning
1. Manually set a user's password to expire soon (in database)
2. Login with that user
3. **Expected**: Warning about upcoming expiration

#### Test 3.3: Forced Password Change
1. Manually expire a user's password (in database)
2. Try to login with that user
3. **Expected**: Redirected to change password page

### Test 4: Real-time Validation
**URL**: Password change page

**Test Process**:
1. Start typing in "New Password" field
2. **Expected**: Real-time feedback on password strength
3. Try different password combinations:
   - `pass` → Should show "Weak" 
   - `Password1` → Should show requirements not met
   - `Password1!` → Should show "Strong"

## 🔍 Database Verification Commands

### Check Password Security Status
```bash
python test_password_security.py
```

### Check Specific User's Password Status
```bash
python check_latest_otp.py  # Modify to check password fields
```

### Manual Database Queries
```sql
-- Check password expiration dates
SELECT email, password_created_at, password_expires_at, 
       password_change_required, failed_login_attempts
FROM "user" 
WHERE email = 'test_phone@example.com';

-- Check password history
SELECT ph.created_at, u.email
FROM password_history ph
JOIN "user" u ON ph.user_id = u.id
ORDER BY ph.created_at DESC;
```

## 🎯 Quick Demo Script

### Set Up Test Scenario
```python
# In Python shell or script
from blueprint.models import User, db
import datetime

# Find test user
user = User.query.filter_by(email="test_phone@example.com").first()

# Expire password for testing
user.password_expires_at = datetime.datetime.utcnow() - datetime.timedelta(days=1)
db.session.commit()

# Or lock account for testing
user.failed_login_attempts = 5
user.account_locked_until = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
db.session.commit()
```

## ✅ Expected Behaviors

### Successful Tests
- ✅ Strong passwords accepted
- ✅ Weak passwords rejected with clear feedback
- ✅ Password history prevents reuse
- ✅ Account lockout after 5 failed attempts
- ✅ Expired passwords force change
- ✅ Password expiration warnings shown
- ✅ Real-time validation works

### Error Handling
- ✅ Clear error messages for failed validation
- ✅ Graceful handling of expired passwords
- ✅ Proper redirect flows for security requirements
- ✅ User-friendly feedback for all scenarios

## 🚀 Quick Verification Checklist

- [ ] Password policy page loads correctly
- [ ] Password change form validates requirements
- [ ] Strong passwords are accepted
- [ ] Weak passwords are rejected
- [ ] Password history prevents reuse
- [ ] Failed logins are tracked and limited
- [ ] Account lockout works after 5 attempts
- [ ] Expired passwords force change
- [ ] Expiration warnings are shown
- [ ] Real-time validation works properly

## 🔧 Troubleshooting

### Common Issues
1. **Page not found**: Ensure Flask app is running
2. **Database errors**: Check migration completed successfully
3. **Permission errors**: Verify user permissions
4. **Template errors**: Check template files exist

### Reset Test Data
```bash
# Reset user for testing
python -c "
from blueprint.models import User, db
from flask import Flask
import os
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
from extensions import db
db.init_app(app)
with app.app_context():
    user = User.query.filter_by(email='test_phone@example.com').first()
    if user:
        user.failed_login_attempts = 0
        user.account_locked_until = None
        user.password_change_required = False
        db.session.commit()
        print('User reset for testing')
"
```

---

## 🎉 Testing Complete!

If all tests pass, your Password History & Expiration system is working correctly and ready for production use!
