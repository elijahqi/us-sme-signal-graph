# US-SME Signal Graph

Reproducible reconstruction and search-uplift evaluation for a provenance-aware U.S. semiconductor supplier graph.

## Current milestone

Build and freeze **Baseline v0.1-SIA** without Brave or You search results. It uses the public, structured U.S. Semiconductor Ecosystem Map maintained by the Semiconductor Industry Association (SIA).

This is not the lost original paper snapshot. The paper reported 664 mixed-type entities and 542 relations from 48 seeds, but did not release the underlying entity/relation files. Baseline v0.1-SIA is a clean reconstruction starting point whose scope and limitations are explicit.

## Quick start

    python3 scripts/build_baseline.py
    python3 scripts/validate_baseline.py

To rebuild from the frozen local source page without a network request:

    make rebuild-frozen

Outputs are written to data/processed/baseline_v0_1_sia/:

- companies.csv
- facilities.csv
- relations.csv
- source_pages.csv
- company_aliases.csv
- supplier_baseline.csv
- baseline_manifest.json
- source_snapshot.html.gz
- SHA256SUMS

## Search uplift

The preregistered experiment is documented in [docs/search_uplift_pilot.md](docs/search_uplift_pilot.md). Search-provider results are not part of the baseline. Brave and You enter only after the baseline is frozen.

## Guardrails

- No ByteDance internal data, code, customers, or confidential records.
- Search payloads are transient unless explicit provider storage rights are obtained.
- Every published fact must point to an independent original source page.
- Counts distinguish source records, facilities, companies, and graph edges.
- A company is not labeled SME without separate size evidence.

