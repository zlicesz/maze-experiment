#!/usr/bin/env python3
"""
Build a Maze materials file in which only a FEW word pairs use a PSEUDOWORD distractor,
and "were" is the distractor at the "was" position for a few chosen items.

Usage:
    python3 make_materials.py original_materials.csv materials.csv

The input file is your ORIGINAL materials file (real-word distractors). Needs:
    pip install wordfreq      (used only to make sure no pseudoword is a real word)

What it does
  * In each sentence, PSEUDO_PER_SENTENCE word pairs (default 2) get a pseudoword distractor.
    A pseudoword is pronounceable and has the SAME number of letters as the correct word,
    keeping capital letters and punctuation (e.g. "week," -> "veeg,").
  * All other word pairs keep the real-word distractor from the original file.
  * The pseudoword positions are never the first word (x-x-x), never "was", and only words of
    3+ letters. They are chosen from words that appear in BOTH the AAL and Neutral versions of
    the item, so both versions get identical distractors at identical words.
  * For the items listed in WERE_ITEMS, the distractor at the position of "was" is "were".
    Both conditions of an item get the same treatment.
  * New columns: WasWere (yes/no) and PseudoPos (the word positions, counting from 1, that
    have a pseudoword distractor, e.g. "3 6").
"""
import csv, hashlib, random, re, sys
from collections import defaultdict
from wordfreq import zipf_frequency

# ---- Settings you can change ----
WERE_ITEMS = {"WAS02", "WAS06", "WAS10", "WAS14", "WAS18", "WAS22"}
PSEUDO_PER_SENTENCE = 2      # how many word pairs per sentence get a pseudoword (0 = none)
MIN_LETTERS = 4              # only words with at least this many letters get a pseudoword
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

def cores(row):
    return [split_punct(w)[1].lower() for w in tidy(row["Sentence"])]

def choose_pseudo_words(item_rows):
    """Pick the words (lowercase) of an item that get a pseudoword distractor in every version."""
    if PSEUDO_PER_SENTENCE <= 0:
        return []
    common = None
    for r in item_rows:
        eligible = {c for c in cores(r)[1:] if len(c) >= MIN_LETTERS and c != "was"}
        common = eligible if common is None else common & eligible
    ranked = sorted(common, key=lambda c: hashlib.md5(f"{item_rows[0]['Item']}|{c}".encode()).hexdigest())
    return ranked[:PSEUDO_PER_SENTENCE]

def make_row(row, chosen):
    words = tidy(row["Sentence"])
    orig = tidy(row["Distractor"])
    assert len(orig) == len(words), f"{row['Item']} {row['Condition']}: word counts differ"
    dists = [orig[0]]                     # x-x-x
    used, done, pos = set(), set(), []
    was_pos = next((i for i, w in enumerate(words) if split_punct(w)[1].lower() == "was"), None)
    use_were = row["Item"] in WERE_ITEMS and was_pos is not None
    for i in range(1, len(words)):
        pre, core, post = split_punct(words[i])
        k = core.lower()
        if use_were and i == was_pos:
            dists.append("were")
        elif k in chosen and k not in done:
            done.add(k)
            seed = hashlib.md5(f"{row['Item']}|{k}".encode()).hexdigest()
            p = pseudo(core, seed, used)
            used.add(p)
            if core[:1].isupper():
                p = p.capitalize()
            dists.append(pre + p + post)
            pos.append(i + 1)
        else:
            dists.append(orig[i])         # keep the original real-word distractor
    return " ".join(dists), ("yes" if use_were else "no"), " ".join(map(str, pos))

def main(src, dst):
    with open(src, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    by_item = defaultdict(list)
    for r in rows:
        by_item[r["Item"]].append(r)
    chosen = {item: choose_pseudo_words(rs) for item, rs in by_item.items()}
    for r in rows:
        r["Distractor"], r["WasWere"], r["PseudoPos"] = make_row(r, chosen[r["Item"]])
    cols = ["Item", "Condition", "Group", "Sentence", "Distractor", "WasWere", "PseudoPos"]
    with open(dst, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)
    n_pseudo = sum(len(r["PseudoPos"].split()) for r in rows)
    print(f"Wrote {len(rows)} rows to {dst} ({n_pseudo} pseudoword distractors in total)")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(*sys.argv[1:])
