"""TASK-003 private issuance tests; TC-007 HTTP parity awaits route wiring."""

from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from threading import Lock

import pytest

from reset_demo import create_app
from reset_demo.foundation import (
    InMemoryStore,
    Notification,
    NotificationSink,
    secure_token,
)
from reset_demo.recovery import IssuanceError, RecoveryService

T = datetime(2026, 10, 25, 10, 0, tzinfo=UTC)
A = "alex@example.test"
B = "blair@example.test"


class Clock:
    def __init__(self) -> None:
        self.value = T

    def __call__(self) -> datetime:
        return self.value


class TokenFactory:
    def __init__(self) -> None:
        self.calls = 0
        self.fail = False
        self.repeat: str | None = None
        self._lock = Lock()

    def __call__(self) -> str:
        with self._lock:
            self.calls += 1
            if self.fail:
                raise RuntimeError(
                    "private injected token failure for alex@example.test"
                )
            if self.repeat is not None:
                return self.repeat
            return secure_token()


class FailingSink(NotificationSink):
    def __init__(self) -> None:
        super().__init__()
        self.fail_after_append = False
        self.fail_before_append = False

    def record(self, notification: Notification) -> None:
        if self.fail_before_append:
            raise RuntimeError("private injected sink failure for alex@example.test")
        super().record(notification)
        if self.fail_after_append:
            raise RuntimeError("private injected sink failure after append")


def fixture(
    *,
    sink: NotificationSink | None = None,
) -> tuple[RecoveryService, InMemoryStore, Clock, TokenFactory, NotificationSink]:
    clock = Clock()
    tokens = TokenFactory()
    sink = sink if sink is not None else NotificationSink()
    app = create_app(clock=clock, token_factory=tokens, sink=sink)
    resources = app.extensions["reset_demo"]
    return RecoveryService(resources), resources.store, clock, tokens, sink


def test_tc_008_fifth_sixth_and_trailing_hour_boundary() -> None:
    """TC-008: the earliest acceptance leaves at exactly T+1h."""
    service, store, clock, tokens, sink = fixture()
    assert all(service.request_link(A) is None for _ in range(5))
    assert store.accepted_requests(A) == (T,) * 5
    assert len(store.reset_tokens()) == len(sink.snapshot()) == 5
    assert all(token.issued_at_utc == T for token in store.reset_tokens())
    assert all(token.consumed_at_utc is None for token in store.reset_tokens())
    assert all(
        notification.owner == A and notification.kind == "reset_link"
        for notification in sink.snapshot()
    )
    first_token = sink.snapshot()[0].private_payload.removeprefix("/reset/")
    assert (
        store.get_reset_token(sha256(first_token.encode()).hexdigest())
        == store.reset_tokens()[0]
    )
    assert first_token not in repr(store.reset_tokens())

    clock.value = T + timedelta(minutes=30)
    assert service.request_link(A) is None
    clock.value = T + timedelta(hours=1, microseconds=-1)
    assert service.request_link(A) is None
    assert tokens.calls == 7  # two initial seed passwords, five links
    assert store.accepted_requests(A) == (T,) * 5
    assert len(store.reset_tokens()) == len(sink.snapshot()) == 5

    clock.value = T + timedelta(hours=1)
    assert service.request_link(A) is None
    assert store.accepted_requests(A) == (clock.value,)
    assert len(store.reset_tokens()) == len(sink.snapshot()) == 6
    assert store.reset_tokens()[-1].issued_at_utc == clock.value


def test_tc_009_concurrent_normalized_account_scoped_requests() -> None:
    """TC-009: mixed spelling and whitespace cannot bypass the serialized cap."""
    service, store, _, tokens, sink = fixture()
    identifiers = (
        [A, " ALEX@EXAMPLE.TEST ", "Alex@Example.Test"] * 12
        + [B, " BLAIR@EXAMPLE.TEST ", B, B]
        + ["missing@example.test"] * 8
    )
    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(service.request_link, identifiers))

    assert results == [None] * len(identifiers)
    assert store.accepted_requests(A) == (T,) * 5
    assert store.accepted_requests(B) == (T,) * 4
    assert store.accepted_requests("missing@example.test") == ()
    assert len(store.reset_tokens()) == len(sink.snapshot()) == 9
    assert tokens.calls == 11  # two initial seed passwords, nine links
    assert {notice.owner for notice in sink.snapshot()} == {A, B}
    assert len({notice.private_payload for notice in sink.snapshot()}) == 9
    assert len({token.token_digest for token in store.reset_tokens()}) == 9
    assert service.request_link(" MISSING@EXAMPLE.TEST ") is None
    assert tokens.calls == 11
    assert service.request_link(B) is None
    assert service.request_link(B) is None
    assert store.accepted_requests(B) == (T,) * 5
    assert len(sink.snapshot()) == 10


def test_tc_010_token_and_sink_failures_do_not_commit() -> None:
    """TC-010: factory, pre-append and post-append failures preserve all state."""
    sink = FailingSink()
    service, store, clock, tokens, _ = fixture(sink=sink)
    for _ in range(4):
        service.request_link(A)
    accepted, records, notices = (
        store.accepted_requests(A),
        store.reset_tokens(),
        sink.snapshot(),
    )
    clock.value = T + timedelta(minutes=1)

    tokens.fail = True
    with pytest.raises(
        IssuanceError, match="Reset request could not be processed"
    ) as exc:
        service.request_link(A)
    assert A not in str(exc.value)
    tokens.fail = False

    sink.fail_before_append = True
    with pytest.raises(IssuanceError, match="Reset request could not be processed"):
        service.request_link(A)
    sink.fail_before_append = False

    sink.fail_after_append = True
    with pytest.raises(IssuanceError, match="Reset request could not be processed"):
        service.request_link(A)
    sink.fail_after_append = False

    assert store.accepted_requests(A) == accepted
    assert store.reset_tokens() == records
    assert sink.snapshot() == notices
    assert service.request_link(A) is None
    assert store.accepted_requests(A) == (*accepted, clock.value)
    assert len(store.reset_tokens()) == len(sink.snapshot()) == 5
    last = sink.snapshot()[-1]
    assert last.owner == A
    assert (
        store.get_reset_token(
            sha256(last.private_payload.removeprefix("/reset/").encode()).hexdigest()
        )
        == store.reset_tokens()[-1]
    )


def test_tc_010_collision_and_expired_window_failure_preserve_state() -> None:
    """TC-010: duplicate secret and failed prune cannot lose a previous record."""
    service, store, clock, tokens, sink = fixture()
    service.request_link(A)
    before = (store.accepted_requests(A), store.reset_tokens(), sink.snapshot())
    tokens.repeat = sink.snapshot()[0].private_payload.removeprefix("/reset/")
    with pytest.raises(IssuanceError, match="Reset request could not be processed"):
        service.request_link(A)
    assert (store.accepted_requests(A), store.reset_tokens(), sink.snapshot()) == before

    tokens.repeat = None
    clock.value = T + timedelta(hours=1)
    tokens.fail = True
    with pytest.raises(IssuanceError, match="Reset request could not be processed"):
        service.request_link(A)
    assert (store.accepted_requests(A), store.reset_tokens(), sink.snapshot()) == before
    tokens.fail = False
    service.request_link(A)
    assert store.accepted_requests(A) == (clock.value,)
    assert len(store.reset_tokens()) == len(sink.snapshot()) == 2
