// node --test skills/implement/scripts/
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import { bundledPlaybook, flat, readProjectPlaybook } from "../../poteto-mode/scripts/check-playbooks.mjs";
import { parseChecklist } from "./check-run.mjs";
import { GATES, IMPLEMENT, LANDING_ITEMS, generate, parseSteps } from "./open-todo.mjs";

const SCRIPT = join(dirname(fileURLToPath(import.meta.url)), "open-todo.mjs");
const OVERLAY = readProjectPlaybook(join(IMPLEMENT, ".agents/playbooks/implement.md"));
const ROUTES = ["feature", "bug-fix", "refactoring", "perf-issue", "visual-parity"];
const DONE = ["Claimed the Issue #7", "Entered the run worktree", "Wrote spec.md"];

function emptyRepo() {
  return mkdtempSync(join(tmpdir(), "open-todo-"));
}

function repoWithPlaybook(name, body) {
  const root = emptyRepo();
  mkdirSync(join(root, ".agents/playbooks"), { recursive: true });
  writeFileSync(join(root, ".agents/playbooks", name), body);
  return root;
}

function todo(playbook, root = emptyRepo(), landing = "worktree", start = "") {
  const { text, problems } = generate({ playbook, root, landing, start, done: DONE });
  assert.deepEqual(problems, []);
  return text;
}

function lines(text) {
  return text.split("\n");
}

for (const route of ROUTES) {
  test(`${route} generates a todo that check-run reads as all open and nothing else`, () => {
    const text = todo(route);
    const parsed = parseChecklist(text);
    assert.deepEqual(parsed.problems, []);
    const steps = parseSteps(bundledPlaybook(route)).steps;
    const gateLines = GATES.map((gate) => `- [ ] ${gate}`);
    assert.equal(parsed.items, DONE.length + parsed.open.length);
    assert.deepEqual(parsed.open.slice(-3), gateLines);
    assert.ok(parsed.open.length >= steps.length + 3, `${parsed.open.length} open lines for ${steps.length} steps`);
    assert.ok(lines(text).includes("## Landing"));
    assert.deepEqual(lines(text).slice(lines(text).indexOf("## Landing") + 2, -1), LANDING_ITEMS.worktree.map((entry) => `- [ ] ${entry}`));
  });
}

test("header and run items come first, in the worktree and in-place shapes", () => {
  assert.deepEqual(lines(todo("Bug fix")).slice(0, 6), [
    "Playbook: Bug fix", "Landing: worktree", "",
    "- [x] Claimed the Issue #7", "- [x] Entered the run worktree", "- [x] Wrote spec.md",
  ]);
  const inPlace = todo("bug-fix", emptyRepo(), "in-place", "0123abcd");
  assert.deepEqual(lines(inPlace).slice(0, 3), ["Playbook: Bug fix", "Landing: in-place", "Start: 0123abcd"]);
  assert.deepEqual(lines(inPlace).slice(lines(inPlace).indexOf("## Landing") + 2, -1), LANDING_ITEMS["in-place"].map((entry) => `- [ ] ${entry}`));
});

test("steps are the playbook's own words, one line each, sub-bullets as nested items", () => {
  const feature = lines(todo("feature"));
  assert.ok(feature.includes("- [ ] 2. `architect` for parallel design exploration."));
  assert.ok(feature.includes("- [ ] 5. Verify on the matching surface. \"Inconclusive\" or wrong-surface is not a pass. Flag it."));
  const checkpoint = feature.indexOf("- [ ] 3. Write the throughput checkpoint as four todo items. A dimension that genuinely does not apply (single file, no fan-out) keeps its item with `n/a: <reason>` rather than being dropped:");
  assert.ok(checkpoint > 0);
  assert.deepEqual(feature.slice(checkpoint + 1, checkpoint + 5), [
    "  - [ ] **Blocking first steps.** Gates run before fan-out.",
    "  - [ ] **Independent workstreams.** Disjoint files, services, or layers parallelize. Shared writes serialize.",
    "  - [ ] **Shared mutable state.** Default to splitting the target (the **separate-before-serializing-shared-state** principle skill). Serialize only for real invariants.",
    "  - [ ] **Smallest safe decomposition.** If one worker is best, name why.",
  ]);
  const perf = lines(todo("perf-issue"));
  assert.ok(perf.includes("- [ ] 2. `how` to ground hypotheses. Don't claim a perf ceiling without running it first. Try the performance mantras in order, cheapest first: 1. Don't do it. Stop work whose result nothing uses rather than cheapening it. 2. Do it, but don't do it again. 3. Do it less. 4. Do it later. 5. Do it when they're not looking. 6. Do it concurrently. 7. Do it cheaper. When an earlier mantra meets the target, stop."));
  const bug = lines(todo("bug-fix"));
  assert.ok(bug.includes("- [ ] 5. Stage the commits so the failing repro lands before the fix in git history. See the **tdd** skill for the failing-test-first cadence when the bug has a cheap local test path. Skip it when the test would be expensive, integration-heavy, or unclear. This is the canonical **sequence-verifiable-units** principle skill, the failing test first and the fix on top."));
});

test("every overlay change lands at its anchor on every route whose playbook has the anchor", () => {
  let applied = 0;
  for (const route of ROUTES) {
    const out = lines(todo(route));
    const source = flat(bundledPlaybook(route));
    const original = parseSteps(bundledPlaybook(route)).steps.map((step) => `- [ ] ${step.text}`);
    for (const change of OVERLAY.changes) {
      const anchor = flat(change.anchor);
      if (!source.includes(anchor)) continue;
      applied += 1;
      const at = original.findIndex((line) => line.includes(anchor));
      const stepNumber = original[at].match(/^- \[ \] (\d+)\./)[1];
      const now = out.find((line) => line.startsWith(`- [ ] ${stepNumber}. `));
      const where = `${route}: ${change.verb} "${change.anchor}"`;
      if (change.verb === "Replace") {
        assert.ok(now.includes(change.text), where);
        assert.ok(!out.some((line) => line.includes(anchor)), `${where} still has its anchor`);
      } else if (change.verb === "In") {
        assert.ok(now.includes(anchor) && now.includes(change.text), where);
      } else {
        const index = out.indexOf(now);
        const neighbour = change.verb === "After" ? out[index + 1] : out[index - 1];
        assert.equal(neighbour, `- [ ] ${change.text}`, where);
      }
    }
  }
  assert.equal(applied, 17, "6 on feature, 3 on bug-fix, 2 on refactoring, 2 on perf-issue, 4 on visual-parity");
});

test("the anchored results read as intended on the routes that differ", () => {
  const feature = lines(todo("feature"));
  assert.deepEqual(feature.slice(6, 8), [
    "- [ ] Decide the design-skip rule (`/implement` step 3) for this step and the `architect` step.",
    "- [ ] 1. `how` over the affected subsystem.",
  ]);
  assert.ok(feature.includes("- [ ] 6. Units already commit in order with `Unit:` trailers, and the landing folds them (`/implement` step 5, Unit commits). Stack follow-ups. Use the **sequence-verifiable-units** principle skill, building, verifying, and committing each small unit before the next. A follow-up is a new Tracker Issue (`/implement` step 5, Follow-ups)."));
  assert.ok(feature.includes("- [ ] 8. No pull request is opened: the gates below, then LANDING.md, one landing for the run."));
  const bug = lines(todo("bug-fix"));
  assert.ok(!bug.some((line) => line.includes("Decide the design-skip rule")), "the design-skip change is Feature's only");
  assert.ok(bug.includes("- [ ] 2. Binary-search the cause. Form the candidate hypotheses, then rule them out until one survives. Seed them with `how` over the affected subsystem and the **why** skill for regression history. Each pass, take the split that cuts the most remaining problem space, get runtime evidence, eliminate. When program state is unclear, add instrumentation or logging and read it as the code runs. Don't guess. Drive a long or stubborn hunt with Claude Code's `loop` skill. Confirm the surviving *mechanism* with runtime evidence before the step-3 architect/interrogate fan-out."));
  assert.ok(lines(todo("visual-parity")).includes("- [ ] 5. No pull request is opened: the gates below, then LANDING.md, one landing for the run and every component."));
});

test("a repo playbook's change lands before the overlay's, at its own anchor", () => {
  const root = repoWithPlaybook("smoke.md", "---\nextends: feature\nwhen: Any feature in this repo.\n---\n\n- **After** \"Verify on the matching surface.\" Run `scripts/smoke.sh` and keep its output.\n");
  const out = lines(todo("feature", root));
  const at = out.findIndex((line) => line.startsWith("- [ ] 5. Verify on the matching surface."));
  assert.equal(out[at + 1], "- [ ] Run `scripts/smoke.sh` and keep its output.");
  assert.ok(!lines(todo("bug-fix", root)).includes("- [ ] Run `scripts/smoke.sh` and keep its output."), "it extends feature only");
});

test("a repo playbook that replaced an overlay anchor fails with the anchor named", () => {
  const root = repoWithPlaybook("pr.md", "---\nextends: feature\nwhen: Features here open a draft PR.\n---\n\n- **Replace** \"Run **Opening a PR**\" Open a draft PR with `gh pr create --draft`.\n");
  const { text, problems } = generate({ playbook: "feature", root, landing: "worktree", done: DONE });
  assert.equal(text, "");
  assert.deepEqual(problems, ['.agents/playbooks/implement.md: "Run **Opening a PR**" is in feature.md but in no item of the todo: an earlier change replaced it, or it sits outside the numbered steps']);
});

test("an anchor no extended playbook has, and a route the overlay does not extend, fail", () => {
  const root = repoWithPlaybook("stale.md", "---\nextends: feature\nwhen: Stale.\n---\n\n- **In** \"Run the Planner.\" Slice it first.\n");
  assert.deepEqual(generate({ playbook: "feature", root, landing: "worktree" }).problems, ['.agents/playbooks/stale.md: "Run the Planner." is not in any playbook it extends']);
  assert.deepEqual(generate({ playbook: "hillclimb", root: emptyRepo(), landing: "worktree" }).problems, ["hillclimb: the Overlay does not extend it; /implement routes only to feature, bug-fix, refactoring, perf-issue, visual-parity"]);
  assert.deepEqual(generate({ playbook: "feature", root: emptyRepo(), landing: "in-place" }).problems, ["--landing in-place needs --start <sha>"]);
});

test("the command line writes the todo to stdout and exits 2 on a usage error", () => {
  const root = emptyRepo();
  const ok = spawnSync(process.execPath, [SCRIPT, "bug-fix", "--root", root, "--landing", "in-place", "--start", "abc123", "--done", "Wrote spec.md"], { encoding: "utf8" });
  assert.equal(ok.status, 0, ok.stderr);
  assert.equal(ok.stdout, generate({ playbook: "bug-fix", root, landing: "in-place", start: "abc123", done: ["Wrote spec.md"] }).text);
  const usage = spawnSync(process.execPath, [SCRIPT, "bug-fix", "--root", root, "--landing", "in-place"], { encoding: "utf8" });
  assert.equal(usage.status, 2);
  assert.equal(usage.stderr.trim(), "--landing in-place needs --start <sha>");
  const bad = spawnSync(process.execPath, [SCRIPT, "hillclimb", "--root", root, "--landing", "worktree"], { encoding: "utf8" });
  assert.equal(bad.status, 1);
  assert.match(bad.stderr, /the Overlay does not extend it/);
  rmSync(root, { recursive: true, force: true });
});
