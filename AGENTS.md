1. `purchase-contract-field-extraction-candidate-brief.md` is the source of truth for project requirements. When planning or implementing behavior, consult it before adding requirements not stated there.
2. Above everything else, prioritize the clarity and reliability of the required core workflow.
3. Keep the implementation simple. Do not over-engineer.
4. Tests should cover requirements and representative edge cases, not exhaustive combinations or hypothetical production scenarios.
5. Do not invent production requirements that are not present in the candidate brief.
6. Prefer straightforward implementations over defensive abstractions or unnecessary architectural layers.
7. Keep deterministic extraction scoped to the supplied text-based purchase-contract problem; do not attempt to build a general document extraction framework.
8. Implement optional features only after all required behavior and tests are complete.
9. Stop when the acceptance criteria are satisfied.
10. Respect the assignment's 6–8 hour total working-time budget when making implementation decisions.
11. Let's keep the total amount of tests at a maximum of 25 meaningful backend tests and 10 focused frontend tests.
12. Do not create Git commits; the developer makes all commits. You may suggest commit messages.