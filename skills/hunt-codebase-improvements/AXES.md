# The eight Hunt axes

One section per axis, in the order a run reports them. Each brief says what the **Hunter** looks for, what it may run, and its evidence bar: a finding without that evidence is not reported. The shared rules (change no file outside your subfolder, run only commands that change nothing, report at most five) come from `SKILL.md`.

## State bugs

Look for: the states and transitions of the feature with the most states, from the screen to the server. Name the feature and its states, then walk every transition, including the ones a user reaches by double-clicking, going back, reloading, or acting while a request is pending.

May run: reads of the code; the running app, when there is one, through read-only requests and page loads.

Evidence bar: a finding is a transition that should not be possible. It carries the file and line that allows it and the steps that reproduce it.

## Cruft

Look for: dead code; duplicates that have drifted apart; wrappers that add nothing; dependencies that are unused or replaceable.

May run: searches of the code, the dependency list, and read-only commands that list what a package manager has installed.

Evidence bar: for dead code, proof that nothing reaches it: no caller, and no route, reflection, or configuration that reaches it. For a duplicate, both places with their differences. For a wrapper, the file and line and what it adds, which is nothing. For a dependency, where the manifest lists it and the search that found no use.

## Outbound calls

Look for: every HTTP, database, queue, and LLM call, checked for a missing timeout, retries without backoff and jitter, writes that are unsafe to retry, and connection pools too small for peak load.

May run: reads of the code and configuration.

Evidence bar: the file and line of the call, and what is missing there.

## UI polish

Look for: every screen, at a desktop width, on the running app. A missing loading, empty, or error state; a button without a hover or disabled state; a form error shown away from its field; drift from the house design, or from the reference app the instructions name. No screen is checked at a phone width: the apps these skills serve have no phone layouts.

May run: the browser commands in your brief, in your own session; reads of the code. Without a running app, or when the browser check failed, work from the code alone and say so. Compare against a reference app's code where your brief says the reference app was not run.

Evidence bar: a screenshot, saved in your subfolder, of the screen at the desktop width. Without a running browser, the file and line of the missing state, and a plain statement that no screenshot exists.

## Performance

Look for: measured first, on the running app where there is one. Then N+1 queries, missing indexes, lists without paging, awaits in sequence that could run in parallel, heavy work on the request path, and page weight.

May run: timed read-only requests and page loads against the running app, repeated enough to show the spread; reads of the code.

Evidence bar: a measured number with its run count and spread. Without a running app: the code evidence and a plain statement that the cost is unmeasured. A finding that names one number to drive down says it is a fit for `/hillclimb`.

## CI time

Look for: the last 150 or so pull request CI runs, read with `gh run list` and `gh run view`, filtered to pull request events. Split each run's time into queue, setup, and run time, and add up the seconds lost to each cause: cache misses, no sharding, jobs in sequence, the full suite on every pull request. Pull request CI only: leave deploy pipelines and other workflows out.

May run: `gh run list` and `gh run view`, which read.

Evidence bar: the seconds per cause, from the runs read, with how many runs that is.

## Scheduled jobs

Look for: every job the repo defines, such as workflow schedules and recurring jobs registered in code. A cron entry on a server is infrastructure and outside this axis. For each job: how often it runs, its failures, whether anyone uses its output, and where it overlaps another job. Give each a verdict: keep it, change how often it runs, or turn it off.

May run: reads of the code; `gh run list` and `gh run view` for a job's recent results, when the repo's remote is GitHub.

Evidence bar: the schedule's definition and the job's recent results. Report a job only when its verdict is change or turn off.

## Scaling needs

Look for: cache, queue, load balancer, read replicas, object storage or CDN, retries, and logs. Judge each "needed now" or "not yet", with the code as evidence.

May run: reads of the code and configuration.

Evidence bar: the code that shows the need exists now. Only a need judged "needed now" is reported. A need that asks for new hosting, such as a load balancer, read replicas, or a CDN, is marked as an infrastructure fix.
