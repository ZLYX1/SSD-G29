# 🌟 Rating & Feedback System - Manual Testing Guide

## 📋 **Testing Overview**

The Rating & Feedback System allows users to rate and provide feedback after completed bookings. This is **Functional Requirement #16**.

---

## **🧪 Phase 1: Automated Testing**

### 1.1 Run the Rating System Test Suite
```bash
python test_rating_system.py
```

**Expected Output:**
- ✅ Rating creation tests
- ✅ Rateable bookings identification  
- ✅ Rating statistics calculation
- ✅ Complete workflow simulation

---

## **🚀 Phase 2: Database Setup**

### 2.1 Ensure Rating Table Exists
```sql
-- Check if rating table exists
SELECT * FROM information_schema.tables WHERE table_name = 'rating';

-- If not exists, create it:
CREATE TABLE rating (
    id SERIAL PRIMARY KEY,
    booking_id INTEGER NOT NULL UNIQUE REFERENCES booking(id),
    reviewer_id INTEGER NOT NULL REFERENCES "user"(id),
    reviewed_id INTEGER NOT NULL REFERENCES "user"(id),
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_rating_booking_id ON rating(booking_id);
CREATE INDEX idx_rating_reviewed_id ON rating(reviewed_id);
```

### 2.2 Create Test Data
```sql
-- Ensure you have test users with completed bookings
-- You can use the seed command:
```
```bash
flask seed
```

---

## **🔗 Phase 3: Flask Application Testing**

### 3.1 Start the Application
```bash
python app.py
```

### 3.2 Test Rating System Routes

#### **Route 1: View Rateable Bookings**
- **URL**: `http://localhost:5000/rating/rateable-bookings`
- **Purpose**: Shows bookings that can be rated
- **Expected**: List of completed bookings without ratings

#### **Route 2: Submit a Rating**
- **URL**: `http://localhost:5000/rating/submit`
- **Method**: POST
- **Data**: 
  ```json
  {
    "booking_id": 1,
    "reviewed_id": 2,
    "rating": 5,
    "feedback": "Excellent service!"
  }
  ```

#### **Route 3: View My Ratings**
- **URL**: `http://localhost:5000/rating/my-ratings`
- **Purpose**: Shows ratings given by current user

#### **Route 4: Get Booking Ratings**
- **URL**: `http://localhost:5000/rating/booking/1/ratings`
- **Purpose**: Shows all ratings for a specific booking

#### **Route 5: Get User Ratings**
- **URL**: `http://localhost:5000/rating/user/2/ratings`
- **Purpose**: Shows all ratings received by a user

---

## **📝 Phase 4: Step-by-Step Manual Testing**

### 4.1 Setup Test Scenario

**Create Test Users:**
1. **Seeker**: `seeker@test.com`
2. **Escort**: `escort@test.com`

**Create Test Booking:**
```python
# Through admin or seed data
booking = Booking(
    seeker_id=1,
    escort_id=2,
    start_time=datetime.now() - timedelta(hours=2),
    end_time=datetime.now() - timedelta(hours=1),
    status='Completed'
)
```

### 4.2 Test Rating Submission

**Step 1: Login as Seeker**
- Navigate to `/auth?mode=login`
- Login with seeker credentials

**Step 2: View Rateable Bookings**
- Go to `/rating/rateable-bookings`
- **Expected**: See the completed booking listed

**Step 3: Submit Rating**
- Click "Rate" button or form
- **Input**:
  - Rating: 4 stars
  - Feedback: "Great service, very professional"
- **Submit form**
- **Expected**: Success message and redirect

**Step 4: Verify Rating**
- Go to `/rating/my-ratings`
- **Expected**: See your submitted rating
- Check escort's profile
- **Expected**: Rating appears on their profile

### 4.3 Test Rating Restrictions

**Test 1: Prevent Duplicate Ratings**
- Try to rate the same booking again
- **Expected**: Error message "You have already rated this booking"

**Test 2: Only Rate Completed Bookings**
- Try to rate a pending/confirmed booking
- **Expected**: Booking not visible in rateable list

**Test 3: Rating Validation**
- Try to submit rating with 0 stars
- **Expected**: Validation error
- Try to submit rating with 6 stars
- **Expected**: Validation error

---

## **📊 Phase 5: Rating Statistics Testing**

### 5.1 Create Multiple Ratings
Create several ratings for the same escort:
- Rating 1: 5 stars
- Rating 2: 4 stars  
- Rating 3: 5 stars

### 5.2 Test Average Calculation
- View escort's profile
- **Expected**: Average rating ≈ 4.7/5.0
- **Expected**: Show total number of ratings

### 5.3 Test Rating Display
- **Profile Page**: Shows average rating prominently
- **Browse Page**: Shows ratings in escort list
- **Booking History**: Shows if booking was rated

---

## **🎯 Phase 6: UI/UX Testing**

### 6.1 Rating Form Interface
**Test Elements:**
- ⭐ Star rating selector (1-5 stars)
- 📝 Feedback text area
- ✅ Submit button
- ❌ Cancel button

**Test Interactions:**
- Click stars to select rating
- Hover effects on stars
- Character limit on feedback
- Form validation messages

### 6.2 Rating Display Interface
**Test Elements:**
- ⭐ Star display (filled/empty)
- 📅 Rating date
- 👤 Reviewer name (or anonymous)
- 💬 Feedback text
- 📊 Average rating calculation

---

## **🔒 Phase 7: Security Testing**

### 7.1 Authorization Tests
**Test 1: Only Rate Own Bookings**
- Try to rate booking you weren't part of
- **Expected**: Access denied

**Test 2: CSRF Protection**
- Submit rating form without CSRF token
- **Expected**: CSRF error

**Test 3: Authentication Required**
- Access rating routes without login
- **Expected**: Redirect to login

### 7.2 Data Validation
**Test Input Sanitization:**
- Submit XSS attempt in feedback: `<script>alert('xss')</script>`
- **Expected**: Script tags escaped/removed
- Submit SQL injection in rating: `'; DROP TABLE rating; --`
- **Expected**: Query safely parameterized

---

## **✅ Test Checklist**

### **Core Functionality:**
- [ ] Users can view rateable bookings
- [ ] Users can submit ratings (1-5 stars + feedback)
- [ ] Ratings are stored correctly in database
- [ ] Average ratings calculated properly
- [ ] Ratings display on profiles
- [ ] Prevent duplicate ratings per booking

### **Business Logic:**
- [ ] Only completed bookings can be rated
- [ ] Only booking participants can rate
- [ ] Ratings must be 1-5 stars
- [ ] Feedback is optional but recommended

### **Security:**
- [ ] CSRF protection enabled
- [ ] Authentication required
- [ ] Input validation and sanitization
- [ ] Authorization checks (own bookings only)

### **User Experience:**
- [ ] Intuitive star rating interface
- [ ] Clear feedback forms
- [ ] Proper success/error messages
- [ ] Responsive design

---

## **🎊 Success Criteria**

**The Rating & Feedback System is working correctly when:**

1. ✅ **Users can rate completed bookings** with 1-5 stars and feedback
2. ✅ **Ratings are prevented** for pending/future/rejected bookings
3. ✅ **No duplicate ratings** allowed per booking
4. ✅ **Average ratings calculated** and displayed on profiles
5. ✅ **Rating statistics** show on user profiles and browse pages
6. ✅ **Security measures** prevent unauthorized access and malicious input
7. ✅ **UI is intuitive** with star selectors and clear feedback forms

---

## **🐛 Common Issues & Solutions**

### **Issue: "Rating routes not found (404)"**
**Solution**: Ensure rating blueprint is registered in app.py:
```python
from blueprint.rating import rating_bp
app.register_blueprint(rating_bp, url_prefix='/rating')
```

### **Issue: "No rateable bookings shown"**
**Solution**: 
1. Create completed bookings with past end_time
2. Ensure booking status is 'Completed'
3. Verify no existing rating for the booking

### **Issue: "Rating not saving to database"**
**Solution**:
1. Check database migration was applied
2. Verify foreign key constraints
3. Check rating validation (1-5 stars)

### **Issue: "Average rating not updating"**
**Solution**: Check if rating statistics query is correct and cache is cleared

---

## **📈 Next Steps After Testing**

1. **Performance**: Add indexes on rating queries
2. **Features**: Add rating filters and sorting
3. **Analytics**: Track rating trends and patterns
4. **Moderation**: Add admin tools to manage inappropriate ratings
