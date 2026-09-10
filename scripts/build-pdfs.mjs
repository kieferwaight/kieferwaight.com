import { mkdir, readdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createServer } from 'node:http';
import { createReadStream } from 'node:fs';
import { stat } from 'node:fs/promises';
import puppeteer from 'puppeteer';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const distDir = path.join(root, 'dist');
const pdfDir = path.join(distDir, 'pdfs');
const HEADLINE = 'SYSTEMS ARCHITECT &amp; FRACTIONAL CTO';

// Each section's dist directory is walked recursively for index.html files;
// skipRootIndex excludes the section's own top-level listing page (not a real article).
const SECTIONS = [
    { urlBase: 'writing', distSubdir: 'writing', skipRootIndex: true },
    { urlBase: 'case-studies', distSubdir: 'case-studies', skipRootIndex: true },
    { urlBase: 'research', distSubdir: 'research', skipRootIndex: false },
];

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

async function listIndexFiles(dir) {
    const entries = await readdir(dir, { withFileTypes: true }).catch(() => []);
    const results = [];
    for (const entry of entries) {
        const entryPath = path.join(dir, entry.name);
        if (entry.isDirectory()) {
            results.push(...(await listIndexFiles(entryPath)));
        } else if (entry.name === 'index.html') {
            results.push(entryPath);
        }
    }
    return results;
}

async function collectPages() {
    const pages = [];
    for (const section of SECTIONS) {
        const sectionDir = path.join(distDir, section.distSubdir);
        const indexFiles = await listIndexFiles(sectionDir);
        for (const indexFile of indexFiles) {
            const relativeDir = path.relative(sectionDir, path.dirname(indexFile));
            if (section.skipRootIndex && relativeDir === '') continue;
            const urlPath = relativeDir === '' ? `${section.urlBase}/` : `${section.urlBase}/${relativeDir}/`;
            const slug = relativeDir === '' ? section.urlBase : `${section.urlBase}-${relativeDir.split(path.sep).join('-')}`;
            pages.push({ urlPath, slug });
        }
    }
    return pages;
}

async function main() {
    const pages = await collectPages();
    if (pages.length === 0) {
        console.log('pdfs: no pages found in dist/, skipping (run `npm run build` first)');
        return;
    }

    await mkdir(pdfDir, { recursive: true });
    const { server, port } = await startStaticServer();
    const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox'] });
    try {
        for (const { urlPath, slug } of pages) {
            const page = await browser.newPage();
            await page.setViewport({ width: 1240, height: 1754 });
            await page.emulateMediaFeatures([{ name: 'prefers-color-scheme', value: 'light' }]);
            await page.goto(`http://127.0.0.1:${port}/${urlPath}`, { waitUntil: 'networkidle0' });
            await page.evaluate(() => document.documentElement.setAttribute('data-theme', 'light'));
            await page.emulateMediaType('print');
            const pdf = await page.pdf({
                format: 'A4',
                printBackground: true,
                margin: { top: '0.6in', bottom: '0.6in', left: '0.5in', right: '0.5in' },
                displayHeaderFooter: true,
                headerTemplate: `<div style="width:100%;font-family:'Helvetica Neue',Arial,sans-serif;font-weight:800;font-size:9px;letter-spacing:-.03em;text-transform:uppercase;text-align:center;padding-top:6px;color:#0f172a;">KIEFER <span style="color:#68a0ff;">WAIGHT</span> <span style="font-weight:500;letter-spacing:.06em;color:#64748b;margin-left:6px;">| ${HEADLINE}</span></div>`,
                footerTemplate: '<div style="width:100%;font-size:8px;color:#94a3b8;text-align:center;padding-bottom:6px;"><span class="pageNumber"></span> / <span class="totalPages"></span></div>',
            });
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
