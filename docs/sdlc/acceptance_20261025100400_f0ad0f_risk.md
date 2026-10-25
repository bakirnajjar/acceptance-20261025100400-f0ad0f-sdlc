# Prospective delivery risk register

**Stage:** `custom_document` · **Stage key:** `acceptance_20261025100400_f0ad0f_risk` · **Contract version:** `1.0`

Ten prospective delivery risks cover the approved REQ-001 through REQ-021 for a small Python 3.12 Flask password-reset application. Checks are proposed, not claimed as implemented; no deployment or deployment workflow is in scope.

## Purpose and interpretation

Each risk describes a possible cause and impact followed by a practical proposed mitigation/check. Requirement links use approved `requirements_analysis` IDs only. **Must** marks the most consequential recovery-flow and account-protection risks for attention; **should** marks important presentation, verification, and delivery-boundary risks. Neither value changes a requirement's status, establishes a likelihood measurement, or asserts an existing defect.

## Evidence and scope

The story defines a Python 3.12 Flask server-rendered pytest application with synthetic accounts, an in-memory notification sink, production-limitations documentation, and no deployment or deployment workflows. The attachment shows only the sign-in page. The run-specific recovery standard defines account-independent reset-request responses, at most five requests per account per hour, single-use links expiring 30 minutes after issuance, sign-out of all active sessions on successful reset, and owner notification after every successful reset. There is no supplied implementation, test outcome, production architecture, or reset-page design.

**Exact source references** (codes below are local shorthand, not substitute locators):

| Code | source_type | source_id | locator |
| --- | --- | --- | --- |
| S1 | `user_story` | `user_story` | `characters 0-16000` |
| S2 | `attachment` | `fd6b3020-ac35-442c-bd77-c53062c11e9c` | `sign-in-wireframe.png` |
| S3 | `knowledge` | `bcf198d8-a628-401c-8641-b726fcbd00b5` | `v1, chunk 0` |

S2 records a centered outlined white sign-in card, “Sign in” heading, “Email address” input with `name@example.com`, masked-looking “Password” field with asterisks, blue underlined “Forgot password?” link, dark rectangular “Sign in” button, and “No account? Contact your administrator.” footer. The approved `requirements_analysis` output supplies the linked IDs but has no returned stage-output source reference; no locator is invented. Only the run-specific S3 source is cited, not similarly named libraries.

## Risks

### R22A08-001 — Sign-in presentation or server rendering diverges from the wireframe

- **Category / priority:** Sign-in presentation / `should`
- **Approved requirements:** REQ-001, REQ-002, REQ-003, REQ-004, REQ-005, REQ-017
- **Related risk IDs:** None
- **Evidence:** S1, S2
- **Cause:** The server-rendered sign-in template or input markup could omit or alter the centered outlined white card, “Sign in” heading, labeled “Email address” field with `name@example.com` placeholder, labeled masked “Password” field with asterisks, dark rectangular “Sign in” button, or “No account? Contact your administrator.” footer.
- **Impact:** The supplied sign-in experience and specified page behavior would not be represented accurately.
- **Proposed mitigation/check:** Compare the rendered page with the observed wireframe, inspect field labels and masking, and exercise server-rendered output. Do not infer that the visible button performs authentication.

### R22A08-002 — Forgot-password entry does not start recovery

- **Category / priority:** Recovery entry / `must`
- **Approved requirements:** REQ-006, REQ-017
- **Related risk IDs:** None
- **Evidence:** S2, S3, S1
- **Cause:** The blue underlined “Forgot password?” link could be missing, hard to recognize, or not connected to a server-rendered reset-request flow.
- **Impact:** A user could not begin recovery from the supplied sign-in page.
- **Proposed mitigation/check:** Inspect the visible link and follow it from the sign-in page to a functional reset-request entry, checking that page content is server-rendered; do not invent a visual design for recovery pages.

### R22A08-003 — Reset-request responses disclose account existence

- **Category / priority:** Request privacy / `must`
- **Approved requirements:** REQ-007
- **Related risk IDs:** None
- **Evidence:** S3
- **Cause:** Conditional response content or status for an existing versus nonexistent account, including behavior around throttling, could differ.
- **Impact:** Reset requests could reveal whether a synthetic account exists, contrary to the recovery standard.
- **Proposed mitigation/check:** Compare otherwise equivalent reset-request responses for known and unknown identifiers and inspect throttled cases for disclosure; the exact throttled response and unknown-account counting remain open, not presumed to be implemented.

### R22A08-004 — Known-account hourly reset-request limit is exceeded

- **Category / priority:** Request limiting / `must`
- **Approved requirements:** REQ-008, REQ-007
- **Related risk IDs:** None
- **Evidence:** S3
- **Cause:** Request counting, time-window boundaries, or inconsistent throttling could allow more than five accepted reset requests for one known account within an hour, or make account existence apparent.
- **Impact:** The volume control or response indistinguishability could fail.
- **Proposed mitigation/check:** Submit six requests for a known account within one hour, verify no more than five are accepted, check a window boundary, and compare responses so throttling does not reveal account existence. Unknown-account counting and the precise throttled response remain undecided.

### R22A08-005 — Reset link remains usable after consumption or expiry

- **Category / priority:** Link validity / `must`
- **Approved requirements:** REQ-009, REQ-010
- **Related risk IDs:** None
- **Evidence:** S3
- **Cause:** Link state might not be consumed on successful use, or expiry might be computed from a later event or checked with the wrong 30-minute boundary.
- **Impact:** A replayed or expired link could complete another password reset.
- **Proposed mitigation/check:** Use a valid link once and attempt replay; attempt use just before, exactly at, and after 30 minutes from issuance, confirming that the link cannot complete a reset at or after the boundary. Reset-link transport is unspecified.

### R22A08-006 — Successful reset fails to change a synthetic account password

- **Category / priority:** Reset completion and data / `must`
- **Approved requirements:** REQ-011, REQ-014
- **Related risk IDs:** None
- **Evidence:** S1, S3
- **Cause:** Completion could neglect the linked account state, or fixtures could accidentally rely on real identities instead of synthetic accounts.
- **Impact:** A valid unused unexpired link would not produce the intended password change, or the synthetic-only boundary could be lost.
- **Proposed mitigation/check:** Exercise a complete reset against a synthetic fixture and inspect the account password state before and after; inspect account data for synthetic-only identities. No new-password policy or restart-persistence guarantee is inferred.

### R22A08-007 — A successful reset leaves an active session signed in

- **Category / priority:** Session invalidation / `must`
- **Approved requirements:** REQ-012
- **Related risk IDs:** None
- **Evidence:** S3
- **Cause:** Reset completion could invalidate only the current session or omit other application-represented active sessions for the account.
- **Impact:** A pre-reset signed-in session could remain usable despite a successful reset.
- **Proposed mitigation/check:** Establish multiple represented active sessions for one synthetic account, complete its reset, and confirm none remains signed in. The session mechanism and definition of active beyond application representation remain open.

### R22A08-008 — Owner notification is missed or leaves the in-memory sink

- **Category / priority:** Notifications / `must`
- **Approved requirements:** REQ-013, REQ-015
- **Related risk IDs:** None
- **Evidence:** S3, S1
- **Cause:** The success path could omit a notification, address the wrong owner, or use an external delivery path instead of the in-memory sink.
- **Impact:** A successful reset would not produce the specified observable owner notice or would exceed the small-app delivery boundary.
- **Proposed mitigation/check:** For every successful reset in the test scenarios, inspect the in-memory sink for an owner-addressed notification recorded after completion and verify notifications are captured there rather than externally delivered. No external link transport is assumed.

### R22A08-009 — Runtime or pytest coverage diverges from the requested delivery

- **Category / priority:** Runtime and verification / `should`
- **Approved requirements:** REQ-016, REQ-018
- **Related risk IDs:** None
- **Evidence:** S1
- **Cause:** Implementation could target a different Python runtime or framework, or automated tests could omit sign-in or recovery behaviors.
- **Impact:** The delivered project might not be verifiable against its specified technical and behavioral constraints.
- **Proposed mitigation/check:** Inspect the configured Python 3.12 runtime and Flask usage; run pytest and inspect test cases for the sign-in presentation and recovery request, limit, link, completion, sessions, and notifications. No implementation or test results are available at this risk-assessment stage.

### R22A08-010 — Production limitations or no-deployment boundary are missed

- **Category / priority:** Documentation and scope / `should`
- **Approved requirements:** REQ-019, REQ-020, REQ-021
- **Related risk IDs:** None
- **Evidence:** S1
- **Cause:** Documentation could omit the small application's production limitations, or delivery work could deploy it or add a deployment workflow despite the explicit boundary.
- **Impact:** Readers might mistake the demo for a production-ready service, or delivery could exceed approved scope.
- **Proposed mitigation/check:** Review project documentation for production limitations and review delivery actions and changed workflow files to verify there was no deployment and no new deployment workflow. This does not propose deployment.

## Assumptions

1. This is a prospective delivery risk register, not a report of observed defects, shipped mitigations, tested outcomes, or a production environment.
2. The approved `requirements_analysis` output supplies the only linked identifiers, REQ-001 through REQ-021; no `stage_output` locator was supplied, so no `stage_output` reference is invented.
3. The `must` and `should` priority values express qualitative attention to delivery risks, not requirement priority, measured likelihood, or an approved severity scale.
4. Known-account requests are checked against the five-per-account-per-hour limit without assuming a limit for unknown accounts; the reset-request response must not disclose account existence, including when considering throttling.
5. Active sessions means sessions represented by the application for an account; the session mechanism remains unspecified.
6. The sign-in button is a visible control without an inferred authentication outcome. New-password policy, reset-link transport, persistence across restart, and recovery-page visual layout remain unspecified.
7. Notifications are observed in the in-memory sink, not presumed to be externally delivered; accounts used for this small application are synthetic.

## Open questions (non-blocking)

1. **How should requests for nonexistent accounts count toward an hourly per-account limit?** Relevant to R22A08-003 and R22A08-004; do not invent an unknown-account threshold, and keep responses independent of account existence.
2. **What response should a throttled request produce, and how will it avoid distinguishing existing from nonexistent accounts?** Relevant to R22A08-003 and R22A08-004; the exact throttled response is not specified.
3. **How will the application represent all active sessions of one account?** Relevant to R22A08-007; check invalidation of every represented session without prescribing the mechanism.
4. **Is the visible Sign in button intended to authenticate, and what outcome, if any, should it have?** Relevant to R22A08-001; only the displayed control is specified.
5. **What new-password policy, if any, should be applied?** Relevant to R22A08-006; no length or complexity rule is inferred.
6. **How should reset links be conveyed to owners?** Relevant to R22A08-005 and R22A08-008; the in-memory sink is observable, but external delivery is not prescribed.
7. **Should synthetic account, link, session, or notification state survive an application restart?** Relevant to R22A08-006 through R22A08-008; restart persistence is not required by the available evidence.
8. **What should the recovery-request and new-password pages look like?** Relevant to R22A08-002; the supplied wireframe shows only the sign-in page.
