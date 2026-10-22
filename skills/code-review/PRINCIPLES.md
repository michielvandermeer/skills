# Design principles

These principles describe how code should be shaped. A finding under one is a judgement call, and a hard violation only when it names a wrong result, a crash, or lost data. A documented repo standard always wins over a principle. Skip anything a linter, formatter, or type checker already enforces, and name the principle when you cite it, as in "possible Boundary discipline: ...".

## Boundary discipline

Validate input, narrow types, and handle errors where data enters the system: CLI arguments, config files, network calls, external APIs, database rows. Inside the system, trust the types. Keep business logic in pure functions that the framework layer only calls.

**In a diff:**
- A null check, range check, or try/catch deep in a call chain, on data an earlier layer already validated.
- Config or raw input read inside business logic instead of parsed once at load time.
- Business rules inside a handler or framework callback, untestable without the framework.
- A transport, storage, or wire type exported through a module's public surface.

**Fix:** move the check to the boundary and parse the raw input into a domain type there. Delete the inner checks. Extract the logic into a pure function and leave the handler thin.

## Type system discipline

Let the compiler reject impossible states, mixed-up primitives, and unhandled cases. A runtime "this cannot happen" check marks a type that is too weak.

**In a diff:**
- Optional fields whose valid combinations need a comment: `completed: boolean` beside `completedAt?: Date`.
- Two same-typed parameters that mean different things: `userId: string, orderId: string`.
- A cast, `any`, or non-null assertion that silences the compiler instead of proving the fact.
- A switch whose default branch would hide a new variant.
- A hand-written copy of a shape a schema or API spec owns.

**Fix:** model variants as a discriminated union or sealed type. Give each semantic primitive its own branded type. Parse at the boundary instead of casting. Make each match exhaustive so a new variant fails compilation. Derive types from the owning schema. Strengthen a type only where code would otherwise throw, and stop there.

## Model the domain

Encode the domain in a data structure instead of spreading it across conditionals. The right structure deletes branches and makes invalid states impossible.

**In a diff:**
- A new feature that adds one more branch to an existing if/else or switch chain.
- A second boolean or status field that must stay in sync with the first.
- The same rule or shape assumption repeated across files.
- Modules named for steps (load, validate, save) that each repeat the same rules.

**Fix:** use the structure the domain already has: a state machine for lifecycle flags, a lookup table for branching, a discriminated union for variants, a reducer for state changes, or a module that owns one body of domain knowledge. Keep plain code when the shape is clear, local, and unlikely to grow. An abstraction that removes no branches or invalid states only adds indirection.

## Foundational thinking

Get the data shape right before the logic. When the core types fit the main access paths, the code around them becomes obvious.

**In a diff:**
- Logic that works around a data structure, such as searching a list that is always looked up by key.
- Two types for one concept, converted back and forth.
- A new capability spread across callers as special cases instead of living in one abstraction.
- A helper extracted from a few lines that only look alike.
- Shared state with no answer to "what if another actor changes this at the same time?"

**Fix:** change the core type or structure so the main paths become direct. Merge parallel types into one model. Give the new capability one home. Deduplicate structure, not every line: three similar statements beat a premature abstraction.

## Minimize reader load

Maintainability is the work a reader does to understand code. Count the layers between a question and its answer, and the hidden or mutable state the reader must keep in mind.

**In a diff:**
- A wrapper with one caller, or an adapter with one implementation.
- A layer that repeats the methods and arguments of the layer below it.
- State held wider than needed: a field that could be a local, or a global that could be a field.
- The same invariant re-checked in every consumer.

**Fix:** inline one-caller wrappers and pass-through layers. Narrow state to the smallest scope; return values instead of mutating; derive values instead of syncing them by hand. State the invariant once, at the boundary. The test: a new reader can answer "where does X come from?" and "what can change X?" in under 30 seconds.

## Laziness protocol

Make the smallest change that solves the problem, and make each decision in one place. Lean toward deleting code over adding it.

**In a diff:**
- Changes beyond what the task needs: reformatting, renames, or refactors unrelated to it.
- New parameters threaded through several functions to carry one signal.
- The same choice repeated at several call sites, such as a feature check, a mode test, or a config lookup.
- Boilerplate added for elegance where a few direct lines would do.

**Fix:** cut the diff back to what solves the problem, and move unrelated cleanup to its own change. Make the decision once, in one source of truth, and pass the result down as a plain value or flag. Remove layers and parameters that exist only to carry a signal through.

## Subtract before you add

Remove complexity first, then build on the simpler base. Leave the design simpler than you found it, with the same or a smaller surface.

**In a diff:**
- New code beside dead code, unused parameters, or stale references the change could have removed.
- Validators, parsers, guards, or options for cases the spec does not ask for and no caller hits.
- A stub, placeholder, or file that only points elsewhere and holds nothing new.
- Polish on code that is not yet at its minimum.

**Fix:** delete the dead code, redundant checks, and stubs, ideally in a commit before the addition. Remove speculative hooks and options until a real need shows up. Design for the callers that exist today.

## Migrate callers then delete legacy APIs

When a new internal API replaces an old one, migrate every caller and delete the old API in the same change. This holds whenever no external user depends on the old API.

**In a diff:**
- A new function or endpoint added beside the old one, both still in use.
- A compatibility shim from old API to new, with no removal plan.
- An internal API marked deprecated while internal callers still use it.
- Tests that still assert the old contract or its implementation details.

**Fix:** list the callers, move each one to the new API, and delete the old API in the same change. Keep a temporary adapter only when a real constraint demands it, and give it an end date. Rewrite tests against the new contract, and delete tests that only guarded the old internals.

## Redesign from first principles

Integrate a new requirement as if it had been a founding assumption of the design, instead of bolting it on.

**In a diff:**
- A special case wedged into existing code: a new flag parameter, an `if (newThing)` branch, a mode most code ignores.
- The requirement handled in one place while related types, docs, examples, or names still describe the old design.
- A workaround that exists only because the old structure did not expect the requirement.

**Fix:** ask what you would build from scratch with this requirement known. Reshape the types and modules toward that design. Then carry the change through every reference: types, docs, examples, names, and comments. A large redesign can land in several steps, as long as each step moves toward the whole design.

## Make operations idempotent

An operation that changes state should reach the same end state however often it runs and wherever an earlier run stopped. Ask of each one: what if this runs twice, and what if the last run crashed halfway?

**In a diff:**
- A create or insert that fails or duplicates when the record already exists.
- A multi-step operation whose later steps assume the earlier ones never ran.
- Cleanup keyed on creation order instead of content.
- A lock file with no way to detect that its owner died.
- Startup code that assumes a clean slate after a crash.

**Fix:** use upsert, create-if-missing, or compare-then-write. At startup, find existing state, clean what is stale, and adopt what is live. Detect stale locks by checking whether the owning process still runs. Add a reconciliation step wherever the outcome depends on leftover state.

## Separate before serializing shared state

When concurrent actors might write the same file, key, branch, or object, first remove the sharing. Serialize access only when one shared writer is a real invariant, and then enforce it in code.

**In a diff:**
- Two workers or jobs writing their own fields into one shared state file or record.
- A lock around state each actor could own separately.
- A comment or convention ("do not run in parallel") standing in for concurrency control.

**Fix:** give each actor its own file, key, or record, and merge the results only where they are read. Two workers that each write a field of one `state.json` still share it; `indexer-state.json` and `metrics-state.json` do not. When one shared target must stay, enforce the order in code: a single writer, sequential phases, a lock, or an atomic compare-and-swap.

## Fix root causes

Fix a bug where it starts, not where it shows. A guard that stops the crash leaves the fault in place.

**In a diff:**
- A null check, try/catch, default, or retry added at the crash site, while the bad value still arrives.
- A workaround with a long comment to justify it.
- One instance fixed while the same pattern remains elsewhere.
- A restart bug patched in code when stale persisted state is the cause.
- A bug fix with no test that reproduces the original failure.

**Fix:** trace the bad value back to its origin, correct it there, and remove the guard. A workaround that needs a paragraph of justification means the code should change. Search for the same pattern and fix every instance. For restart bugs, validate persisted state when it loads. Add a test that fails without the fix.

## Encode lessons in structure

A rule that matters belongs in code that enforces it. A comment restating the rule is the symptom.

**In a diff:**
- The same warning comment ("call init first", "keep in sync with X") added in several places.
- A comment rule a type could enforce, such as "call A before B".
- A hand correction the codebase has needed before.
- A structural fix plus a comment that repeats the same rule.

**Fix:** encode the rule. Use a type that makes the wrong call impossible, a lint whose message names the fix, a runtime check at the boundary, a generated file, or a test. Once the structure enforces the rule, delete the comment. Keep prose only for a rule that needs judgement, and give it one prominent place with an example of the failure.

## Test behavior, not implementation

A test calls the code the way its users do and asserts the exact result they see, at the level it acted. Setup may reach lower. The assertion stays at the interface the test drove. A tautological test passes whether or not the code under test is correct, and proves nothing: one that would pass if every imported function returned `undefined` is tautological.

**In a diff:**
- Loose assertions: `toBeDefined`, `toBeTruthy`, `not.toThrow`, `toBeGreaterThan(0)`.
- Only checking that a mock was called, or that a result is empty or undefined.
- An expected value computed by the code under test: `expect(f(a)).toBe(f(a))`.
- A test that restates a constant or config default.
- Assertions on data the test built itself, with no call to the subject.
- A mock or stub of the unit the test claims to test.
- An assertion below the level the test acted at: an HTTP request checked by querying the database, a public method checked by reading a private field.

**Fix:** call the subject with one concrete input and assert the literal output or effect. Rewrite a tautological test until breaking the subject turns it red. Assert through the interface the test acted on: after a `POST`, read back with a `GET`. Where the effect has no read path at that level, such as an email sent, assert the payload the boundary double received. For a mock, assert the payload it received. For an absence, also assert the presence on another input. Pin a constant only when its value is a documented promise to users, and name that promise.

## Deterministic tests

A test gives the same result on every run, alone, in any order, and in parallel. A test that fails one run in fifty teaches everyone to rerun instead of read.

**In a diff:**
- A fixed sleep before an assertion, waiting for async work: `sleep(500)`, `Thread.Sleep`, `setTimeout`.
- The real clock, an unseeded random source, or a live third-party call inside a test.
- State one test leaves for another to read: a shared row, a static field, a file at a fixed path.
- A test that passes only when another test ran first.

**Fix:** await the event, or poll the condition with a timeout. Inject the clock and seed the random source. Give each test its own data and clean it up, so the suite passes in any order.

## Test the failure cases

A behaviour gets a test on each path where it fails or reaches an edge, beside its happy path. An agent writes the happy path first and tends to stop there.

**In a diff:**
- A new validation, guard, or error branch that no test triggers.
- A limit or range with no test at its edge: zero, empty, the maximum, one past it.
- An error-path test that asserts only that something threw, not which error the user sees.

**Fix:** add one test per error branch and per edge the code handles, each asserting the exact error or result the user meets there.

## Prove it works

A change is done when its behaviour is observed on the real thing, not inferred from a proxy such as "it compiles". In a diff, missing proof is a claim with no evidence.

**In a diff:**
- A behaviour change, bug fix, or feature with no test or check that exercises it.
- A check on a proxy (a file exists, a log line printed) instead of the actual value or effect.
- A check keyed on a field the old code also produces, such as a version string, so it passes on both.

**Fix:** add a test or script that drives the real behaviour and asserts the actual value. Key it on behaviour only the new code produces. When a test should fail first, confirm it fails with the predicted mismatch, not an unrelated error. Prefer a rerunnable script over a manual check.
