# SPDX-License-Identifier: Apache-2.0
"""Shipment dispatch with retry and exponential backoff."""

from __future__ import annotations

import random
import time
from collections.abc import Callable
from dataclasses import dataclass


class ShipmentError(Exception):
    """A dispatch attempt failed. Retryable unless `permanent` is True."""

    def __init__(self, message: str, *, permanent: bool = False) -> None:
        super().__init__(message)
        self.permanent = permanent


@dataclass(frozen=True)
class Shipment:
    tracking_id: str
    carrier: str
    address: str


DispatchFn = Callable[[Shipment], None]


def retry_shipment(
    shipment: Shipment,
    dispatch: DispatchFn,
    *,
    max_attempts: int = 5,
    base_delay_seconds: float = 0.2,
    jitter: float = 0.1,
    sleeper: Callable[[float], None] = time.sleep,
) -> int:
    """Call `dispatch(shipment)` until it succeeds or the attempts are exhausted.

    Transient `ShipmentError` values are retried with exponential backoff
    (`base_delay_seconds * 2 ** attempt`) plus a small random jitter so
    several failed packages do not retry in lockstep. A `ShipmentError`
    marked `permanent` (for example an unknown address) is not retried.
    Returns the 1-based attempt that succeeded.
    """
    last_error: ShipmentError | None = None
    for attempt in range(max_attempts):
        try:
            dispatch(shipment)
            return attempt + 1
        except ShipmentError as exc:
            last_error = exc
            if exc.permanent or attempt == max_attempts - 1:
                raise
            delay = base_delay_seconds * (2 ** attempt)
            delay += random.uniform(0, jitter)
            sleeper(delay)
    assert last_error is not None
    raise last_error
