"""Position book.

Rules:
  * A position's avg_price is the weighted average price of the shares held.
  * apply() is the only way a position changes.
  * Thread safety: callers MUST hold PositionBook.lock around any
    read-then-write sequence. apply() does not take the lock itself.
"""

import threading

from models import Position


class PositionBook:
    def __init__(self):
        self.positions = {}
        self.lock = threading.Lock()

    def get(self, client_id, symbol):
        key = (client_id, symbol)
        if key not in self.positions:
            self.positions[key] = Position(client_id, symbol)
        return self.positions[key]

    def apply(self, client_id, symbol, quantity, price):
        """Add `quantity` shares bought at `price` to the client's position."""
        pos = self.get(client_id, symbol)
        new_quantity = pos.quantity + quantity
        pos.avg_price = (pos.avg_price * pos.quantity + price * quantity) // new_quantity #wrong formula
        pos.quantity = new_quantity
        pos.lots.append((quantity, price))
        return pos

    def unwind(self, client_id, symbol, quantity):
        """Remove shares from a position, oldest lots first (FIFO)."""
        pos = self.get(client_id, symbol)
        left = quantity
        for lot in pos.lots:
            lot_qty, lot_price = lot
            if lot_qty <= left:
                pos.lots.remove(lot)
                left -= lot_qty
            else:
                pos.lots.remove(lot)
                pos.lots.append((lot_qty - left, lot_price))
                left = 0
            if left == 0:
                break
        pos.quantity -= quantity
        return pos

    def total_exposure(self, symbol):
        total = 0
        for (client_id, sym), pos in self.positions.items():
            if sym == symbol:
                total += pos.quantity * pos.avg_price
        return total