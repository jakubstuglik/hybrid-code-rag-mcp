# SPDX-License-Identifier: Apache-2.0
"""Charges and refunds, with an idempotency key on each write."""

from __future__ import annotations

from dataclasses import dataclass, field


class PaymentError(Exception):
    """A charge or refund was rejected by the gateway."""


@dataclass(frozen=True)
class Payment:
    payment_id: str
    amount_cents: int
    currency: str
    status: str


@dataclass
class PaymentGateway:
    """Records charges and refunds. Repeated keys replay the first outcome."""

    _by_key: dict[str, Payment] = field(default_factory=dict)
    _next_id: int = 1

    def charge(
        self,
        amount_cents: int,
        *,
        currency: str = "USD",
        idempotency_key: str,
    ) -> Payment:
        if amount_cents <= 0:
            raise PaymentError("charge amount must be positive")
        existing = self._by_key.get(idempotency_key)
        if existing is not None:
            return existing
        payment = Payment(
            payment_id=f"pay_{self._next_id}",
            amount_cents=amount_cents,
            currency=currency,
            status="captured",
        )
        self._next_id += 1
        self._by_key[idempotency_key] = payment
        return payment

    def refund(self, payment_id: str, *, idempotency_key: str) -> Payment:
        """Issue an idempotent refund for a previously captured charge."""
        existing = self._by_key.get(idempotency_key)
        if existing is not None:
            return existing
        original = next((p for p in self._by_key.values() if p.payment_id == payment_id), None)
        if original is None:
            raise PaymentError(f"unknown payment {payment_id}")
        if original.status != "captured":
            raise PaymentError(f"payment {payment_id} is {original.status}, not captured")
        refunded = Payment(
            payment_id=original.payment_id,
            amount_cents=original.amount_cents,
            currency=original.currency,
            status="refunded",
        )
        self._by_key[idempotency_key] = refunded
        return refunded
