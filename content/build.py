#!/usr/bin/env python3
"""Build the Outflank content pack: Substack images, LinkedIn carousel PNGs + PDF.

Every image is an HTML page in the f1rstword.com theme, rendered with headless Chrome so
the web fonts load. Run from anywhere:  python3 content/build.py

Fonts come from Google Fonts. They're downloaded once into content/.build/fonts and embedded
as data URIs, because Chrome won't load web fonts from local file:// pages otherwise.
"""
import base64
import os
import platform
import re
import shutil
import ssl
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent            # content/
REPO = ROOT.parent
BUILD = ROOT / '.build'
FONT_DIR = BUILD / 'fonts'
SUB = ROOT / 'substack' / 'images'
CAR = ROOT / 'linkedin' / 'carousel'
SCALE = 2                                          # --force-device-scale-factor

GOOGLE_FONTS = ('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,900;1,9..144,700'
                '&family=Space+Grotesk:wght@400;500;700&family=Caveat:wght@700&display=block')
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'


# ---------------------------------------------------------------- fonts
def _get(url):
    ctx = ssl.create_default_context(cafile=os.environ.get('SSL_CERT_FILE'))
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, context=ctx, timeout=60) as r:
        return r.read()


def font_css():
    """Google Fonts CSS with every font file inlined as a data URI (cached on disk)."""
    FONT_DIR.mkdir(parents=True, exist_ok=True)
    css_file = FONT_DIR / 'fonts.css'
    if not css_file.exists():
        css_file.write_bytes(_get(GOOGLE_FONTS))
    css = css_file.read_text()

    def inline(m):
        url = m.group(1)
        local = FONT_DIR / re.sub(r'[^A-Za-z0-9._-]', '_', url.split('/s/')[-1])
        if not local.exists():
            local.write_bytes(_get(url))
        return f"url(data:font/woff2;base64,{base64.b64encode(local.read_bytes()).decode()})"

    return re.sub(r'url\((https://fonts\.gstatic\.com/[^)]+)\)', inline, css)


# ---------------------------------------------------------------- chrome
def chrome():
    for c in [os.environ.get('CHROME'),
              '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
              shutil.which('google-chrome'), shutil.which('chromium'), shutil.which('chromium-browser')]:
        if c and Path(c).exists():
            return c
    sys.exit('Chrome not found. Set CHROME=/path/to/chrome')


def chrome_flags():
    flags = ['--headless=new', '--disable-gpu', '--hide-scrollbars']
    if platform.system() == 'Linux' and os.geteuid() == 0:
        flags.append('--no-sandbox')  # Chrome refuses to run as root without it (CI/containers)
    return flags


def screenshot(html_path, out, w, h):
    subprocess.run([chrome(), *chrome_flags(), f'--force-device-scale-factor={SCALE}',
                    f'--window-size={w},{h}', '--virtual-time-budget=15000',
                    f'--screenshot={out}', f'file://{html_path}'],
                   check=True, capture_output=True)


def print_pdf(html_path, out):
    subprocess.run([chrome(), *chrome_flags(), '--no-pdf-header-footer', '--virtual-time-budget=15000',
                    f'--print-to-pdf={out}', f'file://{html_path}'], check=True, capture_output=True)


# ---------------------------------------------------------------- theme
MARK = (REPO / 'assets' / 'mark.svg').read_text()
MARK = re.sub(r'<title.*?</desc>', '', MARK, flags=re.S)
MARK = re.sub(r'width="\d+" height="\d+"', 'width="100%" height="100%"', MARK, count=1)

THEME = '''
:root{--ink:#1A1523;--ink2:#453B52;--coral:#FF5233;--coral-dk:#C23A20;--cream:#FFF6EE;--cream2:#FBEEE0;
--lav:#E6E1F7;--sky:linear-gradient(180deg,#F4A896 0%,#E8A0C4 34%,#B8A9D9 67%,#7FA8D9 100%);
--g:#1F8F4E;--gbg:#DDF3E4;--a:#9A5B00;--abg:#FFE8BF;--r:#C23A20;--rbg:#FFD9D1}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:__W__px;height:__H__px;overflow:hidden}
body{font-family:'Space Grotesk',sans-serif;color:var(--ink);background:var(--cream);position:relative;
 -webkit-font-smoothing:antialiased;-webkit-print-color-adjust:exact;print-color-adjust:exact;
 font-feature-settings:"ss01" 0}
.page{position:relative;width:__W__px;height:__H__px;overflow:hidden;background:var(--cream)}
.sky{background:var(--sky)}
.dark{background:var(--ink);color:var(--cream)}
.glow{position:absolute;border-radius:50%;background:radial-gradient(closest-side,rgba(255,255,255,.55),rgba(255,255,255,0));pointer-events:none}
.sun{position:absolute;border-radius:50%;border:3px solid var(--ink);
 background:radial-gradient(circle at 40% 35%,#FFF1B8 0%,#FFD5A0 45%,var(--coral) 100%)}
.card{background:var(--cream2);border:3px solid var(--ink);border-radius:26px;box-shadow:7px 7px 0 var(--ink)}
.pill{display:inline-flex;align-items:center;gap:6px;border:2px solid var(--ink);border-radius:999px;
 background:var(--cream);font-weight:700;white-space:nowrap}
.kicker{font-family:'Caveat',cursive;font-weight:700;color:var(--coral-dk);display:inline-block;transform:rotate(-2deg);line-height:1}
.dark .kicker{color:#FFB3A3}
h1,h2,h3{font-family:'Fraunces',serif;font-weight:900;line-height:1.02;letter-spacing:-.012em;font-variation-settings:"opsz" 144}
h1 em,h2 em,h3 em{font-style:italic;font-weight:700;color:var(--coral)}
.dark h2 em{color:var(--coral)}
.hero{color:var(--cream);text-shadow:3px 3px 0 var(--coral-dk),6px 6px 0 var(--ink)}
.hero em{color:var(--coral);text-shadow:3px 3px 0 var(--ink)}
h1,h2,h3{text-wrap:balance}
p,li,td,div{text-wrap:pretty}
.brand{position:absolute;display:flex;align-items:center;gap:7px;font-family:'Fraunces',serif;font-weight:900}
.brand .m{display:block}
.pnum{position:absolute;font-weight:700;letter-spacing:.04em}
.ok{color:var(--g);background:var(--gbg)}
.warn{color:var(--a);background:var(--abg)}
.bad{color:var(--r);background:var(--rbg)}
.tag{display:inline-block;border:2px solid currentColor;border-radius:999px;font-weight:700;white-space:nowrap}
code{font-family:'Space Grotesk',monospace;font-weight:700;background:var(--lav);border:1.5px solid var(--ink);border-radius:7px;padding:0 5px}
'''


def page(w, h, body, extra_css='', cls=''):
    css = font_css() + THEME.replace('__W__', str(w)).replace('__H__', str(h)) + extra_css
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><style>{css}</style></head>'
            f'<body><div class="page {cls}">{body}</div></body></html>')


def brand(size=18, left=22, bottom=18, color='var(--ink)'):
    return (f'<div class="brand" style="left:{left}px;bottom:{bottom}px;font-size:{size}px;color:{color}">'
            f'<span class="m" style="width:{size * 1.35:.0f}px;height:{size * 1.35:.0f}px">{MARK}</span>Outflank</div>')


def pnum(n, total, right=24, bottom=20, color='var(--ink)'):
    return f'<div class="pnum" style="right:{right}px;bottom:{bottom}px;font-size:15px;color:{color}">{n}/{total}</div>'


def head(kicker, title, k_size=26, t_size=40, cls='', gap=4):
    return (f'<div class="kicker" style="font-size:{k_size}px;margin-bottom:{gap}px">{kicker}</div>'
            f'<h2 class="{cls}" style="font-size:{t_size}px">{title}</h2>')


# ================================================================= SUBSTACK (728 css px → 1456 px)
SW = 728


def sub_hero():
    h = 410
    body = f'''
<div class="glow" style="left:-80px;top:-60px;width:420px;height:220px"></div>
<div class="glow" style="right:-60px;bottom:30px;width:360px;height:180px;opacity:.7"></div>
<div class="sun" style="right:46px;top:34px;width:78px;height:78px"></div>
<div style="position:absolute;left:44px;top:44px;right:150px">
  <div class="kicker" style="font-size:27px;color:var(--ink)">a true story, mostly about plumbing</div>
</div>
<h1 class="hero" style="position:absolute;left:42px;top:92px;width:640px;font-size:58px;line-height:1.0">You don’t need <em>a SaaS</em> to track competitors.</h1>
<div class="pill" style="position:absolute;left:46px;top:226px;padding:9px 18px;font-family:Fraunces,serif;font-style:italic;font-weight:700;font-size:23px;box-shadow:4px 4px 0 var(--ink);transform:rotate(-1.5deg)">I wrote a cron job instead.</div>
<div style="position:absolute;right:30px;bottom:22px;display:flex;gap:8px">
  <span class="pill" style="padding:5px 12px;font-size:13px;transform:rotate(2deg)">211 passing tests</span>
  <span class="pill" style="padding:5px 12px;font-size:13px;background:#FFE8BF;transform:rotate(-2deg)">8 real pages</span>
  <span class="pill" style="padding:5px 12px;font-size:13px;transform:rotate(1.5deg)">$0 quiet week</span>
</div>
{brand(16, 44, 22)}'''
    return page(SW, h, body, cls='sky'), h


def step(n, title, sub, cls=''):
    return (f'<div class="card st {cls}"><div class="n">{n}</div><div class="t">{title}</div><div class="s">{sub}</div></div>')


ARCH_CSS = '''
.row{display:flex;gap:10px;align-items:stretch}
.st{flex:1;padding:12px 10px 12px;border-radius:18px;box-shadow:5px 5px 0 var(--ink)}
.st .n{width:26px;height:26px;border-radius:50%;background:var(--coral);border:2px solid var(--ink);color:var(--cream);
 font-weight:700;font-size:13px;display:flex;align-items:center;justify-content:center;margin-bottom:6px}
.st .t{font-family:Fraunces,serif;font-weight:900;font-size:17px;line-height:1.05}
.st .s{font-size:11.5px;color:var(--ink2);margin-top:4px;line-height:1.3}
.lane{position:relative;border:2px dashed var(--ink);border-radius:22px;padding:30px 14px 16px}
.lane .lbl{position:absolute;top:-14px;left:16px;padding:3px 11px;font-size:12px}
.down{display:flex;justify-content:center;margin:6px 0}
.down svg{width:18px;height:22px}
'''
ARROW = '<div class="down"><svg viewBox="0 0 18 22"><path d="M9 1 V19 M2 13 L9 20 L16 13" fill="none" stroke="#1A1523" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg></div>'


def sub_architecture():
    h = 760
    body = f'''
<div style="position:absolute;left:36px;top:30px;right:36px">
  {head('how it works', 'Code watches. <em>AI only reads</em> what changed.', 25, 33)}
  <div class="pill" style="margin-top:16px;padding:7px 14px;font-size:13.5px;background:var(--lav)">⏱ GitHub Actions cron · every Monday 03:17 UTC · in your private repo</div>
  {ARROW}
  <div class="lane" style="background:#FFFDF9"><span class="pill lbl ok" style="border-color:var(--g)">free + deterministic</span>
    <div class="row">
      {step(1, 'Fetch', 'robots.txt first, polite + identified')}
      {step(2, 'Extract', 'main content, or your <b>include</b> selectors')}
      {step(3, 'Normalize', 'strip timestamps, years, tracking params')}
      {step(4, 'Diff', 'vs last week’s snapshot')}
      {step(5, 'Filter', 'keyword triggers, size threshold')}
    </div>
  </div>
  {ARROW}
  <div class="lane" style="background:#FFF6EE"><span class="pill lbl warn" style="border-color:var(--a)">AI · only real changes · hard cost cap</span>
    <div class="row">
      {step(6, 'Triage', 'fast model: noise, minor or material')}
      {step(7, 'Analyze', 'stronger model, material changes only')}
      {step('→', 'Battlecards', 'only the affected sections are rewritten')}
    </div>
  </div>
  {ARROW}
  <div class="row">
    <div class="card" style="flex:1.2;padding:12px 16px;border-radius:18px;box-shadow:5px 5px 0 var(--ink)"><div style="font-family:Fraunces;font-weight:900;font-size:16px">Committed to your repo</div><div style="font-size:12.5px;color:var(--ink2);margin-top:3px">snapshots · digests · battlecards · Git history = change log</div></div>
    <div class="card" style="flex:1;padding:12px 16px;border-radius:18px;box-shadow:5px 5px 0 var(--ink);background:#FFD9D1"><div style="font-family:Fraunces;font-weight:900;font-size:16px">Sent to you</div><div style="font-size:12.5px;color:var(--ink2);margin-top:3px">GitHub issue · Slack · Discord</div></div>
  </div>
</div>
{brand(15, 36, 18)}'''
    return page(SW, h, body, ARCH_CSS), h


TABLE_CSS = '''
.tbl{width:100%;border-collapse:separate;border-spacing:0;border:3px solid var(--ink);border-radius:22px;overflow:hidden;
 background:var(--cream2);box-shadow:7px 7px 0 var(--ink)}
.tbl th{background:var(--ink);color:var(--cream);text-align:left;font-size:12.5px;letter-spacing:.06em;text-transform:uppercase;padding:11px 14px}
.tbl td{padding:13px 14px;border-top:2px solid var(--ink);vertical-align:top;font-size:13.5px;line-height:1.38;color:var(--ink2)}
.tbl td b{color:var(--ink)}
.tbl td.site{font-family:Fraunces,serif;font-weight:900;font-size:17px;color:var(--ink);width:128px}
.tbl .tag{font-family:'Space Grotesk',sans-serif;font-size:11px;padding:2px 8px;margin-top:6px}
'''


def sub_real_websites():
    h = 560
    body = f'''
<div style="position:absolute;left:36px;top:30px;right:40px">
  {head('day one, real internet', 'Real websites broke <em>three assumptions</em>', 25, 34)}
  <p style="font-size:14px;color:var(--ink2);margin:10px 0 18px">The four vendors are examples of what the tool does with real pages, not a review of them.</p>
  <table class="tbl">
    <tr><th>Site</th><th>What happened</th><th>What I changed</th></tr>
    <tr><td class="site">Convin<br><span class="tag bad">wrong site</span></td>
        <td>From the server I ran it on, convin.ai redirected to a <b>US product for home&#8209;service businesses</b>.</td>
        <td>Swapped it out. Check the final URL your tracker actually sees.</td></tr>
    <tr><td class="site">Hyperbound<br><span class="tag warn">likely A/B test</span></td>
        <td><code>/pricing</code> quietly redirected to <code>/pricing-b</code>. A variant flip could look like a price change.</td>
        <td>Watch a stable part of the page, or ignore the parts that flip.</td></tr>
    <tr><td class="site">Second Nature<br><span class="tag warn">208 chars</span></td>
        <td>Default extraction kept a <b>208&#8209;character</b> fragment of the financial-services page.</td>
        <td>One <code>include</code> selector → <b>4.7k characters</b> <span class="tag ok" style="margin:0">fixed</span></td></tr>
  </table>
  <div class="kicker" style="font-size:25px;margin-top:22px;margin-left:6px">none of this shows up in a test suite.</div>
</div>
{brand(15, 36, 18)}'''
    return page(SW, h, body, TABLE_CSS), h


BC_CSS = '''
.bc{padding:20px 24px 18px}
.bc h3{font-size:16px;margin:14px 0 6px}
.bc h3:first-of-type{margin-top:0}
.bc ul{list-style:none}
.bc li{position:relative;padding-left:20px;font-size:13.5px;line-height:1.42;color:var(--ink2);margin-bottom:6px}
.bc li:before{content:"";position:absolute;left:2px;top:7px;width:9px;height:9px;border-radius:50%;background:var(--coral);border:1.5px solid var(--ink)}
.bc li b{color:var(--ink)}
.hl{background:var(--abg);border:2px solid var(--a);border-radius:14px;padding:8px 10px 6px 30px!important;margin:4px 0 8px}
.hl:before{left:11px!important;top:15px!important}
'''


def sub_battlecard():
    h = 650
    body = f'''
<div style="position:absolute;left:36px;top:30px;right:40px">
  {head('the moment it earned its keep', 'The battlecard said <em>don’t pitch Hindi</em>', 25, 34)}
  <div class="card bc" style="margin-top:18px">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
      <div style="font-family:Fraunces;font-weight:900;font-size:24px">Hyperbound <span style="font-family:'Space Grotesk';font-weight:500;font-size:13px;color:var(--ink2)">· battlecard excerpt, trimmed</span></div>
      <span class="tag ok" style="font-size:11.5px;padding:3px 10px">REAL OUTPUT</span>
    </div>
    <h3>Pricing &amp; packaging</h3>
    <ul><li><b>Model:</b> “priced per user, with separate licenses available for Practice and Perform”. No prices are shown.</li>
        <li><b>Free plan:</b> includes the Outbound, Objection Handling and Inbound roleplay packs.</li></ul>
    <h3>Where they’re strong</h3>
    <ul><li class="hl">Indian languages: Hindi, Gujarati, Marathi and Tamil are listed, so vernacular support alone is <b>not</b> a differentiator against them.</li></ul>
    <h3>Where we likely win</h3>
    <ul><li>Indian BFSI and pharma depth: their banking page is about financial advisors and AUM growth, with no pharma content observed.</li></ul>
    <h3>How to handle them in a sales conversation</h3>
    <ul><li><b>Don’t lead with “we support Hindi”.</b> Lead with Indian BFSI and pharma scenarios and compliance instead.</li></ul>
  </div>
  <div class="kicker" style="font-size:24px;margin-top:18px;margin-left:6px">a change alert is a notification. this is intelligence.</div>
</div>
{brand(15, 36, 18)}'''
    return page(SW, h, body, BC_CSS), h


FUNNEL_CSS = '''
.fn{display:flex;align-items:stretch;gap:8px;margin-top:22px}
.fa{align-self:center}
.fs{flex:1;display:flex;flex-direction:column;justify-content:center;text-align:center;padding:16px 6px 13px;border-radius:20px;box-shadow:5px 5px 0 var(--ink)}
.fs .v{font-family:Fraunces,serif;font-weight:900;font-size:40px;line-height:1}
.fs .l{font-size:12px;color:var(--ink2);margin-top:6px;line-height:1.25}
.fa{font-weight:700;font-size:20px}
'''


def sub_quiet_week():
    h = 470
    body = f'''
<div style="position:absolute;left:36px;top:30px;right:40px">
  {head('the boring run is the whole argument', 'A quiet week costs <em>$0</em>', 25, 36)}
  <p style="font-size:14px;color:var(--ink2);margin-top:10px">Second run, later the same day. Same 8 pages, fetched fresh.</p>
  <div class="fn">
    <div class="card fs"><div class="v">8</div><div class="l">pages fetched</div></div><div class="fa">→</div>
    <div class="card fs"><div class="v">8</div><div class="l">identical after normalizing</div></div><div class="fa">→</div>
    <div class="card fs ok" style="background:var(--gbg)"><div class="v" style="color:var(--g)">0</div><div class="l">AI calls</div></div><div class="fa">→</div>
    <div class="card fs ok" style="background:var(--gbg)"><div class="v" style="color:var(--g)">$0</div><div class="l">spent</div></div>
  </div>
  <div style="display:flex;gap:14px;margin-top:30px">
    <div class="card" style="flex:1.35;padding:14px 18px;background:#FFFDF9"><div style="font-family:Fraunces;font-weight:900;font-size:17px">The expensive run is the first</div>
      <div style="font-size:13px;color:var(--ink2);margin-top:5px;line-height:1.4">4 battlecards ≈ 7.5k input + 3.3k output tokens → <b style="color:var(--ink)">≈ $0.10–0.25</b> on Claude Opus. <span class="tag warn" style="font-size:10.5px;padding:1px 7px">estimate</span></div></div>
    <div class="card" style="flex:1;padding:14px 18px;background:var(--lav)"><div style="font-family:Fraunces;font-weight:900;font-size:17px">Hard cap, every run</div>
      <div style="font-size:13px;color:var(--ink2);margin-top:5px;line-height:1.4">$1 by default. Past it, no more model calls; those pages are retried next run.</div></div>
  </div>
</div>
{brand(15, 36, 18)}'''
    return page(SW, h, body, FUNNEL_CSS), h


CMP_CSS = TABLE_CSS + '''
.tbl td.k{font-family:Fraunces,serif;font-weight:900;font-size:15.5px;color:var(--ink);width:104px;white-space:nowrap}
.tbl td.c{background:#FFFDF9}
'''


def sub_saas_vs_cron():
    h = 612
    body = f'''
<div style="position:absolute;left:36px;top:30px;right:40px">
  {head('my view, not a benchmark', 'Subscription vs <em>cron job</em>', 25, 36)}
  <table class="tbl" style="margin-top:20px">
    <tr><th></th><th>Subscription</th><th style="background:var(--coral-dk)">Cron job (Outflank)</th></tr>
    <tr><td class="k">Cost</td><td>Fixed price per seat or plan, every month</td><td class="c"><b>Pay per change.</b> A quiet week costs $0.</td></tr>
    <tr><td class="k">Your data</td><td>In the vendor’s dashboard</td><td class="c">In <b>your own private repo</b></td></tr>
    <tr><td class="k">History</td><td>Whatever the tool keeps</td><td class="c"><b>Git history</b> of every page</td></tr>
    <tr><td class="k">Setup</td><td>Sales call, onboarding</td><td class="c">Template + <b>one secret</b></td></tr>
    <tr><td class="k">Tuning</td><td>The vendor’s settings</td><td class="c">One YAML file: keywords, selectors, caps</td></tr>
  </table>
  <div class="card" style="margin-top:22px;padding:12px 18px;background:var(--abg);border-color:var(--ink)">
    <span style="font-family:Fraunces;font-weight:900;font-size:16px">Where a subscription wins:</span>
    <span style="font-size:13.5px;color:var(--ink2)"> minute-level alerts, hundreds of pages, or nobody on your team to own a small repo.</span>
  </div>
</div>
{brand(15, 36, 18)}'''
    return page(SW, h, body, CMP_CSS), h


BROKE_CSS = '''
.br{display:flex;gap:12px;align-items:flex-start;padding:11px 16px;border-top:2px solid var(--ink)}
.br:first-child{border-top:none}
.br .i{flex:0 0 26px;height:26px;border-radius:50%;background:var(--coral);border:2px solid var(--ink);color:var(--cream);font-weight:700;font-size:13px;display:flex;align-items:center;justify-content:center;margin-top:1px}
.br .t{flex:1;font-size:13.5px;line-height:1.38;color:var(--ink2)}
.br .t b{color:var(--ink);font-size:14.5px}
.br .tag{font-size:10.5px;padding:2px 8px;margin-top:3px}
'''


def sub_what_broke():
    rows = [
        ('The request format', 'The JSON schema sent to the model used <code>minLength</code>, a keyword the API doesn’t support. Every live AI call would likely have failed. Mocked tests couldn’t see it.'),
        ('The workflow deleted its own engine', 'For pages that need a browser, a second <code>npm install --no-save</code> removed the package the first one added.'),
        ('Docker read a comment as the API key', '<code>KEY=   # note</code> works with dotenv. Docker’s <code>--env-file</code> reads it as <code># note</code>.'),
        ('Alerts could ping people', 'Scraped <code>&lt;!channel&gt;</code> or <code>@someone</code> could have pinged a Slack channel or a GitHub user. Everything is escaped now.'),
        ('CI broke the tests', 'The tests inherited the CI runner’s environment, so CI took a different code path.'),
        ('Publishing had its own gate', 'npm required two-factor authentication, then staged the first release behind a placeholder version.'),
    ]
    items = ''.join(f'<div class="br"><div class="i">{i + 1}</div><div class="t"><b>{t}</b><br>{d}</div><span class="tag ok">fixed</span></div>'
                    for i, (t, d) in enumerate(rows))
    h = 720
    body = f'''
<div style="position:absolute;left:36px;top:30px;right:40px">
  {head('not the AI', 'What broke was <em>the plumbing</em>', 25, 36)}
  <div class="card" style="margin-top:18px;padding:4px 0">{items}</div>
  <div class="kicker" style="font-size:24px;margin-top:20px;margin-left:6px">the model was the least of my problems.</div>
</div>
{brand(15, 36, 18)}'''
    return page(SW, h, body, BROKE_CSS), h


CHECK_CSS = '''
.ck{display:flex;gap:12px;align-items:flex-start;padding:10px 16px;border-top:2px dashed rgba(26,21,35,.25)}
.ck:first-child{border-top:none}
.ck .b{flex:0 0 24px;height:24px;border:2.5px solid var(--ink);border-radius:7px;background:var(--cream);display:flex;align-items:center;justify-content:center;margin-top:1px}
.ck .b svg{width:15px;height:15px}
.ck .t{font-size:14px;line-height:1.38;color:var(--ink2)}
.ck .t b{color:var(--ink);font-size:15px}
'''
TICK = '<svg viewBox="0 0 16 16"><path d="M2.5 8.5 L6.5 12.5 L13.5 3.5" fill="none" stroke="#FF5233" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def checklist_items():
    return [
        ('Run it on three real sites', 'before you trust it.'),
        ('Read what it extracted, not what it concluded.', 'A 208&#8209;character page still gets a confident summary.'),
        ('Run it twice.', 'If the second run isn’t quiet, your noise filtering is wrong.'),
        ('Check the final URL.', 'Geo redirects and A/B tests are real.'),
        ('Filter before you call a model.', 'Keywords and size thresholds are free.'),
        ('Cap the cost of every run.', ''),
        ('Escape everything you send to Slack or GitHub.', ''),
    ]


def sub_checklist():
    items = ''.join(f'<div class="ck"><div class="b">{TICK}</div><div class="t"><b>{a}</b> {b}</div></div>' for a, b in checklist_items())
    h = 690
    body = f'''
<div style="position:absolute;left:36px;top:30px;right:40px">
  {head('copy this', 'The <em>live-run</em> checklist', 25, 36)}
  <div style="font-size:13px;color:var(--ink2);margin-top:6px">My rule of thumb before trusting any AI tool for GTM.</div>
  <div class="card" style="margin-top:16px;padding:6px 0">{items}</div>
  <div class="card dark" style="margin-top:22px;padding:15px 20px;background:var(--ink);color:var(--cream);box-shadow:7px 7px 0 var(--coral-dk)">
    <div class="kicker" style="font-size:21px;color:#FFB3A3">decision rule (rule of thumb)</div>
    <div style="font-family:Fraunces;font-weight:900;font-size:19px;line-height:1.2;margin-top:4px">If the pages you care about change <em style="color:var(--coral);font-weight:700">weekly or slower</em>, a cron job beats a subscription.</div>
  </div>
</div>
{brand(15, 36, 18)}'''
    return page(SW, h, body, CHECK_CSS), h


SUBSTACK = [
    ('01-hero.png', sub_hero), ('02-architecture.png', sub_architecture), ('03-real-websites.png', sub_real_websites),
    ('04-battlecard.png', sub_battlecard), ('05-quiet-week.png', sub_quiet_week), ('06-saas-vs-cron.png', sub_saas_vs_cron),
    ('07-what-broke.png', sub_what_broke), ('08-checklist.png', sub_checklist),
]

# ================================================================= CAROUSEL (540x675 css px → 1080x1350 px)
CW, CH, TOTAL = 540, 675, 8
SLIDE_CSS = '''
.wrap{position:absolute;left:38px;right:38px;top:44px}
.lead{font-size:17px;line-height:1.42;color:var(--ink2)}
.jobs{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:22px}
.job{padding:16px 16px 14px}
.job .t{font-family:Fraunces,serif;font-weight:900;font-size:22px}
.job .s{font-size:14px;color:var(--ink2);margin-top:4px;line-height:1.35}
.flow .f{display:flex;align-items:center;gap:12px;padding:11px 14px;border-radius:18px;box-shadow:5px 5px 0 var(--ink)}
.flow .f .n{flex:0 0 30px;height:30px;border-radius:50%;background:var(--coral);border:2px solid var(--ink);color:var(--cream);font-weight:700;font-size:14px;display:flex;align-items:center;justify-content:center}
.flow .f .t{font-family:Fraunces,serif;font-weight:900;font-size:18px;line-height:1.1}
.flow .f .s{font-size:13px;color:var(--ink2);line-height:1.3}
.flow .f .tag{margin-left:auto;font-size:11px;padding:2px 8px}
.flow .gap{height:10px}
.stats{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:20px}
.stat{padding:20px 18px 18px}
.stat .v{font-family:Fraunces,serif;font-weight:900;font-size:54px;line-height:1}
.stat .l{font-size:13.5px;color:var(--ink2);margin-top:6px;line-height:1.3}
.lim{padding:14px 16px;margin-top:14px}
.lim .t{font-family:Fraunces,serif;font-weight:900;font-size:20px;display:flex;align-items:center;gap:8px}
.lim .t .tag{font-family:'Space Grotesk';font-size:11px;padding:2px 8px}
.lim .s{font-size:14px;color:var(--ink2);margin-top:5px;line-height:1.38}
.ck{display:flex;gap:11px;align-items:flex-start;padding:9px 14px;border-top:2px dashed rgba(26,21,35,.25)}
.ck:first-child{border-top:none}
.ck .b{flex:0 0 24px;height:24px;border:2.5px solid var(--ink);border-radius:7px;background:var(--cream);display:flex;align-items:center;justify-content:center}
.ck .b svg{width:15px;height:15px}
.ck .t{font-size:15px;line-height:1.32;color:var(--ink);font-weight:500}
'''


def slide(n, body, cls='', dark=False):
    c = 'var(--cream)' if dark else 'var(--ink)'
    return f'{body}{brand(16, 30, 26, c)}{pnum(n, TOTAL, 32, 30, c)}', cls


def s1():
    return slide(1, f'''
<div class="glow" style="left:-90px;top:-60px;width:400px;height:240px"></div>
<div class="glow" style="right:-80px;bottom:120px;width:320px;height:200px;opacity:.7"></div>
<div class="sun" style="right:40px;top:44px;width:74px;height:74px"></div>
<div class="wrap" style="top:120px">
  <div class="kicker" style="font-size:30px;color:var(--ink)">a true story</div>
  <h1 class="hero" style="font-size:64px;line-height:.98;margin-top:8px">You don’t need <em>a SaaS</em> to track competitors.</h1>
  <div class="pill" style="margin-top:34px;padding:11px 20px;font-family:Fraunces,serif;font-style:italic;font-weight:700;font-size:25px;box-shadow:5px 5px 0 var(--ink);transform:rotate(-1.5deg)">I wrote a cron job instead.</div>
</div>
<div class="kicker" style="position:absolute;right:38px;bottom:70px;font-size:28px;color:var(--ink)">swipe →</div>''', 'sky')


def s2():
    jobs = [('Watch', 'the pages that matter: pricing, product, changelog'), ('Notice', 'when something real changes, not a timestamp'),
            ('Explain', 'what it means for your pitch'), ('Update', 'the battlecard before the next deal')]
    cards = ''.join(f'<div class="card job"><div class="t">{t}</div><div class="s">{s}</div></div>' for t, s in jobs)
    return slide(2, f'''
<div class="wrap">
  {head('the question', 'What does it take to know when a competitor <em>changes pricing</em>?', 28, 38)}
  <div class="lead" style="margin-top:14px">Strip it down and it’s four jobs:</div>
  <div class="jobs">{cards}</div>
  <div class="kicker" style="font-size:25px;margin-top:26px">none of these needs a server running all day.</div>
</div>''')


def s3():
    rows = [
        (1, 'Cron, once a week', 'GitHub Actions in your private repo', '', ''),
        (2, 'Fetch &amp; clean', 'robots.txt first; strip timestamps and noise', 'free', 'ok'),
        (3, 'Diff &amp; filter', 'vs last week; keyword triggers; size threshold', 'free', 'ok'),
        (4, 'AI triage', 'fast model: noise, minor or material', 'capped', 'warn'),
        (5, 'AI analysis', 'stronger model, material changes only', 'capped', 'warn'),
        (6, 'Digest + battlecards', 'committed to your repo; issue, Slack or Discord', '', ''),
    ]
    out = ''
    for i, (n, t, s, tag, cls) in enumerate(rows):
        bg = 'var(--gbg)' if cls == 'ok' else ('var(--abg)' if cls == 'warn' else 'var(--cream2)')
        tg = f'<span class="tag {cls}">{tag}</span>' if tag else ''
        out += f'<div class="card f" style="background:{bg}"><div class="n">{n}</div><div><div class="t">{t}</div><div class="s">{s}</div></div>{tg}</div>'
        if i < len(rows) - 1:
            out += '<div class="gap"></div>'
    return slide(3, f'''
<div class="wrap">
  {head('the method', 'Code watches. <em>AI reads</em> only what changed.', 28, 38)}
  <div class="flow" style="margin-top:20px">{out}</div>
</div>''')


def s4():
    stats = [('211', 'passing tests before the first real website'), ('8', 'real pages across 4 example competitors'),
             ('0', 'AI calls on the second run: nothing changed'), ('$0', 'spent on that run')]
    cards = ''.join(f'<div class="card stat"><div class="v">{v}</div><div class="l">{l}</div></div>' for v, l in stats)
    return slide(4, f'''
<div class="wrap">
  {head('the numbers', 'What the <em>first runs</em> showed', 28, 40)}
  <div class="stats">{cards}</div>
  <div class="card" style="margin-top:18px;padding:13px 16px;background:var(--lav)">
    <div style="font-size:14.5px;line-height:1.4;color:var(--ink2)"><b style="color:var(--ink)">The expensive run is the first:</b> 4 battlecards ≈ <b style="color:var(--ink)">$0.10–0.25</b> on Claude Opus. <span class="tag warn" style="font-size:11px;padding:1px 7px">estimate</span></div>
  </div>
  <div class="kicker" style="font-size:25px;margin-top:22px">the boring run is the whole argument.</div>
</div>''')


def s5():
    lims = [('Convin', 'bad', 'wrong site', 'From my server, it redirected to a US product for home&#8209;service businesses.'),
            ('Hyperbound', 'warn', 'likely A/B test', '<code>/pricing</code> quietly redirected to <code>/pricing-b</code>.'),
            ('Second Nature', 'warn', '208 chars', 'Came back almost empty until one <code>include</code> selector pulled in 4.7k characters.')]
    cards = ''.join(f'<div class="card lim"><div class="t">{t} <span class="tag {c}">{tg}</span></div><div class="s">{s}</div></div>' for t, c, tg, s in lims)
    return slide(5, f'''
<div class="wrap">
  {head('the limits', 'Real websites broke <em>3 assumptions</em>', 28, 40)}
  <div class="lead" style="margin-top:10px;font-size:15px">Examples, not a review of these companies.</div>
  {cards}
  <div class="kicker" style="font-size:23px;margin-top:20px">and: no real competitor change caught yet.</div>
</div>''')


def s6():
    return slide(6, f'''
<div class="wrap">
  {head('the insight', 'The AI was the easy part. <em>The&nbsp;plumbing</em> was the product.', 28, 38, cls='', gap=6)}
  <div class="card" style="margin-top:24px;padding:16px 18px;background:var(--cream2);color:var(--ink);box-shadow:7px 7px 0 var(--coral-dk)">
    <div class="kicker" style="font-size:21px">the battlecard said</div>
    <div style="font-family:Fraunces;font-weight:900;font-size:22px;line-height:1.15;margin-top:4px">“Don’t lead with ‘we support Hindi’.”</div>
    <div style="font-size:14px;color:var(--ink2);margin-top:6px;line-height:1.38">Hyperbound already lists Hindi, Gujarati, Marathi and Tamil.</div>
  </div>
  <div class="kicker" style="font-size:23px;margin-top:30px">what actually broke</div>
  <div style="display:flex;flex-wrap:wrap;gap:10px;margin-top:10px">
    <span class="pill" style="padding:7px 13px;font-size:14.5px;color:var(--ink)">a request format the API rejects</span>
    <span class="pill" style="padding:7px 13px;font-size:14.5px;color:var(--ink)">an npm install that deleted the engine</span>
    <span class="pill" style="padding:7px 13px;font-size:14.5px;color:var(--ink)">Docker reading a comment as the key</span>
    <span class="pill" style="padding:7px 13px;font-size:14.5px;color:var(--ink)">alerts that could ping a Slack channel</span>
  </div>
  <div style="margin-top:18px;font-size:15px;line-height:1.45;color:#E6E1F7">None of them was the model. All of them are fixed.</div>
</div>''', 'dark', dark=True)


def s7():
    items = [checklist_items()[i] for i in (0, 1, 2, 3, 4, 5)]
    rows = ''.join(f'<div class="ck"><div class="b">{TICK}</div><div class="t">{a} <span style="color:var(--ink2);font-weight:400">{b}</span></div></div>' for a, b in items)
    return slide(7, f'''
<div class="wrap">
  {head('the rule', 'Before you trust <em>any AI tool</em>', 28, 40)}
  <div class="card" style="margin-top:18px;padding:4px 0">{rows}</div>
  <div class="card" style="margin-top:18px;padding:12px 16px;background:var(--ink);color:var(--cream);box-shadow:6px 6px 0 var(--coral-dk)">
    <div style="font-family:Fraunces;font-weight:900;font-size:16.5px;line-height:1.25">Rule of thumb: if the pages change <em style="color:var(--coral);font-weight:700">weekly or slower</em>, a cron job beats a subscription.</div>
  </div>
</div>''')


def s8():
    return slide(8, f'''
<div class="glow" style="left:-80px;top:-50px;width:380px;height:220px"></div>
<div class="wrap" style="top:70px">
  <div class="kicker" style="font-size:30px;color:var(--ink)">the takeaway</div>
  <h2 class="hero" style="font-size:52px;line-height:1.0;margin-top:8px">Competitor tracking <em>can be</em> a cron job.</h2>
  <div class="card" style="margin-top:28px;padding:16px 18px">
    <div style="font-family:Fraunces;font-weight:900;font-size:21px">Outflank is free and open source.</div>
    <div style="font-size:14.5px;color:var(--ink2);margin-top:5px;line-height:1.4">Template + repo link in the first comment. Want something like this built for your team? Message me.</div>
  </div>
  <div class="card" style="margin-top:18px;padding:14px 18px;background:var(--ink);color:var(--cream);box-shadow:7px 7px 0 var(--coral-dk)">
    <div class="kicker" style="font-size:22px;color:#FFB3A3">your turn</div>
    <div style="font-family:Fraunces;font-weight:900;font-size:21px;line-height:1.2;margin-top:3px">What would you watch first: pricing pages, changelogs or careers pages?</div>
  </div>
</div>''', 'sky')


SLIDES = [s1, s2, s3, s4, s5, s6, s7, s8]


def carousel_pdf_html(slides):
    css = font_css() + THEME.replace('__W__', str(CW)).replace('__H__', str(CH)) + SLIDE_CSS + f'''
@page{{size:{CW}px {CH}px;margin:0}}
html,body{{width:{CW}px;height:auto;overflow:visible}}
.page{{page-break-after:always;break-after:page}}
.page:last-child{{page-break-after:auto;break-after:auto}}
'''
    pages = ''.join(f'<div class="page {cls}">{body}</div>' for body, cls in slides)
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><style>{css}</style></head><body>{pages}</body></html>'


def main():
    BUILD.mkdir(exist_ok=True)
    SUB.mkdir(parents=True, exist_ok=True)
    CAR.mkdir(parents=True, exist_ok=True)
    for name, fn in SUBSTACK:
        html, h = fn()
        src = BUILD / name.replace('.png', '.html')
        src.write_text(html)
        screenshot(src, SUB / name, SW, h)
        print(f'substack/images/{name}  ({SW * SCALE}x{h * SCALE})')
    built = []
    for i, fn in enumerate(SLIDES, 1):
        body, cls = fn()
        built.append((body, cls))
        src = BUILD / f'slide-{i:02d}.html'
        src.write_text(page(CW, CH, body, SLIDE_CSS, cls))
        screenshot(src, CAR / f'slide-{i:02d}.png', CW, CH)
        print(f'linkedin/carousel/slide-{i:02d}.png  ({CW * SCALE}x{CH * SCALE})')
    pdf_src = BUILD / 'carousel.html'
    pdf_src.write_text(carousel_pdf_html(built))
    print_pdf(pdf_src, CAR / 'carousel.pdf')
    pages = len(re.findall(rb'/Type\s*/Page(?!s)', (CAR / 'carousel.pdf').read_bytes()))
    print(f'linkedin/carousel/carousel.pdf  ({pages} pages)')
    if pages != TOTAL:
        sys.exit(f'PDF has {pages} pages, expected {TOTAL}')


if __name__ == '__main__':
    main()
