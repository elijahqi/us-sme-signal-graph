.PHONY: baseline validate test adjudicate verify metrics public-release preflight query-lattice check-query-lattice manuscript-pdf

baseline:
	python3 scripts/build_baseline.py

rebuild-frozen:
	python3 scripts/build_baseline.py --input-html data/raw/sia_ecosystem.html

validate:
	python3 scripts/validate_baseline.py

test:
	python3 -m unittest discover -s tests -v

query-lattice:
	python3 scripts/build_query_lattice.py

check-query-lattice:
	python3 scripts/build_query_lattice.py --check

adjudicate:
	python3 scripts/apply_reviewer1_adjudication.py

verify:
	python3 scripts/apply_verification.py \
		--fetched experiments/search_uplift/private/formal_24q/verification/fetched_v3/source_candidates.csv \
		--fetched experiments/search_uplift/private/formal_24q/verification/fetched_v5/source_candidates.csv

metrics:
	python3 scripts/compute_pilot_metrics.py
	python3 scripts/compute_provider_attribution.py \
		--incidence experiments/search_uplift/private/formal_24q/provider_url_incidence.csv

public-release: adjudicate verify metrics
	python3 scripts/build_public_release.py
	python3 scripts/validate_public_release.py

preflight:
	python3 scripts/release_preflight.py

manuscript-pdf:
	bash scripts/build_manuscript_pdf.sh

