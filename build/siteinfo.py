"""Datos del sitio: negocio, servicios, zonas, imágenes y la hoja de control."""
import json, os, struct

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAIN = 'https://www.actividadesdelimpieza.com'
PHONE = '642 11 89 72'
TEL = '642118972'
WA = '34642118972'
EMAIL = 'info@actividadesdelimpieza.com'
TODAY = '2026-10-21'
BRAND = 'Actividades de Limpieza'


def wa_link(text):
    from urllib.parse import quote
    return 'https://wa.me/%s?text=%s' % (WA, quote(text, safe=''))


# ───────── Imágenes ─────────
CREDITS = json.load(open(os.path.join(ROOT, 'assets/img/credits.json'), encoding='utf-8'))

STOCK = {
    'comunidades': 'Persona limpiando una ventana con persianas de madera',
    'oficinas': 'Pasillo de oficina con mamparas de cristal y suelo pulido',
    'colegios': 'Aula vacía y ordenada, con pupitres y pizarra',
    'polideportivos': 'Sala de gimnasio con mancuernas y suelo de goma',
    'parkings': 'Vista aérea de las plazas de un aparcamiento',
    'maquinaria': 'Vista aérea de las plazas de un aparcamiento',
    'fin-de-obra': 'Cuarto de baño recién terminado, con ducha de cristal y encimera',
    'blog-obra': 'Persona dibujando un plano sobre una mesa de trabajo',
}


def jpeg_size(path):
    with open(path, 'rb') as f:
        f.read(2)
        while True:
            marker, = struct.unpack('>H', f.read(2))
            size, = struct.unpack('>H', f.read(2))
            if 0xFFC0 <= marker <= 0xFFC3:
                f.read(1)
                h, w = struct.unpack('>HH', f.read(4))
                return w, h
            f.read(size - 2)


def img(key):
    """Devuelve dict con src, w, h, alt-base, credit (texto) y credit_url."""
    path = os.path.join(ROOT, 'assets/img/%s.jpg' % key)
    w, h = jpeg_size(path)
    d = {'src': '/assets/img/%s.jpg' % key, 'w': w, 'h': h, 'key': key}
    if key in CREDITS:
        c = CREDITS[key]
        d['credit'] = '%s · %s, %s' % (c['title'].rsplit('.', 1)[0], c['artist'], c['license'])
        d['short'] = '%s, %s' % (c['artist'], c['license'])
        d['url'] = c['page']
    else:
        d['credit'] = 'Imagen de archivo (licencia Unsplash)'
        d['short'] = 'Imagen de archivo'
        d['url'] = ''
    return d


# ───────── Servicios ─────────
SERVICES = [
    dict(slug='limpieza-comunidades', name='Comunidades', full='Limpieza de comunidades', group=0, value='diaria o semanal',
         blurb='Portales, escaleras, ascensores, cuartos de basura y garajes.', img='comunidades',
         h1='Limpieza de comunidades en Málaga', ctx='una comunidad de vecinos', space='Comunidad'),
    dict(slug='limpieza-oficinas', name='Oficinas', full='Limpieza de oficinas', group=1, value='fuera de horario',
         blurb='Despachos, baños, suelos y cristales, sin interrumpir tu jornada.', img='oficinas',
         h1='Limpieza de oficinas en Málaga', ctx='una oficina', space='Oficina'),
    dict(slug='limpieza-colegios', name='Colegios', full='Limpieza de colegios', group=1, value='protocolo sanitario',
         blurb='Aulas, comedores y baños con productos hipoalergénicos.', img='colegios',
         h1='Limpieza de colegios en Málaga', ctx='un centro educativo', space='Colegio'),
    dict(slug='limpieza-polideportivos', name='Polideportivos', full='Limpieza de polideportivos', group=1, value='anti-hongos',
         blurb='Vestuarios, gradas y pistas con tratamientos antideslizantes.', img='polideportivos',
         h1='Limpieza de polideportivos en Málaga', ctx='un polideportivo', space='Polideportivo'),
    dict(slug='limpieza-parkings', name='Parkings', full='Limpieza de parkings', group=2, value='fregado mecánico',
         blurb='Barrido, fregado, paredes y señalización, también de noche.', img='parkings',
         h1='Limpieza de parkings en Málaga', ctx='un parking', space='Parking'),
    dict(slug='limpieza-con-maquinaria', name='Maquinaria', full='Limpieza con maquinaria', group=2, value='a medida',
         blurb='Fregadoras, hidrolimpiadoras y aspiradoras industriales.', img='maquinaria',
         h1='Limpieza con maquinaria en Málaga', ctx='una gran superficie', space='Maquinaria'),
    dict(slug='limpieza-fin-de-obra', name='Fin de obra', full='Limpieza de fin de obra', group=2, value='24–48 h',
         blurb='Polvo de obra, cristales y desinfección final. Lista para estrenar.', img='fin-de-obra',
         h1='Limpieza de fin de obra en Málaga', ctx='una obra', space='Obra'),
]
SERVICE_BY_SLUG = {s['slug']: s for s in SERVICES}
GROUPS = ['Comunidades y viviendas', 'Empresas y centros', 'Superficies y obras']

# ───────── Zonas ─────────
ZONES = [
    dict(slug='limpieza-malaga', name='Málaga capital', short='Málaga', img='malaga-muelle-uno', hoods='Centro, Teatinos, Carretera de Cádiz, Cruz de Humilladero, Puerto de la Torre y El Palo.', hook='Comunidades y oficinas de toda la ciudad.',
         alt='El puerto de Málaga al amanecer, con la catedral al fondo'),
    dict(slug='limpieza-torremolinos', name='Torremolinos', short='Torremolinos', img='torremolinos', hoods='Bajondillo, La Carihuela, Playamar y El Pinillo.', hook='Hoteles, comunidades y comercio de la avenida.',
         alt='Playa del Bajondillo en Torremolinos'),
    dict(slug='limpieza-benalmadena', name='Benalmádena', short='Benalmádena', img='benalmadena', hoods='Arroyo de la Miel, Benalmádena Costa, Pueblo y Puerto Marina.', hook='Residenciales con piscina y zonas comunes amplias.',
         alt='Puerto Marina de Benalmádena'),
    dict(slug='limpieza-fuengirola', name='Fuengirola', short='Fuengirola', img='fuengirola', hoods='Los Boliches, Torreblanca, Las Lagunas y el paseo marítimo.', hook='Comunidades de la costa y locales de restauración.',
         alt='Paseo marítimo de Fuengirola'),
    dict(slug='limpieza-marbella', name='Marbella', short='Marbella', img='marbella', hoods='Casco antiguo, Puerto Banús, Nueva Andalucía y San Pedro Alcántara.', hook='Estándares exigentes en urbanizaciones y oficinas.',
         alt='Calle del casco antiguo de Marbella'),
    dict(slug='limpieza-mijas', name='Mijas', short='Mijas', img='mijas', hoods='Mijas Pueblo, Las Lagunas, La Cala y Calahonda.', hook='Urbanizaciones en ladera y zonas comunes con jardín.',
         alt='Mijas Pueblo, con sus casas blancas en la ladera'),
    dict(slug='limpieza-estepona', name='Estepona', short='Estepona', img='estepona', hoods='Casco antiguo, Bahía Dorada, Cancelada y El Paraíso.', hook='Comunidades de litoral y comercios del centro.',
         alt='Calle del casco antiguo de Estepona con macetas y flores'),
    dict(slug='limpieza-rincon-de-la-victoria', name='Rincón de la Victoria', short='Rincón de la Victoria', img='rincon', hoods='La Cala del Moral, Benagalbón y la Torre de Benagalbón.', hook='Comunidades de primera línea y paseo marítimo.',
         alt='Playa de Rincón de la Victoria'),
    dict(slug='limpieza-velez-malaga', name='Vélez-Málaga', short='Vélez-Málaga', img='velez', hoods='Centro histórico, Torre del Mar y Caleta de Vélez.', hook='Comunidades, oficinas y comercio de la Axarquía.',
         alt='Vista de Vélez-Málaga y su castillo'),
    dict(slug='limpieza-antequera', name='Antequera', short='Antequera', img='antequera', hoods='Centro histórico, La Verónica y el polígono industrial.', hook='Comunidades, oficinas y naves.',
         alt='Antequera con la Peña de los Enamorados al fondo'),
]
ZONE_BY_SLUG = {z['slug']: z for z in ZONES}

# ───────── Hoja de control (herramienta) ─────────
# tier: v = cada visita, m = cada mes, x = a petición
CHECKLISTS = {
    'Comunidad': ('limpieza-comunidades', [
        ('Portales y escaleras', 'v'), ('Ascensores y espejos', 'v'), ('Cuartos de basura', 'v'),
        ('Zonas comunes y jardín', 'v'), ('Garaje y rampas', 'm'), ('Cristales y barandillas', 'm')]),
    'Oficina': ('limpieza-oficinas', [
        ('Despachos y mesas', 'v'), ('Baños y office', 'v'), ('Suelos y moquetas', 'v'),
        ('Papeleras y consumibles', 'v'), ('Cristales y mamparas', 'm'), ('Teclados y teléfonos', 'v')]),
    'Colegio': ('limpieza-colegios', [
        ('Aulas y pupitres', 'v'), ('Comedor', 'v'), ('Baños y lavabos', 'v'),
        ('Patios y accesos', 'v'), ('Cristales de aulas', 'm'), ('Puesta a punto de verano', 'x')]),
    'Polideportivo': ('limpieza-polideportivos', [
        ('Vestuarios y duchas', 'v'), ('Gradas', 'v'), ('Pistas y suelos', 'v'),
        ('Aseos', 'v'), ('Tratamiento anti-hongos', 'm'), ('Antideslizante en zonas húmedas', 'x')]),
    'Parking': ('limpieza-parkings', [
        ('Barrido mecánico', 'v'), ('Fregado de plazas y rampas', 'm'), ('Paredes y señalización', 'm'),
        ('Papeleras y accesos', 'v'), ('Cuartos de instalaciones', 'm'), ('Manchas de aceite', 'x')]),
    'Obra': ('limpieza-fin-de-obra', [
        ('Polvo de obra en todas las superficies', 'v'), ('Cristales y carpintería', 'v'), ('Baños y cocinas', 'v'),
        ('Suelos', 'v'), ('Rejillas, armarios y rodapiés', 'v'), ('Revisión final con el promotor', 'x')]),
}
FREQS = ['Diaria', 'Semanal', 'Quincenal', 'Puntual']

# ───────── Navegación ─────────
NAV = [('Servicios', '/servicios'), ('Zonas', '/zonas'), ('Blog', '/blog'), ('Nosotros', '/sobre-nosotros'), ('Contacto', '/contacto')]
