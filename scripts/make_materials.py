#!/usr/bin/env python3
"""
Build a Maze materials file with PSEUDOWORD distractors, and "were" as the
distractor at the "was" position for a few chosen items.

Usage:
    python3 make_materials.py materials.csv materials_new.csv

Needs:  pip install wordfreq      (used only to make sure no pseudoword is a real word)

What it does
  * Every distractor word is replaced by a pronounceable pseudoword with the SAME number
    of letters as the correct word, keeping capital letters and punctuation
    (e.g. "week," -> "wuft,").
  * The first distractor stays x-x-x.
  * For the items listed in WERE_ITEMS, the distractor at the position of "was" is "were".
    Both conditions (AAL / Neutral) of an item get the same treatment.
  * The same correct word in the same item always gets the same pseudoword, so the AAL and
    Neutral versions of an item share identical distractors wherever their words are identical.
  * A new column WasWere (yes/no) marks the items with was/were.
"""
import csv, hashlib, random, re, sys
from wordfreq import zipf_frequency

# ---- Settings you can change ----
WERE_ITEMS = {"WAS02", "WAS06", "WAS10", "WAS14", "WAS18", "WAS22"}
# ---------------------------------

ONSETS = ["b","d","f","g","h","j","k","l","m","n","p","r","s","t","v","w","z",
          "bl","br","cl","cr","dr","fl","fr","gl","gr","pl","pr","sl","st","tr","sh","ch"]
VOWELS = ["a","e","i","o","u","a","e","i","o","u","oo","ee"]
CODAS  = ["b","d","g","k","l","m","n","p","r","s","t","ld","lk","nd","nk","nt","rd","rk","rt","st","sk"]

tidy = lambda s: re.sub(r"\s+([,.;:!?])", r"\1", s.strip()).split()

def split_punct(w):
    m = re.match(r"^([^\w]*)(.*?)([^\w]*)$", w)
    return m.group(1), m.group(2), m.group(3)

def pseudo(core, seed, avoid=()):
    """Pronounceable nonword with exactly len(core) letters, built from syllables."""
    rng = random.Random(seed)
    n = len(core)
    if n == 1:
        return rng.choice([c for c in "bdfgjkpqvwxz" if c not in avoid])
    if n == 2:
        cands = [c + v for c in "bdfgjklmnprstvwz" for v in "aeiou"]
        cands = [c for c in cands if c != core.lower() and c not in avoid]
        cands.sort(key=lambda w: zipf_frequency(w, "en"))
        return rng.choice(cands[:20])          # one of the 20 rarest CV strings
    for _ in range(40000):
        w = ""
        while len(w) < n:
            need_onset = (not w) or (w[-1] in "aeiou")     # never join two vowels
            onset = rng.choice(ONSETS) if (need_onset or rng.random() < 0.9) else ""
            syl = onset + rng.choice(VOWELS)
            if rng.random() < 0.5:
                syl += rng.choice(CODAS)
            w += syl
        if len(w) != n:
            continue
        if re.search(r"(.)\1\1", w) or w == core.lower() or w in avoid:
            continue
        if zipf_frequency(w, "en") == 0:
            return w
    raise RuntimeError("could not make a pseudoword for " + core)

def make_row(row):
    words = tidy(row["Sentence"])
    dists = ["x-x-x"]
    seen = {}
    used = set()          # pseudowords already used in this sentence (kept unique)
    was_pos = next((i for i, w in enumerate(words) if split_punct(w)[1].lower() == "was"), None)
    use_were = row["Item"] in WERE_ITEMS and was_pos is not None
    for i, w in enumerate(words[1:], start=1):
        pre, core, post = split_punct(w)
        if use_were and i == was_pos:
            dists.append("were")
            continue
        k = core.lower()
        seen[k] = seen.get(k, 0) + 1
        seed = hashlib.md5(f"{row['Item']}|{k}|{seen[k]}".encode()).hexdigest()
        p = pseudo(core, seed, used)
        used.add(p)
        if core[:1].isupper():
            p = p.capitalize()
        dists.append(pre + p + post)
    assert len(dists) == len(words)
    return " ".join(dists), ("yes" if use_were else "no")

def main(src, dst):
    with open(src, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["Distractor"], r["WasWere"] = make_row(r)
    cols = ["Item", "Condition", "Group", "Sentence", "Distractor", "WasWere"]
    with open(dst, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {dst}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(*sys.argv[1:])
