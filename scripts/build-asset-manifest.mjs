import { mkdir, readdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const contentDir = path.join(root, 'src', 'content');
const diagramsDir = path.join(root, 'src', 'diagrams');
const publicDiagramsDir = path.join(root, 'public', 'diagrams');
const outputPath = path.join(root, 'public', 'assets-manifest.json');
const dataOutputPath = path.join(root, 'src', 'data', 'assets-manifest.json');
const imageOrigin = 'https://images.kieferwaight.com/';

async function walk(dir) {
    const entries = await readdir(dir, { withFileTypes: true }).catch(() => []);
    const paths = await Promise.all(entries.map(async (entry) => {
        const filePath = path.join(dir, entry.name);
        return entry.isDirectory() ? walk(filePath) : filePath;
    }));
    return paths.flat();
}

function stripQuery(url) {
    return url.split('?')[0];
}

async function collectReferences() {
    const contentFiles = (await walk(contentDir)).filter((filePath) => filePath.endsWith('.md'));
    const diagramRefs = new Map();
    const imageRefs = new Map();

    for (const filePath of contentFiles) {
        const raw = await readFile(filePath, 'utf8');
        const relativeContentPath = path.relative(root, filePath);

        for (const [, src] of raw.matchAll(/\/diagrams\/([\w.-]+\.svg)/g)) {
            if (!diagramRefs.has(src)) diagramRefs.set(src, new Set());
            diagramRefs.get(src).add(relativeContentPath);
        }

        for (const [, src] of raw.matchAll(/https:\/\/images\.kieferwaight\.com\/([^\s")]+)/g)) {
            const key = stripQuery(src);
            if (!imageRefs.has(key)) imageRefs.set(key, new Set());
            imageRefs.get(key).add(relativeContentPath);
        }
    }

    return { diagramRefs, imageRefs };
}

async function buildDiagramEntries(diagramRefs) {
    const svgFiles = (await walk(publicDiagramsDir)).filter((filePath) => filePath.endsWith('.svg'));
    const svgNames = new Set(svgFiles.map((filePath) => path.relative(publicDiagramsDir, filePath)));
    const referencedNames = new Set(diagramRefs.keys());
    const allNames = new Set([...svgNames, ...referencedNames]);

    return [...allNames].sort().map((name) => ({
        id: name,
        svgPath: `/diagrams/${name}`,
        existsOnDisk: svgNames.has(name),
        referencedBy: [...(diagramRefs.get(name) ?? [])].sort(),
    }));
}

function buildImageEntries(imageRefs) {
    return [...imageRefs.keys()].sort().map((key) => ({
        id: key,
        url: `${imageOrigin}${key}`,
        referencedBy: [...imageRefs.get(key)].sort(),
    }));
}

async function main() {
    const { diagramRefs, imageRefs } = await collectReferences();
    const diagrams = await buildDiagramEntries(diagramRefs);
    const images = buildImageEntries(imageRefs);

    const manifest = {
        generatedAt: new Date().toISOString(),
        diagrams,
        images,
        summary: {
            diagramCount: diagrams.length,
            diagramsMissingOnDisk: diagrams.filter((entry) => !entry.existsOnDisk).length,
            diagramsUnreferenced: diagrams.filter((entry) => entry.referencedBy.length === 0).length,
            imageCount: images.length,
        },
    };

    await writeFile(outputPath, JSON.stringify(manifest, null, 2) + '\n');
    await mkdir(path.dirname(dataOutputPath), { recursive: true });
    await writeFile(dataOutputPath, JSON.stringify(manifest, null, 2) + '\n');
    console.log(`asset manifest: ${diagrams.length} diagrams, ${images.length} images -> ${path.relative(root, outputPath)}`);
}

main();
