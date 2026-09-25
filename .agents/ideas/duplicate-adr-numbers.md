# Idea — Two ADRs share number 0050

Status: idea

## Motivation

`docs/adr/` holds two files numbered 0050:

- `0050-an-adr-states-the-decision-in-force.md` (added in 02ecf7d)
- `0050-retro-learns-from-corrections.md` (added in 60e5088)

Two Specs were probably written in parallel, and each one took the next free number. A link like
"ADR-0050" now points at two documents, and the rule that ADR numbers are never reused
(ADR-0050, "an ADR states the decision in force") has no way to hold while a number is shared.

This came up during the grilling session that gave `/doctor` a layout pass, and
it was left out of that change.

## Goal

Each ADR in a `docs/adr/` folder has a number of its own.

## Open questions

- Should one of the two be renumbered by hand, with every link fixed?
- Should `/doctor` detect duplicate numbers and renumber the newer one?
- Should whichever skill writes an ADR guard against this, for example by checking `master` for
  the next free number at commit time?
