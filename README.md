# Local synthetic password-reset demo — not production ready

Python 3.12 Flask/Jinja application for a local synthetic demo. The factory
creates a fresh, process-local locked account store and a separate private
in-memory notification sink for each app. Sign-in, recovery request,
acknowledgement and reset-entry screens are server-rendered. Private reset-link
issuance, browser reset completion and a revocable session registry are implemented,
but sign-in authentication is not. **Do not use this as a production service or
enter real accounts, passwords or credentials.** No external link or notice
delivery is implemented.

## Setup

Install [uv](https://docs.astral.sh/uv/) and Python 3.12. From the repository
root, install the locked project and development dependencies:

```sh
uv sync --locked --python python3.12
```

For the exact `python3.12` gates below, rather than uv's virtual environment,
install the locked dependencies and editable project into that interpreter's
user site (prefer a disposable environment). This avoids modifying externally
managed system packages:

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

Alternatively, after `uv sync`, run each gate using uv's isolated environment
by prefixing the corresponding command with `uv run --locked` and replacing
`python3.12` with `python`. Compilation is the build gate; pytest is the test
gate; both Ruff commands are lint/format gates.

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
before expiry changes the password and shows a success page. The browser UI
cannot retrieve a link from the sink: there is deliberately no sink-inspection
route or owner delivery channel. To exercise the complete S1–S6 journey in a
single app instance, run the in-process synthetic HTTP test (it inspects the
private sink without exposing it over HTTP):

```sh
uv run --locked python -m pytest tests/test_behavioral_gate.py -k test_tc_023_http_journey_parity_authorization_owner_effects_and_no_transport
```

The original foundation placeholder remains at `/`. This loopback development
server is for local use only. No environment variables are required for the
demo. Accounts
`alex@example.test` and `blair@example.test` are
synthetic; each app creates unpredictable initial passwords transiently and
stores only salted Werkzeug scrypt hashes (N=32768, r=8, p=1). The initial
passwords are not available for sign-in. The injectable aware UTC clock,
password hasher, CSPRNG token factory (`secrets.token_urlsafe(32)`), store and
sink are internal factory arguments for deterministic tests. No public route
exposes the sink or account state.

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

## Production limitations and prerequisites (TC-024 / REQ-019)

**Not production ready.** One lock protects each app's in-memory store, but
only within that app/process. Restarting discards and reseeds accounts and
loses password changes, issued links, reset intents, accepted-request counts,
session revocations and sink notices. Another process or worker has a separate
store and sink: there are **no shared/durable rate limits, sessions, token or
intent state, or notification records**. The private, owner-addressed sink is
observable to in-process tests only; recording a link or reset notice there is
**not delivery to the owner**. There is no database, external service, hosting
setup or deployment configuration in this demo.

The first reset URL contains a bearer secret. Redirecting to a secret-free
form, no-store/no-referrer responses and path-free logging on the included
development server reduce exposure but cannot erase browser history or prevent
clients, proxies and other infrastructure from logging the initial URL.
Loopback **HTTP does not provide transport security**. The CSRF and reset-intent
cookies are HttpOnly and SameSite=Lax and become Secure under HTTPS, but local
HTTP cookies and traffic can be exposed; application signing keys are generated
anew per app instance rather than managed as durable production secrets.
Generic public responses do not guarantee indistinguishable processing time,
and unknown identifiers have no abuse quota. The new-password rule is merely
nonempty; sign-in has no authenticated login, session issuance or login policy.
The private session registry is not wired to authenticated HTTP requests.

Before considering a separately scoped production design, provide durable
transactional storage and migrations with backup/recovery; shared cross-worker
rate accounting, token/intent state and session validation/revocation; reliable
owner-controlled link/notice delivery with retry or transactional outbox;
HTTPS end-to-end, secure cookie/session and signing-secret management (including
proxy and logging policy for bearer URLs); authenticated sign-in and password,
abuse-prevention and timing policies; and monitoring and operational recovery.
None of these prerequisites is supplied by running this local demo.

## Delivery-boundary review (TC-025 / TC-026)

For TC-026, compare the **full tracked changed-file list** with prework baseline
`0065943` using `git diff --name-status 0065943 --`, check untracked files with
`git ls-files --others --exclude-standard`, and inspect baseline workflows with
`git ls-tree -r --name-only 0065943 -- .github/workflows`. At this task's review,
the baseline had no `.github/workflows` entries and the changed-file list added
no `.github/workflows` file, hosting/deployment configuration or deployment
script. Existing `.github/futuristic/` assessment files are not deployment
workflows. This is a **repository change-set finding only**.

TC-025 is a separate **manual action-record review**: inspect a complete,
auditable record of delivery actions for deploy, publish, hosting or
external-environment operations. Such a complete action record is not available
in this repository review. Therefore no-deployment across the entire delivery
is **unverified (evidence gap)**; the clean file diff does not prove no
deployment action occurred. No deployment is part of these local instructions.
