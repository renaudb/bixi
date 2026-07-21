lint:
	ruff check .
	pyright .

test:
	pytest .

format:
	ruff format .

typecheck:
	pyright .
