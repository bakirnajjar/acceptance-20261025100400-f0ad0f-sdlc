"""TASK-005: link entry, intent handoff and unavailable reset completion."""

import logging
import re
from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from reset_demo import PathFreeRequestHandler, create_app
from reset_demo.recovery import RecoveryService

T = datetime(2026, 10, 25, 10, 0, tzinfo=UTC)
A = "alex@example.test"
B = "blair@example.test"


class Clock:
    def __init__(self) -> None:
        self.value = T

    def __call__(self) -> datetime:
        return self.value


def fixture():
    clock = Clock()
    app = create_app(clock=clock)
    resources = app.extensions["reset_demo"]
    service = RecoveryService(resources)
    service.request_link(A)
    return app, resources, clock, resources.sink.snapshot()[0].private_payload


def private_state(resources):
    return (
        resources.store.accounts(),
        resources.store.reset_tokens(),
        resources.store.sessions(),
        resources.sink.snapshot(),
    )


def assert_private_response(response, raw):
    assert "no-store" in response.headers["Cache-Control"]
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert raw.encode() not in response.data
    assert raw not in repr(tuple(response.headers.items()))


def test_tc_012_link_get_twice_is_unused_with_secret_free_browser_handoff(caplog):
    """TC-012: two GETs reach S4 without consuming a bearer or exposing it."""
    app, resources, _, link = fixture()
    client = app.test_client()
    raw = link.removeprefix("/reset/")
    before = private_state(resources)
    with caplog.at_level(logging.INFO):
        for _ in range(2):
            redirect = client.get(link)
            assert redirect.status_code == 303
            assert redirect.headers["Location"] == "/reset/new"
            assert_private_response(redirect, raw)
            cookie = client.get_cookie("reset_intent", path="/reset")
            assert cookie is not None and raw not in cookie.value
            cookie_header = next(
                value
                for value in redirect.headers.getlist("Set-Cookie")
                if value.startswith("reset_intent=")
            )
            assert "HttpOnly" in cookie_header
            assert "SameSite=Lax" in cookie_header
            assert "Path=/reset" in cookie_header
            assert "Secure" not in cookie_header
            page = client.get("/reset/new")
            html = page.get_data(as_text=True)
            assert page.status_code == 200
            assert_private_response(page, raw)
            assert "<!doctype html>" in html
            assert '<h1 id="page-title" tabindex="-1">' in html
            assert '<label for="new-password">New password</label>' in html
            assert 'name="new_password" type="password"' in html
            assert 'name="csrf_token" value="' in html
            assert 'action="/reset/complete" method="post"' in html
            assert '<button type="submit">Reset password</button>' in html
            assert ":focus-visible { outline: 3px solid #005fca" in html
            assert cookie.value not in html
            assert private_state(resources) == before
    assert raw not in caplog.text
    assert len(resources.store.reset_intents()) == 2
    assert raw not in repr(resources.store.reset_intents())
    assert all(
        intent.token_digest == resources.store.reset_tokens()[0].token_digest
        for intent in resources.store.reset_intents()
    )

    secure = app.test_client().get(link, environ_overrides={"wsgi.url_scheme": "https"})
    assert all("Secure" in cookie for cookie in secure.headers.getlist("Set-Cookie"))
    assert_private_response(secure, raw)


def test_tc_013_unknown_malformed_used_and_direct_new_are_unavailable():
    """TC-013: all rejected links lead to S6, without a reset form or mutation."""
    app, resources, _, link = fixture()
    token = resources.store.reset_tokens()[0]
    with resources.store._lock:
        resources.store._reset_tokens[token.token_digest] = replace(
            token,
            consumed_at_utc=T,
        )
    before = private_state(resources)
    for target in (link, "/reset/unknown", "/reset/" + "z" * 43, "/reset/%25"):
        client = app.test_client()
        response = client.get(target)
        assert response.status_code == 303
        assert response.headers["Location"] == "/reset/unavailable"
        assert_private_response(response, link.removeprefix("/reset/"))
        unavailable = client.get(response.headers["Location"])
        html = unavailable.get_data(as_text=True)
        assert unavailable.status_code == 200
        assert_private_response(unavailable, link.removeprefix("/reset/"))
        assert '<h1 id="page-title" tabindex="-1">Reset unavailable</h1>' in html
        assert 'role="status"' in html
        assert '<a href="/reset/request">Request a new reset link</a>' in html
        assert '<a href="/sign-in">Return to sign in</a>' in html
        assert 'name="new_password"' not in html
        assert client.get("/reset/new").headers["Location"] == "/reset/unavailable"
        assert private_state(resources) == before


def test_tc_014_issuance_deadline_and_intent_deadline_rechecked_on_get():
    """TC-014: 30 minutes starts at issuance, even if S4 was visited earlier."""
    app, resources, clock, link = fixture()
    client = app.test_client()
    clock.value = T + timedelta(minutes=29, seconds=59, microseconds=999999)
    assert client.get(link).headers["Location"] == "/reset/new"
    assert client.get("/reset/new").status_code == 200
    clock.value = T + timedelta(minutes=30)
    assert client.get("/reset/new").headers["Location"] == "/reset/unavailable"
    assert client.get(link).headers["Location"] == "/reset/unavailable"
    clock.value += timedelta(microseconds=1)
    assert client.get(link).headers["Location"] == "/reset/unavailable"
    assert resources.store.reset_tokens()[0].consumed_at_utc is None

    clock.value = T
    RecoveryService(resources).request_link(B)
    second = resources.sink.snapshot()[-1].private_payload
    assert client.get(second).headers["Location"] == "/reset/new"
    clock.value += timedelta(minutes=5)
    assert client.get("/reset/new").headers["Location"] == "/reset/unavailable"
    assert resources.store.reset_tokens()[-1].consumed_at_utc is None


def test_tc_013_existing_intent_rechecks_consumed_link():
    """TC-013: a once-valid intent cannot render a form after token consumption."""
    app, resources, _, link = fixture()
    client = app.test_client()
    client.get(link)
    assert client.get("/reset/new").status_code == 200
    token = resources.store.reset_tokens()[0]
    with resources.store._lock:
        resources.store._reset_tokens[token.token_digest] = replace(
            token,
            consumed_at_utc=T,
        )
    assert client.get("/reset/new").headers["Location"] == "/reset/unavailable"
    assert client.get(link).headers["Location"] == "/reset/unavailable"


def test_tc_012_intent_secret_must_not_reuse_link_secret():
    """TC-012: even an injected repeating RNG cannot put the link in a cookie."""
    _, resources, _, link = fixture()
    raw = link.removeprefix("/reset/")
    with pytest.raises(ValueError, match="Reset intent collision"):
        resources.store.create_reset_intent(raw, "b" * 43, T, token_factory=lambda: raw)
    assert resources.store.reset_intents() == ()


def test_tc_017_unauthorized_intent_and_unavailable_post_have_no_effect():
    """TC-017: cookie theft alone, CSRF forgery and direct POST never succeed."""
    app, resources, _, link = fixture()
    owner = app.test_client()
    other = app.test_client()
    assert owner.get(link).headers["Location"] == "/reset/new"
    html = owner.get("/reset/new").get_data(as_text=True)
    csrf = re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)
    intent = owner.get_cookie("reset_intent", path="/reset").value
    other.set_cookie("reset_intent", intent, path="/reset")
    assert other.get("/reset/new").headers["Location"] == "/reset/unavailable"
    before = private_state(resources)
    for client, form in (
        (other, {"new_password": "new secret", "csrf_token": csrf}),
        (owner, {"new_password": "new secret"}),
        (owner, {"new_password": "new secret", "csrf_token": "forged"}),
        (owner, {"new_password": "", "csrf_token": csrf}),
        (owner, {"new_password": "new secret", "csrf_token": csrf}),
    ):
        response = client.post("/reset/complete", data=form)
        assert response.status_code == 303
        assert response.headers["Location"] == "/reset/unavailable"
        assert_private_response(response, link.removeprefix("/reset/"))
        assert private_state(resources) == before
    direct = app.test_client().post(
        "/reset/complete", data={"new_password": "new secret", "csrf_token": csrf}
    )
    assert direct.headers["Location"] == "/reset/unavailable"
    assert private_state(resources) == before


def test_tc_021_form_and_unavailable_are_accessible_without_completion():
    """TC-021: S4 has named, masked controls; S6 has accessible retry paths."""
    app, resources, _, link = fixture()
    client = app.test_client()
    client.get(link)
    page = client.get("/reset/new")
    html = page.get_data(as_text=True)
    csrf = re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)
    assert 'id="new-password" name="new_password" type="password"' in html
    assert '<label for="new-password">New password</label>' in html
    assert ":focus-visible { outline: 3px solid #005fca" in html
    before = private_state(resources)
    rejected = client.post(
        "/reset/complete", data={"new_password": "not-yet", "csrf_token": csrf}
    )
    assert rejected.headers["Location"] == "/reset/unavailable"
    assert 'role="status"' in client.get("/reset/unavailable").get_data(as_text=True)
    assert private_state(resources) == before


def test_tc_012_dev_access_log_omits_request_targets():
    """TC-012: the dev server's request logger prints only response status."""
    handler = object.__new__(PathFreeRequestHandler)
    messages = []
    handler.log = lambda *args: messages.append(args)
    handler.log_request(303)
    assert messages == [("info", "HTTP response %s", 303)]
