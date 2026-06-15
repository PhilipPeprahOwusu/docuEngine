.PHONY: help install dev test clean migrate upgrade downgrade format lint type-check run docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make dev          - Install dev dependencies"
	@echo "  make test         - Run tests"
	@echo "  make clean        - Clean up cache and temp files"
	@echo "  make migrate      - Create new migration"
	@echo "  make upgrade      - Apply database migrations"
	@echo "  make downgrade    - Rollback last migration"
	@echo "  make format       - Format code with black"
	@echo "  make lint         - Lint code with flake8"
	@echo "  make type-check   - Check types with mypy"
	@echo "  make run          - Run development server"
	@echo "  make docker-up    - Start Docker containers"
	@echo "  make docker-down  - Stop Docker containers"

install:
	pip install -r requirements.txt

dev:
	pip install -r requirements.txt
	pip install black flake8 mypy pytest-cov

test:
	pytest -v --cov=app --cov-report=html

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf dist
	rm -rf build

migrate:
	alembic revision --autogenerate -m "$(m)"

upgrade:
	alembic upgrade head

downgrade:
	alembic downgrade -1

format:
	black app/

lint:
	flake8 app/

type-check:
	mypy app/

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down
