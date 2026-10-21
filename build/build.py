#!/usr/bin/env python3
"""Genera el sitio estático. Uso: python3 build/build.py  (desde la raíz del proyecto)."""
import html, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from siteinfo import *            # noqa: F401,F403
from posts_new import POSTS_NEW
from redirects import build_redirects

os.chdir(ROOT)
esc = lambda s: html.escape(s, quote=True)
PAGES = json.load(open('build/data/pages.json', encoding='utf-8'))
POSTS_OLD = json.load(open('build/data/posts_old.json', encoding='utf-8'))
LEGAL = json.load(open('build/data/legal.json', encoding='utf-8'))
WRITTEN = []

ARROW = '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="square" aria-hidden="true"><path d="M4 12h16M14 6l6 6-6 6"/></svg>'
ARROW_L = '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="square" aria-hidden="true"><path d="M20 12H4M10 6l-6 6 6 6"/></svg>'
WAICON = '<svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor" aria-hidden="true"><path d="M17.5 14.4c-.3-.15-1.76-.87-2.03-.97-.27-.1-.47-.15-.67.15-.2.3-.77.97-.94 1.17-.17.2-.35.22-.64.07-.3-.15-1.26-.46-2.4-1.48-.89-.79-1.49-1.77-1.66-2.07-.17-.3-.02-.46.13-.6.13-.13.3-.35.45-.52.15-.17.2-.3.3-.5.1-.2.05-.37-.02-.52-.08-.15-.67-1.61-.92-2.2-.24-.58-.49-.5-.67-.5h-.57c-.2 0-.52.07-.8.37-.27.3-1.04 1.02-1.04 2.48 0 1.46 1.07 2.88 1.22 3.08.15.2 2.1 3.2 5.08 4.49.71.3 1.26.49 1.69.63.71.23 1.36.2 1.87.12.57-.08 1.76-.72 2-1.41.25-.7.25-1.29.17-1.41-.07-.13-.27-.2-.57-.35zM12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2z"/></svg>'


def write(path, content):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    open(path, 'w', encoding='utf-8').write(content)
    WRITTEN.append(path)


def url(slug):
    return DOMAIN + ('/' if slug in ('', 'index') else '/' + slug)


def jsonld(*objs):
    return ''.join('<script type="application/ld+json">%s</script>\n' % json.dumps(o, ensure_ascii=False, separators=(',', ':')) for o in objs)


BUSINESS = {
    '@context': 'https://schema.org', '@type': 'LocalBusiness', '@id': DOMAIN + '/#negocio',
    'name': BRAND, 'url': DOMAIN + '/', 'telephone': '+' + WA, 'email': EMAIL,
    'description': 'Empresa de limpieza profesional en Málaga y provincia desde 2008: comunidades, oficinas, colegios, polideportivos, parkings, maquinaria y fin de obra.',
    'image': DOMAIN + '/og-image.jpg', 'logo': DOMAIN + '/logo.png', 'priceRange': '€€', 'foundingDate': '2008',
    'address': {'@type': 'PostalAddress', 'addressLocality': 'Málaga', 'addressRegion': 'Andalucía', 'addressCountry': 'ES'},
    'geo': {'@type': 'GeoCoordinates', 'latitude': 36.7213, 'longitude': -4.4214},
    'openingHoursSpecification': {'@type': 'OpeningHoursSpecification', 'dayOfWeek': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'], 'opens': '08:00', 'closes': '19:00'},
    'areaServed': [{'@type': 'City', 'name': z['short']} for z in ZONES],
    'makesOffer': [{'@type': 'Offer', 'itemOffered': {'@type': 'Service', 'name': s['full'], 'url': url(s['slug'])}} for s in SERVICES],
}
WEBSITE = {'@context': 'https://schema.org', '@type': 'WebSite', '@id': DOMAIN + '/#web', 'name': BRAND, 'url': DOMAIN + '/', 'inLanguage': 'es-ES', 'publisher': {'@id': DOMAIN + '/#negocio'}}


def breadcrumb(items):
    return {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        dict({'@type': 'ListItem', 'position': i + 1, 'name': n}, **({'item': u} if u else {})) for i, (n, u) in enumerate(items)]}


def faq_ld(faq):
    strip = lambda t: re.sub(r'<[^>]+>', '', t)
    return {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': f['q'], 'acceptedAnswer': {'@type': 'Answer', 'text': strip(f['a'])}} for f in faq]}


GTM = """<script>
window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}
gtag('consent','default',{'ad_storage':'denied','analytics_storage':'denied','ad_user_data':'denied','ad_personalization':'denied'});
(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);})(window,document,'script','dataLayer','GTM-T75K8RBJ');
</script>"""

# recortes en zigzag para la hoja de la carta
N = 16
def _zig():
    top = []
    for i in range(N + 1):
        x = '%.3f%%' % (100 * i / N)
        top.append('%s %s' % (x, '10px' if i % 2 == 0 else '0'))
    bot = []
    for i in range(N, -1, -1):
        x = '%.3f%%' % (100 * i / N)
        bot.append('%s %s' % (x, 'calc(100% - 10px)' if i % 2 == 0 else '100%'))
    return 'polygon(%s)' % ', '.join(top + bot)
ZIG = _zig()


def picture(im, alt, cls='', lazy=True, extra=''):
    return '<img src="%s" alt="%s" width="%d" height="%d"%s%s%s>' % (
        im['src'], esc(alt), im['w'], im['h'], ' class="%s"' % cls if cls else '', ' loading="lazy" decoding="async"' if lazy else ' fetchpriority="high"', extra)


def credit_line(im, prefix=''):
    if im['url']:
        return '<p class="credit">%s<a href="%s" rel="noopener">%s</a></p>' % (prefix, esc(im['url']), esc(im['credit']))
    return '<p class="credit">%s%s</p>' % (prefix, esc(im['credit']))


def head(title, desc, path, *, og_type='website', ld='', og_img=None, robots='index, follow', preload=''):
    canon = url(path)
    og = og_img or DOMAIN + '/og-image.jpg'
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="{robots}">
<meta name="theme-color" content="#38450f">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:locale" content="es_ES">
<meta property="og:image" content="{og}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{og}">
<link rel="icon" href="/icon-192.png" type="image/png" sizes="192x192">
<link rel="apple-touch-icon" href="/icon-192.png">
<link rel="manifest" href="/manifest.json">
<link rel="preload" href="/assets/fonts/inter-var.woff2" as="font" type="font/woff2" crossorigin>
{preload}<link rel="stylesheet" href="/css/styles.css?v=6">
{GTM}
{ld}<script>document.documentElement.classList.add('js');</script>
</head>
"""


def bar(page, home=False):
    links = ''.join('<a href="%s"%s>%s</a>' % (h, ' aria-current="page"' if page == h else '', n) for n, h in NAV)
    return f"""<a class="skip" href="#main">Saltar al contenido</a>
<header class="bar{' is-over' if home else ''}" data-bar>
  <a class="wordmark" href="/" aria-label="{BRAND}, inicio">{BRAND}</a>
  <nav class="bar-nav" aria-label="Principal">{links}</nav>
  <a class="bar-tel" href="tel:{TEL}" data-ctx="bar">{PHONE}</a>
  <a class="btn" href="/presupuesto">Presupuesto</a>
  <button class="bar-burger" type="button" aria-expanded="false" aria-controls="menu">Menú</button>
</header>
<div class="menu" id="menu" role="dialog" aria-label="Menú" aria-modal="true">
  <button class="menu-close" type="button">Cerrar</button>
  {''.join('<a href="%s">%s</a>' % (h, n) for n, h in NAV)}
  <a class="btn btn-paper" href="/presupuesto">Pedir presupuesto</a>
</div>
"""


def stub():
    return f"""<div class="stub" data-stub aria-label="Acciones rápidas">
  <a class="btn btn-paper stub-call" href="tel:{TEL}" data-ctx="stub">Llamar</a>
  <a class="btn" href="/presupuesto">Pedir presupuesto</a>
  <a class="stub-tel" href="tel:{TEL}" data-ctx="stub">{PHONE}</a>
</div>
"""


def cookie_html():
    return """<div class="cookie" data-cookie role="region" aria-label="Aviso de cookies">
  <p>Usamos cookies técnicas y, solo si lo aceptas, de analítica para medir el uso del sitio. <a href="/cookies">Más información</a>.</p>
  <div class="cookie-actions"><button class="btn" type="button" data-consent="accept">Aceptar</button><button class="btn alt" type="button" data-consent="decline">Rechazar</button></div>
</div>
"""


def reply(heading='Pide tu presupuesto', text='Cuéntanos qué espacio quieres limpiar y cada cuánto. Respondemos en 24 horas laborables.',
          copy='Sin letra pequeña y sin permanencia: si algo no te convence, se ajusta o se cancela con un preaviso.', wa_text='Hola, me gustaría pedir un presupuesto de limpieza.', cls='reply'):
    return f"""<section class="{cls} field on-field" aria-labelledby="reply-h">
  <div class="wrap reply-grid">
    <p class="reply-copy" data-reveal>{esc(copy)}</p>
    <div class="reply-card sheet" data-reveal style="--d:120ms">
      <h2 id="reply-h">{esc(heading)}</h2>
      <p>{esc(text)}</p>
      <a class="btn btn-block" href="/presupuesto">Pedir presupuesto {ARROW}</a>
      <p class="alt">o escribe por <a href="{wa_link(wa_text)}" data-ctx="reply">WhatsApp</a> · <a href="tel:{TEL}">{PHONE}</a></p>
    </div>
  </div>
</section>
"""


def footer():
    sv = ''.join('<li><a href="/%s">%s</a></li>' % (s['slug'], s['name']) for s in SERVICES)
    zn = ''.join('<li><a href="/%s">%s</a></li>' % (z['slug'], z['short']) for z in ZONES)
    st = img('malaga-muelle-uno')
    return f"""<footer class="back">
  <div class="back-panel" data-reveal>
    <div class="back-grid">
      <div>
        <h2>Hasta pronto</h2>
        <p class="back-msg">Escríbenos o llámanos: respondemos en horario laborable y, si hace falta, visitamos el espacio sin coste.</p>
        <div class="back-links">
          <div><h3>Servicios</h3><ul>{sv}</ul></div>
          <div><h3>Zonas</h3><ul>{zn}</ul></div>
        </div>
      </div>
      <div class="back-addr">
        <div class="stamp" aria-hidden="true"><img src="{st['src']}" alt="" width="{st['w']}" height="{st['h']}" loading="lazy"></div>
        <ul>
          <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
          <li><a href="tel:{TEL}" data-ctx="footer">{PHONE}</a></li>
          <li><a href="{wa_link('Hola, me gustaría pedir un presupuesto de limpieza.')}" data-ctx="footer">WhatsApp</a></li>
          <li>Málaga y provincia · Lun–Vie 8:00–19:00</li>
          <li><a href="/presupuesto">Presupuesto gratis</a> · <a href="/blog">Blog</a> · <a href="/sobre-nosotros">Nosotros</a></li>
        </ul>
        <img class="back-logo" src="/logo.png" alt="{BRAND}" width="280" height="120" loading="lazy">
      </div>
    </div>
    <p class="imprint">© <span data-year>2026</span> {BRAND} · <a href="/politica-privacidad">Privacidad</a> · <a href="/aviso-legal">Aviso legal</a> · <a href="/cookies">Cookies</a> · <a href="/creditos">Créditos de las imágenes</a></p>
  </div>
</footer>
"""


def page(path, title, desc, body, *, page_nav=None, home=False, ld='', og_type='website', og_img=None, robots='index, follow', preload='', with_stub=True, extra_script=''):
    h = head(title, desc, path, og_type=og_type, ld=ld, og_img=og_img, robots=robots, preload=preload)
    out = h + '<body%s>\n<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-T75K8RBJ" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>\n' % (' data-home' if home else '')
    out += cookie_html() + bar(page_nav or '/' + path, home)
    out += '<main id="main">\n' + body + '\n</main>\n' + footer() + (stub() if with_stub else '')
    out += '<script src="/js/app.js?v=6" defer></script>\n' + extra_script + '</body>\n</html>\n'
    write(('index' if path in ('', 'index') else path) + '.html', out)


def crumbs(items):
    lis = ''.join('<li>%s</li>' % ('<a href="%s">%s</a>' % (u, n) if u else '<span aria-current="page">%s</span>' % n) for n, u in items)
    return '<nav class="crumbs" aria-label="Migas de pan"><ol>%s</ol></nav>' % lis


def accordion(faq, open_first=True):
    out = []
    for i, f in enumerate(faq):
        out.append('<details%s><summary>%s<span class="chev" aria-hidden="true"></span></summary><div class="answer"><p>%s</p></div></details>' % (' open' if (i == 0 and open_first) else '', esc(f['q']), f['a']))
    return '<div class="accordion">%s</div>' % ''.join(out)


H2_SHORT = {
    'Limpieza profesional en Benalmádena, tres pueblos y una marina': 'Limpieza en Benalmádena: tres pueblos y una marina',
    'Urbanizaciones grandes con piscina y administradores en Benalmádena': 'Urbanizaciones grandes con piscina en Benalmádena',
    'Productos pensados para niños: hipoalergénicos y virucidas': 'Productos pensados para niños: hipoalergénicos',
    'Preguntas frecuentes sobre limpieza de colegios en Málaga': 'Preguntas frecuentes sobre limpieza de colegios',
    'Para administradores de fincas: un proveedor que no da guerra': 'Para administradores de fincas: sin dar guerra',
    'Limpieza profesional en Fuengirola, de la playa a Las Lagunas': 'Limpieza en Fuengirola, de la playa a Las Lagunas',
    'Comunidades de la costa y urbanizaciones de Las Lagunas': 'Comunidades de la costa y Las Lagunas',
    'Limpieza profesional en Málaga capital, de punta a punta': 'Limpieza en Málaga capital, de punta a punta',
    'Comunidades y administradores de fincas en Málaga capital': 'Comunidades y administradores en Málaga capital',
    'Limpieza profesional en Marbella, sin ruido y con resultados': 'Limpieza en Marbella, sin ruido y con resultados',
    'La limpieza en Mijas, del blanco del pueblo al bullicio de la costa': 'Limpieza en Mijas: del pueblo blanco a la costa',
    'Oficinas, clínicas y despachos: cada espacio, su protocolo': 'Oficinas, clínicas y despachos: un protocolo cada uno',
    'Preguntas frecuentes sobre limpieza de oficinas en Málaga': 'Preguntas frecuentes sobre limpieza de oficinas',
    'El problema de los vestuarios: hongos, bacterias y olores': 'Vestuarios: hongos, bacterias y olores',
    'Frecuencias y horarios: sin tocar entrenamientos ni torneos': 'Horarios que respetan entrenamientos y torneos',
    'Para administradores de fincas y comunidades de la costa este': 'Para administradores de la costa este',
    'Limpieza profesional en Torremolinos, del paseo a El Pinillo': 'Limpieza en Torremolinos, del paseo a El Pinillo',
    'Comunidades con piscina y apartamentos turísticos en Torremolinos': 'Piscinas y apartamentos turísticos en Torremolinos',
    'Vélez-Málaga, de la iglesia de Santa María al paseo de Torre del Mar': 'Vélez-Málaga, de Santa María a Torre del Mar',
    'Limpieza profesional en Estepona, entre macetas y playa': 'Limpieza en Estepona, entre macetas y playa',
}


CLAIMS = [
    (': más de 5.000 servicios realizados y 127 clientes activos que renuevan mes a mes.', ', sin depender de subcontratas.'),
    (': más de 5.000 servicios realizados y 127 clientes activos.', '.'),
    (': más de 5.000 servicios realizados y 127 clientes activos que renuevan mes a mes, en parte porque nunca', ', en parte porque nunca'),
    ('responde una empresa con más de 5.000 servicios a sus espaldas, no un particular', 'responde una empresa con equipo propio y seguro, no un particular'),
    (': más de 5.000 servicios realizados y 127 clientes activos que confían temporada tras temporada.', ', temporada tras temporada.'),
]


def prose_clean(h):
    for a, b in CLAIMS:
        h = h.replace(a, b)
    for a, b in H2_SHORT.items():
        h = h.replace(a, b)
    h = re.sub(r'<figure.*?</figure>', '', h, flags=re.S)
    h = re.sub(r'(<table.*?</table>)', r'<div class="scroll">\1</div>', h, flags=re.S)
    h = re.sub(r'\n\s*', '\n', h)
    return h


def bar_links(items, cls=''):
    return '<div class="bar-links %s">%s</div>' % (cls, ''.join('<a href="%s" data-reveal>%s%s%s</a>' % (h, '<span>%s</span>' % n, '<small>%s</small>' % s if s else '', ARROW) for n, h, s in items))


# ═════════════════ HOME ═════════════════
FAQ_HOME = [
    dict(q='¿Qué zonas de Málaga cubrís?', a='Toda la provincia: la capital (Centro, Teatinos, Carretera de Cádiz, Cruz de Humilladero, Puerto de la Torre, El Palo), la Costa del Sol (Torremolinos, Benalmádena, Fuengirola, Mijas, Marbella, Estepona), Rincón de la Victoria, Vélez-Málaga y Antequera. Si tu zona no aparece, escríbenos: valoramos cada caso. <a href="/zonas">Ver las zonas</a>.'),
    dict(q='¿El presupuesto es gratis y sin compromiso?', a='Sí. Visitamos el espacio si hace falta y te enviamos una propuesta detallada en menos de 24 horas laborables: tareas, frecuencias y precio cerrado. No firmas nada hasta que lo apruebas.'),
    dict(q='¿Qué productos utilizáis?', a='Productos profesionales ecológicos, biodegradables y seguros para personas, mascotas y superficies. En colegios, clínicas y centros deportivos aplicamos protocolos específicos de desinfección.'),
    dict(q='¿Con qué frecuencia hacéis los servicios?', a='Diaria, semanal, quincenal o mensual, según el espacio y su uso. También hacemos limpiezas puntuales: fin de obra, puesta a punto de viviendas, eventos y servicios extraordinarios.'),
    dict(q='¿El personal está asegurado y cualificado?', a='Sí. Todo el equipo está dado de alta en la Seguridad Social, con seguro de responsabilidad civil, y recibe formación continua en técnicas de limpieza, maquinaria y protocolos de seguridad.'),
    dict(q='¿Hay permanencia?', a='No. Si el servicio no te convence, lo ajustamos o lo cancelamos con un simple preaviso. Preferimos que nos elijas por resultados, no por contrato.'),
]

MOMENTS = [
    ('Nos cuentas qué necesitas', 'Por teléfono, WhatsApp o formulario: superficie, uso y horarios.', 'blog-obra', 'Persona dibujando un plano sobre una mesa de trabajo'),
    ('Visitamos el espacio', 'Si hace falta, medimos y vemos el uso real. Sin coste.', 'oficinas', 'Pasillo de oficina con mamparas de cristal y suelo pulido'),
    ('Presupuesto en 24 horas', 'Tareas, frecuencias, productos y precio cerrado, por escrito.', 'colegios', 'Aula vacía y ordenada, con pupitres y pizarra'),
    ('Empieza el servicio', 'Equipo asignado, checklist en cada visita y una persona de contacto.', 'comunidades', 'Persona limpiando una ventana con persianas de madera'),
    ('Revisamos contigo', 'Seguimiento periódico y ajustes cuando algo cambia.', 'fin-de-obra', 'Cuarto de baño recién terminado, con ducha de cristal y encimera'),
]


def tasks_html(space, freq):
    slug, items = CHECKLISTS[space]
    label = {'v': {'Diaria': 'cada día', 'Semanal': 'cada visita', 'Quincenal': 'cada visita', 'Puntual': 'una vez'}[freq], 'm': 'cada mes' if freq != 'Puntual' else 'una vez', 'x': 'a petición'}
    return ''.join('<li><span class="tick" aria-hidden="true"></span><span>%s</span><span class="leader" aria-hidden="true"></span><em>%s</em></li>' % (n, label[t]) for n, t in items)


def build_home():
    hero = img('malaga-larios')
    sg = []
    for gi, gname in enumerate(GROUPS):
        items = ''.join(
            '<a class="menu-item" href="/%s"><span class="menu-row"><b>%s</b><span class="leader" aria-hidden="true"></span><em>%s</em></span><p>%s</p></a>' % (s['slug'], s['name'], s['value'], s['blurb'])
            for s in SERVICES if s['group'] == gi)
        sg.append('<div class="menu-group" data-reveal><h3>%s</h3>%s</div>' % (gname, items))
    picks_sp = ''.join('<button type="button" aria-pressed="%s" data-space="%s">%s</button>' % ('true' if k == 'Comunidad' else 'false', k, k) for k in CHECKLISTS)
    picks_fr = ''.join('<button type="button" aria-pressed="%s" data-freq="%s">%s</button>' % ('true' if k == 'Semanal' else 'false', k, k) for k in FREQS)
    moments = ''.join(
        '<li class="moment"><h3>%s</h3><p>%s</p>%s</li>' % (t, d, picture(img(k), a)) for t, d, k, a in MOMENTS)
    zones = ''.join(
        '<details%s><summary>%s<span class="plus" aria-hidden="true"></span></summary><div class="panel"><p>%s <b>%s</b></p><a class="btn-text" href="/%s">Limpieza en %s</a></div></details>' % (
            ' open' if i == 0 else '', z['name'], z['hoods'], z['hook'], z['slug'], z['short']) for i, z in enumerate(ZONES))
    qa_t, qa_s, vis = img('malaga-catedral'), img('malaga-muelle-uno'), img('malaga-gibralfaro')
    body = f"""
<section class="hero" data-hero aria-label="Presentación">
  <div class="hero-stage">
    {picture(hero, 'Calle Larios de Málaga, con sus edificios de ladrillo y balcones de forja, el suelo de mármol pulido y farolas con flores', 'hero-photo', lazy=False)}
    <div class="hero-card" data-hero-card>
      <div class="hero-card-body" data-hero-body>
        <h1 class="hero-title"><span>Empresa</span><span>de limpieza</span><span>en Málaga</span></h1>
        <div>
          <ul class="hero-facts">
            <li>Comunidades, oficinas, colegios y obras</li>
            <li>Presupuesto cerrado en 24 h laborables</li>
            <li>Sin permanencia. En Málaga desde 2008</li>
          </ul>
          <p class="hero-sentence">Equipo propio, productos ecológicos y un checklist en cada visita.</p>
        </div>
        <div class="hero-foot">
          <p class="hero-credit">Calle Larios, Málaga. Foto: {esc(hero['short'])}</p>
          <a class="btn" href="/presupuesto" data-ctx="hero">Pedir presupuesto</a>
          <a class="btn-text" href="tel:{TEL}" data-ctx="hero">Llamar {PHONE}</a>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="field on-field menu-field" id="servicios" aria-labelledby="carta">
  <div class="wrap">
    <div class="sheet sheet-menu">
      <h2 id="carta" data-reveal>Qué limpiamos</h2>
      {''.join(sg)}
      <p class="menu-foot" data-reveal><a class="btn-text" href="/servicios">Ver todos los servicios</a></p>
    </div>
  </div>
</section>

<section class="section" id="hoja" aria-labelledby="hoja-h">
  <div class="wrap control">
    <div class="control-copy">
      <h2 id="hoja-h" data-reveal>Tu hoja de control</h2>
      <p class="statement" data-reveal style="--d:80ms">Cada visita termina con una hoja como esta, revisada y firmada. Elige tu espacio y mira qué incluye.</p>
      <p class="pick-label" data-reveal style="--d:120ms">Qué quieres limpiar</p>
      <div class="pick" role="group" aria-label="Tipo de espacio" data-reveal style="--d:140ms">{picks_sp}</div>
      <p class="pick-label" data-reveal style="--d:160ms">Cada cuánto</p>
      <div class="pick" role="group" aria-label="Frecuencia" data-reveal style="--d:180ms">{picks_fr}</div>
    </div>
    <div class="sheet sheet-control" data-reveal style="--d:120ms" data-sheet>
      <header><h3 data-sheet-title>Hoja de control · Comunidad</h3><span class="small muted" data-sheet-freq>Visitas: semanales</span></header>
      <ul class="tasks" data-tasks aria-live="polite">{tasks_html('Comunidad', 'Semanal')}</ul>
      <div class="sign"><span>Firma del equipo</span><span>Firma del cliente</span></div>
      <div class="sheet-actions">
        <a class="btn" href="/presupuesto" data-sheet-quote>Pedir presupuesto de esta hoja</a>
        <a class="btn-text" href="{wa_link('Hola, me gustaría un presupuesto de limpieza.')}" data-sheet-wa data-ctx="hoja">Enviar por WhatsApp</a>
      </div>
    </div>
  </div>
</section>

<section class="section field-surface" id="proceso" aria-labelledby="proc-h" style="padding-bottom:calc(var(--gap-section)*0.7)">
  <div class="wrap">
    <div class="rail-head">
      <h2 id="proc-h" data-reveal>Cómo trabajamos</h2>
      <div class="rail-btns" data-reveal><button type="button" data-rail="-1" aria-label="Anterior">{ARROW_L}</button><button type="button" data-rail="1" aria-label="Siguiente">{ARROW}</button></div>
    </div>
    <div class="rail-bar" aria-hidden="true"><i data-rail-bar></i></div>
  </div>
  <ol class="rail" data-rail-track tabindex="0" aria-label="Pasos del servicio">{moments}<li class="rail-end" aria-hidden="true"></li></ol>
  <div class="wrap"><p class="credit" style="margin-top:24px">Imágenes de archivo con licencia Unsplash, a modo ilustrativo.</p></div>
</section>

<section class="section" id="zonas" aria-labelledby="zonas-h">
  <div class="wrap">
    <div class="zones">
      <h2 class="giant" id="zonas-h" data-reveal>Zonas</h2>
      <div class="bars" data-reveal style="--d:100ms">{zones}</div>
      <p style="margin-top:24px"><a class="btn-text" href="/zonas">Ver todas las zonas de servicio</a></p>
    </div>
  </div>
</section>

<section class="qa-sec field-surface" id="faq" aria-labelledby="faq-h">
  <div class="wrap qa">
    <div class="qa-copy">
      <h2 id="faq-h" data-reveal>Preguntas frecuentes</h2>
      <ul class="qa-facts" data-reveal style="--d:80ms"><li>Lun–Vie, 8:00–19:00</li><li>Málaga y provincia</li><li>Presupuesto en 24 h laborables</li></ul>
      <div data-reveal style="--d:120ms">{accordion(FAQ_HOME)}</div>
      <div class="qa-actions"><a class="btn" href="/presupuesto">Pedir presupuesto</a><a class="btn-text" href="/contacto">Hablar con nosotros</a></div>
    </div>
    <div class="qa-media" data-reveal="clip">
      {picture(qa_t, 'Catedral de Málaga, de noche, vista desde la calle', 'qa-tall')}
      {picture(qa_s, 'Paseo del Muelle Uno en el puerto de Málaga', 'qa-sq')}
      <p class="credit">{esc(qa_t['short'])} · {esc(qa_s['short'])}</p>
    </div>
  </div>
</section>

{reply(wa_text='Hola, me gustaría pedir un presupuesto de limpieza.')}

<section class="visit" aria-labelledby="visit-h">
  <video class="visit-photo" autoplay muted loop playsinline preload="metadata" poster="/assets/video/malaga-panoramica.jpg" aria-label="Panorámica de la costa de Málaga desde el castillo de Santa Catalina" data-loop>
    <source src="/assets/video/malaga-panoramica.webm" type="video/webm"><source src="/assets/video/malaga-panoramica.mp4" type="video/mp4">
  </video>
  <div class="visit-inner">
    <div class="visit-card" data-reveal>
      <h2 id="visit-h">Hablemos</h2>
      <p>Málaga y provincia</p>
      <div class="hours"><div><span>Lunes a viernes</span><span>8:00–19:00</span></div><div><span>Sábado y domingo</span><span>cerrado</span></div></div>
      <a class="tel" href="tel:{TEL}" data-ctx="visit">{PHONE}</a>
      <p><a href="mailto:{EMAIL}">{EMAIL}</a></p>
      <a class="btn btn-block" href="/presupuesto">Pedir presupuesto</a>
    </div>
    <p class="visit-credit">Costa de Málaga desde el castillo de Santa Catalina. Vídeo: Daniel Capilla, CC BY-SA 4.0</p>
  </div>
</section>
"""
    ld = jsonld(BUSINESS, WEBSITE, faq_ld(FAQ_HOME))
    page('', 'Empresa de Limpieza en Málaga | Actividades de Limpieza',
         'Empresa de limpieza en Málaga desde 2008. Comunidades, oficinas, colegios, parkings y fin de obra. Presupuesto gratis en 24 h, sin permanencia.',
         body, page_nav='/', home=True, ld=ld, preload='<link rel="preload" as="image" href="%s" fetchpriority="high">\n' % hero['src'],
         extra_script='<script>window.ADL_LISTS=%s;</script>\n' % json.dumps(dict({k: {'service': SERVICE_BY_SLUG[v[0]]['full'], 'tasks': [list(t) for t in v[1]]} for k, v in CHECKLISTS.items()}, _wa=WA), ensure_ascii=False))


# ═════════════════ COMPONENTES DE PÁGINA INTERIOR ═════════════════
def credit_inline(im):
    if im['url']:
        return 'Foto: <a href="%s" rel="noopener">%s</a>' % (esc(im['url']), esc(im['short']))
    return 'Imagen de archivo, a modo ilustrativo'


def split(crumb_items, h1, lede, actions, im, alt, meta_html=''):
    return f"""<section class="split">
  <div class="split-copy">
    {crumbs(crumb_items)}
    <h1 data-reveal>{esc(h1)}</h1>
    <p class="statement" data-reveal style="--d:80ms">{esc(lede)}</p>
    {meta_html}
    <div class="phero-actions" data-reveal style="--d:140ms">{actions}</div>
  </div>
  <figure class="split-media" data-reveal="clip">{picture(im, alt, lazy=False)}<figcaption class="credit">{credit_inline(im)}</figcaption></figure>
</section>"""


def thumb_links(items):
    out = ''
    for name, href, sub, key, alt in items:
        out += '<a href="%s" data-reveal>%s<span><b>%s</b>%s</span>%s</a>' % (href, picture(img(key), alt), name, '<small>%s</small>' % sub if sub else '', ARROW)
    return '<div class="thumb-links">%s</div>' % out


def zone_items(slugs):
    return [('Limpieza en ' + ZONE_BY_SLUG[n]['name'], '/' + n, ZONE_BY_SLUG[n]['hook'], ZONE_BY_SLUG[n]['img'], ZONE_BY_SLUG[n]['alt']) for n in slugs]


def service_items(slugs):
    return [(SERVICE_BY_SLUG[n]['full'], '/' + n, SERVICE_BY_SLUG[n]['value'].capitalize(), SERVICE_BY_SLUG[n]['img'], STOCK[SERVICE_BY_SLUG[n]['img']]) for n in slugs]


def zones_section(slugs, title='Dónde trabajamos'):
    return '<section class="related" aria-label="%s"><h2>%s</h2>%s</section>' % (title, title, thumb_links(zone_items(slugs)))


# ═════════════════ SERVICIOS / ZONAS (índices) ═════════════════
def build_servicios():
    rows = ''.join(
        '<a href="/%s" data-reveal><div><h2>%s</h2><p>%s</p><p class="small muted" style="margin-top:8px">%s</p></div>%s</a>' % (
            s['slug'], s['full'], s['blurb'], s['value'].capitalize(), picture(img(s['img']), STOCK[s['img']])) for s in SERVICES)
    hero = split([('Inicio', '/'), ('Servicios', None)], 'Servicios de limpieza profesional en Málaga',
                 'Comunidades, oficinas, colegios, instalaciones deportivas, parkings, maquinaria y fin de obra. Cada servicio con su protocolo, su frecuencia y su presupuesto cerrado.',
                 f'<a class="btn" href="/presupuesto">Pedir presupuesto</a><a class="btn-text" href="tel:{TEL}">Llamar {PHONE}</a>',
                 img('malaga-catedral'), 'Catedral de Málaga, de noche, vista desde la calle')
    body = f"""{hero}
<div class="wrap">
<section class="service-list index-list" aria-label="Lista de servicios" style="padding-top:var(--gap-section)">{rows}</section>
<article class="prose" style="margin-bottom:var(--gap-section)" data-reveal>
<h2>Cómo elegimos el servicio adecuado</h2>
<p>No todos los espacios se limpian igual. Una <a href="/limpieza-comunidades">comunidad de vecinos</a> pide constancia y trato con el administrador; una <a href="/limpieza-oficinas">oficina</a>, discreción y horarios fuera de la jornada; un <a href="/limpieza-colegios">colegio</a>, productos hipoalergénicos y protocolos de desinfección; un <a href="/limpieza-polideportivos">polideportivo</a>, control de hongos y suelos antideslizantes.</p>
<p>Para superficies grandes combinamos el trabajo manual con <a href="/limpieza-con-maquinaria">maquinaria profesional</a>, y para <a href="/limpieza-parkings">parkings y garajes</a> usamos fregado mecánico. Si has terminado una reforma, la <a href="/limpieza-fin-de-obra">limpieza de fin de obra</a> deja la vivienda o el local listo para estrenar.</p>
<h2>Qué incluye siempre el servicio</h2>
<ul>
<li>Visita previa sin coste cuando el espacio lo requiere.</li>
<li>Propuesta por escrito con tareas, frecuencias, productos y precio cerrado en 24 horas laborables.</li>
<li>Equipo propio dado de alta en la Seguridad Social y con seguro de responsabilidad civil.</li>
<li>Una persona de contacto y un checklist en cada visita.</li>
<li>Sin permanencia: se ajusta o se cancela con un preaviso.</li>
</ul>
<p>Trabajamos en <a href="/zonas">diez zonas de la provincia de Málaga</a>. Si dudas sobre qué necesitas, lee nuestras <a href="/blog">guías del blog</a> o <a href="/contacto">escríbenos</a>.</p>
</article>
</div>
{reply(wa_text='Hola, me gustaría pedir un presupuesto de limpieza.')}"""
    ld = jsonld(breadcrumb([('Inicio', DOMAIN + '/'), ('Servicios', None)]),
                {'@context': 'https://schema.org', '@type': 'ItemList', 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': url(s['slug']), 'name': s['full']} for i, s in enumerate(SERVICES)]})
    page('servicios', 'Servicios de Limpieza en Málaga | Actividades de Limpieza',
         'Servicios de limpieza profesional en Málaga: comunidades, oficinas, colegios, polideportivos, parkings, maquinaria y fin de obra. Presupuesto en 24 h.', body, ld=ld)


def build_zonas():
    rows = ''.join('<a href="/%s" data-reveal><div><h2>%s</h2><p>%s</p><p class="small muted" style="margin-top:8px">%s</p></div>%s</a>' % (
        z['slug'], z['name'], z['hoods'], z['hook'], picture(img(z['img']), z['alt'])) for z in ZONES)
    hero = split([('Inicio', '/'), ('Zonas', None)], 'Zonas de servicio: de la capital a la costa',
                 'Cubrimos Málaga capital, la Costa del Sol, la Axarquía y Antequera con los mismos estándares: equipo propio, presupuesto en 24 h y sin permanencia. Elige tu zona.',
                 f'<a class="btn" href="/presupuesto">Pedir presupuesto</a><a class="btn-text" href="tel:{TEL}">Llamar {PHONE}</a>',
                 img('malaga-gibralfaro'), 'Vista panorámica de Málaga y su puerto desde el castillo de Gibralfaro')
    body = f"""{hero}
<div class="wrap">
<section class="service-list index-list" aria-label="Lista de zonas" style="padding-top:var(--gap-section)">{rows}</section>
<p class="credit" style="margin-bottom:var(--gap-section)">Fotografías de Wikimedia Commons; autoría y licencia en <a href="/creditos">créditos</a>.</p>
</div>
{reply(wa_text='Hola, me gustaría pedir un presupuesto de limpieza.')}"""
    ld = jsonld(breadcrumb([('Inicio', DOMAIN + '/'), ('Zonas', None)]),
                {'@context': 'https://schema.org', '@type': 'ItemList', 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': url(z['slug']), 'name': 'Limpieza en ' + z['name']} for i, z in enumerate(ZONES)]})
    page('zonas', 'Zonas de Servicio en Málaga | Actividades de Limpieza',
         'Limpieza profesional en toda la provincia de Málaga: capital, Torremolinos, Benalmádena, Fuengirola, Marbella, Mijas, Estepona, Vélez-Málaga y Antequera.', body, ld=ld)


# ═════════════════ SERVICIO / ZONA (detalle) ═════════════════
def urllib_unquote(s):
    from urllib.parse import unquote
    return unquote(s)


def ficha_html(p, heading):
    items = ''.join('<li><span class="tick" aria-hidden="true"></span><span><b>%s</b>%s</span></li>' % (c['b'] + (':' if c['t'] else ''), (' ' + c['t']) if c['t'] else '') for c in p['checks'])
    return f"""<aside class="ficha sheet" data-reveal><h2>{esc(heading)}</h2><ul>{items}</ul>
<div class="ficha-actions"><a class="btn" href="/presupuesto">Pedir presupuesto</a><a class="btn-text" href="{wa_link(urllib_unquote(p['wa_text']))}" data-ctx="ficha">Escribir por WhatsApp</a></div></aside>"""


def detail(slug, kind):
    p = PAGES[slug]
    p['desc'] = p['desc'].replace(' ☎ 642 11 89 72', ' Tel. 642 11 89 72').replace('Sin permanencia, presupuesto en 24 h.', 'Sin permanencia.').replace('Servicio fuera de horario laboral, desinfección', 'Fuera de horario laboral, desinfección').replace('Torre de Benagalbón. Presupuesto en 24 h.', 'Torre de Benagalbón. Presupuesto 24 h.')
    if kind == 'service':
        s = SERVICE_BY_SLUG[slug]
        h1, im, alt = s['h1'], img(s['img']), STOCK[s['img']]
        parent, name, title = ('Servicios', '/servicios'), s['full'], p['title']
    else:
        z = ZONE_BY_SLUG[slug]
        h1, im, alt = 'Empresa de limpieza en ' + z['name'], img(z['img']), z['alt']
        parent, name = ('Zonas', '/zonas'), 'Limpieza en ' + z['name']
        title = 'Empresa de Limpieza en %s | %s' % (z['name'], BRAND)
        if len(title) > 60:
            title = 'Limpieza en %s | %s' % (z['name'], BRAND)
    prose = prose_clean(p['prose'])
    quote = '<p class="pull">%s</p>' % esc(p['quote']) if p['quote'] else ''
    if kind == 'zone':
        rel1 = thumb_links(zone_items(p['near']))
        rel2 = thumb_links(service_items([sv['slug'] for sv in SERVICES[:3]]))
        t1, t2 = 'También trabajamos cerca', 'Servicios que más se piden'
    else:
        rel1 = thumb_links(service_items(p['near']))
        rel2 = thumb_links(zone_items([zz['slug'] for zz in ZONES[:4]]))
        t1, t2 = 'Servicios relacionados', 'En tu zona'
    actions = f'<a class="btn" href="/presupuesto" data-ctx="hero">Pedir presupuesto</a><a class="btn-text" href="{wa_link(urllib_unquote(p["wa_text"]))}" data-ctx="hero">WhatsApp</a>'
    hero = split([('Inicio', '/'), parent, (name, None)], h1, p['lede'], actions, im, alt)
    body = f"""{hero}
<div class="wrap">
<div class="cols" style="padding-top:var(--gap-section)">
  {ficha_html(p, p['aside_eyebrow'])}
  <article class="prose" data-reveal style="--d:100ms">
    {prose}
    {quote}
    <div class="faq-block"><h2>{esc(p['faq_h2'])}</h2>{accordion(p['faq'])}</div>
  </article>
</div>
<section class="related" aria-labelledby="rel1"><h2 id="rel1">{t1}</h2>{rel1}</section>
<section class="related" aria-labelledby="rel2" style="padding-top:0"><h2 id="rel2">{t2}</h2>{rel2}</section>
</div>
{reply(text=p['cta_lede'] or 'Cuéntanos qué espacio quieres limpiar y cada cuánto.', wa_text=urllib_unquote(p['wa_text']), cls='reply compact-reply')}"""
    svc = {'@context': 'https://schema.org', '@type': 'Service', 'name': name, 'url': url(slug), 'description': p['desc'],
           'provider': {'@id': DOMAIN + '/#negocio'}, 'serviceType': 'Servicio de limpieza profesional',
           'areaServed': ({'@type': 'City', 'name': ZONE_BY_SLUG[slug]['short']} if kind == 'zone' else {'@type': 'AdministrativeArea', 'name': 'Provincia de Málaga'})}
    ld = jsonld(svc, breadcrumb([('Inicio', DOMAIN + '/'), (parent[0], DOMAIN + parent[1]), (name, None)]), faq_ld(p['faq']))
    page(slug, title, p['desc'], body, page_nav='/' + ('servicios' if kind == 'service' else 'zonas'), ld=ld, og_img=DOMAIN + im['src'])


# ═════════════════ NOSOTROS / CONTACTO / PRESUPUESTO ═════════════════
def build_about():
    actions = '<a class="btn" href="/presupuesto">Pedir presupuesto</a><a class="btn-text" href="/contacto">Contacto</a>'
    hero = split([('Inicio', '/'), ('Sobre nosotros', None)], 'Una empresa de limpieza hecha en Málaga',
                 'Empezamos en 2008 con una idea sencilla: que la limpieza profesional se parezca más a la seriedad que al ruido. Seguimos con ella.', actions,
                 img('malaga-muelle-uno'), 'El puerto de Málaga al amanecer, con la catedral al fondo')
    body = f"""{hero}
<div class="wrap">
<div class="cols" style="padding-top:var(--gap-section)">
  <aside class="ficha sheet" data-reveal><h2>Lo que puedes comprobar</h2><ul>
    <li><span class="tick" aria-hidden="true"></span><span><b>2008:</b> año en que empezamos en Málaga.</span></li>
    <li><span class="tick" aria-hidden="true"></span><span><b>7 servicios</b> con protocolo propio.</span></li>
    <li><span class="tick" aria-hidden="true"></span><span><b>10 zonas</b> de la provincia.</span></li>
    <li><span class="tick" aria-hidden="true"></span><span><b>24 h laborables</b> para tu presupuesto.</span></li>
    <li><span class="tick" aria-hidden="true"></span><span><b>Sin permanencia:</b> ajustas o cancelas con preaviso.</span></li>
  </ul><div class="ficha-actions"><a class="btn" href="/presupuesto">Pedir presupuesto</a></div></aside>
  <article class="prose" data-reveal style="--d:100ms">
    <h2>Quiénes somos</h2>
    <p>Actividades de Limpieza es una empresa de Málaga con equipo propio y un teléfono que responde. Esa es la base del modelo: pocas capas entre quien pide el servicio y quien lo hace.</p>
    <p>La mayoría de nuestros clientes son comunidades de propietarios y administradores de fincas, nuestro origen. Con los años hemos sumado oficinas, colegios, instalaciones deportivas, parkings y trabajos de fin de obra. Cada sector tiene sus protocolos, pero la lógica es la misma: <b>si prometemos algo, se cumple; si algo falla, se arregla</b>.</p>
    <h2>Cómo trabajamos</h2>
    <p>La limpieza profesional no es solo agua y producto. Es <b>gente formada</b>, <b>maquinaria adecuada</b> y <b>una persona responsable por cada servicio</b>. Por eso:</p>
    <ul>
      <li>Todo el equipo está dado de alta en la Seguridad Social y con seguro de responsabilidad civil.</li>
      <li>Cada servicio tiene un responsable directo que responde por teléfono o WhatsApp.</li>
      <li>Usamos productos ecológicos, biodegradables y seguros para personas y mascotas.</li>
      <li>La formación es continua: técnicas de limpieza, maquinaria y protocolos de seguridad.</li>
      <li>No hay permanencia: si el servicio no convence, se ajusta o se cancela.</li>
    </ul>
    <h2>Por qué lo hacemos así</h2>
    <p>Una comunidad no cambia de empresa de limpieza por precio: cambia por <b>confianza</b>. Y la confianza se construye con visitas puntuales, partes de incidencias, facturas claras y un teléfono que atiende alguien que sabe de qué le hablan.</p>
    <p>También hemos aprendido a decir que no. Si un servicio no lo podemos hacer bien, lo decimos antes de firmar.</p>
    <p>Puedes ver cómo trabajamos en cada <a href="/servicios">servicio</a> y en cada <a href="/zonas">zona</a>, o leer las guías del <a href="/blog">blog</a>.</p>
  </article>
</div>
{zones_section(['limpieza-malaga', 'limpieza-marbella', 'limpieza-fuengirola', 'limpieza-torremolinos'])}
</div>
{reply(wa_text='Hola, me gustaría pedir un presupuesto de limpieza.')}"""
    page('sobre-nosotros', 'Sobre Nosotros | Actividades de Limpieza en Málaga',
         'Actividades de Limpieza: empresa de limpieza profesional en Málaga desde 2008. Equipo propio, productos ecológicos y presupuesto en 24 h, sin permanencia.',
         body, ld=jsonld(BUSINESS, breadcrumb([('Inicio', DOMAIN + '/'), ('Sobre nosotros', None)])))


def field(label, name, kind='text', req=False, ph='', err='', auto='', extra=''):
    return '<div class="fld"><label for="%s">%s%s</label><input type="%s" id="%s" name="%s"%s%s%s%s>%s</div>' % (
        name, label, ' *' if req else '', kind, name, name, ' required' if req else '', ' placeholder="%s"' % ph if ph else '', ' autocomplete="%s"' % auto if auto else '', extra, '<p class="err">%s</p>' % err if err else '')


def select(label, name, options, req=False, err=''):
    opts = ''.join('<option value="%s">%s</option>' % (esc(o), esc(o)) if o else '<option value="">Selecciona</option>' for o in options)
    return '<div class="fld"><label for="%s">%s%s</label><select id="%s" name="%s"%s>%s</select>%s</div>' % (name, label, ' *' if req else '', name, name, ' required' if req else '', opts, '<p class="err">%s</p>' % err if err else '')


def build_contact():
    hero = split([('Inicio', '/'), ('Contacto', None)], 'Hablemos de lo que necesitas limpiar',
                 'Por teléfono, WhatsApp o email. Te respondemos en menos de 24 horas laborables, sin compromiso y sin letra pequeña.',
                 f'<a class="btn" href="tel:{TEL}" data-ctx="contacto-hero">Llamar {PHONE}</a><a class="btn-text" href="{wa_link("Hola, me gustaría pedir un presupuesto de limpieza.")}" data-ctx="contacto-hero">WhatsApp</a>',
                 img('malaga-catedral'), 'Catedral de Málaga, de noche, vista desde la calle')
    body = f"""{hero}
<div class="wrap">
<div class="cols" style="padding-top:var(--gap-section)">
  <aside class="ficha sheet" data-reveal><h2>Elige el canal que te venga mejor</h2>
    <ul class="channel" style="display:block">
      <li style="display:block"><b>Teléfono</b><a href="tel:{TEL}" data-ctx="contacto">{PHONE}</a><br><span class="muted">Lun–Vie · 8:00–19:00</span></li>
      <li style="display:block"><b>WhatsApp</b><a href="{wa_link('Hola, me gustaría pedir un presupuesto de limpieza.')}" data-ctx="contacto">{PHONE}</a><br><span class="muted">Respuesta en horario laborable</span></li>
      <li style="display:block"><b>Email</b><a href="mailto:{EMAIL}">{EMAIL}</a><br><span class="muted">Respuesta en 24 h laborables</span></li>
      <li style="display:block"><b>Área de servicio</b>Málaga capital, Costa del Sol, Axarquía y Antequera. <a href="/zonas">Ver zonas</a></li>
    </ul>
  </aside>
  <div class="sheet form-sheet" data-reveal style="--d:100ms">
    <h2>Escríbenos</h2>
    <form id="contact-form" data-validate data-wa="{WA}" novalidate>
      <div class="grid2">{field('Nombre completo', 'nombre', req=True, ph='Tu nombre', err='Escribe tu nombre', auto='name')}{field('Teléfono', 'telefono', 'tel', True, PHONE, 'Necesitamos tu teléfono para responder', 'tel')}</div>
      <div class="grid2">{field('Email', 'email', 'email', False, 'tu@email.com', 'Revisa el formato del email', 'email')}{field('Empresa o comunidad', 'empresa', ph='Nombre de tu empresa o comunidad')}</div>
      <div class="fld"><label for="mensaje">Mensaje *</label><textarea id="mensaje" name="mensaje" required placeholder="Cuéntanos qué espacio es, dónde está y cada cuánto quieres limpiarlo."></textarea><p class="err">Cuéntanos qué necesitas</p></div>
      <div class="note">Al enviar, se abre WhatsApp con tu mensaje preparado. También puedes llamarnos al {PHONE}.</div>
      <div class="form-actions"><button class="btn" type="submit">Enviar por WhatsApp {WAICON}</button></div>
    </form>
  </div>
</div>
<article class="prose" style="margin-bottom:var(--gap-section)" data-reveal>
<h2>Para que tu presupuesto sea exacto</h2>
<p>Cuanta más información nos des, más precisa será la propuesta. Si puedes, cuéntanos el tipo de espacio (<a href="/limpieza-comunidades">comunidad</a>, <a href="/limpieza-oficinas">oficina</a>, <a href="/limpieza-colegios">colegio</a>, local o <a href="/limpieza-fin-de-obra">obra</a>), los metros cuadrados aproximados, la zona y la frecuencia con la que necesitas el servicio.</p>
<p>Si prefieres que lo veamos en persona, concertamos una visita sin coste y te enviamos la propuesta en 24 horas laborables. No hay permanencia ni compromiso.</p>
<p>También puedes <a href="/presupuesto">pedir presupuesto con el formulario paso a paso</a> o consultar <a href="/servicios">todos los servicios</a> antes de escribirnos.</p>
</article>
</div>"""
    page('contacto', 'Contacto | Actividades de Limpieza en Málaga',
         'Contacta con Actividades de Limpieza en Málaga: llama o escribe por WhatsApp al 642 11 89 72, o por email. Respuesta en 24 h laborables. Lun–Vie 8:00–19:00.',
         body, ld=jsonld(BUSINESS, breadcrumb([('Inicio', DOMAIN + '/'), ('Contacto', None)]), {'@context': 'https://schema.org', '@type': 'ContactPage', 'url': url('contacto'), 'name': 'Contacto'}))


def build_quote():
    svc = [s['full'] for s in SERVICES] + ['Otro servicio']
    zon = [z['name'] for z in ZONES] + ['Otra zona de la provincia']
    hero = split([('Inicio', '/'), ('Presupuesto', None)], 'Tu presupuesto de limpieza, en 24 horas',
                 'Tres pasos y un minuto. Te respondemos en menos de 24 horas laborables con una propuesta cerrada, sin compromiso.',
                 f'<a class="btn-text" href="tel:{TEL}">¿Prefieres hablar? {PHONE}</a>', img('malaga-gibralfaro'), 'Vista panorámica de Málaga y su puerto desde el castillo de Gibralfaro')
    body = f"""{hero}
<div class="wrap">
<div class="cols" style="padding-top:var(--gap-section)">
  <aside class="ficha sheet" data-reveal><h2>Qué incluye tu propuesta</h2><ul>
    <li><span class="tick" aria-hidden="true"></span><span>Tareas y frecuencias, una por una.</span></li>
    <li><span class="tick" aria-hidden="true"></span><span>Productos y maquinaria que se usarán.</span></li>
    <li><span class="tick" aria-hidden="true"></span><span>Precio cerrado, sin letra pequeña.</span></li>
    <li><span class="tick" aria-hidden="true"></span><span>Sin permanencia.</span></li>
  </ul><div class="ficha-actions"><a class="btn-text" href="{wa_link('Hola, me gustaría pedir un presupuesto de limpieza.')}" data-ctx="presupuesto">¿Más rápido? WhatsApp</a></div></aside>
  <div class="sheet form-sheet" data-reveal style="--d:100ms">
    <div class="steps" aria-hidden="true"><i class="is-on"></i><i></i><i></i></div>
    <form id="quote-form" novalidate data-wa="{WA}">
      <div class="step-panel is-active">
        <h2>1. Tus datos</h2>
        <div class="grid2">{field('Nombre completo', 'nombre', req=True, ph='Tu nombre', err='Escribe tu nombre', auto='name')}{field('Teléfono', 'telefono', 'tel', True, PHONE, 'Necesitamos tu teléfono para responder', 'tel')}</div>
        <div class="grid2">{field('Email', 'email', 'email', False, 'tu@email.com', 'Revisa el formato del email', 'email')}{field('Empresa o comunidad', 'empresa', ph='Nombre de tu empresa o comunidad')}</div>
        <div class="form-actions"><span></span><button class="btn" type="button" data-step="2">Continuar {ARROW}</button></div>
      </div>
      <div class="step-panel">
        <h2>2. Qué necesitas</h2>
        <div class="grid2">{select('Tipo de servicio', 'servicio', [''] + svc, True, 'Selecciona el servicio')}{select('Frecuencia', 'frecuencia', [''] + FREQS)}</div>
        <div class="grid2">{select('Zona', 'zona', [''] + zon, True, 'Indica la zona')}{field('Metros cuadrados aprox.', 'metros', ph='Ej: 500 m²', extra=' inputmode="numeric"')}</div>
        <div class="form-actions"><button class="btn-text" type="button" data-step="1">Anterior</button><button class="btn" type="button" data-step="3">Continuar {ARROW}</button></div>
      </div>
      <div class="step-panel">
        <h2>3. Cuéntanos más</h2>
        <div class="fld"><label for="mensaje">Descripción de tus necesidades *</label><textarea id="mensaje" name="mensaje" required placeholder="Por ejemplo: comunidad de 24 viviendas en Teatinos, 3 visitas por semana, queremos empezar el mes que viene."></textarea><p class="err">Cuéntanos algo sobre lo que necesitas</p></div>
        <div class="note"><b>¿Cómo funciona?</b> Al enviar, se abre WhatsApp con tu solicitud preparada para enviárnosla. También puedes llamarnos al {PHONE}.</div>
        <div class="form-actions"><button class="btn-text" type="button" data-step="2">Anterior</button><button class="btn" type="submit">Enviar por WhatsApp {WAICON}</button></div>
      </div>
    </form>
  </div>
</div>
{zones_section(['limpieza-malaga', 'limpieza-torremolinos', 'limpieza-fuengirola', 'limpieza-marbella'], 'Zonas donde trabajamos')}
</div>"""
    page('presupuesto', 'Presupuesto de Limpieza Gratis | Actividades de Limpieza',
         'Solicita tu presupuesto de limpieza profesional en Málaga, gratis y sin compromiso. Respuesta en 24 h laborables. Comunidades, oficinas y más. Tel. 642 11 89 72',
         body, ld=jsonld(breadcrumb([('Inicio', DOMAIN + '/'), ('Presupuesto', None)])))


# ═════════════════ BLOG ═════════════════
POST_IMG = {
    'cuanto-cuesta-limpieza-comunidad-malaga': ('comunidades', 'Persona limpiando una ventana con persianas de madera'),
    'limpieza-fin-de-obra-malaga': ('blog-obra', 'Persona dibujando un plano sobre una mesa de trabajo'),
    'como-elegir-empresa-limpieza-malaga': ('malaga-larios', 'Calle Larios de Málaga, con edificios de ladrillo y balcones'),
}
H1S = {
    'cuanto-cuesta-limpieza-comunidad-malaga': 'Cuánto cuesta limpiar una comunidad',
    'como-elegir-empresa-limpieza-malaga': 'Cómo elegir empresa de limpieza: 7 preguntas',
    'limpieza-fin-de-obra-malaga': 'Limpieza de fin de obra: guía completa',
    'limpieza-oficinas-malaga-frecuencia-horarios': 'Cada cuánto limpiar una oficina en Málaga',
    'limpieza-colegios-desinfeccion-verano-malaga': 'Colegios: limpieza diaria y puesta a punto',
    'limpieza-parkings-garajes-comunidad': 'Limpieza de garajes: cada cuánto y cómo',
    'limpieza-comunidades-costa-del-sol-verano': 'Comunidades de la costa: limpieza de verano',
    'calima-malaga-limpieza-fachadas-terrazas': 'Calima en Málaga: cómo limpiar sin rayar',
    'contrato-limpieza-comunidad-vecinos-que-incluir': 'Contrato de limpieza de una comunidad',
}


def all_posts():
    posts = []
    for slug, p in POSTS_OLD.items():
        k, alt = POST_IMG[slug]
        body = re.sub(r'<p>\s*<img[^>]*>\s*</p>', '', p['body'])
        posts.append(dict(slug=slug, title=p['title'], desc=p['desc'], h1=re.sub(r'<[^>]+>', '', p['h1']), lede=p['lede'], cat=p['cat'], date=p['date'], mins=p['mins'], img=k, img_alt=alt, body=body, wa='Hola, tengo una duda sobre limpieza profesional.'))
    for p in POSTS_NEW:
        words = len(re.sub(r'<[^>]+>', ' ', p['body']).split())
        posts.append(dict(p, mins=max(4, round(words / 190))))
    for p in posts:
        p['h1'] = H1S.get(p['slug'], p['h1'])
    posts.sort(key=lambda x: x['date'], reverse=True)
    return posts


def fmt_date(d):
    m = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    y, mo, da = d.split('-')
    return '%d de %s de %s' % (int(da), m[int(mo) - 1], y)


def build_blog(posts):
    rows = ''.join('<a class="post-row" href="/blog/%s" data-reveal><div><h2>%s</h2><p>%s</p><p class="meta">%s · %s · %d min de lectura</p></div>%s</a>' % (
        p['slug'], esc(p['h1']), esc(p['lede']), esc(p['cat']), fmt_date(p['date']), p['mins'], picture(img(p['img']), p['img_alt'])) for p in posts)
    hero = split([('Inicio', '/'), ('Blog', None)], 'Aprende a contratar mejor la limpieza',
                 'Precios orientativos, guías por servicio y las preguntas que conviene hacer antes de firmar. Escrito por el equipo de Actividades de Limpieza.',
                 '<a class="btn" href="/presupuesto">Pedir presupuesto</a>', img('malaga-larios'), 'Calle Larios de Málaga, con edificios de ladrillo y balcones')
    body = f"""{hero}
<div class="wrap"><section class="index-list" aria-label="Artículos" style="padding-top:var(--gap-section)">{rows}</section></div>
{reply(wa_text='Hola, tengo una duda sobre limpieza profesional.')}"""
    ld = jsonld(breadcrumb([('Inicio', DOMAIN + '/'), ('Blog', None)]), {'@context': 'https://schema.org', '@type': 'Blog', 'name': 'Blog de ' + BRAND, 'url': url('blog'), 'publisher': {'@id': DOMAIN + '/#negocio'},
                'blogPost': [{'@type': 'BlogPosting', 'headline': p['h1'], 'url': url('blog/' + p['slug']), 'datePublished': p['date']} for p in posts]})
    page('blog', 'Blog de Limpieza Profesional | Actividades de Limpieza',
         'Guías y consejos de limpieza profesional en Málaga: precios, oficinas, colegios, parkings, comunidades y cómo elegir empresa. Por Actividades de Limpieza.', body, ld=ld)


def build_post(p, posts):
    im = img(p['img'])
    others = [o for o in posts if o['slug'] != p['slug']]
    same = [o for o in others if o['cat'] == p['cat']]
    rel = (same + [o for o in others if o not in same])[:3]
    relh = thumb_links([(o['h1'], '/blog/' + o['slug'], fmt_date(o['date']), o['img'], o['img_alt']) for o in rel])
    meta = '<p class="article-meta" data-reveal style="--d:110ms"><span>%s</span><span>%s</span><span>%d min de lectura</span><span>Equipo de %s</span></p>' % (esc(p['cat']), fmt_date(p['date']), p['mins'], BRAND)
    actions = f'<a class="btn" href="/presupuesto" data-ctx="articulo">Pedir presupuesto</a><a class="btn-text" href="{wa_link(p.get("wa") or "Hola, me gustaría pedir un presupuesto de limpieza.")}" data-ctx="articulo">WhatsApp</a>'
    short = p['h1'] if len(p['h1']) < 48 else p['h1'][:45] + '…'
    hero = split([('Inicio', '/'), ('Blog', '/blog'), (short, None)], p['h1'], p['lede'], actions, im, p['img_alt'], meta_html=meta)
    body = f"""{hero}
<div class="wrap">
<article class="article" style="padding-top:var(--gap-section)"><div class="prose" data-reveal>{prose_clean(p['body'])}</div></article>
<section class="related" style="padding-top:var(--gap-section)" aria-labelledby="rel"><h2 id="rel">Sigue leyendo</h2>{relh}</section>
</div>
{reply(wa_text=p.get('wa') or 'Hola, me gustaría pedir un presupuesto de limpieza.', cls='reply compact-reply')}"""
    ld = jsonld({'@context': 'https://schema.org', '@type': 'BlogPosting', 'headline': p['h1'], 'description': p['desc'], 'url': url('blog/' + p['slug']),
                 'datePublished': p['date'] + 'T09:00:00+02:00', 'dateModified': (TODAY if p['date'] < '2026-09-01' else p['date']) + 'T09:00:00+02:00',
                 'image': DOMAIN + im['src'], 'inLanguage': 'es-ES', 'author': {'@type': 'Organization', 'name': BRAND, 'url': DOMAIN + '/'}, 'publisher': {'@id': DOMAIN + '/#negocio'},
                 'mainEntityOfPage': {'@type': 'WebPage', '@id': url('blog/' + p['slug'])}},
                breadcrumb([('Inicio', DOMAIN + '/'), ('Blog', DOMAIN + '/blog'), (p['h1'], None)]))
    page('blog/' + p['slug'], p['title'], p['desc'], body, page_nav='/blog', ld=ld, og_type='article', og_img=DOMAIN + im['src'])


# ═════════════════ LEGAL, CRÉDITOS, GRACIAS, 404 ═════════════════
def build_legal():
    for slug, l in LEGAL.items():
        body = f"""<div class="wrap inner-top" style="padding-bottom:var(--gap-section)">
{crumbs([('Inicio', '/'), (l['h1'], None)])}
<div class="article"><h1>{esc(l['h1'])}</h1><p class="statement" style="margin-block:20px 40px">{esc(l['lede'])}</p><div class="prose">{prose_clean(l['body'])}</div></div>
</div>"""
        page(slug, l['title'], l['desc'], body, robots='noindex, follow', page_nav='/' + slug)


def build_credits():
    rows = ''
    for k, c in CREDITS.items():
        rows += '<li><b>%s</b>: <a href="%s" rel="noopener">%s</a>, %s, %s. Archivo en Wikimedia Commons.</li>' % (esc(k.replace('-', ' ').capitalize()), esc(c['page']), esc(c['title']), esc(c['artist']), esc(c['license']))
    body = f"""<div class="wrap inner-top" style="padding-bottom:var(--gap-section)">
{crumbs([('Inicio', '/'), ('Créditos', None)])}
<div class="article"><h1>Créditos de las imágenes</h1>
<p class="statement" style="margin-block:20px 40px">Las fotografías de lugares de Málaga y la provincia proceden de Wikimedia Commons con licencias libres. Las imágenes ilustrativas de servicios son de archivo, con licencia Unsplash. Ninguna muestra a nuestro equipo ni nuestros trabajos.</p>
<div class="prose"><ul>{rows}</ul>
<p><b>Vídeo de portada de contacto</b>: <a href="https://commons.wikimedia.org/wiki/File:Panoramic_of_Malaga_from_the_Castle_of_Santa_Catalina.webm" rel="noopener">Panoramic of Malaga from the Castle of Santa Catalina</a>, Daniel Capilla, CC BY-SA 4.0 (recortado y recomprimido).</p>
<p>Licencias: CC BY-SA 3.0 y 4.0 (<a href="https://creativecommons.org/licenses/by-sa/4.0/deed.es" rel="noopener">texto</a>), CC BY 3.0 y CC0. Imágenes ilustrativas de servicios: <a href="https://unsplash.com/license" rel="noopener">licencia Unsplash</a>.</p></div></div></div>"""
    page('creditos', 'Créditos de las imágenes | Actividades de Limpieza', 'Autoría y licencia de las fotografías utilizadas en el sitio.', body, robots='noindex, follow')


def build_thanks():
    body = f"""<div class="center-page"><div class="sheet" data-reveal>
<h1>Gracias, ya tenemos tu solicitud</h1>
<p class="statement">Te responderemos en menos de 24 horas laborables con tu presupuesto. Si prefieres adelantar conversación, escríbenos o llámanos.</p>
<div class="phero-actions"><a class="btn" href="{wa_link('Hola, acabo de enviar una solicitud de presupuesto.')}" data-ctx="gracias">WhatsApp</a><a class="btn-text" href="tel:{TEL}">Llamar {PHONE}</a><a class="btn-text" href="/">Volver al inicio</a></div>
</div></div>"""
    page('gracias', 'Gracias | Actividades de Limpieza', 'Hemos recibido tu solicitud de presupuesto. Te respondemos en 24 horas laborables.', body, robots='noindex, nofollow')


def build_404():
    body = f"""<div class="center-page"><div class="sheet">
<h1>Esta página no está en la hoja</h1>
<p class="statement">La página que buscas no existe o ha cambiado de dirección. Vuelve al inicio o elige un servicio.</p>
<div class="phero-actions"><a class="btn" href="/">Ir al inicio</a><a class="btn-text" href="/servicios">Servicios</a><a class="btn-text" href="tel:{TEL}">Llamar {PHONE}</a></div>
</div></div>"""
    h = head('Página no encontrada | Actividades de Limpieza', 'La página que buscas no existe o ha cambiado de dirección.', '404', robots='noindex, nofollow')
    h = re.sub(r'<link rel="canonical"[^>]*>\n', '', h)
    out = h + '<body>\n' + cookie_html() + bar('') + '<main id="main">' + body + '</main>' + footer() + stub() + '<script src="/js/app.js?v=6" defer></script>\n</body>\n</html>\n'
    write('404.html', out)


# ═════════════════ SITEMAP + LLMS ═════════════════
def build_meta(posts):
    urls = [('', '1.0', 'weekly', TODAY), ('servicios', '0.9', 'monthly', TODAY), ('zonas', '0.8', 'monthly', TODAY), ('presupuesto', '0.9', 'monthly', TODAY),
            ('contacto', '0.6', 'monthly', TODAY), ('sobre-nosotros', '0.5', 'monthly', TODAY), ('blog', '0.7', 'weekly', TODAY)]
    urls += [(s['slug'], '0.9', 'monthly', TODAY) for s in SERVICES]
    urls += [(z['slug'], '0.8', 'monthly', TODAY) for z in ZONES]
    urls += [('blog/' + p['slug'], '0.7', 'monthly', max(p['date'], '2026-08-26') if p['date'] >= '2026-09-01' else TODAY) for p in posts]
    x = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for p, pr, cf, lm in urls:
        x += '  <url><loc>%s</loc><lastmod>%s</lastmod><changefreq>%s</changefreq><priority>%s</priority></url>\n' % (url(p), lm, cf, pr)
    write('sitemap.xml', x + '</urlset>\n')
    t = f"""# {BRAND}

> Empresa de limpieza profesional en Málaga y provincia desde 2008. Comunidades de vecinos, oficinas, colegios, polideportivos, parkings, limpieza con maquinaria y fin de obra. Equipo propio, productos ecológicos, presupuesto en 24 horas laborables y sin permanencia.

## Datos de contacto
- Teléfono y WhatsApp: {PHONE} (Lun–Vie 8:00–19:00)
- Email: {EMAIL}
- Zona de servicio: Málaga y provincia ({', '.join(z['short'] for z in ZONES)})

## Servicios
""" + ''.join('- [%s](%s): %s\n' % (s['full'], url(s['slug']), s['blurb']) for s in SERVICES) + '\n## Zonas de servicio\n' + ''.join('- [%s](%s): %s\n' % (z['name'], url(z['slug']), z['hoods']) for z in ZONES) + '\n## Blog\n' + ''.join('- [%s](%s)\n' % (p['h1'], url('blog/' + p['slug'])) for p in posts) + f"""
## Cómo presupuestar
- Formulario: {url('presupuesto')}
- Contacto: {url('contacto')}
- Proceso: consulta gratuita, propuesta cerrada en 24 horas laborables, servicio con control de calidad y seguimiento continuo.
"""
    write('llms.txt', t)


def main():
    # limpia HTML antiguo generado (los .html de la raíz y blog/)
    for f in os.listdir('.'):
        if f.endswith('.html'):
            os.remove(f)
    for f in os.listdir('blog') if os.path.isdir('blog') else []:
        os.remove(os.path.join('blog', f))
    posts = all_posts()
    build_home(); build_servicios(); build_zonas()
    for s in SERVICES: detail(s['slug'], 'service')
    for z in ZONES: detail(z['slug'], 'zone')
    build_about(); build_contact(); build_quote(); build_blog(posts)
    for p in posts: build_post(p, posts)
    build_legal(); build_credits(); build_thanks(); build_404(); build_meta(posts)
    v = json.load(open('vercel.json', encoding='utf-8'))
    v['redirects'] = build_redirects()
    json.dump(v, open('vercel.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    open('vercel.json', 'a').write('\n')
    # CSS: zigzag
    css = open('css/styles.css', encoding='utf-8').read()
    css = re.sub(r'--zig: [^;]*;', '', css)
    css = css.replace('  --ease: cubic-bezier(0.23, 1, 0.32, 1);', '  --zig: %s;\n  --ease: cubic-bezier(0.23, 1, 0.32, 1);' % ZIG, 1)
    open('css/styles.css', 'w', encoding='utf-8').write(css)
    print('páginas:', len(WRITTEN))


if __name__ == '__main__':
    main()
