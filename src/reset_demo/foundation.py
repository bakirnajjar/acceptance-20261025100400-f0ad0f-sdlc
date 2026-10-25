"""Process-local synthetic account and private notification foundations."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from secrets import token_urlsafe
from threading import RLock
from typing import Protocol

from werkzeug.security import check_password_hash, generate_password_hash

Clock = Callable[[], datetime]
TokenFactory = Callable[[], str]


def utc_now() -> datetime:
    """Return an aware UTC time for expiry and notification timestamps."""
    return datetime.now(UTC)


def secure_token() -> str:
    """Generate a CSPRNG-backed, 256-bit random URL-safe secret."""
    return token_urlsafe(32)


class PasswordHasher(Protocol):
    def hash(self, password: str) -> str: ...

    def verify(self, password_hash: str, password: str) -> bool: ...


class ScryptPasswordHasher:
    """Werkzeug scrypt with N=32768, r=8, p=1 and a random per-hash salt."""

    def hash(self, password: str) -> str:
        return generate_password_hash(password, method="scrypt:32768:8:1")

    def verify(self, password_hash: str, password: str) -> bool:
        return check_password_hash(password_hash, password)


def _synthetic_address(address: str) -> bool:
    local, separator, domain = address.partition("@")
    return bool(
        local
        and separator
        and domain.endswith(".test")
        and domain != ".test"
        and "@" not in domain
        and not any(char.isspace() for char in address)
    )


@dataclass(frozen=True)
class Account:
    id: str
    normalized_identifier: str
    password_hash: str
    synthetic_owner: str


@dataclass(frozen=True)
class ActiveSession:
    """Server-held session metadata; never contains the bearer secret."""

    session_id_digest: str
    account_id: str
    active: bool = True


class InMemoryStore:
    """One-process account, reset and session state guarded by one lock."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._accounts: dict[str, Account] = {}
        self._accepted_requests: dict[str, tuple[datetime, ...]] = {}
        self._reset_tokens: dict[str, ResetToken] = {}
        self._reset_intents: dict[str, ResetIntent] = {}
        self._sessions: dict[str, ActiveSession] = {}

    def add_account(self, account: Account) -> None:
        if (
            not _synthetic_address(account.normalized_identifier)
            or not _synthetic_address(account.synthetic_owner)
            or account.normalized_identifier != account.normalized_identifier.lower()
        ):
            raise ValueError("Only normalized synthetic .test accounts are allowed")
        with self._lock:
            if account.normalized_identifier in self._accounts or any(
                existing.id == account.id for existing in self._accounts.values()
            ):
                raise ValueError("Account already exists")
            self._accounts[account.normalized_identifier] = account

    def get_account(self, identifier: str) -> Account | None:
        with self._lock:
            return self._accounts.get(identifier.strip().lower())

    def accounts(self) -> tuple[Account, ...]:
        with self._lock:
            return tuple(self._accounts.values())

    def create_session(
        self, account_id: str, token_factory: TokenFactory = secure_token
    ) -> str:
        """Create an opaque bearer for a known account; retain only its digest.

        This is a private store operation for fixture creation until a separate
        authenticated sign-in flow is designed. No HTTP route calls it.
        """
        with self._lock:
            if not any(account.id == account_id for account in self._accounts.values()):
                raise ValueError("Unknown account")
            secret = token_factory()
            if (
                not isinstance(secret, str)
                or re.fullmatch(r"[A-Za-z0-9_-]{32,}", secret) is None
            ):
                raise ValueError("Invalid session secret")
            digest = sha256(secret.encode("ascii")).hexdigest()
            if digest in self._sessions:
                raise ValueError("Session collision")
            self._sessions[digest] = ActiveSession(digest, account_id)
            return secret

    def check_session(self, account_id: str, secret: str) -> bool:
        """Check the server-side activity and owner, not a client-only cookie."""
        if (
            not isinstance(secret, str)
            or re.fullmatch(r"[A-Za-z0-9_-]{32,}", secret) is None
        ):
            return False
        digest = sha256(secret.encode("ascii")).hexdigest()
        with self._lock:
            session = self._sessions.get(digest)
            return (
                session is not None
                and session.account_id == account_id
                and session.active
            )

    def revoke_all_sessions(self, account_id: str) -> None:
        """Revoke every represented session for this owner under the store lock."""
        with self._lock:
            self._sessions = {
                digest: (
                    ActiveSession(digest, session.account_id, active=False)
                    if session.account_id == account_id
                    else session
                )
                for digest, session in self._sessions.items()
            }

    def sessions(self) -> tuple[ActiveSession, ...]:
        """Private immutable snapshot for verifying represented session state."""
        with self._lock:
            return tuple(self._sessions.values())

    def accepted_requests(self, account_id: str) -> tuple[datetime, ...]:
        """Return a private, immutable snapshot of committed issuances."""
        with self._lock:
            return self._accepted_requests.get(account_id, ())

    def reset_tokens(self) -> tuple[ResetToken, ...]:
        """Return private token metadata; raw bearer secrets are never stored here."""
        with self._lock:
            return tuple(self._reset_tokens.values())

    def get_reset_token(self, token_digest: str) -> ResetToken | None:
        with self._lock:
            return self._reset_tokens.get(token_digest)

    def reset_intents(self) -> tuple[ResetIntent, ...]:
        """Return metadata only; neither the link nor the intent secret is stored."""
        with self._lock:
            return tuple(self._reset_intents.values())

    def create_reset_intent(
        self,
        raw_token: str,
        browser_binding: str,
        now: datetime,
        token_factory: TokenFactory = secure_token,
    ) -> str | None:
        """Atomically check an unused link and mint a short-lived browser-bound intent."""
        if (
            not isinstance(raw_token, str)
            or re.fullmatch(r"[A-Za-z0-9_-]{32,256}", raw_token) is None
            or not isinstance(browser_binding, str)
            or re.fullmatch(r"[A-Za-z0-9_-]{32,256}", browser_binding) is None
        ):
            return None
        token_digest = sha256(raw_token.encode("ascii")).hexdigest()
        with self._lock:
            token = self._reset_tokens.get(token_digest)
            if not self._eligible_reset_token(token, now):
                return None
            secret = token_factory()
            if (
                not isinstance(secret, str)
                or re.fullmatch(r"[A-Za-z0-9_-]{32,256}", secret) is None
            ):
                raise ValueError("Invalid reset intent secret")
            intent_digest = sha256(secret.encode("ascii")).hexdigest()
            if (
                intent_digest in self._reset_intents
                or intent_digest in self._reset_tokens
                or secret == browser_binding
            ):
                raise ValueError("Reset intent collision")
            self._reset_intents[intent_digest] = ResetIntent(
                intent_digest,
                token_digest,
                now + timedelta(minutes=5),
                sha256(browser_binding.encode("ascii")).hexdigest(),
            )
            return secret

    def check_reset_intent(
        self, secret: str | None, browser_binding: str | None, now: datetime
    ) -> bool:
        """Recheck both intent lifetime and original issuance deadline on every GET."""
        digests = self._intent_digests(secret, browser_binding)
        if digests is None:
            return False
        intent_digest, binding_digest = digests
        with self._lock:
            intent = self._reset_intents.get(intent_digest)
            return bool(
                intent is not None
                and intent.browser_digest == binding_digest
                and now < intent.expires_at_utc
                and self._eligible_reset_token(
                    self._reset_tokens.get(intent.token_digest), now
                )
            )

    @staticmethod
    def _intent_digests(
        secret: str | None, browser_binding: str | None
    ) -> tuple[str, str] | None:
        if (
            not isinstance(secret, str)
            or re.fullmatch(r"[A-Za-z0-9_-]{32,256}", secret) is None
            or not isinstance(browser_binding, str)
            or re.fullmatch(r"[A-Za-z0-9_-]{32,256}", browser_binding) is None
        ):
            return None
        return (
            sha256(secret.encode("ascii")).hexdigest(),
            sha256(browser_binding.encode("ascii")).hexdigest(),
        )

    def complete_reset_intent(
        self,
        secret: str | None,
        browser_binding: str | None,
        password: str,
        clock: Clock,
        hasher: PasswordHasher,
        sink: NotificationSink,
    ) -> bool:
        """Recheck and publish all owner effects as one process-local commit."""
        digests = self._intent_digests(secret, browser_binding)
        if digests is None or not isinstance(password, str) or not password.strip():
            return False
        intent_digest, binding_digest = digests
        with self._lock:
            now = clock()
            intent = self._reset_intents.get(intent_digest)
            if (
                intent is None
                or intent.browser_digest != binding_digest
                or now >= intent.expires_at_utc
            ):
                return False
            token = self._reset_tokens.get(intent.token_digest)
            if not self._eligible_reset_token(token, now):
                return False
            account = next(
                (a for a in self._accounts.values() if a.id == token.account_id),
                None,
            )
            if account is None:
                return False

            # Stage every potentially failing operation before touching published state.
            password_hash = hasher.hash(password)
            if not isinstance(password_hash, str) or not password_hash:
                raise ValueError("Invalid password hash")
            accounts = {
                **self._accounts,
                account.normalized_identifier: replace(
                    account, password_hash=password_hash
                ),
            }
            tokens = {
                **self._reset_tokens,
                token.token_digest: replace(token, consumed_at_utc=now),
            }
            sessions = {
                digest: (
                    replace(held, active=False)
                    if held.account_id == account.id
                    else held
                )
                for digest, held in self._sessions.items()
            }
            notice = Notification(
                account.synthetic_owner,
                "password_reset",
                now,
                "Your password has been reset.",
            )

            def commit() -> None:
                self._accounts, self._reset_tokens, self._sessions = (
                    accounts,
                    tokens,
                    sessions,
                )

            sink.record_atomically(notice, commit)
            return True

    @staticmethod
    def _eligible_reset_token(token: ResetToken | None, now: datetime) -> bool:
        return bool(
            token is not None
            and token.consumed_at_utc is None
            and token.issued_at_utc <= now < token.issued_at_utc + timedelta(minutes=30)
        )

    def issue_if_eligible(
        self,
        identifier: str,
        clock: Clock,
        create_issue: Callable[[Account, datetime], tuple[ResetToken, Notification]],
        sink: NotificationSink,
    ) -> None:
        """Serialize the account check, trailing-hour limit and private commit."""
        with self._lock:
            now = clock()
            account = self._accounts.get(identifier)
            if account is None:
                return
            previous = self._accepted_requests.get(account.id, ())
            recent = tuple(t for t in previous if t > now - timedelta(hours=1))
            if len(recent) >= 5:
                return

            token, notice = create_issue(account, now)
            if token.token_digest in self._reset_tokens:
                raise ValueError("Reset token collision")
            accepted = {**self._accepted_requests, account.id: (*recent, now)}
            tokens = {**self._reset_tokens, token.token_digest: token}

            def commit() -> None:
                self._accepted_requests, self._reset_tokens = accepted, tokens

            sink.record_atomically(notice, commit)


@dataclass(frozen=True)
class ResetToken:
    token_digest: str
    account_id: str
    issued_at_utc: datetime
    consumed_at_utc: datetime | None = None


@dataclass(frozen=True)
class ResetIntent:
    intent_digest: str
    token_digest: str
    expires_at_utc: datetime
    browser_digest: str


@dataclass(frozen=True)
class Notification:
    owner: str
    kind: str
    created_at_utc: datetime
    private_payload: str


class NotificationSink:
    """A private in-memory record of notices, never an outbound transport."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._notifications: list[Notification] = []

    def record(self, notification: Notification) -> None:
        with self._lock:
            self._notifications.append(notification)

    def record_atomically(
        self, notification: Notification, commit: Callable[[], None]
    ) -> None:
        """Undo even an append-then-raise sink failure before publishing store state."""
        with self._lock:
            previous = self._notifications[:]
            try:
                self.record(notification)
                commit()
            except Exception:
                self._notifications[:] = previous
                raise

    def snapshot(self) -> tuple[Notification, ...]:
        with self._lock:
            return tuple(self._notifications)


@dataclass(frozen=True)
class AppResources:
    store: InMemoryStore
    sink: NotificationSink
    clock: Clock
    hasher: PasswordHasher
    token_factory: TokenFactory

    def now(self) -> datetime:
        now = self.clock()
        if now.tzinfo is None or now.utcoffset() != timedelta(0):
            raise ValueError("Clock must return an aware UTC datetime")
        return now


def seed_synthetic_accounts(resources: AppResources) -> None:
    """Create demo identities without a stored or hard-coded initial password."""
    if resources.store.accounts():
        raise ValueError("App store must be empty before synthetic seeding")
    for identifier in ("alex@example.test", "blair@example.test"):
        initial_password = resources.token_factory()
        resources.store.add_account(
            Account(
                id=identifier,
                normalized_identifier=identifier,
                password_hash=resources.hasher.hash(initial_password),
                synthetic_owner=identifier,
            )
        )
