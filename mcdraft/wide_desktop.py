"""Final desktop-only stylesheet, independent of preserved legacy stages."""


def integrate_template(template):
    if 'assets/wide-desktop.css' in template or template.count('</head>') != 1:
        raise RuntimeError('Wide desktop stylesheet insertion point changed or already integrated')
    return template.replace('</head>', '<link rel="stylesheet" href="assets/wide-desktop.css">\n</head>', 1)
