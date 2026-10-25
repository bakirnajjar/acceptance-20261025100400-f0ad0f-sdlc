"""TASK-006: fixture-only opaque active sessions; no authentication route."""

from hashlib import sha256

import pytest
from flask import Flask

from reset_demo import create_app
from reset_demo.foundation import Account

A = "alex@example.test"
B = "blair@example.test"


@pytest.fixture
def represented_sessions() -> tuple[Flask, str, str, str]:
    """Create two A sessions and one B session without an HTTP fixture route."""
    app = create_app()
    store = app.extensions["reset_demo"].store
    a1 = store.create_session(A)
    a2 = store.create_session(A)
    b1 = store.create_session(B)
    return app, a1, a2, b1


def test_tc_018_account_scoped_revocation(
    represented_sessions: tuple[Flask, str, str, str],
) -> None:
    """TC-018: both A sessions become inactive; B's session stays active."""
    app, a1, a2, b1 = represented_sessions
    store = app.extensions["reset_demo"].store
    assert len({a1, a2, b1}) == 3
    assert all(store.check_session(A, secret) for secret in (a1, a2))
    assert store.check_session(B, b1)
    assert not store.check_session(B, a1)
    assert not store.check_session(A, b1)
    assert not store.check_session(A, "not-a-session")
    assert not store.check_session("missing@example.test", a1)

    records = store.sessions()
    assert len(records) == 3
    assert {record.session_id_digest for record in records} == {
        sha256(secret.encode("ascii")).hexdigest() for secret in (a1, a2, b1)
    }
    assert {record.account_id for record in records} == {A, B}
    assert all(record.active for record in records)
    assert all(secret not in repr(records) for secret in (a1, a2, b1))

    store.revoke_all_sessions(A)
    assert not store.check_session(A, a1)
    assert not store.check_session(A, a2)
    assert store.check_session(B, b1)
    assert {record.account_id for record in store.sessions() if record.active} == {B}
    revoked = store.sessions()
    store.revoke_all_sessions(A)
    assert store.sessions() == revoked


def test_tc_018_sessions_are_private_and_sign_in_does_not_authenticate(
    represented_sessions: tuple[Flask, str, str, str],
) -> None:
    """TC-018: only the store creates sessions; HTTP offers no fixture or login."""
    app, a1, a2, b1 = represented_sessions
    store = app.extensions["reset_demo"].store
    client = app.test_client()
    assert {rule.rule for rule in app.url_map.iter_rules()} == {
        "/",
        "/sign-in",
        "/reset/request",
        "/reset/confirmation",
        "/reset/new",
        "/reset/complete",
        "/reset/unavailable",
        "/reset/<opaque_token>",
        "/static/<path:filename>",
    }
    for path in ("/test/sessions", "/sessions", "/session/create"):
        assert client.get(path).status_code == 404
        assert client.post(path).status_code == 404

    before = store.sessions()
    response = client.post("/sign-in", data={"email": A, "password": "fixture-only"})
    assert response.status_code == 501
    assert "Set-Cookie" not in response.headers
    assert store.sessions() == before
    assert all(
        store.check_session(owner, secret)
        for owner, secret in ((A, a1), (A, a2), (B, b1))
    )
    independent_store = create_app().extensions["reset_demo"].store
    assert independent_store.sessions() == ()
    assert not independent_store.check_session(A, a1)


def test_tc_018_reject_unknown_accounts_and_colliding_or_invalid_bearers() -> None:
    """TC-018: failed creation cannot replace or revive a represented session."""
    store = create_app().extensions["reset_demo"].store
    account = store.get_account(A)
    with pytest.raises(ValueError, match="already exists"):
        store.add_account(
            Account(
                A, "another@example.test", account.password_hash, "another@example.test"
            )
        )
    secret = "x" * 43
    with pytest.raises(ValueError, match="Unknown account"):
        store.create_session("missing@example.test", lambda: secret)
    assert store.sessions() == ()
    assert store.create_session(A, lambda: secret) == secret
    with pytest.raises(ValueError, match="collision"):
        store.create_session(B, lambda: secret)
    for invalid in ("short", "a" * 31, " " * 43, None):
        with pytest.raises(ValueError, match="Invalid session secret"):
            store.create_session(A, lambda value=invalid: value)
    assert len(store.sessions()) == 1
    store.revoke_all_sessions(A)
    assert not store.check_session(A, secret)
    with pytest.raises(ValueError, match="collision"):
        store.create_session(A, lambda: secret)
    assert len(store.sessions()) == 1
