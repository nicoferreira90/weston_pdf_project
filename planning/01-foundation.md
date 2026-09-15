# WES-01: Establish a reproducible project and delivery plan

**Status:** Setup verified  
**User outcome:** A reviewer can understand the project and prepare a local environment without external accounts.  
**Time budget:** 1 hour, including planning and setup.

## Context and assumptions

- The candidate brief is the source of requirements. The assignment allows 6–8 hours of actual work within a 48-hour submission window.
- At planning time, `backend/` and `frontend/` are empty and the project is not a Git repository.
- The three supplied PDFs are synthetic, one-page, Spanish, text-based purchase contracts. They may be included as explicit test fixtures. Runtime uploads must never be committed or logged.
- Proposed baseline: FastAPI, Pydantic, a local PDF text reader such as pypdf, and React with TypeScript and Vite. Extraction strategy is recorded in WES-02.

## Scope

- Establish this structure during setup and subsequent tickets:

  ```text
  backend/
    app/
      main.py
      config.py
      api/extraction.py
      extraction/models.py
      extraction/service.py
      extraction/pdf.py
    tests/
      test_extraction.py
      test_api.py
    pyproject.toml
    Dockerfile
  frontend/
    src/
      components/
      api/
      App.tsx
    package.json
    Dockerfile
  planning/
    01-foundation.md
    02-extraction.md
    03-api.md
    04-ui.md
  sample-documents/
  docker-compose.yml
  README.md
  AI_USAGE.md
  .gitignore
  ```

- Add package initializers, dependency lockfiles, and normal frontend build/test configuration as needed; avoid extra architectural layers.
- Set up Python and frontend dependencies and basic startup/build commands. Support both Docker Compose and local Python/Node startup, with PowerShell and macOS/Linux instructions in README.
- Include Dockerfiles and Docker Compose in this setup ticket so reviewers can run the application without installing Python or Node. Start the two development services with source reloading and frontend-to-backend connectivity; keep the setup within the overall 8-hour budget.
- Copy only the three supplied synthetic PDFs into `sample-documents/`, retaining their filenames. Keep the source copies intact.
- Ignore credentials, local environment files, virtual environments, caches, build output, and any runtime upload directories. Keep synthetic fixtures explicitly trackable.
- Start README documentation with setup, architecture, ticket order, assumptions, and current implementation status. Add an honest AI usage record and update it throughout implementation.
- The first substantive commit should contain planning and project setup before implementing extraction, API behavior, or the product UI. A startup shell is sufficient setup; feature files can be introduced in their owning tickets.

## Explicit non-goals

- No extraction behavior, upload endpoint, or product UI in the initial setup commit.
- No authentication, database, multi-tenancy, queue, cloud deployment, OCR, request history, or CI in the required scope.
- No commitment to unsupported library versions before checking the implementation environment.

## Acceptance criteria

- [x] The four tickets exist before feature implementation, and each has scope, non-goals, acceptance criteria, dependencies, and tests.
- [x] Backend and frontend dependencies install from lockfiles in clean Docker images; local startup works with the documented prerequisites.
- [x] The frontend/backend shells run locally using standard Python/Node commands without requiring Docker.
- [x] Docker images build and both services start, and the frontend can reach the backend through its API proxy.
- [x] A reviewer does not need API credentials to run the baseline application.
- [x] Only the supplied synthetic fixtures are included; generated environments and secrets are ignored.
- [ ] Git history shows planning and setup before feature work. Later commits reference `WES-02`, `WES-03`, or `WES-04` as appropriate.
- [x] `AI_USAGE.md` records tools, uses, one suggestion actually changed or rejected with a reason, and verification actually performed. Do not invent actions or results.

## Dependencies and order

First ticket. Follow with WES-02, WES-03, then WES-04. UI work can use the agreed API contract once WES-03's request and response shape is settled.

Total proposed budget: WES-01 1 hour + WES-02 2 hours + WES-03 2 hours + WES-04 3 hours = **8 hours**, using the brief's full working-time allowance. Final verification and submission documentation are included in WES-04. Track actual time; document incomplete work when the cap is reached.

Suggested first commit: `chore(WES-01): add planning tickets and project setup`.

## Proposed test plan

Use a short manual setup checklist; no dedicated automated setup tests are needed:

- Follow the README local startup instructions and run the frontend build.
- Confirm the frontend/backend shells are reachable using the documented local ports.
- Build and start Compose; verify the same frontend and API health endpoints and source reloading.
- Before the first commit, inspect Git status and verify that credentials, uploads, and generated files are ignored while the synthetic fixtures remain trackable.

## Completion evidence

Verified on 2026-09-15:

- Windows local setup: Python 3.13.7, Node 22.18.0, npm 10.9.3. The frontend, backend API docs, direct `/api/health`, and health endpoint through Vite's proxy returned HTTP 200. Native macOS/Linux startup was not separately exercised.
- `npm run build` passed on Windows and inside the Linux frontend container. Backend `python -m pip check`, `python -m ruff check .`, and `python -m ruff format --check .` passed; dependency consistency also passed in the Linux backend container.
- `docker compose config --quiet`, `docker compose build`, and `docker compose up -d --wait` succeeded. The backend health check passed, and the same HTTP endpoints worked through Compose.
- Temporary source edits verified backend reloading and updated frontend modules through the source mounts. Original source content was restored and rechecked.
- Pytest collection and `npm test -- --run` reported no tests, as expected for the skeleton. No feature test pass is claimed.
- Read-only Git checks confirmed generated files, tooling directories, credentials, and runtime PDFs are ignored, while the three synthetic fixtures remain trackable. No commits existed at verification time.

Extraction, the upload endpoint, and the product UI remain placeholders. Actual working time across planning and setup was not separately tracked; the 1-hour figure is the planned budget.
