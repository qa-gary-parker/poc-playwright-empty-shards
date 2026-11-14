# poc-playwright-empty-shards

Measures what Playwright 1.65 changed for sharded runs that match no tests.

## TLDR

- A filter that matches 0 tests: every shard passes on 1.64.1 and every shard fails on 1.65.1 with `Error: No tests found`.
- `--pass-with-no-tests` makes every shard pass again.
- An empty shard still passes on both versions when at least one other shard has a test.
- `--last-failed` after a green run and `--only-changed` with no changed test file still pass when sharded on 1.65.1.
- `playwright-shard-balancer` 0.1.3 in the config does not change any exit code.

## Method

- Suite: 32 spec files, one test each, no browser. `fullyParallel: true`, `workers: 1`.
- Versions: `@playwright/test` 1.64.1 and 1.65.1. Node 24.14.1, macOS.
- `scripts/run-matrix.mjs`: 0, 1, 2, 4, 8 and 16 selected tests (by tag), 2, 4, 8 and 16 shards, with and without `--pass-with-no-tests`, with Playwright's split and with `playwright-shard-balancer`. Every shard is its own process, as in a CI matrix. 1,464 runs.
- `scripts/run-triggers.mjs`: four filters that match no tests, unsharded and as shards 1/2 and 2/2.

## Results

Selection of 0 tests, failed shards out of all shards (`results/jobs.json`):

| Version | `--pass-with-no-tests` | Unsharded | 2 shards | 4 shards | 8 shards | 16 shards |
|---|---|---|---|---|---|---|
| 1.64.1 | no | 1/1 | 0/2 | 0/4 | 0/8 | 0/16 |
| 1.64.1 | yes | 0/1 | 0/2 | 0/4 | 0/8 | 0/16 |
| 1.65.1 | no | 1/1 | 2/2 | 4/4 | 8/8 | 16/16 |
| 1.65.1 | yes | 0/1 | 0/2 | 0/4 | 0/8 | 0/16 |

The rows are the same with `playwright-shard-balancer` in the config.

Selection of 1 to 16 tests: 0 failed shards in all 180 jobs, on both versions. Up to 15 of 16 shards were empty.

Filters that match no tests, without `--pass-with-no-tests` (`results/triggers.json`):

| Filter | 1.64.1 unsharded | 1.64.1 failed shards | 1.65.1 unsharded | 1.65.1 failed shards |
|---|---|---|---|---|
| `--grep` matches nothing | exit 1 | 0/2 | exit 1 | 2/2 |
| Path filter matches nothing | exit 1 | 0/2 | exit 1 | 2/2 |
| `--last-failed` after a green run | exit 1 | 0/2 | exit 1 | 0/2 |
| `--only-changed`, no test file changed | exit 0 | 0/2 | exit 0 | 0/2 |

With `--pass-with-no-tests`, every cell is exit 0.

## Run it

```sh
node scripts/run-matrix.mjs    # installs both versions into work/
node scripts/run-triggers.mjs  # needs work/ from the matrix
```
