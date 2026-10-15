// node --test skills/implement/scripts/
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import { parseChecklist } from "./check-run.mjs";

const SCRIPT = join(dirname(fileURLToPath(import.meta.url)), "check-run.mjs");

function run(text) {
  const path = join(mkdtempSync(join(tmpdir(), "check-run-")), "todo.md");
  writeFileSync(path, text);
  const result = spawnSync(process.execPath, [SCRIPT, path], { encoding: "utf8" });
  return { status: result.status, stdout: result.stdout.trim(), stderr: result.stderr.trim(), path };
}

const DONE = `Playbook: Feature
Landing: in-place
Start: 0123abcd

- [x] Claimed the Issue #7
- [x] 1. \`how\` over the affected subsystem.
- [ ] 2. \`architect\` for parallel design exploration.
  skip: the Spec's Implementation Decisions fix the shape (greet() returns a string) and it touches greet.py and its test
- [x] 3. Write the throughput checkpoint as four todo items:
  - [x] **Blocking first steps.** Gates run before fan-out.
  - [ ] **Independent workstreams.** Disjoint files, services, or layers parallelize.
    n/a: one file
- [x] Design gate: a trail row names the data shape.

## Landing

- [ ] \`check-run.mjs\` exits 0
- [ ] Push
`;

test("a todo with every item done or skipped passes and the landing section is not read", () => {
  const { status, stdout, path } = run(DONE);
  assert.equal(status, 0);
  assert.equal(stdout, `${path}: every item above ## Landing is done or skipped (7 items).`);
  assert.deepEqual(parseChecklist(DONE), { items: 7, open: [], problems: [] });
});

test("an open item is printed and fails the gate", () => {
  const text = DONE.replace("- [x] Claimed the Issue #7", "- [ ] Claimed the Issue #7");
  const { status, stderr } = run(text);
  assert.equal(status, 1);
  assert.equal(stderr, "- [ ] Claimed the Issue #7");
});

test("a skip or n/a line must sit right under its item", () => {
  const { open, problems } = parseChecklist("- [ ] 1. first\n  skip: not needed\n- [ ] 2. second\n\n  n/a: late\n- [ ] 3. third\n  n/a: no fan-out\n");
  assert.deepEqual(open, ["- [ ] 2. second"]);
  assert.deepEqual(problems, ["line 5 is a n/a line with no item above it: n/a: late"]);
  assert.deepEqual(parseChecklist("- [x] 1. first\n  skip: done anyway\n"), { items: 1, open: [], problems: [] });
});

test("a paraphrased line that is not an item fails as not a checklist line", () => {
  const text = DONE.replace("- [x] 1. `how` over the affected subsystem.", "Run how over the subsystem (done)");
  const { status, stderr } = run(text);
  assert.equal(status, 1);
  assert.equal(stderr, "line 6 is not a checklist line: Run how over the subsystem (done)");
  assert.deepEqual(parseChecklist("- [x] 1. a\n- [x] 2a. invented sub-step\n- [x]\n").problems, ["line 3 is not a checklist line: - [x]"]);
});

test("BLOCKED counts only at the start of a line", () => {
  const blocked = DONE.replace("- [x] Design gate: a trail row names the data shape.", "- [x] Design gate: a trail row names the data shape.\nBLOCKED: independent review");
  assert.deepEqual(parseChecklist(blocked).open, ["BLOCKED: independent review"]);
  assert.equal(run(blocked).stderr, "BLOCKED: independent review");
  const mention = DONE.replace("- [x] Design gate: a trail row names the data shape.", "- [x] Review gate: no reviewer missing, so no BLOCKED: line was written.");
  assert.deepEqual(parseChecklist(mention), { items: 7, open: [], problems: [] });
});

test("an empty checklist and a missing file are errors", () => {
  assert.deepEqual(parseChecklist("Playbook: Feature\n\n## Landing\n\n- [ ] Push\n").problems, ["no checklist item found"]);
  const missing = spawnSync(process.execPath, [SCRIPT, join(tmpdir(), "no-such-todo.md")], { encoding: "utf8" });
  assert.equal(missing.status, 2);
});
