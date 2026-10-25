# T001 — proposed test-case coverage map

**Stage:** `test_case_design` · **Run:** `1567db21-14fd-4b10-8f21-7105051ab410` · **Status:** design only; no application, test execution, deployment, or passing result is asserted. This is a planning artifact, **not** `docs/sdlc/test_case_design.json` or `.md`. IDs below are reserved for the eventual contract. The 21 approved requirement acceptance criteria and 18 approved solution-task acceptance criteria each have at least one proposed check. Approved `coverage_dispositions: []`; there are no accepted omissions.

## Authorized evidence and interpretation

| Source type | Source ID | Exact locator | Use |
| --- | --- | --- | --- |
| `user_story` | `user_story` | `characters 0-16000` | Python 3.12/Flask, server-rendered password-reset application, synthetic accounts, private in-memory notifications, pytest, production limitations, no deployment/workflows. |
| `attachment` | `fd6b3020-ac35-442c-bd77-c53062c11e9c` | `sign-in-wireframe.png` | Observed S1 presentation only: white 480×360 canvas, approximately centered outlined card (x≈70–410, y≈20–342), heading, labels/placeholders, blue underlined recovery link, dark button, footer. |
| `knowledge` | `bcf198d8-a628-401c-8641-b726fcbd00b5` | `v1, chunk 0` | Run-specific recovery rules: identical known/unknown reset-request responses, at most five/account/hour, one-time links with 30-minute issuance-based expiry, all sessions signed out, owner notified. |

Approved predecessor identifiers come from `requirements_analysis`, `ui_analysis`, and `solution_design`; the optional `acceptance_20261025100400_f0ad0f_risk` is reference data. The stage-output service returned stage keys **without** a source-reference locator, so none is invented. The wireframe does not establish typed-password masking, activation/navigation, authentication, or recovery-screen appearance. S2–S6, their routes, injected clock, one-process lock, fixture-created sessions, secret-free redirect/intent, and transaction/rollback checks derive from approved **proposed solution design**, not from observed UI. Assertions about the pictured “Sign in” button concern presentation and accessibility, not an unspecified sign-in outcome.

### Reference shorthand for the eventual test-case contract

- **U** = `{source_type: user_story, source_id: user_story, locator: "characters 0-16000"}`.
- **I** = `{source_type: attachment, source_id: fd6b3020-ac35-442c-bd77-c53062c11e9c, locator: "sign-in-wireframe.png"}`.
- **K** = `{source_type: knowledge, source_id: bcf198d8-a628-401c-8641-b726fcbd00b5, locator: "v1, chunk 0"}`.

Use only those exact triples, as applicable to each case; do not manufacture predecessor-output references. In the pinned final schema, place the preconditions and test data explicitly in `steps[]`, followed by numbered actions; place each independently observable assertion in `expected_results[]`.

## Reserved cases and checks

Each row states setup/data, action, and observable expected outcome. “Private” means fixture/service inspection, not a public endpoint. Flask-client comparisons hold the request environment, CSRF validity, cookie state, and injected time equivalent; ignore only randomized CSRF/session values if a fresh matched session is necessary and compare their public **semantics**, rather than masking status, redirect, body, headers, or account-dependent cookies.

| ID | Intent and proposed precise check (setup → action → expected) | REQ links | TASK links | Evidence |
| --- | --- | --- | --- | --- |
| **TC-001** | **Foundation smoke.** Under Python 3.12, create two independent Flask app/fixture instances and inspect their account, clock, hasher, token factory, store and sink. Only labeled synthetic `.test` identities are seeded; password records use adaptive hashes rather than plaintext; state and sink are isolated, private, in-memory and initially independent. No network/account-service calls occur. | REQ-014, REQ-015, REQ-016 | TASK-001, TASK-008 | U |
| **TC-002** | **Runtime and local-only configuration.** Inspect interpreter/version declaration, resolved Flask dependency, application factory and storage wiring; run an app-creation smoke check with Python 3.12. Expect Python 3.12 + Flask, no persistent database or external notification dependency, and no deployment configuration added by foundation work. | REQ-014, REQ-015, REQ-016, REQ-021 | TASK-001 | U |
| **TC-003** | **S1 visual/markup parity.** GET `/sign-in` via Flask client and compare rendered page at the wireframe's 480×360 reference size; verify white background, approximately centered thin outlined card, “Sign in” heading, labeled Email address input with `name@example.com`, labeled Password input with `********`, dark rectangular “Sign in” button, exact `No account? Contact your administrator.` footer. Inspect HTML response (not an empty JavaScript shell); no assertion of successful authentication. | REQ-001, REQ-002, REQ-003, REQ-004, REQ-005, REQ-017 | TASK-002, TASK-008 | U, I |
| **TC-004** | **S1 masking and accessibility.** Using browser/DOM accessibility inspection, enter `visible-test-secret` into Password; verify `type=password` masks entered characters and plaintext does not appear in rendered markup; placeholders are not the only labels. Tab through email, password, recovery link and Sign in button: persistent programmatic names, logical order, visible focus, readable text/control contrast and keyboard activation are observed; empty required inputs show associated, announced errors without asserting authentication. | REQ-002, REQ-003, REQ-004, REQ-006 | TASK-002, TASK-008 | I, U, K |
| **TC-005** | **Recovery entry.** From S1, activate the blue underlined “Forgot password?” link by mouse and keyboard; GET reaches a server-rendered S2 request-entry page with a labeled identifier and operative request control, not a secret or authenticated-only gate. The link has an accessible name; no sign-in outcome is assumed. | REQ-006, REQ-017 | TASK-002, TASK-004, TASK-008 | I, K, U |
| **TC-006** | **Accessible S2/S3 pages.** GET S2, submit a syntactically valid request with CSRF and follow the redirect to S3; inspect server-produced HTML for labeled input, named submit and S1-return controls, generic acknowledgement, heading/focus destination, status announcement, keyboard use and visible focus. No identifier, account-found message or raw reset token appears in S3. | REQ-006, REQ-007, REQ-017 | TASK-004, TASK-008 | U, K |
| **TC-007** | **Known/unknown/capped response parity.** With a fresh known `.test` fixture, syntactically valid unknown identifier, and known identifier after five accepted requests, submit otherwise equivalent `/reset/request` forms in matched public contexts. Compare immediate status, `Location`, other public headers, cookies and body **and** followed S3 HTML; all show the same generic feedback (approved design choice for capped cases), no existence/throttle/secret leak. Private sink gets one new link for eligible known request, none for unknown/capped; no unknown-account quota is assumed. | REQ-007, REQ-008, REQ-015, REQ-017 | TASK-003, TASK-004, TASK-008 | K, U |
| **TC-008** | **Rolling-hour boundary.** Set injected UTC time `T`; issue five accepted known-account requests inside `[T,T+1 hour)`, then a sixth before `T+1 hour`: exactly five private links/timestamps, sixth no issuance. Immediately before the oldest timestamp leaves the trailing hour it remains capped; at `T+1 hour`, when the oldest timestamp is outside the trailing interval, one new link may issue. Count *accepted* link-producing requests, not public acknowledgements. | REQ-008, REQ-015 | TASK-003, TASK-008 | K, U |
| **TC-009** | **Account scope and serialized concurrency.** In an isolated clock-controlled fixture, interleave normalized variants of one known identifier and a second synthetic account; submit concurrent first-account requests beyond five. At most five links for the first account in the hour, independent capacity for the second; no duplicate slot admission and no new link for unknown identifiers. Public acknowledgements remain generic. | REQ-007, REQ-008 | TASK-003, TASK-008 | K |
| **TC-010** | **Issuance failure rollback.** For a known account with four accepted links, inject token-factory failure, then sink-append failure on separate requests. Neither failed attempt retains a token, link, sink entry or accepted slot; restore dependencies and the fifth request succeeds. Public failure never discloses identifier/secret; explicitly distinguish service rollback from any unspecified exact error wording. | REQ-008, REQ-015 | TASK-003, TASK-008 | K, U |
| **TC-011** | **Malformed and forged reset requests.** Submit empty/malformed identifier and missing/invalid CSRF to S2; compare account-independent error treatment for equivalent bad inputs, associated visible/announced errors and no accepted link or sink entry. Check no unauthorized state mutation through CSRF failure and no account-status detail in response; the precise identifier grammar/copy is not prescribed. | REQ-007, REQ-017 | TASK-004, TASK-008 | K, U |
| **TC-012** | **Eligible link GET, privacy and nonconsumption.** Issue a valid synthetic link via the private sink, GET its entry URL twice before expiry and follow a secret-free redirect into S4 with a server-held opaque reset intent. It remains unused until POST; rendered HTML, subsequent redirects, referrer/caching headers and application logs exclude raw bearer secret. S4 has labeled password-type input, CSRF token and keyboard-operable submit; no public sink/link-discovery endpoint exists. The initial URL/browser-history exposure remains a documented limitation. | REQ-009, REQ-010, REQ-015, REQ-017 | TASK-005, TASK-008 | K, U |
| **TC-013** | **Unknown, already-used and malformed links.** GET unknown/malformed link or GET a used link after a successful reset, and try direct completion with no eligible server-held intent. Each reaches non-success S6 or rejection, with S2 retry/S1 return controls and no password form for a rejected link; no password/hash, session or sink-success-notice change. No raw secret in response/log. Do not require reason-specific public copy. | REQ-009, REQ-011, REQ-017 | TASK-005, TASK-007, TASK-008 | K, U |
| **TC-014** | **Issuance-clock expiry edges.** With separate links issued at `T`, verify display and completion at `T+29m59.999s` can succeed, while POST at exactly `T+30m` and later cannot, even if S4 was opened before the deadline; GET at/after deadline reaches S6. Check issuance timestamp, not GET time or request completion time, and assert no password, token-consumption, session or owner-success-notice changes on expired attempts. | REQ-009, REQ-010, REQ-011, REQ-012, REQ-013 | TASK-005, TASK-007, TASK-008 | K, U |
| **TC-015** | **Atomic happy path.** Fixture: synthetic A with old adaptive password hash, two represented active sessions, synthetic B with one active session; issue A's unused unexpired link. CSRF-protected S4 POST with a nonempty new password; expect S5 and a changed adaptive hash verifying the new password (old password no longer verifies), link consumed, both A sessions inactive, B still active and **exactly one** owner-addressed success notice appended to the private sink after success. No plaintext new password or raw link in public response. No public login feature is required. | REQ-009, REQ-011, REQ-012, REQ-013, REQ-014, REQ-015, REQ-017 | TASK-006, TASK-007, TASK-008 | K, U |
| **TC-016** | **Replay has no second effect.** After TC-015's successful consumption, POST the same link/intent with a different password, including a refreshed direct-link attempt. Reject without S5: first new password still verifies, no additional revocation or success notice, and consumed state remains consumed. | REQ-009, REQ-011, REQ-012, REQ-013 | TASK-005, TASK-007, TASK-008 | K, U |
| **TC-017** | **Reset authorization boundary.** Forge or omit reset intent, reuse another session's intent, and omit/alter POST CSRF while supplying a guessed/other-account link. Each mutation is denied; neither account's hash/sessions/token nor owner-success-notice sink state changes, and errors disclose no owner, new password or link. Inspect public headers/cookies for no bearer token; this does not imply a user-login system. | REQ-009, REQ-011, REQ-012, REQ-017 | TASK-005, TASK-007, TASK-008 | K, U |
| **TC-018** | **Session registry alone.** Create A1/A2 and B1 as active server-side fixture sessions; revoke A by account ID and verify A1/A2 fail the active-session check while B1 passes. Confirm session creation uses fixtures only; no public test route or newly assumed sign-in authentication endpoint is added. | REQ-012 | TASK-006, TASK-008 | K, U |
| **TC-019** | **Completion sink failure is atomic.** For A with valid link and multiple sessions, force owner-success-notice append failure on S4 POST. Expect no S5 and no partial effect: old password still verifies, token remains eligible if time permits, all previously active owner sessions remain active and no owner-success notice was appended. Restore sink and retry once: exactly one success follows. | REQ-009, REQ-011, REQ-012, REQ-013, REQ-015 | TASK-007, TASK-008 | K, U |
| **TC-020** | **Competing completions.** Start two simultaneous CSRF-valid S4 completions of the same eligible link with distinct nonempty passwords. Exactly one reaches success and its password hash verifies; one owner-success notice and one token consumption, with all A sessions revoked once. Loser reports no S5 and cannot overwrite the winner's hash; no partial effects. | REQ-009, REQ-011, REQ-012, REQ-013, REQ-015 | TASK-007, TASK-008 | K, U |
| **TC-021** | **S4/S5/S6 error and accessibility paths.** With valid unused intent, submit empty new password or invalid CSRF: associated announced error, no S5, no password/session/token/owner-notice change; only **nonempty** is required, not invented complexity rules. Verify S4 programmatic label, masking, visible focus and keyboard submission; valid success renders server-side S5 with S1 link, rejected expired/used links render server-side S6 with S2/S1 links and no exposed secret; headings/status are accessible after navigation. | REQ-009, REQ-010, REQ-011, REQ-017 | TASK-005, TASK-007, TASK-008 | K, U |
| **TC-022** | **Private in-memory notifications only.** Request a link and complete a reset for synthetic A; inspect private sink for link-entry and later A-addressed success notice in order. Stub/deny outbound network/mail and query public routes: no external notification calls and no public sink inspection or token disclosure; in-memory state is isolated between app fixtures. A sink record is **not** proof of real owner delivery. | REQ-013, REQ-014, REQ-015 | TASK-001, TASK-003, TASK-007, TASK-008 | U, K |
| **TC-023** | **Automated verification gate.** At future coding checkpoint, run `python3.12 -m pytest`, inspect discovered tests and map their assertions to S1/S2/S3, server-rendered pages, known/unknown/capped parity, rolling cap, invalid/replay/expiry, success, owner sessions/notices, failure/concurrency and absence of public secrets/external delivery. Expect successful execution and explicit checks for both success and unavailable branches; the map itself is **not** an executed pytest result. | REQ-018, REQ-016 | TASK-008 | U, I, K |
| **TC-024** | **Production-limitations review.** Read delivery README/docs for local synthetic-demo and pytest instructions, restart loss, single-process lock, lack of shared/durable state, limits/sessions not production-distributed, private in-memory sink not owner delivery, residual initial-link/HTTP/cookie risks and prerequisites for production hardening. Expect clear warning that demo is not production-ready; do not add delivery infrastructure. | REQ-019 | TASK-009 | U |
| **TC-025** | **No deployment action.** At delivery review, inspect complete work/action record and change summary for deploy, publish, hosting or external-environment actions; expect no such action performed and explicit non-deployment review result. Lack of a record is an evidence gap, not proof of non-deployment; no deployment is performed by this check. | REQ-020 | TASK-009 | U |
| **TC-026** | **No new deployment workflow.** Compare the delivered repository change set against its baseline, especially `.github/workflows/`, hosting/config/script additions and CI commands; expect zero newly added deployment workflows or deployment scripts and record the review result. Existing baseline workflows are not misclassified as new. | REQ-021, REQ-020 | TASK-001, TASK-009 | U |

## Acceptance-criterion trace (all criteria individually mapped)

Each approved requirement has **one** acceptance criterion (R1). Links below identify checks, not claims that criteria already pass.

| Criterion | What the criterion requires | Proposed case IDs |
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

Each approved task has **two** acceptance criteria (A1/A2), summarized separately so both can be counted.

| Criterion | Acceptance point | Proposed case IDs |
| --- | --- | --- |
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

**Coverage count:** REQ criteria mapped **21/21**, TASK criteria mapped **18/18** (nine tasks × two), unmapped **0**, approved dispositions **0**. The map reserves **26** stable TC IDs (TC-001–TC-026). A linked case may cover several criteria only where its assertions explicitly check each one. No proposed case is represented as run or passing.

**Boundary/open issues, not silent exclusions:** Unknown-account quota is undefined; test no issuance and account-independent public response, not an invented quota. Exact throttling copy is undefined in the standard, though the approved design proposes the same generic acknowledgement for capped requests. The sign-in button's authentication behavior, detailed S2–S6 design/copy, password complexity beyond the designed nonempty check, owner link conveyance, restart persistence and multi-process operation are not added as requirements. Synthetic sink entries are not external owner delivery. Non-deployment requires a future auditable action record; if absent, report the evidence gap rather than claim the check passed.
