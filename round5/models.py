"""Domain objects. Money is in minor units (kobo). Never floats."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Product:
    sku: str
    name: str
    price: int          # minor units, per unit


@dataclass
class Line:
    product: Product
    quantity: int

    @property
    def amount(self):
        return self.product.price * self.quantity


@dataclass
class Cart:
    cart_id: str
    lines: List[Line] = field(default_factory=list)


@dataclass
class Order:
    order_id: str
    subtotal: int = 0
    discount: int = 0
    shipping: int = 0
    total: int = 0