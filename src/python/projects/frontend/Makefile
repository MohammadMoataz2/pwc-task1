# Frontend Makefile

.PHONY: help install dev build clean test

help: ## Show this help message
	@echo "Frontend Makefile Commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

dev: ## Run development server
	streamlit run main.py --server.port=8501 --server.address=localhost

build: ## Build Docker image
	docker build -t pwc-frontend .

clean: ## Clean up
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

test: ## Run tests (placeholder)
	@echo "Tests would go here"