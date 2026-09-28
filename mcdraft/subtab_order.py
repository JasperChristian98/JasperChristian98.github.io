"""Alphabetise the dashboard's section-level subtab bars in the browser."""


ASSET = '<script defer src="assets/subtab-order.js"></script>\n'


def integrate_template(template: str) -> str:
    if 'assets/subtab-order.js' in template or template.count('</body>') != 1:
        raise RuntimeError('Subtab ordering insertion point changed or already integrated')
    return template.replace('</body>', ASSET + '</body>', 1)
