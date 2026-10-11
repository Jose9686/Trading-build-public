# Trading-build-public

A small weekly review cycle for a set of Git repositories. Once a week it pulls
every project, runs its tests, and gathers the week into a single packet, so
whoever plans next week's work starts from facts rather than memory.

```
projects.json ──▶ sunday.py collect ──▶ weeks/<date>/packet.md ──▶ plan ──▶ build ──▶ sunday.py report
```

## What goes in the packet

For every project in `projects.json`:

- the commits from the last 7 days,
- the last line of its test run (for example `Ran 212 tests ... OK`),
- the last *n* lines of any files you list, such as a TODO list or changelog.

The plan and build steps are deliberately left to you: a person, a code
reviewer, or an AI assistant can read the packet and write the plan.
`sunday.py report` then writes a template for what shipped, what was parked,
and the before/after numbers.

## Setup

```bash
# 1. list your projects
$EDITOR projects.json
# 2. run it weekly, e.g. Sundays at 00:05
5 0 * * 0  cd /path/to/Trading-build-public && python3 sunday.py collect
```

## Tests

```bash
python3 -m unittest discover -s tests -t .
```
