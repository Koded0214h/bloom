# Cart & Checkout — AI-assisted interview practice (round 5, easier)

A shopping cart and its checkout maths. Three files, three failing tests, and a
couple of bugs no test covers.

## The brief

**Support:** "Customers say adding the same item twice shows it as two separate
lines in the cart, and the quantity looks wrong."

**Finance:** "Our bulk discount isn't applying to some orders that should
qualify, and we're charging shipping on orders that should ship free."

## Files

| File | What it holds |
|---|---|
| `models.py` | `Product`, `Line`, `Cart`, `Order` |
| `cart.py` | `add`, `remove`, `set_quantity`, `item_count` |
| `checkout.py` | Subtotal, bulk discount, shipping, `checkout()` |
| `tests/test_cart.py` | 5 tests, 3 failing |

Each module's docstring is its spec. Every failing test is a contradiction
between a docstring bullet and the code under it.

## Running

Python 3.9+, no dependencies.

```bash
cd cart-practice
python tests/test_cart.py
```

With pytest:

```bash
pip install pytest
python -m pytest tests/ -q
python -m pytest tests/ -q -k discount
python -m pytest tests/ -q -vv
```

Poke at it:

```bash
python -c "
import cart as c, checkout
from models import Cart, Product
mug = Product('MUG','Mug',5_000)
cart = Cart('c1')
c.add(cart, mug, 1); c.add(cart, mug, 2)
print(cart.lines)
print(checkout.checkout(cart))
"
```

## Method

1. Run the tests. Read all three failures first.
2. Take one. Say what it asserts and what it got.
3. Trace to one function, then name the **exact line and expression** that's
   wrong. Not "the discount function" — "line 28, `>` should be `>=`".
4. Prioritize. Which of these costs the business money, and which costs the
   customer money? Fix in that order and say why.
5. When the three are green, hunt the silent bugs: read each docstring bullet
   and ask which test proves it. The bullets with no test are where to look.

## The session

30 minutes for this one. Open Claude Code here and paste:

```
You are running a mock Bloomberg AI-assisted coding interview for me. Play two
roles at once, and label every message with which one is speaking.

ROLE 1 — INTERVIEWER
The repo in this directory is a cart and checkout service. Three tests fail. I
have read the brief in the README, so do not repeat it. Let me work. While I
work:
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
- When all three failing tests pass, ask: "What else is broken that no test
  covers?" and let me keep going.
- Tell me when 15 and 30 minutes have passed.

ROLE 2 — THE AI ASSISTANT
Act as a normal, confident coding assistant. I give you prompts; you write the
code, I never do. But in roughly 1 of every 3 responses, introduce ONE subtle
flaw: an off-by-one, a boundary flipped, an unhandled edge case
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
- How many planted flaws did I accept without noticing?
- How many silent bugs did I find after the tests went green?
- Did I chase anything that wasn't a bug?