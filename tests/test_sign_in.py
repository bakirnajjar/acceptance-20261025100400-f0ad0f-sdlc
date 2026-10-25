"""TASK-002 S1 markup and S2 entry checks; browser visuals remain manual."""

from html.parser import HTMLParser

from reset_demo import create_app


class Page(HTMLParser):
    def __init__(self, html: str) -> None:
        super().__init__()
        self.elements: list[tuple[str, dict[str, str | None]]] = []
        self.labels: dict[str, str] = {}
        self.links: list[tuple[str, str]] = []
        self._label_for: str | None = None
        self._link_href: str | None = None
        self._text: list[str] = []
        self.feed(html)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        self.elements.append((tag, attributes))
        if tag == "label":
            self._label_for = attributes.get("for")
            self._text = []
        elif tag == "a":
            self._link_href = attributes.get("href")
            self._text = []

    def handle_data(self, data: str) -> None:
        if self._label_for is not None or self._link_href is not None:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "label" and self._label_for is not None:
            self.labels[self._label_for] = "".join(self._text).strip()
            self._label_for = None
        elif tag == "a" and self._link_href is not None:
            self.links.append((self._link_href, "".join(self._text).strip()))
            self._link_href = None


def test_tc_003_sign_in_server_markup() -> None:
    """TC-003: server response contains the observed S1 content and structure."""
    response = create_app().test_client().get("/sign-in")
    html = response.get_data(as_text=True)
    page = Page(html)
    inputs = {attrs["id"]: attrs for tag, attrs in page.elements if tag == "input"}
    buttons = [attrs for tag, attrs in page.elements if tag == "button"]

    assert response.status_code == 200
    assert "<!doctype html>" in html
    assert '<main class="card" aria-labelledby="page-title">' in html
    assert '<h1 id="page-title" tabindex="-1">Sign in</h1>' in html
    assert page.labels == {"email": "Email address", "password": "Password"}
    assert inputs["email"]["placeholder"] == "name@example.com"
    assert inputs["password"]["placeholder"] == "********"
    assert buttons == [{"type": "submit"}]
    assert '<button type="submit">Sign in</button>' in html
    assert '<p class="footer">No account? Contact your administrator.</p>' in html
    # Assert the intended CSS is served with the HTML, not a browser screenshot match.
    assert "place-items: center" in html
    assert "width: min(340px, calc(100% - 32px))" in html
    assert "border: 1px solid #333" in html
    assert "background: #191919" in html


def test_tc_004_sign_in_control_semantics_and_unavailable_submission() -> None:
    """TC-004: required labeled controls and predictable non-authentication."""
    app = create_app()
    client = app.test_client()
    html = client.get("/sign-in").get_data(as_text=True)
    elements = Page(html).elements
    email_index = next(
        i
        for i, (tag, attrs) in enumerate(elements)
        if tag == "input" and attrs.get("id") == "email"
    )
    password_index = next(
        i
        for i, (tag, attrs) in enumerate(elements)
        if tag == "input" and attrs.get("id") == "password"
    )
    link_index = next(
        i
        for i, (tag, attrs) in enumerate(elements)
        if tag == "a" and attrs.get("href") == "/reset/request"
    )
    button_index = next(i for i, (tag, attrs) in enumerate(elements) if tag == "button")
    assert email_index < password_index < link_index < button_index
    assert elements[email_index][1]["type"] == "email"
    assert elements[password_index][1]["type"] == "password"
    assert all(
        "required" in elements[index][1] for index in (email_index, password_index)
    )
    assert ":focus-visible { outline: 3px solid #005fca" in html
    resources = app.extensions["reset_demo"]
    accounts_before = resources.store.accounts()

    response = client.post(
        "/sign-in",
        data={"email": "alex@example.test", "password": "visible-test-secret"},
    )
    assert response.status_code == 501
    assert b'role="alert">Sign-in is not available in this demo.' in response.data
    assert b"visible-test-secret" not in response.data
    assert b"alex@example.test" not in response.data
    assert resources.store.accounts() == accounts_before
    assert resources.sink.snapshot() == ()


def test_tc_005_forgot_password_enters_server_rendered_request_page() -> None:
    """TC-005 entry only: S2 is reachable but no reset request can be accepted."""
    app = create_app()
    client = app.test_client()
    sign_in = Page(client.get("/sign-in").get_data(as_text=True))
    assert ("/reset/request", "Forgot password?") in sign_in.links
    response = client.get("/reset/request")
    html = response.get_data(as_text=True)
    entry = Page(html)
    assert response.status_code == 200
    assert "<!doctype html>" in html
    assert '<h1 id="page-title" tabindex="-1">Reset password</h1>' in html
    assert entry.labels == {"identifier": "Email address"}
    assert (
        "input",
        {
            "id": "identifier",
            "name": "identifier",
            "type": "email",
            "autocomplete": "email",
            "required": None,
            "aria-describedby": "request-unavailable",
        },
    ) in entry.elements
    assert ("form", {"action": "/reset/request", "method": "post"}) in entry.elements
    assert (
        "button",
        {"type": "submit", "aria-describedby": "request-unavailable"},
    ) in entry.elements
    assert ("a", {"href": "/sign-in"}) in entry.elements
    assert "Reset requests are not available yet." in html
    submission = client.post("/reset/request", data={"identifier": "alex@example.test"})
    assert submission.status_code == 501
    assert b'role="alert">Reset requests are not available yet.' in submission.data
    assert b"alex@example.test" not in submission.data
    assert app.extensions["reset_demo"].sink.snapshot() == ()
