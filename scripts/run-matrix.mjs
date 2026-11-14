// Runs every (version, arm, selection size, shard count, flag) cell and records each shard's exit code.
import { execFile, execFileSync } from 'node:child_process';
import { mkdirSync, writeFileSync, readFileSync, existsSync, rmSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { tmpdir } from 'node:os';

const VERSIONS = ['1.64.1', '1.65.1'];
const BALANCER = '0.1.3';
const SELECTED = [0, 1, 2, 4, 8, 16];
const SHARDS = [2, 4, 8, 16];
const ARMS = ['builtin', 'balancer'];
const FILES = 32;
const CONCURRENCY = 8;
const root = resolve(import.meta.dirname, '..');
// Zero-padded so @pick01 is not a substring of @pick16.
const tag = (k) => `@pick${String(k).padStart(2, '0')}`;

const config = `import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir: 'tests',
  fullyParallel: true,
  workers: 1,
  reporter: process.env.ARM === 'balancer'
    ? [['json'], ['playwright-shard-balancer', { timings: 'shard-timings.json' }]]
    : [['json']],
});
`;

// Test i carries tag(K) for every K > i, so --grep tag(K) selects exactly K tests, one per file.
const spec = (i) => {
  const tags = SELECTED.filter((k) => k > i).map((k) => `'${tag(k)}'`).join(', ');
  return `import { test, expect } from '@playwright/test';
test('case ${i}', { tag: [${tags}] }, async () => {
  expect(${i} + 1).toBe(${i + 1});
});
`;
};

function setup(version) {
  const dir = join(root, 'work', version);
  rmSync(dir, { recursive: true, force: true });
  mkdirSync(join(dir, 'tests'), { recursive: true });
  writeFileSync(join(dir, 'package.json'), JSON.stringify({ name: `w${version}`, private: true }));
  writeFileSync(join(dir, 'playwright.config.ts'), config);
  for (let i = 0; i < FILES; i++) writeFileSync(join(dir, 'tests', `case-${String(i).padStart(2, '0')}.spec.ts`), spec(i));
  execFileSync('npm', ['i', '--silent', '--no-audit', '--no-fund', `@playwright/test@${version}`, `playwright-shard-balancer@${BALANCER}`], { cwd: dir, stdio: 'inherit' });
  const report = join(dir, 'full.json');
  execFileSync('npx', ['playwright', 'test'], { cwd: dir, env: { ...process.env, PLAYWRIGHT_JSON_OUTPUT_NAME: report }, stdio: 'ignore' });
  execFileSync('npx', ['playwright-shard-balancer', 'update', '--timings', 'shard-timings.json', 'full.json'], { cwd: dir, stdio: 'inherit' });
  return dir;
}

function run(dir, cell) {
  const out = join(tmpdir(), `empty-shards-${process.pid}-${cell.id}.json`);
  const args = ['playwright', 'test', '--grep', cell.selected ? tag(cell.selected) : '@pick-none', '--output', `${out}.d`];
  if (cell.shard) args.push(`--shard=${cell.shard}/${cell.shards}`);
  if (cell.flag) args.push('--pass-with-no-tests');
  return new Promise((done) => {
    execFile('npx', args, { cwd: dir, env: { ...process.env, ARM: cell.arm, PLAYWRIGHT_JSON_OUTPUT_NAME: out } }, (err, stdout, stderr) => {
      let ran = null;
      if (existsSync(out)) {
        const s = JSON.parse(readFileSync(out, 'utf8')).stats;
        ran = s.expected + s.unexpected + s.flaky;
        rmSync(out);
      }
      const text = stdout + stderr;
      rmSync(`${out}.d`, { recursive: true, force: true });
      done({ ...cell, exit: err ? err.code : 0, ran, noTestsFound: /No tests found/i.test(text), ...(err && !/No tests found/i.test(text) ? { output: text.slice(-600) } : {}) });
    });
  });
}

const results = [];
for (const version of VERSIONS) {
  const dir = setup(version);
  const cells = [];
  let id = 0;
  for (const arm of ARMS) for (const selected of SELECTED) for (const flag of [false, true]) {
    if (arm === 'builtin') cells.push({ id: id++, version, arm, selected, shards: 1, shard: 0, flag });
    for (const shards of SHARDS) for (let shard = 1; shard <= shards; shard++) cells.push({ id: id++, version, arm, selected, shards, shard, flag });
  }
  let next = 0;
  await Promise.all(Array.from({ length: CONCURRENCY }, async () => {
    while (next < cells.length) results.push(await run(dir, cells[next++]));
  }));
  console.log(`${version}: ${cells.length} runs`);
}
results.sort((a, b) => a.version.localeCompare(b.version) || a.id - b.id);
mkdirSync(join(root, 'results'), { recursive: true });
writeFileSync(join(root, 'results', 'raw.json'), JSON.stringify(results, null, 1));

// One row per job (a job = all shards of one cell).
const jobs = new Map();
for (const r of results) {
  const key = [r.version, r.arm, r.selected, r.shards, r.flag].join('|');
  const j = jobs.get(key) ?? { version: r.version, arm: r.arm, selected: r.selected, shards: r.shards, flag: r.flag, empty: 0, failed: 0, noTestsFound: 0, ran: 0 };
  if (!r.ran) j.empty++;
  if (r.exit !== 0) j.failed++;
  if (r.noTestsFound) j.noTestsFound++;
  j.ran += r.ran ?? 0;
  jobs.set(key, j);
}
const rows = [...jobs.values()];
writeFileSync(join(root, 'results', 'jobs.json'), JSON.stringify(rows, null, 1));
const md = ['| version | arm | selected | shards | --pass-with-no-tests | empty shards | failed shards | tests run |', '|---|---|---|---|---|---|---|---|',
  ...rows.map((j) => `| ${j.version} | ${j.arm} | ${j.selected} | ${j.shards} | ${j.flag ? 'yes' : 'no'} | ${j.empty} | ${j.failed} | ${j.ran} |`)].join('\n');
writeFileSync(join(root, 'results', 'jobs.md'), md + '\n');
console.log(`wrote ${results.length} runs, ${rows.length} jobs`);
