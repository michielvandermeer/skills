"""Compare the /implement runs of two skills commits.

  python benchmark/compare.py <baseline sha or csv> <candidate sha or csv> [--claim "..."]

The primary number is list-price cost per run. The report states the claim, leads with a verdict, and
gives median and range per side. A gap no bigger than the run-to-run spread (the larger range of the
two sides) is "no measurable difference"; a bigger gap needs a rank-sum p below 0.05 to count.
Invalid runs (they did not do the work) are counted and left out of every median."""
import argparse
import csv
import statistics
import sys
from collections import Counter
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
METRICS = [("cost_usd", "List-price cost per run (USD)", "{:.2f}"), ("tokens_total", "Tokens per run (millions)", None),
           ("subagents", "Subagents per run", "{:.0f}"), ("wall_s", "Wall time per run (minutes)", None),
           ("max_context", "Largest context in any call (thousand tokens)", None)]
SCALE = {"tokens_total": (1e6, "{:.1f}"), "wall_s": (60, "{:.0f}"), "max_context": (1e3, "{:.0f}")}


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def is_true(v):
    return v == "True"


def load_rows(arg, results=HERE / "results"):
    path = Path(arg)
    if not path.is_file():
        found = sorted(Path(results).glob(f"{arg}*.csv"))
        if len(found) != 1:
            raise SystemExit(f"{arg}: expected one CSV in {results}, found {len(found)}")
        path = found[0]
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def rank_sum_p(a, b):
    """Exact two-sided Mann-Whitney p, by counting the rank sums of every way to split the pooled runs."""
    pooled = sorted(a + b)
    twice = {}  # twice the mid-rank of each value, so ties stay integers
    for v in set(pooled):
        first = pooled.index(v) + 1
        twice[v] = first + (first + pooled.count(v) - 1)
    n, total = len(a), len(pooled)
    ways = [[0] * (2 * total * (total + 1) // 2 + 1) for _ in range(n + 1)]
    ways[0][0] = 1
    for v in pooled:
        for k in range(n, 0, -1):
            for s in range(len(ways[k]) - twice[v] - 1, -1, -1):
                if ways[k - 1][s]:
                    ways[k][s + twice[v]] += ways[k - 1][s]
    expected = n * (total + 1)
    observed = abs(sum(twice[v] for v in a) - expected)
    return sum(w for s, w in enumerate(ways[n]) if abs(s - expected) >= observed) / comb(total, n)


def decide(b, c):
    """(verdict word, change of the median in percent, rank-sum p) for lower-is-cheaper samples."""
    mb, mc = statistics.median(b), statistics.median(c)
    spread = max(max(b) - min(b), max(c) - min(c))
    p = rank_sum_p(b, c)
    if abs(mc - mb) <= spread:
        word = "no measurable difference"
    elif p < 0.05:
        word = "cheaper" if mc < mb else "costlier"
    else:
        word = "inconclusive"
    return word, (mc - mb) / mb * 100 if mb else 0.0, p


def spans(values, fmt, scale=1):
    values = [v / scale for v in values]
    return f"{fmt.format(statistics.median(values))} [{fmt.format(min(values))}-{fmt.format(max(values))}]"


def by_spec(rows, key):
    out = {}
    for r in rows:
        if is_true(r["valid"]) and num(r[key]) is not None:
            out.setdefault(r["spec"], []).append(num(r[key]))
    return out


def quality(rows):
    valid = [r for r in rows if is_true(r["valid"])]
    count = lambda pred: sum(1 for r in valid if pred(r))
    return {"runs": len(rows), "valid": len(valid), "invalid": len(rows) - len(valid),
            "failed": sum(is_true(r["failed"]) for r in rows),
            "build": count(lambda r: is_true(r["build_ok"])), "tests": count(lambda r: is_true(r["tests_ok"])),
            "forbidden": count(lambda r: (num(r["forbidden_html"]) or 0) + (num(r["forbidden_text"]) or 0) > 0),
            "guard_trips": count(lambda r: (num(r["blocked_writes"]) or 0) > 0),
            "api_errors": sum(num(r["api_errors"]) or 0 for r in rows),
            "diff_ratio": statistics.median([num(r["diff_ratio"]) for r in valid if num(r["diff_ratio"]) is not None] or [0])}


def regressions(qb, qc):
    found = []
    for key, label in (("build", "build passed"), ("tests", "tests passed")):
        if qb["valid"] and qc["valid"] and qc[key] / qc["valid"] < qb[key] / qb["valid"]:
            found.append(f"{label} on {qc[key]} of {qc['valid']} valid candidate runs, against {qb[key]} of {qb['valid']} baseline runs")
    if qb["valid"] and qc["valid"] and qc["forbidden"] / qc["valid"] > qb["forbidden"] / qb["valid"]:
        found.append(f"tests asserting exact markup or content text in {qc['forbidden']} of {qc['valid']} candidate runs, against {qb['forbidden']} of {qb['valid']}")
    if qb["runs"] and qc["runs"] and qc["invalid"] / qc["runs"] > qb["invalid"] / qb["runs"]:
        found.append(f"{qc['invalid']} of {qc['runs']} candidate runs did not do the work, against {qb['invalid']} of {qb['runs']}")
    if qc["api_errors"] > qb["api_errors"]:
        found.append(f"API errors: {qc['api_errors']:.0f} on the candidate, {qb['api_errors']:.0f} on the baseline")
    if qb["diff_ratio"] and not 0.67 <= qc["diff_ratio"] / qb["diff_ratio"] <= 1.5:
        found.append(f"median diff size moved from {qb['diff_ratio']} to {qc['diff_ratio']} times the real landing commit")
    return found


def interleaved(base, cand):
    order = sorted([(r["started"], 0) for r in base] + [(r["started"], 1) for r in cand])
    switches = sum(1 for x, y in zip(order, order[1:]) if x[1] != y[1])
    return len(order) < 2 or switches / (len(order) - 1) >= 0.8


def report(base, cand, claim, names):
    """(text, verdict). Refuses, with no table, when the two sides ran with different settings."""
    out = [f"Claim: {claim}", ""]
    settings = [{(r["model"], r["effort"]) for r in rows} for rows in (base, cand)]
    if len(settings[0]) != 1 or settings[0] != settings[1]:
        out += ["VERDICT: inconclusive. The two sides ran with different settings, so there is nothing to compare.",
                f"Model and effort, baseline: {sorted(settings[0])}; candidate: {sorted(settings[1])}."]
        return "\n".join(out), "inconclusive"
    (model, effort), = settings[0]
    reasons = []
    for spec in {r["spec"] for r in base + cand}:
        hashes = {r["spec_hash"] for r in base + cand if r["spec"] == spec and r["spec_hash"]}
        if len(hashes) > 1:
            reasons.append(f"{spec}: the Issue changed between runs, so the sides did not get the same Spec")
    unchecked = sum(1 for r in base + cand if not is_true(r["failed"]) and not is_true(r["checks_done"]))
    if unchecked:
        reasons.append(f"build and tests were not scored on {unchecked} run(s), so the work and error checks could not be done")
    cb, cc = by_spec(base, "cost_usd"), by_spec(cand, "cost_usd")
    specs = sorted(set(cb) & set(cc))
    if not specs:
        reasons.append("no Spec has a valid run on both sides")
    qb, qc = quality(base), quality(cand)
    word, change, p, table = "inconclusive", 0.0, 1.0, []
    if specs:
        medians = {s: statistics.median(cb[s]) for s in specs}
        rel = lambda by: [v / medians[s] for s in specs for v in by[s]]
        word, change, p = decide(rel(cb), rel(cc))
        passes = [sum(statistics.median(by[s]) for s in specs) for by in (cb, cc)]
        if word == "inconclusive":
            reasons.append(f"the gap is bigger than the run-to-run spread but the rank-sum p is {p:.3f}; run more repeats")
        thin = [s for s in specs if min(len(cb[s]), len(cc[s])) < 5]
        if thin:
            reasons_note = "fewer than 5 valid runs per side on " + ", ".join(thin) + ": under the checklist's minimum, so read the verdict as provisional"
        else:
            reasons_note = None
    verdict = "inconclusive" if reasons else word
    detail = "; ".join(reasons) if reasons else f"{change:+.0f}% median list-price cost"
    flagged = regressions(qb, qc) if qb["valid"] and qc["valid"] else []
    out.append(f"VERDICT: {verdict} ({detail})" + (", with quality regressions (below)" if flagged else ""))
    out.append("")
    if specs:
        out.append(f"Number: one pass over {len(specs)} Spec(s), summing each Spec's median run: ${passes[0]:.2f} on the baseline, "
                   f"${passes[1]:.2f} on the candidate. Relative to each Spec's baseline median, the candidate's median run is "
                   f"{100 + change:.0f}% (n = {sum(len(cb[s]) for s in specs)} baseline, {sum(len(cc[s]) for s in specs)} candidate valid runs).")
        out += ["", limiter(base, cand, change, verdict)]
    out += ["", f"Settings, identical on both sides: model {model}, effort {effort}. Baseline {names[0]}, candidate {names[1]}.",
            "Runs alternated baseline and candidate on one machine, so machine load hit both alike." if interleaved(base, cand)
            else "The runs were NOT interleaved baseline-candidate: a change in machine load can bias the gap."]
    if specs and reasons_note:
        out.append(reasons_note)
    for key, title, fmt in METRICS:
        scale, fmt = SCALE.get(key, (1, fmt))
        b, c = by_spec(base, key), by_spec(cand, key)
        out += ["", f"{title}: median [range] per side", f"{'Spec':26} {'n':>3} {'baseline':>22} {'n':>3} {'candidate':>22} {'change':>7}"]
        for s in specs:
            vb, vc = b.get(s), c.get(s)
            if vb and vc:
                delta = (statistics.median(vc) - statistics.median(vb)) / (statistics.median(vb) or 1) * 100
                out.append(f"{s:26} {len(vb):>3} {spans(vb, fmt, scale):>22} {len(vc):>3} {spans(vc, fmt, scale):>22} {delta:>+6.0f}%")
                if key == "cost_usd":
                    out[-1] += "  " + decide(vb, vc)[0]
    out += ["", "Quality (valid runs unless noted)", f"{'':34} {'baseline':>10} {'candidate':>10}"]
    for label, key in (("runs", "runs"), ("did not do the work (invalid)", "invalid"), ("failed (claude error or timeout)", "failed"),
                       ("valid", "valid"), ("build passed", "build"), ("tests passed", "tests"),
                       ("tests asserting markup or text", "forbidden"), ("guard trips", "guard_trips"),
                       ("API errors", "api_errors"), ("diff size vs landing commit (median)", "diff_ratio")):
        out.append(f"{label:34} {qb[key]:>10} {qc[key]:>10}")
    out += ["", "Quality regressions:" + (" none flagged." if not flagged else "")] + [f"  - {f}" for f in flagged]
    for name, rows in zip(("baseline", "candidate"), (base, cand)):
        why = Counter(x for r in rows if not is_true(r["valid"]) for x in r["invalid_reasons"].split("; ") if x)
        if why:
            out.append(f"Invalid {name} runs: " + "; ".join(f"{n}x {x}" for x, n in why.items()))
    return "\n".join(out), verdict


def roles_of(rows):
    return [key[len("cost_"):] for key in rows[0] if key.startswith("cost_") and key != "cost_usd"]


def cost(row, col):
    value = num(row[col])
    if value is None:
        raise ValueError(f"{col} is {row[col]!r} on run {row['run_id']}, not a number")
    return value


def limiter(base, cand, change, verdict):
    mean = lambda rows, col: sum(cost(r, col) for r in rows if is_true(r["valid"])) / max(1, sum(is_true(r["valid"]) for r in rows))
    roles = [r for r in roles_of(base) if r in roles_of(cand)]
    only = {name: [r for r in roles_of(rows) if r not in roles] for name, rows in (("baseline", base), ("candidate", cand))}
    shares, means = {}, {}
    for name, rows in (("baseline", base), ("candidate", cand)):
        total = mean(rows, "cost_usd") or 1
        means[name] = {r: mean(rows, f"cost_{r}") for r in roles_of(rows)}
        shares[name] = {r: v / total * 100 for r, v in means[name].items()}
    top = max(roles_of(base), key=lambda r: shares["baseline"][r])
    text = f"Limiter: the {top} role is {shares['baseline'][top]:.0f}% of baseline cost"
    if top in roles:
        text += f" ({shares['candidate'][top]:.0f}% on the candidate)"
    text += f", so a change that touched only that role could save at most {shares['baseline'][top]:.0f}%."
    if roles:
        moved = {r: means["candidate"][r] - means["baseline"][r] for r in roles}
        mover = max(roles, key=lambda r: abs(moved[r]))
        text += f" The biggest mover is the {mover} role: {moved[mover]:+.2f} USD per run."
    for name, missing in only.items():
        if missing:
            text += f" Roles only the {name} has: {', '.join(missing)}, with no counterpart to move against."
    if verdict == "cheaper" and -change > shares["baseline"][top]:
        text += (f" The saving ({-change:.0f}%) is bigger than any one role's share: if the change touched one role, "
                 "something else is being measured (a cache, a no-op, a bug); check the invalid and flagged runs.")
    return text


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("baseline")
    p.add_argument("candidate")
    p.add_argument("--claim", help="the claim you expect to show; default: the one recorded when the candidate ran")
    a = p.parse_args(argv)
    base, cand = load_rows(a.baseline), load_rows(a.candidate)
    claim = a.claim or next((r["claim"] for r in cand if r["claim"]), "(none recorded)")
    names = (base[0]["skills_sha"][:12], cand[0]["skills_sha"][:12])
    text, verdict = report(base, cand, claim, names)
    out = HERE / "results" / f"compare-{names[0]}-{names[1]}.md"
    out.write_text(text + "\n", encoding="utf-8")
    print(text)
    print(f"\n(saved to {out})")
    return 2 if verdict == "inconclusive" else 0


if __name__ == "__main__":
    sys.exit(main())
