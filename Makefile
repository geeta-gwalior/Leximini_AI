.PHONY: help build up down seed test eval clean

help:
	@echo "LexiMini AI — Management Commands"
	@echo "  make build      Build all Docker microservices"
	@echo "  make up         Start all microservices in background"
	@echo "  make down       Stop all running microservices"
	@echo "  make seed       Seed Qdrant vector database with Indian laws"
	@echo "  make test       Run automated pytest test suite"
	@echo "  make eval       Run MLOps legal benchmark accuracy evaluation"
	@echo "  make clean      Remove python cache and build artifacts"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

seed:
	python3 scripts/seed_vector_db.py

test:
	python3 -m pytest tests/ -v || pytest tests/ -v

eval:
	python3 mlops/pipelines/eval_benchmarks.py

demo:
	python3 scripts/demo_runner.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

