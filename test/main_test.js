// Maze task in PennController (no audio) for the full WAS materials.
// Reads materials_test.csv from the Resources folder.
// Columns used: Item, Condition, Group, Sentence, Distractor, WasWere
//
// Logging: for every sentence the results file gets
//   - one Key row per word pair (PressedKey + EventTime)
//   - one RT_01, RT_02, ... row per word position (reaction time in ms, from the
//     word pair appearing to the key press; "NA" for words never reached because
//     of an earlier error)
//   - a SentenceTime row (sum of the RTs for that sentence)
//   - Distractor, Sentence and CorrectSides columns on every row
// Use process_results.py to turn the results file into one clean row per word
// (Word, Distractor, RT, ...).
//
// Counterbalancing: each item appears in two versions (AAL / Neutral) in
// Group 1 and Group 2. PennController sees the "Group" column and gives each
// participant only the rows of ONE group, so nobody sees both versions of an item.

PennController.ResetPrefix(null);

// ---- Settings you can change ----
const SHOW_FULL_SENTENCE = true;   // show the full sentence after the last correct choice
const FULL_SENTENCE_MS   = 2000;   // how long it stays on screen (milliseconds)
const LEFT_KEY  = "F";
const RIGHT_KEY = "J";
// ---------------------------------

Sequence("intro", randomize("maze"), SendResults(), "bye");

// Merge punctuation onto the previous word so "week ," becomes "week,"
const tidy = s => s.trim().replace(/\s+([,.;:!?])/g, "$1").split(/\s+/);

newTrial("intro",
    newText("id-label", "<p>Please enter your participant name:</p>")
        .css("font-size", "22px")
        .print()
    ,
    newTextInput("inputID")
        .css("font-size", "22px")
        .print()
    ,
    newText("spacer", "<p></p>").print()
    ,
    newText("intro-text",
        "<p>You will see two words at a time, one on the left and one on the right.</p>" +
        "<p>Choose the word that continues the sentence.</p>" +
        "<p>Press <b>" + LEFT_KEY + "</b> for the LEFT word and <b>" + RIGHT_KEY + "</b> for the RIGHT word.</p>" +
        "<p>If you choose the wrong word, the sentence stops and the next one begins.</p>")
        .css("font-size", "22px")
        .print()
    ,
    newButton("start", "Start")
        .center()
        .print()
        // the button only works once something has been typed in the ID box
        .wait(getTextInput("inputID").test.text(/\S+/))
    ,
    // store the ID so it can be logged in every trial
    newVar("ID", "").global().set(getTextInput("inputID"))
);

Template("materials_test.csv", row => {
    const words = tidy(row.Sentence);
    const dists = tidy(row.Distractor);
    const cmds = [];
    let sides = "";   // which side the correct word was on, for each position
    let t0 = 0;       // time (ms) when the current word pair appeared
    let rt = 0;       // reaction time (ms) for the current word pair

    // Logged variables: PCIbex writes ONE row per logged variable, holding its FINAL
    // value at the end of the trial. So each word position gets its own RT variable.
    cmds.push(newVar("clock", 0));              // not logged: only used for timing
    cmds.push(newVar("SentenceTime", 0).log()); // running total of RTs for the sentence
    for (let j = 0; j < words.length; j++) {
        cmds.push(newVar("RT_" + String(j + 1).padStart(2, "0"), "NA").log());
    }

    for (let i = 0; i < words.length; i++) {
        const correctLeft = Math.random() < 0.5;
        const left  = correctLeft ? words[i] : dists[i];
        const right = correctLeft ? dists[i] : words[i];
        const correctKey = correctLeft ? LEFT_KEY : RIGHT_KEY;
        sides += correctLeft ? "L" : "R";

        cmds.push(
            newCanvas("c" + i, 800, 200)
                .add(100, 80, newText("l" + i, left).css("font-size", "32px"))
                .add(600, 80, newText("r" + i, right).css("font-size", "32px"))
                .print()
            ,
            getVar("clock").set(v => { t0 = Date.now(); return t0; })      // start the clock
            ,
            newKey("k" + i, LEFT_KEY + RIGHT_KEY).log().wait()
            ,
            getVar("clock").set(v => { rt = Date.now() - t0; return rt; }) // stop the clock
            ,
            getVar("RT_" + String(i + 1).padStart(2, "0")).set(v => rt)
            ,
            getVar("SentenceTime").set(v => v + rt)
            ,
            getKey("k" + i).test.pressed(correctKey)
                .failure(
                    getCanvas("c" + i).remove(),
                    newText("err" + i, "Wrong word - next sentence").css("font-size", "24px").print(),
                    newTimer("t" + i, 800).start().wait(),
                    end()   // wrong choice: the trial stops here
                )
            ,
            getCanvas("c" + i).remove()
        );
    }

    // These commands only run if every choice was correct
    if (SHOW_FULL_SENTENCE) {
        cmds.push(
            newText("done-label", "Sentence complete:").css("font-size", "20px").print(),
            newText("full-sentence", "<b>" + words.join(" ") + "</b>").css("font-size", "32px").print(),
            newTimer("t-full", FULL_SENTENCE_MS).start().wait()
        );
    }

    return newTrial("maze", ...cmds)
        .log("ID", getVar("ID"))
        .log("Item", row.Item)
        .log("Condition", row.Condition)
        .log("Group", row.Group)
        .log("Sentence", row.Sentence)
        .log("Distractor", row.Distractor)
        .log("WasWere", row.WasWere)
        .log("CorrectSides", sides);
});

newTrial("bye",
    newText("Thank you for participating!").css("font-size", "24px").print(),
    newButton("finish", "Finish").center().print().wait()
);
