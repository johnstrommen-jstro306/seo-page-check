import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from seo_page_check import inspect_html

GOOD = '''<!doctype html><html lang="en"><head>
<title>Useful software &amp; growth</title><meta content="Product studio" name="description">
<link href="https://example.com/" rel="canonical">
<meta property="og:title" content="Studio"><meta property="og:description" content="Build useful things">
<meta property="og:image" content="https://example.com/share.png">
<script type="application/ld+json">{"@context":"https://schema.org","@type":"Organization","name":"Demo"}</script>
</head><body><h1>Build <em>something</em> useful</h1><img src="decorative.svg" alt=""></body></html>'''


class PageCheckTests(unittest.TestCase):
    def codes(self, html):
        return {x['code'] for x in inspect_html(html)['findings']}

    def test_complete_document(self):
        report = inspect_html(GOOD)
        self.assertEqual(report['findings'], [])
        self.assertEqual(report['title'], ['Useful software & growth'])
        self.assertEqual(report['h1'], ['Build something useful'])

    def test_missing_and_duplicate_metadata(self):
        codes = self.codes('<html><head><title>A</title><title>B</title></head></html>')
        self.assertTrue({'title', 'description', 'canonical-count', 'language', 'h1'} <= codes)

    def test_relative_canonical(self):
        self.assertIn('canonical-url', self.codes(GOOD.replace('https://example.com/" rel', '/relative" rel')))

    def test_googlebot_noindex_and_comments(self):
        self.assertIn('noindex', self.codes(GOOD.replace('</head>', '<meta NAME="Googlebot" content="noindex, follow"></head>')))
        self.assertNotIn('noindex', self.codes(GOOD.replace('</head>', '<!-- <meta name="robots" content="noindex"> --></head>')))

    def test_decorative_alt_is_valid(self):
        self.assertNotIn('image-alt', self.codes(GOOD))
        self.assertIn('image-alt', self.codes(GOOD.replace(' alt=""', '')))

    def test_invalid_jsonld(self):
        self.assertIn('jsonld-syntax', self.codes(GOOD.replace('"name":"Demo"', '"name":oops')))
        self.assertNotIn('jsonld-syntax', self.codes(GOOD.replace('{"@context":"https://schema.org","@type":"Organization","name":"Demo"}', '[]')))

    def test_multiple_headings_are_informational(self):
        findings = inspect_html(GOOD.replace('</body>', '<h1>Another</h1></body>'))['findings']
        self.assertEqual(next(x for x in findings if x['code'] == 'multiple-h1')['level'], 'info')

    def test_cli_json_and_missing_file(self):
        script = str(Path(__file__).with_name('seo_page_check.py'))
        with tempfile.TemporaryDirectory() as d:
            page = Path(d) / 'example.html'
            page.write_text(GOOD, encoding='utf-8')
            result = subprocess.run([sys.executable, script, str(page), '--json'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(json.loads(result.stdout)['findings'], [])
            missing = subprocess.run([sys.executable, script, str(Path(d)/'missing.html')], capture_output=True, text=True)
            self.assertEqual(missing.returncode, 2)
            self.assertIn('Cannot read HTML', missing.stderr)


if __name__ == '__main__':
    unittest.main()
