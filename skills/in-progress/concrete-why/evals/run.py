#!/usr/bin/env python3
"""Run every scenario through every agent lane, with and without the skill.

Usage: run.py <out_dir> [--lanes a,b] [--scenarios s1,s2] [--jobs N]

Writes <out_dir>/<scenario>/<lane>-<arm>.md (the reply) and .err (stderr).
Existing non-empty replies are kept, so a rerun only fills gaps.
"""
import argparse, concurrent.futures as cf, pathlib, subprocess, sys, time

HERE = pathlib.Path(__file__).resolve().parent
SKILL = (HERE.parent / "SKILL.md").read_text()
NRO = pathlib.Path.home() / "dev" / "NRO"

# Every lane runs at medium reasoning effort so lanes differ by model and harness, not effort.
LANES = {
    "claude-opus":   lambda p, cwd, out: (["claude", "-p", p, "--model", "opus", "--effort", "medium", "--no-session-persistence", "--tools", "Read,Grep,Glob"], None),
    "claude-sonnet": lambda p, cwd, out: (["claude", "-p", p, "--model", "sonnet", "--effort", "medium", "--no-session-persistence", "--tools", "Read,Grep,Glob"], None),
    "codex":         lambda p, cwd, out: (["codex", "exec", "-s", "read-only", "--skip-git-repo-check", "--ephemeral", "-c", "model_reasoning_effort=medium", "-C", str(cwd), "-o", str(out), p], out),
    "muse":          lambda p, cwd, out: (["muse", "exec", "--reasoning-effort", "medium", "--workspace", str(cwd), p], None),
    "pi":            lambda p, cwd, out: (["pi", "-p", "--no-session", "--thinking", "medium", "--tools", "read,grep,find,ls", p], None),
    "gemini":        lambda p, cwd, out: (["pi", "-p", "--no-session", "--model", "google/gemini-3.7-flash", "--thinking", "medium", "--tools", "read,grep,find,ls", p], None),
}

FIXTURE_PROMPT = """You are the assistant in the conversation below. Every fact listed was verified by you earlier in this session. Do not run commands or open files. Write your next reply to the user exactly as you would send it, and output only that reply.

<scenario>
{scenario}
</scenario>"""

LIVE_PROMPT = """You are working in the repository in the current directory. This is read-only: do not modify any file, run builds or tests, or use the network. Investigate the repository as much as you need, then answer the user. Output only your reply to the user.

The user asks:
{question}"""

SKILL_PREFIX = "Follow this skill when writing your reply.\n\n<skill>\n{skill}\n</skill>\n\n"


def scenarios():
    out = {}
    for f in sorted((HERE / "scenarios").glob("*.md")):
        text = f.read_text()
        key = f.stem.split("-")[0]
        if text.startswith("# Live:"):
            # Live scenarios: first line names the repo, the rest is the user's question.
            repo_line, question = text.split("\n", 1)
            repo = pathlib.Path(repo_line.split(":", 1)[1].strip()).expanduser()
            out[key] = (LIVE_PROMPT.format(question=question.strip()), repo)
        else:
            out[key] = (FIXTURE_PROMPT.format(scenario=text), None)
    return out


def run_one(lane, key, arm, prompt, cwd, out_dir):
    dest = out_dir / key / f"{lane}-{arm}.md"
    if dest.exists() and dest.stat().st_size > 40:
        return lane, key, arm, "kept"
    dest.parent.mkdir(parents=True, exist_ok=True)
    # Fixture scenarios run from the output folder so no repository instructions load.
    cwd = cwd or dest.parent
    full = (SKILL_PREFIX.format(skill=SKILL) if arm == "skill" else "") + prompt
    for attempt in range(3):
        cmd, file_out = LANES[lane](full, cwd, dest)
        t = time.time()
        try:
            r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=1200, stdin=subprocess.DEVNULL)
            stdout, stderr, code = r.stdout, r.stderr, r.returncode
        except subprocess.TimeoutExpired:
            stdout, stderr, code = "", "timeout", -1
        (dest.with_suffix(".err")).write_text(f"exit {code} after {time.time()-t:.0f}s\n{stderr[-4000:]}")
        if file_out is None:
            dest.write_text(stdout.strip() + "\n")
        if code == 0 and dest.exists() and dest.stat().st_size > 40:
            return lane, key, arm, f"ok ({attempt + 1})"
        time.sleep(30 * (attempt + 1))
    return lane, key, arm, f"FAILED exit {code}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("--lanes", default=",".join(LANES))
    ap.add_argument("--scenarios", default="")
    ap.add_argument("--jobs", type=int, default=8)
    a = ap.parse_args()
    out_dir = pathlib.Path(a.out_dir).resolve()
    sc = scenarios()
    keys = a.scenarios.split(",") if a.scenarios else list(sc)
    jobs = [(l, k, arm, *sc[k], out_dir) for k in keys for l in a.lanes.split(",") for arm in ("baseline", "skill")]
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        for res in ex.map(lambda j: run_one(*j), jobs):
            print(*res, flush=True)


if __name__ == "__main__":
    sys.exit(main())
