# Outflank content pack

Article: **“You don’t need a SaaS to track competitors. I wrote a cron job instead.”**
Thesis: competitor tracking can be a cron job, not a subscription.

This folder is excluded from git through `.git/info/exclude`, so it's never committed.

## What's here

| Path | What it is |
|---|---|
| `substack/article.md` | The Substack article: about 1,430 words, with image placements and alt text. |
| `substack/images/01-hero.png` | Hero image with the title (1456 × 820). |
| `substack/images/02-architecture.png` | Architecture: the weekly cron and the 7-step pipeline, split into free/deterministic and capped AI steps. |
| `substack/images/03-real-websites.png` | Table: the three things real websites did, and what I changed. |
| `substack/images/04-battlecard.png` | Excerpt of the real Hyperbound battlecard (“don’t pitch Hindi”). |
| `substack/images/05-quiet-week.png` | The quiet-week funnel (8 pages → 0 AI calls → $0) and the estimated first-run cost. |
| `substack/images/06-saas-vs-cron.png` | Table: subscription vs cron job, labelled as my view. |
| `substack/images/07-what-broke.png` | The six plumbing failures, all fixed. |
| `substack/images/08-checklist.png` | The live-run checklist plus the decision rule. |
| `linkedin/carousel/slide-01…08.png` | 8 carousel slides at 1080 × 1350. |
| `linkedin/carousel/carousel.pdf` | The same 8 slides as one PDF, which is what you upload to LinkedIn. |
| `linkedin/carousel/alt-text.md` | Document description for the upload, plus per-slide alt text. |
| `linkedin/post-carousel.md` | Post to go with the carousel (1,221 characters, under the 1,300 limit). |
| `linkedin/post.md` | Standalone text-only version of the post (about 2,450 characters). |
| `linkedin/first-comment.md` | First comment, with the article link and the template and repo links. |
| `build.py` | Regenerates every image, slide and the PDF. |

## How to publish

**Substack**
1. Create a new post. Paste the title and subtitle (the `###` line) from `article.md`.
2. Paste the body. At each `![…](images/…)` line, upload that PNG instead, and paste the bracketed text as the image's alt text (image → Edit → Alt text).
3. Use `01-hero.png` as the post's social preview image too.

**LinkedIn, carousel version**
1. New post → **Add a document** → upload `linkedin/carousel/carousel.pdf`.
2. Give the document a title (e.g. “You don’t need a SaaS to track competitors”) and paste the description from `alt-text.md` if asked.
3. Paste `post-carousel.md` as the post text and publish.
4. Straight away, add `first-comment.md` as the first comment, after replacing `[SUBSTACK ARTICLE LINK]` with the article's URL.

**LinkedIn, text-only version:** post `post.md` and add the same first comment. Use one version or the other, not both on the same day.

## How to regenerate

```bash
python3 content/build.py
```

- **Needs Python 3 and Google Chrome.** On a Mac it uses `/Applications/Google Chrome.app`. Elsewhere it finds `google-chrome` or `chromium`; set `CHROME=/path/to/chrome` to override.
- **Fonts:** Fraunces, Space Grotesk and Caveat are downloaded from Google Fonts on the first run, cached in `content/.build/fonts/` and embedded in each page, because Chrome won't load web fonts from local files otherwise. Behind a proxy that inspects TLS, set `SSL_CERT_FILE` to its CA bundle.
- **Where to edit:** all copy and layout live in `build.py`, one function per image. Each image is an HTML page in `content/.build/`, screenshotted with `--force-device-scale-factor=2`. The PDF is printed from one HTML file with `@page { size: 540px 675px }`.
- **Checks:** the script fails if the PDF doesn't have exactly 8 pages.
