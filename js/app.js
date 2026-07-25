document.addEventListener('DOMContentLoaded', () => {

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;

  /* ─── Mobile Menu ─── */
  const menuBtn = document.querySelector('.mobile-menu-btn');
  const navLinks = document.querySelector('.nav-links');
  const navAnchors = navLinks ? navLinks.querySelectorAll('a:not(.nav-cta)') : [];
  const body = document.body;

  if (menuBtn && navLinks) {
    menuBtn.addEventListener('click', () => {
      const expanded = menuBtn.getAttribute('aria-expanded') === 'true';
      menuBtn.setAttribute('aria-expanded', !expanded);
      navLinks.classList.toggle('active');
      const icon = menuBtn.querySelector('i');
      if (icon) {
        icon.className = navLinks.classList.contains('active') ? 'fas fa-times' : 'fas fa-bars';
      }
      body.style.overflow = navLinks.classList.contains('active') ? 'hidden' : '';
    });

    navAnchors.forEach(a => {
      a.addEventListener('click', () => {
        navLinks.classList.remove('active');
        menuBtn.setAttribute('aria-expanded', 'false');
        menuBtn.focus();
        const icon = menuBtn.querySelector('i');
        if (icon) icon.className = 'fas fa-bars';
        body.style.overflow = '';
      });
    });

    document.addEventListener('click', e => {
      if (navLinks.classList.contains('active') &&
          !navLinks.contains(e.target) &&
          !menuBtn.contains(e.target)) {
        navLinks.classList.remove('active');
        menuBtn.setAttribute('aria-expanded', 'false');
        const icon = menuBtn.querySelector('i');
        if (icon) icon.className = 'fas fa-bars';
        body.style.overflow = '';
      }
    });
  }

  /* ─── Active Nav Link on Scroll ─── */
  const sections = document.querySelectorAll('section[id]');
  const navItems = document.querySelectorAll('.nav-links a:not(.nav-cta)');

  if (sections.length && navItems.length && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          navItems.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === '#' + entry.target.id) {
              link.classList.add('active');
            }
          });
        }
      });
    }, { rootMargin: '-40% 0px -55% 0px' });

    sections.forEach(section => observer.observe(section));
  }

  /* ─── Header scroll effect ─── */
  const header = document.querySelector('header');
  let lastScroll = 0;

  window.addEventListener('scroll', () => {
    const scrollY = window.scrollY;
    header.classList.toggle('scrolled', scrollY > 50);
    lastScroll = scrollY;
  }, { passive: true });

  /* ─── Back to Top ─── */
  const backToTop = document.querySelector('.back-to-top');
  if (backToTop) {
    window.addEventListener('scroll', () => {
      backToTop.classList.toggle('visible', window.scrollY > 500);
    }, { passive: true });

    backToTop.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  /* ─── Smooth Scroll for anchor links (no Lenis fallback) ─── */
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', e => {
      const href = anchor.getAttribute('href');
      if (href === '#') return;
      const target = document.querySelector(href);
      if (target) {
        e.preventDefault();
        const offset = header ? header.offsetHeight : 70;
        const top = target.getBoundingClientRect().top + window.pageYOffset - offset;
        window.scrollTo({ top, behavior: 'smooth' });
      }
    });
  });

  /* ─── GSAP Animations ─── */
  if (!prefersReducedMotion && typeof gsap !== 'undefined') {

    gsap.registerPlugin(ScrollTrigger);

    /* Hero stagger animation */
    const heroTl = gsap.timeline({ defaults: { ease: 'power3.out' } });
    heroTl
      .from('.hero-badge', { opacity: 0, y: 20, duration: 0.6 })
      .from('.hero-text h1', { opacity: 0, y: 40, duration: 0.8 }, '-=0.3')
      .from('.hero-text p', { opacity: 0, y: 30, duration: 0.6 }, '-=0.4')
      .from('.hero-btns .btn', { opacity: 0, y: 20, duration: 0.5, stagger: 0.15 }, '-=0.3')
      .from('.hero-image', { opacity: 0, x: 60, duration: 0.8, ease: 'power2.out' }, '-=0.5');

    /* Stats counter animation */
    const statsSection = document.querySelector('.stats-bar');
    if (statsSection) {
      ScrollTrigger.create({
        trigger: statsSection,
        start: 'top 85%',
        onEnter: () => {
          document.querySelectorAll('.stat-number').forEach(el => {
            const target = parseInt(el.getAttribute('data-target'), 10);
            if (!target) return;
            const suffix = el.getAttribute('data-suffix') || '';
            let current = 0;
            const increment = Math.ceil(target / 60);
            const interval = setInterval(() => {
              current += increment;
              if (current >= target) {
                current = target;
                clearInterval(interval);
              }
              el.textContent = current.toLocaleString('es') + suffix;
            }, 25);
          });
        },
        once: true,
      });
    }

    /* Section reveal animations */
    const sections = document.querySelectorAll('section');
    sections.forEach(section => {
      const items = section.querySelectorAll(
        '.service-card, .gallery-card, .timeline-item, .feature-item, .faq-item, .stat-item'
      );
      if (items.length) {
        gsap.from(items, {
          opacity: 0,
          y: 40,
          duration: 0.6,
          stagger: 0.1,
          ease: 'power2.out',
          scrollTrigger: {
            trigger: section,
            start: 'top 80%',
          },
        });
      }

      const headers = section.querySelectorAll('.section-header');
      if (headers.length) {
        gsap.from(headers, {
          opacity: 0,
          y: 30,
          duration: 0.6,
          ease: 'power2.out',
          scrollTrigger: {
            trigger: section,
            start: 'top 85%',
          },
        });
      }
    });

    /* About section animation */
    const aboutContent = document.querySelector('.about-content');
    if (aboutContent) {
      gsap.from('.about-text', {
        opacity: 0,
        x: -40,
        duration: 0.8,
        ease: 'power2.out',
        scrollTrigger: {
          trigger: aboutContent,
          start: 'top 80%',
        },
      });
      gsap.from('.about-img', {
        opacity: 0,
        x: 40,
        duration: 0.8,
        ease: 'power2.out',
        scrollTrigger: {
          trigger: aboutContent,
          start: 'top 80%',
        },
      });
    }

    /* Parallax on hero background shapes */
    gsap.to('.hero::before', {
      y: -80,
      ease: 'none',
      scrollTrigger: {
        trigger: '.hero',
        start: 'top top',
        end: 'bottom top',
        scrub: true,
      },
    });

    /* Timeline line animation */
    const timelineLine = document.querySelector('.process-timeline::before');
    if (timelineLine) {
      gsap.from('.process-timeline::before', {
        scaleY: 0,
        transformOrigin: 'top center',
        duration: 1,
        scrollTrigger: {
          trigger: '.process-timeline',
          start: 'top 80%',
          end: 'bottom 20%',
          scrub: 1,
        },
      });
    }

    /* Contact section CTAs */
    const contactCtas = document.querySelectorAll('.contact .btn, .contact-info h3');
    if (contactCtas.length) {
      gsap.from(contactCtas, {
        opacity: 0,
        y: 30,
        duration: 0.6,
        stagger: 0.15,
        ease: 'power2.out',
        scrollTrigger: {
          trigger: '.contact',
          start: 'top 80%',
        },
      });
    }

  } else if (prefersReducedMotion) {
    /* Ensure all animated elements are visible */
    document.querySelectorAll('[data-animate]').forEach(el => el.classList.add('animated'));
    document.querySelectorAll('.service-card, .gallery-card, .timeline-item, .feature-item').forEach(el => {
      el.style.opacity = '1';
      el.style.transform = 'none';
    });
  }

  /* ─── FAQ Accordion ─── */
  document.querySelectorAll('.faq-question').forEach(btn => {
    btn.addEventListener('click', () => {
      const item = btn.closest('.faq-item');
      const isActive = item.classList.contains('active');

      document.querySelectorAll('.faq-item.active').forEach(el => {
        if (el !== item) el.classList.remove('active');
      });

      item.classList.toggle('active', !isActive);
      btn.setAttribute('aria-expanded', !isActive);
    });
  });

  /* ─── Form Validation ─── */
  const form = document.querySelector('.contact-form');
  if (form) {
    const fields = form.querySelectorAll('input, textarea, select');

    fields.forEach(field => {
      field.addEventListener('blur', () => validateField(field));
      field.addEventListener('input', () => {
        if (field.classList.contains('error')) validateField(field);
      });
    });

    form.addEventListener('submit', e => {
      e.preventDefault();
      let isValid = true;

      fields.forEach(field => {
        if (!validateField(field)) isValid = false;
      });

      if (isValid) {
        const data = new FormData(form);
        const params = new URLSearchParams();
        data.forEach((val, key) => params.append(key, val));

        const name = data.get('nombre') || '';
        const phone = data.get('telefono') || '';
        const message = data.get('mensaje') || '';
        const service = data.get('servicio') || '';

        const text = `Hola,%20me%20gustaría%20solicitar%20información:%0A` +
          `Nombre:%20${encodeURIComponent(name)}%0A` +
          `Teléfono:%20${encodeURIComponent(phone)}%0A` +
          `Servicio:%20${encodeURIComponent(service)}%0A` +
          `Mensaje:%20${encodeURIComponent(message)}`;

        const whatsappUrl = `https://wa.me/34642118972?text=${text}`;
        window.open(whatsappUrl, '_blank');
      }
    });

    function validateField(field) {
      const errorMsg = field.parentElement.querySelector('.error-msg');
      let isValid = true;

      if (field.required && !field.value.trim()) {
        isValid = false;
        if (errorMsg) errorMsg.textContent = 'Este campo es obligatorio';
      } else if (field.type === 'email' && field.value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(field.value)) {
        isValid = false;
        if (errorMsg) errorMsg.textContent = 'Introduce un email válido';
      } else if (field.id === 'telefono' && field.value && !/^[+\d\s()-]{7,}$/.test(field.value)) {
        isValid = false;
        if (errorMsg) errorMsg.textContent = 'Introduce un teléfono válido';
      }

      field.classList.toggle('error', !isValid);
      if (errorMsg) errorMsg.classList.toggle('visible', !isValid);
      return isValid;
    }
  }

  /* ─── Lazy loading images with Intersection Observer ─── */
  if ('IntersectionObserver' in window) {
    const lazyImages = document.querySelectorAll('img[loading="lazy"]');
    const imgObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          const src = img.getAttribute('data-src');
          if (src) {
            img.src = src;
            img.removeAttribute('data-src');
          }
          imgObserver.unobserve(img);
        }
      });
    }, { rootMargin: '200px' });

    lazyImages.forEach(img => imgObserver.observe(img));
  }

  /* ─── Web Vitals tracking (GA4) ─── */
  if (typeof gtag !== 'undefined') {
    try {
      const reportWebVitals = (metric) => {
        gtag('event', metric.name, {
          value: metric.value,
          event_category: 'Web Vitals',
          event_label: metric.id,
          non_interaction: true,
        });
      };

      if (typeof webVitals !== 'undefined') {
        webVitals.onCLS(reportWebVitals);
        webVitals.onFID(reportWebVitals);
        webVitals.onLCP(reportWebVitals);
      }
    } catch (e) {
      console.warn('Web Vitals tracking error:', e);
    }
  }

  /* ─── Keyboard navigation trap for mobile menu ─── */
  if (menuBtn && navLinks) {
    menuBtn.addEventListener('keydown', e => {
      if (e.key === 'Escape' && navLinks.classList.contains('active')) {
        navLinks.classList.remove('active');
        menuBtn.setAttribute('aria-expanded', 'false');
        const icon = menuBtn.querySelector('i');
        if (icon) icon.className = 'fas fa-bars';
        menuBtn.focus();
      }
    });
  }

  console.log('Actividades de Limpieza — web optimizada');
});
