#!/usr/bin/env python3
"""Blind-judge every reply in a run with two judges from different model families.

Usage: judge.py <run_dir>

For each scenario folder, replies are shuffled under anonymous ids (key saved to key.json), and each
judge scores all of them in one pass. Writes <scenario>/judge-<judge>.json and summary.json.
"""
import json, pathlib, random, re, subprocess, sys, concurrent.futures as cf

HERE = pathlib.Path(__file__).resolve().parent
CRITERIA = ["side_asked", "concrete", "self_contained", "honest", "usable", "economy"]

RUBRIC = """Score each reply 1-5 on each criterion. Be strict; most replies should not get 5s.
1. side_asked: a "why not X" question gets the costs of X; a "what's the benefit" question gets the benefit.
2. concrete: starts from what actually happens, not a verdict ("on purpose", "costs more than it saves", "by design"). Every reason names an observable consequence. Every bug or failure is a step-by-step sequence of real events with real names ending in what someone sees; a bare symptom ("the bar never greys out") loses points. Deduct for labels used as reasons and for truisms true of any two options ("they solve different problems").
3. self_contained: the reader can judge without opening anything. Every issue, file, type, function, incident or rule is introduced with what it is, where it sits, and who uses it. When the argument rests on code, the relevant lines are shown with file:line, and comments explain what the lines do. Relaying a source's phrasing that only makes sense after reading the code loses points.
4. honest: no claim beyond the evidence; inferred numbers are marked; unverified things are said to be unverified; admits when the earlier answer was a label or wrong and flips when the facts say so. Deduct hard for invented facts or APIs, and for consequences inflated past the facts.
5. usable: the reader can act on it and could apply the deciding rule themselves next time.
6. economy: no repetition, truisms, filler, or sections nobody asked about. Length itself is not penalised when every line carries a fact."""

JUDGE_PROMPT = """You are a blind judge of assistant replies. The user who asks these questions hates answers that justify a decision with labels or verdicts instead of saying what concretely happens, hates bare references that force them to trust the agent, and is often away from their editor, so wants to see the code an argument rests on.

{context}

{rubric}

Below are {n} candidate replies, each under an id. Judge each independently against the context. Output ONLY a JSON object, no prose, no code fence, shaped:
{{"<id>": {{"scores": {{"side_asked": n, "concrete": n, "self_contained": n, "honest": n, "usable": n, "economy": n}}, "errors": ["each factual error or unsupported claim, quoted briefly"], "note": "one sentence on the reply's biggest strength or weakness"}}, ...}}

{replies}"""

JUDGES = {
    "claude-opus": lambda p: ["claude", "-p", p, "--model", "opus", "--effort", "medium", "--no-session-persistence", "--tools", ""],
    "codex": lambda p: ["codex", "exec", "-s", "read-only", "--skip-git-repo-check", "--ephemeral", "-c", "model_reasoning_effort=medium", p],
}


def context_for(key):
    f = next((HERE / "scenarios").glob(f"{key}-*.md"))
    text = f.read_text()
    if text.startswith("# Live:"):
        truth = (HERE / "ground-truth" / f"{key}.md").read_text()
        return f"The user asked this about a real repository:\n<question>\n{text.split(chr(10), 1)[1].strip()}\n</question>\n\nVerified ground truth from the repository (the agents did not see this; they had to find it themselves):\n<ground_truth>\n{truth}\n</ground_truth>"
    return f"The agent was given these facts and this conversation, and was asked to write its next reply:\n<scenario>\n{text}\n</scenario>"


def parse_json(s):
    m = re.search(r"\{.*\}", s, re.S)
    return json.loads(m.group(0))


def judge_scenario(run, key):
    d = run / key
    replies = sorted(p for p in d.glob("*.md") if p.stat().st_size > 40)
    rng = random.Random(f"{key}-concrete-why")
    ids = [f"R{i:02d}" for i in range(1, len(replies) + 1)]
    rng.shuffle(ids)
    key_map = {rid: p.stem for rid, p in zip(ids, replies)}
    (d / "key.json").write_text(json.dumps(key_map, indent=1, sort_keys=True))
    body = "\n\n".join(f'<reply id="{rid}">\n{(d / (key_map[rid] + ".md")).read_text().strip()}\n</reply>' for rid in sorted(key_map))
    prompt = JUDGE_PROMPT.format(context=context_for(key), rubric=RUBRIC, n=len(key_map), replies=body)
    results = {}
    for name, cmd in JUDGES.items():
        out = d / f"judge-{name}.json"
        if out.exists():
            results[name] = json.loads(out.read_text())
            continue
        for attempt in range(3):
            r = subprocess.run(cmd(prompt), cwd=d, capture_output=True, text=True, timeout=1800, stdin=subprocess.DEVNULL)
            try:
                parsed = parse_json(r.stdout)
                break
            except Exception:
                (d / f"judge-{name}.raw").write_text(r.stdout + "\n---\n" + r.stderr[-3000:])
        else:
            print(key, name, "FAILED", flush=True)
            continue
        out.write_text(json.dumps(parsed, indent=1))
        results[name] = parsed
        print(key, name, "ok", flush=True)
    return key, key_map, results


def main():
    run = pathlib.Path(sys.argv[1]).resolve()
    keys = sorted(p.name for p in run.iterdir() if p.is_dir())
    summary = {}
    with cf.ThreadPoolExecutor(len(keys)) as ex:
        for key, key_map, results in ex.map(lambda k: judge_scenario(run, k), keys):
            for rid, stem in key_map.items():
                lane, arm = stem.rsplit("-", 1)
                for jname, res in results.items():
                    row = res.get(rid)
                    if not row:
                        continue
                    summary.setdefault(key, {}).setdefault(lane, {}).setdefault(arm, {})[jname] = {
                        "total": sum(int(row["scores"][c]) for c in CRITERIA),
                        "scores": [int(row["scores"][c]) for c in CRITERIA],
                        "errors": row.get("errors", []),
                        "note": row.get("note", ""),
                    }
    (run / "summary.json").write_text(json.dumps(summary, indent=1, sort_keys=True))
    print("wrote", run / "summary.json")


if __name__ == "__main__":
    main()
