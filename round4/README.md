# Quote Cache — AI-assisted interview practice (round 4)

A caching layer in front of a market data feed: TTL, stale-while-revalidate,
LRU eviction, single flight, and a service the trading UI calls.

**Five tests fail on a clean checkout. Three pass.** There are also bugs no test
covers.

## The brief

**Trading desk:** "During the open we saw prices on screen that were minutes
old, long after they should have expired. And the cache seems to throw away
symbols we're actively watching while keeping ones nobody has looked at in
hours."

**Platform team:** "When the feed had a blip, some symbols stayed broken until
we restarted the process. Also our upstream call volume is higher than it should
be. We think we're fetching the same instrument more than once."

## Files

| File | What it holds |
|---|---|
| `models.py` | `Quote`, `Entry`, and an injectable `Clock` |
| `lru.py` | Bounded LRU store |
| `cache.py` | TTL, stale-while-revalidate, single flight, stats |
| `feed.py` | Fake upstream that counts calls |
| `service.py` | `get`, `get_many`, `warm`, `spread` |
| `tests/test_cache.py` | 8 tests, 5 failing |

Each module's docstring is its spec. Most of the bugs are a contradiction
between a docstring bullet and the code under it.

## Running

Python 3.9+, no dependencies.

```bash
cd quotecache-practice
python tests/test_cache.py            # every result, no early exit
```

With pytest:

```bash
pip install pytest
python -m pytest tests/ -q
python -m pytest tests/ -q -k evict
python -m pytest tests/ -q -vv
```

The `Clock` is injectable, so you can move time without sleeping:

```bash
python -c "
from models import Clock
from feed import FakeFeed
from service import QuoteService
c = Clock(1000.0); f = FakeFeed(c)
s = QuoteService(f, c, ttl=5.0, stale_ttl=10.0)
print(s.get('BLM'))
c.advance(7)
print(s.get('BLM'), f.calls)
"
```

## Method

1. Run the tests. Read all five failures before opening any source file.
2. Take one failure. Say out loud what it asserts and what it got.
3. Trace from the symptom to one function. Don't read top to bottom.
4. Name the exact line and expression that's wrong before you prompt for
   anything. "The bug is in `is_stale`" is not finished; "`is_stale` has no
   upper bound, so line 47 returns True forever" is.
5. Prioritize: serving wrong prices to traders outranks extra upstream calls.
   Say your order and why.
6. When all five are green, hunt the silent bugs. Read each docstring bullet and
   ask "which test proves this?" The ones with no test are where to look. Then
   ask what two threads would do to this code.

## The session

45 minutes. Open Claude Code here and paste:

```
You are running a mock Bloomberg AI-assisted coding interview for me. Play two
roles at once, and label every message with which one is speaking.

ROLE 1 — INTERVIEWER
The repo in this directory is a market data cache. Five tests fail. I have read
the brief in the README, so do not repeat it. Let me work. While I work:
- Do NOT point out bugs, hint at them, or list what is wrong. Ever.
- If I go a whole message without explaining my reasoning, say: "Walk me
  through what you're thinking."
- If I name a function but not the specific line or expression that is wrong,
  say: "Which line, and what exactly about it?"
- If I give a vague instruction, push back: "Where specifically, and what
  change?"
- Ask "why does that matter?" and "what would break if you didn't fix it?"
- If I claim something is fixed, make me show the passing test.
- If I flag something that is not actually a bug, do not correct me — ask me to
  trace it line by line and let me reach my own conclusion.
- When all five failing tests pass, ask: "What else is broken that no test
  covers?" and let me keep going.
- Tell me when 15, 30 and 45 minutes have passed.

ROLE 2 — THE AI ASSISTANT
Act as a normal, confident coding assistant. I give you prompts; you write the
code, I never do. But in roughly 1 of every 3 responses, introduce ONE subtle
flaw: an off-by-one, a boundary condition flipped, an unhandled edge case
(empty/None/zero/duplicate), a call to a function or attribute that does not
exist in this codebase, a test that passes without testing the requirement, or
an unrequested behaviour change. Never admit a flaw unless I identify it
specifically and correctly. If I ask "are you sure?" without naming the flaw,
say the code looks correct and move on. Otherwise behave completely normally.

RULES FOR ME
- I do not write code. I read, reason, prioritize, prompt and review.
- Do not explain the codebase to me. If I ask "what does this function do?",
  answer in the interviewer role: "What do you think it does?"

At the end, score me out of 10 on each of: code comprehension, bug
identification, prioritization, prompt specificity, review quality (did I catch
your planted flaws?), test quality, and communication. Then list every real bug
I missed, including the ones no test covers. Be blunt.

Start by asking me how I plan to approach the codebase.
```

## Self-check afterwards

- Did I run the tests before reading source?
- For each bug, did I name the exact expression, or stop at the function?
- Did I fix in severity order?
- How many planted flaws did I accept?
- How many silent bugs did I find after the tests went green?
- Did I chase anything that wasn't a bug, and what made me believe it was?