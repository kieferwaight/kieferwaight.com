import { mkdir, readdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import puppeteer from 'puppeteer';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const distDir = path.join(root, 'dist');
const writingDir = path.join(distDir, 'writing');
const pdfDir = path.join(distDir, 'pdfs');

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
    const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox'] });
    try {
        for (const slug of slugs) {
            const htmlPath = path.join(writingDir, slug, 'index.html');
            const page = await browser.newPage();
            await page.goto(pathToFileURL(htmlPath).toString(), { waitUntil: 'networkidle0' });
            const pdf = await page.pdf({ format: 'A4', printBackground: true, margin: { top: '1in', bottom: '1in', left: '0.75in', right: '0.75in' } });
            await page.close();
            const outputPath = path.join(pdfDir, `${slug}.pdf`);
            await writeFile(outputPath, pdf);
            console.log(`pdf: dist/pdfs/${slug}.pdf`);
        }
    } finally {
        await browser.close();
    }
}

main().catch((error) => {
    console.error(error.message);
    process.exitCode = 1;
});
