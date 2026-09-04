import { access, readFile, readdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const dist = path.join(root, 'dist');
const siteOrigin = 'https://kieferwaight.com';

async function walk(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const paths = await Promise.all(entries.map(async (entry) => {
    const filePath = path.join(directory, entry.name);
    return entry.isDirectory() ? walk(filePath) : filePath;
  }));
  return paths.flat();
}

function targetFile(url) {
  const pathname = decodeURIComponent(url.pathname);
  if (pathname === '/') return path.join(dist, 'index.html');
  if (pathname.endsWith('/')) return path.join(dist, pathname.slice(1), 'index.html');
  return path.join(dist, pathname.slice(1));
}

async function exists(filePath) {
  return access(filePath).then(() => true).catch(() => false);
}

async function main() {
  const errors = [];
  const htmlFiles = (await walk(dist)).filter((filePath) => filePath.endsWith('.html'));

  for (const filePath of htmlFiles) {
    const source = await readFile(filePath, 'utf8');
    for (const [, rawHref] of source.matchAll(/\bhref=["']([^"']+)["']/gi)) {
      if (rawHref.startsWith('#') || rawHref.startsWith('mailto:') || rawHref.startsWith('tel:')) continue;
      const url = new URL(rawHref, `${siteOrigin}/`);
      if (url.origin !== siteOrigin) continue;
      if (url.pathname.endsWith('.html')) {
        errors.push(`${path.relative(dist, filePath)} links to stale .html route ${url.pathname}`);
        continue;
      }
      const file = targetFile(url);
      if (!await exists(file)) errors.push(`${path.relative(dist, filePath)} links to missing ${url.pathname}`);
    }
  }

  if (errors.length > 0) {
    console.error(errors.map((error) => `- ${error}`).join('\n'));
    process.exitCode = 1;
    return;
  }
  console.log(`Link validation passed: scanned ${htmlFiles.length} generated pages.`);
}

main().catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});