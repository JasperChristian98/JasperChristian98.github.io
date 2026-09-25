-- Run as administrator after creating confirmed Auth users with these aliases.
-- Adds only accounts that exist. Does not create accounts, change passwords,
-- reactivate suspended members, or replace existing memberships.
with teams(email, manager_name) as (values
  ('team-87664@chat.mcdraft.invalid', 'No Weimann No Cry'),
  ('team-87744@chat.mcdraft.invalid', 'Kamararama FC'),
  ('team-87907@chat.mcdraft.invalid', 'PAUer Rangers'),
  ('team-88057@chat.mcdraft.invalid', 'Backstreet Moyes'),
  ('team-89446@chat.mcdraft.invalid', 'Jaap? Best Stam'),
  ('team-150925@chat.mcdraft.invalid', 'Ollie Gonna Squashya'),
  ('team-204850@chat.mcdraft.invalid', 'NoRSNoRB No Chance'),
  ('team-205209@chat.mcdraft.invalid', 'danny’s doggy dudes'),
  ('team-209204@chat.mcdraft.invalid', 'Buendophilia'),
  ('team-259256@chat.mcdraft.invalid', 'Jacquet Potato')
)
insert into public.league_chat_members(user_id, manager_name)
select u.id, t.manager_name from teams t join auth.users u on lower(u.email)=t.email
on conflict (user_id) do nothing
returning manager_name;

-- Review the enrolled teams; missing teams need their Auth accounts created.
select manager_name, active from public.league_chat_members order by manager_name;
