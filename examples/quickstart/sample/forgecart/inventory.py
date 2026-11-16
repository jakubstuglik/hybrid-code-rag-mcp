# SPDX-License-Identifier: Apache-2.0
"""On-hand stock: reserve units for a checkout, and restock later."""

from __future__ import annotations

from dataclasses import dataclass, field


class InsufficientStock(Exception):
    """Raised when a reservation asks for more units than are on hand."""

    def __init__(self, sku: str, requested: int, available: int) -> None:
        super().__init__(
            f"not enough stock for {sku}: requested {requested}, available {available}"
        )
        self.sku = sku
        self.requested = requested
        self.available = available


@dataclass
class StockService:
    """Tracks on-hand counts by SKU. Reservations are deducted immediately."""

    on_hand: dict[str, int] = field(default_factory=dict)

    def restock(self, sku: str, quantity: int) -> int:
        if quantity <= 0:
            raise ValueError("restock quantity must be positive")
        self.on_hand[sku] = self.on_hand.get(sku, 0) + quantity
        return self.on_hand[sku]

    def available(self, sku: str) -> int:
        return self.on_hand.get(sku, 0)

    def reserve(self, sku: str, quantity: int) -> int:
        """Deduct `quantity` from on-hand stock and return what remains."""
        if quantity <= 0:
            raise ValueError("reserve quantity must be positive")
        available = self.available(sku)
        if available < quantity:
            raise InsufficientStock(sku, quantity, available)
        remaining = available - quantity
        self.on_hand[sku] = remaining
        return remaining

    def release(self, sku: str, quantity: int) -> int:
        """Return previously reserved units to on-hand stock (cancelled checkout)."""
        return self.restock(sku, quantity)
