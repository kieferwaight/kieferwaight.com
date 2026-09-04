import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
execFileSync('git', ['config', 'core.hooksPath', path.join(root, '.githooks')], { stdio: 'inherit' });
console.log('Git hooks installed from .githooks.');