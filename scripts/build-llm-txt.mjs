import { readdir, readFile, writeFile } from 'node:fs/promises';
import { join, relative } from 'node:path';

const root = new URL('..', import.meta.url).pathname;
const contentDir = join(root, 'src', 'content');
const outputPath = join(root, 'public', 'llm.txt');

// Only these collections represent routable pages; timeline/studio-timeline are data consumed by other pages.
const PAGE_COLLECTIONS = ['pages', 'writing', 'case-studies', 'archive', 'projects', 'research'];

const SITE_URL = 'https://kieferwaight.com';
const SOCIAL_URLS = ['https://github.com/kieferwaight', 'https://www.linkedin.com/in/kieferwaight/'];

const SECTION_ORDER = [
    'Start here',
    'Profile and resume',
    'Profile and projects',
    'Advisory',
    'Case studies',
    'Writing and research',
    'Archive and project record',
    'Other pages',
];

async function walk(dir) {
    const entries = await readdir(dir, { withFileTypes: true });
    const files = await Promise.all(entries.map(async (entry) => {
        const path = join(dir, entry.name);
        return entry.isDirectory() ? walk(path) : path;
    }));
    return files.flat();
}

function parseFrontmatter(raw) {
    const match = raw.match(/^---\n([\s\S]*?)\n---/);
    if (!match) return {};
    const meta = {};
    for (const line of match[1].split('\n')) {
        const fieldMatch = line.match(/^([A-Za-z0-9_]+):\s*(.*)$/);
        if (!fieldMatch) continue;
        const [, key, rawValue] = fieldMatch;
        meta[key] = rawValue.trim().replace(/^"(.*)"$/, '$1');
    }
    return meta;
}

function sectionFor(canonical) {
    const path = canonical.replace(SITE_URL, '') || '/';
    if (path === '/') return 'Start here';
    if (path.startsWith('/resume')) return 'Profile and resume';
    if (path.startsWith('/projects')) return 'Profile and projects';
    if (path.startsWith('/advisory')) return 'Advisory';
    if (path.startsWith('/case-studies')) return 'Case studies';
    if (path.startsWith('/writing') || path.startsWith('/research')) return 'Writing and research';
    if (path.startsWith('/archive')) return 'Archive and project record';
    return 'Other pages';
}

async function collectEntries() {
    const entries = [];
    for (const collection of PAGE_COLLECTIONS) {
        const dir = join(contentDir, collection);
        const files = (await walk(dir)).filter((path) => path.endsWith('.md'));
        for (const file of files) {
            const raw = await readFile(file, 'utf8');
            const meta = parseFrontmatter(raw);
            if (!meta.canonical || meta.draft === 'true') continue;
            entries.push({
                canonical: meta.canonical,
                title: (meta.title || meta.canonical).replace(/\s+/g, ' ').trim(),
                description: (meta.description || '').replace(/\s+/g, ' ').trim(),
                sourceUrl: meta.source_url || '',
            });
        }
    }
    return entries;
}

function buildLlmTxt(entries) {
    const grouped = new Map();
    for (const entry of entries) {
        const section = sectionFor(entry.canonical);
        if (!grouped.has(section)) grouped.set(section, []);
        grouped.get(section).push(entry);
    }

    const lines = [
        '# Kiefer Waight',
        '',
        '> Systems Architect and Fractional CTO portfolio covering applied AI, edge systems, and platform architecture.',
        '',
        "This file is generated from the site's Markdown front matter on every build.",
        'Use the page descriptions below to select relevant context before crawling deeper.',
        '',
        '## Identity',
        `- GitHub: ${SOCIAL_URLS[0]}`,
        `- LinkedIn: ${SOCIAL_URLS[1]}`,
        `- Sitemap: ${SITE_URL}/sitemap-index.xml`,
        `- Robots: ${SITE_URL}/robots.txt`,
        '',
    ];

    for (const section of SECTION_ORDER) {
        const sectionEntries = grouped.get(section);
        if (!sectionEntries || sectionEntries.length === 0) continue;
        lines.push(`## ${section}`, '');
        for (const entry of [...sectionEntries].sort((a, b) => a.canonical.localeCompare(b.canonical))) {
            lines.push(`- [${entry.title}](${entry.canonical}): ${entry.description}`);
            if (entry.sourceUrl) lines.push(`  - Source: ${entry.sourceUrl}`);
        }
        lines.push('');
    }

    return lines.join('\n').replace(/\n+$/, '\n');
}

const entries = await collectEntries();
await writeFile(outputPath, buildLlmTxt(entries));
console.log(`llm.txt: ${entries.length} pages indexed`);
