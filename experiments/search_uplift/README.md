# Search uplift experiment

Brave and You are experimental discovery and verification arms. They do not contribute to Baseline v0.1-SIA.

Workflow:

1. Freeze baseline manifest and hashes.
2. Freeze query set and provider parameters.
3. Run Brave-only and You-only search without live crawl.
4. Canonicalize URLs and companies.
5. Fetch original pages through a provider-neutral fetcher.
6. Blind-review candidate supplier validity and SME evidence.
7. Calculate precision, net-new companies, marginal contribution, overlap, confidence intervals, and downstream effects.

See docs/search_uplift_pilot.md and experiments/search_uplift/query_set.csv.

