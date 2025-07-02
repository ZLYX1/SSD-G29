-- Email Verification Migration
-- Add email verification fields to the User table

ALTER TABLE "user" 
ADD COLUMN email_verified BOOLEAN DEFAULT FALSE NOT NULL,
ADD COLUMN email_verification_token VARCHAR(100) UNIQUE,
ADD COLUMN email_verification_token_expires TIMESTAMP;

-- Create an index on the verification token for faster lookups
CREATE INDEX idx_user_verification_token ON "user"(email_verification_token);

-- Comments for clarity
COMMENT ON COLUMN "user".email_verified IS 'Flag indicating if the user has verified their email address';
COMMENT ON COLUMN "user".email_verification_token IS 'Token sent to user for email verification';
COMMENT ON COLUMN "user".email_verification_token_expires IS 'Expiration timestamp for the verification token';
