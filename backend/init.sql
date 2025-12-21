"""SQL initialization script for PostgreSQL."""

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create users with proper permissions
CREATE USER IF NOT EXISTS reception_user WITH PASSWORD 'reception_password';
GRANT ALL PRIVILEGES ON DATABASE reception_agent TO reception_user;
