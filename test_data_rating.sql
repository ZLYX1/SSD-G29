-- Test Data for Rating System Demo
-- This script creates sample users and bookings to demonstrate the rating system

-- Clear existing test data (optional)
DELETE FROM rating WHERE id > 0;
DELETE FROM booking WHERE id > 100;
DELETE FROM profile WHERE user_id > 100;
DELETE FROM "user" WHERE id > 100;

-- Create test users
INSERT INTO "user" (id, email, password_hash, role, active, gender, email_verified, created_at)
VALUES 
(101, 'escort_alice@example.com', 'scrypt:32768:8:1$example_hash$dummy', 'escort', true, 'female', true, NOW() - INTERVAL '7 days'),
(102, 'escort_bob@example.com', 'scrypt:32768:8:1$example_hash$dummy', 'escort', true, 'male', true, NOW() - INTERVAL '7 days'),
(103, 'seeker_charlie@example.com', 'scrypt:32768:8:1$example_hash$dummy', 'seeker', true, 'male', true, NOW() - INTERVAL '7 days'),
(104, 'seeker_diana@example.com', 'scrypt:32768:8:1$example_hash$dummy', 'seeker', true, 'female', true, NOW() - INTERVAL '7 days'),
(105, 'escort_eve@example.com', 'scrypt:32768:8:1$example_hash$dummy', 'escort', true, 'female', true, NOW() - INTERVAL '7 days');

-- Create profiles for test users
INSERT INTO profile (user_id, name, age, bio, preference)
VALUES 
(101, 'Alice Smith', 25, 'Professional companion with excellent communication skills', 'Professional'),
(102, 'Bob Johnson', 28, 'Friendly and professional escort service', 'Casual'),
(103, 'Charlie Brown', 35, 'Looking for quality companionship', 'Professional'),
(104, 'Diana Wilson', 30, 'Seeking professional escort services', 'Premium'),
(105, 'Eve Davis', 24, 'Premium escort services available', 'Premium');

-- Create completed bookings that can be rated
INSERT INTO booking (id, seeker_id, escort_id, start_time, end_time, status)
VALUES 
(201, 103, 101, NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days' + INTERVAL '2 hours', 'Completed'),
(202, 104, 102, NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days' + INTERVAL '3 hours', 'Completed'),
(203, 103, 105, NOW() - INTERVAL '1 week', NOW() - INTERVAL '1 week' + INTERVAL '3 hours', 'Completed'),
-- Future booking (should not be rateable)
(204, 104, 101, NOW() + INTERVAL '2 days', NOW() + INTERVAL '2 days' + INTERVAL '2 hours', 'Accepted'),
-- Recent booking still not completed
(205, 103, 102, NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day' + INTERVAL '3 hours', 'Accepted');

-- Add one sample rating to show how it works
INSERT INTO rating (booking_id, reviewer_id, reviewed_id, rating, feedback, created_at)
VALUES 
(203, 103, 105, 5, 'Exceptional service! Eve was professional, punctual, and provided excellent companionship. Highly recommended!', NOW() - INTERVAL '1 day');

-- Display what we created
SELECT 'Created test users:' as info;
SELECT id, email, role, email_verified FROM "user" WHERE id > 100 ORDER BY id;

SELECT 'Created completed bookings (rateable):' as info;
SELECT b.id, u1.email as seeker, u2.email as escort, b.start_time, b.status
FROM booking b
JOIN "user" u1 ON b.seeker_id = u1.id
JOIN "user" u2 ON b.escort_id = u2.id
WHERE b.id > 200 AND b.status = 'Completed'
ORDER BY b.id;

SELECT 'Created sample rating:' as info;
SELECT r.id, b.id as booking_id, u1.email as reviewer, u2.email as reviewed, r.rating, r.feedback
FROM rating r
JOIN booking b ON r.booking_id = b.id
JOIN "user" u1 ON r.reviewer_id = u1.id
JOIN "user" u2 ON r.reviewed_id = u2.id
ORDER BY r.id;
