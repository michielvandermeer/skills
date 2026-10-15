#!/usr/bin/env node
// The landing gate of an /implement run: exit 0 only when every line of todo.md above `## Landing` is a header line,
// a done item, or an item with a `skip:` or `n/a:` line under it, and no `BLOCKED:` line is there.
// Usage: node check-run.mjs <path to todo.md>
import { readFileSync, realpathSync } from "node:fs";
import process from "node:process";
import { fileURLToPath } from "node:url";

const HEADER = /^(Playbook|Landing|Start|Landed): \S/;
const ITEM = /^\s*- \[([ xX])\] \S/;
const NOTE = /^\s+(skip|n\/a): \S/;
const BLOCKED = /^BLOCKED:/;
const LANDING = /^## Landing\s*$/;

// { items, open, problems }: the checklist above `## Landing`, its open lines, and the lines outside the grammar.
export function parseChecklist(text) {
  const result = { items: 0, open: [], problems: [] };
  let pending = null;
  let last = null;
  const settle = () => {
    if (pending) result.open.push(pending);
    pending = null;
  };
  const lines = text.replace(/^﻿/, "").split(/\r?\n/);
  for (let n = 0; n < lines.length; n++) {
    const line = lines[n];
    if (LANDING.test(line)) break;
    const noteOf = line.match(NOTE);
    if (noteOf) {
      if (!last) result.problems.push(`line ${n + 1} is a ${noteOf[1]} line with no item above it: ${line.trim()}`);
      pending = null;
      last = null;
      continue;
    }
    settle();
    last = null;
    if (line.trim() === "" || HEADER.test(line)) continue;
    if (BLOCKED.test(line)) {
      result.open.push(line.trim());
      continue;
    }
    const itemOf = line.match(ITEM);
    if (!itemOf) {
      result.problems.push(`line ${n + 1} is not a checklist line: ${line.trim()}`);
      continue;
    }
    result.items += 1;
    last = line;
    if (itemOf[1] === " ") pending = line.trim();
  }
  settle();
  if (result.items === 0) result.problems.push("no checklist item found");
  return result;
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
  const path = process.argv[2];
  if (!path) {
    console.error("usage: check-run.mjs <path to todo.md>");
    process.exit(2);
  }
  let text;
  try {
    text = readFileSync(path, "utf8");
  } catch (error) {
    console.error(`${path}: ${error.message}`);
    process.exit(2);
  }
  const { items, open, problems } = parseChecklist(text);
  if (problems.length > 0 || open.length > 0) {
    console.error([...problems, ...open].join("\n"));
    process.exit(1);
  }
  console.log(`${path}: every item above ## Landing is done or skipped (${items} items).`);
}
