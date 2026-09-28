"""Attach club badges without changing the preserved stages."""

ASSETS = '''
<link rel="stylesheet" href="assets/club-badges.css">
<script defer src="assets/club-badges.js"></script>
'''


def integrate_template(template):
    if 'assets/club-badges.js' in template or template.count('</body>') != 1:
        raise RuntimeError('Club badge insertion point changed or already integrated')
    return template.replace('</body>', ASSETS + '\n</body>', 1)
