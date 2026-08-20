# HTML Report Format

Self-contained HTML for Product to forward — people who never open the codebase. The closing render is **user-facing** and holds **room language** from [SKILL.md](SKILL.md). Render `complete.html` from `complete.md` only at close. The Prototype is the picture during the session.

## Scaffold

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Refinement — {{change title}}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
      .today { background: #f5f5f4; }
      .in-scope { background: #ecfdf5; }
      .out-of-scope { background: #fff7ed; }
    </style>
  </head>
  <body class="bg-stone-50 text-slate-900 font-sans">
    <main class="max-w-5xl mx-auto px-6 py-12 space-y-12">
      <header>...</header>
      <section id="intent">...</section>
      <section id="how-it-works-today" class="today">...</section>
      <section id="in-scope" class="in-scope">...</section>
      <section id="out-of-scope" class="out-of-scope">...</section>
      <section id="prototype">...</section>
      <section id="open-questions">...</section>
    </main>
  </body>
</html>
```

## Header

Change title, date, source (Jira key as a link, or the idea path), and a one-line statement of intent.

Every Complete section appears here in markdown order, including those carrying `None` — the fixed shape is the point, and HTML and Jira share the same six headings.

## How it works today

Behaviour and observable limits, even when `session.md` holds full-fidelity code for resume. A `complete.html` is rendered after the code walk has landed, so it never carries a provisional today.

## In scope / Out of scope

User-facing outcomes and boundaries. Stone-tinted = today, emerald-tinted = in, amber-tinted = out; say so in a compact legend. Out-of-scope items that are split-offs link to their stub.

## Prototype

One prominent card: the question, what playing settled for Scope, and a link to `.agents/prototypes/<slug>/`. `None` is a short card, not an omitted section.

## Open questions

One amber card, each question with who owes the answer.

## Tone

Room language from [SKILL.md](SKILL.md). Domain nouns come from `CONTEXT.md` — if the glossary says Order, the report says Order.

Every claim about today traces to `session.md`'s `How it works today`, which traces to the code. In scope names only what the room confirmed. Unsettled detail about after is an open question.
