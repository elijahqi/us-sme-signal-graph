# External annotator guide v0.3

## Purpose

Evaluate whether the supplied business is an **evidence-qualified domestic producer (EQDP)** for one frozen capability and state. You are not deciding procurement readiness, capacity, certification, financial health, or endorsement. Provider, rank, query intent, and predicted business size are hidden. Search-result snippets are never evidence.

Review only the supplied company and independently fetched original sources. You may request another original source about that company, but you may not discover a replacement company. Record every supplemental URL and active review minutes. Use `unclear` instead of guessing.

## Decision sequence

### 1. Business identity

- `yes`: a specific operating commercial business is resolved.
- `no`: not a business, hobby-only activity, inactive/fictional entity, or irreconcilable conflation.
- `unclear`: legal/operating name, domain, ownership, or successor status remains unresolved.

Record aliases, parent/subsidiary relationships, and legal form when supported. Do not merge businesses on fuzzy name similarity alone.

### 2. Direct production role

- `yes`: makes, fabricates, assembles, processes, rebuilds, remanufactures, or contract-produces the requested item or capability.
- `no`: distributor-only, reseller-only, broker, consultant, software-only vendor, recruiter, marketplace, directory, news site, or noncommercial hobby page.
- `unclear`: terms such as “solutions,” “supplier,” or “maker” do not establish production.

A sole proprietor, owner-operated shop, or home-based commercial producer is eligible. Conventional factory scale is not required.

### 3. Capability match

- `yes`: original evidence explicitly states the requested capability or an unambiguous technical equivalent.
- `partial`: neighboring capability or broad sector match only.
- `no`: evidence conflicts with the task.
- `unclear`: language is too vague.

Quote the shortest complete evidence span. “Serves manufacturers,” “advanced solutions,” or a broad industry label is insufficient.

### 4. Production presence in the queried state

- `industrial_facility_confirmed`
- `job_shop_or_workshop_confirmed`
- `owner_or_home_production_confirmed`
- `us_made_claim_site_unresolved`
- `office_warehouse_or_lab_only`
- `foreign_only`
- `unknown`

The first three satisfy the location component. Evidence must connect production to the queried state. An office, warehouse, engineering laboratory, registered-agent address, or planned facility is insufficient. For an owner/home producer, city/state plus an explicit commercial production statement is sufficient; do not seek or record a private residential street address.

### 5. Commercial offering

- `yes`: the business offers the product or manufacturing service to external customers.
- `no`: internal production, research demonstration, personal hobby, or inactive offering.
- `unclear`: no current commercial signal.

### 6. Final EQDP

Set `eqdp=yes` only when identity, direct production, capability, eligible state production presence, and commercial offering all pass with current original-page provenance. Otherwise select `no` or `unclear` and one primary exclusion reason:

- `not_operating_business`
- `identity_conflict`
- `duplicate_entity`
- `distributor_reseller_or_broker`
- `nonmanufacturing_service`
- `hobby_or_noncommercial`
- `capability_mismatch`
- `generic_sector_claim_only`
- `wrong_state`
- `office_warehouse_or_lab_only`
- `foreign_production_only`
- `historical_or_inactive`
- `insufficient_evidence`
- `source_unavailable`

EQDP does not imply that the business has capacity, certifications, willingness, or buyer approval.

## Scale, legal form, and web visibility

These labels are separate from EQDP and cannot change it.

Choose a scale band only when supported:

- `owner_only_or_nonemployer_supported`
- `micro_employer_1_9_supported`
- `small_employer_10_99_supported`
- `mid_employer_100_499_supported`
- `large_500_plus_supported`
- `unknown`

Census nonemployer status means no paid employees and applicable federal-tax/receipts conditions. Aggregate Census data cannot prove that a named business is a nonemployer. Directory or social-platform employee estimates are provisional and must name the source; they cannot prove nonemployer or SBA status.

Legal form is `sole_proprietor`, `single_member_llc`, `other_llc`, `partnership`, `corporation`, `other`, or `unknown`. Do not infer sole proprietorship from the owner's name or the word “studio.”

Web visibility is:

- `dedicated_business_domain`;
- `marketplace_or_social_only`;
- `directory_or_registry_only`;
- `mixed`; or
- `unknown`.

## Separate SBA status

1. Assign the activity-specific six-digit NAICS using the current Census definition.
2. Record the current 13 CFR 121.201 threshold and retrieval date.
3. Resolve the exact business and known affiliates.
4. Choose `sba_self_certified_small`, `size_consistent_unverified`, `not_small`, or `unknown`.

A current entity-matched SAM/SBA representation can support `sba_self_certified_small`; it remains a business representation. Never convert LinkedIn, LeadIQ, ZoomInfo, marketplace, or directory estimates into official SBA status. Use `unknown` if affiliation or identity is unresolved.

## Independence, conflicts, and privacy

Work independently until submission. An adjudicator receives both original labels and records the final rationale without overwriting them. Disclose and reassign a business with which you have worked, invested, competed, or had a material relationship.

Do not collect personal phone numbers, personal emails, household names, credentials, access-controlled data, or unnecessary personal information. Do not publish a sole proprietor's residential street address. Retain public business facts, city/state where supportable, URLs, retrieval times, hashes, short necessary quotations, and non-sensitive labels.

