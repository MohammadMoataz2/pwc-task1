# PWC Contract Analysis System - Main Makefile

# Include environment variables from .env file if it exists
ifneq (,$(wildcard .env))
    include .env
    export
endif

# Colors for output
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
RED = \033[0;31m
NC = \033[0m # No Color

.PHONY: help build up down logs clean install-dev test

help: ## Show this help message
	@echo "${GREEN}PWC Contract Analysis System${NC}"
	@echo "==============================================="
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "${YELLOW}%-20s${NC} %s\n", $$1, $$2}'

check-env: ## Check if required environment variables are set
	@echo "${BLUE}Checking environment variables...${NC}"
	@if [ ! -f .env ]; then \
		echo "${RED}ERROR: .env file not found${NC}"; \
		echo "Please copy .env.example to .env and configure it"; \
		exit 1; \
	fi
	@if [ -z "$(OPENAI_API_KEY)" ] || [ "$(OPENAI_API_KEY)" = "your-openai-api-key-here" ]; then \
		echo "${RED}ERROR: OPENAI_API_KEY is not properly set in .env file${NC}"; \
		echo "Please edit .env file and set a valid OpenAI API key"; \
		exit 1; \
	fi
	@echo "${GREEN}Environment check passed${NC}"

show-env: ## Show current environment variables (non-sensitive ones)
	@echo "${BLUE}Current Environment Configuration:${NC}"
	@echo "STORAGE_TYPE: $(STORAGE_TYPE)"
	@echo "AI_PROVIDER: $(AI_PROVIDER)"
	@echo "OPENAI_MODEL: $(OPENAI_MODEL)"
	@echo "MONGODB_DATABASE: $(MONGODB_DATABASE)"
	@echo "DEBUG: $(DEBUG)"
	@echo "OPENAI_API_KEY: $(if $(OPENAI_API_KEY),***SET***,NOT_SET)"
	@echo "SECRET_KEY: $(if $(SECRET_KEY),***SET***,NOT_SET)"

build: ## Build all Docker images
	@echo "${GREEN}Building all Docker images...${NC}"
	docker-compose build

rebuild: ## Rebuild all Docker images (no cache)
	@echo "${GREEN}Rebuilding all Docker images (no cache)...${NC}"
	docker-compose build --no-cache

up: check-env ## Start all services
	@echo "${GREEN}Starting all services...${NC}"
	docker-compose up -d
	@echo "${GREEN}Services started successfully!${NC}"
	@echo "${BLUE}API available at: http://localhost:8000${NC}"
	@echo "${BLUE}API docs available at: http://localhost:8000/docs${NC}"
	@echo "${BLUE}MongoDB Admin (Mongo Express) available at: http://localhost:8081${NC}"
	@echo "${YELLOW}MongoDB Admin credentials: admin / admin123${NC}"

down: ## Stop all services
	@echo "${GREEN}Stopping all services...${NC}"
	docker-compose down

restart: down up ## Restart all services

logs: ## Show logs from all services
	docker-compose logs -f

logs-api: ## Show API logs
	docker-compose logs -f api

logs-worker: ## Show worker logs
	docker-compose logs -f worker

logs-db: ## Show database logs
	docker-compose logs -f mongodb

status: ## Show status of all services
	@echo "${GREEN}Service Status:${NC}"
	docker-compose ps

clean: ## Clean up containers, images, and volumes
	@echo "${GREEN}Cleaning up...${NC}"
	docker-compose down -v --rmi all --remove-orphans
	docker system prune -f

install-dev: ## Install development dependencies
	@echo "${GREEN}Installing development dependencies...${NC}"
	cd src/python/libs/pwc && pip install -r requirements.txt
	cd src/python/projects/api && pip install -r requirements.txt
	cd src/python/projects/analyze_contracts && pip install -r requirements.txt

test-api: ## Run API tests
	@echo "${GREEN}Running API tests...${NC}"
	cd src/python/projects/api && make test

test-worker: ## Run worker tests
	@echo "${GREEN}Running worker tests...${NC}"
	cd src/python/projects/analyze_contracts && make test

test: test-api test-worker ## Run all tests

dev-api: ## Run API in development mode
	@echo "${GREEN}Starting API in development mode...${NC}"
	cd src/python/projects/api && make dev

dev-worker: ## Run worker in development mode
	@echo "${GREEN}Starting worker in development mode...${NC}"
	cd src/python/projects/analyze_contracts && make dev

setup: ## Initial setup of the project
	@echo "${GREEN}Setting up PWC Contract Analysis System...${NC}"
	@echo "1. Installing dependencies..."
	make install-dev
	@echo "2. Creating .env file..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "${YELLOW}Created .env file from .env.example${NC}"; \
		echo "${YELLOW}Please edit .env file and add your OpenAI API key${NC}"; \
	else \
		echo "${BLUE}.env file already exists${NC}"; \
	fi
	@echo "3. Building Docker images..."
	make build
	@echo "${GREEN}Setup complete!${NC}"
	@echo "${BLUE}Next steps:${NC}"
	@echo "1. Edit .env file and add your OpenAI API key"
	@echo "2. Run 'make up' to start the system"

# Development shortcuts
api-shell: ## Get shell access to API container
	docker-compose exec api /bin/bash

worker-shell: ## Get shell access to worker container
	docker-compose exec worker /bin/bash

db-shell: ## Get shell access to MongoDB
	docker-compose exec mongodb mongosh