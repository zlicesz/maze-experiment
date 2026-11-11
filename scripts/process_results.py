#!/usr/bin/env python3
"""
Turn a PCIbex results file from the Maze experiment into one clean row per word.

Usage:
    python3 process_results.py results.csv materials.csv word_level.csv

Output columns:
    ID, Item, Condition, Group, Sentence, Position, Word, Distractor,
    PressedKey, CorrectSide, Correct, RT, SentenceTime, WasWere

RT is taken from the RT_01, RT_02, ... rows when they exist (new version of main.js).
Otherwise it is computed from the time differences between key presses (older results).
Distractors come from the Distractor column if it exists, otherwise from materials.csv.
"""
import csv, re, sys, urllib.parse
from collections import defaultdict

def tidy(s):
    return re.sub(r"\s+([,.;:!?])", r"\1", s.strip()).split()

def parse(results_path):
    """Yield (extra_columns, fields) for every data row."""
    extra = []
    with open(results_path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("# Results on"):
                extra = []
            m = re.match(r"^# (\d+)\. (.*)\.$", line)
            if m and int(m.group(1)) >= 13:
                if int(m.group(1)) == 13:
                    extra = []
                extra.append(m.group(2))
            if not line or line.startswith("#"):
                continue
            fields = next(csv.reader([line]))
            yield list(extra), fields

def main(results, materials, out):
    # materials lookup: (Item, Condition) -> distractor string
    dist_lookup = {}
    with open(materials, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            dist_lookup[(r["Item"], r["Condition"])] = r["Distractor"]

    trials = defaultdict(lambda: {"keys": [], "rt": {}, "start": None, "st": None, "meta": {}})
    order = []
    for extra, f in parse(results):
        if len(f) < 13 or f[5] != "maze":
            continue
        # fixed columns: 0 time, 1 md5, 2 controller, 3 order, 4 inner, 5 label, 6 group,
        # 7 type, 8 name, 9 parameter, 10 value, 11 eventtime, then the extras
        names, value, evt = f[8], f[10], f[11]
        meta = dict(zip(extra, f[12:12 + len(extra)]))
        key = (f[0], f[1], f[3])       # reception time + participant + trial number
        t = trials[key]
        if key not in order:
            order.append(key)
        t["meta"] = meta
        ptype, param = f[7], f[9]
        if ptype == "PennController" and param == "_Trial_" and value == "Start":
            t["start"] = int(evt)
        elif ptype == "Key" and param == "PressedKey":
            t["keys"].append((int(re.sub(r"\D", "", names)), value, int(evt)))
        elif ptype == "Var" and names.startswith("RT_") and param == "Final":
            if value != "NA":
                t["rt"][int(names[3:])] = int(float(value))
        elif ptype == "Var" and names == "SentenceTime" and param == "Final":
            t["st"] = int(float(value))

    rows = []
    for key in order:
        t = trials[key]
        m = t["meta"]
        if not t["keys"] or "Sentence" not in m:
            continue
        sentence = urllib.parse.unquote(m["Sentence"])
        words = tidy(sentence)
        dist_str = urllib.parse.unquote(m.get("Distractor", "")) or dist_lookup.get((m["Item"], m["Condition"]), "")
        dists = tidy(dist_str)
        sides = m.get("CorrectSides", "")
        keys = sorted(t["keys"])
        prev = t["start"]
        total = 0
        for idx, pressed, evt in keys:
            pos = idx + 1
            rt = t["rt"].get(pos)
            if rt is None and prev is not None:
                rt = evt - prev
            prev = evt
            total += rt or 0
            side = sides[idx] if idx < len(sides) else ""
            correct = (pressed == "F" and side == "L") or (pressed == "J" and side == "R")
            rows.append({
                "ID": urllib.parse.unquote(m.get("ID", "")),
                "Item": m.get("Item", ""), "Condition": m.get("Condition", ""),
                "Group": m.get("Group", ""), "Sentence": sentence,
                "Position": pos,
                "Word": words[idx] if idx < len(words) else "",
                "Distractor": dists[idx] if idx < len(dists) else "",
                "PressedKey": pressed, "CorrectSide": side,
                "Correct": int(correct), "RT": rt, "SentenceTime": None,
                "WasWere": m.get("WasWere", ""),
            })
        for r in rows[-len(keys):]:
            r["SentenceTime"] = t["st"] if t["st"] is not None else total

    cols = ["ID","Item","Condition","Group","Sentence","Position","Word","Distractor",
            "PressedKey","CorrectSide","Correct","RT","SentenceTime","WasWere"]
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} word rows from {len(order)} sentences to {out}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
