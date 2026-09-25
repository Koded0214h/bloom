"""Fee rules.

Product spec:
  * Fee is 1.5% of the transfer amount.
  * Fees are always rounded UP to the nearest minor unit, never down.
  * Minimum fee is 50 minor units. Maximum fee is 2000 minor units.
  * The SENDER pays the fee, on top of the amount they send.
"""

FEE_RATE = 0.015
MIN_FEE = 50
MAX_FEE = 2000


def fee_for(amount):
    fee = int(amount * FEE_RATE)
    if fee < MIN_FEE:
        fee = MIN_FEE
    if fee > MAX_FEE:
        fee = MAX_FEE
    return fee