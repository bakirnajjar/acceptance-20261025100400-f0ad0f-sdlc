"""TASK-008 integrated public-flow checks and the TC-023 pytest coverage audit."""

import ast
import http.client
import logging
import re
import smtplib
import socket
import sys
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from threading import Thread

from werkzeug.serving import make_server

from reset_demo import PathFreeRequestHandler, create_app
from reset_demo.foundation import secure_token

A = "alex@example.test"
B = "blair@example.test"
X = "missing@example.test"
T = datetime(2026, 10, 25, 10, 0, tzinfo=UTC)


def csrf(response) -> str:
    match = re.search(
        r'name="csrf_token" value="([^"]+)"', response.get_data(as_text=True)
    )
    assert match is not None
    return match.group(1)


def public(response) -> tuple[int, tuple[tuple[str, str], ...], bytes]:
    return response.status_code, tuple(response.headers.items()), response.data


def assert_secret_free(response, *secrets: str) -> None:
    output = repr(public(response)).encode()
    for secret in secrets:
        assert secret.encode() not in output
    assert response.headers["Cache-Control"] == "no-store"
    assert response.headers["Referrer-Policy"] == "no-referrer"


def test_tc_023_collected_behavioral_cases_have_executable_assertions(request) -> None:
    """TC-023: audit collected TC-001..023 tests, not just design descriptions."""
    assert sys.version_info[:2] == (3, 12)
    collected = {
        int(match.group(1))
        for item in request.session.items
        if (match := re.search(r"test_tc_(\d{3})_", item.name))
    }
    assert 23 in collected
    for item in request.session.items:
        if re.search(r"test_tc_(\d{3})_", item.name):
            assert not any(
                item.get_closest_marker(marker)
                for marker in ("skip", "skipif", "xfail")
            )

    asserted_cases = set()
    for test_file in Path(__file__).parent.glob("test_*.py"):
        tree = ast.parse(test_file.read_text(encoding="utf-8"))
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            match = re.fullmatch(r"test_tc_(\d{3})_.*", node.name)
            if match and any(isinstance(child, ast.Assert) for child in ast.walk(node)):
                asserted_cases.add(int(match.group(1)))
    assert asserted_cases == set(range(1, 24))
    assert collected <= asserted_cases
    # Actual success of the suite and the other gates is checked by the
    # external quality commands, not inferred from this structural audit.


def test_tc_023_http_journey_parity_authorization_owner_effects_and_no_transport(
    monkeypatch, caplog
) -> None:
    """TC-023: exercise S1-S6 through HTTP with network delivery forbidden."""
    attempts = []

    def forbid(*args, **kwargs):
        attempts.append((args, kwargs))
        raise AssertionError("Unexpected outbound notification transport")

    monkeypatch.setattr(socket.socket, "connect", forbid)
    monkeypatch.setattr(smtplib, "SMTP", forbid)
    monkeypatch.setattr(urllib.request, "urlopen", forbid)

    app = create_app(clock=lambda: T)
    resources = app.extensions["reset_demo"]
    client = app.test_client()
    sign_in = client.get("/sign-in")
    assert sign_in.status_code == 200
    assert b'href="/reset/request">Forgot password?</a>' in sign_in.data
    entry = client.get("/reset/request")
    form_csrf = csrf(entry)
    assert b'<label for="identifier">Email address</label>' in entry.data

    def request_link(identifier):
        return client.post(
            "/reset/request",
            data={"identifier": identifier, "csrf_token": form_csrf},
        )

    with caplog.at_level(logging.INFO):
        known = request_link(A)
        for _ in range(4):
            assert public(request_link(A)) == public(known)
        unknown = request_link(X)
        capped = request_link(A)
        assert public(known) == public(unknown) == public(capped)
        assert known.status_code == 303
        assert known.headers["Location"] == "/reset/confirmation"
        confirmations = [
            public(client.get(response.headers["Location"]))
            for response in (known, unknown, capped)
        ]
        assert confirmations[0] == confirmations[1] == confirmations[2]
        assert b"eligible" in confirmations[0][2]
        notices = resources.sink.snapshot()
        assert len(notices) == len(resources.store.accepted_requests(A)) == 5
        assert resources.store.accepted_requests(X) == ()
        assert {notice.owner for notice in notices} == {A}
        link = notices[0].private_payload
        raw = link.removeprefix("/reset/")
        for response in (known, unknown, capped):
            assert_secret_free(response, A, X, raw)
        assert all(
            raw.encode() not in repr(confirmation).encode()
            for confirmation in confirmations
        )

        a1, a2 = resources.store.create_session(A), resources.store.create_session(A)
        b1 = resources.store.create_session(B)
        old_hash = resources.store.get_account(A).password_hash
        redirect = client.get(link)
        assert redirect.status_code == 303
        assert redirect.headers["Location"] == "/reset/new"
        assert_secret_free(redirect, raw, A)
        form = client.get(redirect.headers["Location"])
        assert form.status_code == 200
        assert b'<label for="new-password">New password</label>' in form.data
        assert b'name="new_password" type="password"' in form.data
        assert_secret_free(form, raw, A)
        assert resources.store.reset_tokens()[0].consumed_at_utc is None
        valid_csrf = csrf(form)
        before = (
            resources.store.accounts(),
            resources.store.reset_tokens(),
            resources.store.sessions(),
            resources.sink.snapshot(),
        )
        forbidden = client.post(
            "/reset/complete",
            data={"csrf_token": "forged", "new_password": "synthetic-new-pass"},
        )
        assert forbidden.status_code == 400
        assert b'role="alert"' in forbidden.data
        assert_secret_free(forbidden, raw, A, "synthetic-new-pass")
        direct = app.test_client().post(
            "/reset/complete",
            data={"csrf_token": valid_csrf, "new_password": "synthetic-new-pass"},
        )
        assert direct.status_code == 303
        assert direct.headers["Location"] == "/reset/unavailable"
        assert_secret_free(direct, raw, A, "synthetic-new-pass")
        assert (
            resources.store.accounts(),
            resources.store.reset_tokens(),
            resources.store.sessions(),
            resources.sink.snapshot(),
        ) == before

        # The forged CSRF rotates the browser token; read the new S4 form.
        success = client.post(
            "/reset/complete",
            data={
                "csrf_token": csrf(client.get("/reset/new")),
                "new_password": "synthetic-new-pass",
            },
        )
        assert success.status_code == 200
        assert b"Password reset complete" in success.data
        assert_secret_free(success, raw, A, "synthetic-new-pass")
        new_hash = resources.store.get_account(A).password_hash
        assert new_hash != old_hash
        assert resources.hasher.verify(new_hash, "synthetic-new-pass")
        assert not resources.hasher.verify(old_hash, "synthetic-new-pass")
        assert resources.store.reset_tokens()[0].consumed_at_utc == T
        assert not resources.store.check_session(A, a1)
        assert not resources.store.check_session(A, a2)
        assert resources.store.check_session(B, b1)
        assert [
            (notice.kind, notice.owner) for notice in resources.sink.snapshot()
        ] == [
            *[("reset_link", A)] * 5,
            ("password_reset", A),
        ]
        replay = client.get(link)
        assert replay.headers["Location"] == "/reset/unavailable"
        unavailable = client.get(replay.headers["Location"])
        assert b"Reset unavailable" in unavailable.data
        assert b'href="/reset/request"' in unavailable.data
        assert b'href="/sign-in"' in unavailable.data
        assert b'name="new_password"' not in unavailable.data
        for response in (replay, unavailable):
            assert_secret_free(response, raw, A)

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
        for path in ("/sink", "/notifications", "/reset/tokens", "/test/sink"):
            probe = client.get(path)
            if path.startswith("/reset/"):
                assert probe.status_code == 303
                assert probe.headers["Location"] == "/reset/unavailable"
            else:
                assert probe.status_code == 404
            assert raw.encode() not in repr(public(probe)).encode()
    assert raw not in caplog.text
    assert A not in caplog.text
    assert "synthetic-new-pass" not in caplog.text
    assert attempts == []


def test_tc_012_loopback_http_omits_initial_bearer_from_response_and_access_log(
    caplog,
) -> None:
    """TC-012: real loopback HTTP, not only Flask test_client, keeps logs path-free."""
    app = create_app(clock=lambda: T)
    resources = app.extensions["reset_demo"]
    client = app.test_client()
    form_csrf = csrf(client.get("/reset/request"))
    client.post("/reset/request", data={"identifier": A, "csrf_token": form_csrf})
    link = resources.sink.snapshot()[0].private_payload
    raw = link.removeprefix("/reset/")

    server = make_server("127.0.0.1", 0, app, request_handler=PathFreeRequestHandler)
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        with caplog.at_level(logging.INFO, logger="werkzeug"):
            connection = http.client.HTTPConnection(
                "127.0.0.1", server.server_port, timeout=5
            )
            try:
                connection.request("GET", link)
                response = connection.getresponse()
                body = response.read()
                headers = response.getheaders()
                assert response.status == 303
                assert dict(headers)["Location"] == "/reset/new"
                assert raw.encode() not in body + repr(headers).encode()
                cookie = "; ".join(
                    value.split(";", 1)[0]
                    for key, value in headers
                    if key.lower() == "set-cookie"
                )
                assert raw not in cookie
                connection.request("GET", "/reset/new", headers={"Cookie": cookie})
                page = connection.getresponse()
                html = page.read()
                assert page.status == 200
                assert b'<label for="new-password">New password</label>' in html
                assert raw.encode() not in html + repr(page.getheaders()).encode()
            finally:
                connection.close()
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=5)
    assert not worker.is_alive()
    assert "HTTP response 303" in caplog.text
    assert raw not in caplog.text
    assert link not in caplog.text


def test_tc_010_http_issuance_failure_is_private_and_does_not_use_fifth_slot(
    caplog,
) -> None:
    """TC-010: an HTTP issuance error is generic and leaves a retryable slot."""
    fail = False
    private_marker = "private-issuance-error-alex"

    def token_factory():
        if fail:
            raise RuntimeError(private_marker)
        return secure_token()

    app = create_app(clock=lambda: T, token_factory=token_factory)
    resources = app.extensions["reset_demo"]
    client = app.test_client()
    form_csrf = csrf(client.get("/reset/request"))

    def submit():
        return client.post(
            "/reset/request",
            data={"identifier": A, "csrf_token": form_csrf},
        )

    for _ in range(4):
        assert submit().headers["Location"] == "/reset/confirmation"
    before = (
        resources.store.accepted_requests(A),
        resources.store.reset_tokens(),
        resources.sink.snapshot(),
    )
    fail = True
    with caplog.at_level(logging.INFO):
        rejected = submit()
    assert rejected.status_code == 503
    assert b'role="alert"' in rejected.data
    assert_secret_free(rejected, A, private_marker)
    assert private_marker not in caplog.text
    assert A not in caplog.text
    assert (
        resources.store.accepted_requests(A),
        resources.store.reset_tokens(),
        resources.sink.snapshot(),
    ) == before
    fail = False
    assert submit().headers["Location"] == "/reset/confirmation"
    assert (
        len(resources.store.accepted_requests(A)) == len(resources.sink.snapshot()) == 5
    )


def test_tc_017_cross_account_intent_cookie_cannot_authorize_other_browser() -> None:
    """TC-017: A's CSRF and browser binding cannot use B's stolen intent."""
    app = create_app(clock=lambda: T)
    resources = app.extensions["reset_demo"]
    a = app.test_client()
    b = app.test_client()
    a_csrf = csrf(a.get("/reset/request"))
    b_csrf = csrf(b.get("/reset/request"))
    requested_a = a.post("/reset/request", data={"identifier": A, "csrf_token": a_csrf})
    requested_b = b.post("/reset/request", data={"identifier": B, "csrf_token": b_csrf})
    assert requested_a.status_code == requested_b.status_code == 303
    a_link, b_link = (n.private_payload for n in resources.sink.snapshot())
    assert a.get(a_link).headers["Location"] == "/reset/new"
    assert b.get(b_link).headers["Location"] == "/reset/new"
    a_intent = a.get_cookie("reset_intent", path="/reset").value
    b_intent = b.get_cookie("reset_intent", path="/reset").value
    assert a_intent != b_intent
    before = (
        resources.store.accounts(),
        resources.store.reset_tokens(),
        resources.store.sessions(),
        resources.sink.snapshot(),
    )
    a.set_cookie("reset_intent", b_intent, path="/reset")
    denied_get = a.get("/reset/new")
    denied_post = a.post(
        "/reset/complete",
        data={"csrf_token": a_csrf, "new_password": "not-authorized"},
    )
    for response in (denied_get, denied_post):
        assert response.status_code == 303
        assert response.headers["Location"] == "/reset/unavailable"
        assert_secret_free(
            response,
            A,
            B,
            a_link.removeprefix("/reset/"),
            b_link.removeprefix("/reset/"),
            "not-authorized",
        )
    assert (
        resources.store.accounts(),
        resources.store.reset_tokens(),
        resources.store.sessions(),
        resources.sink.snapshot(),
    ) == before
    a.set_cookie("reset_intent", a_intent, path="/reset")
    assert a.get("/reset/new").status_code == 200
    assert b.get("/reset/new").status_code == 200
