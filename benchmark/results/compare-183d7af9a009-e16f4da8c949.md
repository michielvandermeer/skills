Claim: Smoke test: both sides land ui-bug-394 with only the plugin under test loaded

VERDICT: inconclusive (the gap is bigger than the run-to-run spread but the rank-sum p is 1.000; run more repeats)

Number: one pass over 1 Spec(s), summing each Spec's median run: $2.84 on the baseline, $4.40 on the candidate. Relative to each Spec's baseline median, the candidate's median run is 155% (n = 1 baseline, 1 candidate valid runs).

Limiter: the main role is 32% of baseline cost (23% on the candidate), so a change that touched only that role could save at most 32%. The biggest mover is the reviewer role: +1.03 USD per run.

Settings, identical on both sides: model sonnet, effort high. Baseline 183d7af9a009, candidate e16f4da8c949.
Runs alternated baseline and candidate on one machine, so machine load hit both alike.
fewer than 5 valid runs per side on ui-bug-394: under the checklist's minimum, so read the verdict as provisional

List-price cost per run (USD): median [range] per side
Spec                         n               baseline   n              candidate  change
ui-bug-394                   1       2.84 [2.84-2.84]   1       4.40 [4.40-4.40]    +55%  inconclusive

Tokens per run (millions): median [range] per side
Spec                         n               baseline   n              candidate  change
ui-bug-394                   1          2.9 [2.9-2.9]   1          4.5 [4.5-4.5]    +58%

Subagents per run: median [range] per side
Spec                         n               baseline   n              candidate  change
ui-bug-394                   1                6 [6-6]   1                8 [8-8]    +33%

Wall time per run (minutes): median [range] per side
Spec                         n               baseline   n              candidate  change
ui-bug-394                   1                9 [9-9]   1             15 [15-15]    +70%

Largest context in any call (thousand tokens): median [range] per side
Spec                         n               baseline   n              candidate  change
ui-bug-394                   1             62 [62-62]   1             65 [65-65]     +6%

Quality (valid runs unless noted)
                                     baseline  candidate
runs                                        1          1
did not do the work (invalid)               0          0
failed (claude error or timeout)            0          0
valid                                       1          1
build passed                                1          1
tests passed                                1          1
Verifier passed                             1          1
tests asserting markup or text              0          0
guard trips                                 0          0
API errors                                  0          0
diff size vs landing commit (median)       0.89       0.95

Quality regressions: none flagged.
