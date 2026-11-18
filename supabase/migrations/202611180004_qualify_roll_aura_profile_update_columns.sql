create or replace function public.roll_aura()
returns table(result_aura_id text, result_tier integer, result_total_rolls bigint)
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
  on conflict on constraint player_inventory_pkey
  do update set quantity = public.player_inventory.quantity + 1;

  insert into public.roll_history(user_id, aura_id, tier)
  values (v_user, v_aura, v_tier);

  update public.player_profiles
  set total_rolls = public.player_profiles.total_rolls + 1,
      best_tier = greatest(public.player_profiles.best_tier, v_tier),
      updated_at = now()
  where user_id = v_user
  returning player_profiles.total_rolls into v_new_total;

  return query select v_aura, v_tier, v_new_total;
end;
$$;
revoke all on function public.roll_aura() from public, anon;
grant execute on function public.roll_aura() to authenticated;
