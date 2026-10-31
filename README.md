# SEO Page Check

**A small, dependency-free checker for the HTML you actually ship.**

Built by [John Strommen](https://github.com/johnstrommen-jstro306), founder of [PharettaLabs](https://pharettalabs.com), drawing on hands-on technical SEO and product experience.

Give it a saved HTML file or a page from your static build. It reports common metadata and markup issues for review, without crawling a site or sending your HTML to an external service.

## Run it

Requires Python 3.9 or newer. No packages or API keys required.

```sh
python3 seo_page_check.py /path/to/index.html
python3 seo_page_check.py /path/to/index.html --json
```

## What it checks

- Missing, empty, or duplicate page titles and meta descriptions
- Missing, multiple, or relative canonical URLs
- HTML language and main headings
- HTML robots and Googlebot `noindex` directives
- Images missing an `alt` attribute (empty alt is accepted for decorative images)
- Open Graph title, description, and image presence
- JSON-LD syntax, including multiple blocks

Multiple H1s are informational, not automatically treated as an SEO error. All findings require context: a page might intentionally be noindex, and a canonical strategy may differ by page type.

## Example output

```text
PharettaLabs / SEO Page Check
Title: My product
Canonical: (missing)
Images: 3 | JSON-LD blocks: 1
[REVIEW] canonical-count: Review canonical intent; expected one canonical URL for this check.
[REVIEW] image-alt: 1 image(s) lack an alt attribute. Empty alt is valid for decorative images.
```

The JSON output contains the extracted signals, findings, and limitations. The command returns 0 after a successful inspection, even when findings exist; input or argument errors return 2. There is no arbitrary SEO score or implied ranking prediction.

## Limitations

This is a static HTML inspection, not a browser, crawler, HTML5 validator, accessibility audit, or complete SEO audit. It does not inspect HTTP headers, robots.txt, redirects, rendered JavaScript, search indexation, or ranking. JSON-LD syntax checks do not establish schema correctness or Google rich-result eligibility. Use Search Console and the relevant validation tools for those questions.

## Tests

```sh
python3 -m unittest -v
```

Tests cover complete and incomplete metadata, canonical URLs, robots directives, comments, decorative images, JSON-LD, headings, and CLI behavior.

## More from PharettaLabs

- [Second Summit](https://github.com/johnstrommen-jstro306/second-summit-showcase): AI career tools and application workflows
- [BookWard](https://github.com/johnstrommen-jstro306/bookward-showcase): reading memory, discovery, and catalog data
- [Punch List](https://github.com/johnstrommen-jstro306/punch-list-showcase): AI task capture and household coordination

[Work with PharettaLabs](https://pharettalabs.com) · [Explore an idea](https://pharettalabs.com/start/)

## Contributing

Bug reports with a small, non-sensitive HTML example are welcome. Run the tests before proposing changes. Keep checks explainable and avoid turning heuristics into guarantees.

## License

MIT. See [LICENSE](LICENSE).
