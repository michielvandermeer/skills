# HTML Report Format

The Refinement's twin: a single self-contained HTML file beside its markdown. Tailwind and Mermaid both come from CDNs. This is what the room looks at while they talk and what Product forwards afterwards — it is read by people who will never open the codebase.

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
      <section id="intent">...</section>
      <section id="what-changes">...</section>
      <section id="use-cases" class="space-y-10">...</section>
      <section id="open-questions">...</section>
      <section id="out-of-scope">...</section>
    </main>
  </body>
</html>
```

## Header

Change title, date, source (Jira key as a link, or the idea path), and a one-line statement of intent. Stone-tinted = today, emerald-tinted = after; say so in a compact legend. No introduction paragraph.

## What changes

The delta, as bullets a Product manager can read aloud. Where the change replaces existing behaviour, render it as a two-column `today → after` pair rather than prose.

## Use-case card

Each use case is one `<article>`: the user story as the heading, its scenarios as a list, and one visual. The visual carries the weight — if it needs a paragraph to be understood, redraw it.

QA reads the scenarios as the thing they will test against, so keep each one concrete: a named starting state, one action, one observable outcome. Mark the non-happy-path scenario with an amber left border so it can't be skimmed past.

## Visual vocabulary

Pick the one that fits the use case. Mix across the report.

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

An HTML table: one row per condition combination the grilling surfaced, columns for the condition inputs and one for the expected outcome. This is where parked and settled edge cases become visibly distinct — settled rows carry their outcome, parked rows carry a `?` and a link to the open question.

### Screen flow (when the change is UI-shaped)

Hand-built boxes: one `<div>` per screen or dialog with its key elements listed as `text-xs` lines inside, arrows as inline SVG between them. Wireframe weight, not pixel-accurate — the point is which screens exist and in what order, not what they look like.

## Open questions

One amber card, each question with who owes the answer. A Refinement with three named open questions is doing its job; leave them prominent rather than tucked at the bottom of a page nobody scrolls.

## Tone

Plain English at the altitude of the room. The domain nouns come from `CONTEXT.md` — if the glossary says Order, the report says Order, not "the order record".

Actors, screens, states, and observable outcomes are the whole vocabulary, in prose and in the boxes on a diagram alike — architecture nouns stay out. Where a statement seems to need one, name the behaviour instead: *"the planner sees the new date immediately"*, not *"the projection updates synchronously"*.

Every claim about today traces to the markdown's `How it works today`, which traces to the code. An unsettled detail about after is an open question, not a confident box on a diagram.

A mid-session render can catch a **provisional today**. Carry its label into the render, so the room reads that section as a document rather than as the code.
