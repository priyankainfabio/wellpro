# Wellpro Static Mirror

This repository contains a portable static mirror of `https://wellpro.one/`.

## Local Preview

Serve the `docs/` folder as the web root:

```powershell
python -m http.server 8080 -d docs
```

Then open:

```text
http://localhost:8080/
```

## GitHub Pages

In the repository settings, deploy from:

- Branch: `main`
- Folder: `/docs`

The `docs/.nojekyll` file is included so GitHub Pages serves the mirrored assets directly.

## Vercel

The root `vercel.json` deploys `docs` as the static output directory, enables clean URLs, and redirects common `.html` URLs to folder-style routes.

No build step is required.

## Notes

- CSS, JavaScript, images, and web fonts are stored under `docs/assets/`.
- Runtime page-hit analytics were disabled for offline and privacy-friendly use.
- Remaining `http://` and `https://` strings are outbound links, schema metadata, SVG namespaces, comments, or other non-asset references unless noted during verification.
