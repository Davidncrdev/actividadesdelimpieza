"""Extrae el contenido de las páginas antiguas a build/data/*.json (ejecutar una sola vez)."""
import re, glob, json, html, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

def strip_svg(s): return re.sub(r'<svg>.*?</svg>', '', s, flags=re.S)
def text(s): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', s))).strip()

def meta(s, name, attr='name'):
    m = re.search(r'<meta %s="%s" content="(.*?)">' % (attr, re.escape(name)), s)
    return html.unescape(m.group(1)) if m else ''

def page_meta(s):
    return {
        'title': text(re.search(r'<title>(.*?)</title>', s, re.S).group(1)),
        'desc': meta(s, 'description'),
        'og_title': meta(s, 'og:title', 'property'),
        'og_desc': meta(s, 'og:description', 'property'),
    }

pages = {}
for f in sorted(glob.glob('limpieza-*.html')):
    slug = f[:-5]
    s = open(f, encoding='utf-8').read()
    d = page_meta(s)
    art = re.search(r'<article class="prose"[^>]*>(.*?)</article>', s, re.S).group(1)
    art = strip_svg(art)
    i = art.find('<h2>Preguntas frecuentes')
    prose, faq_html = art[:i], art[i:]
    faq = []
    for q, a in re.findall(r'<button class="faq-q"[^>]*>(.*?)</button>.*?<div class="faq-a-inner">\s*(.*?)\s*</div>\s*</div>\s*</div>', faq_html, re.S):
        faq.append({'q': text(q), 'a': re.sub(r'^<p>|</p>$', '', a.strip())})
    faq_h2 = text(re.search(r'<h2>(.*?)</h2>', faq_html).group(1))
    bq = re.search(r'<blockquote>(.*?)</blockquote>', prose, re.S)
    quote = text(bq.group(1)) if bq else ''
    prose = re.sub(r'\s*<blockquote>.*?</blockquote>', '', prose, flags=re.S)
    h1 = text(re.search(r'<h1[^>]*>(.*?)</h1>', s, re.S).group(1))
    lede = text(re.search(r'<p class="lede"[^>]*>(.*?)</p>', s, re.S).group(1))
    checks = []
    ul = re.search(r'<ul class="checks">(.*?)</ul>', s, re.S)
    if ul:
        for li in re.findall(r'<li>(.*?)</li>', strip_svg(ul.group(1)), re.S):
            m = re.match(r'\s*<b>(.*?)</b>\s*(.*)', li, re.S)
            checks.append({'b': text(m.group(1)).rstrip(':'), 't': text(m.group(2))} if m else {'b': '', 't': text(li)})
    aside_h2 = text(re.search(r'<div class="sticky-col"[^>]*>.*?<h2[^>]*>(.*?)</h2>', s, re.S).group(1))
    aside_eyebrow = text(re.search(r'<div class="sticky-col"[^>]*>.*?<span class="eyebrow">(.*?)</span>', s, re.S).group(1))
    near = re.findall(r'class="service-card" href="/([^"]+)"', s)
    wa = re.search(r'wa\.me/34642118972\?text=([^"]+)" data-ctx="hero"', s)
    cta = re.search(r'<div class="cta-panel".*?<p class="lede">(.*?)</p>', s, re.S)
    img = re.search(r'<img src="https://images\.unsplash[^"]*" alt="([^"]*)"', s)
    pages[slug] = {**d, 'h1_old': h1, 'lede': lede, 'checks': checks, 'aside_h2': aside_h2, 'aside_eyebrow': aside_eyebrow,
                   'prose': re.sub(r'\n\s*\n', '\n', prose).strip(), 'quote': quote, 'faq': faq, 'faq_h2': faq_h2,
                   'near': near, 'wa_text': html.unescape(wa.group(1)) if wa else '', 'cta_lede': text(cta.group(1)) if cta else '',
                   'img_alt': html.unescape(img.group(1)) if img else ''}
json.dump(pages, open('build/data/pages.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# blog
posts = {}
for f in sorted(glob.glob('blog/*.html')):
    slug = f[5:-5]
    s = open(f, encoding='utf-8').read()
    d = page_meta(s)
    body = re.search(r'<div class="article-body prose"[^>]*>(.*?)</div>\s*<div class="cta-panel"', s, re.S).group(1)
    cat = text(re.search(r'<span class="chip">(.*?)</span>', strip_svg(s)).group(1)).replace('Blog · ', '')
    h1 = text(re.search(r'<h1[^>]*>(.*?)</h1>', s, re.S).group(1))
    lede = text(re.search(r'<p class="lede"[^>]*>(.*?)</p>', s, re.S).group(1))
    date = re.search(r'"datePublished": "(\d{4}-\d{2}-\d{2})', s).group(1)
    mins = re.search(r'(\d+) min de lectura', s).group(1)
    posts[slug] = {**d, 'h1': h1, 'lede': lede, 'cat': cat, 'date': date, 'mins': int(mins), 'body': strip_svg(body).strip()}
json.dump(posts, open('build/data/posts_old.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# legales
legal = {}
for slug in ['aviso-legal', 'cookies', 'politica-privacidad']:
    s = open(slug + '.html', encoding='utf-8').read()
    d = page_meta(s)
    body = re.search(r'<div class="prose"[^>]*>(.*?)</div>\s*</div>\s*</section>', s, re.S).group(1)
    lede = text(re.search(r'<p class="lede"[^>]*>(.*?)</p>', s, re.S).group(1))
    h1 = text(re.search(r'<h1[^>]*>(.*?)</h1>', s, re.S).group(1))
    legal[slug] = {**d, 'h1': h1, 'lede': lede, 'body': strip_svg(body).strip()}
json.dump(legal, open('build/data/legal.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print({k: len(v['prose']) for k, v in pages.items()}, list(posts), list(legal))
