#!/usr/bin/env python3
"""Render a run's replies and judge scores into one self-contained HTML page.

Usage: build_page.py <run_dir> <out.html>
"""
import json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
LANE_NAMES = {
    "claude-opus": "Claude Opus 5.5 · medium",
    "claude-sonnet": "Claude Sonnet 5.5 · medium",
    "codex": "Codex · gpt-6.1-sol · medium",
    "muse": "Muse · default model · medium",
    "pi": "Pi · mimo-v2.6-pro · medium",
}
TITLES = {
    "s1": ("Feature flag cleanup", "why not just delete it tho whats actually the downside"),
    "s2": ("Zod vs hand-written validation", "why not just write the validation myself its 3 fields, zod is overkill for this"),
    "s3": ("Migrations on boot vs a Job", "whats the actual benefit tho it works fine now"),
    "s4": ("Closing old issues", "thats not an answer, im asking why not leave them open. what does closing actualy do"),
    "s5": ("NRO: why mutations return their change", None),
}


def main():
    run, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    summary = json.loads((run / "summary.json").read_text())
    data = {"lanes": LANE_NAMES, "scenarios": {}}
    for key in sorted(summary):
        f = next((HERE / "scenarios").glob(f"{key}-*.md"))
        text = f.read_text()
        live = text.startswith("# Live:")
        title, ask = TITLES[key]
        sc = {"title": title, "live": live, "ask": ask or text.split("\n", 1)[1].strip(), "context": "" if live else text,
              "truth": (HERE / "ground-truth" / f"{key}.md").read_text() if live else "", "lanes": {}}
        for lane in LANE_NAMES:
            if lane not in summary[key]:
                continue
            sc["lanes"][lane] = {arm: {"reply": (run / key / f"{lane}-{arm}.md").read_text(), "judges": summary[key][lane].get(arm, {})}
                                 for arm in ("skill", "baseline")}
        data["scenarios"][key] = sc
    tpl = (HERE / "page.tpl.html").read_text()
    out.write_text(tpl.replace("__DATA__", json.dumps(data).replace("</", "<\\/")))
    print(out, out.stat().st_size)


if __name__ == "__main__":
    main()
