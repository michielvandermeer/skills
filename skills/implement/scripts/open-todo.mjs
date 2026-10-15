#!/usr/bin/env node
// Writes an /implement run's todo.md to stdout: the routed playbook's steps verbatim, the consuming repo's project
// playbooks and then the implement Overlay applied at their anchors, the three gates, the landing items, and the
// playbook's prose outside its steps under `## Playbook`.
// Usage: node open-todo.mjs <playbook> --root <consuming repo> --landing worktree|in-place [--start <sha>] [--done "<run item>"]...
import { existsSync, readdirSync, realpathSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";
import { BUNDLED, bundledPlaybook, checkPlaybooks, flat, readProjectPlaybook } from "../../poteto-mode/scripts/check-playbooks.mjs";

export const IMPLEMENT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const STEP = /^(\d+)\. (.*)$/;
const SUB_ITEM = /^\s+(?:- |\d+\. )(.*)$/;
const INDENTED = /^\s+\S/;
const HEADING = /^#+ /;

export const GATE_NAMES = ["Design gate", "Review gate", "Verification gate"];
export const GATES = [
  "Design gate: a trail row names the data shape and its organizing structure, from `design.md` when `architect` ran; a Bug fix also has its runtime-evidence row (`/implement` step 6).",
  "Review gate: `/deslop`, `/no-comments`, then `interrogate` with the intent paragraph from `spec.md`, each over the run's range (`/implement` step 6).",
  "Verification gate: a fresh Verifier that wrote no code, on the head that lands, after the review (`/implement` step 6).",
];
export const LANDING_ITEMS = {
  worktree: [
    "`check-run.mjs` exits 0 (LANDING.md, Before the rebase)",
    "Rebase onto `<onto>`, then the post-rebase re-check unless its skip rule applies (LANDING.md, The rebase)",
    "Close the Issue as its own unit commit (LANDING.md, Close the Issue)",
    "Landing commit (LANDING.md, The landing commit)",
    "Fast-forward and cleanup (LANDING.md, Fast-forward and cleanup)",
    "Push (LANDING.md, The push)",
    "Retro (`/implement` step 8)",
    "Report (`/implement`, Report)",
  ],
  "in-place": [
    "`check-run.mjs` exits 0 (LANDING.md, Before the rebase)",
    "Close the Issue as its own unit commit (LANDING.md, Close the Issue)",
    "Fold into one commit on `<start>` (LANDING.md, Worktree waived)",
    "Push (LANDING.md, The push)",
    "Retro (`/implement` step 8)",
    "Report (`/implement`, Report)",
  ],
};

const item = (text) => ({ text: flat(text).trim(), done: false, children: [] });

// The numbered steps of a bundled playbook, and its prose outside them. A step runs to the next step or the next
// unindented line; an indented `- ` bullet or `1. ` line under it is an item of its own, any other indented line is
// more of the step's text. The prose is every other line but the heading, verbatim, with blank runs collapsed.
export function parseSteps(text) {
  const lines = text.replace(/^﻿/, "").split(/\r?\n/);
  const title = lines.find((line) => HEADING.test(line))?.replace(HEADING, "").trim() ?? "";
  const steps = [];
  const prose = [];
  let step = null;
  for (const line of lines) {
    const top = line.match(STEP);
    if (top) {
      step = item(`${top[1]}. ${top[2]}`);
      steps.push(step);
      continue;
    }
    if (step && line.trim() === "") continue;
    const sub = step && line.match(SUB_ITEM);
    if (sub) step.children.push(item(sub[1]));
    else if (step && INDENTED.test(line)) step.text = `${step.text} ${line.trim()}`;
    else {
      step = null;
      if (!HEADING.test(line) && !(line.trim() === "" && prose.at(-1) === "")) prose.push(line.trimEnd());
    }
  }
  while (prose.at(-1) === "") prose.pop();
  while (prose[0] === "") prose.shift();
  return { title, steps, prose: prose.join("\n") };
}

function locate(items, anchor) {
  const hits = [];
  const walk = (list) => list.forEach((entry, index) => {
    if (entry.text.includes(anchor)) hits.push({ list, index, entry });
    walk(entry.children);
  });
  walk(items);
  return hits;
}

const APPLY = {
  After: ({ list, index }, text) => list.splice(index + 1, 0, item(text)),
  Before: ({ list, index }, text) => list.splice(index, 0, item(text)),
  Replace: ({ entry }, text, anchor) => { entry.text = flat(entry.text.replace(anchor, () => text)).trim(); },
  In: ({ entry }, text) => { entry.text = `${entry.text} ${text}`; },
};

// Applies one project playbook's changes to the routed playbook's items. Returns the problems, one per change that
// anchors on a step this route should have but the todo no longer does, or on text no extended playbook has.
export function applyChanges(items, playbook, routed, bundled = BUNDLED) {
  const problems = [];
  if (!playbook.extends.includes(routed)) return problems;
  const routedText = flat(bundledPlaybook(routed, bundled) ?? "");
  const others = playbook.extends.filter((stem) => stem !== routed).map((stem) => flat(bundledPlaybook(stem, bundled) ?? ""));
  for (const change of playbook.changes) {
    const anchor = flat(change.anchor);
    const hits = locate(items, anchor);
    if (hits.length === 1) APPLY[change.verb](hits[0], change.text, anchor);
    else if (hits.length > 1) problems.push(`${playbook.label}: "${change.anchor}" is in ${hits.length} items of ${routed}; quote more of the step`);
    else if (routedText.includes(anchor)) problems.push(`${playbook.label}: "${change.anchor}" is in ${routed}.md but in no item of the todo: an earlier change replaced it, or it sits outside the numbered steps`);
    else if (!others.some((text) => text.includes(anchor))) problems.push(`${playbook.label}: "${change.anchor}" is not in any playbook it extends`);
  }
  return problems;
}

function render(items, depth = 0) {
  return items.flatMap((entry) => [
    `${"  ".repeat(depth)}- [${entry.done ? "x" : " "}] ${entry.text}`,
    ...render(entry.children, depth + 1),
  ]);
}

export function stemOf(name) {
  return name.trim().toLowerCase().replace(/\s+/g, "-");
}

// { text, problems }: the todo.md text, or the problems that stop it from being written.
export function generate({ playbook, root, landing, start = "", done = [], implement = IMPLEMENT, bundled = BUNDLED }) {
  const routed = stemOf(playbook);
  const overlay = readProjectPlaybook(join(implement, ".agents/playbooks/implement.md"), ".agents/playbooks/implement.md");
  const problems = [...checkPlaybooks(root, bundled), ...checkPlaybooks(implement, bundled)];
  const source = bundledPlaybook(routed, bundled);
  if (source === null) problems.push(`${routed}: this pstack has no such playbook`);
  else if (!overlay.extends.includes(routed)) problems.push(`${routed}: the Overlay does not extend it; /implement routes only to ${overlay.extends.join(", ")}`);
  if (!LANDING_ITEMS[landing]) problems.push(`--landing must be worktree or in-place, not "${landing}"`);
  if (landing === "in-place" && !start) problems.push("--landing in-place needs --start <sha>");
  if (problems.length > 0) return { text: "", problems };

  const { title, steps, prose } = parseSteps(source);
  const projectDir = join(root, ".agents/playbooks");
  const projectPlaybooks = existsSync(projectDir)
    ? readdirSync(projectDir).filter((name) => name.endsWith(".md")).sort()
      .map((name) => readProjectPlaybook(join(projectDir, name), `.agents/playbooks/${name}`))
    : [];
  for (const project of [...projectPlaybooks, overlay]) problems.push(...applyChanges(steps, project, routed, bundled));
  if (problems.length > 0) return { text: "", problems };

  const header = [`Playbook: ${title}`, `Landing: ${landing}`, ...(landing === "in-place" ? [`Start: ${start}`] : [])];
  const runItems = done.map((text) => ({ ...item(text), done: true }));
  const lines = [
    ...header,
    "",
    ...render(runItems),
    ...render(steps),
    ...render(GATES.map(item)),
    "",
    "## Landing",
    "",
    ...render(LANDING_ITEMS[landing].map(item)),
    "",
    "## Playbook",
    "",
    prose,
  ];
  return { text: `${lines.join("\n")}\n`, problems: [] };
}

function parseArgs(argv) {
  const args = { playbook: "", root: "", landing: "", start: "", done: [] };
  const rest = [...argv];
  while (rest.length > 0) {
    const arg = rest.shift();
    if (arg === "--root") args.root = rest.shift() ?? "";
    else if (arg === "--landing") args.landing = rest.shift() ?? "";
    else if (arg === "--start") args.start = rest.shift() ?? "";
    else if (arg === "--done") args.done.push(rest.shift() ?? "");
    else if (arg.startsWith("--")) return { error: `unknown option ${arg}` };
    else if (!args.playbook) args.playbook = arg;
    else return { error: `unexpected argument ${arg}` };
  }
  if (!args.playbook || !args.root || !args.landing) return { error: "usage: open-todo.mjs <playbook> --root <consuming repo> --landing worktree|in-place [--start <sha>] [--done \"<run item>\"]..." };
  if (args.landing === "in-place" && !args.start) return { error: "--landing in-place needs --start <sha>" };
  if (args.done.some((text) => !text.trim())) return { error: "--done needs the run item's text" };
  return { args: { ...args, root: resolve(args.root) } };
}

// node leaves argv[1] unresolved and may set it to a non-file (`node -e ... arg`).
function invokedDirectly() {
  if (!process.argv[1]) return false;
  try {
    return fileURLToPath(import.meta.url) === realpathSync(process.argv[1]);
  } catch {
    return false;
  }
}

if (invokedDirectly()) {
  const { args, error } = parseArgs(process.argv.slice(2));
  if (error) {
    console.error(error);
    process.exit(2);
  }
  const { text, problems } = generate(args);
  if (problems.length > 0) {
    console.error(problems.join("\n"));
    process.exit(1);
  }
  process.stdout.write(text);
}
