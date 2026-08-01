# Size-evidence audit deviation

The first size-evidence pass is invalid for manuscript use because its prompt context included the general EQDP review rationale. That rationale could itself contain an earlier model statement about employee count, creating circular model-to-model evidence even when the original page did not appear in the size prompt.

Corrective action:

- discard all labels from `size_evidence_audit/`;
- regenerate size contexts only from frozen independently fetched original-page visible text;
- extract deterministic windows around explicit employee, workforce, owner-only, nonemployer, and SBA/SAM terms;
- automatically label an empty size context `insufficient`; and
- rerun structured review on non-empty original-text contexts.

No size-evidence number from the invalid pass may appear in the manuscript. A later 1,179-positive/805-cluster corrected pass was also superseded—not for circularity, but because literal-quote re-audit downgraded 31 producer-label positives. The final size run was regenerated from 1,148 provisional positive pairs and 790 provisional operating-entity clusters.

During the corrected audit, an explicit statement that the focal firm had "over" a stated number of staff exposed a loss in the initial output taxonomy: it was genuine size evidence but neither an exact count nor a two-sided range. The corrected schema therefore distinguishes exact counts, two-sided ranges, lower bounds, and upper bounds. Open endpoints remain null and may not be invented. A lower bound alone cannot establish that a firm is below an SBA employee ceiling; an upper bound may be relevant but still does not establish SBA status without the applicable NAICS size standard and entity-level evidence.
