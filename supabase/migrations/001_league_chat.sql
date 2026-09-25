-- Run once in the Supabase SQL Editor. One project = one private league room.
begin;

create table public.league_chat_members (
  user_id uuid primary key references auth.users(id) on delete cascade,
  manager_name text not null unique check (char_length(btrim(manager_name)) between 1 and 100),
  active boolean not null default true,
  last_sent_at timestamptz
);

create table public.league_chat_messages (
  id bigint generated always as identity primary key,
  user_id uuid not null references auth.users(id),
  client_id uuid not null,
  manager_name text not null,
  body text not null check (char_length(btrim(body)) between 1 and 2000),
  created_at timestamptz not null default clock_timestamp(),
  unique(user_id, client_id)
);

alter table public.league_chat_members enable row level security;
alter table public.league_chat_messages enable row level security;
revoke all on public.league_chat_members, public.league_chat_messages from anon, authenticated;
grant select (user_id, manager_name, active) on public.league_chat_members to authenticated;
grant select on public.league_chat_messages to authenticated;

create policy "Read own membership" on public.league_chat_members
  for select to authenticated using (user_id = (select auth.uid()));

create policy "Only active league members read chat" on public.league_chat_messages
  for select to authenticated using (exists (
    select 1 from public.league_chat_members m
    where m.user_id = (select auth.uid()) and m.active
  ));

-- The browser cannot insert directly or supply its own sender name/timestamp.
-- Locking membership serialises sends per user, including concurrent tabs.
create function public.send_league_chat_message(p_body text, p_client_id uuid)
returns public.league_chat_messages
language plpgsql security definer set search_path = '' as $$
declare
  member public.league_chat_members;
  message public.league_chat_messages;
begin
  if auth.uid() is null then raise exception 'Sign in to send messages'; end if;
  select * into member from public.league_chat_members
    where user_id = auth.uid() and active for update;
  if not found then raise exception 'Your account is not an active league member'; end if;
  if p_client_id is null or p_body is null or char_length(btrim(p_body)) not between 1 and 2000 then
    raise exception 'Messages must contain 1 to 2000 characters';
  end if;
  select * into message from public.league_chat_messages
    where user_id = auth.uid() and client_id = p_client_id;
  if found then return message; end if;
  if member.last_sent_at > clock_timestamp() - interval '3 seconds' then
    raise exception 'Please wait three seconds between messages';
  end if;
  insert into public.league_chat_messages(user_id, client_id, manager_name, body)
    values (auth.uid(), p_client_id, member.manager_name, btrim(p_body)) returning * into message;
  update public.league_chat_members set last_sent_at = clock_timestamp() where user_id = auth.uid();
  return message;
end;
$$;
revoke all on function public.send_league_chat_message(text, uuid) from public, anon;
grant execute on function public.send_league_chat_message(text, uuid) to authenticated;

alter publication supabase_realtime add table public.league_chat_messages;
commit;
