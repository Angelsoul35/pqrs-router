.PHONY: install test lint run demo clean

install:
	pip install -e ".[dev]"

test:
	pytest --cov=pqrs_router --cov-report=term-missing

lint:
	ruff check pqrs_router tests

run:
	uvicorn pqrs_router.main:app --reload --port 8000

demo:
	python -m pqrs_router.cli demo

clean:
	rm -rf .pytest_cache .ruff_cache .coverage htmlcov
