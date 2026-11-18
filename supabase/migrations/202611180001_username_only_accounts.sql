create table if not exists public.username_registry (
  username text primary key,
  user_id uuid not null unique references auth.users(id) on delete cascade,
  created_at timestamptz not null default now(),
  constraint username_registry_format check (username ~ '^[a-z0-9_]{3,20}$')
);
alter table public.username_registry enable row level security;
revoke all on public.username_registry from public, anon, authenticated;
