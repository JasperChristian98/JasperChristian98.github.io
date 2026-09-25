"""Attach the shared chat without changing the preserved dashboard stages."""

PAGE_HTML = '''
<section class="page" id="page-league-chat">
  <div class="page-heading"><h1>League chat</h1><p>The McDraft common room. Matchday reactions, transfer talk and bragging rights.</p></div>
  <div class="card mcd-chat">
    <div class="mcd-chat-header"><div><div class="eyebrow">McDRAFT LIVE</div><h2>One league. One room.</h2></div><span id="chat-connection" role="status">Not connected</span><button id="chat-reconnect" type="button" hidden>Reconnect</button></div>
    <p id="chat-status" role="status" aria-live="polite">Opening league chat…</p>
    <div id="chat-setup" hidden><p>League chat is being set up. Come back once the organiser opens the room.</p></div>
    <details id="chat-share-tools"><summary>Share something from McDraft</summary><label for="chat-share-kind">What are we talking about?</label><select id="chat-share-kind"><option value="trade">Transfer proposal</option><option value="result">Match result</option><option value="agent">Free agent</option><option value="player">Any player</option></select><label for="chat-share-item">Choose an item</label><select id="chat-share-item"></select><button id="chat-share-pick" type="button">Preview share</button><p class="card-description">Shares use the dashboard's latest captured data. Add your take before sending.</p></details>
    <div id="chat-share-preview" hidden><strong>Share preview</strong><pre id="chat-share-text"></pre><button id="chat-share-add" type="button">Add to my message</button><button id="chat-share-cancel" type="button">Cancel</button></div>
    <div id="chat-auth" hidden>
      <p>Choose your team and enter the password supplied by the league organiser.</p>
      <form id="chat-login-form"><label for="chat-team">Your team</label><select id="chat-team" autocomplete="username" required></select><label for="chat-password">Team password</label><div class="mcd-chat-actions"><input id="chat-password" type="password" autocomplete="current-password" required maxlength="256"><button id="chat-login" type="submit">Join the room</button></div></form>
      <p class="card-description">Forgotten your password? Ask the league organiser to reset it.</p>
    </div>
    <div id="chat-account" hidden><span id="chat-identity"></span><button id="chat-signout" type="button">Sign out / switch team</button><small>Browsing another team does not change who you post as.</small></div>
    <div id="chat-room" hidden>
      <div class="mcd-chat-actions"><button id="chat-older" type="button">Earlier messages</button><button id="chat-refresh" type="button">Refresh conversation</button><button id="chat-new" type="button" hidden>New messages ↓</button></div>
      <div id="chat-messages" role="log" aria-label="League messages" aria-live="off" tabindex="0"></div>
      <p id="chat-empty" hidden>No messages yet. Start the conversation.</p>
      <form id="chat-compose"><label for="chat-message">Message the league</label><textarea id="chat-message" rows="3" maxlength="2000" required placeholder="What’s the verdict this gameweek?"></textarea><div class="mcd-chat-actions"><small>Up to 2,000 characters. Enter for a new line; Ctrl/⌘ + Enter to send.</small><button type="submit" id="chat-send">Send message</button></div></form>
    </div>
  </div>
</section>
'''

ASSETS = '''
<link rel="stylesheet" href="assets/league-chat.css">
<script defer src="assets/chat-config.js"></script>
<script defer src="assets/league-chat.js"></script>
<script defer src="assets/chat-sharing.js"></script>
'''


def integrate_template(template):
    page = '<section class="page" id="page-transfers">'
    nav = "['Results & Team of the Week','gameweeks'],"
    for anchor in (page, nav, '</body>'):
        if template.count(anchor) != 1:
            raise RuntimeError('League chat insertion point changed: ' + anchor)
    if 'id="page-league-chat"' in template:
        raise RuntimeError('League chat is already integrated')
    return (template.replace(page, PAGE_HTML + '\n' + page, 1)
            .replace(nav, "['League chat','league-chat'],\n  " + nav, 1)
            .replace('</body>', ASSETS + '\n</body>', 1))
