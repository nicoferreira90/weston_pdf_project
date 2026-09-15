# WES-02: Extract selected contract fields with trustworthy result semantics

**Status:** Planned  
**User outcome:** A user receives values or explicit missing results for exactly the fields requested.  
**Time budget:** 2 hours.

## Context and assumptions

- The PDFs use Spanish prose, accented names, wrapped lines, UF prices, and explicit signing text. A heading such as `Precio` can be present even when the price is absent.
- Chosen extraction approach: deterministic local text parsing for the supplied contract style. It requires no credentials and fits the time budget. Document its limited language/layout coverage rather than claiming general contract understanding.
- Parse text and contextual patterns, never filenames or known fixture values. Expected sample values belong only in tests and documentation.
- Preserve source values as strings, including accents and monetary units. Normalize whitespace, but do not convert UF, reinterpret number separators, or convert dates to a different format.

## Scope

- `app/extraction/models.py`: define the four supported field IDs and validated result types.
- `app/extraction/pdf.py`: read PDF bytes and extract text; report unreadable or textless documents as processing failures.
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

## Acceptance criteria

- [ ] Only selected field extractors execute, and returned IDs exactly match the requested selection in order.
- [ ] The supplied fixtures produce this status matrix when all fields are selected:

  | Document | Purchaser | Price | Signing date | Property address |
  | --- | --- | --- | --- | --- |
  | `complete-purchase-contract.pdf` | found | found | found | found |
  | `missing-property-address.pdf` | found | found | found | missing |
  | `missing-price-and-date.pdf` | found | missing | missing | found |

- [ ] Expected values reflect the actual fixtures: the complete contract contains Ana María Pérez Soto, `UF 8.500`, `1 de septiembre de 2026`, and Avenida Apoquindo 4500, departamento 1201, comuna de Las Condes, Santiago.
- [ ] The address-missing fixture contains Diego Andrés Morales Vega, `UF 6.250`, and `10 de septiembre de 2026`; `Santiago de Chile` in its opening is not treated as a property address.
- [ ] The price/date-missing fixture contains Camila Fernanda Rojas Silva and Pasaje Los Alerces 1840, comuna de Ñuñoa, Santiago. `Fecha de firma: pendiente` is missing, and its address number is not a price.
- [ ] Wrapped names and addresses retain their full content, without neighboring headings or clauses. Sentence-ending punctuation may be trimmed consistently.
- [ ] Renaming a file has no effect; changing synthetic document values changes the extracted values.
- [ ] An incidental date does not override an explicit signing date; a pending signing date is not replaced with an unrelated date.
- [ ] Corrupt or textless PDFs cause processing errors. A readable document lacking the selected fields succeeds with missing results.

## Dependencies and order

Depends on WES-01. Establish the models and service interface before WES-03. Keep extraction implementation replaceable without changing the HTTP contract.

Suggested commit: `feat(WES-02): extract selected fields from PDF text`.

## Proposed test plan

- In `backend/tests/test_extraction.py`, test each supplied PDF once with all fields selected, asserting values and found/missing statuses. These fixtures already cover accented and wrapped values, absent-value prose, and the distinction between purchaser and seller.
- Test two representative selections: one field and a subset containing both a found and a missing field. Assert exactly the selected IDs are returned, and use one focused spy to verify unselected extractors are not called.
- Add one synthetic variation with changed values and an unrelated date to check content-based extraction and preference for the explicit signing date. The service accepts bytes, so filenames cannot drive its results.
- Cover corrupt PDF bytes, a textless PDF, and readable text without the selected fields to distinguish failures from legitimate missing results.
- Keep tests local and deterministic. Aim for roughly 10 extraction tests; WES-02 and WES-03 share the AGENTS.md maximum of **25 backend tests**, counting parameterized cases individually. This is a ceiling, not a target. Selection validation belongs to WES-03; do not repeat it here.

## Completion evidence

Record actual commands, results, time spent, and remaining parser limitations when implemented.
