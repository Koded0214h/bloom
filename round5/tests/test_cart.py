"""
Run:
    python tests/test_cart.py          # full summary, no early exit
    python -m pytest tests/ -q         # after: pip install pytest

Three of these fail on a clean checkout. Two pass.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cart as cart_ops
import checkout
from models import Cart, Product

MUG = Product("MUG", "Mug", 5_000)        # 50.00
TEE = Product("TEE", "T-shirt", 12_000)   # 120.00


def new_cart():
    return Cart(cart_id="c1")


# --- failing: reported by support -----------------------------------------

def test_adding_same_sku_merges_into_one_line():
    c = new_cart()
    cart_ops.add(c, MUG, 1)
    cart_ops.add(c, MUG, 2)
    assert len(c.lines) == 1
    assert c.lines[0].quantity == 3


def test_bulk_discount_at_exactly_three_units():
    """Spec: 3 or more units gets 10% off."""
    c = new_cart()
    cart_ops.add(c, MUG, 3)                 # 150.00
    order = checkout.checkout(c)
    assert order.discount == 1_500


# --- failing: reported by finance -----------------------------------------

def test_free_shipping_uses_the_discounted_amount():
    """
    2 tees + 1 mug = 290.00 subtotal, 10% off = 261.00 paid for goods.
    That is above the 200.00 free-shipping line, so shipping is free.
    """
    c = new_cart()
    cart_ops.add(c, TEE, 2)
    cart_ops.add(c, MUG, 1)
    order = checkout.checkout(c)
    assert order.discount == 2_900
    assert order.shipping == 0
    assert order.total == 26_100


# --- passing --------------------------------------------------------------

def test_remove_returns_false_for_missing_sku():
    c = new_cart()
    assert cart_ops.remove(c, "NOPE") is False


def test_item_count_adds_up():
    c = new_cart()
    cart_ops.add(c, MUG, 2)
    cart_ops.add(c, TEE, 1)
    assert cart_ops.item_count(c) == 3


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print("PASS ", t.__name__)
        except AssertionError as e:
            failed += 1
            print("FAIL ", t.__name__, "-", e or "assertion failed")
        except Exception as e:
            failed += 1
            print("ERROR", t.__name__, "-", type(e).__name__, e)
    print(f"\n{len(tests) - failed} passed, {failed} failed")