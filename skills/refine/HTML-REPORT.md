# HTML Report Format

Self-contained HTML for the room and for Product to forward — people who never open the codebase. Both renders are **user-facing** and hold **room language** from [SKILL.md](SKILL.md).

Two renders: mid-session `session.html` from `session.md`; closing `complete.html` from `complete.md`. Sections below are the closing shape.

## Mid-session render

Map `Intent` → `introduction`, `What changes` → `scope`. Include open questions, use cases, and out of scope. Restate `How it works today` as behaviour and observable limits (room language), even when `session.md` holds full-fidelity code for resume. Carry a **provisional today** label when present. Omit `notes` until synthesis.

## Scaffold

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Refinement — {{change title}}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script type="module">
      import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
      mermaid.initialize({ startOnLoad: true, theme: "neutral", securityLevel: "loose" });
    </script>
    <style>
      /* small custom layer: today/after tinting, parked-question markers */
      .today { background: #f5f5f4; }
      .after { background: #ecfdf5; }
    </style>
  </head>
  <body class="bg-stone-50 text-slate-900 font-sans">
    <main class="max-w-5xl mx-auto px-6 py-12 space-y-12">
      <header>...</header>
      <section id="introduction">...</section>
      <section id="open-questions">...</section>
      <section id="use-cases" class="space-y-10">...</section>
      <section id="scope">...</section>
      <section id="out-of-scope">...</section>
      <section id="notes">...</section>
    </main>
  </body>
</html>
```

## Header

Change title, date, source (Jira key as a link, or the idea path), and a one-line statement of intent. Stone-tinted = today, emerald-tinted = after; say so in a compact legend.

Every Complete section appears here in markdown order, including those carrying `None` — the fixed shape is the point, and HTML and Jira share the same six headings.

## Scope

The work as bullets a Product manager can read aloud — items rather than prose.

## Use-case card

Each use case is one `<article>`: the user story as the heading, its scenarios as a list, and one visual. The visual carries the weight — if it needs a paragraph to be understood, redraw it.

QA reads the scenarios as the thing they will test against, so keep each one concrete: a named starting state, one action, one observable outcome. Mark the non-happy-path scenario with an amber left border so it can't be skimmed past.

## Visual vocabulary

Pick the one that fits the use case. Mix across the report. Diagram labels use the same vocabulary as the prose: actors, screens, states, observable outcomes.

### Today / after flow pair (the workhorse)

Two Mermaid `flowchart`s side by side, same width, stone card for today and emerald for after. Steps that survive the change keep their wording verbatim between the two, so the eye lands on what moved.

```html
<div class="grid grid-cols-2 gap-4">
  <div class="rounded-lg border border-stone-200 today p-4">
    <p class="text-xs uppercase tracking-wider text-stone-500 mb-2">Today</p>
    <pre class="mermaid">
      flowchart TD
        A[Planner opens Order] --> B[Edits each line by hand]
        B --> C[Saves]
    </pre>
  </div>
  <div class="rounded-lg border border-emerald-200 after p-4">
    <p class="text-xs uppercase tracking-wider text-emerald-700 mb-2">After</p>
    <pre class="mermaid">
      flowchart TD
        A[Planner opens Order] --> B[Applies a reschedule]
        B --> C[Confirms the preview]
        C --> D[Saves]
    </pre>
  </div>
</div>
```

### State diagram (when the change is stateful)

A Mermaid `stateDiagram-v2` of the statuses something moves through, with transitions the change adds drawn in emerald and transitions it removes drawn dashed and greyed. One diagram covering both states of the world beats a pair here.

### Decision table (for the edge cases)

An HTML table: one row per condition combination the grilling surfaced, columns for the condition inputs and one for the expected outcome. Settled rows carry their outcome; parked rows carry a `?` and a link to the open question.

### Screen flow (when the change is UI-shaped)

Hand-built boxes: one `<div>` per screen or dialog with its key elements listed as `text-xs` lines inside, arrows as inline SVG between them. Wireframe weight — which screens exist and in what order.

## Open questions

One amber card, each question with who owes the answer. Sits second so it is not scrolled past.

## Notes

One plain card: constraints of today that bind the change, plus useful context the other sections omit.

## Tone

Room language from [SKILL.md](SKILL.md). Domain nouns come from `CONTEXT.md` — if the glossary says Order, the report says Order.

Every claim about today traces to `session.md`'s `How it works today`, which traces to the code. In `complete.html`, today-claims condense into Introduction and Notes rather than a new source. An unsettled detail about after is an open question, not a confident box on a diagram.

A `complete.html` is rendered after the code walk has landed, so it never carries a provisional today.
