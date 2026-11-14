// Real CI filters that can match zero tests, each run as shard 1/2 and 2/2. Needs work/<version> from run-matrix.mjs.
import { spawnSync } from 'node:child_process';
import { writeFileSync, existsSync } from 'node:fs';
import { join, resolve } from 'node:path';

const VERSIONS = ['1.64.1', '1.65.1'];
const root = resolve(import.meta.dirname, '..');
// Each run rewrites .last-run.json, so a green full run follows every filtered run.
const TRIGGERS = {
  'grep matches nothing': ['--grep', '@pick-none'],
  'only-changed, no test file changed': ['--only-changed'],
  'last-failed after a green run': ['--last-failed'],
  'path filter matches nothing': ['no-such-dir/'],
};
const sh = (dir, cmd, args, env = {}) => spawnSync(cmd, args, { cwd: dir, env: { ...process.env, ...env }, encoding: 'utf8' });

const rows = [];
for (const version of VERSIONS) {
  const dir = join(root, 'work', version);
  if (!existsSync(join(dir, '.git'))) {
    writeFileSync(join(dir, '.gitignore'), 'node_modules\ntest-results\n*.json\n');
    sh(dir, 'git', ['init', '-q', '-b', 'main']);
    sh(dir, 'git', ['add', '-A']);
    sh(dir, 'git', ['-c', 'user.name=poc', '-c', 'user.email=poc@example.com', 'commit', '-q', '-m', 'suite']);
  }
  const green = sh(dir, 'npx', ['playwright', 'test', '--reporter=line']);
  if (green.status !== 0) throw new Error(`full run failed on ${version}`);
  for (const [trigger, args] of Object.entries(TRIGGERS)) for (const flag of [false, true]) {
    const once = (shard) => {
      const r = sh(dir, 'npx', ['playwright', 'test', ...args, ...shard, '--reporter=json', ...(flag ? ['--pass-with-no-tests'] : [])]);
      sh(dir, 'npx', ['playwright', 'test', '--reporter=line']);
      let ran = 0;
      try { const st = JSON.parse(r.stdout).stats; ran = st.expected + st.unexpected + st.flaky; } catch {}
      return { exit: r.status, ran };
    };
    const single = once([]);
    const shards = [1, 2].map((k) => once([`--shard=${k}/2`]));
    rows.push({ version, trigger, flag, unshardedExit: single.exit, failedShards: shards.filter((e) => e.exit !== 0).length, testsRun: single.ran + shards.reduce((n, e) => n + e.ran, 0) });
  }
}
writeFileSync(join(root, 'results', 'triggers.json'), JSON.stringify(rows, null, 1));
for (const r of rows) console.log([r.version, r.trigger, r.flag ? 'flag' : 'noflag', `unsharded exit ${r.unshardedExit}`, `failed shards ${r.failedShards}/2`, `tests run ${r.testsRun}`].join('\t'));
