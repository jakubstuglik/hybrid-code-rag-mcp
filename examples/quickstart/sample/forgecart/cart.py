# SPDX-License-Identifier: Apache-2.0
"""Shopping cart: line items, add/remove, and a priced total."""

from __future__ import annotations

from dataclasses import dataclass, field

from forgecart.pricing import Coupon, calculate_discount


@dataclass(frozen=True)
class CartItem:
    sku: str
    title: str
    unit_price_cents: int
    quantity: int = 1

    def line_total_cents(self) -> int:
        return self.unit_price_cents * self.quantity


@dataclass
class Cart:
    """In-memory cart. Totals are integer cents so currency rounding is exact."""

    items: list[CartItem] = field(default_factory=list)
    coupon: Coupon | None = None

    def add_item(self, item: CartItem) -> None:
        """Add a line, or increase the quantity when the SKU is already present."""
        if item.quantity <= 0:
            raise ValueError("quantity must be positive")
        for index, existing in enumerate(self.items):
            if existing.sku == item.sku:
                self.items[index] = CartItem(
                    sku=existing.sku,
                    title=existing.title,
                    unit_price_cents=existing.unit_price_cents,
                    quantity=existing.quantity + item.quantity,
                )
                return
        self.items.append(item)

    def remove_item(self, sku: str) -> CartItem:
        for index, existing in enumerate(self.items):
            if existing.sku == sku:
                return self.items.pop(index)
        raise KeyError(f"no cart line for sku {sku!r}")

    def subtotal_cents(self) -> int:
        return sum(item.line_total_cents() for item in self.items)

    def apply_coupon(self, coupon: Coupon) -> None:
        self.coupon = coupon

    def calculate_total(self) -> int:
        """Return the payable total in cents, after any coupon discount."""
        subtotal = self.subtotal_cents()
        discount = calculate_discount(subtotal, self.items, self.coupon)
        total = subtotal - discount
        return total if total > 0 else 0
