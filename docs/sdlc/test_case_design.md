# Proposed test case design

**Stage:** `test_case_design` · **Schema:** `1.0` · **Status:** design only. These are future checks, not executed or passing tests.

The approved `requirements_analysis` defines 21 acceptance criteria (REQ-001–REQ-021, one each); `solution_design` defines 18 task acceptance criteria (TASK-001–TASK-009, two each). The approved `ui_analysis` distinguishes observed S1 from proposed S2–S6. All case IDs and trace links below are approved predecessor identifiers, not claims that an application exists.

## Authorized evidence

| Type | Source ID | Exact locator | Evidences |
| --- | --- | --- | --- |
| user_story | `user_story` | `characters 0-16000` | Python 3.12/Flask, server rendering, synthetic accounts, private in-memory notifications, pytest, production limits, no deployment/workflows |
| attachment | `fd6b3020-ac35-442c-bd77-c53062c11e9c` | `sign-in-wireframe.png` | Only observed S1 presentation on a white 480×360 canvas |
| knowledge | `bcf198d8-a628-401c-8641-b726fcbd00b5` | `v1, chunk 0` | Generic known/unknown request responses, five/account/hour, single-use 30-minute links, session sign-out and owner notice |

The stage-output service supplied predecessor stage keys without source-reference locators; no stage-output citation is invented. The image shows placeholders but proves neither password masking on entry nor authentication/navigation. S2–S6 and the generic capped acknowledgement, one-process lock, fixture sessions, secret-free intent and nonempty-password rule are **approved proposed design**, not observed UI or additional recovery-standard rules. An in-memory sink entry is not external delivery.

## Acceptance-criterion coverage

**Requirements: 21/21; implementation-task criteria: 18/18; unmapped: 0; approved exclusions/dispositions: 0.** Each row traces to at least one proposed case and does not assert a pass.

| Criterion | Acceptance check | Proposed cases |
| --- | --- | --- |
| REQ-001 R1 | Centered outlined white S1 card and heading | TC-003 |
| REQ-002 R1 | Labeled email input and exact placeholder | TC-003, TC-004 |
| REQ-003 R1 | Password label, placeholder **and entered-character masking** | TC-003, TC-004 |
| REQ-004 R1 | Visible dark rectangular Sign in button | TC-003, TC-004 |
| REQ-005 R1 | Exact administrator-contact footer | TC-003 |
| REQ-006 R1 | Blue underlined recovery link starts reset request | TC-005, TC-006 |
| REQ-007 R1 | Equivalent existing/nonexistent reset responses identical | TC-007, TC-011 |
| REQ-008 R1 | At most five accepted requests for known account/hour | TC-008, TC-009 |
| REQ-009 R1 | Used link cannot complete again | TC-016, TC-020 |
| REQ-010 R1 | Expiry at **exactly** 30 minutes from issuance or later | TC-014 |
| REQ-011 R1 | Valid reset changes synthetic account password | TC-015 |
| REQ-012 R1 | Successful reset signs out **every** represented owner session | TC-015, TC-018 |
| REQ-013 R1 | Successful reset records owner-addressed notification after reset | TC-015, TC-022 |
| REQ-014 R1 | Only synthetic account identities | TC-001, TC-022 |
| REQ-015 R1 | Notifications captured in memory, not externally delivered | TC-022 |
| REQ-016 R1 | Python 3.12 with Flask | TC-001, TC-002 |
| REQ-017 R1 | Application pages rendered on server | TC-003, TC-005, TC-006, TC-012, TC-021 |
| REQ-018 R1 | Executable pytest coverage of specified flows | TC-023 |
| REQ-019 R1 | Project docs identify production limitations | TC-024 |
| REQ-020 R1 | No deployment performed | TC-025 |
| REQ-021 R1 | No deployment workflow added | TC-026 |
| TASK-001 A1 | Python 3.12 app smoke, synthetic-only isolated state/private sink, no external contacts | TC-001, TC-022 |
| TASK-001 A2 | Python/Flask config; no persistent database/deployment workflow | TC-002, TC-026 |
| TASK-002 A1 | Flask GET S1 matches all named visual/field/footer features | TC-003, TC-004 |
| TASK-002 A2 | Blue underlined link reaches server-rendered S2; no invented sign-in auth | TC-005 |
| TASK-003 A1 | Six in rolling hour yield ≤5 links; oldest leaves window then issuance resumes | TC-008, TC-009 |
| TASK-003 A2 | Unknown/capped issue nothing and no account-specific outcome; issuance/sink failure consumes no slot | TC-007, TC-010 |
| TASK-004 A1 | S1→S2, compare complete public known/unknown/capped responses, inspect private links | TC-005, TC-007 |
| TASK-004 A2 | S2/S3 server-rendered, named controls/return, generic feedback, no public secret | TC-006, TC-011 |
| TASK-005 A1 | Unused just-before-30 allowed; exactly-at/after-30, used and unknown rejected | TC-013, TC-014 |
| TASK-005 A2 | Eligible GET S4 without consumption, secret-free redirect/intent/HTML/logs | TC-012 |
| TASK-006 A1 | Two A sessions revoked, B session remains active | TC-018, TC-015 |
| TASK-006 A2 | Fixture-created sessions, no public test-route or assumed sign-in behavior | TC-018 |
| TASK-007 A1 | Valid reset: hash, token, all sessions, exactly one owner notice; replay/expiry no effects | TC-015, TC-014, TC-016 |
| TASK-007 A2 | Competing completions exactly one success; sink-failure complete rollback/no S5 | TC-019, TC-020 |
| TASK-008 A1 | Future Python 3.12 pytest runs scenarios incl. response parity/multiple sessions | TC-023 |
| TASK-008 A2 | Success and unavailable branches, secret-free public markup and no external delivery | TC-013, TC-019, TC-022, TC-023 |
| TASK-009 A1 | Local run/test docs and production/in-memory-delivery warnings | TC-024 |
| TASK-009 A2 | Recorded action review: no deployment; changed-file review: no new workflow | TC-025, TC-026 |

## Proposed cases

Each first step explicitly specifies preconditions and test data. Subsequent numbered steps are actions; each expected-result bullet is an observable proposed assertion. Private inspections use service/fixture state, never a public token endpoint.

### TC-001 — Synthetic isolated Flask foundation

**Requirements:** REQ-014, REQ-015, REQ-016 · **Tasks:** TASK-001, TASK-008

**Steps**

1. Preconditions/data: Python 3.12 environment; two independently created app fixtures, synthetic A and B with labeled .test identities; outbound account and notification access is blocked.
2. Construct both Flask applications using injected UTC clock, hasher, token factory, store and private sink; inspect seeded accounts and stored password records.
3. Mutate account and notification state in the first fixture; inspect the second fixture and enumerate publicly reachable inspection routes.

**Expected results**

- Both applications construct under Python 3.12/Flask with synthetic-only .test accounts and adaptive password hashes, never seeded plaintext passwords or real identities.
- Account state and notification sink are in memory, isolated between app fixtures, and cannot be inspected by a public sink or test endpoint; no external account or notification service is contacted.

**Evidence:** `user_story` / `user_story` / `characters 0-16000`

### TC-002 — Python and local dependency configuration

**Requirements:** REQ-014, REQ-015, REQ-016 · **Tasks:** TASK-001

**Steps**

1. Preconditions/data: future delivered project and its runtime/dependency files; Python 3.12 is available.
2. Inspect runtime and resolved Flask dependency, application factory and storage/notification wiring; smoke-create the app with Python 3.12.
3. Inspect foundation configuration for persistent database, external notification transport or newly added deployment setup.

**Expected results**

- Runtime configuration specifies Python 3.12 and Flask and the factory instantiates under Python 3.12.
- Foundation uses synthetic in-memory accounts and private in-memory notifications, without a persistent database, external delivery dependency or added deployment configuration.

**Evidence:** `user_story` / `user_story` / `characters 0-16000`

### TC-003 — Observed sign-in composition and server rendering

**Requirements:** REQ-001, REQ-002, REQ-003, REQ-004, REQ-005, REQ-017 · **Tasks:** TASK-002, TASK-008

**Steps**

1. Preconditions/data: future Flask app, 480×360 reference viewport and supplied S1 wireframe.
2. GET /sign-in without JavaScript and inspect the response HTML, rendered layout and controls against the image.
3. Inspect labels, placeholders, button and footer text without submitting Sign in.

**Expected results**

- The server returns complete HTML rather than an empty client-only shell; at the reference size it shows a white canvas and approximately centered thin dark outlined card headed Sign in.
- The card has Email address with placeholder name@example.com, Password with placeholder ********, a visible dark rectangular Sign in button and exact footer No account? Contact your administrator.
- No authentication outcome is inferred from the visible button.

**Evidence:** `user_story` / `user_story` / `characters 0-16000`; `attachment` / `fd6b3020-ac35-442c-bd77-c53062c11e9c` / `sign-in-wireframe.png`

### TC-004 — Sign-in masking and accessible controls

**Requirements:** REQ-002, REQ-003, REQ-004, REQ-006 · **Tasks:** TASK-002, TASK-008

**Steps**

1. Preconditions/data: rendered S1 in a browser/DOM accessibility harness; test string visible-test-secret and blank required fields.
2. Type the string into Password; inspect its type, displayed characters, accessible labels, initial placeholders and returned HTML.
3. Tab through email, password, Forgot password? and Sign in; activate controls by keyboard and submit blank required inputs.

**Expected results**

- Password is type=password, typed characters are visually masked and are not echoed into returned markup; Email address and Password retain programmatic labels independent of placeholders.
- Tab order is logical, controls have persistent accessible names, visible focus and readable contrast, and link/button are keyboard-operable.
- Blank-field validation identifies and announces associated required fields without implying successful authentication.

**Evidence:** `attachment` / `fd6b3020-ac35-442c-bd77-c53062c11e9c` / `sign-in-wireframe.png`; `user_story` / `user_story` / `characters 0-16000`

### TC-005 — Forgot-password recovery entry

**Requirements:** REQ-006, REQ-017 · **Tasks:** TASK-002, TASK-004, TASK-008

**Steps**

1. Preconditions/data: anonymous S1 browser session; no authenticated account or reset secret.
2. Locate the blue underlined Forgot password? link and activate it once by pointer and once by keyboard in separate sessions.
3. Inspect the response page and its identifier field and request control.

**Expected results**

- Both activations navigate to a server-rendered S2 reset-request entry page without a sign-in gate or bearer secret.
- The link has the accessible name Forgot password?; S2 exposes a labeled identifier field and operative request control, without implying Sign in authentication.

**Evidence:** `attachment` / `fd6b3020-ac35-442c-bd77-c53062c11e9c` / `sign-in-wireframe.png`; `knowledge` / `bcf198d8-a628-401c-8641-b726fcbd00b5` / `v1, chunk 0`; `user_story` / `user_story` / `characters 0-16000`

### TC-006 — Accessible request and acknowledgement pages

**Requirements:** REQ-006, REQ-007, REQ-017 · **Tasks:** TASK-004, TASK-008

**Steps**

1. Preconditions/data: isolated S2 Flask client with valid CSRF and a synthetic known identifier; browser accessibility harness.
2. GET S2 and submit a valid request, follow its redirect to S3, and inspect both responses without client-side rendering.
3. Traverse controls by keyboard and inspect names, focus destinations, errors/status semantics and public text.

**Expected results**

- S2 and S3 return complete server-generated HTML; S2 has a programmatically labeled identifier, named submit and S1 return, with visible focus and keyboard operation.
- S3 has an accessible heading or focus destination, announced generic acknowledgement and S1 return; its response discloses no identifier, account-found status or raw reset token.

**Evidence:** `knowledge` / `bcf198d8-a628-401c-8641-b726fcbd00b5` / `v1, chunk 0`; `user_story` / `user_story` / `characters 0-16000`

### TC-007 — Known unknown and capped public response parity

**Requirements:** REQ-007, REQ-008, REQ-015, REQ-017 · **Tasks:** TASK-003, TASK-004, TASK-008

**Steps**

1. Preconditions/data: equivalent isolated Flask-client contexts with equal clock, headers, cookie/CSRF validity and syntactically valid known A, nonexistent X and known A after five accepted links; use private sink inspection.
2. POST the otherwise equivalent identifiers to /reset/request; capture immediate status, Location, other public headers, cookies and body, then follow each redirect to S3.
3. Compare all public response fields and S3 HTML; separately count links in the private sink before and after each submission.

**Expected results**

- Known, unknown and capped valid submissions have identical public status, redirect, headers, cookies, body and generic S3 acknowledgement; any randomized CSRF/session values are matched by public semantics, not used to conceal account-dependent differences.
- An eligible known request appends exactly one private link; unknown and capped requests append none and expose no account, throttle or bearer-secret detail. No unknown-account quota is assumed.

**Evidence:** `knowledge` / `bcf198d8-a628-401c-8641-b726fcbd00b5` / `v1, chunk 0`; `user_story` / `user_story` / `characters 0-16000`

### TC-008 — Fifth sixth and rolling-hour boundary

**Requirements:** REQ-008, REQ-015 · **Tasks:** TASK-003, TASK-008

**Steps**

1. Preconditions/data: fresh known synthetic A, injected UTC clock T and empty private sink.
2. Issue five accepted A requests at T or later within the trailing hour; attempt a sixth just before T+1h and inspect accepted timestamps and links.
3. At T+1h minus the smallest supported time increment attempt another request; at T+1h, after the oldest T timestamp leaves the window, attempt once more.

**Expected results**

- At most five accepted, link-producing A requests occur in every trailing hour; the sixth and pre-boundary request issue no new link or accepted timestamp.
- At the boundary where the oldest accepted timestamp no longer belongs to the trailing hour, one new link and timestamp may be recorded; public feedback remains generic.

**Evidence:** `knowledge` / `bcf198d8-a628-401c-8641-b726fcbd00b5` / `v1, chunk 0`; `user_story` / `user_story` / `characters 0-16000`

### TC-009 — Account-scoped serialized issuance

**Requirements:** REQ-007, REQ-008 · **Tasks:** TASK-003, TASK-008

**Steps**

1. Preconditions/data: isolated clock-controlled fixture with synthetic A and B, normalized spelling variants of A and a nonexistent identifier.
2. Concurrently submit more than five A requests in one hour, interleaved with B and nonexistent-identifier requests; inspect private tokens, accepted timestamps and responses.
3. Submit another B request if capacity remains.

**Expected results**

- All normalized A variants share one cap of five accepted links, with no duplicate admission under concurrency; B's account-specific capacity remains independent.
- Unknown identifiers produce no token, and responses disclose neither existence nor capped status.

**Evidence:** `knowledge` / `bcf198d8-a628-401c-8641-b726fcbd00b5` / `v1, chunk 0`

### TC-010 — Issuance and sink failure rollback

**Requirements:** REQ-008, REQ-015 · **Tasks:** TASK-003, TASK-008

**Steps**

1. Preconditions/data: known A with four accepted requests in the hour; snapshot timestamps, token store and private sink.
2. On separate requests inject a token-factory exception and then a sink-append exception; inspect service state and public error output after each.
3. Restore dependencies and submit another valid request.

**Expected results**

- Neither failed attempt retains a link/token, sink entry or accepted slot; failure output reveals no account identifier or bearer secret and does not claim completion.
- The restored request occupies the fifth slot and adds exactly one usable private link.

**Evidence:** `knowledge` / `bcf198d8-a628-401c-8641-b726fcbd00b5` / `v1, chunk 0`; `user_story` / `user_story` / `characters 0-16000`

### TC-011 — Malformed and CSRF-forged request rejection

**Requirements:** REQ-007, REQ-017 · **Tasks:** TASK-004, TASK-008

**Steps**

1. Preconditions/data: S2 form, blank and syntactically malformed identifiers, known and unknown variants of each, and missing or invalid CSRF tokens.
2. Submit each invalid form; inspect returned server HTML, field associations and private store/sink.
3. Compare responses for equivalent known/unknown bad inputs and inspect output for account-status or token details.

**Expected results**

- Invalid input has generic account-independent treatment and associated visible, announced errors; CSRF failures reject unauthorized mutation.
- No accepted request, link or sink entry results; public errors reveal no account-existence or bearer-secret detail. Exact identifier grammar and wording are not presumed.

**Evidence:** `knowledge` / `bcf198d8-a628-401c-8641-b726fcbd00b5` / `v1, chunk 0`; `user_story` / `user_story` / `characters 0-16000`

### TC-012 — Eligible link GET remains unused and private

**Requirements:** REQ-009, REQ-010, REQ-015, REQ-017 · **Tasks:** TASK-005, TASK-008

**Steps**

1. Preconditions/data: unexpired unused link issued privately to synthetic A and a log capture; no public sink access.
2. GET the initial link twice before expiry and follow each secret-free redirect to S4; inspect link state, HTML, Location, referrer/cache headers and application logs.
3. Inspect S4 labeled password-type input, CSRF token and keyboard-operable submit; enumerate public link-discovery routes.

**Expected results**

- Both eligible GETs reach server-rendered S4 using server-held opaque reset intent without consuming the link; mutation still requires an authorized POST.
- After the initial bearer URL, redirects, rendered HTML, referrer/caching behavior and application logs do not disclose the raw secret; no public sink/link-discovery endpoint exists.
- S4 has a programmatically labeled, masked new-password field and keyboard-operable CSRF-protected submit; initial URL/browser-history exposure is a documented limitation.

**Evidence:** `knowledge` / `bcf198d8-a628-401c-8641-b726fcbd00b5` / `v1, chunk 0`; `user_story` / `user_story` / `characters 0-16000`

### TC-013 — Unknown malformed and used links reject

**Requirements:** REQ-009, REQ-011, REQ-017 · **Tasks:** TASK-005, TASK-007, TASK-008

**Steps**

1. Preconditions/data: unknown and malformed bearer values, an already consumed link, no eligible intent; snapshot synthetic account hashes, sessions and owner-notice sink.
2. GET each link, and separately attempt direct completion without a valid held intent.
3. Inspect resulting HTML, response/log secrets and private state.

**Expected results**

- Each rejected entry leads to server-rendered non-success S6 or denial with named S2 retry and S1 return controls; rejected links show no usable password form and no reason-specific public copy is required.
- No password/hash, session, token-success or owner-success-notice state changes, and neither response nor application log exposes a bearer secret.

**Evidence:** `knowledge` / `bcf198d8-a628-401c-8641-b726fcbd00b5` / `v1, chunk 0`; `user_story` / `user_story` / `characters 0-16000`

### TC-014 — Issuance-based thirty-minute expiry edges

**Requirements:** REQ-009, REQ-010, REQ-011, REQ-012, REQ-013 · **Tasks:** TASK-005, TASK-007, TASK-008

**Steps**

1. Preconditions/data: separate unused synthetic A links issued at injected UTC T, represented active sessions and snapshot hashes/notices; valid CSRF and nonempty new password.
2. For one link, GET and complete at T+29m59.999s (or latest supported instant strictly before 30 minutes); for another, open S4 before expiry but POST at exactly T+30m.
3. For fresh links, GET and POST at T+30m and later; inspect hash, link state, sessions and owner-success notices after rejected attempts.

**Expected results**

- An eligible completion strictly before the issuance-based deadline can change the password once; opening S4 earlier does not extend eligibility.
- At exactly T+30m or later, both GET entry and POST completion reject without S5, password replacement, token consumption, session revocation or owner-success notice.

**Evidence:** `knowledge` / `bcf198d8-a628-401c-8641-b726fcbd00b5` / `v1, chunk 0`; `user_story` / `user_story` / `characters 0-16000`

### TC-015 — Atomic successful reset and owner effects

**Requirements:** REQ-009, REQ-011, REQ-012, REQ-013, REQ-014, REQ-015, REQ-017 · **Tasks:** TASK-006, TASK-007, TASK-008

**Steps**

1. Preconditions/data: synthetic A with adaptive old-password hash, two represented active A sessions, synthetic B with one active session, unused unexpired A link in private sink; CSRF-valid S4 and a nonempty new password.
2. POST completion once and inspect server response, stored hash, token, all sessions and sink entry order.
3. Check old and new passwords using the hasher and inspect public HTML for plaintext password or raw link.

**Expected results**

- Only a committed reset renders server-side S5; A's new adaptive hash verifies the new password but not the old one, and its link is consumed.
- Both A sessions are inactive while B's remains active; exactly one owner-addressed in-memory success notice is appended after the reset, without an external-delivery claim.
- The public response contains neither plaintext new password nor raw bearer link; no public login feature is required.

**Evidence:** `knowledge` / `bcf198d8-a628-401c-8641-b726fcbd00b5` / `v1, chunk 0`; `user_story` / `user_story` / `characters 0-16000`

### TC-016 — Consumed link cannot reset again

**Requirements:** REQ-009, REQ-011, REQ-012, REQ-013 · **Tasks:** TASK-005, TASK-007, TASK-008

**Steps**

1. Preconditions/data: A's link was consumed by one successful reset to first-new-password; snapshot hash, revoked sessions and success-notice count.
2. Try completion again with a distinct nonempty second password, including a fresh direct-link GET and authorized POST attempt where possible.
3. Inspect response and account, token, session and sink state.

**Expected results**

- Replay cannot render S5 or complete another reset; the first new password continues to verify and the second does not.
- Consumed state stays consumed, with no additional session mutation or owner-success notice.

**Evidence:** `knowledge` / `bcf198d8-a628-401c-8641-b726fcbd00b5` / `v1, chunk 0`

### TC-017 — Reset intent and CSRF authorization boundary

**Requirements:** REQ-009, REQ-011, REQ-012, REQ-017 · **Tasks:** TASK-005, TASK-007, TASK-008

**Steps**

1. Preconditions/data: A and B with distinct valid links and sessions; snapshot hashes, tokens, sessions and owner-notice sink; two separate Flask clients.
2. Attempt S4 POST with missing/forged intent, another client's intent, guessed or other-account link and missing/altered CSRF.
3. Inspect mutation state and all returned HTML, headers and cookies for owner or bearer data.

**Expected results**

- Each unauthorized attempt is denied without S5, changing either account's password/hash, token, active sessions or owner-success-notice entries.
- Public errors and headers/cookies expose no bearer link, submitted new password or account-owner detail; no login mechanism is inferred.

**Evidence:** `knowledge` / `bcf198d8-a628-401c-8641-b726fcbd00b5` / `v1, chunk 0`; `user_story` / `user_story` / `characters 0-16000`

### TC-018 — Fixture-created revocable session registry

**Requirements:** REQ-012 · **Tasks:** TASK-006, TASK-008

**Steps**

1. Preconditions/data: isolated synthetic A/B store; use fixtures to create active opaque server-side sessions A1, A2 and B1.
2. Check all three as active; revoke sessions by A's account ID and check each again.
3. Inspect routes to ensure no public session-creation test endpoint or newly assumed Sign in authentication behavior.

**Expected results**

- A1 and A2 become inactive, while B1 remains active; revocation covers every represented active session for A without affecting B.
- Sessions can be created in fixtures without a public test route or invented authentication outcome.

**Evidence:** `knowledge` / `bcf198d8-a628-401c-8641-b726fcbd00b5` / `v1, chunk 0`; `user_story` / `user_story` / `characters 0-16000`

### TC-019 — Completion notice failure rolls back all effects

**Requirements:** REQ-009, REQ-011, REQ-012, REQ-013, REQ-015 · **Tasks:** TASK-007, TASK-008

**Steps**

1. Preconditions/data: A's valid unexpired link, old password, two active A sessions, private sink; inject an exception on owner-success-notice append and hold clock before expiry.
2. POST CSRF-valid S4 with nonempty new password; inspect page, hash, token eligibility, both sessions and notice count.
3. Restore sink and retry while link remains within its issuance-based validity window.

**Expected results**

- Failure does not render S5 and leaves the old password valid, link eligible, both A sessions active and no new owner-success notice; no partial commit remains.
- Exactly one subsequent successful completion commits hash, token, sessions and owner-addressed notice together.

**Evidence:** `knowledge` / `bcf198d8-a628-401c-8641-b726fcbd00b5` / `v1, chunk 0`; `user_story` / `user_story` / `characters 0-16000`

### TC-020 — Competing completions have one winner

**Requirements:** REQ-009, REQ-011, REQ-012, REQ-013, REQ-015 · **Tasks:** TASK-007, TASK-008

**Steps**

1. Preconditions/data: one eligible A link, two CSRF-valid isolated completion contexts, distinct nonempty passwords and multiple active A sessions; synchronize concurrent POST starts.
2. Submit both S4 completions simultaneously, then inspect both responses, hash, link, sessions and private notices.
3. Verify each candidate password against the final hash.

**Expected results**

- Exactly one submission reports S5 and its password alone verifies; the losing submission reports non-success and cannot overwrite the winner.
- The link is consumed once, all represented A sessions are revoked, exactly one owner-success notice is present and no partial loser effects remain.

**Evidence:** `knowledge` / `bcf198d8-a628-401c-8641-b726fcbd00b5` / `v1, chunk 0`; `user_story` / `user_story` / `characters 0-16000`

### TC-021 — Recovery form errors and accessible end states

**Requirements:** REQ-009, REQ-010, REQ-011, REQ-017 · **Tasks:** TASK-005, TASK-007, TASK-008

**Steps**

1. Preconditions/data: valid unused S4 intent and valid/invalid CSRF, empty and nonempty new passwords, separately expired and used links; capture pre-submit account/session/token/notice state.
2. Submit empty password and invalid CSRF separately; inspect associated errors, focus and private state.
3. Submit a valid nonempty password in a fresh eligible fixture and inspect S5; GET expired/used links and inspect S6 by keyboard and accessibility tree.

**Expected results**

- Invalid submissions announce an associated error and do not show S5 or mutate hash, link, sessions or owner notices; no complexity rule beyond the proposed nonempty requirement is presumed.
- S4 has a named password-type control, visible focus and keyboard submission; successful S5 is server-rendered with S1 return, and rejected S6 is server-rendered with S2 retry/S1 return, accessible headings/status and no exposed secret or active reset form.

**Evidence:** `knowledge` / `bcf198d8-a628-401c-8641-b726fcbd00b5` / `v1, chunk 0`; `user_story` / `user_story` / `characters 0-16000`

### TC-022 — Private in-memory notices without external transport

**Requirements:** REQ-013, REQ-014, REQ-015 · **Tasks:** TASK-001, TASK-003, TASK-007, TASK-008

**Steps**

1. Preconditions/data: separate synthetic A and B app fixtures, outbound network/mail stubs that fail if called and initially empty private sinks.
2. Request A's link, inspect it privately, then complete A's valid reset; inspect event order, destination and the second fixture.
3. Probe public routes for sink or bearer-link disclosure and inspect outbound call counters.

**Expected results**

- Only A's private sink holds its issued link followed by exactly one A-owner-addressed success notice after committed reset; the second fixture stays isolated.
- Outbound notification calls remain zero, and no public route reveals sink contents or a raw link; sink recording is not real owner delivery.

**Evidence:** `user_story` / `user_story` / `characters 0-16000`; `knowledge` / `bcf198d8-a628-401c-8641-b726fcbd00b5` / `v1, chunk 0`

### TC-023 — Future Python 3.12 pytest behavioral gate

**Requirements:** REQ-018, REQ-016 · **Tasks:** TASK-008

**Steps**

1. Preconditions/data: future delivered code, Python 3.12 with project dependencies and pytest tests; no live accounts or external notification service.
2. Run python3.12 -m pytest at the future coding checkpoint and inspect discovered test names and assertions.
3. Map discovered tests to S1-S6/server rendering, parity and cap, invalid/replayed/expiry edges, password and multi-session/notice effects, failures/concurrency, secret-free responses and no outbound delivery.

**Expected results**

- At that future checkpoint the pytest command completes successfully and executable tests explicitly cover the listed positive, unavailable, boundary, accessibility and authorization cases under Python 3.12.
- Coverage is established from test assertions and future execution, not from this proposed case list or a static wireframe; no current execution or passing status is asserted.

**Evidence:** `user_story` / `user_story` / `characters 0-16000`; `attachment` / `fd6b3020-ac35-442c-bd77-c53062c11e9c` / `sign-in-wireframe.png`; `knowledge` / `bcf198d8-a628-401c-8641-b726fcbd00b5` / `v1, chunk 0`

### TC-024 — Document local demo production limitations

**Requirements:** REQ-019 · **Tasks:** TASK-009

**Steps**

1. Preconditions/data: future delivered README and project documentation.
2. Read local synthetic-demo setup and pytest instructions and the production-limitations section.
3. Check for explicit description of restart loss, single-process locking, lack of shared/durable limits and sessions, private sink rather than owner delivery, residual initial-link/HTTP/cookie risks and production-hardening prerequisites.

**Expected results**

- Documentation gives usable local run/test instructions and an explicit not-production-ready warning.
- The listed persistence, scaling, delivery and security limitations are stated as limitations, not hidden behind an unsupported production claim; no delivery infrastructure is added by this review.

**Evidence:** `user_story` / `user_story` / `characters 0-16000`

### TC-025 — Review action record for no deployment

**Requirements:** REQ-020 · **Tasks:** TASK-009

**Steps**

1. Preconditions/data: future complete auditable delivery/action record and change summary; no deployment performed by this check.
2. Review recorded operations for deploy, publish, hosting or external-environment actions and document the review result.
3. If the record is absent or incomplete, mark the non-deployment criterion unverified rather than passing it.

**Expected results**

- When the complete action record is available, it contains no deployment or publication action and the reviewer records a no-deployment finding.
- Missing action evidence is explicitly reported as an evidence gap, never construed as proof that deployment did not occur.

**Evidence:** `user_story` / `user_story` / `characters 0-16000`

### TC-026 — Diff review excludes new deployment workflows

**Requirements:** REQ-021, REQ-020 · **Tasks:** TASK-001, TASK-009

**Steps**

1. Preconditions/data: future delivered repository and pre-work baseline with full changed-file list.
2. Compare changes, especially .github/workflows/, hosting/config files, scripts and CI commands, against the baseline and record the result.
3. Distinguish pre-existing workflows from additions; cross-check the action record for deployment actions.

**Expected results**

- No new deployment workflow, hosting deployment configuration or deployment script is added by the delivered work; pre-existing baseline workflows are not falsely classified as new.
- Review records both the change-set result and the separate no-deployment action finding, or reports missing evidence instead of claiming a pass.

**Evidence:** `user_story` / `user_story` / `characters 0-16000`

## Assumptions and remaining questions

Assumptions (not new acceptance criteria):

- These are proposed checks against future implementation, not executed tests or passing results. Only S1 is pictured; S2-S6, routes and their behavior follow the approved proposed design, not observations of the wireframe.
- The pictured password asterisks are a placeholder, not proof of entered-character masking. The Sign in button has no specified authentication outcome; fixture-created sessions, not a login endpoint, support session-invalidation checks.
- The approved design counts accepted link-issuing requests for known accounts in a trailing hour, returns the same generic public acknowledgement for known, unknown and capped valid submissions, and does not prescribe an unknown-account quota.
- The proposed implementation uses one-process locking, restart-volatile isolated in-memory stores, CSRF protection, digest-stored random links, a secret-free server-held intent, adaptive hashes and a nonempty new-password rule. These are design choices, not image or recovery-standard observations.
- In-memory owner-addressed sink entries are observable records, not proof of external delivery. Do not infer restart persistence, multi-worker safety, password-complexity policy or any deployment.
- No predecessor stage-output citation locator was provided; predecessor REQ and TASK identifiers are trace links, not fabricated stage_output source references. Future non-deployment review requires an auditable action record.

Open questions (all nonblocking for this proposed design):

- Should the visible Sign in button eventually authenticate, and how should real sessions originate? — Only presentation is evidenced; proposed checks use fixture-created sessions.
- How would a synthetic owner obtain a privately captured reset link without public discovery or external delivery? — Tests inspect the private in-memory sink; delivery is not specified.
- Should unknown identifiers have non-disclosing abuse limits or should capped acknowledgement differ from the approved generic design? — Do not invent an unknown-account quota; current proposed design makes capped public responses generic.
- What exact recovery-page copy, identifier validation, password policy and focus behavior should be specified? — Test observable generic status, accessible errors and the approved nonempty rule without inventing visual or complexity requirements.
- Will any later production version require durable or distributed storage, actual owner delivery, or HTTPS and cookie deployment controls? — The proposed local-only application makes no production-readiness claim.

**Boundary:** No application, pytest run, deployment action or passing test result is asserted here. At future delivery, an incomplete action record is an evidence gap rather than proof of non-deployment.
