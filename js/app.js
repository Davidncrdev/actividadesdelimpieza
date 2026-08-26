/* Actividades de Limpieza — JS compartido v4 */
(function () {
  'use strict';

  /* ── Utilidades ── */
  const $ = (sel, ctx) => (ctx || document).querySelector(sel);
  const $$ = (sel, ctx) => Array.from((ctx || document).querySelectorAll(sel));

  /* ── Consentimiento de cookies (GTM Consent Mode v2) ── */
  const CONSENT_KEY = 'adl_consent';
  function gtag() { window.dataLayer.push(arguments); }
  function applyConsent(granted) {
    gtag('consent', 'update', {
      ad_storage: granted ? 'granted' : 'denied',
      analytics_storage: granted ? 'granted' : 'denied',
      ad_user_data: granted ? 'granted' : 'denied',
      ad_personalization: granted ? 'granted' : 'denied',
    });
  }
  const banner = $('.cookie-banner');
  if (banner) {
    const stored = (function () {
      try { return localStorage.getItem(CONSENT_KEY); } catch (e) { return null; }
    })();
    if (stored) {
      applyConsent(stored === 'accepted');
    } else {
      setTimeout(() => banner.classList.add('is-visible'), 1200);
      const acceptBtn = $('[data-consent="accept"]', banner);
      const declineBtn = $('[data-consent="decline"]', banner);
      const setConsent = (value) => {
        try { localStorage.setItem(CONSENT_KEY, value); } catch (e) {}
        applyConsent(value === 'accepted');
        banner.classList.remove('is-visible');
        track('consent_' + value);
      };
      if (acceptBtn) acceptBtn.addEventListener('click', () => setConsent('accepted'));
      if (declineBtn) declineBtn.addEventListener('click', () => setConsent('declined'));
    }
  }

  /* ── dataLayer para GTM ── */
  function track(event, params) {
    if (window.dataLayer) {
      window.dataLayer.push(Object.assign({ event: event }, params));
    }
  }

  /* ── Navbar: estado al hacer scroll ── */
  const nav = $('.nav');
  if (nav) {
    const onScroll = () => nav.classList.toggle('is-scrolled', window.scrollY > 8);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* ── Menú móvil ── */
  const burger = $('.nav-burger');
  const mobileMenu = $('.mobile-menu');
  if (burger && mobileMenu) {
    const close = () => {
      mobileMenu.classList.remove('is-open');
      burger.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    };
    burger.addEventListener('click', () => {
      const open = mobileMenu.classList.toggle('is-open');
      burger.setAttribute('aria-expanded', String(open));
      document.body.style.overflow = open ? 'hidden' : '';
      if (open) track('menu_open');
    });
    $$('a', mobileMenu).forEach((a) => a.addEventListener('click', close));
  }

  /* ── Barra CTA móvil: aparece tras el hero ── */
  const mobileCta = $('.mobile-cta');
  if (mobileCta) {
    const hero = $('.hero') || $('.page-hero');
    if (hero) {
      const onScroll = () => {
        const past = window.scrollY > hero.offsetHeight * 0.55;
        mobileCta.classList.toggle('is-visible', past);
      };
      onScroll();
      window.addEventListener('scroll', onScroll, { passive: true });
    }
  }

  /* ── Reveal al hacer scroll (a prueba de fallos) ── */
  const revealEls = $$('[data-reveal]');
  if (revealEls.length) {
    const reveal = (el) => el.classList.add('is-revealed');
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const inView = (el) => {
      const r = el.getBoundingClientRect();
      return r.top < window.innerHeight * 0.92 && r.bottom > 0;
    };
    if (reduced || !('IntersectionObserver' in window)) {
      revealEls.forEach(reveal);
    } else {
      const io = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              reveal(entry.target);
              io.unobserve(entry.target);
            }
          });
        },
        { threshold: 0.1, rootMargin: '0px 0px -6% 0px' }
      );
      revealEls.forEach((el) => {
        if (inView(el)) { reveal(el); return; } /* visibles de entrada: sin esperar al IO */
        io.observe(el);
      });
      /* Red de seguridad: si el IO fallara, el scroll/resize re-comprueba; barrido a los 4 s. */
      const recheck = () =>
        revealEls.forEach((el) => {
          if (inView(el) && !el.classList.contains('is-revealed')) reveal(el);
        });
      window.addEventListener('scroll', recheck, { passive: true });
      window.addEventListener('resize', recheck, { passive: true });
      setTimeout(recheck, 4000);
    }
  }

  /* ── Contadores animados ── */
  const counters = $$('[data-count]');
  if (counters.length) {
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const animate = (el) => {
      const target = parseFloat(el.getAttribute('data-count'));
      const decimals = el.getAttribute('data-decimals') ? parseInt(el.getAttribute('data-decimals'), 10) : 0;
      const duration = 1400;
      const start = performance.now();
      const tick = (now) => {
        const p = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - p, 3);
        const value = target * eased;
        el.textContent = value.toFixed(decimals).replace('.', ',');
        if (p < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    };
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            if (!reduced) animate(entry.target);
            else entry.target.textContent = parseFloat(entry.target.getAttribute('data-count')).toLocaleString('es-ES');
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.4 }
    );
    counters.forEach((el) => io.observe(el));
  }

  /* ── Acordeón FAQ ── */
  $$('.faq-item').forEach((item) => {
    const q = $('.faq-q', item);
    if (!q) return;
    q.addEventListener('click', () => {
      const open = item.getAttribute('data-open') === 'true';
      item.setAttribute('data-open', String(!open));
      q.setAttribute('aria-expanded', String(!open));
      if (!open) track('faq_open', { question: q.textContent.trim().slice(0, 80) });
    });
  });

  /* ── Eventos de conversión (GTM) ── */
  $$('a[href*="wa.me"]').forEach((a) =>
    a.addEventListener('click', () => track('whatsapp_click', { location: a.getAttribute('data-ctx') || 'general' }))
  );
  $$('a[href^="tel:"]').forEach((a) =>
    a.addEventListener('click', () => track('call_click'))
  );
  $$('form').forEach((f) =>
    f.addEventListener('submit', () => track('form_submit', { form: f.id || 'general' }))
  );

  /* ── Validación de formularios ── */
  function validateField(field) {
    const wrapper = field.closest('.field');
    if (!wrapper) return true;
    const ok = field.validity.valid;
    wrapper.classList.toggle('invalid', !ok);
    return ok;
  }
  function validateForm(form) {
    let valid = true;
    $$('input, select, textarea', form).forEach((field) => {
      if (field.hasAttribute('required') && !validateField(field)) valid = false;
    });
    return valid;
  }
  $$('form[data-validate]').forEach((form) => {
    form.addEventListener('input', (e) => {
      if (e.target.matches('input, select, textarea')) validateField(e.target);
    });
    form.addEventListener('submit', (e) => {
      if (!validateForm(form)) e.preventDefault();
    });
  });

  /* ── Formulario multi-paso de presupuesto ── */
  const quoteForm = $('#quote-form');
  if (quoteForm) {
    const panels = $$('.step-panel', quoteForm);
    const dots = $$('.step-dot', quoteForm);
    let step = 1;

    window.goToStep = function (next, fromValidate) {
      const current = panels[step - 1];
      const go = (target) => {
        current.classList.remove('is-active');
        panels[target - 1].classList.add('is-active');
        dots.forEach((d, i) => d.classList.toggle('is-active', i < target));
        step = target;
        window.scrollTo({ top: quoteForm.offsetTop - 120, behavior: 'smooth' });
      };
      if (fromValidate) {
        let ok = true;
        $$('input, select, textarea', current).forEach((f) => {
          if (f.hasAttribute('required') && !validateField(f)) ok = false;
        });
        if (!ok) return;
        go(next);
      } else {
        go(next);
      }
    };

    quoteForm.addEventListener('submit', function (e) {
      e.preventDefault();
      let ok = true;
      $$('input, select, textarea', quoteForm).forEach((f) => {
        if (f.hasAttribute('required') && !validateField(f)) ok = false;
      });
      if (!ok) return;

      const d = new FormData(quoteForm);
      const text =
        'Hola 👋, solicito presupuesto de limpieza:' +
        '\n\n*Nombre:* ' + (d.get('nombre') || '—') +
        '\n*Teléfono:* ' + (d.get('telefono') || '—') +
        '\n*Email:* ' + (d.get('email') || '—') +
        '\n*Empresa/Comunidad:* ' + (d.get('empresa') || '—') +
        '\n*Servicio:* ' + (d.get('servicio') || '—') +
        '\n*Frecuencia:* ' + (d.get('frecuencia') || '—') +
        '\n*Zona:* ' + (d.get('zona') || '—') +
        '\n*m² aprox:* ' + (d.get('metros') || '—') +
        '\n*Mensaje:* ' + (d.get('mensaje') || '—');
      const wa = quoteForm.getAttribute('data-wa');
      window.open('https://wa.me/' + wa + '?text=' + encodeURIComponent(text), '_blank');
      track('quote_submit');
      window.location.href = 'gracias.html';
    });
  }

  /* ── Formularios genéricos que envían por WhatsApp (data-wa, sin #quote-form) ── */
  $$('form[data-wa]').forEach((form) => {
    if (form.id === 'quote-form') return;
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      let ok = true;
      $$('input, select, textarea', form).forEach((f) => {
        if (f.hasAttribute('required') && !validateField(f)) ok = false;
      });
      if (!ok) return;
      const d = new FormData(form);
      const lines = [];
      d.forEach((value, key) => {
        const label = form.querySelector('[name="' + key + '"]');
        const text = label ? (label.closest('.field').querySelector('label').textContent.trim().replace(/\s*\*\s*$/, '')) : key;
        lines.push('*' + text + ':* ' + (value || '—'));
      });
      const wa = form.getAttribute('data-wa');
      window.open('https://wa.me/' + wa + '?text=' + encodeURIComponent(lines.join('\n')), '_blank');
      track('contact_submit');
      window.location.href = 'gracias.html';
    });
  });

  /* ── Año en el footer ── */
  const year = $('[data-year]');
  if (year) year.textContent = String(new Date().getFullYear());

  /* ── Selector de servicio que preselecciona vía URL (?servicio=...) ── */
  const params = new URLSearchParams(window.location.search);
  const wanted = params.get('servicio');
  if (wanted) {
    const sel = $('#quote-form select[name="servicio"]');
    if (sel) {
      const opt = $$('option', sel).find((o) => o.value === wanted);
      if (opt) sel.value = wanted;
    }
  }
})();
