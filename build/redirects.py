"""Redirecciones 301 desde las URLs del antiguo WordPress (indexadas en Google) a las páginas nuevas.
Mantienen el posicionamiento al cambiar de plataforma."""

OLD = {
    # home
    '/empresa-de-limpieza-en-malaga': '/',
    '/en': '/',
    '/author/condursa': '/',
    # Málaga capital y barrios
    '/actividades-de-limpieza-en-malaga.html': '/limpieza-malaga',
    '/empresa-de-limpieza-y-mantenimiento-en-malaga.html': '/limpieza-malaga',
    '/especialistas-en-mantenimiento-y-limpieza-en-malaga.html': '/limpieza-malaga',
    '/empresa-de-limpieza-y-mantenimiento-en-teatinos.html': '/limpieza-malaga',
    '/empresa-de-limpieza-y-mantenimiento-en-el-limonar.html': '/limpieza-malaga',
    '/empresa-de-limpieza-y-mantenimiento-en-cruz-de-humilladero': '/limpieza-malaga',
    '/empresa-de-limpieza-y-mantenimiento-en-cerrado-calderon': '/limpieza-malaga',
    # Costa
    '/empresa-de-limpieza-y-mantenimiento-en-benalmadena.html': '/limpieza-benalmadena',
    '/empresa-de-limpieza-y-mantenimiento-en-rincon-de-la-victoria.html': '/limpieza-rincon-de-la-victoria',
    # oficinas y locales
    '/limpieza-de-oficinas-y-empresas-en-malaga': '/limpieza-oficinas',
    '/limpieza-de-oficinas-y-empresas-en-el-palo-malaga': '/limpieza-oficinas',
    '/limpieza-de-oficinas-y-empresas-en-teatinos': '/limpieza-oficinas',
    '/limpieza-de-oficinas-y-empresas-en-benalmadena': '/limpieza-benalmadena',
    '/limpieza-de-oficinas-en-malaga.html': '/limpieza-oficinas',
    '/empresa-de-limpieza-de-locales-comerciales-en-malaga.html': '/limpieza-oficinas',
    # comunidades
    '/limpieza-y-mantenimiento-de-comunidades-rincon-de-la-victoria': '/limpieza-rincon-de-la-victoria',
    '/limpieza-y-mantenimiento-de-comunidades-en-benalmadena': '/limpieza-benalmadena',
    '/limpieza-y-mantenimiento-de-comunidades-en-cruz-de-humilladero': '/limpieza-comunidades',
    '/limpieza-y-mantenimiento-de-comunidades-en-teatinos': '/limpieza-comunidades',
    '/limpieza-y-mantenimiento-de-comunidades-en-malaga.html': '/limpieza-comunidades',
    '/mantenimiento-de-comunidades-en-general-en-malaga.html': '/limpieza-comunidades',
    # fin de obra
    '/limpieza-finalizacion-de-obra-locales-comerciales-malaga-provincia': '/limpieza-fin-de-obra',
    '/empresa-especialista-limpieza-fin-de-obra-en-malaga': '/limpieza-fin-de-obra',
    '/limpieza-fin-de-obra-en-benalmadena': '/limpieza-fin-de-obra',
    '/limpieza-fin-de-obra-en-teatinos': '/limpieza-fin-de-obra',
    '/limpieza-fin-de-obra-en-cruz-de-humilladero': '/limpieza-fin-de-obra',
    # parkings y desinfección
    '/especialistas-en-limpieza-de-parkings-en-malaga.html': '/limpieza-parkings',
    '/empresa-desinfeccion-en-comunidades-y-locales-comerciales-malaga': '/servicios',
    # páginas generales
    '/galeria': '/servicios',
    '/accesibilidad': '/',
    '/home': '/',
    '/inicio': '/',
    '/privacidad': '/politica-privacidad',
}


def build_redirects(apex='actividadesdelimpieza.com', www='www.actividadesdelimpieza.com'):
    out = [{'source': '/(.*)', 'has': [{'type': 'host', 'value': apex}], 'destination': 'https://%s/$1' % www, 'permanent': True}]
    for src, dst in OLD.items():
        out.append({'source': src, 'destination': dst, 'permanent': True})
        if not src.endswith('.html'):
            out.append({'source': src + '/', 'destination': dst, 'permanent': True})
    return out
