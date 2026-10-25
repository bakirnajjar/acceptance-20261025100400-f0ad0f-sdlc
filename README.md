# Reset demo foundation

Python 3.12 Flask/Jinja skeleton for a local synthetic demo. This checkpoint
only renders a placeholder page; it does not implement sign-in, password reset,
account storage or notification delivery. No live accounts or credentials are
needed.

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

Open http://127.0.0.1:5000/ to view the Jinja-rendered placeholder. This
development server is for local use only. No environment variables are required
at this stage.
