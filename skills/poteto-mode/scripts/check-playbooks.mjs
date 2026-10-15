#!/usr/bin/env node
import { existsSync, readdirSync, readFileSync, realpathSync, statSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

export const BUNDLED = resolve(dirname(fileURLToPath(import.meta.url)), "../playbooks");
const CHANGE = /^\s*(?:[-*]|\d+\.)\s+\*\*(After|Before|Replace|In)\*\*\s+"((?:[^"\\]|\\.)+)"\s*(.*)$/;
const CHANGE_VERB = /^\s*(?:[-*]|\d+\.)\s+\*\*(?:After|Before|Replace|In)\*\*/;
export const flat = (text) => text.replace(/\s+/g, " ");

export function bundledPlaybook(stem, bundled = BUNDLED) {
  const file = join(bundled, `${stem}.md`);
  return !/[\\/]/.test(stem) && existsSync(file) ? readFileSync(file, "utf8") : null;
}

export function readProjectPlaybook(file, label = file) {
  const text = readFileSync(file, "utf8").replace(/^﻿/, "").replaceAll("\r\n", "\n");
  const front = text.match(/^---\n([\s\S]*?)\n---\n/)?.[1] ?? "";
  const field = (key) => front.match(new RegExp(`^${key}:[ \\t]*(.*)$`, "m"))?.[1].trim() ?? "";
  const problems = [];
  if (!field("when")) problems.push(`${label}: its frontmatter needs a "when:" line`);
  const changes = [];
  for (const line of text.split("\n")) {
    const change = line.match(CHANGE);
    if (change) changes.push({ verb: change[1], anchor: change[2].replace(/\\(.)/g, "$1"), text: change[3].trim() });
    else if (CHANGE_VERB.test(line)) {
      problems.push(`${label}: a change has no straight-quoted step text to anchor on: ${line.trim().slice(0, 80)}`);
    }
  }
  const extendsStems = field("extends").split(",").map((stem) => stem.trim()).filter(Boolean);
  return { label, when: field("when"), extends: extendsStems, changes, problems };
}

export function checkPlaybooks(root, bundled = BUNDLED) {
  const dir = join(root, ".agents/playbooks");
  if (!existsSync(dir)) return [];
  const problems = [];
  for (const name of readdirSync(dir).filter((file) => file.endsWith(".md")).sort()) {
    const playbook = readProjectPlaybook(join(dir, name), `.agents/playbooks/${name}`);
    problems.push(...playbook.problems);
    const bases = playbook.extends.map((stem) => ({ stem, text: bundledPlaybook(stem, bundled) }));
    for (const base of bases) {
      if (base.text === null) problems.push(`${playbook.label}: extends \`${base.stem}\`, which this pstack has no playbook for`);
    }
    for (const { anchor } of playbook.changes) {
      if (!bases.some((base) => base.text && flat(base.text).includes(flat(anchor)))) {
        problems.push(`${playbook.label}: "${anchor}" is not in any playbook it extends`);
      }
    }
  }
  return problems;
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
  const root = resolve(process.argv[2] ?? ".");
  const directory = join(root, ".agents/playbooks");
  const problems = statSync(root, { throwIfNoEntry: false })?.isDirectory()
    ? checkPlaybooks(root)
    : [`${root} is not a directory`];
  if (problems.length > 0) {
    console.error(problems.join("\n"));
    process.exitCode = 1;
  } else if (existsSync(directory)) {
    console.log("Every project playbook matches this pstack's playbooks.");
  } else {
    console.log(`No project playbooks to check: ${directory} does not exist.`);
  }
}
