"""Cart operations.

Rules:
  * add(cart, product, quantity) with a SKU already in the cart increases that
    line's quantity. A cart never holds two lines for the same SKU.
  * quantity must be a positive whole number.
  * remove(cart, sku) removes that SKU's line entirely and returns True.
    Removing a SKU that isn't there returns False.
  * set_quantity(cart, sku, quantity) sets an exact quantity. Setting it to 0
    removes the line.
  * item_count(cart) is the total number of units across all lines.
"""

from models import Line


def find_line(cart, sku):
    for line in cart.lines:
        if line.product.sku == sku:
            return line
    return None


def add(cart, product, quantity=1):
    if quantity <= 0:
        raise ValueError("quantity must be positive")
    cart.lines.append(Line(product=product, quantity=quantity))
    return cart


def remove(cart, sku):
    removed = False
    for line in cart.lines:
        if line.product.sku == sku:
            cart.lines.remove(line)
            removed = True
    return removed


def set_quantity(cart, sku, quantity):
    line = find_line(cart, sku)
    if line is None:
        return False
    line.quantity = quantity
    return True


def item_count(cart):
    total = 0
    for line in cart.lines:
        total += line.quantity
    return total