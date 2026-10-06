#!/usr/bin/env python3
"""Builds site/report.pdf and site/index.html from report.md.

Pipeline: report.md -> pandoc -> HTML with assets/report.css and the Inter
fonts -> headless Chrome -> PDF with a document outline. The HTML is kept as
the web version, with the fonts copied beside it.

Run make_charts.py first if a count or a divider value changed.

Requires pandoc, pdftotext and pdfinfo (poppler) and Google Chrome. Set CHROME
to Chrome's path if it is not in the usual place.

Usage: python3 build_report.py
"""

import html
import os
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'assets'
SITE = ROOT / 'site'
CHROME = os.environ.get('CHROME') or next(
    (path for path in ('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                       '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable')
     if Path(path).exists()), 'google-chrome')

TITLE = 'The Samsung Odyssey G9 black screen'
SUBTITLE = ('A guide for owners whose monitor lights up but shows no picture, '
            'and what is known about why it happens')
RUNNING_TITLE = 'Samsung Odyssey G9 black screen'
DATE = '6 October 2026'
REPOSITORY = 'https://github.com/danieljbk/samsung-odyssey-g9-black-screen'
META = [
    ('Compiled by', 'u/djbkwon'),
    ('Date', DATE),
    ('Models', 'C49G95T, S49AG95'),
    ('Corrections', 'on GitHub'),
]

CSS = (
    # The cover has no disclaimer to pin to the page foot, so it takes its natural
    # height; the fixed height in report.css lets the contents list overflow.
    '.cover { height: auto; }\n.toc-label { margin-top: 9mm; }\n'
    '.toc-compact a { padding: 1.4mm 0; }\n'
    'figure svg { display: block; width: 100%; height: auto; }\n'
    # Links are shown in the accent colour, so a reader knows the sources are clickable.
    'main a, .meta a { color: var(--accent); }\n'
    # report.css keeps a paragraph whose only element is a bold lead-in with the
    # next block; here those paragraphs carry their own text, so the rule would
    # chain a whole section together and push it to the next page.
    'p:has(> strong:only-child) { break-after: auto; }\n'
    # The start-here box, the safety callout, and the tall flowchart.
    '.start-here { margin: 0 0 6mm; padding: 5mm 6mm 2mm; border: 1px solid var(--rule); border-left: 3px solid var(--accent); border-radius: 0 2mm 2mm 0; background: var(--surface); }\n'
    '.start-title { font-size: 11.5pt; font-weight: 600; color: var(--ink); margin-bottom: 3mm; }\n'
    '.start-here li { margin-bottom: 2.2mm; }\n'
    '.start-route { margin-top: 3mm; padding-top: 3mm; border-top: 1px solid var(--rule); }\n'
    '.callout { margin: 5mm 0; padding: 4mm 5mm 1mm; border: 1px solid #f0c9c9; border-left: 3px solid #d03b3b; border-radius: 0 2mm 2mm 0; background: #fdf4f4; break-inside: avoid; }\n'
    'figure.tall svg { width: 72%; margin: 0 auto; }\n'
    'figure.narrow svg { width: 82%; margin: 0 auto; }\n'
    # Section 4 opens on a fresh page so its heading stays with its table.
    '#section-5 { break-before: page; }\n'
    # Captions are inside the table, so a caption cannot be left behind at a page foot.
    'caption { caption-side: top; text-align: left; margin: 5mm 0 2mm; font-size: 8.4pt; line-height: 1.5; }\n'
    # On a screen the report is a column of readable width rather than a sheet of paper.
    '@media screen { body { max-width: 170mm; margin: 12mm auto; padding: 0 6mm; } .toc-page { display: none; } }\n'
    '@media print { .screen-only { display: none; } }\n'
    '.meta { grid-template-columns: repeat(5, auto); }\n'
)


def font_faces(base):
    faces = [(400, 'normal'), (500, 'normal'), (600, 'normal'), (700, 'normal'),
             (400, 'italic'), (600, 'italic')]
    return ''.join(
        f'@font-face {{ font-family: Inter; font-weight: {weight}; font-style: {style}; '
        f'src: url("{base}/inter-latin-{weight}-{style}.woff2") format("woff2"); }}\n'
        for weight, style in faces)


def prepared_markdown():
    """report.md with each figure's SVG inlined in place of its <img>.

    The source shows figures/name.svg as an image so GitHub displays it; the
    build inlines the drawing instead, so its text uses the report's font and
    stays sharp in the PDF."""
    text = (ROOT / 'report.md').read_text()
    return re.sub(r'<img src="figures/([a-z0-9-]+)\.svg"[^>]*>',
                  lambda m: (ROOT / 'figures' / f'{m.group(1)}.svg').read_text().strip(), text)


def body_html():
    result = subprocess.run(
        ['pandoc', '-f', 'markdown+smart', '-t', 'html5', '--wrap=none'],
        input=prepared_markdown(), check=True, capture_output=True, text=True)
    return result.stdout


def cover_html(content, pages):
    # The start-here page follows the cover directly, so the list leaves it out.
    headings = [(anchor, text) for anchor, text in
                re.findall(r'<h2 id="(section-\d+)">(.*?)</h2>', content, re.S)
                if text != 'Start here']
    meta = ''.join(
        f'<div><dt>{html.escape(k)}</dt><dd>'
        + (f'<a href="{REPOSITORY}">{html.escape(v)}</a>' if k == 'Corrections' else html.escape(v))
        + '</dd></div>' for k, v in META)
    # The web version links to the PDF; the PDF itself has no need to.
    meta += '<div class="screen-only"><dt>PDF</dt><dd><a href="report.pdf">Download</a></dd></div>'
    toc = ''.join(f'<li><a href="#{anchor}"><span class="toc-title">{text}</span>'
                  f'<span class="toc-leader"></span>'
                  f'<span class="toc-page">{pages.get(anchor, "")}</span></a></li>'
                  for anchor, text in headings)
    return f'''
<section class="cover">
  <div>
    <p class="eyebrow">Repair research</p>
    <h1>{html.escape(TITLE)}</h1>
    <p class="subtitle">{html.escape(SUBTITLE)}</p>
    <dl class="meta">{meta}</dl>
    <p class="toc-label">Contents</p>
    <ol class="toc toc-compact">{toc}</ol>
  </div>
</section>'''


def document(content, pages):
    css = font_faces('fonts') + (ASSETS / 'report.css').read_text()
    css = css.replace('__RUNNING_TITLE__', RUNNING_TITLE).replace('__FOOTER_DATE__', DATE) + CSS
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(TITLE)}</title>
<style>{css}</style></head>
<body>{cover_html(content, pages)}
<main>{content}</main></body></html>'''


def print_pdf(text, pdf_path):
    html_path = SITE / 'print.html'
    html_path.write_text(text)
    subprocess.run(
        [CHROME, '--headless=new', '--disable-gpu', '--no-sandbox', '--no-pdf-header-footer',
         '--generate-pdf-document-outline', '--virtual-time-budget=15000',
         f'--print-to-pdf={pdf_path}', html_path.as_uri()],
        # UTC, so the PDF's creation date carries no local time zone.
        check=True, capture_output=True, env={**os.environ, 'TZ': 'UTC'})
    html_path.unlink()


def heading_pages(pdf_path, content):
    """The page each section heading lands on, read from a first rendering."""
    pages = {}
    count = int(re.search(r'Pages:\s+(\d+)', subprocess.run(
        ['pdfinfo', str(pdf_path)], check=True, capture_output=True, text=True).stdout).group(1))
    texts = [subprocess.run(['pdftotext', '-f', str(n), '-l', str(n), str(pdf_path), '-'],
                            check=True, capture_output=True, text=True).stdout
             for n in range(1, count + 1)]
    for anchor, heading in re.findall(r'<h2 id="(section-\d+)">(.*?)</h2>', content, re.S):
        plain = html.unescape(re.sub(r'<[^>]+>', '', heading)).replace('’', "'")
        for number, text in enumerate(texts[1:], start=2):
            if plain in text.replace('’', "'"):
                pages[anchor] = number
                break
    return pages


def main():
    SITE.mkdir(exist_ok=True)
    # The fonts sit beside the pages, so the web version and the print share one path.
    shutil.copytree(ASSETS / 'fonts', SITE / 'fonts', dirs_exist_ok=True)
    content = body_html()
    pdf_path = SITE / 'report.pdf'
    # Two passes: the first finds the page of each heading, the second prints
    # those page numbers in the contents list on the cover.
    print_pdf(document(content, {}), pdf_path)
    pages = heading_pages(pdf_path, content)
    print_pdf(document(content, pages), pdf_path)
    (SITE / 'index.html').write_text(document(content, pages))
    print(f'wrote {pdf_path} and {SITE / "index.html"}')


if __name__ == '__main__':
    main()
