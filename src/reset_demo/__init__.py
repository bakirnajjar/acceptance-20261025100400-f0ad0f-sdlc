"""Local Flask application foundation."""

from flask import Flask, render_template, request

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
        # Accept no requests or identifiers until the recovery service is implemented.
        if request.method == "POST":
            return render_template("reset_request.html", unavailable=True), 501
        return render_template("reset_request.html", unavailable=False)

    return app


def main() -> None:
    """Run the local development server."""
    create_app().run(host="127.0.0.1", port=5000)
