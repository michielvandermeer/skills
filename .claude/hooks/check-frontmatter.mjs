// PostToolUse hook: after an Edit or Write to a skill or agent file, check that
// every frontmatter line is one known key, and no key was merged into another's line.
import { readFileSync } from "node:fs";

const KEYS = ["name", "description", "argument-hint", "disable-model-invocation", "effort", "disallowedTools", "background", "model", "tools", "allowed-tools", "user-invocable"];

const input = JSON.parse(readFileSync(0, "utf8"));
const path = (input.tool_input?.file_path ?? "").replaceAll("\\", "/");
if (!/(^|\/)(agents\/[^/]+\.md|skills\/[^/]+\/SKILL\.md)$/.test(path)) process.exit(0);

const lines = readFileSync(path, "utf8").split(/\r?\n/);
if (lines[0] !== "---") process.exit(0);
const end = lines.indexOf("---", 1);
const problems = [];
const merged = new RegExp(`\\S(${KEYS.join("|")}):\\s`);

for (const line of lines.slice(1, end)) {
  const key = line.match(/^([A-Za-z-]+):/)?.[1];
  if (!key || !KEYS.includes(key)) problems.push(`unknown or malformed frontmatter line: ${line}`);
  else if (merged.test(line.slice(key.length + 1))) problems.push(`two keys on one line: ${line}`);
}

if (problems.length) {
  process.stderr.write(`${path}\n${problems.join("\n")}\n`);
  process.exit(2);
}
