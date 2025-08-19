.PHONY: help install dev-install test lint format clean run run-docker stop-docker build

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install production dependencies
	pip install -r requirements.txt

dev-install:  ## Install development dependencies
	pip install -e ".[dev]"
	pip install -r requirements.txt

test:  ## Run tests
	pytest tests/ -v

lint:  ## Run linting
	flake8 services/ tests/
	mypy services/

format:  ## Format code
	black services/ tests/ launch_services.py
	isort services/ tests/ launch_services.py

clean:  ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/ .mypy_cache/ dist/ build/

run:  ## Run services locally
	python launch_services.py

run-docker:  ## Run services with Docker Compose
	docker-compose up --build

stop-docker:  ## Stop Docker Compose services
	docker-compose down

build:  ## Build Docker image
	docker build -t simviator-microservices .

# Development shortcuts
dev: dev-install format lint test  ## Full development setup

# CI/CD shortcuts
ci: install lint test  ## CI pipeline
