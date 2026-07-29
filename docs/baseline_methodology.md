# Baseline v0.1-SIA methodology

## Source

- Page: https://www.semiconductors.org/ecosystem/
- Publisher: Semiconductor Industry Association
- Source family: industry association map
- Extraction: JSON array assigned to companiesData in the page HTML

## Scope

Each source record is a facility/location, not necessarily a unique legal entity. The build separates source records, canonical company nodes, facility nodes, company-to-facility relations, and type/activity relations.

The baseline does not infer legal ownership, SME status, supplier-customer links, or capability details absent from the source.

## Canonicalization

Company names are HTML-decoded, Unicode-normalized, whitespace-collapsed, and casefolded for stable IDs. Facility IDs include company, city, state, latitude, and longitude. Records merge into one company node only when normalized company names match exactly.

Exact-name merging is deliberately conservative. Future releases may add aliases and entity-resolution evidence while retaining original records.

## Relations

- HAS_FACILITY: company to facility
- LOCATED_IN: facility to US-STATE state
- HAS_COMPANY_TYPE: company to COMPANY_TYPE type
- HAS_ACTIVITY: facility to ACTIVITY activity

No SUPPLIES_TO, PARTNERS_WITH, or product capability edges are inferred.

## Provenance

Every node or edge includes, or can be joined to, publisher, source URL, source-record ID, retrieval timestamp, page SHA-256, parser version, and optional supporting URL in the SIA record.

## Known limitations

SIA explicitly says the map is not intended to reflect every U.S. semiconductor ecosystem location and largely represents U.S. locations of SIA member companies. This creates head-company and membership bias. The baseline is intended to quantify how much targeted Brave/You discovery adds beyond that visible core.

The map is broader than NAICS 333242. It includes equipment, materials, fabless, foundry, IDM, universities, and other participants. Search-uplift reporting must show the full ecosystem baseline and the equipment/materials manufacturing subset separately.

## Versioning

Baseline v0.1-SIA is frozen by its manifest and checksums. Re-fetching a changed page creates a new version; the old version remains reproducible.

