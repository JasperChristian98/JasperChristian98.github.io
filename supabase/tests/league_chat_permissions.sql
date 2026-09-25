-- Run in the SQL Editor of a STAGING project after the migration.
-- Everything is rolled back, including the three temporary Auth accounts.
begin;
insert into auth.users(id, email) values
 ('00000000-1111-4000-8000-000000000001','chat-test-a@example.invalid'),
 ('00000000-1111-4000-8000-000000000002','chat-test-b@example.invalid'),
 ('00000000-1111-4000-8000-000000000003','chat-test-outsider@example.invalid');
insert into public.league_chat_members(user_id,manager_name) values
 ('00000000-1111-4000-8000-000000000001','Chat test A'),
 ('00000000-1111-4000-8000-000000000002','Chat test B');

set local role authenticated;
select set_config('request.jwt.claim.sub','00000000-1111-4000-8000-000000000001',true);
do $$
declare message public.league_chat_messages; retried public.league_chat_messages;
begin
  assert (select count(user_id) from public.league_chat_members)=1, 'Membership leaks';
  message := public.send_league_chat_message('Hello league','00000000-2222-4000-8000-000000000001');
  assert message.manager_name='Chat test A', 'Wrong sender';
  assert message.user_id=auth.uid(), 'Wrong user';
  retried := public.send_league_chat_message('Hello league','00000000-2222-4000-8000-000000000001');
  assert message.id=retried.id, 'Retry duplicated message';
  begin
    perform public.send_league_chat_message('Too soon','00000000-2222-4000-8000-000000000002');
    raise exception 'Rate limit failed';
  exception when raise_exception then
    if sqlerrm <> 'Please wait three seconds between messages' then raise; end if;
  end;
  begin
    update public.league_chat_members set manager_name='Impersonated manager' where user_id=auth.uid();
    raise exception 'Membership write was allowed';
  exception when insufficient_privilege then null;
  end;
  begin
    insert into public.league_chat_messages(user_id,client_id,manager_name,body)
      values(auth.uid(),gen_random_uuid(),'Impersonated manager','Forged');
    raise exception 'Direct insert was allowed';
  exception when insufficient_privilege then null;
  end;
end $$;

select set_config('request.jwt.claim.sub','00000000-1111-4000-8000-000000000002',true);
do $$ begin
  assert exists(select 1 from public.league_chat_messages where body='Hello league'), 'Other member cannot read';
end $$;

select set_config('request.jwt.claim.sub','00000000-1111-4000-8000-000000000003',true);
do $$ begin
  assert not exists(select 1 from public.league_chat_messages), 'Outsider can read';
  begin
    perform public.send_league_chat_message('Outsider',gen_random_uuid());
    raise exception 'Outsider could send';
  exception when raise_exception then
    if sqlerrm <> 'Your account is not an active league member' then raise; end if;
  end;
end $$;

reset role;
update public.league_chat_members set active=false where user_id='00000000-1111-4000-8000-000000000002';
set local role authenticated;
select set_config('request.jwt.claim.sub','00000000-1111-4000-8000-000000000002',true);
do $$ begin
  assert not exists(select 1 from public.league_chat_messages), 'Revoked member can read';
end $$;

set local role anon;
select set_config('request.jwt.claim.sub','',true);
do $$ begin
  begin
    perform 1 from public.league_chat_messages;
    raise exception 'Anonymous read was allowed';
  exception when insufficient_privilege then null;
  end;
  begin
    perform public.send_league_chat_message('Anonymous',gen_random_uuid());
    raise exception 'Anonymous send was allowed';
  exception when insufficient_privilege then null;
  end;
end $$;
rollback;
