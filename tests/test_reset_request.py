"""TASK-004 HTTP tests for server-rendered reset request and acknowledgement."""

import re
from datetime import UTC, datetime

from werkzeug.datastructures import MultiDict

from reset_demo import create_app
from reset_demo.recovery import RecoveryService

A = "alex@example.test"
X = "missing@example.test"
T = datetime(2026, 10, 25, 10, 0, tzinfo=UTC)


def csrf_from(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match is not None
    return match.group(1)


def public_snapshot(response) -> tuple[int, tuple[tuple[str, str], ...], bytes]:
    """Keep every response header, including Location and any Set-Cookie."""
    return response.status_code, tuple(response.headers.items()), response.data


def test_tc_006_request_and_confirmation_are_accessible_server_pages() -> None:
    """TC-006: named, focusable controls and generic announced S3 response."""
    app = create_app(clock=lambda: T)
    client = app.test_client()
    entry = client.get("/reset/request")
    html = entry.get_data(as_text=True)
    csrf = csrf_from(html)
    assert entry.status_code == 200
    assert "<!doctype html>" in html
    assert '<h1 id="page-title" tabindex="-1">Reset password</h1>' in html
    assert '<label for="identifier">Email address</label>' in html
    assert 'id="identifier" name="identifier" type="email"' in html
    assert '<button type="submit">Request reset</button>' in html
    assert '<a href="/sign-in">Return to sign in</a>' in html
    assert ":focus-visible { outline: 3px solid #005fca" in html
    assert "no-store" in entry.headers["Cache-Control"]
    assert entry.headers["Referrer-Policy"] == "no-referrer"
    cookie = entry.headers["Set-Cookie"]
    assert "HttpOnly" in cookie and "SameSite=Lax" in cookie
    assert "Secure" not in cookie  # local HTTP, unlike HTTPS below

    submitted = client.post(
        "/reset/request", data={"identifier": A, "csrf_token": csrf}
    )
    assert submitted.status_code == 303
    assert submitted.headers["Location"] == "/reset/confirmation"
    confirmation = client.get(submitted.headers["Location"])
    output = confirmation.get_data(as_text=True)
    assert confirmation.status_code == 200
    assert "<!doctype html>" in output
    assert '<h1 id="page-title" tabindex="-1">Reset request received</h1>' in output
    assert 'role="status">If an account is eligible' in output
    assert '<a href="/sign-in">Return to sign in</a>' in output
    assert ":focus-visible { outline: 3px solid #005fca" in output
    assert confirmation.headers["Referrer-Policy"] == "no-referrer"
    assert "no-store" in confirmation.headers["Cache-Control"]
    assert A not in output
    assert app.extensions["reset_demo"].sink.snapshot()[0].private_payload not in output

    secure_entry = app.test_client().get(
        "/reset/request", environ_overrides={"wsgi.url_scheme": "https"}
    )
    assert "Secure" in secure_entry.headers["Set-Cookie"]


def test_tc_007_known_unknown_capped_full_http_parity_and_private_links() -> None:
    """TC-007: complete HTTP snapshots are equal; sink changes only if eligible."""
    app = create_app(clock=lambda: T)
    resources = app.extensions["reset_demo"]
    client = app.test_client()
    csrf = csrf_from(client.get("/reset/request").get_data(as_text=True))
    cookie_before = client.get_cookie("session")
    assert cookie_before is not None

    known = client.post("/reset/request", data={"identifier": A, "csrf_token": csrf})
    assert len(resources.sink.snapshot()) == 1
    first_link = resources.sink.snapshot()[0].private_payload
    assert first_link.startswith("/reset/")
    assert len(resources.store.accepted_requests(A)) == 1

    unknown = client.post("/reset/request", data={"identifier": X, "csrf_token": csrf})
    assert len(resources.sink.snapshot()) == 1
    assert resources.store.accepted_requests(X) == ()

    service = RecoveryService(resources)
    for _ in range(4):
        service.request_link(A)
    assert len(resources.sink.snapshot()) == 5
    capped = client.post("/reset/request", data={"identifier": A, "csrf_token": csrf})
    assert len(resources.sink.snapshot()) == 5
    assert len(resources.store.accepted_requests(A)) == 5
    assert client.get_cookie("session") == cookie_before

    assert public_snapshot(known) == public_snapshot(unknown) == public_snapshot(capped)
    assert known.status_code == 303
    assert known.headers["Location"] == "/reset/confirmation"
    assert "Set-Cookie" not in known.headers
    confirmations = [
        public_snapshot(client.get(response.headers["Location"]))
        for response in (known, unknown, capped)
    ]
    assert confirmations[0] == confirmations[1] == confirmations[2]
    for _, headers, body in (
        public_snapshot(known),
        confirmations[0],
    ):
        public_output = repr(headers).encode() + body
        assert A.encode() not in public_output
        assert X.encode() not in public_output
        assert first_link.encode() not in public_output
        assert b"throttl" not in public_output.lower()


def test_tc_011_invalid_identifier_and_csrf_are_generic_and_do_not_issue() -> None:
    """TC-011: malformed, duplicate and CSRF-forged forms cannot mutate state."""
    app = create_app(clock=lambda: T)
    resources = app.extensions["reset_demo"]
    client = app.test_client()
    csrf = csrf_from(client.get("/reset/request").get_data(as_text=True))

    malformed_responses = [
        client.post(
            "/reset/request",
            data={"identifier": identifier, "csrf_token": csrf},
        )
        for identifier in ("alex@example.test@", "missing@example.test@", "", "bad")
    ]
    assert all(response.status_code == 400 for response in malformed_responses)
    assert public_snapshot(malformed_responses[0]) == public_snapshot(
        malformed_responses[1]
    )
    for response in malformed_responses:
        html = response.get_data(as_text=True)
        assert 'id="request-error" role="alert" tabindex="-1"' in html
        assert 'aria-describedby="request-error" aria-invalid="true"' in html
        assert 'href="#identifier">Review email address</a>' in html
        assert A not in html and X not in html
        assert "account found" not in html.lower()
        assert "no-store" in response.headers["Cache-Control"]

    duplicate = client.post(
        "/reset/request",
        data=MultiDict([("csrf_token", csrf), ("identifier", A), ("identifier", X)]),
    )
    assert duplicate.status_code == 400
    for forged in (
        {"identifier": A},
        {"identifier": X, "csrf_token": "forged"},
    ):
        response = client.post("/reset/request", data=forged)
        assert response.status_code == 400
        html = response.get_data(as_text=True)
        assert 'role="alert"' in html
        assert 'aria-describedby="request-error"' in html
        assert A not in html and X not in html

    anonymous = app.test_client().post(
        "/reset/request", data={"identifier": A, "csrf_token": csrf}
    )
    assert anonymous.status_code == 400
    assert 'role="alert"' in anonymous.get_data(as_text=True)
    assert resources.store.accepted_requests(A) == ()
    assert resources.store.reset_tokens() == ()
    assert resources.sink.snapshot() == ()
