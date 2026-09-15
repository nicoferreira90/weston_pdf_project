# AI usage

## Tools and purpose

- OpenAI Codex helped read the candidate brief and synthetic PDFs, draft and simplify the four planning tickets, and scaffold the FastAPI/React project, Docker setup, and documentation.
- For WES-02, Codex implemented the result models, PDF text reader, four contextual field matchers, and focused extraction tests. The parser supports UF, CLP, and USD in the documented contract wording.
- Codex used shell commands to inspect files, install dependencies, generate lockfiles, and run setup checks. It consulted official FastAPI, Vite, and Docker documentation for startup, proxying, and container configuration, and official OpenAI documentation for `AGENTS.md` behavior.
- Claude Code (Anthropic) reviews what Codex writes. For the setup commit, it checked the tickets and skeleton against the brief, re-ran the setup checks, and removed wording left over from the Codex conversation from the tickets and README.

## A suggestion changed or rejected

The initial generated extraction ticket proposed testing all 15 nonempty field combinations across all three PDFs. At the user's direction, this was replaced with the three fixture cases and representative selections. The smaller plan better fits the assignment's time budget and keeps attention on missing-field semantics, selected-field behavior, and processing errors.

## Verification of generated work

- Reviewed the skeleton against the brief, AGENTS.md, and the chosen architecture. Extraction is now implemented; API and UI feature files remain placeholders for later tickets.
- Installed dependencies and generated a Python dependency lockfile and npm lockfile.
- Ran the frontend TypeScript/production build successfully, and checked backend dependency consistency, Ruff lint, and Ruff formatting.
- Started the local backend/frontend and verified HTTP 200 responses for the frontend, API documentation, direct health endpoint, and health endpoint through the frontend proxy.
- Built both Docker images, started the Compose stack, and checked the frontend, API documentation, direct health endpoint, and health endpoint through the frontend proxy. Verified source reloading with temporary edits, then restored and rechecked the original source. The frontend build and backend dependency consistency also passed inside the Linux containers.
- At the skeleton stage, pytest and Vitest reported no tests. After WES-02, 12 extraction tests pass locally and in Docker; the frontend test suite remains pending.
- Claude Code independently re-ran `pip check`, Ruff lint and format checks, `npm run build`, `git add --dry-run .`, and `docker compose up --build --wait` with the health endpoints, before the first commit. It also extracted the text of the three synthetic PDFs to confirm the expected values in WES-02.
- For extraction, tests initially failed against the placeholders, then passed after implementation. They assert actual fixture values, selected-only matcher execution, request order and independent results, changed synthetic values, signing-date semantics, textless-document errors, and invalid status/value combinations. Ruff lint and formatting checks also passed. No dependency changes were needed for WES-02.
- Claude Code identified that the address matcher could include an adjacent sentence. Codex extended the existing synthetic cases to reproduce that bug and a renamed-heading failure, then changed the matcher to stop at the sentence boundary while preserving common address abbreviations. The total remains 12 tests.
- The implementation assumes well-formed PDFs. Malformed-file handling is outside scope, while processing errors remain distinct from missing values.

This record will be updated with implementation decisions and feature test results as work progresses.
