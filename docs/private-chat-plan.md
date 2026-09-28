# Private chat plan

Status: proposed for a future session. This document does not enable private
messages or change the running app or database.

## First version

Add a **Private messages** tab alongside the existing league room. A manager
chooses another active team, opens their conversation, and sends text messages
or the existing transfer, player, free-agent and result shares. Keep the current
team-password login and GitHub Pages hosting.

- One conversation per pair of team accounts, with saved history.
- An inbox showing the other team, latest message, time and unread count.
- A conversation header that clearly names the recipient.
- Mobile layout: inbox first, then conversation with a back button.
- The existing 2,000-character limit, retry protection and send rate limit.
- Realtime updates, with one-second catch-up for the open visible conversation.
- Read position saved across browsers; no read receipts shown to the other team.

Leave group chats, attachments, typing indicators, online status, push
notifications, editing and deleting messages for later.

## Identity and privacy

Access belongs to the authenticated team account, never the team currently
selected in the dashboard. Anyone sharing that team's credentials shares its
private inbox. Resetting the password does not create a new inbox; transferring
an existing account to a new manager would also expose its earlier history.

Only the two participants may read a conversation through the app or its API.
Enforce that in database permissions, including realtime delivery; hiding a
conversation in JavaScript is insufficient. Project administrators still have
database access: this is not end-to-end encrypted messaging.

Inactive members cannot read or send. A remaining active participant can retain
access to past messages but cannot send to an inactive recipient. If membership
is restored, that same account regains its history. Display an unavailable
recipient state rather than silently accepting an undeliverable message.

## Backend design

Use an additive migration and keep the public league-room tables intact.

- `league_dm_conversations`: ID, two distinct member user IDs in canonical
  order, creation time, and a unique constraint on the pair. Concurrent opens
  from either side must resolve to the same conversation.
- `league_dm_messages`: ID, conversation ID, authenticated sender ID, client
  request UUID, sender-name snapshot, body and server timestamp. Index history
  by conversation and message ID; make sender/request UUID unique.
- `league_dm_reads`: conversation ID, reader ID and last-read message ID, unique
  per participant/conversation. Read position only moves forward and must refer
  to a message in that conversation.

Expose a minimal active-team directory to signed-in active league members,
containing team names and account IDs only. The existing membership table allows
users to read only their own membership: preserve that policy and provide a
separate restricted directory function. Do not expose login emails, credentials
or membership administration fields.

Provide narrowly scoped database functions to open a conversation, send a
message, list inbox summaries/unread counts, and advance the caller's read
position. Validate identity, participation and active membership on the server.
Prevent direct client writes and default anonymous/public function execution.
Apply row-level security to all new tables, avoid recursive membership policies,
and restrict privileged functions to a fixed search path and explicit checks.

Derive sender and timestamps on the server. Reuse the member-row lock and
`last_sent_at` so the three-second send limit is shared across league chat and
DMs, including concurrent tabs. Retry the same request without duplicating a
message; reject reuse of a request UUID for a different conversation or body.

## Client and sharing

Extract a small shared authentication/session layer from `assets/league-chat.js`
before adding `assets/private-chat.js`. Both views should use the same client,
membership state and sign-out handling. Keep rendering text through safe DOM
APIs, never by interpolating message contents into HTML.

Maintain separate history, pagination, pending sends, drafts and read positions
per conversation. Cancel or ignore old responses when switching conversations
or accounts. Clear private content and subscriptions on sign-out or revoked
membership; do not persist message bodies or drafts in browser storage.

Subscribe for authorized incoming messages to update inbox badges. Catch up the
open conversation every second without overlapping requests; refresh the inbox
less often and after reconnecting. Suspend polling in hidden tabs. Use history
pagination and a catch-up cursor so bursts over a single page are not missed.
Mark messages read only when their conversation is visible and the messages have
been viewed, not merely downloaded. Keep unread counts consistent across tabs.

Extend the existing share preview with a destination: **League room** or a
specific team. Display that destination beside the composer and send button.
Changing destinations must not automatically send or copy an existing draft.
Shares remain editable text snapshots; sending a proposal does not execute or
accept a trade.

## Implementation sequence and acceptance checks

1. Add migration and transactional permission tests in staging. Test both
   participants, a third member, an outsider, anonymous access, revoked access,
   forged sender/recipient IDs and direct API writes. Verify directory and inbox
   results reveal no other conversations or message contents.
2. Test concurrent conversation creation, retries, cross-conversation request
   reuse, shared rate limiting and validated monotonic read positions.
3. Refactor shared session handling, then add inbox and conversation UI through
   `mcdraft/league_chat.py` and static assets, preserving legacy build stages.
   Keep the existing league room working throughout.
4. Add share destinations and browser tests for account/conversation switches,
   drafts, unread counts, stale requests, reconnects, missed-message catch-up,
   safe rendering and mobile navigation. No test should send real messages.
5. Test realtime privacy using separate staging sessions for two participants
   and a third manager. Test revocation while subscribed and recovery after a
   session refresh. Confirm the existing league-chat permission tests still pass.
6. Document the migration and account-history implications, run the full suite,
   then apply the reviewed migration and publish the updated site. The organiser
   will need to run the migration if SQL/admin access is still unavailable.

No new service or SMTP setup is expected. Before implementation, verify current
Supabase realtime authorization behavior and plan limits against official docs.
The main work is conversation isolation and synchronization, not the chat input.
