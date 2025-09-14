.PHONY: format lint typecheck test

format:
	black .

lint:
	ruff .

typecheck:
	mypy .

test:
	pytest
