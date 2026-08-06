---
name: plain-language
description: Plain language in the sense of ISO 24495-1:2023 — the house standard for every sentence a person reads. Use when writing a document, report, review, or interview round a person will read, or when another skill needs the plainness bar.
---

# Plain Language

Every sentence a skill puts in front of a person is written for a developer new to this codebase. They know software. They do not know this repo, and they cannot look up a word that exists only inside a skill.

This binds wording. A grilling session asks the same questions at the same depth, and a review reports the same findings — only the sentences change.

## The bar

- One idea per sentence.
- Active voice, with the actor named.
- At most one subordinate clause.
- Words the reader already holds.

**Clarity outranks brevity.** A sentence that needs a second sentence to land gets one. Cutting words until a claim turns ambiguous fails this bar rather than meeting it.

The test on any sentence: can the reader read it once and act?

## Three tiers of vocabulary

**The project's own terms** — whatever `CONTEXT.md` defines — are used bare. That file is the reader's dictionary, and `/domain-modeling` keeps it current as terms settle.

**A skill's own terms** get a **Gloss** the first time they appear in a session: the plain words in parentheses, once, and then the term stands alone. *"The frontier (the questions I can ask now) is empty."*

**A definition site** — text whose job is to fix the meaning of a term — spends whatever words precision needs. A `CONTEXT.md` entry, a glossary heading, an ADR passage that coins a name. Careful words paid once are what make the shorthand safe to use everywhere else.

## Documents outlive the session

A document travels. A Refinement is written back to a Jira ticket, and a Spec is read cold weeks later by someone who was never in the room. That reader cannot ask what a word meant.

So a durable document spends the plain words rather than a **Gloss**: *"what we do not know yet"*, not *"fog"*. Where a template fixes a section name, keep the name and gloss it once underneath.

## Where the bar stops

Text written for a sub-agent stays as it is — a Step, a handoff. Agents do not tire, and a document read only by one carries no reader to protect.
