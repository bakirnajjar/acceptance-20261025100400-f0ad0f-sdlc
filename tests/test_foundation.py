"""TASK-001: synthetic state, private notices, and factory injection."""

import smtplib
import socket
import sys
import tomllib
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import pytest
from flask import Flask

from reset_demo import create_app
from reset_demo.foundation import (
    Account,
    InMemoryStore,
    Notification,
    NotificationSink,
    ScryptPasswordHasher,
    secure_token,
)


def test_tc_001_synthetic_isolated_flask_foundation() -> None:
    """TC-001: two independent fixtures contain only adaptive synthetic hashes."""
    created = datetime(2026, 10, 25, tzinfo=UTC)
    initial_passwords = (secure_token(), secure_token())
    issued_passwords = iter(initial_passwords)
    hasher = ScryptPasswordHasher()
    second_hasher = ScryptPasswordHasher()

    def second_token_factory() -> str:
        return secure_token()

    first_store, second_store = InMemoryStore(), InMemoryStore()
    first_sink, second_sink = NotificationSink(), NotificationSink()

    with (
        patch.object(
            socket.socket, "connect", side_effect=AssertionError("network used")
        ),
        patch.object(smtplib, "SMTP", side_effect=AssertionError("mail used")),
    ):
        first = create_app(
            clock=lambda: created,
            hasher=hasher,
            token_factory=lambda: next(issued_passwords),
            store=first_store,
            sink=first_sink,
        )
        second = create_app(
            clock=lambda: created,
            hasher=second_hasher,
            token_factory=second_token_factory,
            store=second_store,
            sink=second_sink,
        )
        first_client = first.test_client()
        first_page = first_client.get("/")
        second_page = second.test_client().get("/")

    assert isinstance(first, Flask)
    assert first.extensions["reset_demo"].store is first_store
    assert first.extensions["reset_demo"].sink is first_sink
    assert first.extensions["reset_demo"].clock() == created
    assert first.extensions["reset_demo"].hasher is hasher
    assert second.extensions["reset_demo"].hasher is second_hasher
    assert second.extensions["reset_demo"].token_factory is second_token_factory
    assert first.extensions["reset_demo"].now() == created
    assert first.jinja_env.autoescape("index.html")
    assert first_page.status_code == second_page.status_code == 200
    assert b"Reset demo foundation" in first_page.data
    assert len(first_store.accounts()) == len(second_store.accounts()) == 2
    assert first_store is not second_store
    for account in first_store.accounts() + second_store.accounts():
        assert account.id == account.normalized_identifier == account.synthetic_owner
        assert account.normalized_identifier.endswith(".test")
        assert account.password_hash.startswith("scrypt:32768:8:1$")
        assert account.password_hash not in initial_passwords
    assert hasher.verify(
        first_store.get_account("alex@example.test").password_hash, initial_passwords[0]
    )
    assert first_store.get_account("alex@example.test").password_hash != (
        second_store.get_account("alex@example.test").password_hash
    )
    assert first_sink.snapshot() == second_sink.snapshot() == ()

    first_store.add_account(
        Account(
            id="casey@example.test",
            normalized_identifier="casey@example.test",
            password_hash=hasher.hash(secure_token()),
            synthetic_owner="casey@example.test",
        )
    )
    first_sink.record(
        Notification("alex@example.test", "fixture", created, "private-marker")
    )
    assert second_store.get_account("casey@example.test") is None
    assert second_sink.snapshot() == ()
    assert first_sink.snapshot()[0].private_payload == "private-marker"
    assert b"private-marker" not in first_client.get("/").data
    for path in ("/notifications", "/test/sink", "/test/accounts"):
        assert first_client.get(path).status_code == 404
    assert {rule.rule for rule in first.url_map.iter_rules()} <= {
        "/",
        "/static/<path:filename>",
    }


def test_tc_001_store_enforces_synthetic_identity_and_lock() -> None:
    """TC-001: store rejects real identities and serializes duplicate writes."""
    store = InMemoryStore()
    hasher = ScryptPasswordHasher()
    account = Account(
        id="casey@example.test",
        normalized_identifier="casey@example.test",
        password_hash=hasher.hash(secure_token()),
        synthetic_owner="casey@example.test",
    )
    with pytest.raises(ValueError, match="synthetic"):
        store.add_account(
            Account(
                "real", "real@example.com", account.password_hash, "real@example.com"
            )
        )
    with pytest.raises(ValueError, match="synthetic"):
        store.add_account(
            Account(
                "bad",
                "bad@example.com@demo.test",
                account.password_hash,
                "bad@demo.test",
            )
        )
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(_try_add, (store, store), (account, account)))
    assert sorted(results) == ["added", "duplicate"]
    assert store.accounts() == (account,)
    with pytest.raises(ValueError, match="empty"):
        create_app(store=store)


def _try_add(store: InMemoryStore, account: Account) -> str:
    try:
        store.add_account(account)
    except ValueError:
        return "duplicate"
    return "added"


def test_tc_002_local_runtime_and_clock_contract() -> None:
    """TC-002: Python/Flask configuration and aware UTC factory wiring."""
    config = tomllib.loads((Path(__file__).parents[1] / "pyproject.toml").read_text())
    assert sys.version_info[:2] == (3, 12)
    assert config["project"]["requires-python"] == ">=3.12"
    assert any(
        dependency.startswith("flask")
        for dependency in config["project"]["dependencies"]
    )
    assert all(
        "sql" not in dependency.lower() and "smtp" not in dependency.lower()
        for dependency in config["project"]["dependencies"]
    )
    assert isinstance(create_app(), Flask)
    for bad_clock in (
        lambda: datetime(2026, 10, 25),
        lambda: datetime(2026, 10, 25, tzinfo=timezone(timedelta(hours=1))),
    ):
        with pytest.raises(ValueError, match="aware UTC"):
            create_app(clock=bad_clock)


def test_tc_022_private_sink_foundation_only() -> None:
    """TC-022 (foundation): capture is private, memory-only and per instance."""
    first, second = create_app(), create_app()
    sink = first.extensions["reset_demo"].sink
    timestamp = first.extensions["reset_demo"].now()
    notice = Notification("alex@example.test", "fixture", timestamp, "not-a-link")
    sink.record(notice)
    assert sink.snapshot() == (notice,)
    assert second.extensions["reset_demo"].sink.snapshot() == ()
    assert b"not-a-link" not in first.test_client().get("/").data
