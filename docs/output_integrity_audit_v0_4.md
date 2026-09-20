# Stored-output integrity audit v0.4

This supporting audit was recomputed against the unchanged frozen GPT decisions on 2026-09-20 UTC. It is independent of the still-running GLM max comparison and makes no claim that manuscript revision v0.4 or human validation is complete.

All 16 decision fields, including quotations and rationales, were reconstructed for all 6,164 records and matched the final table with zero field mismatches. The final-table SHA256 remains `24bd429ac9b56cc2f02e693c9943f940608c896f9744a586cddac27a7d83497a`. No model call, human annotation, or relabeling was performed for this check.

Among 3,799 `no` outputs, 704 name `insufficient_evidence` as the primary reason and 91 name `source_unavailable`: 795 records, or 20.93% of the `no` class. This is a recorded label/reason boundary requiring human investigation, not 795 established misclassifications. The already-selected human double-review subset has not been replaced by an outcome-selected boundary sample.

| Final label | Records | Nonempty normalized literal quote | Empty quote | Nonempty quote without a normalized literal match |
| --- | ---: | ---: | ---: | ---: |
| yes | 1,148 | 1,148 | 0 | 0 |
| no | 3,799 | 3,549 | 124 | 126 |
| unclear | 1,217 | 959 | 221 | 37 |

Of 5,016 nonpositive records, 508 lack a nonempty normalized literal match. Empty quotes may be appropriate for unavailable or insufficient evidence. These counts do not trigger new reviews, exclusions, or label changes. A matching quotation establishes string occurrence, not semantic entailment or factual accuracy.

The [row-free JSON summary](../paper/output_integrity_v0_4.json) records counts and input fingerprints. Recompute it with `python3 scripts/audit_output_integrity.py` where the closed corpus is available. Its synthetic tests detect a changed quotation, keep empty quotes distinct from nonliteral quotes, and reject invalid final-label enums. The existing v0.2/v0.3 summaries and original public release are preserved.

The audit's agreement with stored files does not establish human correctness, model generality, entity-resolution precision, or GNN usefulness. Those remain separate empirical questions described in the [research completion status](research_completion_status_v0_4.md).
