# WES-03: Expose a validated PDF extraction endpoint

**Status:** Planned  
**User outcome:** A user can submit one PDF and a field selection and receive either a reliable result or an actionable error.  
**Time budget:** 2 hours.

## Context and assumptions

- The API handles one extraction synchronously. It has no server-side request history or mutable global field selection.
- The API owns upload validation and HTTP error mapping; WES-02 owns document parsing and extraction semantics.
- Keep validation focused on the required single-PDF workflow; custom size/page policies and production hardening are outside this ticket.

## Scope

- `app/main.py`: register extraction routes on the existing FastAPI app. Reuse WES-01's Vite API proxy for frontend access in local and Docker development.
- `app/config.py`: add backend configuration only if required by the implementation.
- `app/api/extraction.py`: implement `POST /api/extractions` using multipart form data with one `file` part and repeated `selected_fields` parts.
- Accept a single file and one to four distinct known field IDs. Reject empty, duplicate, or unknown selections and missing/empty files using straightforward request validation.
- Validate actual PDF readability through the service; a `.pdf` filename alone does not establish valid content.
- Close upload resources on success and failure; do not save documents to a persistent upload directory.
- Capture the selection for this request, invoke the service, and return the WES-02 response shape with HTTP 200 on success.
- Use FastAPI's standard validation responses and a simple `detail` message for processing errors; a custom error framework is unnecessary. Document these responses for the frontend:

  | HTTP status | Meaning |
  | --- | --- |
  | 422 | Invalid selection, missing/empty file, or a document that cannot be read as a supported text PDF |
  | 500 | Unexpected extraction failure, with a generic message |

- Include readable recovery guidance without exposing stack traces, PDF text, extracted values, or internal filesystem paths. Do not log document contents or applicant information.
- Run blocking PDF work using FastAPI's appropriate synchronous/thread execution path rather than blocking an async event loop directly.

## Explicit non-goals

- No authentication, persistence, job polling, queues, streaming progress, batch uploads, public deployment, or elaborate request abstraction layers.
- No endpoint for configuring arbitrary fields; the four available field IDs are fixed.
- No external-service integration, custom upload-limit policies, or concurrency/load testing.

## Acceptance criteria

- [ ] A valid PDF plus a valid selection returns HTTP 200 with exactly one result per selected field in request order.
- [ ] All-missing results from a successfully processed document are HTTP 200; processing errors are non-200 and contain no misleading results array.
- [ ] Invalid selection or upload requests fail clearly before invoking extraction where validation permits.
- [ ] Missing/empty files and unreadable/textless documents produce clear request errors.
- [ ] A filename ending in `.pdf` does not make arbitrary bytes a valid upload, and changing a valid PDF's filename does not change extraction.
- [ ] Repeating the flow with a different selection does not change the first request's results.
- [ ] Upload resources are closed after failure as well as success, and error messages/logging do not reveal document data.
- [ ] The frontend can reach the API using both the documented local development and Docker Compose setup.
- [ ] README documents multipart field names, the response contract, and errors.

## Dependencies and order

Depends on WES-01 setup and WES-02 models/service. WES-04 consumes this contract.

Suggested commit: `feat(WES-03): add validated extraction upload API`.

## Proposed test plan

- In `backend/tests/test_api.py`, make one real-service request with a supplied PDF and a selection containing both found and missing fields. Verify the multipart contract and response without repeating the full extraction fixture suite.
- Use a fake service for invalid selections (empty, unknown, duplicate) and missing/empty files; assert these requests fail before extraction.
- Check three service outcomes: valid all-missing results return HTTP 200, a document-reading failure returns HTTP 422, and an unexpected exception returns HTTP 500. Failures must not produce missing-field results.
- Submit two successive requests with different selections and verify each retains its own results.
- Aim for roughly 10 API tests within the shared **25-backend-test maximum**, counting parameterized cases individually. Use code review to check resource cleanup and absence of document logging; skip a separate logging suite and concurrency harness.

## Completion evidence

Record actual commands, results, time spent, and any changes to the agreed API contract when implemented.
