import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const fontsDir = path.join(root, 'public', 'fonts');
const cssOutputPath = path.join(fontsDir, 'fonts.css');

const GOOGLE_FONTS_CSS_URL = 'https://fonts.googleapis.com/css2?family=Inter:wght@100..900&family=DM+Mono:wght@400;500&family=Source+Serif+4:opsz,wght@8..60,400;8..60,500;8..60,600&display=swap';
// Google serves different font formats based on User-Agent; a modern browser UA is required to get woff2.
const BROWSER_USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36';

async function fileExists(filePath) {
    return readFile(filePath).then(() => true).catch(() => false);
}

async function downloadFont(url) {
    const hash = createHash('sha256').update(url).digest('hex').slice(0, 16);
    const fileName = `${hash}.woff2`;
    const filePath = path.join(fontsDir, fileName);
    if (!(await fileExists(filePath))) {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`Failed to download font ${url}: ${response.status}`);
        await writeFile(filePath, Buffer.from(await response.arrayBuffer()));
        console.log(`font: downloaded ${fileName}`);
    }
    return fileName;
}

async function main() {
    await mkdir(fontsDir, { recursive: true });

    if (await fileExists(cssOutputPath)) {
        console.log('fonts: fonts.css already present, skipping fetch');
        return;
    }

    const response = await fetch(GOOGLE_FONTS_CSS_URL, { headers: { 'User-Agent': BROWSER_USER_AGENT } });
    if (!response.ok) throw new Error(`Failed to fetch Google Fonts CSS: ${response.status}`);
    const css = await response.text();

    const urls = [...css.matchAll(/url\((https:\/\/fonts\.gstatic\.com\/[^)]+)\)/g)].map(([, url]) => url);
    const rewritten = new Map();
    for (const url of urls) {
        rewritten.set(url, await downloadFont(url));
    }

    const localCss = css.replace(/url\((https:\/\/fonts\.gstatic\.com\/[^)]+)\)/g, (match, url) => `url(/fonts/${rewritten.get(url)})`);
    await writeFile(cssOutputPath, localCss);
    console.log(`fonts: wrote ${cssOutputPath} referencing ${rewritten.size} self-hosted font files`);
}

main().catch((error) => {
    console.error(error.message);
    process.exitCode = 1;
});
