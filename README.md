# Maze task: was/were variation (PCIbex)

PCIbex Maze experiment for Prof. Zachary Maher's research on how people process
dialectal and grammatical variation (African American English and Dominant American English).
Participants see two words at a time and choose the one that continues the sentence; a wrong
choice ends the sentence. Built with PennController (JavaScript).

## Folder structure (same layout as a PCIbex project)

| Folder | Contents |
|---|---|
| `data_includes/main.js` | The experiment code |
| `chunk_includes/materials.csv` | 42 items, AAL and Neutral versions, 2 lists |
| `css_includes/`, `js_includes/` | PCIbex framework files (unchanged) |
| `scripts/` | Python tools (see below) |
| `test/` | Short 3-sentence version for testing |

## What the experiment does

- Counterbalancing: each item has an AAL and a Neutral version, split across Group 1 and Group 2.
- Distractors are real words, except that in each sentence only a few word pairs (2 by default)
  use a length-matched pseudoword. The positions are listed in the `PseudoPos` column.
  For six items (WAS02, WAS06, WAS10, WAS14, WAS18, WAS22) the distractor at the position of
  "was" is "were" (`WasWere` column).
- The layout is centered: each word pair appears in two boxes centered on the page.
- Logging: a reaction time for every word position (`RT_01`, `RT_02`, ...), `SentenceTime`,
  the key pressed, the distractor string, and which positions had pseudowords. Words never reached after an error are `NA`.
- Participants enter an ID on the first screen.

## How to run

1. Create a project on the PCIbex Farm (or sync this repository).
2. Make sure `data_includes/main.js` and `chunk_includes/materials.csv` are in the project.
3. Click Test, finish a full run so the results are saved, then download the results.

To try a short version first, put `test/main_test.js` in place of `main.js` and upload
`test/materials_test.csv` as a resource.

## Python scripts (`scripts/`)

Build the materials from the original file (real-word distractors) and add the pseudowords
(needs `pip install wordfreq`; change `PSEUDO_PER_SENTENCE` or `WERE_ITEMS` at the top of the script):

    python3 scripts/make_materials.py original_materials.csv chunk_includes/materials.csv

Turn a results file into one row per word (Word, Distractor, DistractorType, RT, PressedKey, Correct, SentenceTime, WasWere):

    python3 scripts/process_results.py results.csv chunk_includes/materials.csv word_level.csv

## Notes

- Results are sent after every sentence, so partial sessions are kept (a participant who closes
  the window in the middle of a sentence loses only that sentence).
- Do not commit results files (they can contain participant IDs); `.gitignore` excludes them.
- Pseudowords were generated with a simple length-matched script, not a tool like Wuggy.
- `DistractorType` in the processed data is x-x-x, were, pseudo or real.
