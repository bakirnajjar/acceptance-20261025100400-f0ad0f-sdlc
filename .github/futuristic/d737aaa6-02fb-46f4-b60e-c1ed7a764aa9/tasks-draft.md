# Solution-design implementation graph — T002 draft

**Status:** Future coding tasks for review, not implementation or a `docs/sdlc` deliverable. These `TASK-NNN` IDs are design identifiers, not the current run's ledger tasks. The approved predecessor requirements are `REQ-001`–`REQ-021`; the only observed screen is the sign-in wireframe. Recovery screens S2–S6 and route names below are proposals. The sign-in button's authentication outcome is unspecified; no task promises a sign-in implementation. A pytest-only fixture may represent active sessions without adding a public test route.

The proposed small, single-process Python 3.12/Flask app uses Jinja-rendered pages, a recovery service, an application-local locked store holding only synthetic accounts and reset/session state, and a private in-memory notification sink. Browser contracts are `GET /sign-in`, `GET/POST /reset/request`, `GET /reset/confirmation`, `GET /reset/<token>` followed by a secret-free new-password URL, `POST /reset/complete`, and success/unavailable pages. These are design choices, not observed UI or deployed interfaces. There is no database migration, outbound provider, or hosting change; persistence and multi-worker operation would need a separate design. A valid request to a capped known account has the same generic outward acknowledgement as a known or unknown valid identifier; internally only accepted known-account requests issue links. This reconciles the hourly limit with account non-disclosure without inventing an unknown-account quota. Capture safe aggregate diagnostics without identifiers, passwords, links, or notification payloads.

## Dependency-ordered future tasks

- **TASK-001 — Establish the synthetic Flask foundation**
  - **description:** Set up a Python 3.12 Flask application factory, server-template plumbing, isolated in-memory store and private notification sink. Seed only explicitly synthetic `.test` accounts with adaptive password hashes, expose injectable UTC clock/hasher/token factory for tests, and keep state and sink inaccessible from public inspection endpoints. Propose local dependency metadata, not deployment configuration.
  - **requirement_ids:** `["REQ-014","REQ-015","REQ-016"]`
  - **depends_on:** `[]`
  - **acceptance_criteria:** `["A future Python 3.12 pytest smoke check creates the Flask app and verifies its synthetic-only accounts, in-memory store and private sink without contacting an external account or notification service.","The runtime/dependency configuration names Python 3.12 and Flask; starting the app does not introduce a persistent database or deployment workflow."]`
  - **source_references:** `[{"source_type":"user_story","source_id":"user_story","locator":"characters 0-16000"}]`

- **TASK-002 — Render the observed sign-in entry**
  - **description:** Build server-rendered S1 and a minimal S2 request-entry GET route so the blue underlined Forgot password? link actually starts recovery. Match the pictured white canvas, centered outlined card, heading, input labels/placeholders, dark button and footer. Use a password-type input to satisfy the approved masking requirement, rather than claiming the image proves behavior. Keep the button visible without promising authentication. Provide programmatic labels, visible focus and keyboard-operable link.
  - **requirement_ids:** `["REQ-001","REQ-002","REQ-003","REQ-004","REQ-005","REQ-006","REQ-017"]`
  - **depends_on:** `["TASK-001"]`
  - **acceptance_criteria:** `["A future Flask-client check of GET /sign-in finds the centered outlined sign-in card on white, heading Sign in, labeled Email address with name@example.com placeholder, labeled type=password field with ******** placeholder, dark Sign in button, and exact No account? Contact your administrator. footer.","Following the blue underlined Forgot password? link reaches an S2 server-rendered request-entry page; no test asserts the pictured button authenticates."]`
  - **source_references:** `[{"source_type":"user_story","source_id":"user_story","locator":"characters 0-16000"},{"source_type":"attachment","source_id":"fd6b3020-ac35-442c-bd77-c53062c11e9c","locator":"sign-in-wireframe.png"},{"source_type":"knowledge","source_id":"bcf198d8-a628-401c-8641-b726fcbd00b5","locator":"v1, chunk 0"}]`

- **TASK-003 — Implement private request issuance and limiting**
  - **description:** Implement a recovery-service operation for normalized synthetic identifiers. Serialize a sliding trailing-hour window of *accepted* requests for each known account; accept at most five, generate cryptographically random fresh bearer links, retain only token digests in token records and append link events only to the private in-memory sink. Unknown/capped requests issue nothing and return no account-specific outcome to routes. Couple slot reservation, token creation and sink append so issuance errors do not consume a slot. Do not impose an invented unknown-account quota.
  - **requirement_ids:** `["REQ-007","REQ-008","REQ-015"]`
  - **depends_on:** `["TASK-001"]`
  - **acceptance_criteria:** `["With an injected UTC clock, six known-account requests in a rolling hour issue at most five links; a request after the oldest accepted timestamp leaves the trailing hour can issue another.","Unknown and capped identifiers yield no issued link and no account-specific service response; an injected issuance or sink failure does not consume an accepted slot."]`
  - **source_references:** `[{"source_type":"knowledge","source_id":"bcf198d8-a628-401c-8641-b726fcbd00b5","locator":"v1, chunk 0"},{"source_type":"user_story","source_id":"user_story","locator":"characters 0-16000"}]`

- **TASK-004 — Wire the indistinguishable request pages**
  - **description:** Complete S2/S3 with a labeled identifier form, CSRF protection, and `POST /reset/request` calling TASK-003. For otherwise equivalent syntactically valid known, unknown and capped submissions, emit the same redirect/status, public headers/cookie behavior and generic server-rendered acknowledgement without identifier, link or throttle detail. Give malformed input and CSRF failures generic non-account-specific handling; keep the sign-in return link and accessible status/error presentation.
  - **requirement_ids:** `["REQ-006","REQ-007","REQ-008","REQ-017"]`
  - **depends_on:** `["TASK-002","TASK-003"]`
  - **acceptance_criteria:** `["A future Flask-client test follows S1 to S2, submits otherwise equivalent known, unknown and capped valid identifiers, and compares status, location, public headers, cookies and S3 content for parity while inspecting the private sink to find links only for accepted known-account requests.","S2 and S3 HTML is rendered by Flask templates with named controls and generic feedback; public pages never expose a reset secret."]`
  - **source_references:** `[{"source_type":"attachment","source_id":"fd6b3020-ac35-442c-bd77-c53062c11e9c","locator":"sign-in-wireframe.png"},{"source_type":"knowledge","source_id":"bcf198d8-a628-401c-8641-b726fcbd00b5","locator":"v1, chunk 0"},{"source_type":"user_story","source_id":"user_story","locator":"characters 0-16000"}]`

- **TASK-005 — Validate links and render recovery forms**
  - **description:** Resolve bearer links against stored digests and issuance timestamps; permit only unused links strictly before `issued_at + 30 minutes`. Hand off to a short-lived opaque server-held reset intent so S4's labeled new-password form and its submission URL do not contain the link secret; S6 handles invalid, used or expired links with generic retry and sign-in navigation. Recheck validity when rendering and at later completion; GET alone neither consumes a link nor changes a password. Protect forms with CSRF and prevent link exposure through page markup, redirect targets, referrers, caches and application logs; document unavoidable initial URL/history exposure.
  - **requirement_ids:** `["REQ-009","REQ-010","REQ-017"]`
  - **depends_on:** `["TASK-003","TASK-004"]`
  - **acceptance_criteria:** `["A future injected-clock check allows an unused link immediately before the 30-minute boundary but rejects it at and after the boundary; an already-consumed or unknown link goes to S6, never S4.","GET of an eligible link produces an S4 form via a secret-free redirect and intent, does not consume the link, and neither rendered page nor logs include the raw secret."]`
  - **source_references:** `[{"source_type":"knowledge","source_id":"bcf198d8-a628-401c-8641-b726fcbd00b5","locator":"v1, chunk 0"},{"source_type":"user_story","source_id":"user_story","locator":"characters 0-16000"}]`

- **TASK-006 — Represent revocable active sessions**
  - **description:** Add an opaque server-side session registry scoped to synthetic account IDs, an active-session check, and an operation to revoke *every* represented session for one account. Make multiple sessions constructible through test fixtures, not a public test route or an invented authentication flow. If authentication is later authorized, it must use this revocable registry rather than client-only state.
  - **requirement_ids:** `["REQ-012"]`
  - **depends_on:** `["TASK-001"]`
  - **acceptance_criteria:** `["A future fixture creates two active sessions for one synthetic account and one for a different account; revoking the first account makes both of its sessions inactive while leaving the other account's session active.","No public sign-in behavior or test-only session-creation route is introduced solely to make the fixture work."]`
  - **source_references:** `[{"source_type":"knowledge","source_id":"bcf198d8-a628-401c-8641-b726fcbd00b5","locator":"v1, chunk 0"},{"source_type":"user_story","source_id":"user_story","locator":"characters 0-16000"}]`

- **TASK-007 — Complete resets as one logical operation**
  - **description:** Handle S4's CSRF-protected nonempty new-password submission. Under the single-process store lock, recheck unused-link eligibility and the strict issuance-based deadline, replace the synthetic account's adaptive password hash, consume the token, invalidate all of its represented sessions and append an owner-addressed success notification to the private sink as an all-or-nothing logical operation. Make failures, including sink failure, avoid a false success or partial reset; competing completions allow exactly one success. Redirect to S5 only on success, otherwise give a generic recoverable or S6 response. Never echo passwords, links or owner information.
  - **requirement_ids:** `["REQ-009","REQ-010","REQ-011","REQ-012","REQ-013","REQ-015","REQ-017"]`
  - **depends_on:** `["TASK-005","TASK-006"]`
  - **acceptance_criteria:** `["For a valid unused synthetic link, a future test verifies the new password hash, consumed token, all represented owner sessions inactive and exactly one owner-addressed in-memory success notice; a replay or completion at/after 30 minutes changes none of those states.","Two concurrent submissions cannot both succeed; an injected sink failure neither reports S5 success nor leaves a changed password, consumed token or selectively revoked sessions."]`
  - **source_references:** `[{"source_type":"knowledge","source_id":"bcf198d8-a628-401c-8641-b726fcbd00b5","locator":"v1, chunk 0"},{"source_type":"user_story","source_id":"user_story","locator":"characters 0-16000"}]`

- **TASK-008 — Add end-to-end pytest coverage**
  - **description:** Add automated Flask-client and service pytest tests of the pictured S1, linked S2/S3, server rendering, synthetic-only fixtures, private sink, known/unknown/capped response parity, rolling-hour fifth/sixth requests, invalid/replayed links, 30-minute edge, password change, multiple-session invalidation, owner notice and failure/concurrency behavior. Use injected clock and isolated in-memory state; do not use live accounts or external transport. These are future checks, not current passing tests.
  - **requirement_ids:** `["REQ-001","REQ-002","REQ-003","REQ-004","REQ-005","REQ-006","REQ-007","REQ-008","REQ-009","REQ-010","REQ-011","REQ-012","REQ-013","REQ-014","REQ-015","REQ-016","REQ-017","REQ-018"]`
  - **depends_on:** `["TASK-002","TASK-004","TASK-005","TASK-006","TASK-007"]`
  - **acceptance_criteria:** `["At a future coding checkpoint, pytest runs under Python 3.12 and exercises every stated scenario, including public response parity and invalidation of more than one represented active session.","The suite verifies the unavailable/success branches, no secret in public markup, and no external notification delivery rather than inferring them from UI appearance."]`
  - **source_references:** `[{"source_type":"user_story","source_id":"user_story","locator":"characters 0-16000"},{"source_type":"attachment","source_id":"fd6b3020-ac35-442c-bd77-c53062c11e9c","locator":"sign-in-wireframe.png"},{"source_type":"knowledge","source_id":"bcf198d8-a628-401c-8641-b726fcbd00b5","locator":"v1, chunk 0"}]`

- **TASK-009 — Document limits and enforce delivery boundary**
  - **description:** Document how to run the local synthetic demo and pytest, the private sink's lack of external link delivery, restart loss, single-process locking, absent durable/shared rate limit or session state, residual link/HTTP/cookie risks, and changes required before production use. Add an explicit review checklist of delivery actions and changed files for **no deployment** and **no new deployment workflow**; do not add hosting, deployment scripts or workflow files. This reviewable boundary implements negative requirements without a coverage disposition or a claim that a deployment did not happen yet.
  - **requirement_ids:** `["REQ-019","REQ-020","REQ-021"]`
  - **depends_on:** `["TASK-008"]`
  - **acceptance_criteria:** `["A future reviewer can find the stated production limitations, local-only run/test instructions and an explicit warning that the in-memory sink is not owner delivery.","Before future delivery, review the work/action record to verify no deployment was performed and inspect the repository changes to verify no deployment workflow was added; record that result without running a deployment."]`
  - **source_references:** `[{"source_type":"user_story","source_id":"user_story","locator":"characters 0-16000"}]`

## Review notes

- **Coverage dispositions:** None proposed: each of `REQ-001`–`REQ-021` has at least one future task. The no-deployment and no-workflow requirements have an explicit documentation/review task, not fictional code implementation.
- **Unresolved decisions:** Whether sign-in should authenticate and how sessions originate beyond fixtures; how an owner privately accesses a sink-only link; a new-password policy; exact S2–S6 copy/layout and local HTTPS/cookie operation; whether future restart/multi-worker persistence is desired. These are not existing requirements or evidence of implementation.
- **Validation expectation:** The listed checks are proposed future pytest/review acceptance criteria. This T002 draft contains no runnable application, passing-test claim, deployed service or modification to the deliverable `docs/sdlc` files.
