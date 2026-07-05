# Static PWA Pattern

Use this when the app is mostly static assets, a vanilla PWA, Vite/React static export, or any app whose runtime can be served by an unprivileged static web server.

## Runtime Shape

- Use a QA/build stage with Node or the app's build tooling.
- Use a final runtime image with no Node runtime when the app only needs static serving.
- Copy only the runtime artifact set into the final image.
- Run the server as a non-root user on container port `8080` unless the repo already standardizes on another port.
- Add a healthcheck that requests `/`.

## Runtime Files

For no-build static apps, copy only files like:

- `index.html`
- app JavaScript and CSS
- `manifest.json`
- `sw.js`
- `icons/`
- `fonts/`
- other explicitly referenced public assets

For build-output apps, copy only the build output directory, usually `dist/`, `build/`, or `public/`, plus any required server config.

## Cache Headers

Default static PWA intent:

- No-cache: `/`, `index.html`, app shell JS/CSS, `sw.js`, `manifest.json`.
- Immutable: hashed build assets, fonts, icons, and versioned media.
- Avoid long caching for unversioned app shell files.

## Security Headers

Add practical browser headers:

- `X-Content-Type-Options: nosniff`
- `Referrer-Policy`
- `Permissions-Policy`
- `X-Frame-Options` or CSP `frame-ancestors`
- CSP or CSP report-only matching the existing app

Do not add HSTS for plain HTTP localhost or IP-only QA. Add HSTS only in the HTTPS reverse-proxy/TLS phase.

## SPA Fallback

If the app owns client-side routes, fall back unknown app routes to `/index.html`. Keep asset paths strict enough that missing `.js`, `.css`, `.json`, `.png`, `.svg`, `.ttf`, `.woff`, or `.woff2` files return 404 instead of the HTML shell.

## Good First Compose Service

Use a normal service plus a QA profile:

```yaml
services:
  app:
    build:
      context: .
      target: runtime
    ports:
      - "${APP_PORT:-8080}:8080"
    read_only: true
    tmpfs:
      - /tmp
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL

  qa:
    profiles: ["qa"]
    build:
      context: .
      target: qa
```
