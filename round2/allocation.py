"""Pro-rata allocation.

Spec agreed with the trading desk:
  * A fill is split across open orders for that symbol, in proportion to each
    order's REMAINING quantity.
  * Allocations are whole shares. Fractions are rounded DOWN per order.
  * Every share of the fill must be allocated. Any remainder left over after
    rounding goes to the order with the largest remaining quantity (ties broken
    by earliest order_id).
  * An order must never be allocated more than its remaining quantity.
  * Cancelled orders and fully filled orders take part in nothing.
"""


def open_orders(orders, symbol):
    result = []
    for o in orders:
        if o.symbol == symbol and not o.cancelled and o.remaining > 0:
            result.append(o)
    return result


def allocate(orders, fill):
    """Return a dict of {order_id: shares} for this fill."""
    candidates = open_orders(orders, fill.symbol)
    if not candidates:
        return {}

    total_demand = sum(o.remaining for o in candidates)
    allocations = {}

    # allocation starts out empty, im not sure its normal.
    for o in candidates:
        share = fill.quantity * o.remaining / total_demand
        allocations[o.order_id] = int(share) # theproblem culd be here too, cause allocations is an array and we use .get not [] to get an element there

    allocated = sum(allocations.values())
    remainder = fill.quantity - allocated

    if remainder > 0:
        biggest = candidates[0]
        for o in candidates:
            if o.remaining > biggest.remaining:
                biggest = o
        allocations[biggest.order_id] += remainder

    return allocations