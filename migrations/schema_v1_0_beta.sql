-- ========================
-- DROP TABLES IF THEY EXIST
-- ========================
DROP TABLE IF EXISTS public.visitors CASCADE;
DROP TABLE IF EXISTS public.detections CASCADE;
DROP TABLE IF EXISTS public.app_state CASCADE;
DROP TABLE IF EXISTS public.error_logs CASCADE;

-- ========================
-- CREATE TABLES
-- ========================

-- 1. visitors: linked to Supabase Auth users
CREATE TABLE public.visitors (
  id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  first_seen timestamptz NOT NULL DEFAULT now(),
  last_seen timestamptz NOT NULL DEFAULT now(),
  user_agent text,
  ip text,
  visit_count int NOT NULL DEFAULT 1,
  refresh_interval int NOT NULL DEFAULT 120,
  name text,
  email text,
  mode text CHECK (mode IN ('demo', 'live'))
);

CREATE INDEX idx_visitors_last_seen ON public.visitors (last_seen);
CREATE INDEX idx_visitors_email ON public.visitors (email);

-- 2. app_state: to persist last_scan etc.
CREATE TABLE public.app_state (
  key text PRIMARY KEY,
  value jsonb NOT NULL DEFAULT '{}'::jsonb,
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- 3. detections: pattern hits and outcomes
CREATE TABLE public.detections (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  timestamp timestamptz NOT NULL DEFAULT now(),
  symbol text NOT NULL,
  pattern text NOT NULL,
  confidence double precision,
  price numeric(18,8),
  outcome text,
  verified boolean NOT NULL DEFAULT false
);

CREATE INDEX idx_detections_timestamp ON public.detections (timestamp);
CREATE INDEX idx_detections_symbol_time ON public.detections (symbol, timestamp DESC);

-- 4. error_logs: for debug/monitoring
CREATE TABLE public.error_logs (
  id bigserial PRIMARY KEY,
  source text NOT NULL,
  message text,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_error_logs_source ON public.error_logs (source);
CREATE INDEX idx_error_logs_created_at ON public.error_logs (created_at);

-- ========================
-- OPTIONAL: SEED DATA
-- ========================
INSERT INTO public.app_state (key, value)
VALUES ('last_scan', '{}'::jsonb)
ON CONFLICT (key) DO NOTHING;

-- ========================
-- RLS POLICIES FOR visitors
-- ========================
ALTER TABLE public.visitors ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow self select" ON public.visitors
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Allow self update" ON public.visitors
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Allow self insert" ON public.visitors
    FOR INSERT WITH CHECK (auth.uid() = id);

CREATE POLICY "Allow self delete" ON public.visitors
    FOR DELETE USING (auth.uid() = id);

-- ========================
-- RLS POLICIES FOR detections
-- ========================
ALTER TABLE public.detections ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all select" ON public.detections
    FOR SELECT USING (true);

-- ========================
-- RLS POLICIES FOR app_state & error_logs
-- ========================
ALTER TABLE public.app_state ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.error_logs ENABLE ROW LEVEL SECURITY;
