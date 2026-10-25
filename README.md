# Reset demo foundation

Python 3.12 Flask/Jinja foundation for a local synthetic demo. The factory
creates a fresh, process-local locked account store and a separate private
in-memory notification sink for each app. Sign-in, recovery request,
acknowledgement and reset-entry screens are server-rendered. Private reset-link
issuance, browser reset completion and a revocable session registry are implemented,
but authentication is not. No live accounts or credentials are needed; do
not enter real credentials.

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
an explicit unavailable message without authenticating or storing credentials.
The request form uses a CSRF token and returns the same generic confirmation
for eligible, unknown and capped valid identifiers. A known eligible request
records a private link in the in-memory sink, not an email or public response.
A private sink link can open the reset form; CSRF-valid nonempty submission
before expiry changes the password and shows a success page. The original foundation
placeholder remains at `/`. This development server is for local use only.
No environment variables are required at this stage. Accounts
`alex@example.test` and `blair@example.test` are
synthetic; each app creates unpredictable initial passwords transiently and
stores only salted Werkzeug scrypt hashes (N=32768, r=8, p=1). The initial
passwords are not available for sign-in. The injectable aware UTC clock,
password hasher, CSPRNG token factory (`secrets.token_urlsafe(32)`), store and
sink are internal factory arguments for deterministic tests. No public route
exposes the sink or account state. Sink records are local memory, not owner
delivery; process restarts discard accounts, sessions and notifications, and
multiple workers do not share state. This foundation is not production-ready
and uses no database, external service or deployment configuration.

The private `RecoveryService` accepts an identifier without returning an account
or throttle result. For known accounts, its process-local locked store issues up
to five links in the trailing hour, keeping only token digests and UTC issuance
times in the store; the raw link is captured solely by the private in-memory
sink. Unknown or capped requests issue no link. This is not an owner-accessible
delivery channel. Reset pages use no-store and no-referrer headers; the
app-local CSRF session cookie is HttpOnly, SameSite=Lax and Secure under HTTPS.
This local demo has no constant-time HTTP guarantee and no unknown-identifier
abuse control.

The private store can create opaque, CSPRNG-backed sessions for known account
IDs, check activity and account ownership, and revoke all represented sessions
for one account under the same per-app lock. It stores only SHA-256 digests of
session secrets, not the bearer secrets; revoked records remain inactive and
cannot be reused. Tests create two sessions for Alex and one for Blair through
the store, with no fixture HTTP endpoint or sign-in authentication. Reset
completion revokes all represented owner sessions; every future authenticated
request must check the store before trusting a
session. No authenticated session cookies or public session routes are
implemented (the request form uses a separate CSRF session cookie).

An unused link is eligible on GET strictly before its issuance time plus 30
minutes. The GET does not consume it. It redirects to secret-free `/reset/new`
using a five-minute opaque intent stored by digest in the app-local store,
bound to a browser's signed session and transmitted in an HttpOnly, SameSite=Lax
cookie (Secure over HTTPS). Each S4 GET rechecks both the intent and original
link deadline. S4 has a labeled password form and CSRF field; `/reset/complete`
rechecks the same browser's intent, unused token and strict issuance-based
deadline under one store lock. A successful POST commits the new salted scrypt
hash, token consumption, all owner-session revocations and one owner-addressed
private sink notice together before rendering S5, with sign-in navigation;
sink or hashing failure leaves all state unchanged and presents a generic retry
error. Expired, used or unknown links show generic `/reset/unavailable` with
retry and sign-in navigation. Reset pages and redirects are non-cacheable with
no-referrer policy. The local development server omits request targets from
its access log; the initial bearer URL still appears in browser history and
may be visible to clients, proxies or other infrastructure logging it. Local
HTTP and process-local intent storage are not production transport or
persistence guarantees.
