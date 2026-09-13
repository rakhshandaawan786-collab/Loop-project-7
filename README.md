# Break It On Purpose

Sabotaged Project 3's morning-brief loop, then diagnosed the failure
from the spine alone — no replaying the run.

## 1. Measured one beat (Concept 13's math)

| Metric | Value |
|---|---|
| Input read per run (progress.md + repo scan + state) | ~1,176 chars ≈ 294 tokens |
| Output written per run (new progress.md entry) | ~150 chars ≈ 37 tokens |
| Cadence | daily → 30 runs/month |
| Rate used (Claude Sonnet 5, Sept 2026) | $2/M input, $10/M output |
| **Cost per run** | **~$0.001** |
| **Monthly cost (bare task)** | **~$0.03** |
| **Monthly cost (realistic, +800 tokens agent overhead)** | **~$0.08** |

This is a genuinely cheap loop. The exercise in "measure before you
run wild" isn't about this loop being expensive — it's about having
the habit of knowing the number at all before scaling cadence up.

## 2. Sabotage #1 — pointed at a file that doesn't exist

Changed `REPO_DIR = "sample_repo"` to a folder that doesn't exist.

**Before the fix:** Python's `os.walk()` on a missing directory
doesn't raise an error — it just yields nothing. The original script
silently reported "No new TODOs" and even "Resolved (3)" (as if 3 bugs
got fixed!), with **exit code 0**. This is the worst kind of failure:
it looks like good news.

**After the fix:** `scan_todos()` now explicitly checks
`os.path.isdir()` and raises. The run:
- writes one line to `run.log`
- writes a `⚠️ NEEDS HUMAN` note into `progress.md`
- exits with code 1

## 3. Sabotage #2 — an unmeetable success condition, capped

`run_scheduled.sh` defines success as "zero TODOs remain" — impossible
while the repo has real, unfixed TODOs and nothing is fixing them.
Capped at 3 tries. Result: it tried 3 times, then stopped — logged
clearly, marked `NEEDS HUMAN`, did not retry forever.

## 4. Diagnosis from the spine alone

Read only the last lines of `run.log` and `progress.md` — no replay:

```
run.log:
[...] ERROR: hit cap of 3 tries — success condition ('0 TODOs') never met

progress.md:
## 2026-09-13
⚠️ NEEDS HUMAN — hit retry cap (3 tries) without meeting success
condition. The repo has real, unresolved TODOs — this condition can
only be met by someone fixing them, not by retrying.
```

From these two artifacts alone: **what** failed (cap hit, condition
unmeetable), **when** (timestamped), and **what to do about it**
(a human needs to actually fix the TODOs — retrying won't help).

## Files

| File | Purpose |
|---|---|
| `morning_brief.py` | Fixed version — logs every run, never fails silently |
| `morning_brief_ORIGINAL.py` | The original from Project 3, kept to show the silent-failure contrast |
| `run_scheduled.sh` | Wrapper simulating the scheduled heartbeat with a capped retry loop |
| `run.log` | The spine's log — one line per run, pass or fail |
| `progress.md` | The spine's narrative — includes NEEDS HUMAN notes on failure |

## The actual lesson

A loop that fails silently is worse than one that crashes loudly,
because silence gets trusted. Rehearsing this failure now — on
purpose, while watching — is cheap. Finding out three weeks from now
that your overnight loop has been reporting false "all clear" the
whole time is not.
