import { readdir, readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const dist = path.join(root, 'dist');
const imageOrigin = 'https://images.kieferwaight.com/';
const allowedWidths = [480, 768, 960, 1440];

async function walk(directory) {
    const entries = await readdir(directory, { withFileTypes: true });
    const paths = await Promise.all(entries.map(async (entry) => {
        const filePath = path.join(directory, entry.name);
        return entry.isDirectory() ? walk(filePath) : filePath;
    }));
    return paths.flat();
}

async function main() {
    const errors = [];
    const htmlFiles = (await walk(dist)).filter((filePath) => filePath.endsWith('.html'));
    const candidates = new Set();

    for (const filePath of htmlFiles) {
        const source = await readFile(filePath, 'utf8');
        for (const [, srcset] of source.matchAll(/\bsrcset=["']([^"']+)["']/gi)) {
            const entries = srcset.split(',').map((entry) => entry.trim()).filter(Boolean);
            const r2Entries = entries.filter((entry) => entry.startsWith(imageOrigin));
            if (r2Entries.length === 0) continue;
            const widths = r2Entries.map((entry) => Number(entry.match(/\s(\d+)w$/)?.[1])).sort((a, b) => a - b);
            if (widths.length < 3 || widths.some((width) => !allowedWidths.includes(width))) errors.push(`${path.relative(dist, filePath)} has insufficient or unexpected R2 widths: ${widths.join(', ')}`);
            for (const entry of r2Entries) {
                const url = entry.split(/\s+/)[0];
                if (!/-w(?:480|768|960|1440)\.webp$/.test(url)) errors.push(`${path.relative(dist, filePath)} has a nonstandard R2 candidate: ${url}`);
                candidates.add(url);
            }
        }
    }

    const localDerivatives = (await walk(path.join(dist, '_astro')).catch(() => [])).filter((filePath) => /\.(?:avif|webp)$/.test(filePath));
    if (localDerivatives.length > 0) errors.push(`dist/_astro contains ${localDerivatives.length} local image derivatives; expected R2-hosted variants`);

    if (process.argv.includes('--remote')) {
        for (const url of candidates) {
            const response = await fetch(url, { method: 'HEAD' });
            if (!response.ok) errors.push(`R2 image returned ${response.status}: ${url}`);
            if (!response.headers.get('content-type')?.startsWith('image/webp')) errors.push(`R2 image has unexpected content type: ${url}`);
        }
    }

    if (errors.length > 0) {
        console.error(errors.map((error) => `- ${error}`).join('\n'));
        process.exitCode = 1;
        return;
    }
    console.log(`Image validation passed: ${candidates.size} R2 candidates across ${htmlFiles.length} pages.`);
}

main().catch((error) => {
    console.error(error.message);
    process.exitCode = 1;
});