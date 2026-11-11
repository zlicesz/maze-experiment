# Maze task: was/were variation (PCIbex)

PCIbex Maze experiment for Prof. Zachary Maher's research on how people process
dialectal and grammatical variation (African American English and Dominant American English).
Participants see two words at a time and choose the one that continues the sentence; a wrong
choice ends the sentence. Built with PennController (JavaScript).

## Folder structure 

| Folder | Contents |
|---|---|
| `data_includes/main.js` | The experiment code |
| `chunk_includes/materials.csv` | 42 items, AAL and Neutral versions, 2 lists |
| `css_includes/`, `js_includes/` | PCIbex framework files (unchanged) |
| `scripts/` | Python tools (see below) |
| `test/` | Short 3-sentence version for testing |

## Notes

- Results are only saved if a participant reaches the end of the experiment.
- Do not commit results files (they can contain participant IDs); `.gitignore` excludes them.
- Pseudowords were generated with a simple length-matched script, not a tool like Wuggy.
