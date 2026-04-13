-- Migration 001: make user_id nullable on scans
-- Needed for Day 2 — scans created by the API before auth is wired up.
-- Run in: Supabase Dashboard → SQL Editor

ALTER TABLE scans ALTER COLUMN user_id DROP NOT NULL;
