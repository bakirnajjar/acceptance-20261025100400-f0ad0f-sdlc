# Coding delivery — local synthetic password-reset demo

**Scope and result:** T001–T010 are checkpointed; this T011 delivery adds only this report and `tests.json`. The implemented design tasks are TASK-001–TASK-009. This is a local Python 3.12 Flask/Jinja and pytest demonstration, **not a deployed or production-ready service**. The sole observed screen is the supplied sign-in wireframe; other recovery screens follow the approved design. The pictured Sign in button does not authenticate. Notifications are captured in a private in-memory sink, **not delivered to owners**.

## Implemented TASK and REQ trace

| Approved task | Implementation and verification |
| --- | --- |
| TASK-001 | `src/reset_demo/foundation.py`, `src/reset_demo/__init__.py`, `pyproject.toml`, `uv.lock`: fresh app-local locked synthetic `.test` accounts, adaptive scrypt hashes, injectable UTC clock and token factory, private in-memory sink. `tests/test_foundation.py`. |
| TASK-002 | `templates/sign_in.html`, `templates/reset_request.html`, server-rendered routes: observed S1 labels, placeholders, outlined card, footer and recovery entry without invented login. `tests/test_sign_in.py`; real browser presentation/interaction still manual. |
| TASK-003 | `recovery.py` and foundation store: digested random links, serialized five accepted known-account issuances in a trailing hour, unknown/capped generic result, failure-safe sink append. `tests/test_recovery.py`. |
| TASK-004 | Request/confirmation routes and Jinja templates: CSRF and generic known/unknown/capped response parity. `tests/test_reset_request.py`. |
| TASK-005 | Link, intent and new/unavailable routes/templates: unused link and strict issuance-based 30-minute expiry, secret-free server-held intent, safe public responses. `tests/test_reset_link.py`; browser history and other infrastructure logs are not controlled. |
| TASK-006 | Private, opaque, account-scoped session registry and full owner-session revocation, created in fixtures rather than a public login or fixture route. `tests/test_sessions.py`. |
| TASK-007 | Atomic logical reset under process lock: hash replacement, token consumption, owner-session revocation and one owner-addressed sink notice; rollback on hashing/sink failure, replay and concurrency handling. `tests/test_reset_completion.py`. |
| TASK-008 | Isolated executable service, Flask-client and loopback-HTTP journey/failure checks in `tests/`, including `test_behavioral_gate.py`; 39 pytest cases collected and passed. Markup tests are not browser visual, keyboard or accessibility-tree tests. |
| TASK-009 | `README.md`: local run/test instructions, private-sink limitations, restart/multi-worker and security limitations, production prerequisites and delivery-boundary review checklist. No hosting or workflow implementation. |

| Requirement | Delivery evidence and limit |
| --- | --- |
| REQ-001–005 | Server-rendered S1 markup and intended CSS in `templates/sign_in.html` and `tests/test_sign_in.py`; screenshot geometry, actual typed masking and browser presentation are **not** verified by pytest (TC-003/004 manual). |
| REQ-006 | S1 recovery link and S2/S3 HTTP pages (`test_sign_in.py`, `test_reset_request.py`); pointer/keyboard activation and accessible announcements remain manual (TC-005/006). |
| REQ-007 | Complete Flask-client response snapshots for known/unknown/capped valid submissions, private sink assertions (`test_reset_request.py::test_tc_007_known_unknown_capped_full_http_parity_and_private_links`); no constant-time promise. |
| REQ-008 | Fifth/sixth and strict trailing-hour boundary, normalization/concurrency, failure rollback (`test_recovery.py` TC-008–010). |
| REQ-009–010 | Link single use, GET non-consumption and rechecked strict 30-minute issuance deadline (`test_reset_link.py`, `test_reset_completion.py` TC-012–016/020); TC-012 remains manual for full browser/infrastructure behavior. |
| REQ-011 | Changed adaptive hash and no public plaintext on committed reset; replay, authorization and rollback tests (`test_reset_completion.py` TC-015–017/019/020). |
| REQ-012 | All represented owner sessions revoked, other owner unaffected (`test_sessions.py` TC-018, `test_reset_completion.py` TC-015/020). Not an implemented authenticated sign-in/session cookie flow. |
| REQ-013 | One owner-addressed **in-memory** success notice on commit, never an external delivery claim (`test_reset_completion.py` TC-015/019/020/022). |
| REQ-014–016 | Synthetic-only `.test` account isolation, private in-memory sink, Python 3.12/Flask configuration (`test_foundation.py` TC-001/002/022); full TC-002 deployment-configuration inspection is manual. |
| REQ-017 | Flask/Jinja-rendered S1–S6 and HTTP assertions (`test_sign_in.py`, `test_reset_request.py`, `test_reset_link.py`, `test_reset_completion.py`); accessibility-tree checks remain manual. |
| REQ-018 | `python3.12 -m pytest`: 39 passed, including behavioral journey TC-023. This does **not** close browser-dependent manual cases. |
| REQ-019 | `README.md` local setup, production limitations and prerequisites; TC-024 is a documentation review rather than an executable docs assertion. |
| REQ-020 | No deployment action is requested or performed in this T011 task, but a **complete delivery action record is unavailable**; no-deployment across the whole delivery remains unverified (TC-025). |
| REQ-021 | Baseline-to-current repository diff shows no added `.github/workflows/` or deployment configuration/script; TC-026 also calls for the missing action-record cross-check, so it remains manual/unverified overall. |

## Validation executed from repository root

| Exact command | Observed result |
| --- | --- |
| `python3.12 -m pytest --collect-only -q` | 39 actual test nodes collected. |
| `python3.12 -m compileall -q src/reset_demo` | Exit 0, no output. |
| `python3.12 -m pytest` | Exit 0, **39 passed in 10.81s** on Python 3.12.3 / pytest 8.4.2. |
| `python3.12 -m ruff check .` | Exit 0, `All checks passed!`. |
| `python3.12 -m ruff format --check .` | Exit 0, `31 files already formatted`. |

`tests.json` maps each of TC-001–TC-026 exactly once, with collected node references only for the automated entries. **Manual IDs:** TC-002, TC-003, TC-004, TC-005, TC-006, TC-011, TC-012, TC-021, TC-024, TC-025, TC-026. In particular the HTML/HTTP checks alongside TC-003/004/005/006/012/021 do not prove rendered visual geometry, masked typing, actual keyboard operation, screen-reader output, browser history or infrastructure-log handling. TC-011's error attributes are checked but announcements/focus are not. TC-023 is an executable behavioral/integration gate, not an assertion that those manual interactions have passed.

## Delivery boundary and evidence gap

Baseline `0065943` had no `.github/workflows/` entries (`git ls-tree -r --name-only 0065943 -- .github/workflows`). `git diff --name-status 0065943 --` before these T011 artifacts listed only `.github/futuristic/d6399381-47bc-4fad-8beb-54cfdb851b56/assessment.md`, `.gitignore`, `.python-version`, `README.md`, `pyproject.toml`, `uv.lock`, `src/reset_demo/__init__.py`, `src/reset_demo/foundation.py`, `src/reset_demo/recovery.py`, the eight `src/reset_demo/templates/{base,index,reset_confirmation,reset_new,reset_request,reset_success,reset_unavailable,sign_in}.html` files, and the nine `tests/test_{behavioral_gate,foundation,recovery,reset_completion,reset_link,reset_request,sessions,sign_in,smoke}.py` files. `git ls-files --others --exclude-standard` was empty before this artifact change; the two delivery files are now the only intended untracked additions. No changed path is a workflow, hosting configuration or deployment script; `.github/futuristic/` is reporting, not `.github/workflows/`. This **diff finding is not an action-record finding**: the complete delivery action record needed by TC-025 and TC-026 was not available, so do not infer that no deployment occurred across the whole run.

The local demo loses accounts, links, quotas, sessions and notices on restart; independent workers do not share any of that state. The sink cannot deliver links or success notices. The initial bearer URL can remain in browser history or upstream logs even though subsequent page/redirect output and the included app-server access log avoid it. Loopback HTTP does not provide production transport security. There is no production password policy, durable transactional storage, cross-worker session validation, external owner delivery or authenticated sign-in. Production use requires a separately scoped design, not a reinterpretation of these passing tests.
