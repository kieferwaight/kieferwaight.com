import { mkdir, readdir } from 'node:fs/promises';
import { join, relative } from 'node:path';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';

const execFileAsync = promisify(execFile);
const root = new URL('..', import.meta.url).pathname;
const sourceDir = join(root, 'src', 'diagrams');
const outputDir = join(root, 'public', 'diagrams');

async function walk(dir) {
  const entries = await readdir(dir, { withFileTypes: true });
  return (await Promise.all(entries.map(async (entry) => {
    const path = join(dir, entry.name);
    return entry.isDirectory() ? walk(path) : path;
  }))).flat();
}

await mkdir(outputDir, { recursive: true });
const sources = (await walk(sourceDir)).filter((path) => path.endsWith('.mmd'));
for (const source of sources) {
  const output = join(outputDir, relative(sourceDir, source).replace(/\.mmd$/, '.svg'));
  await mkdir(new URL('.', `file://${output}`).pathname, { recursive: true }).catch(() => {});
  await execFileAsync('mmdc', ['-i', source, '-o', output, '-b', '#0b1120', '-t', 'dark', '-p', join(root, 'scripts', 'puppeteer.config.json')], { cwd: root });
  console.log(`diagram: ${relative(root, output)}`);
}
