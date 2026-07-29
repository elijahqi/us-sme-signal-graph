# Frozen Baseline v0.1-SIA

This baseline was reconstructed from the public SIA U.S. Semiconductor Ecosystem Map. It is an intentionally known-incomplete comparison baseline, not the unpublished 664-entity graph reported in the paper.

## Frozen scope

- Source records / facilities: 555
- Exact-name company nodes: 239
- Equipment or Materials supplier-denominator companies: 50
- Manufacturing facilities: 213
- Reference nodes: 56
- Basic provenance relations: 2,150

## Supplier uplift denominator

The Brave/You supplier uplift experiment uses the 50 Equipment/Materials company nodes in supplier_baseline.csv as its primary baseline denominator. The 239-company full ecosystem is reported separately and includes fabless firms, foundries, IDMs, universities, and other non-supplier participants.

All 50 baseline companies have SME status unknown. SME status requires a separate SBA-size evidence step.

## Excluded claims

The frozen baseline does not claim complete U.S. coverage, SME status, supplier-customer links, or legal-entity resolution beyond exact normalized source names.

See baseline_manifest.json and SHA256SUMS for the machine-readable freeze record.
