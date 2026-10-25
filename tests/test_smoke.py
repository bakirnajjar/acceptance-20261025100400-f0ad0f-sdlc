"""Foundation-only smoke checks; recovery behavior belongs to later tasks."""

from reset_demo import create_app


def test_app_serves_server_rendered_page() -> None:
    app = create_app()

    response = app.test_client().get("/")

    assert response.status_code == 200
    assert b"<h1>Reset demo foundation</h1>" in response.data
    assert b"Recovery is not implemented yet." in response.data
