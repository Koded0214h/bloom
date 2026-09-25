"""Pricing rules.

Spec signed off by finance:
  * Proration: when a subscription starts mid-cycle, the customer pays only for
    the days they will actually have the plan, INCLUDING the start day and the
    last day of the cycle. A plan started on the 1st of a 30-day month is
    charged in full.
  * Discount: a coupon's percent_off applies to the SUBTOTAL, before tax.
  * Tax: VAT of 7.5% applies to the amount AFTER discount.
  * Rounding: every money figure is rounded HALF UP to the nearest minor unit.
    Never round half to even, never truncate.
  * A coupon with a currency set is only valid for that currency.
"""

from calendar import monthrange

VAT_RATE = 0.075


def days_in_cycle(on):
    return monthrange(on.year, on.month)[1] # {range, numberofDays}

# 1st - 26th
def prorated_amount(plan, start_on):
    """Charge for the part of the month from start_on to the end of the month."""
    total_days = days_in_cycle(start_on)
    remaining_days = total_days - start_on.day
    return round(plan.monthly_price * remaining_days / total_days) # missing a plus 1 


def apply_coupon(amount, coupon, currency):
    if coupon is None:
        return 0
    return round(amount * coupon.percent_off / 100)


def vat_on(amount):
    return round(amount * VAT_RATE)


def build_invoice(invoice, plan, coupon, start_on=None):
    """Fill in subtotal, discount, tax and total on `invoice`."""
    if start_on is None:
        subtotal = plan.monthly_price
        invoice.lines.append((plan.name + " monthly", subtotal))
    else:
        subtotal = prorated_amount(plan, start_on)
        invoice.lines.append((plan.name + " prorated", subtotal))

    invoice.subtotal = subtotal
    invoice.tax = vat_on(subtotal)
    invoice.discount = apply_coupon(subtotal + invoice.tax, coupon, plan.currency)
    invoice.total = subtotal + invoice.tax - invoice.discount
    return invoice