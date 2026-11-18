-- AETHER RNG shared database schema (Supabase / PostgreSQL)
-- Run this whole file in Supabase SQL Editor.
create table if not exists public.player_profiles (
  user_id uuid primary key references auth.users(id) on delete cascade,
  display_name text not null default '',
  total_rolls bigint not null default 0,
  best_tier integer not null default 0 check (best_tier between 0 and 7),
  equipped_aura_id text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create table if not exists public.player_inventory (
  user_id uuid not null references auth.users(id) on delete cascade,
  aura_id text not null,
  quantity bigint not null default 0 check (quantity >= 0),
  first_obtained_at timestamptz not null default now(),
  primary key (user_id, aura_id)
);
create table if not exists public.roll_history (
  id bigint generated always as identity primary key,
  user_id uuid not null references auth.users(id) on delete cascade,
  aura_id text not null,
  tier integer not null,
  created_at timestamptz not null default now()
);
create index if not exists roll_history_user_created_idx on public.roll_history(user_id, created_at desc);
create index if not exists player_profiles_rolls_idx on public.player_profiles(total_rolls desc);

alter table public.player_profiles enable row level security;
alter table public.player_inventory enable row level security;
alter table public.roll_history enable row level security;

drop policy if exists "profiles readable" on public.player_profiles;
drop policy if exists "public leaderboard profile fields" on public.player_profiles;
drop policy if exists "players read own profile" on public.player_profiles;
create policy "players read own profile" on public.player_profiles for select to authenticated using ((select auth.uid()) = user_id);
drop policy if exists "players update own profile" on public.player_profiles;
create policy "players update own profile" on public.player_profiles for update using (auth.uid() = user_id) with check (auth.uid() = user_id);
drop policy if exists "players read own inventory" on public.player_inventory;
create policy "players read own inventory" on public.player_inventory for select using (auth.uid() = user_id);
drop policy if exists "players read own history" on public.roll_history;
create policy "players read own history" on public.roll_history for select using (auth.uid() = user_id);

-- Clients cannot directly insert or change inventory/history. Rolls are performed by this server-side function.
create or replace function public.roll_aura()
returns table(aura_id text, tier integer, total_rolls bigint)
language plpgsql
security definer
set search_path = '', pg_temp
as $$
declare
  v_user uuid := auth.uid();
  v_roll double precision;
  v_sum double precision := 0;
  v_aura text;
  v_tier integer;
  v_weight double precision;
  v_weights jsonb := '{
    "dust":450000,"leaf":300000,"bubble":150000,
    "ember":70000,"frost":25000,"tide":25000,"storm":12000,
    "nebula":10000,"phantom":5000,"solar":2000,"lunar":1000,
    "singularity":450,"chronos":180,"aurora":90,"eclipse":35,
    "seraph":12,"infinity":3,"origin":1
  }'::jsonb;
  v_item record;
  v_new_total bigint;
  v_name text;
  v_name text;
  v_name text;
begin
  if v_user is null then
    raise exception 'Authentication required';
  end if;
  v_name := coalesce(nullif(auth.jwt()->'user_metadata'->>'display_name',''), 'Player-' || upper(substr(replace(v_user::text, '-', ''), 1, 6)));
  insert into public.player_profiles(user_id, display_name)
  values (v_user, v_name)
  on conflict (user_id) do nothing;

  select random() * sum((value::text)::double precision)
    into v_roll from jsonb_each(v_weights);

  for v_item in select key, value from jsonb_each(v_weights) loop
    v_weight := (v_item.value::text)::double precision;
    v_sum := v_sum + v_weight;
    if v_roll <= v_sum then
      v_aura := v_item.key;
      exit;
    end if;
  end loop;

  v_tier := case
    when v_aura in ('dust','leaf','bubble') then 0
    when v_aura in ('ember','frost') then 1
    when v_aura in ('tide','storm') then 2
    when v_aura in ('nebula','phantom') then 3
    when v_aura in ('solar','lunar') then 4
    when v_aura in ('singularity','chronos') then 5
    when v_aura in ('aurora','eclipse') then 6
    else 7 end;

  insert into public.player_inventory(user_id, aura_id, quantity)
  values (v_user, v_aura, 1)
  on conflict (user_id, aura_id)
  do update set quantity = public.player_inventory.quantity + 1;

  insert into public.roll_history(user_id, aura_id, tier)
  values (v_user, v_aura, v_tier);

  update public.player_profiles
  set total_rolls = total_rolls + 1,
      best_tier = greatest(best_tier, v_tier),
      updated_at = now()
  where user_id = v_user
  returning player_profiles.total_rolls into v_new_total;

  return query select v_aura, v_tier, v_new_total;
end;
$$;
revoke all on function public.roll_aura() from public;
grant execute on function public.roll_aura() to authenticated;


-- Keep public leaderboard data separate from private player profile rows.
create table if not exists public.global_leaderboard (
  user_id uuid primary key references auth.users(id) on delete cascade,
  display_name text not null,
  total_rolls bigint not null default 0,
  best_tier integer not null default 0,
  updated_at timestamptz not null default now()
);
alter table public.global_leaderboard enable row level security;
drop policy if exists "public leaderboard readable" on public.global_leaderboard;
create policy "public leaderboard readable" on public.global_leaderboard
for select to anon, authenticated using (true);
revoke all on public.global_leaderboard from anon, authenticated;
grant select (display_name, total_rolls, best_tier) on public.global_leaderboard to anon, authenticated;

create or replace function public.sync_global_leaderboard()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
  insert into public.global_leaderboard(user_id, display_name, total_rolls, best_tier, updated_at)
  values (new.user_id, new.display_name, new.total_rolls, new.best_tier, now())
  on conflict (user_id) do update
  set display_name = excluded.display_name,
      total_rolls = excluded.total_rolls,
      best_tier = excluded.best_tier,
      updated_at = now();
  return new;
end;
$$;
revoke all on function public.sync_global_leaderboard() from public, anon, authenticated;
drop trigger if exists sync_global_leaderboard_trigger on public.player_profiles;
create trigger sync_global_leaderboard_trigger
after insert or update of display_name, total_rolls, best_tier
on public.player_profiles
for each row execute function public.sync_global_leaderboard();

grant usage on schema public to authenticated, anon;
grant select on public.player_profiles to authenticated;
grant select on public.player_inventory, public.roll_history to authenticated;
revoke insert, update, delete on public.player_profiles, public.player_inventory, public.roll_history from anon, authenticated;
grant update (equipped_aura_id) on public.player_profiles to authenticated;
revoke all on function public.roll_aura() from public, anon;
grant execute on function public.roll_aura() to authenticated;
