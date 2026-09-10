import { mkdir, readdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createServer } from 'node:http';
import { createReadStream } from 'node:fs';
import { stat } from 'node:fs/promises';
import puppeteer from 'puppeteer';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const distDir = path.join(root, 'dist');
const writingDir = path.join(distDir, 'writing');
const pdfDir = path.join(distDir, 'pdfs');

const contentTypes = new Map([
    ['.html', 'text/html'],
    ['.css', 'text/css'],
    ['.js', 'application/javascript'],
    ['.svg', 'image/svg+xml'],
    ['.woff2', 'font/woff2'],
    ['.json', 'application/json'],
]);

function startStaticServer() {
    const server = createServer(async (req, res) => {
        const urlPath = decodeURIComponent(req.url.split('?')[0]);
        const filePath = path.join(distDir, urlPath.endsWith('/') ? `${urlPath}index.html` : urlPath);
        try {
            await stat(filePath);
            res.setHeader('Content-Type', contentTypes.get(path.extname(filePath)) ?? 'application/octet-stream');
            createReadStream(filePath).pipe(res);
        } catch {
            res.statusCode = 404;
            res.end('Not found');
        }
    });
    return new Promise((resolve) => {
        server.listen(0, '127.0.0.1', () => resolve({ server, port: server.address().port }));
    });
}

async function listWritingSlugs() {
    const entries = await readdir(writingDir, { withFileTypes: true }).catch(() => []);
    return entries.filter((entry) => entry.isDirectory()).map((entry) => entry.name);
}

async function main() {
    const slugs = await listWritingSlugs();
    if (slugs.length === 0) {
        console.log('pdfs: no writing pages found in dist/writing, skipping (run `npm run build` first)');
        return;
    }

    await mkdir(pdfDir, { recursive: true });
    const { server, port } = await startStaticServer();
    const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox'] });
    try {
        for (const slug of slugs) {
            const page = await browser.newPage();
            await page.emulateMediaFeatures([{ name: 'prefers-color-scheme', value: 'light' }]);
            await page.goto(`http://127.0.0.1:${port}/writing/${slug}/`, { waitUntil: 'networkidle0' });
            await page.evaluate(() => document.documentElement.setAttribute('data-theme', 'light'));
            await page.emulateMediaType('print');
            const pdf = await page.pdf({ format: 'A4', printBackground: true, margin: { top: '1in', bottom: '1in', left: '0.75in', right: '0.75in' } });
            await page.close();
            const outputPath = path.join(pdfDir, `${slug}.pdf`);
            await writeFile(outputPath, pdf);
            console.log(`pdf: dist/pdfs/${slug}.pdf`);
        }
    } finally {
        await browser.close();
        server.close();
    }
}

main().catch((error) => {
    console.error(error.message);
    process.exitCode = 1;
});
