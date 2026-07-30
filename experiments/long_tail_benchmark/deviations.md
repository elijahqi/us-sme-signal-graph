# Formal-run deviations

## DEV-001: URL parser failure before evidence fetch

- Run: `formal_v0_3`
- Affected attempted queries: `LTQ0001` through `LTQ0010`
- Stage: first formal batch, before any original source page was fetched
- Symptom: both providers returned 10 web results per query, but the in-process URL canonicalizer produced zero URLs
- Cause: the orchestration isolate did not provide the assumed URL parser; the exception was incorrectly converted to an empty URL
- Evidence impact: none of the attempted provider results entered the research corpus; no source pages were fetched and the zero-URL aggregates were isolated as invalid
- Corrective action: use a dependency-free URL canonicalizer and fail closed whenever a provider reports results but yields zero parsed result URLs
- Rerun rule: rerun the same frozen queries under the same parameters; do not alter query strings or replace results

## DEV-002: PTY did not close the processor input stream

- Run: `formal_v0_3`
- Affected attempted queries: `LTQ0001` through `LTQ0010` rerun
- Stage: after valid URL parsing, before original source fetching
- Symptom: 118 query-level union URLs were produced, but the local processor remained blocked reading interactive stdin and did not create a manifest
- Cause: the PTY transport rendered an EOF control character as terminal input rather than closing the stream
- Evidence impact: no source page or aggregate result entered the formal corpus; the waiting process was terminated by exact PID
- Corrective action: pass the rights-safe NDJSON batch to a noninteractive processor through an encoded argument, with explicit size and decode validation
- Rerun rule: rerun the same frozen queries under the same parameters; do not alter query strings or replace results

