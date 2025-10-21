# PWC Contract Analysis API Makefile

# Variables
DOCKER_IMAGE = pwc-contract-api
DOCKER_TAG = latest
CONTAINER_NAME = pwc_api

# Colors for output
GREEN = \033[0;32m
YELLOW = \033[1;33m
NC = \033[0m # No Color

.PHONY: help install dev test clean docker-build docker-run docker-stop

help: ## Show this help message
	@echo "${GREEN}PWC Contract Analysis API${NC}"
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "${YELLOW}%-20s${NC} %s\n", $$1, $$2}'

install: ## Install dependencies
	@echo "${GREEN}Installing dependencies...${NC}"
	pip install -r requirements.txt
	pip install -r ../../libs/pwc/requirements.txt

dev: ## Run development server
	@echo "${GREEN}Starting development server...${NC}"
	PYTHONPATH=../../libs:$$PYTHONPATH uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

test: ## Run tests
	@echo "${GREEN}Running tests...${NC}"
	pytest tests/ -v

clean: ## Clean up Python cache files
	@echo "${GREEN}Cleaning up...${NC}"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +

docker-build: ## Build Docker image
	@echo "${GREEN}Building Docker image...${NC}"
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .

docker-run: ## Run Docker container
	@echo "${GREEN}Running Docker container...${NC}"
	docker run -d \
		--name $(CONTAINER_NAME) \
		-p 8000:8000 \
		--env-file .env \
		$(DOCKER_IMAGE):$(DOCKER_TAG)

docker-stop: ## Stop and remove Docker container
	@echo "${GREEN}Stopping Docker container...${NC}"
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true

docker-logs: ## Show Docker container logs
	docker logs -f $(CONTAINER_NAME)

lint: ## Run linting
	@echo "${GREEN}Running linting...${NC}"
	flake8 api/
	black --check api/
	isort --check-only api/

format: ## Format code
	@echo "${GREEN}Formatting code...${NC}"
	black api/
	isort api/