import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { join, relative } from 'node:path';

const root = new URL('..', import.meta.url).pathname;
const contentRoot = join(root, 'src', 'content');
const diagramRoot = join(root, 'src', 'diagrams');

async function walk(dir) {
  const entries = await (await import('node:fs/promises')).readdir(dir, { withFileTypes: true });
  return (await Promise.all(entries.map(async (entry) => {
    const path = join(dir, entry.name);
    return entry.isDirectory() ? walk(path) : path;
  }))).flat();
}

const files = (await walk(contentRoot)).filter((path) => path.endsWith('.md'));
for (const file of files) {
  let markdown = await readFile(file, 'utf8');
  let index = 0;
  markdown = markdown.replace(/```mermaid\n([\s\S]*?)\n```/g, (_, source) => {
    index += 1;
    const base = relative(contentRoot, file).replace(/[^a-z0-9]+/gi, '-').replace(/^-|-$/g, '').toLowerCase();
    const name = `${base}-${String(index).padStart(2, '0')}`;
    const sourcePath = join(diagramRoot, `${name}.mmd`);
    const publicPath = `/diagrams/${name}.svg`;
    const alt = `${name.replace(/-/g, ' ')} architecture diagram`;
    return `<figure class="diagram-figure"><img src="${publicPath}" alt="${alt}" loading="lazy" decoding="async" /></figure>`;
  });
  if (index) {
    await mkdir(diagramRoot, { recursive: true });
    let sourceIndex = 0;
    const matches = [...(await readFile(file, 'utf8')).matchAll(/```mermaid\n([\s\S]*?)\n```/g)];
    for (const match of matches) {
      sourceIndex += 1;
      const base = relative(contentRoot, file).replace(/[^a-z0-9]+/gi, '-').replace(/^-|-$/g, '').toLowerCase();
      await writeFile(join(diagramRoot, `${base}-${String(sourceIndex).padStart(2, '0')}.mmd`), match[1].trim() + '\n');
    }
    await writeFile(file, markdown);
  }
}
