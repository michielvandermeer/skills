# Page

The page is `explain/<slug>/index.html`. Tailwind and Mermaid come from their CDNs; everything else is inline, so it opens by double-click.

## Scaffold

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{{topic}}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script type="module">
      import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
      mermaid.initialize({ startOnLoad: true, theme: "neutral" });
    </script>
  </head>
  <body class="bg-stone-50 text-slate-900">
    <main class="max-w-4xl mx-auto px-6 py-12 space-y-12">...</main>
  </body>
</html>
```

## Shape

- Open with the answer in one sentence, then the drawing that carries it. Prose explains the drawing; a drawing that needs a paragraph gets redrawn.
- One section per part of the topic, each led by its own drawing.
- **Mermaid** for graph-shaped relationships: flows, sequences, dependencies. **Inline SVG** for the editorial ones: a layout in memory, a structure changing shape, quantities side by side.
- **Controls** — step-through buttons, a slider, detail on hover — where moving through states or varying a value is the understanding: an algorithm's steps, a parameter's effect. A page about a static structure stays static. Plain inline JavaScript.
- One accent colour, plus one highlight for whatever changes.
- A Sources section at the bottom.

## Check

Screenshot the page when the machine can: a headless Chromium-family browser (`chromium --headless --virtual-time-budget=5000 --window-size=1280,2400 --screenshot=<slug-folder>/screenshot.png file://<path>`) or the host's own browser tool. Look at it: every drawing rendered, nothing overlapping or cut off, every control visible. Fix and look again.

Done when the screenshot shows a clean page, or no screenshot can be taken. Delete `screenshot.png` then; it is run scratch.
