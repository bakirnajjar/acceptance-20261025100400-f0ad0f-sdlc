# Phase 1 assessment: Risk notes

## Mandate and boundary

Produce a custom-document risk register for `acceptance_20261025100400_f0ad0f_risk`, with item IDs prefixed `R22A08`. Each delivery risk must link to one or more approved `REQ-###` identifiers from the authorized `requirements_analysis` stage. The final deliverables, after plan approval only, are `docs/sdlc/acceptance_20261025100400_f0ad0f_risk.json` and `.md`. This assessment is not a plan or product output. No application changes, deployment, or workflow changes are in scope.

## Evidence examined

| Evidence | Exact platform reference | Assessment |
| --- | --- | --- |
| Full pinned story | `user_story` / `user_story` / `characters 0-16000` | Python 3.12, Flask, server-rendered pages, pytest, synthetic accounts, in-memory notifications, production-limitations documentation, no deployment or deployment workflows. The story reader reported no further page. |
| Supplied wireframe | `attachment` / `fd6b3020-ac35-442c-bd77-c53062c11e9c` / `sign-in-wireframe.png` | Visually observed a centered outlined white sign-in card; heading "Sign in"; labeled "Email address" input with `name@example.com` placeholder; labeled masked-looking "Password" field with asterisks; blue underlined "Forgot password?" link; dark rectangular "Sign in" button; footer "No account? Contact your administrator." The attachment reader supplies only the reference, not image text. |
| Run-specific curated recovery standard | `knowledge` / `bcf198d8-a628-401c-8641-b726fcbd00b5` / `v1, chunk 0` | ACC-STD-01: identical existing/nonexistent-account reset-request response and five requests per account per hour; ACC-STD-02: single-use links expiring after 30 minutes and sign-out from all active sessions; ACC-STD-03: notify the owner after every successful reset. Search returned other similarly named libraries; these are not substituted for the run-specific source cited in the approved requirements. |
| Approved predecessor | Stage output key `requirements_analysis` (authorized prior-stage reader; approved `REQ-001` through `REQ-021`) | Defines the only approved requirement identifiers and acceptance criteria for risk linkage. Its assumptions and non-blocking questions constrain the risk register; no requirement is added or reinterpreted here. |

## Risk coverage to develop after approval

| Delivery risk area | Approved requirement linkage | Evidence-based concern |
| --- | --- | --- |
| Wireframe fidelity and recovery entry | REQ-001 through REQ-006, REQ-017 | Server-rendered sign-in page could omit a visible control, text, style, or navigable recovery entry; do not infer that the button must authenticate. |
| Account-existence disclosure and request-volume control | REQ-007, REQ-008 | Conditional response or inconsistent throttling could leak account existence or fail the five-per-account-per-hour cap. |
| Reset-link replay and expiry boundary | REQ-009, REQ-010, REQ-011 | A reused or 30-minutes-old link could change a password, or a valid link could fail to update the synthetic account. |
| Account session and notification follow-through | REQ-012, REQ-013, REQ-015 | A reset could leave represented sessions signed in or fail to record an owner notification in the in-memory sink. |
| Demo runtime, data isolation, automated checks, and limitations | REQ-014, REQ-016, REQ-018, REQ-019 | Real identities or external notification delivery could creep in; Python/Flask/pytest behavior and limitations could be undocumented or inadequately exercised. |
| No-deployment boundary | REQ-020, REQ-021 | Delivery work could inadvertently deploy the app or introduce a deployment workflow. |

## Evidence gaps and handling

- No approved architecture, implementation, test results, deployment plan, or production environment description is provided. Risks must be prospective delivery risks, not claims that a defect exists or that mitigation has shipped.
- The predecessor explicitly leaves unknown-account throttling, throttled responses, session representation, authentication semantics, new-password policy, reset-link transport, persistence across restart, and recovery-page layout unspecified. Record uncertainties where they materially affect a risk; do not turn a proposed mitigation into a new requirement.
- The story does not specify a quantitative risk-scoring scheme or risk owner. Priority, if used, must be presented as a reasoned risk-register judgment rather than an approved severity mandate; do not invent likelihood measurements.
- The wireframe gives only sign-in visual evidence, not the appearance of reset pages; avoid visual assertions about those pages.

## Assessment outcome

Evidence is sufficient to draft a prospective, requirement-linked risk register after plan approval. The unresolved details above are non-blocking for a risk document when clearly marked as assumptions/open questions. Preserve the precise evidence references, the approved REQ IDs, the pinned stage key, and the `R22A08` item prefix during contract authoring.
