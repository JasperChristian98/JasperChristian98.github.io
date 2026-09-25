# McDraft team-password chat

The dashboard stays on GitHub Pages. Supabase verifies team passwords and stores
private messages. Email codes, email templates and SMTP are not required for this
login flow. The organiser creates accounts and distributes passwords privately.

## Existing project: what changes

If you already ran `supabase/migrations/001_league_chat.sql`, **do not run it
again**. The existing tables, message history, membership rules and send function
are reused. Only login changes. The project URL and public key are already in
`assets/chat-config.js`.

## 1. Create a team account

In Supabase, open Authentication ? Users ? Add user ? Create new user.
Use the team's alias from this table as its email, choose a unique strong password,
and enable **Auto Confirm User** (confirmed email). Use **Create**, not an email
invitation. These aliases are account identifiers, not working mailboxes; Supabase
must not require an email confirmation to log in.

| Team | Auth email / public login alias |
|---|---|
| No Weimann No Cry | `team-87664@chat.mcdraft.invalid` |
| Kamararama FC | `team-87744@chat.mcdraft.invalid` |
| PAUer Rangers | `team-87907@chat.mcdraft.invalid` |
| Backstreet Moyes | `team-88057@chat.mcdraft.invalid` |
| Jaap? Best Stam | `team-89446@chat.mcdraft.invalid` |
| Ollie Gonna Squashya | `team-150925@chat.mcdraft.invalid` |
| NoRSNoRB No Chance | `team-204850@chat.mcdraft.invalid` |
| danny’s doggy dudes | `team-205209@chat.mcdraft.invalid` |
| Buendophilia | `team-209204@chat.mcdraft.invalid` |
| Jacquet Potato | `team-259256@chat.mcdraft.invalid` |

Start with your own team. Repeat for the other managers when ready. The website
shows team names; managers never need to type these aliases. Aliases are public
and contain no personal email addresses or passwords. Passwords go only into the
Supabase account form, never this repository or `assets/chat-config.js`.

If you previously created a real-email account and assigned it a membership,
reuse that account's UUID: change its email to the team alias and set a password
through Supabase administration. Alternatively remove its unused membership
before creating a new team account. Each manager name can belong to only one
membership. Do not delete accounts that own existing messages.

## 2. Enable membership

After creating the account, run `supabase/setup_team_memberships.sql` in the SQL
Editor as an administrator. It joins the public aliases to existing Auth accounts
and adds their league memberships. It does not create accounts or passwords and
can be rerun as you add teams. It preserves existing memberships and suspensions.
Check that your team appears with `active = true` in the resulting table.

The team-password approach is still backed by server-side authentication. Changing
the public team selector, alias configuration or local HTML cannot bypass the
Supabase membership checks. Public self-sign-up is not used; disable new-user
sign-ups in Supabase Auth settings if you do not need them for anything else.

## 3. Test and publish

Open the updated dashboard ? League ? League chat. Choose your team and enter
its password. The displayed sender comes from verified backend membership.
The global team selection prefills the login form while signed out. Once signed
in, browsing other teams leaves your chat identity unchanged. Use **Sign out /
switch team** to log into another account.

Check a wrong password is rejected, then use two accounts in separate browsers
to confirm live delivery and saved history. Changing the dashboard's team selector
must not change the sender. Sign-out must clear messages and the draft.

Publish `index.html`, `assets/` and the source changes using the normal GitHub
Pages flow. Relative asset paths work on project Pages URLs. Scheduled Python
builds preserve chat integration and never change passwords or message history.

## Passwords and recovery

Give each manager their password privately. Anyone holding that password can act
as that team. Supabase handles password verification and authentication rate
limits; the public configuration contains aliases only. Browser sessions persist,
so managers should sign out on shared devices.

Password resets are handled by the organiser through Supabase's privileged Auth
administration (including `auth.admin.updateUserById` with a new password). That
API requires a server-side/admin key: never place it in the browser configuration.
There is no email reset button in this version. Existing signed-in sessions may
remain valid after a password change; if access must stop immediately, disable
membership first and revoke sessions through Auth administration.

## Fresh project setup

For a new Supabase project, run `supabase/migrations/001_league_chat.sql` once.
It creates the membership table, message table, row-level permissions, send
function and Realtime publication. Then fill in `supabaseUrl` and the
`sb_publishable_...` key in `assets/chat-config.js`. Never use a secret/service-role
key there. Follow the team-account and membership steps above.

## Validation

`supabase/tests/league_chat_permissions.sql` exercises member/nonmember access,
impersonation protection, rate limits and idempotent retries. Run it in a staging
project's SQL Editor after the migration. Test users and messages are rolled back.
A blank final `set_config` result is expected; failures raise SQL errors.

Offline browser checks use a fake transport and send no emails or real messages:

```powershell
$env:MCD_CHAT_BROWSER = 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
python -m unittest discover -s tests -p test_league_chat.py -v
```

## Operation

- One private league room, plain-text messages up to 2,000 characters, with history.
- Sender names/timestamps and a three-second per-user send limit are enforced by
  the database. Retrying an unconfirmed send with unchanged text uses the same
  request ID to prevent duplicates.
- Realtime delivers inserts. The open, visible chat also checks every second (other visible dashboard pages every 15 seconds); reconnects
  reload recent history. Earlier messages loads older pages.
- Messages stay in Supabase, not public HTML or the league-history JSON. Admin
  removals appear after refreshing the conversation or reconnecting.
- Disable access with `update public.league_chat_members set active = false where
  user_id = 'UUID';`. Server reads/sends stop immediately. The client clears its
  displayed history on the next membership check; previously read content cannot
  be recalled from a person's device.
- Unsent drafts survive connection failures on the current page, but not sign-out
  or page reload. No attachments, private messages or push notifications yet.

## Sharing from the dashboard

Use **Share in chat** on negotiation proposals, **Share this trade in chat** in
Trade Lab, or the share buttons on player cards and completed results. You can
also open **Share something from McDraft** in chat to choose a proposal, result,
free agent or any player.

Each action opens a plain-text preview using the dashboard's captured data.
Sign in, choose **Add to my message**, edit or add your thoughts, then **Send
message**. Opening a preview never posts anything. Trade shares are labelled
hypothetical; a share does not execute or accept a trade. No database migration
is needed for sharing or the faster automatic refresh.

## Dependency and references

The vendored browser client is `assets/vendor/supabase-2.117.2.js` with its MIT
license. SHA-256:
`59d39487c3589843b410322d8a3d562ce022aba1e5ccb16898ef3fb2a0da2ecd`.
Source: `https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.117.2/dist/umd/supabase.js`.

- [Password login](https://supabase.com/docs/reference/javascript/auth-signinwithpassword)
- [Admin account creation](https://supabase.com/docs/reference/javascript/auth-admin-createuser)
- [Admin password changes](https://supabase.com/docs/reference/javascript/auth-admin-updateuserbyid)
- [Realtime](https://supabase.com/docs/guides/realtime/postgres-changes)
- [Row-level security](https://supabase.com/docs/guides/database/postgres/row-level-security)
