"""Domain objects for the trade allocation service.

Quantities are whole shares. Prices are in minor units (cents) to avoid floats.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Order:
    order_id: str
    client_id: str
    symbol: str
    quantity: int           # total shares the client asked for
    filled: int = 0         # shares allocated so far
    cancelled: bool = False

    @property
    def remaining(self):
        return self.quantity - self.filled


@dataclass
class Fill:
    """An execution that came back from the exchange, to be split across orders."""
    fill_id: str
    symbol: str
    quantity: int
    price: int


@dataclass
class Position:
    client_id: str
    symbol: str
    quantity: int = 0
    avg_price: int = 0      # weighted average entry price, minor units
    lots: List[tuple] = field(default_factory=list)   # (quantity, price)