#!/usr/bin/env python3
"""Inspect a saved HTML file for common SEO signals. Python standard library only."""
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import urlparse


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lang = ''
        self.titles = []
        self.h1s = []
        self.meta = {}
        self.canonicals = []
        self.images = []
        self.structured_data = []
        self.capture = None
        self.buffer = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html':
            self.lang = a.get('lang', '') or ''
        elif tag == 'meta':
            key = (a.get('name') or a.get('property') or '').lower()
            self.meta.setdefault(key, []).append(a.get('content', '') or '')
        elif tag == 'link' and 'canonical' in (a.get('rel', '') or '').lower().split():
            self.canonicals.append(a.get('href', '') or '')
        elif tag == 'img':
            self.images.append(a)
        if tag in ('title', 'h1') or (tag == 'script' and (a.get('type', '') or '').lower() == 'application/ld+json'):
            self.capture, self.buffer = tag, []

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_data(self, data):
        if self.capture:
            self.buffer.append(data)

    def handle_endtag(self, tag):
        if self.capture == tag:
            value = ''.join(self.buffer).strip()
            if tag == 'title':
                self.titles.append(value)
            elif tag == 'h1':
                self.h1s.append(value)
            else:
                self.structured_data.append(value)
            self.capture, self.buffer = None, []


def inspect_html(html):
    page = PageParser()
    page.feed(html)
    findings = []

    def add(level, code, message):
        findings.append({'level': level, 'code': code, 'message': message})

    if len(page.titles) != 1 or not page.titles[0].strip():
        add('review', 'title', 'Use one non-empty page title.')
    descriptions = page.meta.get('description', [])
    if len(descriptions) != 1 or not descriptions[0].strip():
        add('review', 'description', 'Provide one useful meta description.')
    if len(page.canonicals) != 1:
        add('review', 'canonical-count', 'Review canonical intent; expected one canonical URL for this check.')
    elif not (urlparse(page.canonicals[0]).scheme in ('http', 'https') and urlparse(page.canonicals[0]).netloc):
        add('review', 'canonical-url', 'Prefer an absolute HTTP(S) canonical URL.')
    if not page.lang.strip():
        add('review', 'language', 'Set an appropriate HTML lang attribute.')
    if not page.h1s or not any(x.strip() for x in page.h1s):
        add('review', 'h1', 'Add a clear main heading.')
    elif len(page.h1s) > 1:
        add('info', 'multiple-h1', 'Multiple H1 headings found; review structure in context. This is not automatically an SEO error.')
    directives = page.meta.get('robots', []) + page.meta.get('googlebot', [])
    if any('noindex' in [x.strip().lower() for x in v.split(',')] for v in directives):
        add('review', 'noindex', 'An HTML robots directive requests noindex. Confirm this is intentional.')
    missing_alt = sum(1 for image in page.images if 'alt' not in image)
    if missing_alt:
        add('review', 'image-alt', f'{missing_alt} image(s) lack an alt attribute. Empty alt is valid for decorative images.')
    for key in ('og:title', 'og:description', 'og:image'):
        if not any(v.strip() for v in page.meta.get(key, [])):
            add('info', key, f'{key} is missing; consider it for social sharing.')
    for index, block in enumerate(page.structured_data, start=1):
        try:
            value = json.loads(block)
            if not isinstance(value, (dict, list)):
                add('review', 'jsonld-shape', f'JSON-LD block {index} is not an object or array.')
        except json.JSONDecodeError as exc:
            add('review', 'jsonld-syntax', f'JSON-LD block {index} is invalid JSON at line {exc.lineno}.')
    return {
        'title': page.titles,
        'description': descriptions,
        'canonical': page.canonicals,
        'h1': page.h1s,
        'language': page.lang,
        'image_count': len(page.images),
        'jsonld_block_count': len(page.structured_data),
        'findings': findings,
        'limits': 'Static HTML only. No HTTP headers, robots.txt, rendering, crawling, indexation, ranking, or schema eligibility validation.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file', type=Path, help='Saved UTF-8 HTML file')
    parser.add_argument('--json', action='store_true', help='Output machine-readable JSON')
    args = parser.parse_args()
    try:
        html = args.file.read_text(encoding='utf-8-sig')
    except (OSError, UnicodeError) as exc:
        parser.exit(2, f'Cannot read HTML: {exc}\n')
    report = inspect_html(html)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print('PharettaLabs / SEO Page Check')
        print('Title:', ' | '.join(report['title']) or '(missing)')
        print('Canonical:', ', '.join(report['canonical']) or '(missing)')
        print(f"Images: {report['image_count']} | JSON-LD blocks: {report['jsonld_block_count']}")
        for item in report['findings']:
            print(f"[{item['level'].upper()}] {item['code']}: {item['message']}")
        if not report['findings']:
            print('No findings in these limited checks. This is not a full SEO audit.')
        print('\nLimits:', report['limits'])


if __name__ == '__main__':
    main()
