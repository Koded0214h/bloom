# Billing Service — AI-assisted interview practice (round 3)

Subscription billing: plans, prorated first charges, coupons, VAT, retries, and
a nightly cycle job.

**Four tests fail on a clean checkout. Three pass.** The failing ones are the
bug reports, written as tests. There are also bugs that no test covers.

## The brief

You are on the billing team. Two reports came in:

**Finance:** "Customers who sign up on the 1st are being undercharged, and our
coupon discounts are coming out larger than they should. VAT looks off on
discounted invoices."

**Support:** "A customer who cancelled last month was billed again. And during
last week's gateway timeout, the retry job charged at least one customer
twice."

## Files

| File | What it holds |
|---|---|
| `models.py` | `Plan`, `Coupon`, `Subscription`, `Charge`, `Invoice` |
| `pricing.py` | Proration, coupons, VAT, rounding |
| `repository.py` | Data access: which subscriptions are billable, charge storage |
| `service.py` | `charge()`, `run_cycle()`, `total_revenue()` |
| `tests/test_billing.py` | 7 tests, 4 failing |

Every module's docstring is its spec. Several bugs are only visible as a
contradiction between the docstring and the code.

## Running

Python 3.9+, no dependencies.

```bash
cd billing-practice
python tests/test_billing.py          # prints every result, does not stop at the first failure
```

Better, with pytest:

```bash
pip install pytest
python -m pytest tests/ -q
python -m pytest tests/ -q -k proration      # one test
python -m pytest tests/ -q -x                # stop at first failure
python -m pytest tests/ -q -vv               # full assertion diffs
```

Poke at behaviour directly:

```bash
python -c "
from datetime import date
import pricing
from models import Plan
p = Plan('pro','Pro',10_000)
for d in (1, 15, 30):
    print(d, pricing.prorated_amount(p, date(2026,6,d)))
"
```

## Method

Work the way you would in a real repo:

1. **Run the tests first.** Four fail. Read the failure output before reading
   any source.
2. **Take one failing test.** Read what it asserts and what it got.
3. **Trace from the symptom** to the one function responsible. Don't read from
   the top of the file.
4. **Check that function against its own docstring.** State the mismatch out
   loud before you prompt for anything.
5. **Prioritize.** Money that is wrong in the customer's favour, money that is
   wrong in yours, and money charged twice are not the same severity. Say which
   you're fixing first and why.
6. **Only after the four failures are green**, look for the bugs nobody
   reported. Start with the requirements in each docstring that no test
   touches, and think about what two threads would do.

## The session

45 minutes. Open Claude Code in this directory and paste this:

```
You are running a mock Bloomberg AI-assisted coding interview for me. Play two
roles at once, and label every message with which one is speaking.

ROLE 1 — INTERVIEWER
The repo in this directory is a subscription billing service. Four tests fail.
I have read the README brief, so do not repeat it. Let me work. While I work:
- Do NOT point out bugs, hint at them, or list what is wrong. Ever.
- If I go a whole message without explaining my reasoning, say: "Walk me
  through what you're thinking."
- If I give a vague instruction, push back: "Where specifically, and what
  change?"
- Ask "why does that matter?" and "what would break if you didn't fix it?"
- If I claim something is fixed, ask how I know, and make me show the test.
- If I flag something that is not actually a bug, do not correct me — ask me to
  trace it line by line and let me reach my own conclusion.
- When all four failing tests pass, ask me: "What else is broken that no test
  covers?" and let me keep going.
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

Start by asking me how I plan to approach the codebase.
```

## Self-check afterwards

- Did I run the tests before reading source?
- How long until I said my first sentence out loud?
- Did I fix in severity order, or in the order I happened to find things?
- Did my prompts name a file, a function and a specific change?
- How many planted flaws did I accept without noticing?
- How many bugs did I find that no test covered?
- Did I chase anything that turned out not to be a bug? Why did I believe it?