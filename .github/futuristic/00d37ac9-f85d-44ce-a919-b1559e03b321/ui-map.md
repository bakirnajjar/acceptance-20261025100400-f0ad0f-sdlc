# T001 — UI evidence and requirements map

This is a planning map for the later `ui_analysis` contract, **not** the final JSON or Markdown deliverable. UI analysis is applicable: the story supplies one sign-in wireframe, while the recovery pages below are proposals only. Approved predecessor identifiers are REQ-001–REQ-021 from `docs/sdlc/requirements_analysis.json`; citing that approved output does not create a stage-output source reference.

## Authorized source references

| Short name | Exact source reference |
| --- | --- |
| Image | `{"source_type":"attachment","source_id":"fd6b3020-ac35-442c-bd77-c53062c11e9c","locator":"sign-in-wireframe.png"}` |
| Story | `{"source_type":"user_story","source_id":"user_story","locator":"characters 0-16000"}` |
| Standard | `{"source_type":"knowledge","source_id":"bcf198d8-a628-401c-8641-b726fcbd00b5","locator":"v1, chunk 0"}` |

No source-reference locator was returned for the prior stage. The image is the **only** supplied visual: a 480 × 360 white canvas, with an approximately centered black/gray outlined card at x70–410 and y20–342. It depicts no other screen or interaction. In the map below, **Observed** means a feature actually depicted by the image and cites Image; **Proposed (inferred, not observed)** means a suggested UI realization or state, not evidence of implementation. The Standard and Story establish requirements, not observed screen appearances.

## Screen inventory

### S1 — Sign in

- **Observed — Image; REQ-001–REQ-006:** Purpose indicated by the “Sign in” heading. The card has an “Email address” label over an empty bordered input with gray `name@example.com` placeholder; a “Password” label over a bordered input showing gray `********` placeholder; a blue underlined “Forgot password?” link beneath the password field; a dark near-black rectangular “Sign in” button; and the gray footer “No account? Contact your administrator.” The card is outlined on the white canvas. Data displayed are placeholders and static copy, **not** an entered password or account record. Visible affordances are two inputs, a link, and a button; the screenshot does **not** establish what occurs when any is operated or whether entered password characters are masked.
- **Proposed (inferred, not observed) — Image, Standard; REQ-003, REQ-006, REQ-017:** Use a real password-type input to satisfy the approved masking requirement (the image shows only an asterisk placeholder). Make “Forgot password?” lead to S2; do not claim a working sign-in outcome. Render page content on the server. Whether the button authenticates and what feedback it gives remain open.

### S2 — Recovery request

- **Proposed (inferred, not observed) — Standard, Story; REQ-006–REQ-008, REQ-017:** Purpose: request a reset for an account identifier. Suggested components/data: a heading explaining recovery, a labeled email/account input, a request-submit control and a way back to S1. The user can submit an identifier; the exact page copy, layout, identifier format and routing are not evidenced. The Standard requires identical reset-request responses for existing and nonexistent accounts and no more than five accepted requests per account per hour. Throttle feedback must not reveal existence; **whether and how its response matches an ordinary request is undecided**.

### S3 — Request confirmation

- **Proposed (inferred, not observed) — Standard; REQ-007, REQ-008, REQ-017:** Purpose: acknowledge an ordinary reset request without disclosing account existence. Suggested components/data: generic confirmation copy and a return-to-S1 link, showing no “account found/not found” or reset-link secret. No user-specific account data is proposed. The normal response must be identical for otherwise equivalent existing/nonexistent identifiers. Precise copy and throttled-request presentation are open; do not assume a throttled response is definitely identical to an ordinary request.

### S4 — New password

- **Proposed (inferred, not observed) — Standard, Story; REQ-009–REQ-012, REQ-017:** Purpose: allow a holder of an issued, unused, unexpired reset link to supply a new password. Suggested components/data: recovery heading, labeled password-type input, submit control, and accessible feedback. Do not display the link secret or account-existence information. A link is single-use and ceases to allow completion at **30 minutes or later after issuance**; these checks apply when completing the reset. A valid completion changes the synthetic account password and signs out all of its active sessions. Password policy, confirmation-input requirement, and exact link transport are unresolved.

### S5 — Reset success

- **Proposed (inferred, not observed) — Standard, Story; REQ-011–REQ-013, REQ-015, REQ-017:** Purpose: confirm a completed reset and offer a return to S1. Suggested components/data: generic success message and sign-in link, with no reset-link secret. Display only after valid completion, not on an unsuccessful attempt. Successful reset signs out every active session for the account and notifies its owner; the story calls for capture in an **in-memory notification sink**, not presumed external delivery. Neither the notification mechanism nor this page is depicted in the image.

### S6 — Invalid/expired/used link

- **Proposed (inferred, not observed) — Standard; REQ-009, REQ-010, REQ-017:** Purpose: explain that reset cannot be completed with this link and allow a new request via S2 or return to S1. Suggested components/data: non-secret failure copy with a labeled next-step link; no password submission through a rejected link. Used links cannot complete again; expired links cannot complete at or after the 30-minute issuance boundary. Whether invalid, expired and used reasons should be distinguished publicly is an open content/security decision.

## Stepwise flows and boundaries

1. **Observed — Image; REQ-001–REQ-006:** S1 depicts the sign-in card and “Forgot password?” link. No click, submitted form, navigation or authentication result is visible.
2. **Proposed (inferred, not observed) — Image, Standard; REQ-006, REQ-017:** Activating the S1 link opens S2 as the entry to recovery.
3. **Proposed (inferred, not observed) — Standard; REQ-007, REQ-008:** Submit S2 identifier; for ordinary requests show S3 with an identical response regardless of existence. Enforce the five-accepted-requests/account/hour limit without disclosing account existence. The exact response under throttling is unresolved, not asserted to equal the ordinary response.
4. **Proposed (inferred, not observed) — Standard, Story; REQ-009–REQ-011, REQ-015:** If an eligible synthetic account has an issued link, the owner obtains it through an as-yet-unspecified means (the story specifies an in-memory notification sink, not external transport). Opening an eligible link presents S4. An invalid, used, or expired link instead leads to S6; no reset completes.
5. **Proposed (inferred, not observed) — Standard, Story; REQ-009–REQ-013:** Submit a new password on S4. If the link is still unused and younger than 30 minutes from issuance, change the account password, consume the link, sign out every active session, capture an owner notification and show S5. Reuse or expiry at submission must not complete the reset; show S6 or an equivalent failure state with a way to request again.
6. **Proposed (inferred, not observed) — Standard; REQ-009, REQ-010:** S6 leads back to S2 for a new request, or S1; S5 offers return to S1. No automatic new session or successful sign-in is assumed.

## Accessibility and per-screen states

All items in this section are **Proposed (inferred, not observed)**, not image observations. Use keyboard-operable links/buttons with a logical DOM/tab/focus order, visible focus indication, readable text/control contrast (including gray placeholders, blue link and dark button), persistent programmatic labels rather than placeholder-only names, and accessible names matching the visible controls. On server-rendered navigation, move focus to the new page heading or error summary; associate inline errors with inputs and announce status/error text to screen readers without exposing account existence. The image establishes none of these qualities. Story supports server-rendered pages (REQ-017); Image provides visual context for S1; Standard governs recovery security (REQ-006–REQ-013).

| Screen | Empty / validation | Error and inaccessible-condition feedback | Pending / loading |
| --- | --- | --- | --- |
| S1; REQ-002–REQ-004, REQ-006 | Empty email/password fields as pictured; propose required-field errors on submission, persistent “Email address” and “Password” accessible names; an entered password should be masked per REQ-003, not because the screenshot proves it. | Propose field-level errors and announced summary without assuming an authentication backend, outcomes, or account-specific sign-in copy. | Propose non-duplicating, accessible pending feedback only if sign-in submission is implemented; no loading state is observed. |
| S2; REQ-006–REQ-008 | Empty identifier requires an accessible error; malformed input handling and accepted identifier format require product clarification; retain label on re-render. | Propose neutral error wording and no existence disclosure. If limited, do not accept a sixth request for the known account within an hour; exact public throttle response is open. | Propose a generic submission-pending state with no account-specific signal; do not claim the wireframe depicts it. |
| S3; REQ-007–REQ-008 | No form data required; empty account-specific content is intentional. | Avoid a “not found” or “found” variant for ordinary requests; if confirmation rendering fails, offer generic recoverable error without existence disclosure. Throttle copy remains undecided. | If navigation waits, announce generic progress; final ordinary response remains account-indistinguishable. |
| S4; REQ-009–REQ-011 | Require a nonempty new password with an associated label; do not invent length, complexity or confirmation rules. | On invalid/used/expired link, prevent completion and provide S6 (including expiration at 30 minutes after issuance); on server failure, announce an error without falsely claiming success. | Propose generic submit-pending feedback without leaking the token or duplicating submission. |
| S5; REQ-011–REQ-013 | No form fields or account data required; success text and a named S1 link. | If reset or notification processing has not succeeded, do not present S5 as completed; exact failure-handling copy remains open. | Propose only a generic page-navigation pending state, not a claim about actual background delivery. |
| S6; REQ-009–REQ-010 | No password fields; present clear recovery-request and sign-in links with programmatic names. | Explain inability to use the link without echoing its token; safe level of distinction among invalid/expired/used is open. | Propose generic navigation-pending feedback, if needed; no further reset operation occurs here. |

## Coverage inventory

| Approved requirements | Directly evidenced by wireframe? | UI mapping / boundary |
| --- | --- | --- |
| REQ-001 | Yes, Image | S1 white canvas and centered outlined heading card. |
| REQ-002 | Yes, Image | S1 labeled empty email input and `name@example.com` placeholder. |
| REQ-003 | Partly, Image | S1 password label and `********` placeholder visible; masking of characters entered later is **not** observed. |
| REQ-004 | Yes, Image | S1 dark rectangular “Sign in” button; result unobserved. |
| REQ-005 | Yes, Image | S1 administrator-contact footer text; no contact interaction inferred. |
| REQ-006 | Partly, Image + Standard | Blue underlined S1 link pictured; starting recovery is specified by Standard, not demonstrated by the static image. Proposed transition S1 → S2. |
| REQ-007 | No | Standard governs S2 → S3 identical response for account existence; no visual proof. |
| REQ-008 | No | Standard governs S2 limit of five accepted requests/account/hour; response under throttle open. |
| REQ-009 | No | Standard governs S4 and S6 single-use link handling. |
| REQ-010 | No | Standard governs S4 and S6 expiry 30 minutes after issuance. |
| REQ-011 | No | Story + Standard support proposed S4 → S5 valid password change; no visual proof. |
| REQ-012 | No | Standard: successful reset signs out every active session; not verifiable from a screen. |
| REQ-013 | No | Standard: notify owner after every successful reset; S5 does not prove delivery. |
| REQ-014 | No | Story: synthetic accounts are a data constraint, not discernible from wireframe. |
| REQ-015 | No | Story: in-memory notification sink, not observable on wireframe or asserted as external delivery. |
| REQ-016 | No | Story: Python 3.12 and Flask are implementation constraints, not visual evidence. |
| REQ-017 | No | Story: proposed pages server-rendered; a static screenshot cannot verify rendering mechanism. |
| REQ-018 | No | Story: pytest coverage is a delivery/test constraint, not a visual UI feature. |
| REQ-019 | No | Story: production-limitations documentation is not shown. |
| REQ-020 | No | Story: no deployment; not a UI behavior or visible fact. |
| REQ-021 | No | Story: no deployment workflows; not a UI behavior or visible fact. |

Thus **REQ-007–REQ-021 have no direct visual coverage**. Proposed UI touchpoints for REQ-007–REQ-013 and REQ-017 cannot establish implementation, session handling, notification capture, testing, documentation, runtime or deployment status.

## Assumptions and open questions

**Assumptions for analysis, not observations:** only S1 is pictured; S2–S6 are proposed server-rendered surfaces to make the specified recovery flow intelligible, with no prescribed routes, copy or layout. In-memory notifications do not imply external delivery. No sign-in outcome, registration path, restart persistence, reset-token transport or password complexity rule is established. Unknown-account limiting behavior is unspecified; known accounts must respect five accepted requests per hour while ordinary responses must not identify account existence.

**Open questions (nonblocking for this map):**

1. Does the “Sign in” button authenticate, and what response or error copy is expected?
2. What are the exact layout, titles, copy and navigation affordances for S2–S6? Should invalid, expired and used links share public wording?
3. What does a throttled request display, and must it match an ordinary response? How are nonexistent-account requests counted while preserving non-enumeration?
4. How can synthetic owners access issued links when notifications are captured in memory, and what is the approved mechanism for viewing them?
5. What password policy, if any, applies to the new-password field; is a confirmation field desired?
6. How is “every active session” represented, and what should the interface say about post-reset sign-out?
7. What validation copy, field format, focus target, pending feedback and failure-retry behavior are required for each proposed screen?
