"""Checkout totals.

Rules agreed with the business:
  * Bulk discount: if the cart holds 3 OR MORE units in total, 10% comes off
    the subtotal.
  * Shipping is a flat 1,500 kobo, but it is FREE when the amount the customer
    actually pays for goods (subtotal minus discount) is 20,000 or more.
  * total = subtotal - discount + shipping.
  * An empty cart cannot be checked out.
"""

import uuid

import cart as cart_ops
from models import Order

BULK_THRESHOLD = 3
BULK_PERCENT = 10
FLAT_SHIPPING = 1_500
FREE_SHIPPING_FROM = 20_000


def subtotal(cart):
    total = 0
    for line in cart.lines:
        total += line.amount
    return total


def bulk_discount(cart, amount):
    if cart_ops.item_count(cart) > BULK_THRESHOLD:
        return amount * BULK_PERCENT // 100
    return 0


def shipping_for(amount):
    if amount >= FREE_SHIPPING_FROM:
        return 0
    return FLAT_SHIPPING


def checkout(cart):
    order = Order(order_id=str(uuid.uuid4()))
    order.subtotal = subtotal(cart)
    order.discount = bulk_discount(cart, order.subtotal)
    order.shipping = shipping_for(order.subtotal)
    order.total = order.subtotal - order.discount + order.shipping
    return order