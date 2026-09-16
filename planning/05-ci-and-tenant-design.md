# WES-05: Run checks in CI and describe tenant field versioning

**Status:** Complete

**User outcome:** A reviewer can see automated checks on changes and understand how bank-specific field configuration could evolve without changing historical results.

**Time budget:** 1 hour for both optional deliverables, using the remaining time after approximately 6 hours on WES-01 through WES-04.

**Approximate actual time:** 1 hour, reported by the developer; approximately 7 hours across all five tickets.

## Context and assumptions

- The core workflow is complete. Both deliverables are optional extensions named in the candidate brief.
- The repository is hosted on GitHub. Existing lockfiles and commands already support Python 3.13 and Node.js 22.
- Tenant configuration is a design note only; the application continues to use its four fixed fields without tenants or persistent history.

## Scope

- Add `.github/workflows/tests.yml`, triggered by pushes and pull requests, with independent backend and frontend jobs on Ubuntu.
- Backend: install `requirements.lock` and the project with its development extra, then run Ruff lint, Ruff formatting checks, and the existing pytest suite.
- Frontend: install with `npm ci`, run the existing Vitest suite once, and build the production frontend, including TypeScript checking.
- Give the workflow read-only repository permissions. A failed install, check, test, or build must fail its job.
- As a second deliverable, add a short README design note separating stable field IDs from immutable, versioned bank configurations. Describe available fields and labels, retained historical versions, and the tenant/configuration version/selected IDs recorded with a request. Identify the parser/schema version when extraction meaning changes.
- Describe how the UI receives a configuration version and submits it back, how the API validates it, and how activation and rollback work independently per bank. Choose an explicit stale-version policy; never silently substitute the new active version.
- Mark the tenant design as unimplemented. Add a README status badge only after the first successful hosted CI run.

## Explicit non-goals

- No OS/version matrix, coverage thresholds, Docker image builds, custom caching, deployment, or deliberately failing branch.
- No new application tests, dependencies, tenant code, database, authentication, or configuration endpoints.

## Acceptance criteria

- [x] A push or pull request is configured to run both jobs with the specified runtimes and lockfiles.
- [x] Backend lint, formatting checks, 23 backend tests, 10 frontend tests, and the frontend build pass using the workflow's check commands; failures are not suppressed.
- [x] A hosted GitHub Actions run confirms both jobs passed and the expected test counts, then the README links its status badge.
- [x] README explains configuration identity, immutable versions, stable field IDs, retained historical meaning, request validation, stale-version handling, activation, and rollback, and clearly labels the design as unimplemented.
- [x] AI_USAGE records the work and distinguishes local/container verification from an actual hosted CI run.

## Dependencies and order

Depends on completed WES-01 through WES-04. CI and the design note can be reviewed independently.

Suggested commits:

1. `ci(WES-05): run backend and frontend checks on GitHub Actions`
2. `docs(WES-05): describe tenant field configuration versioning`

## Proposed verification

- Review workflow paths, triggers, action inputs, runtime versions, and failure propagation. Run the existing check commands in Linux; do not add tests that duplicate workflow syntax.
- After the workflow is committed and pushed, inspect the GitHub Actions run for both jobs and their test counts. Until then, do not claim hosted CI passes or show a success badge.
- Review the tenant note against two examples: changing a bank's available fields leaves a past result unchanged, and submitting a form opened before a configuration update follows the documented stale-version policy.

## Completion evidence

- Added the workflow after this ticket. Reviewed triggers, working directories, Python/Node versions, lockfile installs, read-only permissions, and separate check steps with no failure suppression. Action versions and inputs were checked against the official action documentation.
- The existing Linux containers passed the workflow's backend commands (`python -m ruff check .`, `python -m ruff format --check .`, `python -m pytest -q`) and frontend commands (`npm test -- --run`, `npm run build`): 23 backend tests, 10 frontend tests, lint, formatting, TypeScript, and production build. Backend tests retain the two documented upstream deprecation warnings.
- The developer confirmed that the hosted CI workflow passed. The workflow runs the existing 23 backend and 10 frontend tests; those counts were independently verified in Linux containers. Hosted logs were not separately retrieved by the assistant. README now links the live workflow badge and run history.
- Added the README's [tenant configuration design](../README.md#tenant-field-configuration-proposed-design), explicitly marked unimplemented. Reviewed the two examples: bank A's configuration change preserves version 1 results and leaves bank B unaffected; a stale version 1 form receives HTTP 409 before extraction. Accepted requests pin their configuration for the duration of processing.
- Actual time: approximately 1 hour for WES-05 and 7 hours overall, as reported by the developer. No tenant application code, dependencies, or automated tests were added for the design note.
