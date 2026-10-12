-- Roles for the opportunities database. Locally a superuser runs this; on Neon
-- `opportunities-db provision` creates the same roles through the migrator.
--
-- opportunities_migrator  owns the schema and runs migrations only.
-- opportunities_api       the API at runtime: no superuser, no BYPASSRLS, owns nothing.
-- opportunities_publisher sweeps and marks the outbox across workspaces; nothing else.

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'opportunities_migrator') THEN
        CREATE ROLE opportunities_migrator LOGIN NOSUPERUSER NOCREATEROLE NOBYPASSRLS;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'opportunities_api') THEN
        CREATE ROLE opportunities_api LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS NOINHERIT;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'opportunities_publisher') THEN
        CREATE ROLE opportunities_publisher LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS NOINHERIT;
    END IF;
END
$$;
