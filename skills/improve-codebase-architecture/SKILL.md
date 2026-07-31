---
name: improve-codebase-architecture
description: Scan a codebase for deepening opportunities, present them as a visual HTML report, then grill through whichever one you pick.
disable-model-invocation: true
---

# Improve Codebase Architecture

Surface architectural friction and propose **deepening opportunities** — refactors that turn shallow modules into deep ones. The aim is testability and AI-navigability.

Two vocabularies carry the whole skill, and every candidate is written in both:

- **Architecture** comes from the `/codebase-design` skill — **module**, **interface**, **depth**, **seam**, **adapter**, **leverage**, **locality**, and its principles (the deletion test, "the interface is the test surface", "one adapter = hypothetical seam, two = real"). Run it, and use those words exactly: where a sentence reaches for a looser word, the precise one is always available.
- **Domain** comes from `CONTEXT.md`, which gives names to good seams. If the glossary defines "Order", a candidate concerns the Order intake module.

ADRs in `docs/adr/` record decisions this skill takes as settled.

## Process

### 1. Explore

Read `CONTEXT.md` and any ADRs covering the area you're touching first.

Then use the Agent tool with `subagent_type=skills:explorer` to walk the codebase. Explore organically, following friction where you feel it rather than sweeping for a fixed checklist. These are the shapes friction usually takes:

- Understanding one concept requires bouncing between many small modules.
- A module is **shallow** — its interface is nearly as complex as its implementation.
- Pure functions were extracted for testability, but the real bugs hide in how they're called (no **locality**).
- Tightly-coupled modules leak across their seams.
- A part of the codebase is untested, or hard to test through its current interface.

Apply the **deletion test** to anything you suspect is shallow: would deleting it concentrate complexity, or just move it? A "yes, concentrates" is the signal you want.

Done when every candidate has survived the deletion test and names the modules it touches.

### 2. Describe what each candidate does

Shortlist the candidates, then dispatch a second `skills:explorer` sub-agent scoped to them. The first pass hunts friction across the whole codebase; this one describes only what survived it. For each candidate it returns:

- **What the affected code does**, in domain terms — scoped to the functionality the architectural problem sits inside, not a tour of the surrounding area.
- **What triggers it** — the *shapes* of the entry points rather than an enumeration of call sites. Where the code has no user-facing surface, name the real consumer: another module, a scheduled run, a CLI invocation.

Read from the code, never inferred from file or module names, and held to **Plain language** — pitched at a colleague who knows the product but not this corner of it, so `CONTEXT.md` terms go undefined and area mechanics unassumed.

Where the pass cannot establish what the code does, the candidate stays and the card says so: nobody being able to tell what a module does is the strongest evidence of the friction this skill exists to find, and the Problem line makes exactly that argument.

Done when every shortlisted candidate has a description, or an explicit statement that one could not be established.

### 3. Write the report

Determine a timestamp, and write two files into `.agents/architecture-reviews/<timestamp>/`: `report.md`, written so a `/grill-with-docs` session can pick it up, and a self-contained `report.html` beside it. Both carry the same candidates with the same parts — neither summarises the other. Open the HTML for the user — `xdg-open <path>` on Linux, `open <path>` on macOS, `start <path>` on Windows — and tell them the absolute path.

Run the `/plain-language` skill before writing either file. A review is read with a team who work on different parts of the system, so a card lands with people who have never opened the code it describes.

Every candidate is one card, carrying:

- **Title** — short, names the deepening.
- **What this does** — step 2's description, 1–4 sentences, leading the card ahead of the file list. One sentence is a complete answer where one sentence is the truth.
- **Files** — which files/modules are involved.
- **Problem** — one sentence on why the current architecture causes friction.
- **Solution** — one sentence on what would change.
- **Wins** — the gain in terms of locality and leverage, and how tests improve.
- **Before / After diagram** — side by side, illustrating the shallowness and the deepening.
- **Recommendation strength** — `Strong`, `Worth exploring`, or `Speculative`.
- **ADR callout** — where the candidate contradicts an ADR, a warning reading _"contradicts ADR-0007 — but worth reopening because…"_. Surface the contradiction only where the friction is real enough to warrant reopening that decision, and the bar for real is friction you have observed in the code.

End the report with a **Top recommendation** section: which candidate you'd tackle first and why.

The report uses **Tailwind via CDN** for layout and styling, and **Mermaid via CDN** for diagrams. Reach for Mermaid when relationships are graph-shaped (call graphs, dependencies, sequences), and hand-built divs/SVG when you want something editorial (mass diagrams, cross-sections, collapse animations). See [HTML-REPORT.md](HTML-REPORT.md) for the scaffold, how each part renders, diagram patterns, and styling.

The report stops at candidates: each one says what would change and why it helps, and the interface behind the seam is step 4's work with the user in the room.

Done when both files are written, every candidate has a card carrying all eight parts plus an ADR callout where one applies, and the user has been asked which one they want to explore.

### 4. Grilling loop

Once the user picks a candidate, run the `/grilling` skill to walk the design tree with them — constraints, dependencies, the shape of the deepened module, what sits behind the seam, what tests survive. The card's **What this does** is already established; the session starts from it rather than re-deriving it.

Side effects happen inline as decisions crystallize — run the `/domain-modeling` skill to keep the domain model current as you go:

- **Naming a deepened module after a concept not in `CONTEXT.md`?** Add the term to `CONTEXT.md`. Create the file lazily if it doesn't exist.
- **Sharpening a fuzzy term during the conversation?** Update `CONTEXT.md` right there.
- **User rejects the candidate with a load-bearing reason?** Offer an ADR, framed as: _"Want me to record this as an ADR so future architecture reviews don't re-suggest it?"_ The bar is that a future explorer would need the reason to avoid re-suggesting the same thing — a reason that outlives this week and isn't self-evident from the code.
- **Want to explore alternative interfaces for the deepened module?** Run the `/codebase-design` skill and use its design-it-twice parallel sub-agent pattern.

Done when the design tree's frontier is empty and every term the session coined is in `CONTEXT.md`.
