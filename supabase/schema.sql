-- ============================================================
-- CloudGuard — Supabase Schema
-- Run this in: Supabase Dashboard → SQL Editor
-- ============================================================

-- Enable UUID generation
create extension if not exists "pgcrypto";

-- ============================================================
-- WAITLIST
-- ============================================================
create table if not exists waitlist (
  id          uuid primary key default gen_random_uuid(),
  email       text unique not null,
  created_at  timestamptz default now()
);

-- ============================================================
-- USERS
-- Synced from Clerk via webhook (Day 2+).
-- clerk_id is the Clerk user ID (e.g. user_2abc...)
-- ============================================================
create table if not exists users (
  id          uuid primary key default gen_random_uuid(),
  clerk_id    text unique not null,
  email       text not null,
  plan        text not null default 'free' check (plan in ('free', 'pro')),
  created_at  timestamptz default now(),
  updated_at  timestamptz default now()
);

-- ============================================================
-- SCANS
-- One row per triggered scan job.
-- ============================================================
create table if not exists scans (
  id            uuid primary key default gen_random_uuid(),
  user_id       uuid not null references users(id) on delete cascade,
  provider      text not null check (provider in ('aws', 'azure', 'gcp')),
  status        text not null default 'pending'
                  check (status in ('pending', 'running', 'completed', 'failed')),
  score         integer check (score between 0 and 100),
  grade         text check (grade in ('A', 'B', 'C', 'D', 'F')),
  error_msg     text,
  created_at    timestamptz default now(),
  completed_at  timestamptz
);

-- ============================================================
-- FINDINGS
-- Individual security findings from a scan.
-- ============================================================
create table if not exists findings (
  id                  uuid primary key default gen_random_uuid(),
  scan_id             uuid not null references scans(id) on delete cascade,
  resource_id         text,
  resource_type       text,
  region              text,
  severity            text not null check (severity in ('critical', 'high', 'medium', 'low', 'info')),
  title               text not null,
  description         text,
  -- Cached AI remediation (JSON: { description, cli_command, console_steps, risk_level })
  remediation_cached  jsonb,
  created_at          timestamptz default now()
);

-- ============================================================
-- ROW LEVEL SECURITY
-- Users can only see their own data.
-- ============================================================

alter table users    enable row level security;
alter table scans    enable row level security;
alter table findings enable row level security;

-- users: each user sees only their own row
create policy "users_self_select" on users
  for select using (auth.uid()::text = clerk_id);

create policy "users_self_update" on users
  for update using (auth.uid()::text = clerk_id);

-- scans: users see only their own scans
create policy "scans_owner_select" on scans
  for select using (
    user_id = (select id from users where clerk_id = auth.uid()::text limit 1)
  );

create policy "scans_owner_insert" on scans
  for insert with check (
    user_id = (select id from users where clerk_id = auth.uid()::text limit 1)
  );

-- findings: users see findings for their own scans
create policy "findings_owner_select" on findings
  for select using (
    scan_id in (
      select s.id from scans s
      join users u on u.id = s.user_id
      where u.clerk_id = auth.uid()::text
    )
  );

-- waitlist: anyone can insert (no auth needed), but cannot read
create policy "waitlist_insert_anon" on waitlist
  for insert with check (true);

alter table waitlist enable row level security;

-- ============================================================
-- INDEXES
-- ============================================================
create index if not exists idx_scans_user_id    on scans(user_id);
create index if not exists idx_scans_status     on scans(status);
create index if not exists idx_findings_scan_id on findings(scan_id);
create index if not exists idx_findings_severity on findings(severity);
