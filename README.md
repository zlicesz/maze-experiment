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
- Distractors are length-matched pseudowords. For six items (WAS02, WAS06, WAS10, WAS14,
  WAS18, WAS22) the distractor at the position of "was" is "were" (`WasWere` column).
- Logging: a reaction time for every word position (`RT_01`, `RT_02`, ...), `SentenceTime`,
  the key pressed, and the distractor string. Words never reached after an error are `NA`.
- Participants enter an ID on the first screen.

## How to run

1. Create a project on the PCIbex Farm (or sync this repository).
2. Make sure `data_includes/main.js` and `chunk_includes/materials.csv` are in the project.
3. Click Test, finish a full run so the results are saved, then download the results.

To try a short version first, put `test/main_test.js` in place of `main.js` and upload
`test/materials_test.csv` as a resource.

## Python scripts (`scripts/`)

Build the materials with pseudoword distractors (needs `pip install wordfreq`):

    python3 scripts/make_materials.py original_materials.csv chunk_includes/materials.csv

Turn a results file into one row per word (Word, Distractor, RT, PressedKey, Correct, SentenceTime, WasWere):

    python3 scripts/process_results.py results.csv chunk_includes/materials.csv word_level.csv

## Notes

- Results are only saved if a participant reaches the end of the experiment.
- Do not commit results files (they can contain participant IDs); `.gitignore` excludes them.
- Pseudowords were generated with a simple length-matched script, not a tool like Wuggy.
