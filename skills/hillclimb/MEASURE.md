# Measuring a Hillclimb

A Hillclimb trusts one thing: the frozen measurement script. These rules keep its numbers about the work. One run on a shared machine can swing by ±50%, so one run proves nothing.

## The script

`<folder>/measure.<ext>`, written in whatever the repo already runs scripts with.

- `measure <checkout> [runs]` measures one side; `measure <before> <after> [runs]` alternates the sides — before, after, before, after — so warm-up, caches, and drift hit both alike.
- Each run executes the measured command in that checkout and writes its raw output to `<scratch>`. The timed region holds the measured work only; building and installing happen before it.
- Every run records the number, the **work count** — what was actually done, such as the number of tests that ran — and the **error count**: failures, non-success responses, crashes. A change that skips work or fails fast looks faster; these two counts catch it.
- It prints one line per side — median, min–max range, runs, work count, errors — and nothing else, because the driving session reads every summary for hours.

**Freeze** it after the sensitivity check. No Attempt and no fixer edits it. A Hillclimb that must change it measures a new baseline and says so in that row's `Note`.

## Sensitivity check

Before freezing, run the script on two cases known to differ — the full workload against a narrowed one, or a run with a deliberate delay added — and confirm their medians separate by more than their ranges. When they do not, the script measured noise or the wrong work: revise the workload or the number.

## Before any measurement

- Check `uptime`, `nproc`, and what else is running — `ps`, `docker ps`. Another session's test run is the usual source of noise. When it cannot be stopped, the alternation shares the noise between the sides; say so in the row's `Note`.
- Keep profilers, samplers, and tracers out of measured runs. They slow the work, and a heavy sampler beside a heavy suite can run the machine out of memory.
- Measure both sides on the same machine, in the same hour, each in its own checkout, built the same way.

## Judging a pair

- At least 3 runs per side, alternating. While the ranges overlap and the medians differ, add runs, up to 10 per side.
- A gap smaller than the run-to-run spread is **no change**.
- When wall-clock time swings too widely to judge, CPU time or a phase timing the repo already records is often the steadier number. Propose it in step 1, when the number is agreed — never midway.
- Before keeping a change, compare its work and error counts with the before side's.

## Finding the limiter

For the profiling Explorer. Profile in runs nobody reports.

- **Why not twice as fast?** Name what limits the number: CPU per process, the runtime's profiler, I/O wait, lock waits, a database waiting on its client. Map the hot spot to source.
- **Do the arithmetic.** Removing a piece that takes 10% of the run can make the run at most about 11% faster. A gain past what the piece costs measured something other than the work.
- **Did the work happen?** Confirm the work ran inside the timed region — the tests executed, the rows were written, the result was used.
