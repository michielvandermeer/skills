import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import { INTERROGATE_HEADINGS, checkRun, parseTodo } from "./check-run.mjs";
import { generate } from "./open-todo.mjs";

const SCRIPT = join(dirname(fileURLToPath(import.meta.url)), "check-run.mjs");
const TRAIL = "ts\tphase\tdecision\twhy\tevidence\tresult\n";
const ROW = (phase) => `2026-10-15T00:00:00Z\t${phase}\tdone\tbecause\tpath\tpass\n`;
const GATE_ROWS = TRAIL + ROW("design gate") + ROW("review gate") + ROW("verification gate");
const VERDICT = INTERROGATE_HEADINGS.map((heading) => `### ${heading}\n\ntext\n`).join("\n");
const ARCHITECT_SKIP = "- [x] 2. `architect` for parallel design exploration. Its candidates write under the Run directory, never the worktree (`/implement` step 5, One writer).";

function runDir({ playbook = "feature", landing = "worktree", start = "", edit = (text) => text, files = {} } = {}) {
  const root = mkdtempSync(join(tmpdir(), "check-run-"));
  const dir = join(root, ".agents/runs/slug");
  mkdirSync(join(dir, "evidence"), { recursive: true });
  const done = ["Claimed the Issue #7", "Entered the run worktree", "Wrote spec.md"];
  const { text, problems } = generate({ playbook, root, landing, start, done });
  assert.deepEqual(problems, []);
  writeFileSync(join(dir, "todo.md"), edit(text));
  for (const [name, body] of Object.entries(files)) writeFileSync(join(dir, name), body);
  return dir;
}

const tickedAboveLanding = (text) => text
  .replaceAll("- [ ] ", "- [x] ")
  .replace(/^(## Landing[\s\S]*)$/m, (section) => section.replaceAll("- [x] ", "- [ ] "));

function landed(overrides = {}) {
  return runDir({
    edit: (text) => tickedAboveLanding(text).replace(ARCHITECT_SKIP, `${ARCHITECT_SKIP}\n  skip: the Spec fixes the shape`),
    files: { "trail.tsv": GATE_ROWS, "evidence/interrogate.md": VERDICT },
    ...overrides,
  });
}

function run(dir) {
  const result = spawnSync(process.execPath, [SCRIPT, dir], { encoding: "utf8" });
  return { status: result.status, stdout: result.stdout.trim(), stderr: result.stderr.trim() };
}

const lineOf = (text, needle) => text.slice(0, text.indexOf(needle)).split("\n").length;

function clean(...dirs) {
  for (const dir of dirs) rmSync(dir, { recursive: true, force: true });
}

test("a run that may land passes, and the landing section's open items do not count", () => {
  const dir = landed();
  const { status, stdout } = run(dir);
  assert.equal(status, 0, stdout);
  assert.match(stdout, /every item above ## Landing is done or skipped \(18 items\)/);
  assert.deepEqual(checkRun(dir).problems, []);
  clean(dir);
});

test("a fresh todo fails only on its open items, children on their own lines, so step 4 can check it", () => {
  const dir = runDir();
  const problems = checkRun(dir).problems;
  assert.equal(problems.length, 15);
  assert.ok(problems.every((line) => line.startsWith("- [ ] ") || line.startsWith("  - [ ] ")), problems.join("\n"));
  assert.ok(problems.includes("  - [ ] **Smallest safe decomposition.** If one worker is best, name why."));
  assert.equal(run(dir).status, 1);
  clean(dir);
});

test("a skip or n/a line must sit right under its item, and attaches to a child when the child is last", () => {
  const todo = parseTodo("- [ ] 1. first\n  skip: not needed\n- [ ] 2. second\n\n  n/a: late\n- [ ] 3. third\n  - [ ] **Child.** one\n  n/a: no fan-out\n");
  assert.deepEqual(todo.checklist.map((item) => [item.text, item.note]), [["1. first", "skip"], ["2. second", null], ["3. third", null], ["**Child.** one", "n/a"]]);
  assert.deepEqual(todo.problems, ["line 5 is a n/a line with no item above it: n/a: late"]);
});

test("a reworded step, a cut step, a reworded child, and a paraphrased line fail against open-todo.mjs, naming the line", () => {
  const reworded = runDir({ edit: (text) => text.replace("- [ ] 1. `how` over the affected subsystem.", "- [ ] 1. Run how over the subsystem") });
  assert.deepEqual(checkRun(reworded).problems.filter((line) => line.includes("differs")), ["line 7 differs from open-todo.mjs: 1. Run how over the subsystem"]);
  const cut = runDir({ edit: (text) => text.replace(/^- \[ \] 5\. Verify on the matching surface\..*\n/m, "") });
  assert.ok(checkRun(cut).problems.includes("todo.md has 14 step lines after its run items where open-todo.mjs generates 15"), checkRun(cut).problems.join("\n"));
  const cutFirst = runDir({ edit: (text) => text.replace("- [ ] 1. `how` over the affected subsystem.\n", "") });
  assert.ok(checkRun(cutFirst).problems.includes("line 6 differs from open-todo.mjs: Wrote spec.md"), checkRun(cutFirst).problems.join("\n"));
  const child = runDir({ edit: (text) => text.replace("  - [ ] **Smallest safe decomposition.** If one worker is best, name why.", "  - [ ] **Smallest safe decomposition.** One worker.") });
  assert.ok(checkRun(child).problems.some((line) => line.endsWith("differs from open-todo.mjs: **Smallest safe decomposition.** One worker.")), checkRun(child).problems.join("\n"));
  const paraphrased = runDir({ edit: (text) => text.replace("- [ ] 1. `how` over the affected subsystem.", "Run how over the subsystem (done)") });
  assert.ok(checkRun(paraphrased).problems.includes("line 7 is not a checklist line: Run how over the subsystem (done)"));
  clean(reworded, cut, cutFirst, child, paraphrased);
});

test("a changed landing item or a missing or changed ## Playbook section fails", () => {
  const landing = runDir({ edit: (text) => text.replace("- [ ] Push (LANDING.md, The push)", "- [ ] Push it (LANDING.md, The push)") });
  assert.ok(checkRun(landing).problems.some((line) => line.endsWith("differs from open-todo.mjs: Push it (LANDING.md, The push)")));
  const missing = runDir({ edit: (text) => text.slice(0, text.indexOf("## Playbook")) });
  assert.ok(checkRun(missing).problems.includes("## Playbook section is missing: open-todo.mjs writes the playbook's own prose there"));
  const changed = runDir({ edit: (text) => text.replace("**You own the design.", "**You own the code.") });
  assert.ok(checkRun(changed).problems.includes("## Playbook section differs from what open-todo.mjs writes"));
  clean(landing, missing, changed);
});

test("BLOCKED: fails anywhere in the file, including as a note under the Review gate", () => {
  let written = "";
  const under = runDir({ edit: (text) => (written = text.replace(/^(- \[ \] Review gate:.*)$/m, "$1\n  BLOCKED: independent review")) });
  assert.ok(checkRun(under).problems.includes(`line ${lineOf(written, "  BLOCKED:")}: BLOCKED: independent review`), checkRun(under).problems.join("\n"));
  assert.ok(!checkRun(under).problems.some((line) => line.includes("no item above it")), "an indented BLOCKED: line is a note, not a stray line");
  const mention = runDir({ edit: (text) => (written = text.replace("## Playbook", "## Playbook\n\nNo BLOCKED: line was written.")) });
  assert.ok(checkRun(mention).problems.includes(`line ${lineOf(written, "No BLOCKED")}: No BLOCKED: line was written.`), checkRun(mention).problems.join("\n"));
  clean(under, mention);
});

test("a note under a gate fails, and a note under a landing item fails unless it is push or retro", () => {
  const skippedGate = runDir({ edit: (text) => text.replace(/^(- \[ \] Design gate:.*)$/m, "$1\n  skip: small change") });
  assert.ok(checkRun(skippedGate).problems.some((line) => line.startsWith("a skip note under a gate, which cannot be skipped: Design gate:")), checkRun(skippedGate).problems.join("\n"));
  const landingNotes = runDir({ edit: (text) => text
    .replace("- [ ] Push (LANDING.md, The push)", "- [ ] Push (LANDING.md, The push)\n  skip: no remote")
    .replace("- [ ] Retro (`/implement` step 8)", "- [ ] Retro (`/implement` step 8)\n  skip: nothing went wrong")
    .replace("- [ ] Landing commit (LANDING.md, The landing commit)", "- [ ] Landing commit (LANDING.md, The landing commit)\n  n/a: landed by hand") });
  const problems = checkRun(landingNotes).problems.filter((line) => line.includes("landing item"));
  assert.deepEqual(problems, ["a n/a note under a landing item only push and retro may carry: Landing commit (LANDING.md, The landing commit)"]);
  clean(skippedGate, landingNotes);
});

test("a checked gate needs a trail row whose phase is the gate's name in lowercase", () => {
  const dir = landed({ files: { "trail.tsv": TRAIL + ROW("design") + ROW("review gate") + ROW("verify"), "evidence/interrogate.md": VERDICT } });
  assert.deepEqual(checkRun(dir).problems, [
    'Design gate is checked but trail.tsv has no row with phase "design gate"',
    'Verification gate is checked but trail.tsv has no row with phase "verification gate"',
  ]);
  rmSync(join(dir, "trail.tsv"));
  assert.deepEqual(checkRun(dir).problems, ["trail.tsv is missing, so no gate has its trail row"]);
  clean(dir);
});

test("a checked Review gate needs evidence/interrogate.md with interrogate's seven headings", () => {
  const dir = landed();
  rmSync(join(dir, "evidence/interrogate.md"));
  assert.deepEqual(checkRun(dir).problems, ["Review gate is checked but evidence/interrogate.md is missing"]);
  writeFileSync(join(dir, "evidence/interrogate.md"), VERDICT.replace("### Consider", "### Considered").replace("### Agreement Map", "## Agreement"));
  assert.deepEqual(checkRun(dir).problems, ["Review gate is checked but evidence/interrogate.md lacks the headings: Consider, Agreement Map"]);
  writeFileSync(join(dir, "evidence/interrogate.md"), VERDICT.replaceAll("### ", "## "));
  assert.deepEqual(checkRun(dir).problems, [], "any heading level counts");
  clean(dir);
});

test("a Bug fix with its Design gate checked needs evidence/repro-red.txt", () => {
  const edit = (text) => tickedAboveLanding(text).replace(/^(- \[x\] 3\. Plan the fix\..*)$/m, "$1\n  skip: the fix stays inside one function, so no architect");
  const dir = runDir({ playbook: "bug-fix", edit, files: { "trail.tsv": GATE_ROWS, "evidence/interrogate.md": VERDICT } });
  assert.deepEqual(checkRun(dir).problems, ["Design gate is checked on a Bug fix but evidence/repro-red.txt is missing or empty"]);
  writeFileSync(join(dir, "evidence/repro-red.txt"), "AssertionError: 'release-notes' != 'release-2-notes'\nFAILED (failures=1)\n");
  assert.deepEqual(checkRun(dir).problems, []);
  clean(dir);
});

test("a checked Design gate needs design.md unless an architect step carries a skip note", () => {
  const feature = landed({ edit: tickedAboveLanding });
  assert.deepEqual(checkRun(feature).problems, ["Design gate is checked but design.md is missing and no architect step carries a skip note: step 2"]);
  writeFileSync(join(feature, "design.md"), "# Design\n");
  assert.deepEqual(checkRun(feature).problems, []);
  const bug = runDir({ playbook: "bug-fix", edit: tickedAboveLanding, files: { "trail.tsv": GATE_ROWS, "evidence/interrogate.md": VERDICT, "evidence/repro-red.txt": "red\n" } });
  assert.deepEqual(checkRun(bug).problems, ["Design gate is checked but design.md is missing and no architect step carries a skip note: step 3"], "step 2's bare mention of architect is not an architect step");
  clean(feature, bug);
});

test("the in-place shape regenerates from its Start: header", () => {
  const dir = runDir({ landing: "in-place", start: "0123abcd" });
  assert.ok(checkRun(dir).problems.every((line) => line.startsWith("- [ ] ") || line.startsWith("  - [ ] ")), checkRun(dir).problems.join("\n"));
  clean(dir);
});

test("a directory outside .agents/runs, a missing todo.md, and an empty checklist are errors", () => {
  const outside = mkdtempSync(join(tmpdir(), "check-run-outside-"));
  writeFileSync(join(outside, "todo.md"), "Playbook: Feature\n");
  assert.equal(run(outside).status, 2);
  assert.match(run(outside).stderr, /is not <repository root>\/.agents\/runs\/<slug>/);
  const empty = runDir({ edit: () => "Playbook: Feature\nLanding: worktree\n\n## Landing\n\n- [ ] Push (LANDING.md, The push)\n" });
  assert.ok(checkRun(empty).problems.includes("no checklist item found"));
  assert.equal(run(empty).status, 1);
  rmSync(join(empty, "todo.md"));
  assert.equal(run(empty).status, 2);
  assert.equal(spawnSync(process.execPath, [SCRIPT], { encoding: "utf8" }).status, 2);
  clean(outside, empty);
});
