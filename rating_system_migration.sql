-- Rating System Database Migration
-- Creates the rating table and related indexes

-- Create the rating table
CREATE TABLE IF NOT EXISTS rating (
    id SERIAL PRIMARY KEY,
    booking_id INTEGER NOT NULL UNIQUE,
    reviewer_id INTEGER NOT NULL,
    reviewed_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    CONSTRAINT fk_rating_booking FOREIGN KEY (booking_id) REFERENCES booking(id) ON DELETE CASCADE,
    CONSTRAINT fk_rating_reviewer FOREIGN KEY (reviewer_id) REFERENCES "user"(id) ON DELETE CASCADE,
    CONSTRAINT fk_rating_reviewed FOREIGN KEY (reviewed_id) REFERENCES "user"(id) ON DELETE CASCADE
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_rating_booking_id ON rating(booking_id);
CREATE INDEX IF NOT EXISTS idx_rating_reviewer_id ON rating(reviewer_id);
CREATE INDEX IF NOT EXISTS idx_rating_reviewed_id ON rating(reviewed_id);
CREATE INDEX IF NOT EXISTS idx_rating_created_at ON rating(created_at);

-- Create a composite index for common queries
CREATE INDEX IF NOT EXISTS idx_rating_reviewed_rating ON rating(reviewed_id, rating);

-- Add comments for documentation
COMMENT ON TABLE rating IS 'Stores user ratings and feedback for completed bookings';
COMMENT ON COLUMN rating.booking_id IS 'ID of the booking being rated (unique constraint ensures one rating per booking)';
COMMENT ON COLUMN rating.reviewer_id IS 'ID of the user giving the rating';
COMMENT ON COLUMN rating.reviewed_id IS 'ID of the user being rated';
COMMENT ON COLUMN rating.rating IS 'Rating value from 1-5 stars';
COMMENT ON COLUMN rating.feedback IS 'Optional text feedback from the reviewer';
COMMENT ON COLUMN rating.created_at IS 'Timestamp when the rating was submitted';

-- Create a view for easy rating statistics
CREATE OR REPLACE VIEW rating_stats AS
SELECT 
    reviewed_id,
    COUNT(*) as total_ratings,
    AVG(rating) as average_rating,
    MIN(rating) as min_rating,
    MAX(rating) as max_rating,
    COUNT(CASE WHEN rating = 5 THEN 1 END) as five_star_count,
    COUNT(CASE WHEN rating = 4 THEN 1 END) as four_star_count,
    COUNT(CASE WHEN rating = 3 THEN 1 END) as three_star_count,
    COUNT(CASE WHEN rating = 2 THEN 1 END) as two_star_count,
    COUNT(CASE WHEN rating = 1 THEN 1 END) as one_star_count
FROM rating 
GROUP BY reviewed_id;

COMMENT ON VIEW rating_stats IS 'Aggregated rating statistics for each user';

-- Insert some sample data for testing (optional)
-- Uncomment the following lines if you want sample data

/*
-- Sample ratings (requires existing users and bookings)
INSERT INTO rating (booking_id, reviewer_id, reviewed_id, rating, feedback) VALUES
(1, 1, 2, 5, 'Excellent service, very professional and punctual!'),
(2, 3, 2, 4, 'Good experience overall, would recommend.'),
(3, 1, 4, 3, 'Average service, could be better.');
*/

-- Verify the table was created successfully
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default,
    character_maximum_length
FROM information_schema.columns 
WHERE table_name = 'rating' 
ORDER BY ordinal_position;
