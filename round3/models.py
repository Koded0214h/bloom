"""Domain objects. All money is in minor units (kobo/cents). Never floats."""

from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional


@dataclass
class Plan:
    plan_id: str
    name: str
    monthly_price: int          # minor units
    currency: str = "NGN"


@dataclass
class Coupon:
    code: str
    percent_off: int            # 0-100
    currency: Optional[str] = None   # None = valid for any currency


@dataclass
class Subscription:
    subscription_id: str
    customer_id: str
    plan: Plan
    started_on: date
    status: str = "active"           # active | past_due | cancelled
    cancel_at_period_end: bool = False
    coupon: Optional[Coupon] = None


@dataclass
class Charge:
    charge_id: str
    subscription_id: str
    amount: int
    currency: str
    status: str                      # pending | succeeded | failed
    idempotency_key: str


@dataclass
class Invoice:
    invoice_id: str
    subscription_id: str
    subtotal: int = 0
    discount: int = 0
    tax: int = 0
    total: int = 0
    lines: List[tuple] = field(default_factory=list)   # (description, amount)