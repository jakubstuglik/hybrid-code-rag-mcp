# SPDX-License-Identifier: Apache-2.0
"""Discount rules: coupons and quantity breaks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from forgecart.cart import CartItem


@dataclass(frozen=True)
class Coupon:
    """A single-use-style coupon. `percent` is 0–100; `amount_cents` is a flat cut."""

    code: str
    percent: int = 0
    amount_cents: int = 0
    min_subtotal_cents: int = 0


def calculate_discount(
    subtotal_cents: int,
    items: list[CartItem],
    coupon: Coupon | None = None,
) -> int:
    """Return the discount in cents.

    The function stacks two kinds of reduction, in this order:

    1. Quantity breaks: any line with quantity 5 or more gets 10 percent off
       that line; quantity 10 or more gets 15 percent off that line.
    2. A coupon, if one is present and the subtotal reaches its minimum.
       A percent coupon is applied to the subtotal after quantity breaks;
       a flat coupon then subtracts `amount_cents`. The combined discount
       never exceeds the original subtotal.
    """
    if subtotal_cents <= 0:
        return 0

    quantity_discount = 0
    for item in items:
        if item.quantity >= 10:
            quantity_discount += item.line_total_cents() * 15 // 100
        elif item.quantity >= 5:
            quantity_discount += item.line_total_cents() * 10 // 100

    after_breaks = subtotal_cents - quantity_discount
    coupon_discount = 0
    if coupon is not None and subtotal_cents >= coupon.min_subtotal_cents:
        if coupon.percent:
            coupon_discount += after_breaks * coupon.percent // 100
        if coupon.amount_cents:
            coupon_discount += coupon.amount_cents

    total = quantity_discount + coupon_discount
    return total if total < subtotal_cents else subtotal_cents
