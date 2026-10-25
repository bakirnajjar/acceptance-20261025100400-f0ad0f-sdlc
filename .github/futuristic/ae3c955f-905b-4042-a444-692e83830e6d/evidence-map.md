# T001 evidence-to-behavior map

This is a candidate map for the subsequent requirements contract, not that contract. Each row describes one observable behavior or delivery constraint; the final contract should give it a testable Given/When/Then acceptance criterion. Do not infer pixel dimensions, authentication rules, or recovery UI details from the wireframe.

## Exact evidence references

| Key | `source_type` | `source_id` | `locator` | Scope |
| --- | --- | --- | --- | --- |
| S | `user_story` | `user_story` | `characters 0-16000` | Complete pinned story; `next_offset: null`, no end marker |
| W | `attachment` | `fd6b3020-ac35-442c-bd77-c53062c11e9c` | `sign-in-wireframe.png` | Reader returned a reference only; use the supplied visual observations, not invented image text; no visible acceptance marker |
| K | `knowledge` | `bcf198d8-a628-401c-8641-b726fcbd00b5` | `v1, chunk 0` | Run-specific account recovery standard, ACC-STD-01–03 |

No approved prior stage outputs. Identically worded knowledge results from other libraries are not cited.

## Candidate atomic behaviors

| ID | Candidate behavior / acceptance probe | Evidence |
| --- | --- | --- |
| REQ-001 | Given the sign-in page is opened, then show a centered outlined sign-in card with the heading “Sign in” on a white background. No exact dimensions or color codes implied. | S, W |
| REQ-002 | Given the sign-in card, then show an “Email address” labeled input with placeholder `name@example.com`. | W |
| REQ-003 | Given the sign-in card, then show a “Password” labeled masked input with placeholder `********`. | W |
| REQ-004 | Given the sign-in card, then show a “Sign in” button as a dark rectangular control; its authentication outcome is unspecified. | W |
| REQ-005 | Given the sign-in card, then show “No account? Contact your administrator.” as footer copy; this does not imply registration. | W |
| REQ-006 | Given the sign-in page, when the blue underlined “Forgot password?” link is selected, then start a password-reset request flow. | W, K (ACC-STD-01) |
| REQ-007 | Given reset requests for existing and nonexistent accounts, when each is submitted, then the responses are identical. | K (ACC-STD-01) |
| REQ-008 | Given repeated requests for one account, when requests occur within one hour, then no more than five are accepted for that account. | K (ACC-STD-01) |
| REQ-009 | Given a reset link has completed a reset, when it is used again, then it cannot complete another reset. | K (ACC-STD-02) |
| REQ-010 | Given a link issued 30 minutes earlier, when it is used after its expiry, then it cannot complete a reset. | K (ACC-STD-02) |
| REQ-011 | Given a valid reset flow for a synthetic account, when reset completes, then that account's password is changed. | S, K (ACC-STD-02) |
| REQ-012 | Given an account with active sessions, when its password reset completes, then every active session for that account is signed out. | K (ACC-STD-02) |
| REQ-013 | Given any successful password reset, when it completes, then the account owner is notified. | K (ACC-STD-03) |
| REQ-014 | Given the application is run, then its accounts are synthetic rather than real customer identities. | S |
| REQ-015 | Given a notification is produced, then it is captured in an in-memory notification sink rather than delivered externally. | S |
| REQ-016 | Given the delivered application, then its implementation uses Python 3.12 and Flask. | S |
| REQ-017 | Given an application page is requested, then the page is rendered server-side. | S |
| REQ-018 | Given the delivered project, then automated pytest tests exercise its specified behaviors. | S |
| REQ-019 | Given the delivered documentation, then it identifies production limitations of the small application. | S |
| REQ-020 | Given the delivered project, then no deployment is performed. | S |
| REQ-021 | Given the delivered repository changes, then no deployment workflows are added. | S |

## Assumptions to carry into the final contract

- acceptance-20261025100400-f0ad0f-skill-sentinel — the acceptance skill produced this output; carry this leading marker into a final-contract assumption.
- No story end marker or attachment acceptance marker was supplied; do not invent either.
- For unknown accounts, preserve an account-existence-independent request response; do not prescribe how nonexistent accounts are counted against a *per-account* limit.
- Under throttling, do not reveal account existence; exact throttle response semantics are not specified.
- Treat “all active sessions” as all sessions represented by the application, without prescribing their storage or mechanism.
- The sign-in button is a visible affordance; successful authentication, registration, password policy, token transport, persistence across restarts, and exact recovery-page layout are not defined by the evidence.
- Use the in-memory notification sink for observable notifications; do not assume live email or another delivery channel.

## Non-blocking questions

| Question | Working assumption until clarified |
| --- | --- |
| How are requests for nonexistent accounts counted against a per-account hourly limit? | Enforce the stated five-per-account-per-hour rule for known accounts while preserving identical account-existence responses; do not assign an invented unknown-account threshold. |
| What response should a throttled request show, and must it match the ordinary reset-request response? | Keep account existence indistinguishable; leave the precise throttle response open. |
| What represents an active session in this application? | Choose an application-local representation that lets a successful reset invalidate every active session for that account. |
| Must the “Sign in” button actually authenticate, and what is the desired result? | Require the shown control but make no unsupported authentication outcome claim. |
| What password policy governs a new password? | Leave complexity and length rules unspecified. |
| How are reset links transported to an account owner? | Allow the in-memory notification sink to capture them without external sending; do not prescribe a channel. |
| Must accounts, reset state, or notifications survive application restart? | Do not assume durability beyond the synthetic-account and in-memory-sink constraints. |
| What must recovery-request and new-password pages look like? | Require functional server-rendered pages without inventing wireframes for them. |
