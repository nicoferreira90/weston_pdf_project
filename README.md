# Weston purchase-contract extraction

A FastAPI and React project for extracting selected fields from text-based purchase-contract PDFs. The planned workflow lets users choose purchaser name, purchase price, contract date, and/or property address before submitting a document.

**Current status: runnable project skeleton.** Docker Compose and local startup are implemented. The backend provides `GET /api/health`, and the frontend displays a setup page. Extraction, uploads, and the product UI will be implemented in WES-02 through WES-04.

Requirements are defined in the [candidate brief](purchase-contract-field-extraction-candidate-brief.md). Project working guidance is in [AGENTS.md](AGENTS.md).

## Quick start with Docker

Docker Compose is an included development feature. With Docker running in Linux-container mode, start both services from the repository root:

```sh
docker compose up --build
```

Open the frontend at **http://localhost:5173**. The backend is at http://localhost:8000, with interactive API documentation at http://localhost:8000/docs. No API credentials or local Python/Node installation are needed for this path.

The frontend forwards `/api` requests to the backend. You can check the complete connection at http://localhost:5173/api/health; it should return `{"status":"ok"}`.

Source directories are mounted into the containers, so edits to backend Python and frontend source files reload automatically. Dependencies stay inside the images; rebuild after changing dependency manifests or lockfiles. The supplied synthetic PDFs are mounted read-only for backend tests.

To run in the background, use `docker compose up --build -d`. Useful commands:

```sh
docker compose logs -f
docker compose down
```

This is a development setup using Uvicorn reload and the Vite development server. Ports are published on the local machine only. If a port is already occupied, stop the other local server before starting Compose.

## Local setup without Docker

Use **Python 3.13** and **Node.js 22.12 or newer within the 22.x line**, with npm. Both startup paths use the same application code and dependency lockfiles.

Use two terminals, each starting in the repository root (`weston_pdf_project/`).

### Backend — Windows PowerShell

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock -e ".[dev]"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

Calling the virtual environment's Python directly avoids needing to activate it or change PowerShell's execution policy.

### Backend — macOS/Linux

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.lock -e ".[dev]"
python -m uvicorn app.main:app --reload --port 8000
```

The `dev` extra includes pytest, HTTPX, and Ruff. `requirements.lock` pins the runtime and development dependencies.

### Frontend — second terminal, all platforms

```sh
cd frontend
npm ci
npm run dev
```

`npm ci` installs the versions recorded in `package-lock.json`. Local addresses:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- API documentation: `http://localhost:8000/docs`

Vite proxies `/api` to `http://127.0.0.1:8000` locally and to `http://backend:8000` inside Compose via `API_PROXY_TARGET`. Browser requests use relative `/api/...` URLs in both cases. Stop each local server with `Ctrl+C`. On Windows, use `npm.cmd` if PowerShell blocks the `npm.ps1` wrapper.

## Planned workflow

1. Select one or more of the four available fields.
2. Choose one PDF and start extraction.
3. See exactly the selected fields, each with a found value or an explicit missing flag.
4. Repeat with another document or selection. Previous results retain the selection used to produce them.

A missing field means the document was successfully processed but the value could not be located. File-reading and other processing failures appear as request errors.

## Architecture and scope

- `backend/app/main.py`: FastAPI application and health endpoint.
- `backend/app/api/extraction.py`: placeholder for WES-03's upload endpoint.
- `backend/app/extraction/`: placeholders for WES-02's models, PDF reader, and extraction service.
- `frontend/src/`: React/TypeScript startup shell and test setup; API and component directories are ready for WES-04.
- `sample-documents/`: the three supplied synthetic PDFs.
- `docker-compose.yml`: backend/frontend development services with source reloading.
- `planning/`: implementation tickets and proposed verification.

Extraction will use deterministic local text parsing scoped to the supplied Spanish contract style. It will preserve names, dates, addresses, and monetary units as text and will not depend on filenames or hardcoded sample values. Runtime uploads and extracted applicant information must not enter logs or version control.

OCR, external model APIs, authentication, databases, queues, and request history are outside the required scope. Extraction and the upload/result workflow are not implemented yet. Parser limitations and any remaining gaps will be recorded as work progresses.

## Checks and tests

Run backend tests from `backend/`:

```powershell
# Windows PowerShell
.\.venv\Scripts\python.exe -m pytest
```

```bash
# macOS/Linux, with the virtual environment active
python -m pytest
```

From `frontend/`:

```sh
npm test -- --run
npm run build
```

With Compose running, the equivalent commands are:

```sh
docker compose exec backend python -m pytest
docker compose exec frontend npm test -- --run
docker compose exec frontend npm run build
```

**No feature tests exist yet:** pytest and Vitest currently report no tests and return a nonzero exit code. Tests will accompany WES-02 through WES-04, within the maximum of 25 backend tests and 10 frontend tests. Final verification will include a browser walkthrough of the supplied PDFs, a subset selection, and a corrupt file.

Setup verification is recorded in [WES-01](planning/01-foundation.md#completion-evidence). Backend lint commands are `python -m ruff check .` and `python -m ruff format --check .` from `backend/` using its virtual environment, or their equivalents via `docker compose exec backend`.

## Delivery plan

| Ticket | Outcome | Budget |
| --- | --- | --- |
| [WES-01](planning/01-foundation.md) | Project setup and reproducible local startup | 1 hour |
| [WES-02](planning/02-extraction.md) | Selected-field extraction and missing semantics | 2 hours |
| [WES-03](planning/03-api.md) | Validated PDF upload API | 2 hours |
| [WES-04](planning/04-ui.md) | Complete user flow and final verification | 3 hours |

Total budget: **8 hours**, including documentation and verification. The first substantive Git commit must contain planning and project setup before feature implementation. Later commits reference their ticket IDs.

See [AI_USAGE.md](AI_USAGE.md) for tools used, a changed/rejected suggestion, and verification performed.
