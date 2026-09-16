# AI usage

## Tools and purpose

- OpenAI Codex helped read the candidate brief and synthetic PDFs, draft and simplify the four planning tickets, and scaffold the FastAPI/React project, Docker setup, and documentation.
- For WES-02, Codex implemented the result models, PDF text reader, four contextual field matchers, and focused extraction tests. The parser supports UF, CLP, and USD in the documented contract wording.
- For WES-03, Codex implemented the multipart upload endpoint, selection validation, processing-error mapping, and 11 API tests. It checked FastAPI's form/file documentation and FastAPI's request-cleanup source code before implementing the route.
- For WES-04, Codex built the React extraction workflow and 10 mocked-fetch tests, then applied the reviewed error-message fixes: HTTP error handling before successful-response validation and a non-repeating alert heading. Codex also updated delivery documentation and reran final verification.
- Codex used shell commands to inspect files, install dependencies, generate lockfiles, and run setup checks. It consulted official FastAPI, Vite, and Docker documentation for startup, proxying, and container configuration, and official OpenAI documentation for `AGENTS.md` behavior.
- Claude Code (Anthropic) reviews what Codex writes. For the setup commit, it checked the tickets and skeleton against the brief, re-ran the setup checks, and removed wording left over from the Codex conversation from the tickets and README.
- Claude Code reviewed WES-03 and WES-04, wrote the CSS restyle, and ran cross-platform verification. Its contribution included implementation as well as review.
- Astra generated the synthetic A–N PDFs using a pypdf script that reused the canonical page size and font resources, and checked each fixture against the extraction service. The fixture index records both expected results and deliberate parser limitations.
- For WES-05, Codex drafted the optional CI/tenant-design ticket and implemented the GitHub Actions workflow. It checked the official [checkout](https://github.com/actions/checkout), [setup-python](https://github.com/actions/setup-python), and [setup-node](https://github.com/actions/setup-node) documentation for action versions and inputs. The tenant design note remains pending.

## A suggestion changed or rejected

The initial generated extraction ticket proposed testing all 15 nonempty field combinations across all three PDFs. At the user's direction, this was replaced with the three fixture cases and representative selections. The smaller plan better fits the assignment's time budget and keeps attention on missing-field semantics, selected-field behavior, and processing errors.

## Verification of generated work

- Reviewed the implementation against the brief, AGENTS.md, and the chosen architecture. The extraction service, HTTP API, and user interface are implemented.
- Installed dependencies and generated a Python dependency lockfile and npm lockfile.
- Ran the frontend TypeScript/production build successfully, and checked backend dependency consistency, Ruff lint, and Ruff formatting.
- Started the local backend/frontend and verified HTTP 200 responses for the frontend, API documentation, direct health endpoint, and health endpoint through the frontend proxy.
- Built both Docker images, started the Compose stack, and checked the frontend, API documentation, direct health endpoint, and health endpoint through the frontend proxy. Verified source reloading with temporary edits, then restored and rechecked the original source. The frontend build and backend dependency consistency also passed inside the Linux containers.
- At the skeleton stage, pytest and Vitest reported no tests. WES-02 added 12 extraction tests; WES-03 and WES-04 brought the totals to 23 backend and 10 frontend tests.
- Claude Code independently re-ran `pip check`, Ruff lint and format checks, `npm run build`, `git add --dry-run .`, and `docker compose up --build --wait` with the health endpoints, before the first commit. It also extracted the text of the three synthetic PDFs to confirm the expected values in WES-02.
- For extraction, tests initially failed against the placeholders, then passed after implementation. They assert actual fixture values, selected-only matcher execution, request order and independent results, changed synthetic values, signing-date semantics, textless-document errors, and invalid status/value combinations. Ruff lint and formatting checks also passed. No dependency changes were needed for WES-02.
- Claude Code identified that the address matcher could include an adjacent sentence. Codex extended the existing synthetic cases to reproduce that bug and a renamed-heading failure, then changed the matcher to stop at the sentence boundary while preserving common address abbreviations. The total remains 12 tests.
- The implementation assumes well-formed PDFs. Malformed-file handling is outside scope, while processing errors remain distinct from missing values.
- For WES-03, tests initially failed against the placeholder, then all 23 backend tests passed locally and in Docker. Ruff lint and formatting checks passed. Real uploads were verified directly and through Vite for both local startup and Compose, including a textless-PDF error through Compose. Resource cleanup and absence of document logging were reviewed in the handler and FastAPI's request lifecycle.

- Final WES-04 verification passed all 23 backend tests, all 10 frontend tests, and the frontend production build on Windows and in Linux containers. Backend Ruff lint and format checks passed. Headless Edge checks exercised the three canonical PDFs, keyboard subset submission, a textless-PDF error, request-error recovery controls, desktop/mobile layout, long-value wrapping, and accessible status/alert roles. A full screen-reader session and native macOS/Linux startup were not separately tested.
- Windows reserved port 5173 during the final pass. Docker verification used a temporary host-port override to 6173; local verification used backend 8001 and frontend 6174. The same application code and API proxy were used. Temporary browser/local-server processes were stopped after the checks; verification helpers and captures remain outside version control.

- For WES-05, the workflow's check commands passed in existing Linux containers: backend lint and formatting, 23 backend tests, 10 frontend tests, and the frontend production build. A hosted Actions run, including checkout/runtime setup/dependency installation, has not yet been verified; no CI badge or hosted success is claimed.

The developer estimates approximately 6 hours of actual working time through WES-04: 2 hours for WES-01, 1 hour each for WES-02 and WES-03, and 2 hours for WES-04. These are retrospective estimates, separate from the original 8-hour plan. WES-05 has a 1-hour budget; its actual time has not yet been recorded.
