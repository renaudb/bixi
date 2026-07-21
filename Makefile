.PHONY: lint test format typecheck docs

lint:
	ruff check .
	pyright .

test:
	pytest .

format:
	ruff format .

typecheck:
	pyright .

docs:
	sphinx-build -b html docs docs/_build
