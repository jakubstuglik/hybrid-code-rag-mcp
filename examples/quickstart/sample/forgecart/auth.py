# SPDX-License-Identifier: Apache-2.0
"""Session login and expiry for a checkout user."""

from __future__ import annotations

import hashlib
import hmac
import time
from dataclasses import dataclass


class SessionExpired(Exception):
    """The session exists but its `expires_at` is in the past."""

    def __init__(self, session_id: str) -> None:
        super().__init__(f"session {session_id} has expired")
        self.session_id = session_id


@dataclass
class Session:
    session_id: str
    user_id: str
    expires_at: float


class SessionManager:
    """Issues signed session ids and rejects expired or unknown ones."""

    def __init__(self, secret: bytes, ttl_seconds: int = 3600) -> None:
        if not secret:
            raise ValueError("secret must be non-empty")
        self._secret = secret
        self._ttl_seconds = ttl_seconds
        self._sessions: dict[str, Session] = {}

    def login(self, user_id: str, now: float | None = None) -> Session:
        stamp = now if now is not None else time.time()
        expires_at = stamp + self._ttl_seconds
        material = f"{user_id}:{expires_at}".encode()
        session_id = hmac.new(self._secret, material, hashlib.sha256).hexdigest()
        session = Session(session_id=session_id, user_id=user_id, expires_at=expires_at)
        self._sessions[session_id] = session
        return session

    def authenticate(self, session_id: str, now: float | None = None) -> Session:
        """Return the live session, or raise if it is missing or expired."""
        session = self._sessions.get(session_id)
        if session is None:
            raise KeyError(f"unknown session {session_id}")
        stamp = now if now is not None else time.time()
        if stamp >= session.expires_at:
            del self._sessions[session_id]
            raise SessionExpired(session_id)
        return session

    def logout(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)
