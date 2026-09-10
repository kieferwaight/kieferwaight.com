import { mkdir, readdir, readFile, writeFile } from 'node:fs/promises';
import { join, relative } from 'node:path';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { createHash } from 'node:crypto';

const execFileAsync = promisify(execFile);
const root = new URL('..', import.meta.url).pathname;
const sourceDir = join(root, 'src', 'diagrams');
const outputDir = join(root, 'public', 'diagrams');
const manifestPath = join(sourceDir, '.manifest.json');

async function walk(dir) {
  const entries = await readdir(dir, { withFileTypes: true });
  return (await Promise.all(entries.map(async (entry) => {
    const path = join(dir, entry.name);
    return entry.isDirectory() ? walk(path) : path;
  }))).flat();
}

async function readManifest() {
  return JSON.parse(await readFile(manifestPath, 'utf8').catch(() => '{}'));
}

async function outputExists(output) {
  return readFile(output).then(() => true).catch(() => false);
}

await mkdir(outputDir, { recursive: true });
const manifest = await readManifest();
const sources = (await walk(sourceDir)).filter((path) => path.endsWith('.mmd'));
let built = 0;
for (const source of sources) {
  const relativeSource = relative(sourceDir, source);
  const output = join(outputDir, relativeSource.replace(/\.mmd$/, '.svg'));
  const hash = createHash('sha256').update(await readFile(source)).digest('hex');
  if (manifest[relativeSource] === hash && await outputExists(output)) continue;
  await mkdir(new URL('.', `file://${output}`).pathname, { recursive: true }).catch(() => {});
  await execFileAsync('mmdc', ['-i', source, '-o', output, '-b', '#0b1120', '-t', 'dark', '-p', join(root, 'scripts', 'puppeteer.config.json')], { cwd: root });
  manifest[relativeSource] = hash;
  built += 1;
  console.log(`diagram: ${relative(root, output)}`);
}
await writeFile(manifestPath, JSON.stringify(manifest, null, 2) + '\n');
console.log(`diagrams: ${built} rebuilt, ${sources.length - built} unchanged`);

