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

## v0.2.0-rc1 status

The first pilot completed retrieval, provider-blind Reviewer-1 adjudication of the 75 direct-company/high-signal rows, and independent-source verification of every first-party lenient positive. It generated 30 net-new strict supplier candidates.

The public release remains an RC because 111 lower-signal domain rows have not received the same adjudication, a second independent annotator has not completed the preregistered sample, agreement is not available, and the Wilson precision lower bound is below the 0.55 gate.

