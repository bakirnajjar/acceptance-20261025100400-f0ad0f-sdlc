# T001 — prospective delivery risk and coverage map

Stage: `custom_document` · Key: `acceptance_20261025100400_f0ad0f_risk` · Pinned schema: `1.0` · Proposed item prefix: `R22A08`

This is an evidence/coverage map for the later contract, **not** an implementation finding or an additional requirements list. Requirement identifiers come only from the approved `requirements_analysis` output. Priorities below are provisional risk-register judgments, not measured likelihoods or approved severity ratings.

## Exact source references

| Key | source_type | source_id | locator |
| --- | --- | --- | --- |
| S1 | `user_story` | `user_story` | `characters 0-16000` |
| S2 | `attachment` | `fd6b3020-ac35-442c-bd77-c53062c11e9c` | `sign-in-wireframe.png` |
| S3 | `knowledge` | `bcf198d8-a628-401c-8641-b726fcbd00b5` | `v1, chunk 0` |

S2's visual observations are those recorded in the approved assessment, not a claim to have extracted additional image details. S3 is the run-specific recovery standard; similarly named sources are not substituted.

## Proposed risks

| Proposed ID | Prospective delivery risk and useful check | Approved requirement IDs | Evidence | Priority |
| --- | --- | --- | --- | --- |
| R22A08-001 | Server-rendered sign-in page could miss the centered outlined white card, “Sign in” heading, labeled email input with `name@example.com`, masked password input, dark rectangular button, or exact administrator footer. Compare rendered page and input behavior with the recorded wireframe observations; visible button does **not** imply working authentication. | REQ-001, REQ-002, REQ-003, REQ-004, REQ-005, REQ-017 | S1, S2 | Medium |
| R22A08-002 | The blue underlined “Forgot password?” link could be omitted or fail to start the reset-request flow. Check navigation from the server-rendered sign-in page; recovery-page layout remains unspecified. | REQ-006, REQ-017 | S2, S3, S1 | High |
| R22A08-003 | Different existing/nonexistent-account reset-request responses could disclose account existence. Compare otherwise equivalent responses, including cases affected by throttling without inventing the precise throttled-response design. | REQ-007 | S3 | High |
| R22A08-004 | More than five requests for a known account might be accepted within an hour, or rate limiting might undermine response indistinguishability. Check six known-account requests in one hour alongside the response behavior; unknown-account counting is unresolved. | REQ-008, REQ-007 | S3 | High |
| R22A08-005 | A consumed link could be replayed or a link could remain usable at exactly 30 minutes after issuance. Check single use and expiry at the boundary as well as after it; reset-link transport is unspecified. | REQ-009, REQ-010 | S3 | High |
| R22A08-006 | A valid unused unexpired link might complete without changing the synthetic account password, or tests might rely on real identities. Check the account state using synthetic fixtures; no new-password policy or restart-persistence requirement is inferred. | REQ-011, REQ-014 | S1, S3 | High |
| R22A08-007 | A successful reset might leave another represented active session signed in. Check multiple sessions for the same account after reset; the session mechanism and meaning of “active” remain to be settled. | REQ-012 | S3 | High |
| R22A08-008 | A successful reset might not notify the owner, or notifications might escape the in-memory sink. Check a captured owner-addressed notification after every successful reset without assuming external delivery. | REQ-013, REQ-015 | S3, S1 | High |
| R22A08-009 | The deliverable might miss Python 3.12/Flask or omit pytest coverage for the specified sign-in and reset behaviors. Check runtime/framework and runnable behavioral tests; no tests or implementation outcomes have yet been observed. | REQ-016, REQ-018 | S1 | Medium |
| R22A08-010 | Production limitations could be understated, or delivery could deploy the demo or add a deployment workflow. Review documentation, delivery actions, and changed workflow files; no deployment plan is authorized. | REQ-019, REQ-020, REQ-021 | S1 | Medium |

**Coverage check:** REQ-001 through REQ-021 are each linked above; all proposed IDs are distinct. No architecture, implementation, test results, production environment, likelihood measurements, or risk owner is evidenced. Open decisions include unknown-account throttling and throttled response, session representation, sign-in authentication behavior, password policy, reset-link transport, persistence across restart, and recovery-page layout. These are uncertainties for later design, not new acceptance requirements.
