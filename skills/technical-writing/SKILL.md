---
name: technical-writing
description: The house standard for every sentence a person reads. Use when writing a document, report, review, or interview round a person will read, or when another skill needs the writing bar.
---

# Technical writing

Every sentence a skill puts in front of a person is written for a developer new to this codebase, so they understand it on the first read. They know software. They do not know this repo, and they cannot look up a word that exists only inside a skill. The one other reader is the **Product reader** of a Tracker document, below.

This binds wording. A grilling session asks the same questions at the same depth, and a review reports the same findings. Only the sentences change.

Three rules sit above the rest:

- **Cut every word that does no work.** If the sentence survives without a word, the word goes.
- **Use the short, everyday word.** "Use", not "utilize" or "leverage". "Help", not "facilitate". "If", not "in the event that". A long word has to buy its length with precision.
- **Clarity outranks brevity.** A sentence that needs a second sentence to land gets one. Cutting words until a claim turns ambiguous fails this bar. When a rule makes a sentence worse, fix the sentence another way or leave it alone.

The test on any sentence: can the reader read it once and act?

## Before the first sentence

1. Read [UNSLOP.md](UNSLOP.md), the catalogue of AI tells. Every text a person reads in this session is checked against each of its patterns before they read it. A text written to a file also gets a search for `—`, `–`, and `;`, and every match outside code is rewritten.
2. Writing a document no template shapes, such as a README, a page under `docs/`, or a research file? Read [TYPES.md](TYPES.md) and pick the document's one type.

Done: `UNSLOP.md` is read, and a free-form document has its type.

## Vocabulary

**The project's own terms**, whatever `CONTEXT.md` defines, are used bare. That file is the reader's dictionary, and `/domain-modeling` keeps it current as terms settle. The codebase is the word list too: write the real symbol, file, flag, or command name, not a synonym or a description of it.

**A skill's own terms** get a **Gloss** the first time they appear in a session: the plain words in parentheses, once, and then the term stands alone. *"The frontier (the questions I can ask now) is empty."*

**A definition site**, text whose job is to fix the meaning of a term, spends whatever words precision needs. A `CONTEXT.md` entry, a glossary heading, an ADR passage that coins a name. Careful words paid once are what make the shorthand safe to use everywhere else.

Coin nothing else. Use the words a developer would say out loud: "move", "delete", "a limit that only goes down", not "evacuate", "ratchet", or "endgame".

## Documents outlive the session

A document travels. An Issue is shared well beyond the session that wrote it, and a Spec is read cold weeks later by someone who was never in that session. That reader cannot ask what a word meant.

So a durable document spends the plain words rather than a **Gloss**: *"what we do not know yet"*, not *"fog"*. Where a template fixes a section name, keep the name and gloss it once underneath.

A document in the Tracker, an Issue, a Map, or a Spec, is also read by the **Product reader**: someone who knows the product but not its code, such as a QA tester. The part that says what is wrong and what changes is theirs. It names only what that reader meets on the product (screens, controls, commands they type, messages) and terms `CONTEXT.md` defines. Files, functions, classes, and internal parts belong to the technical part, which keeps the developer reader. Those sections are a Spec's Problem Statement, Solution, How to Check It, and User Stories, a `needs-` Issue's Motivation and Goal, and a Map's Destination.

## Sentences

- Talk to the reader as "you", in the present tense. Use "will" only for what really happens later.
- Name the actor: "the compiler checks", not "is checked". Passive only when the actor is unknown or beside the point.
- Write an instruction as a command, one per sentence: "Run `npm test`." Put the condition or warning before it: "To delete the document, click Delete."
- One thought per sentence. Split an instruction past about 20 words and any other sentence past about 25.
- Put the common case first and exceptions after.
- Keep "the" and "a", and the small words that show structure, such as "that" in "check that the switch is off".
- Keep "only" and "not" next to the word they change: "fails only on growth".
- Make every "it", "they", and "this" point at one obvious thing, and repeat the noun when in doubt. "This" and "which" never point at a whole clause.
- Give each verb its own clause: "Phase 1 moves the converters and Phase 2 moves the runtime."
- Break up long noun strings: "the script that checks the import budget", not "the import budget check script".
- Call each thing by one name everywhere, and give each word one meaning.
- Make text in parentheses a full sentence. A **Gloss** is the one exception. Write "a, b, or both", not "a/b" or "and/or", and never form a plural with "(s)".
- Where a dash or a semicolon would go, end the sentence or use a comma: text a person reads carries no em dash, en dash, or semicolon. A colon only introduces a list, an example, or a block, or follows a label a template fixes.
- Skip idioms, Latin abbreviations, and "simply", "easy", or "quickly" in a procedure.
- Write real paths. Make every count true at the commit that lands it.

Formatting:

- Headings carry the point, not just the topic ("Pick the type first", not "Types"), in sentence case. One h1 per page, and no skipped levels.
- Numbered lists for sequences, bullets for everything else. Introduce a list with a complete sentence and keep its items parallel.
- Code, paths, and commands go in code font. UI elements go in bold. Use serial commas. Say up front that a list is partial rather than ending it with "etc.".

## Rhythm

A text can obey every rule and still read as machine-written: every sentence clipped short, no view anywhere, nothing specific.

- Mix sentence lengths on purpose. A short sentence lands a point. A longer one carries a fact with its condition or consequence.
- Have a view where the text allows it. When weighing trade-offs, say what you make of them instead of listing pros and cons. Reference stays dry.
- Be specific: not "schema changes can cause issues" but "a column rename fails the build".

## Where the bar stops

Text written for a sub-agent stays as it is: a sub-agent prompt, a handoff. Agents do not tire, and a document read only by one carries no reader to protect. Product UI strings follow the product's own copy guidelines.

## Worked example

Before:

> Configuration of the import budget script parameters is performed via budget.json. Note that it's important to remember that running with --write, which updates the committed budget to reflect the current count, should only be done when lowering it. If exceeded, CI fails.

After:

> `budget.mjs` reads the committed budget from `budget.json` and counts the files that import protos. If the count exceeds the budget, CI fails. Run `budget.mjs --write` only to lower the budget.
