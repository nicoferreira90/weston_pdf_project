# Weston purchase-contract extraction

A FastAPI and React application for extracting selected fields from text-based purchase-contract PDFs. Users choose purchaser name, purchase price, contract date, and/or property address before submitting a document.

**Current status: complete extraction workflow implemented and verified.** The React UI supports field selection, PDF upload, found/missing results, and recovery from request errors. Both Docker Compose and local Python/Node startup are supported, without external accounts or API credentials.

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

Ports **8000 and 5173 must be available**. Stop conflicting local servers or Compose services first. Vite uses a strict port setting and exits if 5173 is unavailable instead of choosing another port.

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

Windows may reserve a port even when no server is listening. If 5173 fails with an access-permissions error, inspect `netsh interface ipv4 show excludedportrange protocol=tcp` and choose an available port. For example, run the local frontend with `npm run dev -- --port 6173`. For Docker, change the frontend port mapping in `docker-compose.yml` to `"127.0.0.1:6173:5173"` and restart Compose. Open `http://localhost:6173`; the backend and API proxy configuration stay the same.

## Extraction API

Send `POST /api/extractions` as `multipart/form-data` with one `file` part and repeated `selected_fields` values. Select one to four distinct IDs from `purchaser_name`, `purchase_price`, `contract_date`, and `property_address`. Field order is preserved in the response.

From the repository root on macOS/Linux:

```bash
curl http://localhost:8000/api/extractions \
  -F "file=@sample-documents/missing-property-address.pdf" \
  -F "selected_fields=property_address" \
  -F "selected_fields=purchase_price"
```

Windows PowerShell:

```powershell
curl.exe http://localhost:8000/api/extractions -F "file=@sample-documents/missing-property-address.pdf" -F "selected_fields=property_address" -F "selected_fields=purchase_price"
```

Both requests return HTTP 200 with:

```json
{
  "results": [
    {"field_id": "property_address", "status": "missing", "value": null},
    {"field_id": "purchase_price", "status": "found", "value": "UF 6.250"}
  ]
}
```

The same endpoint is available through the Vite proxy at `http://localhost:5173/api/extractions`. The UI uses the relative URL `/api/extractions`. Each request supplies its own file and selection; the server keeps no request history or shared selection.

| Status | Meaning |
| --- | --- |
| 200 | Processing succeeded, including when every selected field is missing. |
| 422 | Missing, unknown, duplicate, or too many field IDs; a missing/empty file; or a PDF without extractable text. |
| 500 | An unexpected reader or extraction failure; returns a generic message. |

Errors have a `detail` property and no results array. FastAPI request-validation errors use a list of validation details; duplicate selections, empty uploads, and processing errors use a message string. For example, a textless PDF returns HTTP 422 with:

```json
{"detail": "The PDF contains no extractable text. Please upload a text-based PDF."}
```

The API assumes well-formed PDFs; custom malformed-file checks and upload size/page policies are outside scope. Unexpected failures return `{"detail":"Extraction failed. Please try again."}` without parser diagnostics or document contents. Upload resources are closed after processing, and the application does not persist the document or log its contents. FastAPI may use temporary spooled files while receiving uploads; these are closed with the request.

## Using the application

1. Select one or more of the four available fields.
2. Choose one text-based PDF and click **Extract fields**. Form controls are disabled while the request runs.
3. See exactly the selected fields, each with a found value or an explicit missing flag.
4. Repeat with another document or selection. Completed results retain their submitted filename and selection while you prepare the next request. Starting that request clears the old results; a failure shows an error and lets you retry.

A missing field means the document was successfully processed but the value could not be located. File-reading and other processing failures appear as request errors.

### Demo documents

Select all four fields and upload each supplied PDF:

| Document | Expected result |
| --- | --- |
| `complete-purchase-contract.pdf` | All four fields found. |
| `missing-property-address.pdf` | Property address missing; the other three fields found. |
| `missing-price-and-date.pdf` | Purchase price and contract date missing; purchaser name and property address found. |

Then select only Purchase price and Property address and repeat an upload to see only those two results. The additional [A–N demo set](sample-documents/non-canon-pdfs/README.md) covers explicit currencies, wrapping, abbreviations, distracting values, absent fields, and documented wording limits, with expected results for each PDF.

## Architecture and scope

- `backend/app/main.py`: FastAPI application and health endpoint.
- `backend/app/api/extraction.py`: multipart upload endpoint, selection validation, and HTTP error mapping. The synchronous route runs blocking PDF work in FastAPI's thread pool.
- `backend/app/extraction/`: validated result models, an in-memory PDF text reader, and the selected-field extraction service.
- `frontend/src/App.tsx`: form inputs, submission state, and completed results stored with their request context.
- `frontend/src/api/extraction.ts`: multipart requests, response validation, and readable network/HTTP error messages.
- `frontend/src/components/Results.tsx`: selected-field results and explicit Missing flags.
- `frontend/src/fields.ts`: the four field IDs and labels shared by the form and results.
- `frontend/src/styles.css`: responsive layout, input states, focus styles, and result/error presentation.
- `sample-documents/`: the three canonical synthetic PDFs and the additional `non-canon-pdfs/` demo set.
- `docker-compose.yml`: backend/frontend development services with source reloading.
- `planning/`: implementation tickets and proposed verification.

Extraction uses deterministic local text parsing scoped to the supplied Spanish contract style. It preserves names, dates, addresses, and monetary units as text and does not depend on filenames or hardcoded sample values. Runtime uploads and extracted applicant information must not enter logs or version control.

OCR, external model APIs, authentication, databases, queues, and request history are outside the required scope.

### Extraction service and supported wording

From a Python session in `backend/`, using its virtual environment:

```python
from pathlib import Path
from app.extraction.models import FieldId
from app.extraction.service import extract_fields

document = Path("../sample-documents/complete-purchase-contract.pdf").read_bytes()
response = extract_fields(document, [FieldId.PURCHASE_PRICE, FieldId.CONTRACT_DATE])
print(response.model_dump_json(indent=2))
```

The service reads text once and runs only the selected matchers, returning results in selection order. The API validates selections before calling the service. Supported patterns are:

- Purchaser names in the introductory `comparecen … como comprador/compradora` clause, excluding `don/doña`.
- Prices stated as `El precio total prometido para la compraventa es de …`, with an explicit UF, CLP, or USD prefix. Amounts retain their separators; no currency conversion or bare-`$` inference is performed.
- Dates stated as `Firmado el …` or `Fecha de firma: …`, in Spanish day/month/year wording. Dates remain strings without calendar validation; pending signing dates are not inferred from other dates.
- Addresses following the property's `La vendedora promete vender … ubicado/ubicada en …` wording and ending at the sentence boundary. Wrapped addresses and the abbreviations `Av.`, `Avda.`, `Depto.`, and `Dpto.` are preserved; subsequent sentences and headings are excluded.

Matching ignores case and normalizes whitespace. It assumes the supplied style of prose; it is not a general contract parser. Different wording can return `missing` even when a value is present. A well-formed PDF without extractable text raises `DocumentProcessingError`; other reader errors propagate rather than becoming missing values. Malformed or non-PDF files are not specially handled.

### Known gaps

- Only the documented Spanish wording is supported. Other wording can return `missing` despite a visible value; the app does not provide confidence scores or evidence snippets.
- Scanned/textless PDFs cannot be extracted and produce a request error. Corrupt or non-PDF uploads that fail in the reader receive a generic HTTP 500; there is no dedicated malformed-file validation.
- There is no persistent history or asynchronous job processing. Each request completes synchronously, and the UI holds only its latest completed result until the next submission or page reload.
- Verification covered Windows local startup and Linux containers. Native macOS/Linux startup and a full screen-reader session were not separately exercised; keyboard behavior and accessible status/alert roles were checked.

## Checks and tests

[GitHub Actions](.github/workflows/tests.yml) is configured to run on pushes and pull requests, with separate Ubuntu jobs for backend lint/formatting/tests and frontend tests/build. It uses Python 3.13, Node.js 22, and the existing dependency lockfiles. The check commands pass in Linux containers; the first hosted run is pending.

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

**23 backend tests and 10 frontend tests pass on Windows and in Linux containers.** The frontend production build also passes in both environments. Backend coverage includes the supplied values, selected-field execution and order, CLP/USD variations, signing dates, textless documents, result-model invariants, multipart validation, error mapping, and independent requests. Frontend tests mock `fetch` and cover form validation, loading controls, request context, found/missing results, retry behavior, both 422 response shapes, unavailable servers, and unreadable responses.

The browser walkthrough covered the three canonical PDFs, a subset submitted by keyboard, a textless-PDF error, desktop/mobile layouts, and long-value wrapping through both startup paths. Final verification used alternate host ports because Windows reserved 5173; details and limits are recorded in [WES-04](planning/04-ui.md#completion-evidence). The backend suite emits two upstream Starlette/AnyIO deprecation warnings; these do not fail the tests. The test counts remain within the limits of 25 backend and 10 frontend tests.

Setup verification is recorded in [WES-01](planning/01-foundation.md#completion-evidence). Backend lint commands are `python -m ruff check .` and `python -m ruff format --check .` from `backend/` using its virtual environment, or their equivalents via `docker compose exec backend`.

## Delivery plan

| Ticket | Outcome | Planned budget | Approximate time spent |
| --- | --- | --- | --- |
| [WES-01](planning/01-foundation.md) | Project setup and reproducible local startup | 1 hour | 2 hours |
| [WES-02](planning/02-extraction.md) | Selected-field extraction and missing semantics | 2 hours | 1 hour |
| [WES-03](planning/03-api.md) | Validated PDF upload API | 2 hours | 1 hour |
| [WES-04](planning/04-ui.md) | Complete user flow and final verification | 3 hours | 2 hours |
| [WES-05](planning/05-ci-and-tenant-design.md) (optional) | CI and tenant configuration design note | 1 hour | Not yet recorded |

The original WES-01 through WES-04 plan budgeted **8 hours**; actual working time through WES-04 is approximately **6 hours**, based on the developer's retrospective estimate across planning, implementation, review, and verification. WES-05 allocates **1 hour** of the remaining allowance, for a projected total of **7 hours**. These are estimates rather than precise time logs. The first substantive Git commit contains planning and setup before feature implementation, and later commits reference their ticket IDs.

See [AI_USAGE.md](AI_USAGE.md) for tools used, a changed/rejected suggestion, and verification performed.
