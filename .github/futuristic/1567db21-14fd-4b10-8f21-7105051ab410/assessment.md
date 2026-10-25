# Phase 1 assessment: test case design

## Scope and evidence

The full pinned story requests a local Python 3.12/Flask, server-rendered password-reset application with pytest, synthetic accounts, an in-memory notification sink, production-limitations documentation, and no deployment or deployment workflows. The supplied image shows only the sign-in page: a white canvas with an approximately centered, thin dark outlined card; "Sign in" heading; "Email address" and "Password" labels; `name@example.com` and `********` placeholders; a blue underlined "Forgot password?" link; a dark rectangular "Sign in" button; and "No account? Contact your administrator." footer. The picture does not establish input masking on entry, actual navigation, authentication, or recovery-page appearance.

Approved predecessor outputs available through the stage-output service are `requirements_analysis`, `ui_analysis`, and `solution_design`; a related prospective risk register, `acceptance_20261025100400_f0ad0f_risk`, is also available. Requirements analysis defines REQ-001 through REQ-021 with one acceptance criterion each. Solution design defines TASK-001 through TASK-009, each with two acceptance criteria, and `coverage_dispositions: []`; thus all 21 requirements require proposed test coverage rather than relying on an approved exemption. The UI analysis distinguishes observed S1 from proposed S2-S6, and the solution design proposes a local-only, lock-protected in-memory implementation. Neither is proof of an existing application or passing tests.

The run-specific curated recovery standard requires the forgot-password entry, identical existing/nonexistent reset-request responses, at most five requests per account per hour, single-use links expiring 30 minutes from issuance, sign-out of every active session on successful reset, and owner notification. Use the matching run-specific knowledge reference, not similarly named documents from other runs.

Evidence references supplied by the tools (retain exact identifiers and locators in the eventual contract):

| Type | Source ID | Locator |
| --- | --- | --- |
| user_story | `user_story` | `characters 0-16000` |
| attachment | `fd6b3020-ac35-442c-bd77-c53062c11e9c` | `sign-in-wireframe.png` |
| knowledge | `bcf198d8-a628-401c-8641-b726fcbd00b5` | `v1, chunk 0` |

The stage-output reads provide stage keys but no `source_reference` object or locator. Do not fabricate a `stage_output` reference; use their approved identifiers for trace links, and cite the available story, image, or run-specific standard where applicable.

## Coverage design for the next phase

- Test the observed S1 presentation, actual password-type masking, accessible labeling and keyboard use, and the S1-to-S2 recovery entry (REQ-001-006; TASK-002, TASK-008).
- Compare full public responses for valid known, unknown and capped requests; test invalid/CSRF input and issuance/sink failure; exercise the rolling-hour fifth, sixth and window-boundary cases without inventing an unknown-account quota (REQ-007-008, REQ-015; TASK-003-004, TASK-008).
- Check unknown, used, replayed and expired links; test GET without consumption, completion immediately before and exactly at/after 30 minutes, secret-free public pages, and concurrent submissions (REQ-009-010; TASK-005, TASK-007-008).
- Test a successful synthetic-account password change, all represented owner sessions revoked without affecting another account, exactly one owner-addressed in-memory success notice, and atomic rollback on sink failure; no public sign-in feature is inferred (REQ-011-015; TASK-001, TASK-006-008).
- Inspect Python 3.12/Flask configuration, server-rendered pages, pytest behavioral tests, production limitations, action record for non-deployment, and repository changes for absence of a new deployment workflow (REQ-016-021; TASK-001-002, TASK-004-005, TASK-007-009). Proposed TC-NNN cases must link known REQ-NNN and TASK-NNN IDs and state observable preconditions, data, actions and expected results in the pinned schema's steps and expected-results fields.

## Limits and unresolved details

No implementation, executed pytest results, deployment record, or recovery-page wireframes were supplied; test cases are proposals, not passing results. The sign-in button's authentication behavior, link conveyance to an owner, detailed recovery copy, password-complexity rules, unknown-account throttling and multi-process/restart persistence remain unspecified. The approved solution design proposes fixture-created sessions, a nonempty new password, generic known/unknown/capped public feedback, and private link inspection without external delivery; tests should verify those proposed design choices without claiming they came from the image or standard. A documentation/action-record review can establish the non-deployment boundary only when delivery evidence exists.
