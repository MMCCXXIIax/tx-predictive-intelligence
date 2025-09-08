-- 0) Enable pgcrypto for digest()
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS citext WITH SCHEMA public;

-- 1) PROFILES: Remove any existing policy and recreate
DROP POLICY IF EXISTS "service_all_profiles" ON public.profiles;
DROP POLICY IF EXISTS "service_role_manage_profiles" ON public.profiles;

CREATE POLICY "service_role_manage_profiles"
  ON public.profiles
  FOR ALL
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');

-- 2) DETECTIONS: Restrict reads to authenticated users
DROP POLICY IF EXISTS "Allow all select" ON public.detections;
DROP POLICY IF EXISTS "Authenticated can view detections" ON public.detections;

CREATE POLICY "Authenticated can view detections"
  ON public.detections
  FOR SELECT
  USING (auth.uid() IS NOT NULL);

-- 3) ERROR LOGS: Enable RLS, admins can read, service role can insert
ALTER TABLE public.error_logs ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Admins can view error logs" ON public.error_logs;
CREATE POLICY "Admins can view error logs"
  ON public.error_logs
  FOR SELECT
  USING (COALESCE((auth.jwt() ->> 'role'), '') = 'admin');

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

-- 5) SECURITY AUDIT LOG: Allow service role to insert
DROP POLICY IF EXISTS "Service role can insert audit logs" ON public.security_audit_log;
CREATE POLICY "Service role can insert audit logs"
  ON public.security_audit_log
  FOR INSERT
  WITH CHECK (auth.role() = 'service_role');

-- 6) VISITORS: Anonymize IP on insert/update
CREATE OR REPLACE FUNCTION public.hash_ip(ip_address text)
RETURNS text AS $$
BEGIN
  BEGIN
    PERFORM digest('test', 'sha256');
    RETURN encode(digest(ip_address || 'salt_for_privacy_protection', 'sha256'), 'hex');
  EXCEPTION
    WHEN undefined_function THEN
      RETURN md5(ip_address || 'salt_for_privacy_protection');
  END;
END;
$$ LANGUAGE plpgsql;

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
CHECK (mode IN ('demo', 'live'));

ALTER TABLE public.profiles
ALTER COLUMN email TYPE citext USING email::text::citext;

-- 8) TEST DATA: Seed into BOTH auth.users and public.users before profiles/visitors
INSERT INTO auth.users (id, email)
VALUES ('56047c1b-2f56-4a18-b215-6a19a0dcebda', 'test@example.com')
ON CONFLICT (id) DO NOTHING;

INSERT INTO public.users (id)
VALUES ('56047c1b-2f56-4a18-b215-6a19a0dcebda')
ON CONFLICT (id) DO NOTHING;

INSERT INTO public.profiles (id, username, name, email, mode)
VALUES (
  '56047c1b-2f56-4a18-b215-6a19a0dcebda',
  'testuser',
  'Test User',
  'test@example.com',
  'live'
)
ON CONFLICT (id) DO NOTHING;

INSERT INTO public.visitors (id, ip, name, email, mode)
VALUES (
  '56047c1b-2f56-4a18-b215-6a19a0dcebda',
  '192.168.1.1',
  'Test User',
  'test@example.com',
  'live'
)
ON CONFLICT (id) DO NOTHING;

CREATE EXTENSION IF NOT EXISTS pgcrypto;


CREATE OR REPLACE FUNCTION hash_ip(ip_address TEXT)
RETURNS TEXT AS $$
BEGIN
    IF ip_address IS NULL THEN
        RETURN NULL;
    END IF;
    RETURN encode(digest(ip_address || 'salt_for_privacy_protection', 'sha256'), 'hex');
END;
$$ LANGUAGE plpgsql IMMUTABLE;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE OR REPLACE FUNCTION public.hash_ip(ip_address TEXT)
RETURNS TEXT AS $$
BEGIN
    IF ip_address IS NULL THEN
        RETURN NULL;
    END IF;
    RETURN encode(digest(ip_address || 'salt_for_privacy_protection', 'sha256'), 'hex');
END;
$$ LANGUAGE plpgsql IMMUTABLE;


