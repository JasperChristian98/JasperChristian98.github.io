"""Attach comparison and local lineup planning to the generated dashboard."""

ASSETS = '''
<link rel="stylesheet" href="assets/player-tools.css">
<script defer src="assets/player-tools.js"></script>
'''


def integrate_template(template):
    if 'assets/player-tools.js' in template or template.count('</body>') != 1:
        raise RuntimeError('Player tools insertion point changed or already integrated')
    return template.replace('</body>', ASSETS + '\n</body>', 1)
