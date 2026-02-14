# Makefile for ReSynth

.PHONY: help install dev-install test lint format clean run-api run-cli run-web

# Default target
help:
	@echo "ReSynth - Research Paper Synthesis Agent"
	@echo ""
	@echo "Available commands:"
	@echo "  install      Install dependencies"
	@echo "  dev-install  Install development dependencies"
	@echo "  test         Run tests"
	@echo "  lint         Run linting"
	@echo "  format       Format code"
	@echo "  clean        Clean temporary files"
	@echo "  run-api      Run API server"
	@echo "  run-cli      Run CLI example"
	@echo "  run-web      Run web interface"
	@echo ""

# Installation
install:
	pip install -r requirements.txt
	python -m spacy download en_core_web_sm

dev-install: install
	pip install -e ".[dev]"

# Testing
test:
	python -m pytest tests/ -v --cov=src --cov-report=html --cov-report=term

test-quick:
	python -m pytest tests/ -v --tb=short

# Code quality
lint:
	flake8 src/ tests/ main.py cli.py app.py
	mypy src/ --ignore-missing-imports

format:
	black src/ tests/ main.py cli.py app.py setup.py
	isort src/ tests/ main.py cli.py app.py setup.py

# Cleaning
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

# Running the application
run-api:
	python main.py

run-cli:
	python cli.py --search "machine learning interpretability" --max-papers 3

run-web:
	streamlit run app.py

# Development helpers
setup-env:
	cp .env.example .env
	@echo "Please edit .env file with your API keys"

check-deps:
	pip check
	pip list | grep -E "(fastapi|streamlit|chromadb|sentence-transformers|arxiv|openai)"

# Documentation
docs:
	@echo "Documentation is available in README.md"
	@echo "API docs: http://localhost:8000/docs (when API server is running)"

# Quick start
quickstart: install
	@echo "Setting up quick start example..."
	python cli.py --search "transformer architectures" --max-papers 2 --no-content
	@echo "Now you can query with:"
	@echo "python cli.py --query 'What are attention mechanisms in transformers?'"
