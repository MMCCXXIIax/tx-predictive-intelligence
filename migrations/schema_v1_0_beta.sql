-- Enable UUID generation
create extension if not exists "pgcrypto";

-- 1) profiles: used by /api/save-profile (id must be PK for ON CONFLICT)
create table if not exists public.profiles (
  id uuid primary key default gen_random_uuid(),
  name text,
  email text,
  mode text not null default 'demo',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint profiles_mode_check check (mode in ('demo','live'))
);

-- Optional, if you want fast lookup by email (not unique to avoid conflicts)
create index if not exists idx_profiles_email on public.profiles (email);

-- Keep updated_at current on updates
create or replace function public.set_updated_at()
returns trigger
language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists trg_profiles_updated_at on public.profiles;
create trigger trg_profiles_updated_at
before update on public.profiles
for each row execute function public.set_updated_at();

-- 2) visitors: tracked by your dashboard + refresh interval
create table if not exists public.visitors (
  id uuid primary key,
  first_seen timestamptz not null default now(),
  last_seen timestamptz not null default now(),
  user_agent text,
  ip text,
  visit_count int not null default 1,
  refresh_interval int not null default 120
);

create index if not exists idx_visitors_last_seen on public.visitors (last_seen);

-- 3) app_state: used to persist last_scan etc.
create table if not exists public.app_state (
  key text primary key,
  value jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

-- 4) detections: your pattern hits and outcomes
create table if not exists public.detections (
  id uuid primary key default gen_random_uuid(),
  timestamp timestamptz not null default now(),
  symbol text not null,
  pattern text not null,
  confidence double precision,
  price numeric(18,8),
  outcome text,
  verified boolean not null default false
);

-- Helpful indexes for dashboards and lookups
create index if not exists idx_detections_timestamp on public.detections (timestamp);
create index if not exists idx_detections_symbol_time on public.detections (symbol, timestamp desc);

-- 5) error_logs: referenced by /api/debug for AlphaVantage counts
create table if not exists public.error_logs (
  id bigserial primary key,
  source text not null,
  message text,
  created_at timestamptz not null default now()
);

create index if not exists idx_error_logs_source on public.error_logs (source);
create index if not exists idx_error_logs_created_at on public.error_logs (created_at);

-- Optional seed for app_state if you want a defined starting row
insert into public.app_state (key, value)
values ('last_scan', '{}'::jsonb)
on conflict (key) do nothing;


-- Patch detections table to have UUID default
alter table public.detections
    alter column id set default gen_random_uuid(),
    alter column timestamp set default now();

-- Safety: fill in any old NULL ids with UUIDs (in case of existing bad rows)
update public.detections
set id = gen_random_uuid()
where id is null;

update public.detections
set timestamp = now()
where timestamp is null;
