#!/usr/bin/env node
// The landing gate of an /implement run: exit 0 only when todo.md has no open item and no closed gate.
// Usage: node check-run.mjs <path to todo.md>
import { readFileSync } from "node:fs";
import process from "node:process";

const ITEM = /^\s*[-*]\s+\[([ xX])\]\s*(.*)$/;
const SKIP = /\bskip:\s*\S/;
const BLOCKED = /\bBLOCKED:/;

export function openLines(text) {
  const open = [];
  let items = 0;
  for (const line of text.replace(/^﻿/, "").split(/\r?\n/)) {
    if (BLOCKED.test(line)) {
      open.push(line.trim());
      continue;
    }
    const item = line.match(ITEM);
    if (!item) continue;
    items += 1;
    if (item[1] === " " && !SKIP.test(item[2])) open.push(line.trim());
  }
  return { open, items };
}

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
const { open, items } = openLines(text);
if (items === 0) {
  console.error(`${path}: no checklist item found`);
  process.exit(1);
}
if (open.length > 0) {
  console.error(open.join("\n"));
  process.exit(1);
}
console.log(`${path}: every item is done or skipped (${items} items).`);
