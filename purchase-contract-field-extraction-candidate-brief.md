# Weston engineering take-home: configurable purchase-contract extraction

## Purpose

This exercise is designed to show us how you turn a product requirement into
structured engineering work and working software. We will review your problem
decomposition, technical decisions, testing process, implementation, and ability
to explain the result.

The application is an assessment only. It will not be used in Weston's product.
All sample documents contain synthetic information.

## Time and use of AI tools

You will have 48 hours from receipt of the assignment. Please limit your actual working time between 6-8 hours. A focused, incomplete submission with clear tradeoffs is better than an undocumented all-nighter.

You may use coding agents, code-completion tools, LLMs, documentation, and other
normal development tools. Add an `AI_USAGE.md` file that briefly explains:

- Which tools you used.
- What you used them for.
- One generated suggestion you changed or rejected, and why.
- How you verified code you did not write manually.

You remain responsible for every part of the submission and should be able to
explain it during the follow-up discussion.

## Scenario

A Weston user reviews purchase contracts submitted as part of a mortgage
workflow. Before uploading a contract, the user chooses which fields Weston
should extract.

The available fields are fixed:


| Field ID           | Label            | Meaning                                                          |
| ------------------ | ---------------- | ---------------------------------------------------------------- |
| `purchaser_name`   | Purchaser name   | The primary purchaser's full name                                |
| `purchase_price`   | Purchase price   | The price stated in the contract, including its currency or unit |
| `contract_date`    | Contract date    | The date on which the purchase contract was signed               |
| `property_address` | Property address | The address of the property being purchased                      |


After the user uploads a PDF, the application extracts only the selected fields
and displays the result. If a selected field cannot be found in a successfully
processed document, the application clearly flags that field as missing.

The supplied PDFs are synthetic, text-based documents. They are intended to
exercise the application flow, not to benchmark OCR or model accuracy.

## Required user flow

1. The user opens the application and sees the four available fields.
2. The user selects one or more fields.
3. The user uploads one PDF purchase contract and starts extraction.
4. The application processes the document using the selected field list.
5. The user sees one result for every selected field:
  - `found`, with the extracted value; or
  - `missing`, with a clear visual flag.
6. Fields the user did not select are not extracted or displayed.
7. The user can repeat the flow with a different document and field selection.

The selected fields belong to that individual extraction request. A later
selection must not change the meaning of a previously completed request.

## Extraction boundary

Keep document extraction behind a small interface or service boundary. At a
minimum, that boundary should accept the document and selected field IDs and
return structured results similar to:

```json
{
  "results": [
    {
      "field_id": "purchase_price",
      "status": "found",
      "value": "UF 8,500"
    },
    {
      "field_id": "property_address",
      "status": "missing",
      "value": null
    }
  ]
}
```

You may implement extraction with a small LLM model API. If you use an external service:

- Do not commit credentials.
- Make the application usable without our access to your account.
- Keep automated tests deterministic by replacing the external call with a
fake or mock.
- Validate external output before it enters the rest of the application.

Do not hardcode results based on the supplied filenames or exact expected
values.

## Important result semantics

`missing` means the application successfully processed the document but could
not locate that selected field.

A file-reading error, invalid model response, timeout, or other processing
failure is not the same as a missing field. Show those failures separately and
do not turn every selected field into a misleading `missing` result.

## Planning and tickets

Before implementing the feature, create between three and six structured
tickets under `planning/`. Markdown files are sufficient; no external project
management account is required.

Your first substantive Git commit should contain the tickets and project setup,
before the feature implementation. Each ticket should include:

- A short title and user outcome.
- Context and assumptions.
- Scope and explicit non-goals.
- Acceptance criteria, including at least one failure or edge case.
- Dependencies or ordering constraints.
- A proposed test plan.

Reference the relevant ticket in later commit messages or pull-request-style  
notes. We are interested in whether the work is divided into understandable,  
reviewable increments.



## Technical constraints

- Build a greenfield application.
- Use Python with FastAPI for the backend.
- Use React or Next.js for the user interface.
- No authentication, multi-tenancy, cloud deployment, database integration, background queue, or production OCR pipeline is required.
- Keep source documents private to the application. Do not commit uploaded  
documents or extracted applicant information to logs.

You may use different technologies if you explain the reason before beginning
in your planning notes. 

Sample documents

The assignment includes:

- `complete-purchase-contract.pdf`: all four fields are present.
- `missing-property-address.pdf`: the property address is absent.
- `missing-price-and-date.pdf`: the purchase price and contract date are absent.

Your application should work with these files. You may add synthetic test files
of your own.

## Expected submission

Send us a Git repository containing:

- The running application.
- The planning tickets.
- `README.md` with setup, commands, architecture, assumptions, and known gaps.
- `AI_USAGE.md`.

Do not include API keys, real borrower documents, or real personal information.

## Follow-up discussion

In a 45-minute review, you will demonstrate the required flow and explain:

- How you decomposed the problem.
- How your data moves through the application.
- Why you chose the extraction boundary and data contracts you used.
- How your tests influenced the design.
- What you would change before using the application with real mortgage files.

We will care more about the clarity and reliability of the core workflow than
visual polish or optional infrastructure.

## Optional extensions

Only attempt these after the required behavior and tests are complete:

- Display a supporting text snippet or page reference for found values.
- Process uploads asynchronously with visible status and retry behavior.
- Preserve a history of extraction requests.
- Add CI that runs the test suite.
- Describe how field configuration would be versioned for multiple bank tenants.

