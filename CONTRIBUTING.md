# Contributing

Thanks for taking the time to contribute. This is a personal portfolio and archive, so changes should be focused, factual, and consistent with the existing site.

## Before you start

- Open an issue first for substantial changes.
- Do not submit private, copyrighted, or unverified material for the archive.
- Keep public URLs, historical claims, and source citations accurate.

## Local workflow

1. Install dependencies with `npm install`.
2. Start the site with `npm run dev`.
3. Run `npm run check` and `npm run build` before opening a pull request.

## Content and assets

- Put authored Markdown in the appropriate `src/content/` collection.
- Keep canonical URLs explicit in frontmatter.
- Do not add large images to Git. Upload originals and responsive variants to R2 with `npm run images:upload`, then reference `https://images.kieferwaight.com/...`.
- Edit Mermaid sources in `src/diagrams/`, not generated SVGs.

## Pull requests

Describe the user-visible change, link related issues, and include validation results. Keep each pull request narrowly scoped.