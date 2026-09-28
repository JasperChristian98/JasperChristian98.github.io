"""A client-rendered atlas of 100 supplemental charts across Analytics tabs."""


ASSETS = '''<link rel="stylesheet" href="assets/chart-atlas.css">
<script defer src="assets/chart-atlas.js"></script>
'''


def integrate_template(template: str) -> str:
    required_pages = (
        'analytics-sub-insights', 'analytics-sub-matrices', 'analytics-sub-ratings',
        'analytics-sub-player', 'analytics-sub-relationships', 'analytics-sub-river-passport',
        'analytics-sub-club', 'analytics-sub-squad-strength', 'analytics-sub-squad-build',
        'analytics-sub-decisions', 'analytics-sub-availability-impact',
        'analytics-sub-fixtures-h2h', 'analytics-sub-season', 'analytics-sub-league-stats',
        'analytics-sub-gameweek-lab', 'analytics-sub-visuals',
    )
    if ('assets/chart-atlas.js' in template or template.count('</body>') != 1
            or any(template.count(f'id="{page}"') != 1 for page in required_pages)):
        raise RuntimeError('Chart Atlas insertion point changed or already integrated')
    return template.replace('</body>', ASSETS + '</body>', 1)
