#!/usr/bin/env python3
"""sunday.py — a weekly review cycle for a set of Git projects.

    python3 sunday.py collect     # weeks/<date>/packet.md: per project, this week's commits, test result, chosen files
    python3 sunday.py report      # weeks/<date>/REPORT.md: a template for what shipped, what was parked, and why

Run it on a schedule (cron, a CI job, a cloud routine). The packet is one file that a reviewer, human
or otherwise, reads to plan next week's fixes and improvements. Nothing here needs a secret.
"""
import argparse, datetime, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.join(HERE, "projects")


def week_dir(today=None):
    return os.path.join(HERE, "weeks", (today or datetime.date.today()).isoformat())


def sh(cmd, cwd=None, timeout=1800):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return p.returncode, (p.stdout + p.stderr)


def sync(pr):
    """Clone the project on first use, then fast-forward its branch."""
    d = os.path.join(PROJ, pr["name"])
    os.makedirs(PROJ, exist_ok=True)
    if not os.path.isdir(d):
        sh(["git", "clone", "-q", "--branch", pr["branch"], pr["url"], d])
    else:
        sh(["git", "-C", d, "fetch", "-q", "origin"])
        sh(["git", "-C", d, "checkout", "-q", pr["branch"]])
        sh(["git", "-C", d, "merge", "-q", "--ff-only", f"origin/{pr['branch']}"])
    return d


def section(pr, d):
    """One project's part of the packet."""
    _, log = sh(["git", "-C", d, "log", "--since=7 days ago", "--format=%h %ad %s", "--date=short"])
    commits = [l for l in log.splitlines() if l.strip()]
    if pr.get("test"):
        _, t = sh(pr["test"].split(), cwd=d)
        test_line = (t.strip().splitlines() or ["no output"])[-1][:120]
    else:
        test_line = "no test command configured"
    lines = [f"## {pr['name']} ({pr['branch']})", f"- commits this week: {len(commits)}",
             *[f"    {c[:110]}" for c in commits[:60]], f"- tests: {test_line}", ""]
    for rel, n in pr.get("files", {}).items():   # e.g. {"TODO.md": 40}: the last n lines of each listed file
        f = os.path.join(d, rel)
        if os.path.exists(f):
            tail = open(f, errors="replace").read().splitlines()[-n:]
            lines += [f"### {rel} (last {n} lines)", "```", *tail, "```", ""]
    return lines


def collect():
    w = week_dir(); os.makedirs(w, exist_ok=True)
    lines = [f"# Week packet — {os.path.basename(w)}", ""]
    for pr in json.load(open(os.path.join(HERE, "projects.json"))):
        lines += section(pr, sync(pr))
    out = os.path.join(w, "packet.md")
    open(out, "w").write("\n".join(lines) + "\n")
    print(f"packet: {out} ({os.path.getsize(out) // 1024} KB)")
    return 0


def report():
    w = week_dir(); os.makedirs(w, exist_ok=True)
    files = sorted(os.listdir(w))
    open(os.path.join(w, "REPORT.md"), "w").write(
        f"# Week report — {os.path.basename(w)}\n\nArtifacts: {', '.join(files)}\n\n"
        "## Shipped\n\n## Parked (and why)\n\n## Numbers before / after\n\n## Carry-over\n")
    print(f"-> {w}/REPORT.md")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["collect", "report"])
    sys.exit({"collect": collect, "report": report}[ap.parse_args().step]())
