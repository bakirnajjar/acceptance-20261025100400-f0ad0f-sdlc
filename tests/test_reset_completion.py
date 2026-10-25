"""TASK-007: transactional reset completion and server-rendered end states."""

import logging
import re
import smtplib
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from threading import Barrier

from reset_demo import create_app
from reset_demo.foundation import ScryptPasswordHasher
from reset_demo.recovery import RecoveryService

A = "alex@example.test"
B = "blair@example.test"
T = datetime(2026, 10, 25, 10, 0, tzinfo=UTC)


class Clock:
    def __init__(self):
        self.value = T

    def __call__(self):
        return self.value


def setup(*, hasher=None):
    clock = Clock()
    app = create_app(clock=clock, hasher=hasher)
    resources = app.extensions["reset_demo"]
    RecoveryService(resources).request_link(A)
    link = resources.sink.snapshot()[0].private_payload
    return app, resources, clock, link


def open_form(app, link):
    client = app.test_client()
    assert client.get(link).headers["Location"] == "/reset/new"
    html = client.get("/reset/new").get_data(as_text=True)
    assert 'name="new_password" type="password"' in html
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match is not None
    return client, match.group(1)


def submit(client, csrf, candidate="fake-new-pass"):
    return client.post(
        "/reset/complete", data={"csrf_token": csrf, "new_password": candidate}
    )


def state(resources):
    return (
        resources.store.accounts(),
        resources.store.reset_tokens(),
        resources.store.sessions(),
        resources.sink.snapshot(),
    )


def assert_private(response, link, candidate):
    public = response.data + repr(tuple(response.headers.items())).encode()
    assert A.encode() not in public
    assert B.encode() not in public
    assert link.encode() not in public
    assert link.removeprefix("/reset/").encode() not in public
    assert candidate.encode() not in public
    assert response.headers["Cache-Control"] == "no-store"
    assert response.headers["Referrer-Policy"] == "no-referrer"


def test_tc_014_complete_rechecks_exact_issuance_deadline():
    """TC-014: last microsecond succeeds; earlier S4 does not extend expiry."""
    app, resources, clock, link = setup()
    clock.value = T + timedelta(minutes=29)
    client, csrf = open_form(app, link)
    clock.value = T + timedelta(minutes=29, seconds=59, microseconds=999999)
    assert submit(client, csrf).status_code == 200
    assert resources.store.reset_tokens()[0].consumed_at_utc == clock.value

    app, resources, clock, link = setup()
    clock.value = T + timedelta(minutes=29)
    client, csrf = open_form(app, link)
    before = state(resources)
    clock.value = T + timedelta(minutes=30)
    failed = submit(client, csrf)
    assert failed.status_code == 303
    assert failed.headers["Location"] == "/reset/unavailable"
    assert state(resources) == before
    assert app.test_client().get(link).headers["Location"] == "/reset/unavailable"
    clock.value += timedelta(microseconds=1)
    assert submit(client, csrf).headers["Location"] == "/reset/unavailable"
    assert state(resources) == before


def test_tc_015_success_commits_hash_token_sessions_and_one_notice(caplog):
    """TC-015: commit all owner effects, render S5 without exposing private data."""
    app, resources, clock, link = setup()
    store = resources.store
    a1, a2, b1 = (
        store.create_session(A),
        store.create_session(A),
        store.create_session(B),
    )
    old_hash = store.get_account(A).password_hash
    b_hash = store.get_account(B).password_hash
    client, csrf = open_form(app, link)
    candidate = "fake-new-pass"
    clock.value += timedelta(minutes=2)
    with caplog.at_level(logging.INFO):
        response = submit(client, csrf, candidate)
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "<!doctype html>" in html
    assert '<h1 id="page-title" tabindex="-1">Password reset complete</h1>' in html
    assert 'role="status"' in html
    assert '<a href="/sign-in">Return to sign in</a>' in html
    assert 'name="new_password"' not in html
    assert_private(response, link, candidate)
    assert (
        A not in caplog.text
        and link not in caplog.text
        and candidate not in caplog.text
    )
    new_hash = store.get_account(A).password_hash
    assert new_hash != old_hash
    assert new_hash.startswith("scrypt:32768:8:1$")
    assert resources.hasher.verify(new_hash, candidate)
    assert not resources.hasher.verify(old_hash, candidate)
    assert store.get_account(B).password_hash == b_hash
    assert store.reset_tokens()[0].consumed_at_utc == clock.value
    assert not store.check_session(A, a1) and not store.check_session(A, a2)
    assert store.check_session(B, b1)
    notices = resources.sink.snapshot()
    assert [notice.kind for notice in notices] == ["reset_link", "password_reset"]
    assert notices[-1].owner == A
    assert notices[-1].created_at_utc == clock.value
    assert candidate not in repr(notices)
    assert client.get_cookie("reset_intent", path="/reset") is None


def test_tc_016_replay_has_no_further_effects():
    """TC-016: consumed link, existing intent and new GET cannot reset twice."""
    app, resources, _, link = setup()
    client, csrf = open_form(app, link)
    assert submit(client, csrf).status_code == 200
    committed = state(resources)
    response = submit(client, csrf, "fake-second-pass")
    assert response.status_code == 303
    assert response.headers["Location"] == "/reset/unavailable"
    assert app.test_client().get(link).headers["Location"] == "/reset/unavailable"
    assert state(resources) == committed
    stored = resources.store.get_account(A).password_hash
    assert resources.hasher.verify(stored, "fake-new-pass")
    assert not resources.hasher.verify(stored, "fake-second-pass")


def test_tc_017_browser_intent_and_csrf_are_required():
    """TC-017: stolen intent, mismatched browser and bad forms do not commit."""
    app, resources, _, link = setup()
    owner, csrf = open_form(app, link)
    other = app.test_client()
    other.get("/reset/request")  # Give the other client its own CSRF session.
    other.set_cookie(
        "reset_intent",
        owner.get_cookie("reset_intent", path="/reset").value,
        path="/reset",
    )
    other_csrf = re.search(
        r'name="csrf_token" value="([^"]+)"',
        other.get("/reset/request").get_data(as_text=True),
    ).group(1)
    before = state(resources)
    assert other.get("/reset/new").headers["Location"] == "/reset/unavailable"
    for client, supplied_csrf in ((other, other_csrf), (app.test_client(), csrf)):
        response = submit(client, supplied_csrf)
        assert response.status_code == 303
        assert response.headers["Location"] == "/reset/unavailable"
        assert_private(response, link, "fake-new-pass")
        assert state(resources) == before
    for supplied_csrf, candidate in (
        (None, "fake-new-pass"),
        ("forged", "fake-new-pass"),
        ("current", ""),
        ("current", "  "),
    ):
        current = re.search(
            r'name="csrf_token" value="([^"]+)"',
            owner.get("/reset/new").get_data(as_text=True),
        ).group(1)
        form = {"new_password": candidate}
        if supplied_csrf is not None:
            form["csrf_token"] = (
                current if supplied_csrf == "current" else supplied_csrf
            )
        response = owner.post("/reset/complete", data=form)
        assert response.status_code == 400
        html = response.get_data(as_text=True)
        assert 'id="reset-error" role="alert" tabindex="-1"' in html
        assert 'aria-describedby="reset-error"' in html
        assert_private(response, link, "fake-new-pass")
        assert state(resources) == before
    assert owner.get("/reset/new").status_code == 200


def test_tc_019_sink_failure_after_append_and_hash_failure_leave_no_effects(
    monkeypatch,
):
    """TC-019: failed prepare or sink append rolls back; retry can commit."""

    class FaultHasher(ScryptPasswordHasher):
        fail = False

        def hash(self, password):
            if self.fail:
                raise RuntimeError("hash unavailable")
            return super().hash(password)

    hasher = FaultHasher()
    app, resources, _, link = setup(hasher=hasher)
    a1, a2 = resources.store.create_session(A), resources.store.create_session(A)
    client, csrf = open_form(app, link)
    before = state(resources)
    hasher.fail = True
    rejected = submit(client, csrf)
    assert rejected.status_code == 503
    assert 'role="alert"' in rejected.get_data(as_text=True)
    assert_private(rejected, link, "fake-new-pass")
    assert state(resources) == before
    hasher.fail = False

    original_record = resources.sink.record

    def append_then_fail(notice):
        original_record(notice)
        raise RuntimeError("sink unavailable")

    monkeypatch.setattr(resources.sink, "record", append_then_fail)
    rejected = submit(client, csrf)
    assert rejected.status_code == 503
    assert 'role="alert"' in rejected.get_data(as_text=True)
    assert_private(rejected, link, "fake-new-pass")
    assert state(resources) == before
    assert resources.store.check_session(A, a1)
    assert resources.store.check_session(A, a2)
    assert client.get("/reset/new").status_code == 200
    monkeypatch.setattr(resources.sink, "record", original_record)
    assert submit(client, csrf).status_code == 200
    assert len(resources.sink.snapshot()) == len(before[-1]) + 1


def test_tc_020_competing_completions_have_exactly_one_winner():
    """TC-020: different clients, intents and passwords race for one link."""
    app, resources, _, link = setup()
    clients = [open_form(app, link), open_form(app, link)]
    a1, a2 = resources.store.create_session(A), resources.store.create_session(A)
    barrier = Barrier(2)
    candidates = ("fake-first-pass", "fake-second-pass")

    def compete(index):
        barrier.wait()
        client, csrf = clients[index]
        return submit(client, csrf, candidates[index])

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(compete, range(2)))
    assert sorted(response.status_code for response in results) == [200, 303]
    assert next(r for r in results if r.status_code == 303).headers["Location"] == (
        "/reset/unavailable"
    )
    winner = next(i for i, r in enumerate(results) if r.status_code == 200)
    stored = resources.store.get_account(A).password_hash
    assert resources.hasher.verify(stored, candidates[winner])
    assert not resources.hasher.verify(stored, candidates[1 - winner])
    assert resources.store.reset_tokens()[0].consumed_at_utc == T
    assert not resources.store.check_session(A, a1)
    assert not resources.store.check_session(A, a2)
    assert [n.kind for n in resources.sink.snapshot()] == [
        "reset_link",
        "password_reset",
    ]
    for index, response in enumerate(results):
        assert_private(response, link, candidates[index])


def test_tc_021_success_and_unavailable_are_accessible_end_states():
    """TC-021: S5 is named and server-rendered; S6 has generic retry links."""
    app, _, _, link = setup()
    client, csrf = open_form(app, link)
    success = submit(client, csrf)
    assert 'role="status"' in success.get_data(as_text=True)
    assert '<a href="/sign-in">Return to sign in</a>' in success.get_data(as_text=True)
    assert ":focus-visible { outline: 3px solid #005fca" in success.get_data(
        as_text=True
    )
    unavailable = client.get(link, follow_redirects=True).get_data(as_text=True)
    assert '<h1 id="page-title" tabindex="-1">Reset unavailable</h1>' in unavailable
    assert 'role="status"' in unavailable
    assert '<a href="/reset/request">Request a new reset link</a>' in unavailable
    assert '<a href="/sign-in">Return to sign in</a>' in unavailable
    assert 'name="new_password"' not in unavailable


def test_tc_022_notices_remain_private_without_outbound_transport(monkeypatch):
    """TC-022: no mail/network call, public sink route or cross-app leakage."""
    calls = []

    def forbidden(*args, **kwargs):
        calls.append((args, kwargs))
        raise AssertionError("External delivery is not part of the demo")

    monkeypatch.setattr(smtplib, "SMTP", forbidden)
    monkeypatch.setattr(urllib.request, "urlopen", forbidden)
    app, resources, _, link = setup()
    isolated = create_app(clock=lambda: T).extensions["reset_demo"]
    client, csrf = open_form(app, link)
    assert submit(client, csrf).status_code == 200
    assert [(n.kind, n.owner) for n in resources.sink.snapshot()] == [
        ("reset_link", A),
        ("password_reset", A),
    ]
    assert isolated.sink.snapshot() == ()
    assert isolated.store.reset_tokens() == ()
    assert calls == []
    for path in ("/sink", "/reset/notifications", "/reset/tokens"):
        response = client.get(path)
        assert response.status_code in (303, 404)
        assert link.encode() not in response.data
