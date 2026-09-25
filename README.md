# Bloom — AI-assisted coding interview practice

A collection of small, self-contained Python services, each seeded with subtle
bugs, used to rehearse a mock "AI-assisted coding interview." In each round you
don't write code yourself — you read, reason, prioritize, prompt an AI
assistant to make changes, and review what it gives back. One round also has
the assistant secretly plant flaws in its own output that you have to catch.

Every round lives in its own `roundN/` directory and is fully independent —
different domain, different bugs, no shared code.

## Rounds so far

| Round | Domain | Theme |
|---|---|---|
| `round1/` | Payments settlement (ledger, fees, transfers) | Spec-vs-code contradictions, no README/prompt yet |
| `round2/` | Trade allocation (orders, fills, positions) | Pro-rata splitting, FIFO unwind bugs |
| `round3/` | Subscription billing (plans, coupons, VAT, retries) | Failing tests double as bug reports |
| `round4/` | Market data quote cache (TTL, LRU, single-flight) | Cache correctness under concurrency-ish edge cases |

Each round (from round2 onward) has its own `README.md` with:
- A short spec of what the service does
- The bug reports from "stakeholders" (support/finance/trading desk/etc.)
- A `Files` table describing each module
- Running instructions (pytest)
- The full mock-interview prompt to paste into Claude Code
- A self-check checklist to run after the session

Read the round's own README before starting it — this file is just the index.

## Running a round

```bash
cd roundN
python -m pytest tests/ -q
```

Tests will show a mix of passing and failing tests — failing tests are often
themselves the bug reports (see each round's README for specifics).

## Doing a round

1. `cd` into the round directory and read its `README.md` in full.
2. Set a timer (rounds typically suggest 45 minutes).
3. Open Claude Code (or your assistant of choice) in that directory and paste
   the round's prompt verbatim.
4. Work the round: don't write code, explain your reasoning out loud, trace
   symptoms to root cause before fixing, and review every change the
   assistant proposes — some rounds have it intentionally sneak in bugs.
5. Go through the round's self-check questions afterward.

## Adding a new round

1. Create `roundN/` (next available number) at the repo root.
2. Build the buggy service:
   - A handful of small modules, each with a docstring that acts as the spec.
   - Seed 3-6 subtle, realistic bugs (off-by-ones, unhandled edge cases,
     wrong rounding, stale state, race-condition-shaped logic, etc.).
   - Add a `tests/` directory. Decide whether tests should mostly pass (bugs
     hide as spec/code contradictions, like round1/round2) or whether some
     should fail on a clean checkout as ready-made bug reports (like
     round3/round4).
3. Write `roundN/README.md` modeled on the existing rounds:
   - Title + one-line description of the domain.
   - A "brief" section with 1-3 stakeholder bug reports in plain language —
     never state the actual bug, only the symptom.
   - A `Files` table describing what each module holds.
   - Running instructions (plain Python + pytest, mirror the existing rounds).
   - A `## The session` (or `## The brief` + prompt) section with the full
     copy-pasteable mock-interview prompt. Reuse the structure from
     `round2/README.md` or `round3/README.md`/`round4/README.md`:
     - Interviewer role: brief with only symptoms, never hint at bugs, ask the
       candidate to narrate reasoning, push back on vague instructions.
     - Assistant role: normal confident coding assistant; optionally have it
       plant subtle flaws in some fraction of responses (only for rounds meant
       to test review rigor).
     - Rules for the candidate: no writing code themselves.
     - End-of-session scoring rubric (comprehension, bug ID, prioritization,
       prompt specificity, review quality, test quality, communication) plus a
       list of every real bug missed.
   - A "Self-check afterwards" list of reflection questions.
4. Update the table in this root `README.md` with the new round.
5. Don't commit `__pycache__/`; a root `.gitignore` covers it — verify new
   files aren't caught before committing.

## Repo layout

```
bloom/
├── round1/
├── round2/
├── round3/
├── round4/
└── README.md   <- this file
```
