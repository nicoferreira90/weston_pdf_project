# WES-03: Expose a validated PDF extraction endpoint

**Status:** Implemented and verified

**User outcome:** A user can submit one PDF and a field selection and receive either a reliable result or an actionable error.  
**Time budget:** 2 hours.

## Context and assumptions

- The API handles one extraction synchronously. It has no server-side request history or mutable global field selection.
- The API owns upload validation and HTTP error mapping; WES-02 owns document parsing and extraction semantics.
- Keep validation focused on the required single-PDF workflow; custom size/page policies and production hardening are outside this ticket.
- Assume well-formed PDFs. Malformed or non-PDF files are not specially handled; unexpected reader failures use the generic processing-error response.

## Scope

- `app/main.py`: register extraction routes on the existing FastAPI app. Reuse WES-01's Vite API proxy for frontend access in local and Docker development.
- `app/api/extraction.py`: implement `POST /api/extractions` using multipart form data with one `file` part and repeated `selected_fields` parts.
- Accept a single file and one to four distinct known field IDs. Reject empty, duplicate, or unknown selections and missing/empty files using straightforward request validation.
- Pass PDF bytes to the extraction service and handle its textless-document error separately from unexpected processing failures.
- Rely on FastAPI's request cleanup to close uploads on success and failure; do not save documents to a persistent upload directory.
- Capture the selection for this request, invoke the service, and return the WES-02 response shape with HTTP 200 on success.
- Use FastAPI's standard validation responses and a simple `detail` message for processing errors; a custom error framework is unnecessary. Document these responses for the frontend:

  | HTTP status | Meaning |
  | --- | --- |
  | 422 | Invalid selection, missing/empty file, or `DocumentProcessingError` for a textless PDF |
  | 500 | Unexpected extraction or reader failure, with a generic message |

- Include readable recovery guidance without exposing stack traces, PDF text, extracted values, or internal filesystem paths. Do not log document contents or applicant information.
- Run blocking PDF work using FastAPI's appropriate synchronous/thread execution path rather than blocking an async event loop directly.

## Explicit non-goals

- No authentication, persistence, job polling, queues, streaming progress, batch uploads, public deployment, or elaborate request abstraction layers.
- No endpoint for configuring arbitrary fields; the four available field IDs are fixed.
- No external-service integration, custom upload-limit policies, or concurrency/load testing.
- No custom malformed/non-PDF validation or associated test cases.

## Acceptance criteria

- [x] A valid PDF plus a valid selection returns HTTP 200 with exactly one result per selected field in request order.
- [x] All-missing results from a successfully processed document are HTTP 200; processing errors are non-200 and contain no misleading results array.
- [x] Invalid selection or upload requests fail clearly before invoking extraction where validation permits.
- [x] Missing/empty files and textless PDFs produce clear HTTP 422 errors; unexpected reader failures produce a generic HTTP 500 error without missing-field results.
- [x] Changing a valid PDF's filename does not change extraction.
- [x] Repeating the flow with a different selection does not change the first request's results.
- [x] Upload resources are closed after failure as well as success, and error messages/logging do not reveal document data.
- [x] The frontend can reach the API using both the documented local development and Docker Compose setup.
- [x] README documents multipart field names, the response contract, and errors.

## Dependencies and order

Depends on WES-01 setup and WES-02 models/service. WES-04 consumes this contract.

Suggested commit: `feat(WES-03): add validated extraction upload API`.

## Proposed test plan

- In `backend/tests/test_api.py`, make one real-service request with a supplied PDF and a selection containing both found and missing fields. Verify the multipart contract and response without repeating the full extraction fixture suite.
- Use a fake service for invalid selections (empty, unknown, duplicate, too many) and missing/empty files; assert these requests fail before extraction.
- Check three service outcomes: valid all-missing results return HTTP 200, a textless-document `DocumentProcessingError` returns HTTP 422, and an unexpected exception returns HTTP 500. Failures must not produce missing-field results.
- Submit two successive requests with different selections and verify each retains its own results.
- The suite contains **11 API tests**, bringing the backend total to **23**, within the shared maximum of 25. Parameterized cases count individually. Use code review to check resource cleanup and absence of document logging; skip a separate logging suite and concurrency harness.

## Completion evidence

- `python -m pytest -q -p no:cacheprovider`: **23 passed** in the Windows virtual environment.
- `docker compose exec -T backend python -m pytest -q -p no:cacheprovider`: **23 passed** in the Linux container.
- Backend Ruff lint and formatting checks passed. The pinned test dependencies emit two upstream deprecation warnings from Starlette's HTTPX and AnyIO integrations; these do not fail the tests.
- The API tests initially failed against the placeholder route, then passed after implementation. A renamed real fixture verifies mixed found/missing results; fakes isolate request validation and error mapping.
- Real multipart uploads succeeded directly and through Vite in Compose (ports 8000/5173). A real blank-page PDF returned the documented HTTP 422 response through both paths. OpenAPI exposes the multipart endpoint.
- Temporary local servers on ports 8001/5174 also accepted an extraction upload directly and through Vite, then were stopped. Alternate ports avoided conflicting with the running Compose stack.
- Resource review: FastAPI's multipart request cleanup closes uploads after success, handler failures, and validation failures before route execution. The handler logs only the exception type on unexpected failures and returns fixed processing-error messages. The existing error tests verify that exception messages and tracebacks are not logged.
- The synchronous route keeps blocking file reads and PDF parsing in FastAPI's thread pool. No new dependencies or backend settings were required; the existing Vite proxy handles frontend access.
- The 2-hour figure is the planned budget; exact active working time was not separately tracked. The user interface remains in WES-04.
