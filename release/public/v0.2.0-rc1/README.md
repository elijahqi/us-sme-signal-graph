# US-SME Signal Graph v0.2.0-rc1

This release contains 30 provider-neutral, independently verified U.S. semiconductor supplier candidates that are absent from the frozen 50-company SIA Equipment/Materials comparison baseline.

Files:

- `verified_supplier_candidates.csv`: company, capability, source URLs, hashes, and evidence status;
- `pilot_metrics.json`: aggregate retrieval, verification, precision, lift, and gate results;
- `release_manifest.json`: scope and core file hashes;
- `SHA256SUMS`: integrity manifest.

The release does not contain provider payloads, snippets, ranks, fetched page text, or row-level SIA-derived data. `probable_sme` is non-authoritative and does not mean SBA certification. There are no `confirmed_sme` rows.

This is a release candidate because independent double annotation, agreement, and entity-resolution audit gates are incomplete. See `docs/pilot_results_v0_2_rc1.md` in the repository.
