"""Local Flask application foundation."""

import re
from secrets import compare_digest

from flask import (
    Flask,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask.sessions import SecureCookieSessionInterface
from werkzeug.serving import WSGIRequestHandler

from reset_demo.foundation import (
    AppResources,
    Clock,
    InMemoryStore,
    NotificationSink,
    PasswordHasher,
    ScryptPasswordHasher,
    TokenFactory,
    secure_token,
    seed_synthetic_accounts,
    utc_now,
)
from reset_demo.recovery import IssuanceError, RecoveryService


class LocalSessionInterface(SecureCookieSessionInterface):
    """Protect the CSRF cookie on HTTPS while allowing the local HTTP demo."""

    def get_cookie_secure(self, app: Flask) -> bool:
        return request.is_secure or super().get_cookie_secure(app)


class PathFreeRequestHandler(WSGIRequestHandler):
    """Do not log request targets: the initial reset URL contains a bearer secret."""

    def log_request(self, code: int | str = "-", size: int | str = "-") -> None:
        self.log("info", "HTTP response %s", code)


def _valid_identifier(identifier: str) -> bool:
    """Accept an email-shaped identifier, without checking account existence."""
    return (
        len(identifier) <= 254
        and re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", identifier) is not None
    )


def create_app(
    *,
    clock: Clock = utc_now,
    hasher: PasswordHasher | None = None,
    token_factory: TokenFactory = secure_token,
    store: InMemoryStore | None = None,
    sink: NotificationSink | None = None,
) -> Flask:
    """Create independent app-local state and safe injection seams for tests."""
    app = Flask(__name__)
    app.secret_key = secure_token()
    app.session_interface = LocalSessionInterface()
    app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")
    resources = AppResources(
        store=store if store is not None else InMemoryStore(),
        sink=sink if sink is not None else NotificationSink(),
        clock=clock,
        hasher=hasher if hasher is not None else ScryptPasswordHasher(),
        token_factory=token_factory,
    )
    resources.now()
    seed_synthetic_accounts(resources)
    app.extensions["reset_demo"] = resources
    recovery = RecoveryService(resources)

    @app.after_request
    def protect_reset_pages(response):
        if request.path.startswith("/reset/"):
            response.headers["Cache-Control"] = "no-store"
            response.headers["Referrer-Policy"] = "no-referrer"
        return response

    @app.get("/")
    def index() -> str:
        return render_template("index.html")

    @app.route("/sign-in", methods=["GET", "POST"])
    def sign_in() -> str | tuple[str, int]:
        # No authentication contract exists. Never inspect or echo submitted credentials.
        if request.method == "POST":
            return render_template("sign_in.html", unavailable=True), 501
        return render_template("sign_in.html", unavailable=False)

    @app.route("/reset/request", methods=["GET", "POST"])
    def reset_request() -> str | tuple[str, int]:
        csrf_token = session.get("reset_csrf")
        if request.method == "GET":
            if not isinstance(csrf_token, str):
                csrf_token = secure_token()
                session["reset_csrf"] = csrf_token
            return render_template("reset_request.html", csrf_token=csrf_token)

        submitted = request.form.getlist("csrf_token")
        csrf_valid = (
            isinstance(csrf_token, str)
            and len(submitted) == 1
            and compare_digest(csrf_token, submitted[0])
        )
        identifiers = request.form.getlist("identifier")
        identifier = identifiers[0].strip() if len(identifiers) == 1 else ""
        invalid = not _valid_identifier(identifier)
        if not csrf_valid or invalid:
            if not csrf_valid:
                csrf_token = secure_token()
                session["reset_csrf"] = csrf_token
            return (
                render_template(
                    "reset_request.html",
                    csrf_token=csrf_token,
                    error="Request could not be processed. Please check the form and try again.",
                    identifier_invalid=invalid,
                ),
                400,
            )

        try:
            recovery.request_link(identifier)
        except IssuanceError:
            return (
                render_template(
                    "reset_request.html",
                    csrf_token=csrf_token,
                    error="Request could not be processed. Please try again.",
                ),
                503,
            )
        return redirect(url_for("reset_confirmation"), code=303)

    @app.get("/reset/confirmation")
    def reset_confirmation() -> str:
        return render_template("reset_confirmation.html")

    @app.get("/reset/new")
    def reset_new():
        if not resources.store.check_reset_intent(
            request.cookies.get("reset_intent"),
            session.get("reset_browser"),
            resources.now(),
        ):
            return redirect(url_for("reset_unavailable"), code=303)
        csrf_token = session.get("reset_csrf")
        if not isinstance(csrf_token, str):
            csrf_token = secure_token()
            session["reset_csrf"] = csrf_token
        return render_template("reset_new.html", csrf_token=csrf_token)

    @app.post("/reset/complete")
    def reset_complete():
        intent = request.cookies.get("reset_intent")
        binding = session.get("reset_browser")
        if not resources.store.check_reset_intent(intent, binding, resources.now()):
            return redirect(url_for("reset_unavailable"), code=303)

        csrf_token = session.get("reset_csrf")
        submitted = request.form.getlist("csrf_token")
        csrf_valid = (
            isinstance(csrf_token, str)
            and len(submitted) == 1
            and compare_digest(csrf_token, submitted[0])
        )
        passwords = request.form.getlist("new_password")
        if not csrf_valid or len(passwords) != 1 or not passwords[0].strip():
            if not csrf_valid:
                csrf_token = secure_token()
                session["reset_csrf"] = csrf_token
            return (
                render_template(
                    "reset_new.html",
                    csrf_token=csrf_token,
                    error="Reset could not be completed. Check the form and try again.",
                ),
                400,
            )

        try:
            completed = resources.store.complete_reset_intent(
                intent,
                binding,
                passwords[0],
                resources.now,
                resources.hasher,
                resources.sink,
            )
        except (RuntimeError, ValueError, TypeError, OSError):
            return (
                render_template(
                    "reset_new.html",
                    csrf_token=csrf_token,
                    error="Reset could not be completed. Please try again.",
                ),
                503,
            )
        if not completed:
            return redirect(url_for("reset_unavailable"), code=303)
        response = make_response(render_template("reset_success.html"))
        response.delete_cookie("reset_intent", path="/reset")
        return response

    @app.get("/reset/unavailable")
    def reset_unavailable() -> str:
        return render_template("reset_unavailable.html")

    @app.get("/reset/<opaque_token>")
    def reset_link(opaque_token: str):
        binding = session.get("reset_browser")
        if (
            not isinstance(binding, str)
            or re.fullmatch(r"[A-Za-z0-9_-]{32,256}", binding) is None
        ):
            binding = secure_token()
        try:
            intent = resources.store.create_reset_intent(
                opaque_token, binding, resources.now()
            )
        except (RuntimeError, ValueError, TypeError):
            intent = None
        if intent is None:
            response = make_response(redirect(url_for("reset_unavailable"), code=303))
            response.delete_cookie("reset_intent", path="/reset")
            return response
        session["reset_browser"] = binding
        response = make_response(redirect(url_for("reset_new"), code=303))
        response.set_cookie(
            "reset_intent",
            intent,
            max_age=300,
            path="/reset",
            httponly=True,
            secure=request.is_secure,
            samesite="Lax",
        )
        return response

    return app


def main() -> None:
    """Run the local development server."""
    create_app().run(
        host="127.0.0.1", port=5000, request_handler=PathFreeRequestHandler
    )
