# Contributing

Contributions are welcome when they improve reproducibility, data quality, or external validation.

## Requirements

- Do not submit confidential, employer-owned, personal, or access-controlled data.
- Do not commit search-provider payloads or third-party row-level datasets without an explicit compatible license.
- Every proposed company or relation must include an original evidence URL and retrieval date.
- Distinguish source records, facilities, companies, relations, and SME status.
- Add or update tests for parser and entity-resolution changes.
- Document material methodology changes in the release notes.

Run before opening a pull request:

    make test
    make preflight

