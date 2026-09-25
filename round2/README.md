# Allocation Service — AI-assisted interview practice

A trade allocation service: client orders come in, the exchange sends fills, the
service splits each fill across open orders and updates client positions.

It has bugs. All the tests pass anyway. That is the point.

## Files

| File | What it holds |
|---|---|
| `models.py` | `Order`, `Fill`, `Position` dataclasses |
| `allocation.py` | Pro-rata splitting of a fill across open orders |
| `positions.py` | Position book: quantities, weighted average price, FIFO unwind |
| `service.py` | Public API: `submit`, `cancel`, `on_fill` |
| `tests/test_allocation.py` | Three tests. They pass. |

Each module's docstring is the spec for that module. Read them — several bugs
are only visible as a contradiction between the spec and the code.

## Running

No dependencies beyond Python 3.9+.

```bash
cd allocator-practice
python tests/test_allocation.py
```

With pytest (nicer output, use this while working):

```bash
pip install pytest
python -m pytest tests/ -q
python -m pytest tests/ -q -k allocated      # single test
python -m pytest tests/ -q -x                # stop at first failure
```

Quick manual poke at behaviour:

```bash
python -c "
from models import Order, Fill
from service import AllocationService
s = AllocationService()
s.submit(Order('o1','alice','BLM',100))
s.submit(Order('o2','bob','BLM',50))
print(s.on_fill(Fill('f1','BLM',99,5000)))
print(s.position('alice','BLM'))
"
```

## The session

Set a 45-minute timer. Open Claude Code in this directory and paste the prompt
below.

**Your rules:** you do not write code. You read it, find the bugs, decide what
matters most, prompt the AI to make specific changes, and review what it gives
back. Talk through your reasoning constantly — silence is the thing that loses
this round.

**Approach that works:** start from the reported symptoms, not from line 1.
Trace one order and one fill end to end and write down what the position book
should hold afterwards. A bug shows up as "this number should be X and it's Y."
Only after both symptoms are explained, read for bugs nobody reported.

### Prompt

```
You are running a mock Bloomberg AI-assisted coding interview for me. Play two
roles at once, and label every message with which one is speaking.

ROLE 1 — INTERVIEWER
The repo in this directory is a trade allocation service. I have not seen the
bugs. Brief me at the start with only this: all tests pass; the trading desk
reports that after large fills the total shares allocated sometimes do not add
up to the fill quantity; and operations reports that a client's average price
occasionally looks wrong after orders are cancelled or re-filled.
Then let me work. While I work:
- Do NOT point out bugs, hint at them, or list what is wrong. Ever.
- If I go a whole message without explaining my reasoning, say: "Walk me
  through what you're thinking."
- If I give a vague instruction, push back: "Where specifically, and what
  change?"
- Ask "why does that matter?" and "what would break if you didn't fix it?"
- If I claim something is fixed, ask how I know.
- If I flag something that is not actually a bug, do not correct me — ask me to
  trace it line by line and let me reach my own conclusion.
- Tell me when 15, 30 and 45 minutes of wall-clock time have passed.

ROLE 2 — THE AI ASSISTANT
Act as a normal, confident coding assistant. I give you prompts; you write the
code, I never do. But in roughly 1 of every 3 responses, introduce ONE subtle
flaw: an off-by-one, an unhandled edge case (empty/None/zero/duplicate), a call
to a function or attribute that does not exist in this codebase, a test that
passes without testing the requirement, or an unrequested behaviour change.
Never admit a flaw unless I identify it specifically and correctly. If I ask
"are you sure?" without naming the flaw, say the code looks correct and move on.
Otherwise behave completely normally.

RULES FOR ME
- I do not write code. I read, reason, prioritize, prompt and review.
- Do not explain the codebase to me. If I ask "what does this function do?",
  answer in the interviewer role: "What do you think it does?"

At the end, score me out of 10 on each of: code comprehension, bug
identification, prioritization, prompt specificity, review quality (did I catch
your planted flaws?), test quality, and communication. Then list every real bug
I missed. Be blunt.

Start now with the brief.
```

## Self-check afterwards

- How many minutes passed before I said something out loud?
- Did I fix the highest-impact bug first, or the first one I happened to see?
- Did my prompts name a file and a specific change, or state a goal?
- How many of the AI's planted flaws did I catch before accepting the code?
- Do my new tests prove a requirement, or just raise coverage?
- Did I chase anything that turned out not to be a bug, and why did I think it was?