#!/usr/bin/env node
// The landing gate of an /implement run: exit 0 only when the Run directory shows a run that may land.
// Usage: node check-run.mjs <run directory>
// It reads todo.md, trail.tsv, design.md, and evidence/ there and prints one line per failure:
// - a todo.md line that is not a header, an item, a `skip:`, `n/a:`, or `BLOCKED:` note, or a section heading;
// - an open item above `## Landing`;
// - `BLOCKED:` anywhere in todo.md;
// - a note under a gate item, or under a landing item other than push and retro;
// - a step, gate, landing, or `## Playbook` line that differs from what open-todo.mjs generates for the file's own
//   `Playbook:`, `Landing:`, and `Start:` headers and the repository root above `.agents/runs/<slug>/`;
// - a checked gate with no trail.tsv row whose phase is the gate's name in lowercase;
// - a checked Review gate without evidence/interrogate.md holding interrogate's seven headings;
// - a checked Design gate on a Bug fix without evidence/repro-red.txt;
// - a checked Design gate with design.md missing while no `architect` step carries a note.
import { existsSync, readFileSync, realpathSync, statSync } from "node:fs";
import { basename, dirname, join, resolve } from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";
import { GATE_NAMES, generate } from "./open-todo.mjs";

const HEADER = /^(Playbook|Landing|Start|Landed): (\S.*)$/;
const ITEM = /^(\s*)- \[([ xX])\] (\S.*)$/;
const NOTE = /^\s+(skip|n\/a|BLOCKED): \S/;
const SECTION = /^## (Landing|Playbook)\s*$/;
export const INTERROGATE_HEADINGS = ["Intent", "Reviewers", "Act On", "Consider", "Noted", "Dismissed", "Agreement Map"];
const SKIPPABLE_LANDING = /^(Push|Retro) \(/;
const ARCHITECT = /`architect`|\*\*architect\*\*/;

export function parseTodo(text) {
  const todo = { header: {}, checklist: [], landing: [], playbook: null, problems: [], blocked: [] };
  const playbookLines = [];
  let section = "checklist";
  let last = null;
  const lines = text.replace(/^﻿/, "").split(/\r?\n/);
  for (let n = 0; n < lines.length; n++) {
    const line = lines[n];
    const at = n + 1;
    if (line.includes("BLOCKED:")) todo.blocked.push(`line ${at}: ${line.trim()}`);
    const heading = line.match(SECTION);
    if (heading) {
      section = heading[1].toLowerCase();
      last = null;
      continue;
    }
    if (section === "playbook") {
      playbookLines.push(line.trimEnd());
      continue;
    }
    const noteOf = line.match(NOTE);
    if (noteOf) {
      if (last) last.note = noteOf[1];
      else todo.problems.push(`line ${at} is a ${noteOf[1]} line with no item above it: ${line.trim()}`);
      last = null;
      continue;
    }
    last = null;
    if (line.trim() === "") continue;
    const headerOf = line.match(HEADER);
    if (headerOf) {
      todo.header[headerOf[1].toLowerCase()] = headerOf[2].trim();
      continue;
    }
    const itemOf = line.match(ITEM);
    if (!itemOf) {
      todo.problems.push(`line ${at} is not a checklist line: ${line.trim()}`);
      continue;
    }
    last = { at, indent: itemOf[1], done: itemOf[2] !== " ", text: itemOf[3].trim(), note: null };
    todo[section].push(last);
  }
  if (section === "playbook") todo.playbook = playbookLines.join("\n").trim();
  if (todo.checklist.length === 0) todo.problems.push("no checklist item found");
  return todo;
}

const isGate = (item) => item.indent === "" && GATE_NAMES.some((name) => item.text.startsWith(`${name}:`));
const gateOf = (item) => GATE_NAMES.find((name) => item.text.startsWith(`${name}:`));
const shape = (item) => `${item.indent}- ${item.text}`;
const stepName = (item) => (item.text.match(/^\d+\./) ? `step ${item.text.match(/^(\d+)\./)[1]}` : item.text);
const read = (path) => (existsSync(path) ? readFileSync(path, "utf8") : null);

function trailPhases(runDir) {
  const text = read(join(runDir, "trail.tsv"));
  if (text === null) return null;
  return new Set(text.split(/\r?\n/).slice(1).map((row) => row.split("\t")[1]?.trim().toLowerCase()).filter(Boolean));
}

function firstGeneratedIndexAfterRunItems(checklist, generatedChecklist) {
  const found = checklist.findIndex((item) => shape(item) === shape(generatedChecklist[0]));
  return found >= 0 ? found : checklist.length - generatedChecklist.length;
}

function linesDifferingFromGenerated(todo, root) {
  const { playbook, landing, start = "" } = todo.header;
  if (!playbook || !landing) return [`todo.md needs a Playbook: and a Landing: header line to compare against open-todo.mjs`];
  const expected = generate({ playbook, root, landing, start, done: [] });
  if (expected.problems.length > 0) return expected.problems.map((problem) => `open-todo.mjs: ${problem}`);
  const generated = parseTodo(expected.text);
  const problems = [];
  const first = firstGeneratedIndexAfterRunItems(todo.checklist, generated.checklist);
  if (first < 0) {
    problems.push(`todo.md has ${todo.checklist.length} checklist lines where open-todo.mjs generates ${generated.checklist.length} after the run items`);
  } else {
    const have = todo.checklist.slice(first);
    generated.checklist.slice(0, have.length).forEach((want, index) => {
      if (shape(have[index]) !== shape(want)) problems.push(`line ${have[index].at} differs from open-todo.mjs: ${have[index].text}`);
    });
    if (have.length !== generated.checklist.length) {
      problems.push(`todo.md has ${have.length} step lines after its run items where open-todo.mjs generates ${generated.checklist.length}`);
    }
  }
  if (todo.landing.length !== generated.landing.length) {
    problems.push(`## Landing has ${todo.landing.length} items where open-todo.mjs generates ${generated.landing.length}`);
  } else {
    generated.landing.forEach((want, index) => {
      const have = todo.landing[index];
      if (shape(have) !== shape(want)) problems.push(`line ${have.at} differs from open-todo.mjs: ${have.text}`);
    });
  }
  if (todo.playbook === null) problems.push("## Playbook section is missing: open-todo.mjs writes the playbook's own prose there");
  else if (todo.playbook !== generated.playbook) problems.push("## Playbook section differs from what open-todo.mjs writes");
  return problems;
}

const RULES = [
  ({ todo }) => todo.problems,
  ({ todo }) => todo.blocked,
  ({ todo }) => todo.checklist.filter((item) => !item.done && !item.note).map((item) => `${item.indent}- [ ] ${item.text}`),
  ({ todo }) => todo.checklist.filter((item) => isGate(item) && item.note).map((item) => `a ${item.note} note under a gate, which cannot be skipped: ${item.text}`),
  ({ todo }) => todo.landing.filter((item) => item.note && !SKIPPABLE_LANDING.test(item.text))
    .map((item) => `a ${item.note} note under a landing item only push and retro may carry: ${item.text}`),
  ({ todo, root }) => linesDifferingFromGenerated(todo, root),
  ({ todo, runDir }) => {
    const checked = todo.checklist.filter((item) => isGate(item) && item.done);
    if (checked.length === 0) return [];
    const phases = trailPhases(runDir);
    if (phases === null) return ["trail.tsv is missing, so no gate has its trail row"];
    return checked.filter((item) => !phases.has(gateOf(item).toLowerCase()))
      .map((item) => `${gateOf(item)} is checked but trail.tsv has no row with phase "${gateOf(item).toLowerCase()}"`);
  },
  ({ todo, runDir }) => {
    if (!todo.checklist.some((item) => isGate(item) && item.done && gateOf(item) === "Review gate")) return [];
    const verdict = read(join(runDir, "evidence/interrogate.md"));
    if (verdict === null) return ["Review gate is checked but evidence/interrogate.md is missing"];
    const missing = INTERROGATE_HEADINGS.filter((heading) => !new RegExp(`^#+\\s+${heading}\\s*$`, "m").test(verdict));
    return missing.length > 0 ? [`Review gate is checked but evidence/interrogate.md lacks the headings: ${missing.join(", ")}`] : [];
  },
  ({ todo, runDir }) => {
    if (!todo.checklist.some((item) => isGate(item) && item.done && gateOf(item) === "Design gate")) return [];
    const problems = [];
    if (todo.header.playbook === "Bug fix" && !(read(join(runDir, "evidence/repro-red.txt")) ?? "").trim()) {
      problems.push("Design gate is checked on a Bug fix but evidence/repro-red.txt is missing or empty");
    }
    const architect = todo.checklist.filter((item) => !isGate(item) && ARCHITECT.test(item.text));
    if (architect.length > 0 && !architect.some((item) => item.note) && !existsSync(join(runDir, "design.md"))) {
      problems.push(`Design gate is checked but design.md is missing and no architect step carries a skip note: ${architect.map(stepName).join(", ")}`);
    }
    return problems;
  },
];

export function checkRun(runDir) {
  runDir = resolve(runDir);
  const todoPath = join(runDir, "todo.md");
  if (!statSync(runDir, { throwIfNoEntry: false })?.isDirectory()) return { usageError: `${runDir} is not a directory`, problems: [], items: 0 };
  const text = read(todoPath);
  if (text === null) return { usageError: `${todoPath} is missing`, problems: [], items: 0 };
  if (basename(dirname(runDir)) !== "runs" || basename(dirname(dirname(runDir))) !== ".agents") {
    return { usageError: `${runDir} is not <repository root>/.agents/runs/<slug>, so open-todo.mjs has no root to generate from`, problems: [], items: 0 };
  }
  const run = { todo: parseTodo(text), runDir, root: dirname(dirname(dirname(runDir))) };
  return { usageError: null, problems: RULES.flatMap((rule) => rule(run)), items: run.todo.checklist.length };
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
  const runDir = process.argv[2];
  if (!runDir) {
    console.error("usage: check-run.mjs <run directory>");
    process.exit(2);
  }
  const { usageError, problems, items } = checkRun(runDir);
  if (usageError) {
    console.error(usageError);
    process.exit(2);
  }
  if (problems.length > 0) {
    console.error(problems.join("\n"));
    process.exit(1);
  }
  console.log(`${resolve(runDir)}: every item above ## Landing is done or skipped (${items} items), every line matches open-todo.mjs, and each checked gate has its evidence.`);
}
