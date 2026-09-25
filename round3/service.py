"""
Billing service — the layer the API and the nightly job both call.

Requirements:
  1. run_cycle() charges every billable subscription once per cycle.
  2. charge() is retried by the job runner on failure, so it must be
     idempotent: the same idempotency_key must never produce a second charge.
  3. A failed payment moves the subscription to "past_due". A successful one
     moves it back to "active".
  4. A coupon that is restricted to a currency must not apply to a
     subscription in another currency.
  5. total_revenue() reports money actually collected, per currency.
  6. Worker threads call charge() concurrently.
"""

import uuid

import pricing
from models import Charge, Invoice


class PaymentDeclined(Exception):
    pass


class BillingService:
    def __init__(self, repo, gateway):
        self.repo = repo
        self.gateway = gateway

    def invoice_for(self, subscription, start_on=None):
        invoice = Invoice(
            invoice_id=str(uuid.uuid4()),
            subscription_id=subscription.subscription_id,
        )
        return pricing.build_invoice(
            invoice, subscription.plan, subscription.coupon, start_on
        )

    def charge(self, subscription, idempotency_key, start_on=None):
        invoice = self.invoice_for(subscription, start_on)

        charge = Charge(
            charge_id=str(uuid.uuid4()),
            subscription_id=subscription.subscription_id,
            amount=invoice.total,
            currency=subscription.plan.currency,
            status="pending",
            idempotency_key=idempotency_key,
        )
        self.repo.save_charge(charge)

        existing = self.repo.charge_by_key(idempotency_key)
        if existing is not None and existing.status == "succeeded":
            return existing

        try:
            self.gateway.charge(subscription.customer_id, invoice.total)
            charge.status = "succeeded"
            subscription.status = "active"
        except PaymentDeclined:
            charge.status = "failed"
            subscription.status = "past_due"

        return charge

    def run_cycle(self):
        charged = []
        for s in self.repo.find_billable():
            key = s.subscription_id + "-cycle"
            charged.append(self.charge(s, key))
        return charged

    def total_revenue(self):
        total = 0
        for c in self.repo.charges.values():
            if c.status == "succeeded":
                total += c.amount
        return total