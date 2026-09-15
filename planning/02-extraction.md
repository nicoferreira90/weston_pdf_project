# WES-02: Extract selected contract fields with trustworthy result semantics

**Status:** Implemented and verified

**User outcome:** A user receives values or explicit missing results for exactly the fields requested.  
**Time budget:** 2 hours.

## Context and assumptions

- The PDFs use Spanish prose, accented names, wrapped lines, UF prices, and explicit signing text. A heading such as `Precio` can be present even when the price is absent.
- Chosen extraction approach: deterministic local text parsing for the supplied contract style. It requires no credentials and fits the time budget. Document its limited language/layout coverage rather than claiming general contract understanding.
- Parse text and contextual patterns, never filenames or known fixture values. Expected sample values belong only in tests and documentation.
- Preserve source values as strings, including accents and monetary units. Normalize whitespace, but do not convert UF, reinterpret number separators, or convert dates to a different format.
- Price matching supports explicit `UF`, `CLP`, and `USD` prefixes in the same purchase-price wording. A bare `$` does not identify one of these currencies; currency inference is outside scope.
- Assume well-formed PDFs. Malformed and non-PDF inputs are not specially handled; unexpected reader errors still propagate instead of producing missing results.

## Scope

- `app/extraction/models.py`: define the four supported field IDs and validated result types.
- `app/extraction/pdf.py`: read PDF bytes and extract text; report textless documents as processing failures and let other reader errors propagate.
- `app/extraction/service.py`: expose a small boundary accepting PDF bytes and the selected field IDs, returning a structured result collection. Keep it independent of FastAPI, HTTP, filenames, and React.
- Accept the validated selection from the API and execute field-specific extraction only for selected fields. Reading shared PDF text is necessary; extracting all four values and filtering afterward does not satisfy this requirement.
- Use contextual rules for purchaser identity, total purchase price, signing date, and the property's address. Prefer explicit signing text over other dates; do not mistake a seller, incidental amount, or party address for a requested value.
- Return one result per requested field, in request order:

  ```json
  {
    "results": [
      {"field_id": "purchase_price", "status": "found", "value": "UF 8.500"},
      {"field_id": "property_address", "status": "missing", "value": null}
    ]
  }
  ```

- Use the result models to enforce `found` with a nonempty string and `missing` with `null`.
- Report processing failures separately from results, using a simple exception the API can handle. A readable text document without any selected values may legitimately return all missing.
- Keep document contents and extracted values out of logs. Do not retain documents in application storage; close parser resources after each request.

## Explicit non-goals

- No OCR, scanned-document support, legal interpretation, inference of unstated values, currency conversion, confidence scores, or universal Spanish/English template coverage.
- No LLM integration or external extraction service in this implementation.
- No API transport or UI presentation in this ticket.
- No custom malformed/non-PDF validation or associated test cases.

## Acceptance criteria

- [x] Only selected field extractors execute, and returned IDs exactly match the requested selection in order.
- [x] The supplied fixtures produce this status matrix when all fields are selected:

  | Document | Purchaser | Price | Signing date | Property address |
  | --- | --- | --- | --- | --- |
  | `complete-purchase-contract.pdf` | found | found | found | found |
  | `missing-property-address.pdf` | found | found | found | missing |
  | `missing-price-and-date.pdf` | found | missing | missing | found |

- [x] Expected values reflect the actual fixtures: the complete contract contains Ana María Pérez Soto, `UF 8.500`, `1 de septiembre de 2026`, and Avenida Apoquindo 4500, departamento 1201, comuna de Las Condes, Santiago.
- [x] The address-missing fixture contains Diego Andrés Morales Vega, `UF 6.250`, and `10 de septiembre de 2026`; `Santiago de Chile` in its opening is not treated as a property address.
- [x] The price/date-missing fixture contains Camila Fernanda Rojas Silva and Pasaje Los Alerces 1840, comuna de Ñuñoa, Santiago. `Fecha de firma: pendiente` is missing, and its address number is not a price.
- [x] Wrapped names and addresses retain their full content, without neighboring headings or clauses. Sentence-ending punctuation may be trimmed consistently.
- [x] Explicit UF, CLP, and USD prices in the supported clause are extracted with their original unit, amount, and separators, without conversion.
- [x] Renaming a file has no effect; changing synthetic document values changes the extracted values.
- [x] An incidental date does not override an explicit signing date; a pending signing date is not replaced with an unrelated date.
- [x] Textless PDFs cause processing errors. A readable document lacking the selected fields succeeds with missing results.

## Dependencies and order

Depends on WES-01. Establish the models and service interface before WES-03. Keep extraction implementation replaceable without changing the HTTP contract.

Suggested commit: `feat(WES-02): extract selected fields from PDF text`.

## Implementation sequence

1. **Models:** define the four field IDs, one result model, and a response containing the results list. Enforce the status/value relationship with straightforward model validation. Request-selection validation remains in WES-03.
2. **PDF reader:** accept bytes, use pypdf to read page text in memory, join the text, and close resources. Raise a simple document-processing exception for a wholly textless document. Other reader errors propagate separately; assume well-formed input.
3. **Field matchers:** normalize whitespace while preserving source characters. Use case-insensitive, contextual matching in four small functions, each returning a value or no match:

   | Field | Matching boundary |
   | --- | --- |
   | Purchaser | Name in the introductory purchaser clause, ending before `como comprador/compradora`; omit `don/doña`. |
   | Price | Explicit `UF`, `CLP`, or `USD` followed by an amount in the total purchase-price clause. |
   | Signing date | `Firmado el …` or `Fecha de firma: …` followed by a Spanish date; never substitute an unrelated date for a pending signing date. |
   | Property address | Address following the property's `ubicado/ubicada en …` wording, ending at the sentence boundary; preserve apartment and municipality details and `Av.`, `Avda.`, `Depto.`, and `Dpto.` abbreviations. |

4. **Service:** accept document bytes and selected field IDs, read text once, and dispatch only the selected matchers through a small field-to-function mapping. Build independent results in request order. No service class or general parser framework is needed.
5. **Tests:** add the fixture cases alongside implementation, then the focused selection, synthetic-value, and failure cases below. Use real PDFs for reader checks and controlled text at the reader boundary for synthetic matching variations; add no PDF-generation dependency.
6. **Verification and documentation:** run extraction tests, backend lint, and formatting checks; verify fixture access locally and in Docker. Update this ticket, README limitations, and AI_USAGE with actual results.

## Proposed test plan

- In `backend/tests/test_extraction.py`, test each supplied PDF once with all fields selected, asserting values and found/missing statuses. These fixtures already cover accented and wrapped values, absent-value prose, and the distinction between purchaser and seller.
- Test two representative selections: one field and a subset containing both a found and a missing field. Assert exactly the selected IDs are returned, and use one focused spy to verify unselected extractors are not called.
- Add two synthetic variations, one with CLP and one with USD, changing names, prices, dates, and addresses in the same wording. Include an unrelated date to check preference for the explicit signing date, an extra property sentence to check address boundaries, and a renamed next heading. Preserve abbreviation coverage. UF is covered by the supplied fixtures. The service accepts bytes, so filenames cannot drive its results.
- Add one pending-signing-date case containing another date elsewhere; the selected signing date must remain missing.
- Cover a textless PDF and readable text without the selected fields to distinguish failures from legitimate missing results. Also reject inconsistent found/missing model values.
- The implemented suite totals **12 extraction cases**: three fixtures, two selections, two currency variations, one pending-date case, two document failure/missing cases, and two model-invariant cases. Malformed-file handling is outside scope. WES-02 and WES-03 share the maximum of **25 backend tests**, counting parameterized cases individually. Selection validation belongs to WES-03; it is not repeated here.

## Completion evidence

- `python -m pytest tests/test_extraction.py -q -p no:cacheprovider`: **12 passed** in the Windows virtual environment.
- `docker compose exec -T backend python -m pytest tests/test_extraction.py -q -p no:cacheprovider`: **12 passed** in the Linux container, using the same source and synthetic fixtures.
- Backend Ruff lint and formatting checks passed for the implementation after formatting the test file.
- Tests were first run against the placeholders and failed at the missing model import, then passed after implementation. No new dependencies were added.
- `extract_fields(document, selected_fields)` accepts bytes and an already validated field selection. It has no filename or HTTP dependency. API and UI work remain in WES-03 and WES-04.
- The existing synthetic cases reproduce adjacent-sentence capture and dependence on the next heading before the address fix. Both pass with sentence-bounded matching while preserving `Av.`; the total remains 12 tests.
- Matching is limited to the documented Spanish contract clauses. Different wording may return missing; a missing result is not proof that the document lacks the field. Signing dates remain source strings without calendar validation.
- The 2-hour figure is the planned budget; exact active working time was not separately tracked.
