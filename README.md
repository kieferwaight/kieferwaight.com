# Kiefer Waight — Astro site

Markdown-driven personal site built with Astro content collections.

## Commands

```sh
npm install
npm run dev
npm run check
npm run build
npm run preview
```

Content lives in `src/content/` and is validated through `src/content.config.ts`. Add a Markdown file to `writing`, `case-studies`, `research`, `archive`, `projects`, or `pages` and the matching route is generated at build time.

Diagram sources live in `src/diagrams/` as editable `.mmd` files. `npm run diagrams` compiles them into static SVGs in `public/diagrams/`; `prebuild` runs this automatically. Content references the SVGs as normal images, so diagrams have no client-side rendering delay. All other fenced code uses Astro/Shiki syntax highlighting. Canonicals, Open Graph metadata, and a sitemap are emitted from the shared site layout.
