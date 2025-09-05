
-- 1) PROFILES: Remove overly permissive policy and replace with service-role-only policy
DROP POLICY IF EXISTS "service_all_profiles" ON public.profiles;

-- Service role can manage profiles (optional because service role bypasses RLS, but safe to include)
CREATE POLICY "service_role_manage_profiles"
  ON public.profiles
  FOR ALL
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');

-- 2) DETECTIONS: Restrict reads to authenticated users (remove public read)
DROP POLICY IF EXISTS "Allow all select" ON public.detections;

CREATE POLICY "Authenticated can view detections"
  ON public.detections
  FOR SELECT
  USING (auth.uid() IS NOT NULL);

-- 3) ERROR LOGS: Enable RLS, admins can read, service role can insert
ALTER TABLE public.error_logs ENABLE ROW LEVEL SECURITY;

-- Admins can read
DROP POLICY IF EXISTS "Admins can view error logs" ON public.error_logs;
CREATE POLICY "Admins can view error logs"
  ON public.error_logs
  FOR SELECT
  USING (COALESCE((auth.jwt() ->> 'role'), '') = 'admin');

-- Service role can insert
DROP POLICY IF EXISTS "Service role can insert error logs" ON public.error_logs;
CREATE POLICY "Service role can insert error logs"
  ON public.error_logs
  FOR INSERT
  WITH CHECK (auth.role() = 'service_role');

-- 4) USERS: Enable RLS, admins can read, service role can manage
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Admins can view users" ON public.users;
CREATE POLICY "Admins can view users"
  ON public.users
  FOR SELECT
  USING (COALESCE((auth.jwt() ->> 'role'), '') = 'admin');

DROP POLICY IF EXISTS "Service role can manage users" ON public.users;
CREATE POLICY "Service role can manage users"
  ON public.users
  FOR ALL
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');

-- 5) SECURITY AUDIT LOG: Allow service role to insert (admins can read already)
DROP POLICY IF EXISTS "Service role can insert audit logs" ON public.security_audit_log;
CREATE POLICY "Service role can insert audit logs"
  ON public.security_audit_log
  FOR INSERT
  WITH CHECK (auth.role() = 'service_role');

-- 6) VISITORS: Anonymize IP on insert/update using existing hash_ip(ip_address text)
-- Create a trigger function to hash and null the IP field
CREATE OR REPLACE FUNCTION public.visitors_anonymize()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_catalog
AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    IF NEW.ip IS NOT NULL THEN
      NEW.ip_hash := public.hash_ip(NEW.ip);
      NEW.ip := NULL;
    END IF;
  ELSIF TG_OP = 'UPDATE' THEN
    IF NEW.ip IS DISTINCT FROM OLD.ip AND NEW.ip IS NOT NULL THEN
      NEW.ip_hash := public.hash_ip(NEW.ip);
      NEW.ip := NULL;
    END IF;
  END IF;
  RETURN NEW;
END;
$$;

-- Attach triggers (idempotent drops first)
DROP TRIGGER IF EXISTS visitors_anonymize_bi ON public.visitors;
DROP TRIGGER IF EXISTS visitors_anonymize_bu ON public.visitors;

CREATE TRIGGER visitors_anonymize_bi
  BEFORE INSERT ON public.visitors
  FOR EACH ROW
  EXECUTE FUNCTION public.visitors_anonymize();

CREATE TRIGGER visitors_anonymize_bu
  BEFORE UPDATE ON public.visitors
  FOR EACH ROW
  EXECUTE FUNCTION public.visitors_anonymize();

-- 7) PROFILES: Allow 'live' in mode; standardize email to citext
CREATE EXTENSION IF NOT EXISTS citext WITH SCHEMA public;

-- Mode constraint: allow demo, broker, live
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'profiles_mode_check'
      AND conrelid = 'public.profiles'::regclass
  ) THEN
    ALTER TABLE public.profiles DROP CONSTRAINT profiles_mode_check;
  END IF;
END $$;

ALTER TABLE public.profiles
ADD CONSTRAINT profiles_mode_check
CHECK (mode IN ('demo', 'broker', 'live'));

-- Convert email to citext for case-insensitive handling
ALTER TABLE public.profiles
ALTER COLUMN email TYPE citext USING email::text::citext;
