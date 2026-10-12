# Agentic CRAG System

Phase 1 provides a Supabase PostgreSQL schema for documents and vector chunks,
Python clients for authenticated reads and trusted backend writes, and a daily
GitHub Actions keepalive. The ingestion pipeline is not implemented yet.

## Requirements

- Python 3.12 or newer and [uv](https://docs.astral.sh/uv/).
- A Supabase project with the SQL Editor and Authentication available.

Install the locked Python dependencies from the repository root:

```powershell
uv sync --locked
```

## Configure credentials

Create a local `.env` file in the repository root with these variable names and
your own project values:

```dotenv
SUPABASE_URL=<your-project-url>
SUPABASE_ANON_KEY=<your-anon-key>
SUPABASE_SERVICE_ROLE_KEY=<your-service-role-key>
```

`.env` is Git-ignored. Never commit the service-role key or put it in browser or
frontend code; it bypasses Row Level Security (RLS).

## Set up a fresh database

These instructions are for a **new, empty Supabase project**. Do not rerun the
`CREATE TABLE` migration against a project where the tables already exist.

1. In the Supabase SQL Editor, run
   [`database/migrations/001_create_crag_schema.sql`](database/migrations/001_create_crag_schema.sql).
   It enables pgvector and creates `collections`, `documents`,
   `document_chunks`, and `grading_log`.
2. Run the following SQL in the SQL Editor to add the four fixed collections,
   the vector and collection indexes, and the Phase 1 read-only access rules:

```sql
insert into public.collections (id, name, description) values
  ('technical_docs', 'Technical Documentation', 'Technical guides and reference material.'),
  ('sec_filings', 'SEC Filings', 'Company filings and disclosures.'),
  ('research_papers', 'Research Papers', 'Academic and research publications.'),
  ('policy_reports', 'Policy Reports', 'Policy analysis and reports.')
on conflict (id) do nothing;

create index if not exists document_chunks_embedding_idx
  on public.document_chunks using hnsw (embedding vector_cosine_ops);
create index if not exists document_chunks_collection_idx
  on public.document_chunks (collection_id);

alter table public.collections enable row level security;
alter table public.documents enable row level security;
alter table public.document_chunks enable row level security;
alter table public.grading_log enable row level security;

create policy "Authenticated users can read collections"
  on public.collections for select to authenticated using (true);
create policy "Authenticated users can read documents"
  on public.documents for select to authenticated using (true);
create policy "Authenticated users can read document chunks"
  on public.document_chunks for select to authenticated using (true);
create policy "Authenticated users can read grading log"
  on public.grading_log for select to authenticated using (true);

grant select on public.collections, public.documents,
  public.document_chunks, public.grading_log to anon, authenticated;
revoke insert, update, delete on public.collections, public.documents,
  public.document_chunks, public.grading_log from anon, authenticated;
```

The SQL above is for the initial setup. `CREATE POLICY` will fail if a policy
with the same name already exists. The `anon` role may query these tables but
RLS returns no rows; authenticated users may read all rows. These policies do
**not** limit reads to specific approved accounts. Control who can sign up or
sign in before using this design with sensitive data. Only trusted server-side
code should use the service-role client for writes.

## Verify Phase 1

From the repository root, run the lightweight connection check:

```powershell
uv run python -m ops.keeprunning
```

The expected result is a collection ID, such as `technical_docs`. To check
RLS, create a disposable test user in Supabase Auth, then run:

```powershell
uv run python database/test_rls.py
```

It prompts for that user's email and password; expected collection reads are
empty before sign-in, four rows after sign-in, and empty after sign-out. The
service-role test below attempts a denied anon insert, then inserts and removes
a temporary row with the admin client:

```powershell
uv run python database/test_service_role.py
```

Confirm that it reports the anon permission error, admin insert, and successful
deletion. Do not run the write test against data you cannot safely inspect.

## GitHub Actions keepalive

Add `SUPABASE_URL`, `SUPABASE_ANON_KEY`, and `SUPABASE_SERVICE_ROLE_KEY` as
repository **Actions secrets**. The workflow in
`.github/workflows/keepalive.yml` can be started manually with
**Actions → Supabase Keepalive → Run workflow** and is also scheduled daily at
05:17 UTC (10:47 IST). A successful run prints a collection ID without exposing
the keys. GitHub's scheduled start time can vary.

The Phase 1 database checks and a manual keepalive run passed on 2026-10-09.
The first automatic scheduled run had not yet been observed at that checkpoint.
