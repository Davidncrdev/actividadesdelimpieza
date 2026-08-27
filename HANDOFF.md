# Handoff — Despliegue en Vercel (27 ago 2026)

## Contexto

Sitio estático (HTML/CSS/JS vanilla, sin build) de Actividades de Limpieza (empresa de limpieza en Málaga). Para NAP oficial, decisiones de diseño y convenciones (sprite SVG inline, formularios `data-wa`, `html.js`), ver memoria del proyecto. Problemas al desplegar en Vercel: error `Header at index 1 has invalid source pattern` + errores de nombre de proyecto.

## Qué se hizo

1. **Fix `vercel.json`** — En la regla de headers nº2 (caché inmutable de estáticos), `(js|css|...)` → `(?:js|css|...)`. Vercel valida `source` con path-to-regexp v6, no con regexp: los grupos capturantes sin nombre anidados están prohibidos ("Capturing groups are not allowed"). Verificado contra path-to-regexp@6.3.0. Las reglas `/(.*)` y `/(.*\.html)` eran válidas.

2. **Proyectos de Vercel eliminados** (todos con el nombre o parecidos):
   - `actividadesdelimpieza`
   - `actividadesdelimpiezav1`
   - `adl` (siglas)
   - Ninguno tenía URL de producción. `hgo` se dejó intacto.

3. **Proyecto recreado y vinculado** — `actividadesdelimpieza` en team `davids-projects-e926ced9` (org `team_MgaFSapawsNSdqDuWSf1teaa`). Repo vinculado vía git remote (`.vercel/repo.json`).

4. **Deploy verificado** — primer deploy, asignado a producción:
   `actividadesdelimpieza-hc9kxuf4x-davids-projects-e926ced9.vercel.app`
   - `/` → 200 + cabeceras de seguridad (nosniff, SAMEORIGIN, referrer-policy)
   - `/css/styles.css`, `/js/app.js` → 200 + `cache-control: public, max-age=31536000, immutable`
   - `/contacto` → 200 (cleanUrls funcionando)
   - ⚠️ Las verificaciones requieren `vercel curl` (el Deployment Protection devuelve 302 con curl normal).

## Estado actual

- Proyecto vinculado, deploy en producción OK, cabeceras correctas.
- `.env.local` creado por el CLI y añadido a `.gitignore` (git status: `M .gitignore`).

## Pendiente / decisiones abiertas

1. **Deployment Protection ACTIVO** — el sitio pide login para verse. Para hacerlo público: dashboard → Project Settings → **Deployment Protection → Vercel Authentication → Off**. No se tocó: decisión del usuario.
2. **Dominio propio** — el sitio es actividadesdelimpieza.com. No conectado al proyecto nuevo. `vercel domains add actividadesdelimpieza.com` + verificación DNS.
3. **CLI desactualizado** — `npm i -g vercel@latest` (59.5.0 → 59.6.2).
4. **`.htaccess` en la raíz** — config Apache heredada, inerte en Vercel; se puede borrar.
5. Futuros `vercel deploy` sin `--prod` son preview; producción requiere `--prod`.

## Comandos útiles

```bash
vercel deploy --prod                          # desplegar producción
vercel curl https://actividadesdelimpieza-hc9kxuf4x-davids-projects-e926ced9.vercel.app
vercel ls                                     # estado de deployments
vercel project ls --scope davids-projects-e926ced9
```
