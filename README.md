# Reset demo foundation

Python 3.12 Flask/Jinja foundation for a local synthetic demo. The factory
creates a fresh, process-local locked account store and a separate private
in-memory notification sink for each app. The sign-in screen and recovery
request entry screen are server-rendered, but authentication, reset submission,
session handling and notification issuance are not implemented. No live
accounts or credentials are needed; do not enter real credentials.

## Setup

Install [uv](https://docs.astral.sh/uv/) and Python 3.12. From the repository
root, install the locked project and development dependencies:

```sh
uv sync --locked --python python3.12
```

The commands below use `python3.12` directly rather than uv's virtual
environment. To use those exact commands, install the locked dependencies and
editable project into that interpreter's user site (prefer a disposable
environment). This avoids modifying externally managed system packages:

```sh
uv export --locked --all-groups --no-hashes | uv pip install --python python3.12 --target "$(python3.12 -m site --user-site)" -r /dev/stdin
```

## Quality gates

Run these from the repository root:

```sh
python3.12 -m compileall -q src/reset_demo
python3.12 -m pytest
python3.12 -m ruff check .
python3.12 -m ruff format --check .
```

## Local run

```sh
uv run --locked reset-demo
```

Open http://127.0.0.1:5000/sign-in to view the sign-in card, then follow
"Forgot password?" to the reset request entry page. Sign-in submissions return
an explicit unavailable message without authenticating or storing credentials;
the request entry likewise responds unavailable without accepting/issuing a
reset until the recovery flow is implemented.
The original foundation placeholder remains at `/`. This development server
is for local use only. No environment variables are required
at this stage. Accounts `alex@example.test` and `blair@example.test` are
synthetic; each app creates unpredictable initial passwords transiently and
stores only salted Werkzeug scrypt hashes (N=32768, r=8, p=1). The initial
passwords are not available for sign-in. The injectable aware UTC clock,
password hasher, CSPRNG token factory (`secrets.token_urlsafe(32)`), store and
sink are internal factory arguments for deterministic tests. No public route
exposes the sink or account state. Sink records are local memory, not owner
delivery; process restarts discard both accounts and notifications, and multiple
workers do not share state. This foundation is not production-ready and uses
no database, external service or deployment configuration.
