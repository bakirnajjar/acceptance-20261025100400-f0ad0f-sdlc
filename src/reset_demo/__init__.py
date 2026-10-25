"""Local Flask application foundation."""

from flask import Flask, render_template


def create_app() -> Flask:
    """Create a fresh, server-rendered demo app."""
    app = Flask(__name__)

    @app.get("/")
    def index() -> str:
        return render_template("index.html")

    return app


def main() -> None:
    """Run the local development server."""
    create_app().run(host="127.0.0.1", port=5000)
