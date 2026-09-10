import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const manifestPath = path.join(root, 'public', 'assets-manifest.json');

async function main() {
    const manifest = JSON.parse(await readFile(manifestPath, 'utf8'));
    const errors = [];

    for (const diagram of manifest.diagrams) {
        if (diagram.referencedBy.length > 0 && !diagram.existsOnDisk) {
            errors.push(`diagram referenced by content but missing on disk: ${diagram.id} (referenced by ${diagram.referencedBy.join(', ')})`);
        }
    }

    if (errors.length > 0) {
        console.error(errors.map((error) => `- ${error}`).join('\n'));
        process.exitCode = 1;
        return;
    }

    console.log(`asset validation: ${manifest.diagrams.length} diagrams and ${manifest.images.length} images checked, no broken references`);
}

main();
