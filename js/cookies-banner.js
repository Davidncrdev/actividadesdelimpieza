// Cookie Consent Banner - RGPD Compliant
(function() {
  'use strict';

  const COOKIE_NAME = 'cookie_consent';
  const COOKIE_EXPIRY = 365; // días

  function getCookie(name) {
    const value = '; ' + document.cookie;
    const parts = value.split('; ' + name + '=');
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
  }

  function setCookie(name, value, days) {
    const date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    document.cookie = name + '=' + value + ';expires=' + date.toUTCString() + ';path=/;SameSite=Lax;Secure';
  }

  function createBanner() {
    const banner = document.createElement('div');
    banner.id = 'cookie-banner';
    banner.setAttribute('role', 'dialog');
    banner.setAttribute('aria-labelledby', 'cookie-title');
    banner.setAttribute('aria-modal', 'true');
    banner.innerHTML = `
      <style>
        #cookie-banner {
          position: fixed;
          bottom: 0;
          left: 0;
          right: 0;
          background: #1e293b;
          color: #f8fafc;
          z-index: 9999;
          padding: 20px 0;
          box-shadow: 0 -4px 20px rgba(0,0,0,0.25);
          font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          font-size: 14px;
          line-height: 1.6;
          animation: slideUp 0.5s ease;
        }
        @keyframes slideUp {
          from { transform: translateY(100%); }
          to { transform: translateY(0); }
        }
        #cookie-banner .cookie-container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 0 20px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 20px;
          flex-wrap: wrap;
        }
        #cookie-banner .cookie-text {
          flex: 1;
          min-width: 280px;
        }
        #cookie-banner .cookie-text h3 {
          font-size: 16px;
          margin-bottom: 6px;
          color: #10b981;
        }
        #cookie-banner .cookie-text p {
          margin: 0;
          font-size: 13px;
          color: #b0b0b0;
        }
        #cookie-banner .cookie-text a {
          color: #34d399;
          text-decoration: underline;
        }
        #cookie-banner .cookie-text a:hover {
          color: #10b981;
        }
        #cookie-banner .cookie-buttons {
          display: flex;
          gap: 10px;
          flex-wrap: wrap;
          align-items: center;
        }
        #cookie-banner .btn-cookie {
          padding: 10px 20px;
          border: none;
          border-radius: 8px;
          font-weight: 600;
          font-size: 13px;
          cursor: pointer;
          transition: all 0.3s ease;
          font-family: inherit;
          white-space: nowrap;
        }
        #cookie-banner .btn-accept-all {
          background: #10b981;
          color: white;
          box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.3);
        }
        #cookie-banner .btn-accept-all:hover {
          background: #059669;
          transform: translateY(-1px);
          box-shadow: 0 6px 10px -1px rgba(16, 185, 129, 0.4);
        }
        #cookie-banner .btn-accept-essential {
          background: transparent;
          color: #b0b0b0;
          border: 1px solid #475569;
        }
        #cookie-banner .btn-accept-essential:hover {
          background: rgba(255,255,255,0.05);
          color: #f8fafc;
        }
        #cookie-banner .btn-settings {
          background: transparent;
          color: #34d399;
          border: 1px solid #34d399;
        }
        #cookie-banner .btn-settings:hover {
          background: rgba(52, 211, 153, 0.1);
        }
        @media (max-width: 768px) {
          #cookie-banner .cookie-container {
            flex-direction: column;
            text-align: center;
          }
          #cookie-banner .cookie-buttons {
            justify-content: center;
            width: 100%;
          }
        }
      </style>
      <div class="cookie-container">
        <div class="cookie-text">
          <h3 id="cookie-title">🍪 Este sitio utiliza cookies</h3>
          <p>Utilizamos cookies propias y de terceros para mejorar tu experiencia, analizar el tráfico y mostrar contenido personalizado. Puedes aceptar todas las cookies o configurar tus preferencias. 
          <a href="cookies.html" target="_blank" rel="noopener">Más información</a></p>
        </div>
        <div class="cookie-buttons">
          <button class="btn-cookie btn-accept-essential" onclick="acceptCookies('essential')" aria-label="Aceptar solo cookies esenciales">
            Solo esenciales
          </button>
          <button class="btn-cookie btn-settings" onclick="window.location.href='cookies.html'" aria-label="Configurar preferencias de cookies">
            Configurar
          </button>
          <button class="btn-cookie btn-accept-all" onclick="acceptCookies('all')" aria-label="Aceptar todas las cookies">
            Aceptar todas
          </button>
        </div>
      </div>
    `;
    document.body.appendChild(banner);
  }

  window.acceptCookies = function(preference) {
    setCookie(COOKIE_NAME, preference, COOKIE_EXPIRY);
    const banner = document.getElementById('cookie-banner');
    if (banner) {
      banner.style.animation = 'fadeOut 0.3s ease forwards';
      setTimeout(() => banner.remove(), 300);
    }
    
    // Activar analytics según preferencia
    if (preference === 'all' && typeof gtag !== 'undefined') {
      gtag('consent', 'update', {
        'analytics_storage': 'granted',
        'ad_storage': 'granted'
      });
    }
    
    if (preference === 'essential' && typeof gtag !== 'undefined') {
      gtag('consent', 'update', {
        'analytics_storage': 'denied',
        'ad_storage': 'denied'
      });
    }
  };

  // Inicializar
  const consent = getCookie(COOKIE_NAME);
  if (!consent) {
    // Esperar a que el DOM cargue
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', createBanner);
    } else {
      createBanner();
    }
  }
})();
