# Requirements analysis

Schema version: `1.0` · Stage: `requirements_analysis`

## Evidence references

| Key | `source_type` | `source_id` | `locator` |
| --- | --- | --- | --- |
| S | `user_story` | `user_story` | `characters 0-16000` |
| W | `attachment` | `fd6b3020-ac35-442c-bd77-c53062c11e9c` | `sign-in-wireframe.png` |
| K | `knowledge` | `bcf198d8-a628-401c-8641-b726fcbd00b5` | `v1, chunk 0` |

K is the run-specific curated recovery standard (ACC-STD-01–03). W's attachment reader returned a reference only; the visual observations supplied for the sign-in wireframe support the card, form, link, button and footer below. No other knowledge-library duplicates or prior stage outputs are cited.

## Requirements

### REQ-001 — Sign-in card [S, W]
The sign-in page displays a centered outlined sign-in card on a white background with a “Sign in” heading.

- Given the sign-in page is requested, when it is rendered, then a centered outlined card with the heading “Sign in” appears on a white background.

### REQ-002 — Email field [W]
The sign-in card displays an input labeled “Email address” with placeholder “name@example.com”.

- Given the sign-in page is requested, when the card is rendered, then an input labeled “Email address” has placeholder “name@example.com”.

### REQ-003 — Password field [W]
The sign-in card displays a masked password input labeled “Password” with placeholder “********”.

- Given the sign-in page is requested, when the card is rendered, then an input labeled “Password” masks entered characters and has placeholder “********”.

### REQ-004 — Sign-in button [W]
The sign-in card displays a dark rectangular “Sign in” button.

- Given the sign-in page is requested, when the card is rendered, then a dark rectangular button labeled “Sign in” is visible.

### REQ-005 — Footer [W]
The sign-in card displays the footer text “No account? Contact your administrator.”

- Given the sign-in page is requested, when the card is rendered, then its footer reads “No account? Contact your administrator.”

### REQ-006 — Recovery entry [W, K]
The sign-in page provides a blue underlined “Forgot password?” link that starts a reset request.

- Given the sign-in page is displayed, when the user selects the blue underlined “Forgot password?” link, then a password-reset request flow starts.

### REQ-007 — Account-existence-independent response [K]
The response to a password-reset request is identical whether the account exists or not.

- Given one existing and one nonexistent account identifier, when otherwise equivalent reset requests are submitted, then their responses are identical and do not distinguish account existence.

### REQ-008 — Request limit [K]
Reset requests are limited to five accepted requests per account per hour.

- Given a known account and a one-hour interval, when six reset requests are submitted for that account within the interval, then no more than five requests are accepted.

### REQ-009 — Single-use links [K]
A reset link can complete a password reset only once.

- Given a valid reset link has completed a reset, when the same link is used again, then it cannot complete another reset.

### REQ-010 — Link expiry [K]
A reset link expires 30 minutes after issuance.

- Given a reset link issued at a known time, when it is used at least 30 minutes after issuance, then it cannot complete a reset.

### REQ-011 — Password change [S, K]
Completing a valid reset changes the synthetic account's password.

- Given a synthetic account and its valid unused unexpired reset link, when the owner completes the reset with a new password, then the account's password changes to the new password.

### REQ-012 — Session invalidation [K]
Completing a password reset signs the account out of every active session.

- Given an account with multiple active sessions represented by the application, when its password reset completes, then none of those sessions remains signed in.

### REQ-013 — Owner notification [K, S]
Every successful password reset notifies the account owner.

- Given a synthetic account, when a password reset succeeds, then a notification addressed to its owner is captured after the reset in the in-memory sink.

### REQ-014 — Synthetic accounts [S]
The application uses synthetic accounts rather than real customer accounts.

- Given the application is run, when its account data is inspected, then the accounts used are synthetic, not real customer identities.

### REQ-015 — In-memory notifications [S]
The application captures its notifications in an in-memory notification sink.

- Given a notification is produced, when its destination is inspected, then it is captured in an in-memory notification sink rather than delivered externally.

### REQ-016 — Runtime and framework [S]
The application is implemented in Python 3.12 with Flask.

- Given the delivered application, when its runtime and framework are inspected, then it uses Python 3.12 and Flask.

### REQ-017 — Server rendering [S]
Application pages are rendered on the server.

- Given an application page is requested, when the server responds, then its page content is server-rendered.

### REQ-018 — Automated tests [S]
Automated pytest tests cover the specified application behaviors.

- Given the delivered project, when its automated tests are run with pytest, then they exercise the specified sign-in and password-reset behaviors.

### REQ-019 — Production limitations [S]
Project documentation identifies the application's production limitations.

- Given the delivered project, when its documentation is reviewed, then it identifies limitations of using the small application in production.

### REQ-020 — No deployment [S]
The project is not deployed as part of this work.

- Given the project is delivered, when the work performed is reviewed, then no deployment was performed.

### REQ-021 — No deployment workflows [S]
No deployment workflows are added to the project.

- Given the delivered repository changes, when workflow files are reviewed, then no deployment workflow has been added.

## Assumptions

1. acceptance-20261025100400-f0ad0f-skill-sentinel — the acceptance skill produced this output.
2. The complete pinned story has no end marker, and the attachment has no visible acceptance marker; neither marker is invented.
3. For nonexistent accounts, the reset-request response remains independent of account existence; the per-account request limit is applied to known accounts without inventing an unknown-account threshold.
4. A throttled request does not reveal whether an account exists; the exact throttling response is not specified.
5. Every active session means every session represented by the application for the account; the session mechanism is not prescribed.
6. The sign-in button is a visible control only: successful authentication, registration, password policy, reset-link transport, restart persistence, and exact recovery-page layout are not specified by the evidence.
7. The in-memory notification sink is the observable destination for reset notifications; no external delivery channel is assumed.

## Open questions (all non-blocking)

1. **How should reset requests for nonexistent accounts count toward the per-account hourly limit?** Assumption: apply the five-per-account-per-hour limit to known accounts and keep the response independent of account existence; do not invent an unknown-account limit.
2. **What response should a throttled reset request show, and must it match the ordinary request response?** Assumption: do not reveal account existence, but leave the precise throttling response unspecified.
3. **What constitutes an active session in the small application?** Assumption: use an application-local representation allowing a successful reset to invalidate every represented active session of that account.
4. **Should the displayed Sign in button authenticate, and what should the outcome be?** Assumption: require the displayed control without claiming an authentication outcome.
5. **What policy should govern a new password?** Assumption: leave password length and complexity rules unspecified.
6. **How should reset links be transported to account owners?** Assumption: capture notifications in the in-memory sink without external sending or a prescribed transport channel.
7. **Must synthetic accounts, reset state, or notifications survive an application restart?** Assumption: do not require persistence across restarts.
8. **What should the recovery-request and new-password pages look like?** Assumption: use server-rendered pages for the functional recovery flow, without inventing a visual design.
