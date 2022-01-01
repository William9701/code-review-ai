-- Initial database setup script
-- This file is run when the PostgreSQL container is first created

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search optimization

-- Create custom types
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'analysis_status') THEN
        CREATE TYPE analysis_status AS ENUM ('pending', 'in_progress', 'completed', 'failed', 'cancelled');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'issue_severity') THEN
        CREATE TYPE issue_severity AS ENUM ('critical', 'high', 'medium', 'low', 'info');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'issue_category') THEN
        CREATE TYPE issue_category AS ENUM ('security', 'performance', 'code_quality', 'best_practices', 'maintainability');
    END IF;
END $$;

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE codereview TO codereview;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO codereview;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO codereview;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO codereview;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO codereview;
