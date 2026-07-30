# Data rights and release boundary

## Code

Project-authored code and documentation are Apache-2.0 licensed.

## SIA ecosystem map

The SIA map is publicly accessible, but its Terms of Use page does not provide an open-data license and the site states that content is all rights reserved. Therefore:

- local experiments may fetch and transform the page for research and verification;
- the public repository does not include the raw SIA HTML, row-level extracted tables, or frozen derived baseline;
- public users run the downloader themselves and are responsible for source terms;
- the repository may publish schemas, code, aggregate methodology, source URL, page hash, and non-substitutive statistics;
- permission should be requested before redistributing a row-level SIA-derived dataset.

## Brave Search API

Brave's Search API Terms of Use, updated February 11, 2026, expressly prohibit storing, caching, or creating a database of Search Results except for transient operational storage. They also prohibit derivative works and redistribution unless an applicable Order Form grants different rights. The restriction is based on use, not a minimum number of result rows. Unless a plan explicitly grants storage rights:

- use results transiently to discover source URLs;
- do not commit result titles, snippets, ranks, payloads, or caches;
- fetch original source pages independently;
- publish only provider-aggregate experiment metrics and independently established facts.

## You APIs

You.com's public general Terms do not contain Brave's express prohibition on storing a database of Search Results. They assign You.com's rights, if any, in Outputs to the user but exclude Third Party Output, and permit service-specific supplemental terms. Search titles, snippets, and linked-page content may contain third-party material. The applicable API account terms, Order Form, MSA, and supplemental terms have not yet been shown to grant research-database or redistribution rights. Apply a conservative no-raw-payload release boundary until those terms or written provider confirmation are reviewed, without representing that You publicly imposes the same express storage prohibition as Brave.

## Paper-first closed research corpus

The v0.3 long-tail study does not require a public row-level company dataset. Public artifacts are limited by default to the frozen query lattice, code, schemas, aggregate statistics, methods, and integrity manifests. A closed local corpus may retain independently fetched original-source provenance, derived business facts, entity-resolution decisions, and annotations only where the original publisher's terms, privacy rules, and applicable law permit. Nonpublication does not override provider API storage terms: ordinary Brave raw Search Results remain transient unless an Order Form grants storage rights.

For Brave ordinary access, “transient” means batch-local processing: raw responses are placed in an operating-system temporary directory, reduced to validated aggregate counts, used to initiate independent original-page fetches, and deleted immediately after that batch succeeds. They are not retained through manuscript drafting.

## Original websites

Each source website remains subject to its own terms, robots policy, copyright, privacy, and database rights. Provenance is not a substitute for permission.

## Public v0.2 candidate table

The public candidate table contains reviewed factual fields, source URLs, retrieval hashes, and project-authored classifications. It excludes fetched HTML, evidence windows, provider snippets, search rank, and provider origin. Apache-2.0 covers project code and documentation. The project-authored selection and arrangement of the public factual table is offered under CC BY 4.0; third-party page content and trademarks remain with their owners.

