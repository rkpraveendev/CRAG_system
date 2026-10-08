-- Phase 1, Section 1: extension and table definitions only.
-- Run as one transaction so an error cannot leave a partial schema.
begin;

create extension if not exists vector;

create table public.collections (
  id text primary key,
  name text not null,
  description text,
  created_at timestamptz not null default now()
);

create table public.documents (
  id uuid primary key default gen_random_uuid(),
  collection_id text not null references public.collections(id),
  title text not null,
  source_url text,
  license_label text not null,
  sha256 text not null unique,
  page_count int,
  ingested_at timestamptz not null default now(),
  ingested_by uuid references auth.users(id)
);

create table public.document_chunks (
  id uuid primary key default gen_random_uuid(),
  document_id uuid not null references public.documents(id) on delete cascade,
  collection_id text not null references public.collections(id),
  content text not null,
  page_number int,
  section_heading text,
  chunk_index int not null,
  embedding public.vector(1024) not null,
  created_at timestamptz not null default now()
);

create table public.grading_log (
  id uuid primary key default gen_random_uuid(),
  run_id text not null,
  query text not null,
  chunk_id uuid references public.document_chunks(id),
  llm_label boolean not null,
  llm_model text not null,
  created_at timestamptz not null default now()
);

commit;

