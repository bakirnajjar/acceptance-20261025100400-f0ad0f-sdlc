# Solution design — synthetic password reset

**Status:** Proposed architecture and future implementation tasks, not an implemented application or passing test report. The only observed UI is the supplied sign-in wireframe; S2–S6 below are proposals. No deployment or workflow change is in scope.

## Evidence and traceability

| Evidence | Exact source reference | What it establishes |
| --- | --- | --- |
| Pinned story | `user_story` / `user_story` / `characters 0-16000` | Python 3.12, Flask, server-rendered pages, pytest, synthetic accounts, in-memory notification sink, production-limitations documentation and no deployment/workflows. |
| Supplied image | `attachment` / `fd6b3020-ac35-442c-bd77-c53062c11e9c` / `sign-in-wireframe.png` | A white 480×360 canvas with a roughly centered outlined sign-in card; its labels, placeholders, link, button and footer are visible. It does **not** establish typed-input masking, authentication, link navigation or recovery-page appearance. |
| Run-specific recovery standard | `knowledge` / `bcf198d8-a628-401c-8641-b726fcbd00b5` / `v1, chunk 0` | Identical existing/nonexistent reset-request responses; at most five requests per account per hour; single-use links expiring 30 minutes after issuance; all active sessions signed out and owner notified after success. |

Approved requirements analysis supplies `REQ-001`–`REQ-021`; approved UI analysis distinguishes observed S1 from proposed S2–S6. The approved risk document identifies prospective failure modes, not defects. No separate curated architecture or operations standard was found; all architecture choices below are **proposals**, not organizational standards. The JSON contract uses only the exact evidence references in the table, without inventing `stage_output` locators.

## Architecture and component responsibilities

1. **Flask browser routes and Jinja templates** render S1 and proposed S2–S6 on the server. S1 matches the pictured white background, centered outlined card, “Sign in” heading, labeled “Email address” input with `name@example.com` placeholder, labeled password input with `********` placeholder, dark rectangular “Sign in” button, blue underlined “Forgot password?” link and exact “No account? Contact your administrator.” footer (`REQ-001`–`REQ-006`, `REQ-017`). Implement `type=password` to fulfill `REQ-003`; the image alone does not prove typed-input masking. The button is a visible control **without a specified authentication result**. Recovery pages have persistent programmatic labels, keyboard-operable controls, visible focus, associated generic errors/status and sign-in navigation; exact layout/copy is not evidenced.
2. **Recovery service** owns identifier normalization, request limiting and issuance, digest-based token lookup, expiry/replay checks, reset completion, session invalidation and notification orchestration. Public routes receive account-independent, sanitized results; they never expose a raw token, existence flag or private sink contents.
3. **Application-local locked store** holds synthetic accounts and password hashes, accepted-request timestamps, reset-token digests, opaque reset intents and revocable server-side active-session records. A lock serializes single-process decisions and reset state changes. Sessions are represented so all can be invalidated after reset even though sign-in authentication is not promised. A pytest-only fixture can create several sessions; do not add a public test endpoint.
4. **Private in-memory notification sink** captures links for known synthetic accounts and owner-addressed notices after completed resets (`REQ-013`, `REQ-015`). It is not an external delivery mechanism or public link-discovery API; how an ordinary owner obtains a link is unresolved.

The flow is browser → Flask route/template → recovery service → locked store and private sink. There is no external API, queue, database, mail provider or hosting service. Use synthetic `.test` identities only (`REQ-014`); no migration is needed because there is no durable schema.

## Proposed browser and internal contracts

| Interaction | Input and behavior | Public result |
| --- | --- | --- |
| `GET /sign-in` (S1) | None; rendered wireframe-aligned presentation. | A “Forgot password?” link to `GET /reset/request`; no inferred Sign in authentication. |
| `GET /reset/request` (S2) | None. | Labeled identifier form, CSRF token and S1 return link. |
| `POST /reset/request` | Form `identifier` and CSRF token. Normalize consistently. Under the lock, for a **known** account accept fewer than five previous accepted requests in the trailing hour, generate a fresh link and record it privately; unknown/capped submissions issue nothing. | For otherwise equivalent syntactically valid known, unknown and capped submissions, identical redirect/status, public headers, cookies and generic S3 content. No account status, throttle count or link. Invalid input/CSRF can receive generic account-independent errors. |
| `GET /reset/confirmation` (S3) | None. | Generic acknowledgement and S1 link, without identifier or secret. |
| `GET /reset/<opaque-token>` | Lookup by digest; require unused token and `now < issued_at + 30 minutes`. Do **not** consume on GET. Create a short-lived opaque server-held reset intent. | Redirect to a secret-free `GET /reset/new` on success, or S6 on unknown/expired/used token; no token in redirect target or rendered page. |
| `GET /reset/new` (S4) | Valid reset-intent cookie and rechecked token. | Labeled password-type input and CSRF-protected form; otherwise S6. |
| `POST /reset/complete` | Nonempty new password, reset intent and CSRF token. Recheck unused/expiry under the lock. Commit new adaptive password hash, consumed token, revocation of **every represented active session** and owner notice as one logical operation. | S5 only after all effects succeed; otherwise recoverable generic error or S6. Do not echo a password, link, identifier or owner. |
| `GET /reset/success` (S5); `GET /reset/unavailable` (S6) | None. | S5 follows successful completion with a S1 return link; a direct S5 GET is not evidence of a reset. S6 handles unknown, expired and used links generically, with new-request/S1 navigation. |

“Accepted” denotes an internal issued/reserved link, **not** the outward acknowledgement. In a sliding one-hour window, discard timestamps at or before `now - 1 hour` and accept a request only if fewer than five remain. An issuance/sink error must not consume an accepted slot. The proposed identical capped-account acknowledgement reconciles the limit with account non-disclosure; it is a design choice, not specified throttle copy. No separate nonexistent-identifier quota is invented. Identical public response shape does not guarantee identical processing time: avoid obvious timing differences and document residual enumeration risk rather than claiming constant-time HTTP behavior.

Conceptual records: `Account(id, normalized_identifier, password_hash, synthetic_owner)`, `AcceptedRequest(account_id, accepted_at_utc)`, `ResetToken(token_digest, account_id, issued_at_utc, consumed_at_utc?)`, `ResetIntent(intent_digest, token_digest, expires_at_utc)`, `ActiveSession(session_id_digest, account_id, active)` and `Notification(owner, kind, created_at_utc, private_payload)`. Raw reset links exist transiently only in the private notification sink; never store raw tokens in token records or raw passwords in account records. Every protected request of any later authorized authenticated flow must check server-side session activity; unrevocable client-only state cannot satisfy sign-out of all sessions. No live customer data or external recipients are needed.

## Security, reliability and operations

- Generate independent high-entropy bearer secrets using a cryptographically secure RNG; store their one-way digests. Use an adaptive, maintained password hasher with parameters selected and documented in implementation. Check both unused state and strictly-before-30-minute issuance deadline **again at completion**, including if S4 was opened before expiry. Two competing completions yield at most one success and one notice (`REQ-009`–`REQ-013`).
- State-changing forms use CSRF protection; dynamic template text is escaped. Reset-intent and application-session cookies are opaque, HttpOnly and SameSite, and Secure when HTTPS is used. Redirect away from the initial raw-token URL, omit third-party assets, use `Cache-Control: no-store` and `Referrer-Policy: no-referrer`, and suppress token-bearing paths/queries in access logs. The initial URL can still appear in browser history or the private sink; local HTTP is **not** a production transport guarantee.
- Under a **single process-local lock**, prepare/check a reset and commit password replacement, token consumption, all-session revocation and sink append together. Use staged state/copy-and-swap or rollback so sink failure leaves no changed password, consumed token or selectively revoked sessions and never reports S5 success. Failures give generic recoverable feedback; no distributed atomicity is claimed. Inject a timezone-aware UTC clock, token generator, hasher, sink and fresh store for deterministic tests.
- Log safe aggregate route outcome categories and correlation IDs only; omit identifiers, passwords, tokens, form bodies and notification payloads. Test fourth/fifth/sixth requests and rolling-hour boundary; expiry just before/at/after 30 minutes; used/unknown tokens, replay and concurrent submission; sink failure rollback; multiple sessions and owner notice; parity of public responses for known/unknown/capped cases. These are **future pytest cases**, not tests run for this document.
- A process restart discards state and reseeds synthetic accounts; separate workers do **not** share a limiter, session registry, token state or sink. No database migration applies now. Before any production consideration, separately design durable transactional storage and migration, cross-worker rate accounting and session revocation, reliable owner delivery/outbox, HTTPS and secret management, monitoring, backup/recovery and an authenticated sign-in policy if desired. This deliverable adds **no deployment and no deployment workflow** (`REQ-019`–`REQ-021`).

## Significant decisions and alternatives

| Proposed choice | Alternative considered | Rationale and limit |
| --- | --- | --- |
| Python 3.12/Flask with server-rendered templates and thin route/service/store boundaries | SPA, standalone API or microservices | Matches the pinned story with less infrastructure; no running app is asserted. |
| Single locked in-memory store plus private sink | Durable DB and external mail/SMS | Matches synthetic, in-memory, no-deployment scope; restart and multi-worker operation remain unsupported. |
| Rolling accepted-issuance window and generic outward acknowledgement for known, unknown and capped valid identifiers | Fixed clock-hour buckets or a known-only public 429 | Prevents rollover over-issuance and a throttle-based existence signal. Residual timing risk and unknown-identifier abuse remain open. |
| CSPRNG single-use link stored by digest, with secret-free reset intent | Predictable or stateless link; raw token embedded in the password form | Permits issuance-based 30-minute expiry, atomic replay prevention and reduced markup exposure, though the original URL still carries a secret. |
| Server-side opaque revocable session registry; fixture-generated sessions until sign-in semantics are approved | Pure client-signed sessions; inventing sign-in authentication | Enables invalidation of all represented sessions while honoring the wireframe's evidentiary limit. |
| One logical reset commit including owner notice | Best-effort post-success notice or external send | Avoids reporting success without notice; only the in-memory sink is supported, not actual delivery. |
| No hosting, migration or deployment work | Container deployment and workflow | The pinned story explicitly excludes deployment/workflow additions; future expansion needs separate scope. |

## Dependency-ordered implementation tasks

Each `TASK-NNN` is a **future coding task**, not this document-stage run's task identifier. Full descriptions, acceptance criteria, requirement links, dependencies and exact per-task evidence references are in `solution_design.json`.

| ID | Task and independently reviewable outcome | Requirements | Depends on |
| --- | --- | --- | --- |
| `TASK-001` | Establish synthetic Flask foundation: app factory, templates, isolated store/sink, injectable test seams; verify Python 3.12/Flask and no external state. | `REQ-014`, `REQ-015`, `REQ-016` | — |
| `TASK-002` | Render wireframe-aligned S1 and linked S2 entry, including type=password and accessible controls; check exact visible content without asserting sign-in. | `REQ-001`–`REQ-006`, `REQ-017` | `TASK-001` |
| `TASK-003` | Implement private link issuance and known-account sliding-hour five-request limit with failure-safe reservation; verify sixth request and boundary. | `REQ-007`, `REQ-008`, `REQ-015` | `TASK-001` |
| `TASK-004` | Wire CSRF-protected S2/S3, generic parity for known/unknown/capped valid requests, and secret-free public output. | `REQ-006`–`REQ-008`, `REQ-017` | `TASK-002`, `TASK-003` |
| `TASK-005` | Validate unused links against the 30-minute issuance deadline; hand off to secret-free S4 or S6 and verify boundary/GET non-consumption. | `REQ-009`, `REQ-010`, `REQ-017` | `TASK-003`, `TASK-004` |
| `TASK-006` | Represent and revoke every active application session; verify two owner sessions are revoked and another owner's survives, via fixtures only. | `REQ-012` | `TASK-001` |
| `TASK-007` | Complete reset atomically, changing hash, consuming link, revoking sessions and appending owner notice; verify replay, concurrency and sink-failure rollback. | `REQ-009`–`REQ-013`, `REQ-015`, `REQ-017` | `TASK-005`, `TASK-006` |
| `TASK-008` | Add isolated Flask-client/service pytest scenarios across the observed S1 and proposed recovery flow; run only at a future coding checkpoint. | `REQ-001`–`REQ-018` | `TASK-002`, `TASK-004`, `TASK-005`, `TASK-006`, `TASK-007` |
| `TASK-009` | Document local use and production limits; review actions/changed files to verify no deployment or new deployment workflow. | `REQ-019`–`REQ-021` | `TASK-008` |

All approved `REQ-001`–`REQ-021` identifiers map to one or more tasks. **Coverage dispositions: none**. The negative deployment requirements are handled by `TASK-009`'s reviewable delivery-boundary checks, not by claiming deployment has already been audited. The proposed future coding test gate is `python3.12 -m pytest`; there is no established build or lint runner. It is not run at this document stage.

## Assumptions and open questions

This is a local-only proposed demo; the sink is not owner delivery; S2–S6 layouts and routes are design choices; the sign-in button has no specified authentication behavior. A password-complexity policy, public owner-link access, unknown-identifier abuse controls, production HTTPS/cookie configuration and durable/multi-worker state have no evidenced specification. Reviewer decisions are needed on: (1) whether/how Sign in authenticates and originates sessions; (2) how a synthetic owner can privately access a link; (3) the desired capped-response UX and any non-disclosing unknown-identifier controls; (4) minimum/confirmation/complexity password rules; (5) S2–S6 wording, validation and focus behavior; (6) whether future durable, hosted or external-delivery operation is wanted. None blocks documentation of the current proposed architecture; each would require explicit follow-up rather than being presented as an implemented fact.
