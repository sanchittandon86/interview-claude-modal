# 3. Test Cases

**Generate:** Wrote 34 test cases (TC-x.x), mapped 1:1 to the 9 user stories' acceptance criteria — covering normal paths, error paths (missing required fields, updating a nonexistent product), and edge cases (empty search, no matches, single result, empty recommendation set, rapid/high-volume events).

**Validate:** Checked against:
- **Completeness** — Pass. Every user story had at least one test case validating its primary functionality.
- **Validity** — Pass. Each test case simulated a real, spec-described action; nothing invented beyond what the acceptance criteria stated.
- **Coverage** — Pass. Error-handling cases exist only where a user story's acceptance criteria actually defined a failure condition (US-1, US-2); edge cases exist wherever a boundary condition was described.

**Outcome:** 34 approved test cases became the executable specification: code in the next phases was written to satisfy them, and running the full suite became the acceptance gate for "done" at every later stage (including after UI changes).
