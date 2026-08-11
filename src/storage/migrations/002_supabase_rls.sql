-- Optional Row Level Security for Supabase multi-tenant access
-- Run in Supabase SQL Editor after 001_initial_schema.sql
-- Requires Supabase Auth: map auth.users.id to users.id or use a custom claim

ALTER TABLE shops ENABLE ROW LEVEL SECURITY;
ALTER TABLE cameras ENABLE ROW LEVEL SECURITY;
ALTER TABLE tracking_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE dwell_records ENABLE ROW LEVEL SECURITY;

-- Customers see only their own shops
CREATE POLICY shops_owner_select ON shops
    FOR SELECT
    USING (owner_id = (SELECT id FROM users WHERE email = auth.jwt() ->> 'email'));

-- Service role (pipeline) bypasses RLS when using the service_role connection string
