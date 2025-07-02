-- Enhanced Report System Migration
-- This migration enhances the existing report table with comprehensive reporting features

-- First, check if the report table exists and has the old structure
-- If it exists with old columns, we'll modify it; if not, we'll create it fresh

DO $$
BEGIN
    -- Check if table exists with old structure
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'report') THEN
        -- Update existing table
        
        -- Add new columns if they don't exist
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'report' AND column_name = 'report_type') THEN
            ALTER TABLE report ADD COLUMN report_type VARCHAR(50) NOT NULL DEFAULT 'other';
        END IF;
        
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'report' AND column_name = 'title') THEN
            ALTER TABLE report ADD COLUMN title VARCHAR(200) NOT NULL DEFAULT 'Report';
        END IF;
        
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'report' AND column_name = 'description') THEN
            ALTER TABLE report ADD COLUMN description TEXT;
            -- Migrate old 'reason' to 'description'
            UPDATE report SET description = reason WHERE description IS NULL;
            ALTER TABLE report ALTER COLUMN description SET NOT NULL;
        END IF;
        
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'report' AND column_name = 'evidence_urls') THEN
            ALTER TABLE report ADD COLUMN evidence_urls TEXT;
        END IF;
        
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'report' AND column_name = 'severity') THEN
            ALTER TABLE report ADD COLUMN severity VARCHAR(20) NOT NULL DEFAULT 'Medium';
        END IF;
        
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'report' AND column_name = 'admin_notes') THEN
            ALTER TABLE report ADD COLUMN admin_notes TEXT;
        END IF;
        
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'report' AND column_name = 'resolution') THEN
            ALTER TABLE report ADD COLUMN resolution TEXT;
        END IF;
        
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'report' AND column_name = 'created_at') THEN
            ALTER TABLE report ADD COLUMN created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP;
        END IF;
        
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'report' AND column_name = 'updated_at') THEN
            ALTER TABLE report ADD COLUMN updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP;
        END IF;
        
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'report' AND column_name = 'resolved_at') THEN
            ALTER TABLE report ADD COLUMN resolved_at TIMESTAMP WITHOUT TIME ZONE;
        END IF;
        
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'report' AND column_name = 'assigned_admin_id') THEN
            ALTER TABLE report ADD COLUMN assigned_admin_id INTEGER REFERENCES "user"(id);
        END IF;
        
        -- Update status column to accommodate new statuses
        IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'report' AND column_name = 'status') THEN
            -- Check if the column is large enough for our new status values
            ALTER TABLE report ALTER COLUMN status TYPE VARCHAR(30);
        END IF;
        
        -- Drop old reason column if description exists
        IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'report' AND column_name = 'reason') 
           AND EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'report' AND column_name = 'description') THEN
            ALTER TABLE report DROP COLUMN reason;
        END IF;
        
    ELSE
        -- Create new table with full structure
        CREATE TABLE report (
            id SERIAL PRIMARY KEY,
            reporter_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
            reported_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
            
            -- Enhanced reporting fields
            report_type VARCHAR(50) NOT NULL,
            title VARCHAR(200) NOT NULL,
            description TEXT NOT NULL,
            evidence_urls TEXT,
            severity VARCHAR(20) NOT NULL DEFAULT 'Medium',
            
            -- Status tracking
            status VARCHAR(30) NOT NULL DEFAULT 'Pending Review',
            admin_notes TEXT,
            resolution TEXT,
            
            -- Timestamps
            created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
            updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP WITHOUT TIME ZONE,
            
            -- Admin who handled the report
            assigned_admin_id INTEGER REFERENCES "user"(id)
        );
    END IF;
END $$;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_report_reporter_id ON report(reporter_id);
CREATE INDEX IF NOT EXISTS idx_report_reported_id ON report(reported_id);
CREATE INDEX IF NOT EXISTS idx_report_status ON report(status);
CREATE INDEX IF NOT EXISTS idx_report_severity ON report(severity);
CREATE INDEX IF NOT EXISTS idx_report_type ON report(report_type);
CREATE INDEX IF NOT EXISTS idx_report_created_at ON report(created_at);
CREATE INDEX IF NOT EXISTS idx_report_assigned_admin ON report(assigned_admin_id);

-- Add constraints
DO $$
BEGIN
    -- Add check constraint for severity
    IF NOT EXISTS (SELECT 1 FROM information_schema.check_constraints WHERE constraint_name = 'report_severity_check') THEN
        ALTER TABLE report ADD CONSTRAINT report_severity_check 
        CHECK (severity IN ('Low', 'Medium', 'High', 'Critical'));
    END IF;
    
    -- Add check constraint for status
    IF NOT EXISTS (SELECT 1 FROM information_schema.check_constraints WHERE constraint_name = 'report_status_check') THEN
        ALTER TABLE report ADD CONSTRAINT report_status_check 
        CHECK (status IN ('Pending Review', 'Under Investigation', 'Resolved', 'Dismissed'));
    END IF;
    
    -- Add check constraint for report_type
    IF NOT EXISTS (SELECT 1 FROM information_schema.check_constraints WHERE constraint_name = 'report_type_check') THEN
        ALTER TABLE report ADD CONSTRAINT report_type_check 
        CHECK (report_type IN ('inappropriate_behavior', 'harassment', 'fraud', 'fake_profile', 
                              'violence_threats', 'spam', 'underage', 'identity_theft', 
                              'privacy_violation', 'other'));
    END IF;
END $$;

-- Add trigger for updated_at timestamp
CREATE OR REPLACE FUNCTION update_report_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_report_updated_at ON report;
CREATE TRIGGER trigger_update_report_updated_at
    BEFORE UPDATE ON report
    FOR EACH ROW
    EXECUTE FUNCTION update_report_updated_at();

-- Add comments for documentation
COMMENT ON TABLE report IS 'Enhanced user reporting system for safety and moderation';
COMMENT ON COLUMN report.reporter_id IS 'ID of the user making the report';
COMMENT ON COLUMN report.reported_id IS 'ID of the user being reported';
COMMENT ON COLUMN report.report_type IS 'Category of the report (harassment, fraud, etc.)';
COMMENT ON COLUMN report.title IS 'Brief title describing the issue';
COMMENT ON COLUMN report.description IS 'Detailed description of the incident';
COMMENT ON COLUMN report.evidence_urls IS 'JSON array of evidence URLs/screenshots';
COMMENT ON COLUMN report.severity IS 'Severity level: Low, Medium, High, Critical';
COMMENT ON COLUMN report.status IS 'Current status of the report investigation';
COMMENT ON COLUMN report.admin_notes IS 'Internal notes for investigation team';
COMMENT ON COLUMN report.resolution IS 'Final resolution details';
COMMENT ON COLUMN report.assigned_admin_id IS 'Admin assigned to handle this report';

-- Create a view for report statistics
CREATE OR REPLACE VIEW report_statistics AS
SELECT 
    COUNT(*) as total_reports,
    COUNT(CASE WHEN status = 'Pending Review' THEN 1 END) as pending_reports,
    COUNT(CASE WHEN status = 'Under Investigation' THEN 1 END) as under_investigation,
    COUNT(CASE WHEN status = 'Resolved' THEN 1 END) as resolved_reports,
    COUNT(CASE WHEN status = 'Dismissed' THEN 1 END) as dismissed_reports,
    COUNT(CASE WHEN severity = 'Critical' THEN 1 END) as critical_reports,
    COUNT(CASE WHEN severity = 'High' THEN 1 END) as high_reports,
    COUNT(CASE WHEN created_at >= CURRENT_DATE - INTERVAL '7 days' THEN 1 END) as recent_reports
FROM report;

COMMENT ON VIEW report_statistics IS 'Real-time statistics for the report management dashboard';

-- Verify the table structure
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default,
    character_maximum_length
FROM information_schema.columns 
WHERE table_name = 'report' 
ORDER BY ordinal_position;
