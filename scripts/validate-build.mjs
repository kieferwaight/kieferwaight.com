import { readFile, readdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const dist = path.join(root, 'dist');
const siteOrigin = 'https://kieferwaight.com';

function fail(errors) {
    if (errors.length === 0) return;
    console.error(errors.map((error) => `- ${error}`).join('\n'));
    process.exitCode = 1;
}

async function walk(directory) {
    const entries = await readdir(directory, { withFileTypes: true });
    const paths = await Promise.all(entries.map(async (entry) => {
        const filePath = path.join(directory, entry.name);
        return entry.isDirectory() ? walk(filePath) : filePath;
    }));
    return paths.flat();
}

function canonicalHref(html) {
    const linkTags = html.match(/<link\b[^>]*>/gi) ?? [];
    const canonical = linkTags.find((tag) => /\brel=["']canonical["']/i.test(tag));
    return canonical?.match(/\bhref=["']([^"']+)["']/i)?.[1] ?? null;
}

function hasSitemapLink(html) {
    const linkTags = html.match(/<link\b[^>]*>/gi) ?? [];
    return linkTags.some((tag) => /\brel=["']sitemap["']/i.test(tag) && /\bhref=["']\/sitemap-index\.xml["']/i.test(tag));
}

function htmlMeta(html, attribute, value) {
    const match = html.match(new RegExp(`<meta[^>]*${attribute}=["']${value}["'][^>]*content=["']([^"']*)["']`, 'i'))
        ?? html.match(new RegExp(`<meta[^>]*content=["']([^"']*)["'][^>]*${attribute}=["']${value}["'][^>]*>`, 'i'));
    return match?.[1] ?? null;
}

function routeFromHtml(filePath) {
    const relative = path.relative(dist, filePath).split(path.sep).join('/');
    if (relative === 'index.html') return '/';
    if (!relative.endsWith('/index.html')) return null;
    return `/${relative.slice(0, -'/index.html'.length)}/`;
}

function normalizeUrl(value) {
    const url = new URL(value, siteOrigin);
    return `${url.origin}${url.pathname}`.replace(/([^:])\/\/+/, '$1/').replace(/\/$/, '') || `${siteOrigin}/`;
}

async function readSitemapUrls() {
    const errors = [];
    const indexPath = path.join(dist, 'sitemap-index.xml');
    const indexXml = await readFile(indexPath, 'utf8').catch(() => null);
    if (!indexXml) return { urls: new Set(), errors: ['dist/sitemap-index.xml is missing'] };

    const childPaths = [...indexXml.matchAll(/<loc>([^<]+)<\/loc>/g)].map(([_, url]) => {
        const pathname = new URL(url).pathname.replace(/^\//, '');
        return path.join(dist, pathname);
    });
    const urls = new Set();
    for (const childPath of childPaths) {
        const xml = await readFile(childPath, 'utf8').catch(() => null);
        if (!xml) {
            errors.push(`sitemap child is missing: ${path.relative(dist, childPath)}`);
            continue;
        }
        for (const [, url] of xml.matchAll(/<loc>([^<]+)<\/loc>/g)) urls.add(normalizeUrl(url));
    }
    return { urls, errors };
}

async function main() {
    const errors = [];
    const htmlFiles = (await walk(dist)).filter((filePath) => filePath.endsWith('.html'));
    const pages = new Map();

    for (const filePath of htmlFiles) {
        const route = routeFromHtml(filePath);
        if (!route) continue;
        const html = await readFile(filePath, 'utf8');
        const canonical = canonicalHref(html);
        const normalizedRoute = normalizeUrl(`${siteOrigin}${route}`);
        if (!canonical) errors.push(`${route} is missing a canonical link`);
        else if (normalizeUrl(canonical) !== normalizedRoute) errors.push(`${route} canonical does not match the route: ${canonical}`);
        if (!html.match(/<title>\s*[^<]+\s*<\/title>/i)) errors.push(`${route} is missing a non-empty title`);
        if (!htmlMeta(html, 'name', 'description')) errors.push(`${route} is missing a meta description`);
        if (!htmlMeta(html, 'property', 'og:title')) errors.push(`${route} is missing og:title`);
        if (!htmlMeta(html, 'property', 'og:image')) errors.push(`${route} is missing og:image`);
        if (!hasSitemapLink(html)) errors.push(`${route} is missing the sitemap discovery link`);
        const jsonLd = html.match(/<script[^>]*type=["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/i)?.[1];
        if (!jsonLd) errors.push(`${route} is missing JSON-LD`);
        else {
            try {
                const parsed = JSON.parse(jsonLd);
                if (parsed.url && normalizeUrl(parsed.url) !== normalizedRoute) errors.push(`${route} JSON-LD url does not match the route`);
            } catch {
                errors.push(`${route} contains invalid JSON-LD`);
            }
        }
        if (pages.has(normalizedRoute)) errors.push(`${route} duplicates canonical URL ${canonical}`);
        pages.set(normalizedRoute, route);
    }

    const sitemap = await readSitemapUrls();
    errors.push(...sitemap.errors);
    const robots = await readFile(path.join(dist, 'robots.txt'), 'utf8').catch(() => null);
    if (!robots) errors.push('dist/robots.txt is missing');
    else if (!robots.includes(`Sitemap: ${siteOrigin}/sitemap-index.xml`)) errors.push('robots.txt is missing the sitemap index URL');
    for (const [url, route] of pages) if (!sitemap.urls.has(url)) errors.push(`${route} is missing from the sitemap`);
    for (const url of sitemap.urls) if (!pages.has(url)) errors.push(`sitemap contains a route without generated HTML: ${url}`);
    fail(errors);
    if (errors.length === 0) console.log(`Build validation passed: ${pages.size} pages and ${sitemap.urls.size} sitemap URLs.`);
}

main().catch((error) => {
    console.error(error.message);
    process.exitCode = 1;
});