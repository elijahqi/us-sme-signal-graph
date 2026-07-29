.PHONY: baseline validate test preflight

baseline:
	python3 scripts/build_baseline.py

rebuild-frozen:
	python3 scripts/build_baseline.py --input-html data/raw/sia_ecosystem.html

validate:
	python3 scripts/validate_baseline.py

test:
	python3 -m unittest discover -s tests -v

preflight:
	python3 scripts/release_preflight.py

