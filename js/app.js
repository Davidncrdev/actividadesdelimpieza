/* Actividades de Limpieza — v5 */
(function () {
  'use strict';
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var clamp = function (v, a, b) { return Math.min(b, Math.max(a, v)); };

  /* ── dataLayer + consentimiento (GTM Consent Mode v2) ── */
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  function track(event, params) { window.dataLayer.push(Object.assign({ event: event }, params)); }
  function applyConsent(granted) {
    var v = granted ? 'granted' : 'denied';
    gtag('consent', 'update', { ad_storage: v, analytics_storage: v, ad_user_data: v, ad_personalization: v });
  }
  var cookie = $('[data-cookie]');
  if (cookie) {
    var stored = null;
    try { stored = localStorage.getItem('adl_consent'); } catch (e) {}
    if (stored) {
      applyConsent(stored === 'accepted');
    } else {
      cookie.classList.add('is-on');
      $$('[data-consent]', cookie).forEach(function (b) {
        b.addEventListener('click', function () {
          var val = b.getAttribute('data-consent') === 'accept' ? 'accepted' : 'declined';
          try { localStorage.setItem('adl_consent', val); } catch (e) {}
          applyConsent(val === 'accepted');
          cookie.classList.remove('is-on');
          cookieH = 0; onScroll();
          track('consent_' + val);
        });
      });
    }
  }

  /* ── Barra, menú, ficha persistente ── */
  var bar = $('[data-bar]');
  var hero = $('[data-hero]');
  var stub = $('[data-stub]');
  function heroEnd() { return hero ? hero.offsetHeight - window.innerHeight : 0; }
  var lastY = window.scrollY;
  var cookieH = cookie && cookie.classList.contains('is-on') ? cookie.offsetHeight : 0;
  function onScroll() {
    var y = window.scrollY;
    if (bar) bar.style.setProperty('--bar-top', Math.max(0, cookieH - y) + 'px');
    if (bar && hero) bar.classList.toggle('is-solid', y > heroEnd() - 40);
    if (bar) {
      var inHero = hero && y < heroEnd();
      if (y < 160 || inHero || y < lastY - 6) bar.classList.remove('is-hidden');
      else if (y > lastY + 6) bar.classList.add('is-hidden');
    }
    if (stub) {
      var floor = hero ? heroEnd() * 0.85 : 360;
      if (y < floor) stub.classList.remove('is-on');
      else if (y < lastY - 6) stub.classList.add('is-on');
      else if (y > lastY + 6) stub.classList.remove('is-on');
    }
    lastY = y;
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll);
  onScroll();

  var menu = $('#menu');
  var burger = $('.bar-burger');
  if (menu && burger) {
    var setMenu = function (open) {
      menu.classList.toggle('is-open', open);
      burger.setAttribute('aria-expanded', String(open));
      document.body.style.overflow = open ? 'hidden' : '';
      if (open) $('.menu-close', menu).focus(); else burger.focus();
    };
    burger.addEventListener('click', function () { setMenu(true); });
    $('.menu-close', menu).addEventListener('click', function () { setMenu(false); });
    $$('a', menu).forEach(function (a) { a.addEventListener('click', function () { setMenu(false); }); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && menu.classList.contains('is-open')) setMenu(false); });
  }

  /* ── Hero: la tarjeta se encoge hasta ser una ficha ── */
  var card = $('[data-hero-card]');
  if (hero && card && !reduced) {
    var body = $('[data-hero-body]', card);
    var photo = $('.hero-photo', hero);
    var stage = $('.hero-stage', hero);
    var geo = null;
    var measure = function () {
      card.style.transform = 'none';
      var c = card.getBoundingClientRect();
      var s = stage.getBoundingClientRect();
      var mobile = window.innerWidth <= 720;
      geo = { tx: (mobile ? 12 : 24) - c.left, ty: (s.bottom - (mobile ? 76 : 24)) - c.bottom, end: mobile ? 0.28 : 0.23 };
      frame();
    };
    var ease = function (t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
    var frame = function () {
      if (!geo) return;
      var max = heroEnd();
      var p = clamp(window.scrollY / max, 0, 1);
      var e = ease(clamp((p - 0.1) / 0.72, 0, 1));
      card.style.transform = 'translate3d(' + (geo.tx * e).toFixed(1) + 'px,' + (geo.ty * e).toFixed(1) + 'px,0) scale(' + (1 - (1 - geo.end) * e).toFixed(4) + ')';
      body.style.opacity = String(clamp(1 - e * 2.4, 0, 1));
      body.style.visibility = e > 0.45 ? 'hidden' : 'visible';
      card.style.opacity = String(clamp(1 - (e - 0.82) / 0.18, 0, 1));
      photo.style.transform = 'scale(' + (1.04 + p * 0.08).toFixed(4) + ')';
    };
    var ticking = false;
    window.addEventListener('scroll', function () {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(function () { ticking = false; frame(); });
    }, { passive: true });
    window.addEventListener('resize', measure);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(measure);
    measure();
  }

  /* ── Aparición al hacer scroll ── */
  $$('.prose > *, .ficha li, .fld, .form-actions, .accordion details, .service-list a, .post-row').forEach(function (el) {
    if (el.hasAttribute('data-reveal') || el.closest('[data-reveal="clip"]')) return;
    var sibs = Array.prototype.indexOf.call(el.parentNode.children, el);
    el.setAttribute('data-reveal', '');
    el.style.setProperty('--d', Math.min(sibs, 5) * 50 + 'ms');
  });
  var rev = $$('[data-reveal]');
  if (rev.length) {
    var show = function (el) { el.classList.add('is-in'); };
    if (reduced || !('IntersectionObserver' in window)) {
      rev.forEach(show);
    } else {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) { if (en.isIntersecting) { show(en.target); io.unobserve(en.target); } });
      }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
      rev.forEach(function (el) { io.observe(el); });
      setTimeout(function () {
        rev.forEach(function (el) {
          var r = el.getBoundingClientRect();
          if (r.top < window.innerHeight && r.bottom > 0) show(el);
        });
      }, 2500);
    }
  }

  /* ── Fila de momentos: arrastrar, botones y barra de avance ── */
  var rail = $('[data-rail-track]');
  if (rail) {
    var rbar = $('[data-rail-bar]');
    var btns = $$('[data-rail]');
    var upd = function () {
      var max = rail.scrollWidth - rail.clientWidth;
      var w = rail.clientWidth / rail.scrollWidth;
      var track = rbar.parentNode.clientWidth;
      rbar.style.width = (w * 100).toFixed(2) + '%';
      rbar.style.transform = 'translateX(' + (max > 0 ? (rail.scrollLeft / max) * (track - track * w) : 0).toFixed(1) + 'px)';
      btns.forEach(function (b) { b.disabled = b.getAttribute('data-rail') === '-1' ? rail.scrollLeft < 4 : rail.scrollLeft > max - 4; });
    };
    rail.addEventListener('scroll', upd, { passive: true });
    window.addEventListener('resize', upd);
    upd();
    btns.forEach(function (b) {
      b.addEventListener('click', function () {
        var m = $('.moment', rail);
        rail.scrollBy({ left: parseInt(b.getAttribute('data-rail'), 10) * (m.offsetWidth + 32), behavior: reduced ? 'auto' : 'smooth' });
      });
    });
    var drag = null;
    rail.addEventListener('pointerdown', function (e) {
      if (e.pointerType !== 'mouse') return;
      drag = { x: e.clientX, left: rail.scrollLeft };
      rail.classList.add('is-drag');
      rail.setPointerCapture(e.pointerId);
    });
    rail.addEventListener('pointermove', function (e) { if (drag) rail.scrollLeft = drag.left - (e.clientX - drag.x); });
    var end = function () { if (!drag) return; drag = null; rail.classList.remove('is-drag'); };
    rail.addEventListener('pointerup', end);
    rail.addEventListener('pointercancel', end);
    rail.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') rail.scrollBy({ left: 312, behavior: 'smooth' });
      if (e.key === 'ArrowLeft') rail.scrollBy({ left: -312, behavior: 'smooth' });
    });
  }

  /* ── Hoja de control ── */
  var sheet = $('[data-sheet]');
  if (sheet && window.ADL_LISTS) {
    var L = window.ADL_LISTS;
    var state = { space: 'Comunidad', freq: 'Semanal' };
    var list = $('[data-tasks]', sheet);
    var labels = {
      v: { Diaria: 'cada día', Semanal: 'cada visita', Quincenal: 'cada visita', Puntual: 'una vez' },
      m: { Diaria: 'cada mes', Semanal: 'cada mes', Quincenal: 'cada mes', Puntual: 'una vez' },
      x: { Diaria: 'a petición', Semanal: 'a petición', Quincenal: 'a petición', Puntual: 'a petición' }
    };
    var freqText = { Diaria: 'Visitas: diarias', Semanal: 'Visitas: semanales', Quincenal: 'Visitas: quincenales', Puntual: 'Servicio puntual' };
    var render = function () {
      var d = L[state.space];
      list.innerHTML = d.tasks.map(function (t) {
        return '<li><span class="tick" aria-hidden="true"></span><span>' + t[0] + '</span><span class="leader" aria-hidden="true"></span><em>' + labels[t[1]][state.freq] + '</em></li>';
      }).join('');
      $('[data-sheet-title]', sheet).textContent = 'Hoja de control · ' + state.space;
      $('[data-sheet-freq]', sheet).textContent = freqText[state.freq];
      $('[data-sheet-quote]', sheet).setAttribute('href', '/presupuesto?servicio=' + encodeURIComponent(d.service) + '&frecuencia=' + encodeURIComponent(state.freq));
      var msg = 'Hola, quiero un presupuesto de ' + d.service.toLowerCase() + ' (' + state.freq.toLowerCase() + '). Vi la hoja de control en la web.';
      $('[data-sheet-wa]', sheet).setAttribute('href', 'https://wa.me/' + L._wa + '?text=' + encodeURIComponent(msg));
    };
    var swap = function () {
      if (reduced) { render(); return; }
      $$('li', list).forEach(function (li, i) { li.style.transitionDelay = (i * 20) + 'ms'; li.classList.add('is-out'); });
      setTimeout(function () {
        render();
        var lis = $$('li', list);
        lis.forEach(function (li) { li.classList.add('is-out'); });
        requestAnimationFrame(function () { requestAnimationFrame(function () {
          lis.forEach(function (li, i) { li.style.transitionDelay = (i * 40) + 'ms'; li.classList.remove('is-out'); });
        }); });
      }, 160);
    };
    $$('[data-space]').forEach(function (b) {
      b.addEventListener('click', function () {
        state.space = b.getAttribute('data-space');
        $$('[data-space]').forEach(function (o) { o.setAttribute('aria-pressed', String(o === b)); });
        swap(); track('sheet_space', { space: state.space });
      });
    });
    $$('[data-freq]').forEach(function (b) {
      b.addEventListener('click', function () {
        state.freq = b.getAttribute('data-freq');
        $$('[data-freq]').forEach(function (o) { o.setAttribute('aria-pressed', String(o === b)); });
        swap();
      });
    });
    render();
  }

  /* ── Conversiones ── */
  $$('a[href*="wa.me"]').forEach(function (a) { a.addEventListener('click', function () { track('whatsapp_click', { location: a.getAttribute('data-ctx') || 'general' }); }); });
  $$('a[href^="tel:"]').forEach(function (a) { a.addEventListener('click', function () { track('call_click', { location: a.getAttribute('data-ctx') || 'general' }); }); });

  /* ── Formularios ── */
  function validField(f) {
    var w = f.closest('.fld');
    var ok = f.validity.valid;
    if (w) w.classList.toggle('invalid', !ok);
    return ok;
  }
  function validScope(scope) {
    var ok = true;
    $$('input, select, textarea', scope).forEach(function (f) { if (f.hasAttribute('required') && !validField(f)) ok = false; if (f.type === 'email' && f.value && !validField(f)) ok = false; });
    return ok;
  }
  $$('form').forEach(function (form) {
    form.addEventListener('input', function (e) { if (e.target.matches('input, select, textarea') && e.target.closest('.fld.invalid')) validField(e.target); });
  });

  var quote = $('#quote-form');
  if (quote) {
    var panels = $$('.step-panel', quote);
    var dots = $$('.steps i');
    var step = 1;
    var go = function (n) {
      panels[step - 1].classList.remove('is-active');
      panels[n - 1].classList.add('is-active');
      dots.forEach(function (d, i) { d.classList.toggle('is-on', i < n); });
      step = n;
      var f = $('input, select, textarea', panels[n - 1]);
      if (f) f.focus({ preventScroll: true });
      quote.closest('.form-sheet').scrollIntoView({ behavior: reduced ? 'auto' : 'smooth', block: 'start' });
    };
    $$('[data-step]', quote).forEach(function (b) {
      b.addEventListener('click', function () {
        var n = parseInt(b.getAttribute('data-step'), 10);
        if (n > step && !validScope(panels[step - 1])) return;
        go(n);
      });
    });
    quote.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!validScope(quote)) return;
      var d = new FormData(quote);
      var text = 'Hola, solicito presupuesto de limpieza:' +
        '\n\n*Nombre:* ' + (d.get('nombre') || '—') + '\n*Teléfono:* ' + (d.get('telefono') || '—') + '\n*Email:* ' + (d.get('email') || '—') +
        '\n*Empresa/Comunidad:* ' + (d.get('empresa') || '—') + '\n*Servicio:* ' + (d.get('servicio') || '—') + '\n*Frecuencia:* ' + (d.get('frecuencia') || '—') +
        '\n*Zona:* ' + (d.get('zona') || '—') + '\n*m² aprox:* ' + (d.get('metros') || '—') + '\n*Mensaje:* ' + (d.get('mensaje') || '—');
      window.open('https://wa.me/' + quote.getAttribute('data-wa') + '?text=' + encodeURIComponent(text), '_blank');
      track('quote_submit');
      window.location.href = '/gracias';
    });
    var qp = new URLSearchParams(window.location.search);
    ['servicio', 'frecuencia', 'zona'].forEach(function (k) {
      var v = qp.get(k), sel = $('select[name="' + k + '"]', quote);
      if (v && sel && $$('option', sel).some(function (o) { return o.value === v; })) sel.value = v;
    });
  }
  var contact = $('#contact-form');
  if (contact) {
    contact.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!validScope(contact)) return;
      var d = new FormData(contact);
      var text = 'Hola, os escribo desde la web:\n\n*Nombre:* ' + (d.get('nombre') || '—') + '\n*Teléfono:* ' + (d.get('telefono') || '—') + '\n*Email:* ' + (d.get('email') || '—') +
        '\n*Empresa/Comunidad:* ' + (d.get('empresa') || '—') + '\n*Mensaje:* ' + (d.get('mensaje') || '—');
      window.open('https://wa.me/' + contact.getAttribute('data-wa') + '?text=' + encodeURIComponent(text), '_blank');
      track('contact_submit');
      window.location.href = '/gracias';
    });
  }

  $$('video[data-loop]').forEach(function (v) { if (reduced) { v.removeAttribute('autoplay'); v.pause(); } });

  var y = $('[data-year]');
  if (y) y.textContent = String(new Date().getFullYear());
})();
